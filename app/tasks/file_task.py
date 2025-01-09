from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from celery.signals import task_retry, task_failure, task_postrun, task_internal_error
from redis import Redis

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


@celery_app.task(name='main_task')
def main_task(file_name: str, file_unique_name: str, file_location: str, total_time: int, gap_time: int):
    print(f"Total time is {total_time} and gap time is {gap_time}")

    #session is open
    session = PostgresDb().session()
    
    #main task id
    main_task_id = f"main_task:{main_task.request.id}"
    main_task_id=main_task_id[10:]
    total_sub_tasks= int((total_time*60)/gap_time)

    now = datetime.now(timezone.utc)
    new_task = CeleryTaskModel(
        file_name=file_name,
        file_unique_name=file_unique_name,
        file_path=file_location,
        main_task_id=main_task_id,
        total_sub_tasks=total_sub_tasks,
 )
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    print(f"Main task {main_task_id} started at {now}")
    for i in range(total_sub_tasks):
        eta_time = now + timedelta(seconds=(i+1)*int(gap_time))
        taskk = sub_task.apply_async((file_location,), eta=eta_time)
        print("this is  the main sub id is ",taskk.id)
        sub_task_update=CelerySubTaskModel(
            sub_task_id=taskk.id,
            sub_task_main_id = main_task_id,
        )
        session.add(sub_task_update)
        session.commit()
        print(f"Subtask {taskk.task_id} scheduled for execution at {eta_time}")
    return "Main task executed and subtasks scheduled."


@celery_app.task(name='sub_task', bind=True)
def sub_task(self, file_location):
    #working on sub task
    self.state="PROGRESS"
    current_time = datetime.now(timezone.utc)+timedelta(hours=5, minutes=30)
    try:
        with open(file_location, 'a') as f:
            f.write(
                f"The will print by the sub task and execute at {current_time} \n")
        self.state = "SUCCESS"
        return True
    except Exception as e:
        print(f"Error writing to file {file_location}: {str(e)}")
        self.state = "FAILURE"
        return False

@task_postrun.connect
def handle_task_postrun(task_id, task, state, **kwargs):
    try:
        with PostgresDb().session() as session:
            post_task = session.query(CelerySubTaskModel).filter(CelerySubTaskModel.sub_task_id == task_id).first()
            if not post_task:
                return None
            main_task_action=session.query(CeleryTaskModel).filter(CeleryTaskModel.main_task_id == post_task.sub_task_main_id).first()
            if state == "SUCCESS":
                post_task.status = "SUCCESS"
                
                if main_task_action.remaining_sub_tasks==1:
                    main_task_action.status="SUCCESS"
                else:
                    main_task_action.remaining_sub_tasks=main_task_action.remaining_sub_tasks-1
            elif state == "FAILURE":
                post_task.status = "FAILURE"
                main_task_action.status="FAILURE"

            elif state == "PROGRESS":
                post_task.status = "PROGRESS"
            main_task_action.progress=main_task_action.total_sub_tasks-main_task_action.remaining_sub_tasks/main_task_action.total_sub_tasks*100
            
            session.commit()
            return post_task
               
    except Exception as e:
        session.rollback()
        raise

@task_failure.connect()
def handle_task_failure(sender, **kwargs):
    pass


@task_retry.connect()
def handle_task_retry(sender, **kwargs):
    pass
