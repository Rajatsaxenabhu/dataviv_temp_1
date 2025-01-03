from celery import Celery
from datetime import datetime, timedelta
from celery.signals import celeryd_after_setup

# Initialize Celery
apps = Celery('file_task', broker='redis://redis:6379')
apps.conf.result_backend = 'db+postgresql://postgres:postgres@postgres-db:5432/celery'

# This decorator ensures the task is registered with Celery
@apps.task(name='file_worker')
def file_worker(file_location, start_time):
    """Write current time to file every 10 seconds for 1 minute"""
    # Convert start_time to datetime if it's serialized
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    
    current_time = datetime.now()
    print("Inside the task")

    # Check if 1 minute has elapsed
    if current_time - start_time > timedelta(minutes=1):
        print(f"Task for {file_location} has finished (1 minute elapsed)")
        return False

    try:
        with open(file_location, 'a') as f:
            f.write(f"The current time is: {current_time}\n")
        print(f"Task scheduled again in 10 seconds for {file_location}.")
        file_worker.apply_async(args=[file_location, start_time], countdown=10)
        return True
    except Exception as e:
        print(f"Error writing to file {file_location}: {str(e)}")
        return False
