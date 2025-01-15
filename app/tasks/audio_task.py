from app.tasks.config import celery as celery_app
import os
from datetime import time, datetime, timedelta, timezone
from celery.signals import task_retry, task_failure, task_postrun, task_internal_error
from typing import Optional, Tuple
import logging
from fastapi import HTTPException
from .ffmpeg import audio_capture

from app.database.postgres.deps import PostgresDb
from app.database.postgres.models.tasks import CelerySubTaskModel, CeleryTaskModel

# Configure logging with formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

output_dir = os.path.dirname('/static/audio/')
if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def time_to_timedelta(t: time) -> timedelta:
                return timedelta(
                    hours=t.hour,
                    minutes=t.minute,
                    seconds=t.second,
                    microseconds=t.microsecond
                )
@celery_app.task(name='audio_main_task', bind=True)
def capture_audio_task(self,start_date:datetime, end_date:datetime,capture_interval:time,skip_interval:time, server_link:str):
    
    try:
        with PostgresDb().session() as session:
            #main task id
            main_task_id = f"main_task:{capture_audio_task.request.id}"
            main_task_id=main_task_id[10:]
            total_interval=time_to_timedelta(capture_interval)+time_to_timedelta(skip_interval)
            total_sub_tasks= int((end_date-start_date).total_seconds()/total_interval.total_seconds())
            print("end",(end_date-start_date).total_seconds())
            print("total_interval",total_interval.total_seconds())
            total_sub_tasks= int((end_date-start_date).total_seconds()/total_interval.total_seconds())
            print('total_sub_task',total_sub_tasks)
            now=datetime.now(timezone.utc)
            time_name=datetime.now().strftime("%Y%m%d%H%M%S")
            file_unique_name=f"Audio_{time_name}"
            file_location = f"app/static/audio/{file_unique_name}"
            if not os.path.exists(file_location):
                os.makedirs(file_location)

            new_task = CeleryTaskModel(
                file_type='audio',
                file_unique_name=file_unique_name,
                file_path=file_location,
                main_task_id=main_task_id,
                total_sub_tasks=total_sub_tasks,
                )
            session.add(new_task)
            session.commit()
            print("Main task started at",now)
            for i in range(total_sub_tasks):
                eta_time = start_date + total_interval*i
                subtask = capture_audio_subtask.apply_async((server_link,file_location,capture_interval,), eta=eta_time)
                sub_task_update=CelerySubTaskModel(
                    sub_task_id=subtask.id,
                    sub_task_main_id = main_task_id,
                )
                session.add(sub_task_update)
            session.commit()
    except Exception as e:
        logger.error(f"Error in main_task: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

@celery_app.task(name='audio_sub_task', bind=True)
def capture_audio_subtask(self,server_link:str,savelocation:str,duration:time)->bool:
#     #working on sub task
    self.update_state(state="PROGRESS")
    current_time = datetime.now(timezone.utc)
    try:
        filenameprefix="audio"
        total_duration=duration.hour*3600+duration.minute*60+duration.second
        total_duration=int(total_duration)
        audio_capture(server_link,savelocation,filenameprefix,total_duration)
        #result
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return True