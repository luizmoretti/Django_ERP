from celery import shared_task
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from apps.delivery.models import Delivery, DeliveryCheckpoint
import logging
import csv
import os
from io import StringIO
import json

logger = logging.getLogger(__name__)

@shared_task
def notify_delivery_status_change(delivery_id, old_status, new_status):
    """
    Envia notificações quando o status de uma entrega muda.
    """
    try:
        delivery = Delivery.objects.get(id=delivery_id)
        
        # Dados básicos para a notificação
        context = {
            'delivery_id': delivery.id,
            'customer_name': delivery.customer.name,
            'driver_name': delivery.driver.name,
            'vehicle_info': f"{delivery.vehicle.model} ({delivery.vehicle.license_plate})",
            'old_status': old_status,
            'new_status': new_status,
            'timestamp': timezone.now().strftime("%d/%m/%Y %H:%M:%S"),
            'estimated_arrival': delivery.estimated_arrival.strftime("%d/%m/%Y %H:%M:%S") if delivery.estimated_arrival else "Não disponível"
        }
        
        # Notificação para o cliente
        if delivery.customer.email:
            subject = _("Atualização de Status de Entrega")
            html_message = render_to_string('delivery/email/status_update.html', context)
            plain_message = render_to_string('delivery/email/status_update.txt', context)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [delivery.customer.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"[DELIVERY TASK] Notificação de status enviada para o cliente {delivery.customer.full_name}")
        
        # Notificação para a empresa (gerentes)
        manager_emails = delivery.companie.get_manager_emails()
        if manager_emails:
            subject = _("Atualização de Status de Entrega - Interno")
            html_message = render_to_string('delivery/email/status_update_internal.html', context)
            plain_message = render_to_string('delivery/email/status_update_internal.txt', context)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                manager_emails,
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"[DELIVERY TASK] Notificação de status enviada para gerentes da empresa")
        
        return True
    except Exception as e:
        logger.error(f"[DELIVERY TASK] Erro ao enviar notificação de status: {str(e)}")
        return False

@shared_task
def generate_delivery_report(delivery_id):
    """
    Gera um relatório detalhado de uma entrega, incluindo todos os checkpoints.
    """
    try:
        delivery = Delivery.objects.get(id=delivery_id)
        checkpoints = DeliveryCheckpoint.objects.filter(delivery=delivery).order_by('timestamp')
        
        # Criar CSV em memória
        output = StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            'ID da Entrega', 
            'Cliente', 
            'Motorista',
            'Veículo',
            'Status Atual',
            'Data de Criação',
            'Última Atualização',
            'ETA',
            'Chegada Real'
        ])
        
        # Dados principais da entrega
        writer.writerow([
            str(delivery.id),
            delivery.customer.name,
            delivery.driver.name,
            f"{delivery.vehicle.model} ({delivery.vehicle.license_plate})",
            delivery.status,
            delivery.created_at.strftime("%d/%m/%Y %H:%M:%S"),
            delivery.updated_at.strftime("%d/%m/%Y %H:%M:%S"),
            delivery.estimated_arrival.strftime("%d/%m/%Y %H:%M:%S") if delivery.estimated_arrival else "N/A",
            delivery.actual_arrival.strftime("%d/%m/%Y %H:%M:%S") if delivery.actual_arrival else "N/A"
        ])
        
        # Linha em branco
        writer.writerow([])
        
        # Cabeçalho dos checkpoints
        writer.writerow([
            'Checkpoint ID',
            'Timestamp',
            'Status',
            'Latitude',
            'Longitude',
            'Notas'
        ])
        
        # Dados dos checkpoints
        for checkpoint in checkpoints:
            location = checkpoint.location or {}
            writer.writerow([
                str(checkpoint.id),
                checkpoint.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                checkpoint.status,
                location.get('latitude', 'N/A'),
                location.get('longitude', 'N/A'),
                checkpoint.notes or 'N/A'
            ])
        
        # Obter conteúdo do CSV
        csv_content = output.getvalue()
        output.close()
        
        # Salvar relatório (aqui você pode enviar por email, salvar em storage, etc)
        # Exemplo: salvar em um diretório temporário
        report_dir = os.path.join(settings.MEDIA_ROOT, 'delivery_reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_filename = f"delivery_report_{delivery.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.csv"
        report_path = os.path.join(report_dir, report_filename)
        
        with open(report_path, 'w') as f:
            f.write(csv_content)
            
        logger.info(f"[DELIVERY TASK] Relatório gerado com sucesso para entrega {delivery.id}: {report_path}")
        
        # Retornar o caminho do arquivo
        return report_path
    
    except Exception as e:
        logger.error(f"[DELIVERY TASK] Erro ao gerar relatório: {str(e)}")
        return None
        
@shared_task
def clean_old_delivery_reports(days=30):
    """
    Remove relatórios de entrega mais antigos que o número especificado de dias.
    """
    try:
        report_dir = os.path.join(settings.MEDIA_ROOT, 'delivery_reports')
        if not os.path.exists(report_dir):
            return 0
            
        now = timezone.now()
        count = 0
        
        for filename in os.listdir(report_dir):
            if not filename.startswith('delivery_report_'):
                continue
                
            file_path = os.path.join(report_dir, filename)
            file_mod_time = timezone.datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.get_current_timezone())
            
            # Se o arquivo for mais antigo que o limite
            if (now - file_mod_time).days > days:
                os.remove(file_path)
                count += 1
                
        logger.info(f"[DELIVERY TASK] {count} relatórios antigos removidos com sucesso")
        return count
        
    except Exception as e:
        logger.error(f"[DELIVERY TASK] Erro ao limpar relatórios antigos: {str(e)}")
        return -1

@shared_task
def check_late_deliveries():
    """
    Verifica entregas que estão atrasadas (passou o ETA e ainda não foram entregues).
    """
    try:
        now = timezone.now()
        late_deliveries = Delivery.objects.filter(
            status__in=['in_transit', 'pending'],
            estimated_arrival__lt=now,
            actual_arrival__isnull=True
        )
        
        for delivery in late_deliveries:
            # Calcular o atraso em horas
            delay = (now - delivery.estimated_arrival).total_seconds() / 3600
            
            # Criar contexto para o email
            context = {
                'delivery_id': delivery.id,
                'customer_name': delivery.customer.name,
                'driver_name': delivery.driver.name,
                'vehicle_info': f"{delivery.vehicle.model} ({delivery.vehicle.license_plate})",
                'status': delivery.status,
                'estimated_arrival': delivery.estimated_arrival.strftime("%d/%m/%Y %H:%M:%S"),
                'delay_hours': round(delay, 1),
                'current_time': now.strftime("%d/%m/%Y %H:%M:%S")
            }
            
            # Notificar gerentes da empresa
            manager_emails = delivery.companie.get_manager_emails()
            if manager_emails:
                subject = _("ALERTA: Entrega Atrasada")
                html_message = render_to_string('delivery/email/late_delivery_alert.html', context)
                plain_message = render_to_string('delivery/email/late_delivery_alert.txt', context)
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    manager_emails,
                    html_message=html_message,
                    fail_silently=False
                )
                
                logger.info(f"[DELIVERY TASK] Alerta de atraso enviado para entrega {delivery.id} (atraso de {round(delay, 1)} horas)")
        
        return len(late_deliveries)
    
    except Exception as e:
        logger.error(f"[DELIVERY TASK] Erro ao verificar entregas atrasadas: {str(e)}")
        return -1 