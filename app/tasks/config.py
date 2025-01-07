from celery import Celery


celery = Celery(__name__)
celery.conf.broker_url = "redis://redis:6379/0"
# app.conf.result_backend = 'db+postgresql://postgres:akfjlkwf1p29i491i@postgres:5432/postgres'
celery.conf.result_backend = "redis://redis:6379/0"
# app.conf.worker_send_task_events = True
celery.autodiscover_tasks(['app.tasks.file_task'])
