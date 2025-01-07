from fastapi import FastAPI, File, UploadFile,Depends
from Background_task.file_task import main_task
import shutil
from sqlalchemy.orm import Session
from datetime import datetime
from Configss.config_schema import get_db
from Configss.db_schema import Task
from sqlalchemy_utils import database_exists, create_database
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...),db:Session=Depends(get_db)):
    new_file_name = file.filename
    file_location = f"./work_dir/{new_file_name}"    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    schedule_time=1 # in minutes
    gap_time=10 # in seconds
    tasky=main_task.apply_async(args=[file_location,schedule_time,gap_time])
    print("this is the ",tasky.task_id)
    new_task = Task(file_name=new_file_name,status="READY",task_internal_id=tasky.task_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    print("file uploaded successfully")
    return {"filename": file.filename}

@app.get("/get_tasks/")
async def get_tasks(db:Session=Depends(get_db)):
    tasks = db.query(Task).all()
    return {"tasks": tasks}

    
