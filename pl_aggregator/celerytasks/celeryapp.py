from celery import Celery

from ..configs import get_settings

settings = get_settings()

celeryapp = Celery('celeryapp')
celeryapp.conf.broker_url = settings.celery_broker_url
celeryapp.conf.result_backend = settings.celery_result_backend
celeryapp.conf.result_extended = True
