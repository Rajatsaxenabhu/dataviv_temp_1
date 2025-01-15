from celery import Celery
from celery.signals import task_retry, task_failure, task_postrun, task_internal_error
from app.database.postgres.deps import PostgresDbContext
from sqlalchemy import select
from app.database.postgres.models.tasks import CelerySubTaskModel, CeleryTaskModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

celery = Celery(__name__)
celery.conf.broker_url = "redis://redis:6379/0"
celery.conf.result_backend = "redis://redis:6379/0"
celery.autodiscover_tasks(['app.tasks.image_task','app.tasks.audio_task'])
celery.conf.timezone = "UTC"
celery.conf.enable_utc = True
@task_postrun.connect
def handle_task_postrun(task_id: str, task: any, state: str, **kwargs):
    """
    Updates task statuses and progress after task completion.
    """
    try:
        with PostgresDbContext() as session:
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

@task_failure.connect()
def handle_task_failure(sender, **kwargs):
    # login for failure 
    pass


