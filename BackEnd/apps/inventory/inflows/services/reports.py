from django.utils import timezone
from django.db.models import Count, Sum, Avg, F, Q, ExpressionWrapper, fields, Min, Max
from django.db.models.functions import ExtractMonth, TruncMonth
from ..models import Inflow, InflowItems
import logging

logger = logging.getLogger(__name__)

class InflowReportService:
    """
    Service class for generating Inflow reports
    """
    
    @staticmethod
    def generate_daily_report(start_date=None, end_date=None):
        """
        Generate daily inflow report
        
        Args:
            start_date (date, optional): Start date for report. Defaults to 7 days ago.
            end_date (date, optional): End date for report. Defaults to today.
            
        Returns:
            dict: Report data
        """
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=7)
        if not end_date:
            end_date = timezone.now().date()
            
        try:
            # Get inflows for period
            inflows = Inflow.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            
            # Get items for inflows
            inflow_items = InflowItems.objects.filter(
                inflow__in=inflows
            ).select_related('product')
            
            # Calculate totals
            total_value = sum(
                item.quantity * item.product.price 
                for item in inflow_items
            )
            
            avg_value = total_value / inflows.count() if inflows.count() > 0 else 0
            
            
            if start_date is None or end_date is None:
                raise ValueError("start_date and end_date must not be None")
            
            # Generate report data
            report_data = {
                'period': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'summary': {
                    'total_inflows': inflows.count(),
                    'total_items': inflow_items.count(),
                    'total_value': float(total_value),
                    'average_value': float(avg_value)
                },
                'status_breakdown': {
                    status: inflows.filter(status=status).count()
                    for status in ['pending', 'approved', 'rejected']
                },
                'daily_totals': []
            }
            
            # Add daily breakdown
            current_date = start_date
            while current_date <= end_date:
                daily_inflows = inflows.filter(
                    created_at__date=current_date
                )
                daily_items = inflow_items.filter(
                    inflow__in=daily_inflows
                )
                
                daily_total = sum(
                    item.quantity * item.product.price 
                    for item in daily_items
                )
                
                report_data['daily_totals'].append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'inflows_count': daily_inflows.count(),
                    'items_count': daily_items.count(),
                    'total_value': float(daily_total)
                })
                
                current_date += timezone.timedelta(days=1)
            
            logger.info(
                "Daily inflow report generated successfully",
                extra={
                    'start_date': start_date,
                    'end_date': end_date,
                    'total_inflows': report_data['summary']['total_inflows']
                }
            )
            
            return report_data
            
        except Exception as e:
            logger.error(
                f"Error generating daily inflow report: {str(e)}",
                extra={
                    'start_date': start_date,
                    'end_date': end_date
                },
                exc_info=True
            )
            raise
    
    @staticmethod
    def generate_location_report(start_date=None, end_date=None, location_type='origin'):
        """
        Generate report by origin or destiny location
        
        Args:
            start_date (date, optional): Start date for report
            end_date (date, optional): End date for report
            location_type (str): 'origin' or 'destiny'
            
        Returns:
            dict: Report data with:
                - Total inflows by location
                - Total value by location
                - Most transferred products
                - Average approval time
        """
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
            
        try:
            # Base queryset
            inflows = Inflow.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            
            # Group by location
            location_field = f"{location_type}__name"
            location_stats = inflows.values(location_field).annotate(
                total_inflows=Count('id'),
                total_value=Sum(
                    F('items__quantity') * F('items__product__price'),
                    output_field=fields.DecimalField()
                ),
                avg_approval_time=Avg(
                    ExpressionWrapper(
                        F('updated_at') - F('created_at'),
                        output_field=fields.DurationField()
                    ),
                    filter=Q(status='approved')
                )
            )
            
            # Most transferred products
            top_products = InflowItems.objects.filter(
                inflow__in=inflows
            ).values(
                'product__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_value=Sum(
                    F('quantity') * F('product__price'),
                    output_field=fields.DecimalField()
                )
            ).order_by('-total_quantity')[:10]
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'location_stats': list(location_stats),
                'top_products': list(top_products)
            }
            
        except Exception as e:
            logger.error(
                f"Error generating location report: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def generate_performance_report(start_date=None, end_date=None):
        """
        Generate performance report
        
        Returns:
            dict: Report data with:
                - Average approval time
                - Rejection rate
                - Common rejection reasons
                - Process bottlenecks
        """
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
            
        try:
            inflows = Inflow.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            
            # Calculate metrics
            total_inflows = inflows.count()
            rejected_inflows = inflows.filter(status='rejected')
            rejection_rate = (rejected_inflows.count() / total_inflows * 100) if total_inflows > 0 else 0
            
            # Approval time analysis
            approval_times = inflows.filter(
                status='approved'
            ).annotate(
                approval_time=ExpressionWrapper(
                    F('updated_at') - F('created_at'),
                    output_field=fields.DurationField()
                )
            ).aggregate(
                avg_time=Avg('approval_time'),
                min_time=Min('approval_time'),
                max_time=Max('approval_time')
            )
            
            # Rejection reasons
            rejection_reasons = rejected_inflows.values(
                'rejection_reason'
            ).annotate(
                count=Count('id')
            ).order_by('-count')
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'metrics': {
                    'total_inflows': total_inflows,
                    'rejected_inflows': rejected_inflows.count(),
                    'rejection_rate': rejection_rate,
                    'approval_times': approval_times
                },
                'rejection_reasons': list(rejection_reasons)
            }
            
        except Exception as e:
            logger.error(
                f"Error generating performance report: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def generate_product_report(start_date=None, end_date=None):
        """
        Generate product-focused report
        
        Returns:
            dict: Report data with:
                - Most received products
                - Price variations
                - Reception frequency
                - Low stock alerts
        """
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
            
        try:
            inflow_items = InflowItems.objects.filter(
                inflow__created_at__date__gte=start_date,
                inflow__created_at__date__lte=end_date
            ).select_related('product', 'inflow')
            
            # Product statistics
            product_stats = inflow_items.values(
                'product__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_value=Sum(
                    F('quantity') * F('product__price'),
                    output_field=fields.DecimalField()
                ),
                avg_price=Avg('product__price'),
                reception_count=Count('inflow_id', distinct=True)
            ).order_by('-total_quantity')
            
            # Low stock alerts
            low_stock_products = inflow_items.values(
                'product__name',
                'product__min_quantity'
            ).annotate(
                current_quantity=Sum('quantity')
            ).filter(
                current_quantity__lte=F('product__min_quantity')
            )
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'product_stats': list(product_stats),
                'low_stock_alerts': list(low_stock_products)
            }
            
        except Exception as e:
            logger.error(
                f"Error generating product report: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def generate_financial_report(start_date=None, end_date=None):
        """
        Generate financial report
        
        Returns:
            dict: Report data with:
                - Total value by period
                - Month-over-month comparison
                - Historical projections
                - Cost analysis by product
        """
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=365)
        if not end_date:
            end_date = timezone.now().date()
            
        try:
            # Monthly aggregation
            monthly_stats = InflowItems.objects.filter(
                inflow__created_at__date__gte=start_date,
                inflow__created_at__date__lte=end_date
            ).annotate(
                month=TruncMonth('inflow__created_at')
            ).values('month').annotate(
                total_value=Sum(
                    F('quantity') * F('product__price'),
                    output_field=fields.DecimalField()
                ),
                total_items=Count('id'),
                avg_item_value=Avg(
                    F('quantity') * F('product__price'),
                    output_field=fields.DecimalField()
                )
            ).order_by('month')
            
            # Product cost analysis
            product_costs = InflowItems.objects.filter(
                inflow__created_at__date__gte=start_date,
                inflow__created_at__date__lte=end_date
            ).values(
                'product__name'
            ).annotate(
                total_cost=Sum(
                    F('quantity') * F('product__price'),
                    output_field=fields.DecimalField()
                ),
                avg_cost=Avg('product__price'),
                min_cost=Min('product__price'),
                max_cost=Max('product__price')
            ).order_by('-total_cost')
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'monthly_stats': list(monthly_stats),
                'product_costs': list(product_costs)
            }
            
        except Exception as e:
            logger.error(
                f"Error generating financial report: {str(e)}",
                exc_info=True
            )
            raise
    
    @staticmethod
    def generate_audit_report(start_date=None, end_date=None):
        """
        Generate audit report
        
        Returns:
            dict: Report data with:
                - Change history
                - Approval/rejection logs
                - Responsible tracking
                - Process anomalies
        """
        if not start_date:
            start_date = timezone.now().date() - timezone.timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()
            
        try:
            inflows = Inflow.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).select_related('created_by', 'updated_by')
            
            # Status changes
            status_changes = inflows.values(
                'status',
                'updated_by__email',
                'updated_at'
            ).order_by('updated_at')
            
            # User activity
            user_activity = inflows.values(
                'created_by__email'
            ).annotate(
                created_count=Count('id', filter=Q(created_by=F('created_by'))),
                approved_count=Count('id', filter=Q(status='approved', updated_by=F('created_by'))),
                rejected_count=Count('id', filter=Q(status='rejected', updated_by=F('created_by')))
            )
            
            # Anomaly detection (e.g., multiple status changes in short time)
            anomalies = inflows.annotate(
                changes_count=Count('id'),
                time_between_changes=ExpressionWrapper(
                    F('updated_at') - F('created_at'),
                    output_field=fields.DurationField()
                )
            ).filter(
                Q(changes_count__gt=3) |  # More than 3 changes
                Q(time_between_changes__lt=timezone.timedelta(minutes=5))  # Changes in less than 5 minutes
            )
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'status_changes': list(status_changes),
                'user_activity': list(user_activity),
                'anomalies': list(anomalies.values())
            }
            
        except Exception as e:
            logger.error(
                f"Error generating audit report: {str(e)}",
                exc_info=True
            )
            raise