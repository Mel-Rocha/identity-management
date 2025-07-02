from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from apps.core.logs import logger

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
logger.info("Celery is ready to process tasks.")