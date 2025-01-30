from celery import shared_task
from django.utils import timezone
from .models import Inflow, InflowItems
from django.db.models import Count, Sum
import logging

logger = logging.getLogger(__name__)


@shared_task(name='inflows.tasks.generate_daily_inflow_report')
def generate_daily_inflow_report():
    today = timezone.now().date()
    start_date = today - timezone.timedelta(days=7)
    end_date = today
    
    try:
        total_inflow = Inflow.objects.filter(created_at__gte=start_date, created_at__lte=end_date).count()
        logger.info(f"[INFLOWS TASK] Total inflow for {today}: {total_inflow}")
        return {"total_inflows": total_inflow}
    except Exception as e:
        logger.error(f"[INFLOWS TASK] Error generating daily inflow report: {str(e)}")
        return {"detail": str(e)}