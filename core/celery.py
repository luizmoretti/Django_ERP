import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Configure periodic tasks
app.conf.beat_schedule = {
    'generate-daily-inflow-report': {
        'task': 'generate_daily_inflow_report',
        'schedule': crontab(minute='*/1'),  # Runs every 1 minute
        'options': {'queue': 'warehouse'},
    },
    'check-low-stock': {
        'task': 'check_low_stock',
        'schedule': crontab(minute='*/1'),  # Runs every 1 minute
        'options': {'queue': 'warehouse'},
    },
    # 'check-specific-product': {
        # 'task': 'check_specific_product',
        # 'schedule': crontab(minute='*/1'),  # Runs every 1 minute
        # 'options': {'queue': 'warehouse'},
    # }
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')