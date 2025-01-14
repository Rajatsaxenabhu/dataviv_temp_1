from fastapi import APIRouter, File,Depends
from datetime import datetime,timezone
from datetime import time
from app.database.postgres.deps import get_db
from app.tasks.audio_task import capture_audio_task
from app.tasks.image_task import capture_image_task
from fastapi.responses import JSONResponse
from pydantic import BaseModel
router = APIRouter()
stop_processing = False
class image_time(BaseModel):
    # from datetime import datetime, timezone,timedelta
    # from datetime import time
    # # Your original time
    # another_time = datetime(2025, 1, 10, 18, 0, 0)
    # another_time2=datetime(2025, 1, 11, 0, 0, 0)
    # #now the time is coming
    # interval=time
    # # Convert to UTC by adding timezone information
    # ans = another_time.replace(tzinfo=timezone.utc)
    # ans2= another_time2.replace(tzinfo=timezone.utc)

    # total_seconds = interval.hour * 3600 + interval.minute * 60 + interval.second
    # interval_delta = timedelta(seconds=total_seconds)

    # main_second=(ans2-ans).total_seconds()
    # print("total_sec",int(main_second))
    # print('total_interval',total_seconds)
    start_date:datetime
    end_date:datetime
    interval:time
    server_link:str

class audio_time(BaseModel):
    start_time:datetime
    end_time:datetime
    capture_interval:time
    skip_interval:time
    

@router.post('/image/')
async def image(payload: image_time):
    server_link='rtp://@224.0.0.1:5004' 
    # for testing we use the local video
    server_link='app/videos/rajat.mp4'
    ans=capture_image_task.apply_async(
        args=[
        payload.start_date,
        payload.end_date,
        payload.interval,
        server_link])
    return JSONResponse(content={"task_id": ans.id})

@router.post('/audio/')
async def audio(payload: audio_time):
    server_link='rtp://@224.0.0.1:5004'
    # for testing we use the local video
    server_link='app/videos/rajat.mp4'
    ans=capture_audio_task.apply_async(
        args=[
        payload.start_time,
        payload.end_time,
        payload.capture_interval,
        payload.skip_interval,
        server_link,])        
    return JSONResponse(
        content={"task_id": ans.id} 
    ) 