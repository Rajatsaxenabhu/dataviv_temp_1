from celery import Celery
from datetime import datetime, timedelta,timezone
from celery.signals import celeryd_after_setup

# Initialize Celery
apps = Celery('file_task', broker='redis://redis:6379')
apps.conf.result_backend = 'db+postgresql://postgres:postgres@postgres-db:5432/celery'

@apps.task(name='runn_main_task')
def main_task(file_location,total_time,gap_time):
    now = datetime.now(timezone.utc)
    print(f"Main task started at {now}")
    ans=(total_time*60)/gap_time
    for i in range(1, int(ans)):
        eta_time = now + timedelta(seconds=i*int(gap_time))  
        file_worker.apply_async((file_location,), eta=eta_time)
        print(f"Sub-task {i} scheduled at {eta_time}")
    return "Main task executed and subtasks scheduled."

@apps.task(name='file_worker',bind=True)
def file_worker(self,file_location):
    print("Inside the sub_task")
    current_time = datetime.now(timezone.utc)+timedelta(hours=5, minutes=30)
    print("file locatio is ",file_location)
    try:
        with open(file_location, 'a') as f:
            f.write(f"The will print by the sub task and execute at {current_time} \n")
        self.update_state(state="PROGRESS", meta={'progress': 50})
        return True
    except Exception as e:
        print(f"Error writing to file {file_location}: {str(e)}")
        return False