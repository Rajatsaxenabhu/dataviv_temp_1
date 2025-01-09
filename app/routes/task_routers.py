from fastapi import APIRouter, File, UploadFile, Depends
import shutil
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.postgres.deps import get_db
from app.tasks.file_task import main_task
import uuid
import os
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_name = file.filename
    time_name=datetime.now().strftime("%Y%m%d%H%M%S")
    temp_file_name, ext = os.path.splitext(file_name)
    file_unique_name = f"{temp_file_name}_{time_name}{ext}"
    file_location = f"app/work_dir/{file_unique_name}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    schedule_time = 1
    gap_time = 10
    task = main_task.apply_async(
        args=[file_name,file_unique_name,file_location, schedule_time, gap_time])
    print("this is the ", task.id)
    print("file uploaded successfully")
    return JSONResponse(content={"message": "File uploaded successfully",
                                 "file_name": file_name,
                                 "file_unique_name": file_unique_name,}
                                )
