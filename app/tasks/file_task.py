from datetime import datetime, timedelta, timezone
from celery.signals import task_retry, task_failure, task_postrun, task_internal_error
from redis import Redis
import json
import logging
from app.database.postgres.models.tasks import CelerySubTaskModel

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


@celery_app.task(name='main_task')
def main_task(file_location: str, total_time: int, gap_time: int):
    print(f"Total time is {total_time} and gap time is {gap_time}")

    #session is open
    session = PostgresDb().session()
    
    #main task id
    # task_group_id = f"main_task:{main_task.request.id}"
    # total_iterations_subtask = int((total_time*60)/gap_time)

    # now = datetime.now(timezone.utc)
    # # now update the main task
    # main_task_update = session.query(CeleryTaskModel).filter_by(task_group_id=task_group_id).first()
    # main_task_update.set_status("RUNNING")
    # main_task_update.total_sub_tasks = total_iterations_subtask
    # main_task_update.remaining_sub_tasks = total_iterations_subtask
    # session.commit()
    # print(f"Main task {task_group_id} started at {now}")
    # for i in range(total_iterations_subtask):
    #     eta_time = now + timedelta(seconds=(i+1)*int(gap_time))
    #     taskk = sub_task.apply_async((file_location,), eta=eta_time)
    #     sub_task_update=CelerySubTaskModel(sub_task_group_id=task_group_id,curr_status="PENDING",sub_task_id=taskk.id)
    #     session.add(sub_task_update)
    #     session.commit()
    #     print(f"Subtask {taskk.task_id} scheduled for execution at {eta_time}")
    # return "Main task executed and subtasks scheduled."
    return "main task tmpe1"


@celery_app.task(name='sub_task', bind=True)
def sub_task(self, file_location):
    #working on sub task
    current_time = datetime.now(timezone.utc)+timedelta(hours=5, minutes=30)
    try:
        with open(file_location, 'a') as f:
            f.write(
                f"The will print by the sub task and execute at {current_time} \n")
        self.update_state(state="PROGRESS")
        return True
    except Exception as e:
        print(f"Error writing to file {file_location}: {str(e)}")
        return False


@celery_app.task(name='final_ending_task')
def finalize_task(task_group_id):
    metadata = json.loads(redis_client.get(task_group_id))
    metadata["status"] = "SUCCESS"
    redis_client.set(task_group_id, json.dumps(metadata))
    # login to main data
    print("final task executed and complete all the completed task")


# @task_postrun.connect
# def handle_task_postrun(task_id, task, state, **kwargs):
#     session = PostgresDb().session()
#     if state == "SUCCESS":
#         sub_task_update = session.query(CelerySubTaskModel).filter_by(sub_task_internal_id=task_id).first()
#         sub_task_update.set_status("SUCCESS")
#         main_task_update = session.query(CeleryTaskModel).filter_by(task_group_id=sub_task_update.task_group_id).first()
#         main_task_update.remaining_sub_tasks -= 1
#         main_task_update.progress = ((main_task_update.total_sub_tasks - main_task_update.remaining_sub_tasks)/main_task_update.total_sub_tasks)*100
#         session.commit()
#     if state == "FAILURE":
#         sub_task_update = session.query(CelerySubTaskModel).filter_by(sub_task_internal_id=task_id).first()
#         sub_task_update.set_status("FAILURE")
#         main_task_update = session.query(CeleryTaskModel).filter_by(task_group_id=sub_task_update.task_group_id).first()
#         main_task_update.set_status("FAILURE")
#         session.commit()
#     print(f'let print the {kwargs}')
#     print(f'after this {task_id} state is {state}')


@task_failure.connect()
def handle_task_failure(sender, **kwargs):
    pass


@task_retry.connect()
def handle_task_retry(sender, **kwargs):
    pass


@celery_app.task(name='main_task_progress_from_redis')
def main_task_progress_from_redis(task_group_id):
    metadata = json.loads(redis_client.get(task_group_id))
    print(metadata)
