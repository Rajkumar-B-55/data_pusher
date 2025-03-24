import os
from celery import Celery

from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "data_pusher.settings")

celery_app = Celery("data_pusher")
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

celery_app.autodiscover_tasks(['core'])


@celery_app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
