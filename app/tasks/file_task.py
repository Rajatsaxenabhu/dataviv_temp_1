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
def main_task(file_name: str, file_unique_name: str, file_location: str, total_time: int, gap_time: int)->str:
    print(f"Total time is {total_time} and gap time is {gap_time}")

    #session is open
    try:
        with PostgresDb().session() as session:
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
            print(f"Main task {main_task_id} started at {now}")
            for i in range(total_sub_tasks):
                eta_time = now + timedelta(seconds=(i+1)*int(gap_time))
                subtask = sub_task.apply_async((file_location,), eta=eta_time)
                sub_task_update=CelerySubTaskModel(
                    sub_task_id=subtask.id,
                    sub_task_main_id = main_task_id,
                )
                session.add(sub_task_update)
                logger.info(f"Scheduled subtask {subtask.id} for {eta_time}")
            session.commit()
            print(f"Subtask {subtask.task_id} scheduled for execution at {eta_time}")
            return "Main task executed and subtasks scheduled."
        
    except Exception as e:
        logger.error(f"Error in main_task: {str(e)}")
        session.rollback()
        raise


@celery_app.task(name='sub_task', bind=True)
def sub_task(self, file_location)->bool:
    #working on sub task
    self.update_state(state="PROGRESS")
    current_time = datetime.now(timezone.utc)+timedelta(hours=5, minutes=30)

    # logic karo idhar apna
    try:
        with open(file_location, 'a') as f:
            f.write(
                f"The will print by the sub task and execute at {current_time} \n")
        # self.state = "SUCCESS"
        return True
    except Exception as e:
        print(f"Error writing to file {file_location}: {str(e)}")
        return False

@task_postrun.connect
def handle_task_postrun(task_id: str, task: any, state: str, **kwargs):
    """
    Updates task statuses and progress after task completion.
    """
    try:
        with PostgresDb().session() as session:
            # Get subtask record
            subtask = session.execute(
                select(CelerySubTaskModel)
                .where(CelerySubTaskModel.sub_task_id == task_id)
            ).scalar_one_or_none()
            
            if not subtask:
                return None

            # Get main task record
            main_task = session.execute(
                select(CeleryTaskModel)
                .where(CeleryTaskModel.main_task_id == subtask.sub_task_main_id)
            ).scalar_one_or_none()
            
            if not main_task:
                return None

            # Update statuses and progress
            subtask.status = state
            remaining_tasks = main_task.remaining_sub_tasks

            if state == "SUCCESS":
                main_task.progress = ((main_task.total_sub_tasks-(main_task.remaining_sub_tasks-1))/main_task.total_sub_tasks)*100
                if remaining_tasks <= 1:
                    main_task.status = "SUCCESS"
                    main_task.progress = 100.0
                main_task.remaining_sub_tasks = max(0, remaining_tasks - 1)
                
            elif state == "FAILURE":
                main_task.status = "FAILURE"
                
            elif state == "PROGRESS":
                completed_tasks = main_task.total_sub_tasks - remaining_tasks
                main_task.progress = (completed_tasks / main_task.total_sub_tasks) * 100

            session.commit()
            return subtask
            
    except Exception as e:
        logger.error(f"Error in task_postrun: {str(e)}")
        session.rollback()
        raise

# @task_failure.connect()
# def handle_task_failure(sender, **kwargs):
#     pass


# @task_retry.connect()
# def handle_task_retry(sender, **kwargs):
#     pass
