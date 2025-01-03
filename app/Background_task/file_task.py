from celery import Celery
from datetime import datetime, timedelta
import os
# from .config_schema import Settings
# setting_objs=Settings()
# back_db_address=setting_objs.DB_ADDRESS
# brok_redis_address=setting_objs.REDIS_ADDRESS
apps = Celery('file_task', backend='db+postgresql://postgres:postgres@postgres-db:5432/celery',broker='redis://redis:6379')

apps.conf.result_backend = 'db+postgresql://postgres:postgres@postgres-db:5432/celery'
@apps.task(name='runn_background_task')
def runn_background_task():
    for i in range(10):
        print(f"Background task running {i}")

@apps.task(name='file_worker')
def file_worker(file_path: str,start_time: datetime):
    current_time = datetime.now()
    elapsed_time = current_time - start_time
    if elapsed_time < timedelta(minutes=10):
        with open(file_path, 'a') as f:
            f.write(f"the current time is : {datetime.now()}\n")
        file_worker.apply_async(args=[file_path,start_time], countdown=60)
    else:
        print(f"Task completed for {file_path}. 1 hour has passed.")
