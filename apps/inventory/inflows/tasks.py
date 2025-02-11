from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Sum, Avg, F
from .models import Inflow, InflowItems
from .notifications.handlers import InflowNotificationHandler
from .notifications.constants import (
    APP_NAME,
    NOTIFICATION_TYPE,
    NOTIFICATION_TITLES,
    NOTIFICATION_MESSAGES,
    SEVERITY_TYPES,
    RECIPIENT_TYPES
)
import logging

logger = logging.getLogger(__name__)


@shared_task(name='generate_daily_inflow_report')
def generate_daily_inflow_report():
    today = timezone.now().date()
    start_date = today - timezone.timedelta(days=7)
    end_date = today
    
    try:
        # Gerar estatísticas detalhadas
        inflows = Inflow.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        # Calcular totais dos itens
        inflow_items = InflowItems.objects.filter(
            inflow__in=inflows
        )
        
        total_value = sum(
            item.quantity * item.product.price 
            for item in inflow_items.select_related('product')
        )
        
        avg_value = total_value / inflows.count() if inflows.count() > 0 else 0
        
        report_data = {
            'period': {
                'start': start_date.strftime('%d/%m/%Y'),
                'end': end_date.strftime('%d/%m/%Y')
            },
            'total_inflows': inflows.count(),
            'total_items': inflow_items.count(),
            'total_value': float(total_value),
            'avg_value': float(avg_value),
            'by_supplier': []
        }
        
        # Agrupar por fornecedor
        for supplier_data in inflows.values('origin__name').annotate(count=Count('id')):
            supplier_items = inflow_items.filter(
                inflow__origin__name=supplier_data['origin__name']
            ).select_related('product')
            
            supplier_total = sum(
                item.quantity * item.product.price 
                for item in supplier_items
            )
            
            report_data['by_supplier'].append({
                'name': supplier_data['origin__name'],
                'count': supplier_data['count'],
                'total_value': float(supplier_total)
            })
        
        logger.info(f"[INFLOWS TASK] Generated report for period {start_date} to {end_date}")
        
        # Enviar notificação para Owner, CEO e Admin
        recipients = InflowNotificationHandler.get_recipients_by_type(*RECIPIENT_TYPES['REPORT'])
        recipient_ids = [str(user.id) for user in recipients]
        
        # Usar a mensagem formatada das constantes
        message = NOTIFICATION_MESSAGES[NOTIFICATION_TYPE['INFLOW_REPORT']] % {
            'start': report_data['period']['start'],
            'end': report_data['period']['end'],
            'total_inflows': report_data['total_inflows'],
            'total_items': report_data['total_items'],
            'total_value': report_data['total_value'],
            'avg_value': report_data['avg_value']
        }
        
        InflowNotificationHandler.send_to_recipients(
            recipient_ids=recipient_ids,
            title=NOTIFICATION_TITLES[NOTIFICATION_TYPE['INFLOW_REPORT']],
            message=message,
            app_name=APP_NAME,
            notification_type=SEVERITY_TYPES['INFO'],
            data=report_data
        )
        
        return report_data
        
    except Exception as e:
        error_msg = f"Error generating daily inflow report: {str(e)}"
        logger.error(f"[INFLOWS TASK] {error_msg}")
        return {"error": error_msg}