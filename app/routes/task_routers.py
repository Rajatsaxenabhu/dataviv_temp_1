from fastapi import APIRouter, File, UploadFile, Depends
from app.tasks.file_task import main_task
import shutil
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.postgres.deps import get_db
from Configss.db_schema import Task


router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    new_file_name = file.filename
    file_location = f"./work_dir/{new_file_name}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    schedule_time = 1
    gap_time = 10
    task = main_task.apply_async(
        args=[file_location, schedule_time, gap_time])
    print(task.id)
    print("this is the ", task.id)
    new_task = Task(file_name=new_file_name, status="READY",
                    task_internal_id=task.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    print("file uploaded successfully")
    return {"filename": file.filename}


@router.get("/get_tasks/")
async def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return {"tasks": tasks}
