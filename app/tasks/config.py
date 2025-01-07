from celery import Celery


app = Celery(__name__)
app.conf.broker_url = "redis://redis:6379/0"
# app.conf.result_backend = 'db+postgresql://postgres:akfjlkwf1p29i491i@postgres:5432/postgres'
app.conf.result_backend = "redis://redis:6379/0"
app.conf.worker_send_task_events = True
