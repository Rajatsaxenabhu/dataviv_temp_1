
from datetime import datetime, timedelta, timezone
# from celery.signals import task_retry, task_failure, task_postrun, task_internal_error
from redis import Redis
import json
import logging

from app.database.postgres.deps import PostgresDb
from app.database.postgres.models.tasks import CelerySubTaskModel, CeleryTaskModel
from app.tasks.config import celery as celery_app


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# redis client
redis_client = Redis(
    host='redis',
    port=6379,
    db=1
)


@celery_app.task(name="add")
def add_numbers(x, y):
    print(x + y)
    session = PostgresDb().session()
    print(session)
    return x+y


# @celery_app.task(name='main_task')
# def main_task(file_location: str, total_time: int, gap_time: int):
#     task_group_id = f"main_task:{main_task.request.id}"
#     total_iterations_subtask = int((total_time*60)/gap_time)

#     now = datetime.now(timezone.utc)
#     print(f"Main task {task_group_id} started at {now}")
#     for i in range(total_iterations_subtask):
#         eta_time = now + timedelta(seconds=(i+1)*int(gap_time))
#         taskk = sub_task.celery_apply_async((file_location,), eta=eta_time)

#         print(f"Subtask {taskk.task_id} scheduled for execution at {eta_time}")
#     return "Main task executed and subtasks scheduled."


# @celery_app.task(name='sub_task', bind=True)
# def sub_task(self, file_location):
#     session = PostgresDb().session()

#     current_time = datetime.now(timezone.utc)+timedelta(hours=5, minutes=30)
#     try:
#         with open(file_location, 'a') as f:
#             f.write(
#                 f"The will print by the sub task and execute at {current_time} \n")
#         self.update_state(state="PROGRESS", meta={'progress': 50})
#         return True
#     except Exception as e:
#         print(f"Error writing to file {file_location}: {str(e)}")
#         return False


# @celery_app.task(name='final_ending_task')
# def finalize_task(task_group_id):
#     metadata = json.loads(redis_client.get(task_group_id))
#     metadata["status"] = "SUCCESS"
#     redis_client.set(task_group_id, json.dumps(metadata))
#     # login to main data
#     print("final task executed and complete all the completed task")


# @task_postrun.connect
# def handle_task_postrun(task_id, task, state, **kwargs):
#     print(f'let print the {kwargs}')

#     print(f'after this {task_id} state is {state}')
#     pass


# @task_failure.connect()
# def handle_task_failure(sender, **kwargs):
#     pass


# @task_retry.connect()
# def handle_task_retry(sender, **kwargs):
#     pass


# @celery_app.task(name='main_task_progress_from_redis')
# def main_task_progress_from_redis(task_group_id):
#     metadata = json.loads(redis_client.get(task_group_id))
#     print(metadata)
