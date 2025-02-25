from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from ..models import LoadOrder
import logging

logger = logging.getLogger(__name__)

class LoadOrderReportService:
    """Service for generating load order reports"""
    
    @staticmethod
    def get_daily_summary(date=None):
        """Get summary of load orders for a specific date"""
        try:
            if not date:
                date = timezone.now().date()
                
            orders = LoadOrder.objects.filter(load_date=date)
            
            summary = {
                'date': date,
                'total_orders': orders.count(),
                'total_items': orders.aggregate(
                    total=Sum('items__quantity')
                )['total'] or 0,
                'orders_by_vehicle': orders.values(
                    'load_to__name',
                    'load_to__plate'
                ).annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                ),
                'orders_by_customer': orders.values(
                    'customer__first_name',
                    'customer__last_name'
                ).annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                )
            }
            
            logger.info(f"[LOAD ORDER REPORTS] Generated daily summary for {date}")
            return summary
            
        except Exception as e:
            logger.error(f"[LOAD ORDER REPORTS] Error generating daily summary: {str(e)}")
            raise
    
    @staticmethod
    def get_weekly_summary(end_date=None):
        """Get summary of load orders for the last 7 days"""
        try:
            if not end_date:
                end_date = timezone.now().date()
            
            start_date = end_date - timedelta(days=6)
            orders = LoadOrder.objects.filter(
                load_date__range=[start_date, end_date]
            )
            
            summary = {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'total_orders': orders.count(),
                'total_items': orders.aggregate(
                    total=Sum('items__quantity')
                )['total'] or 0,
                'daily_breakdown': orders.values('load_date').annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                ).order_by('load_date'),
                'vehicle_breakdown': orders.values(
                    'load_to__name',
                    'load_to__plate'
                ).annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                ).order_by('-total_orders'),
                'customer_breakdown': orders.values(
                    'customer__first_name',
                    'customer__last_name'
                ).annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                ).order_by('-total_orders')
            }
            
            logger.info(f"[LOAD ORDER REPORTS] Generated weekly summary from {start_date} to {end_date}")
            return summary
            
        except Exception as e:
            logger.error(f"[LOAD ORDER REPORTS] Error generating weekly summary: {str(e)}")
            raise
    
    @staticmethod
    def get_vehicle_performance(vehicle_id, start_date=None, end_date=None):
        """Get performance metrics for a specific vehicle"""
        try:
            if not end_date:
                end_date = timezone.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=30)
                
            orders = LoadOrder.objects.filter(
                load_to_id=vehicle_id,
                load_date__range=[start_date, end_date]
            )
            
            performance = {
                'period': {
                    'start': start_date,
                    'end': end_date
                },
                'total_orders': orders.count(),
                'total_items': orders.aggregate(
                    total=Sum('items__quantity')
                )['total'] or 0,
                'daily_loads': orders.values('load_date').annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                ).order_by('load_date'),
                'customer_distribution': orders.values(
                    'customer__first_name',
                    'customer__last_name'
                ).annotate(
                    total_orders=Count('id'),
                    total_items=Sum('items__quantity')
                ).order_by('-total_orders')
            }
            
            logger.info(f"[LOAD ORDER REPORTS] Generated vehicle performance report for vehicle {vehicle_id}")
            return performance
            
        except Exception as e:
            logger.error(f"[LOAD ORDER REPORTS] Error generating vehicle performance report: {str(e)}")
            raise