from fastapi import FastAPI, File, UploadFile,Depends
from Background_task.file_task import main_task
import shutil
from sqlalchemy.orm import Session
from datetime import datetime
from Configss.config_schema import get_db
from Configss.db_schema import Task
from sqlalchemy_utils import database_exists, create_database
import random
import string
app = FastAPI()


def generate_random_suffix(length=5):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...),db:Session=Depends(get_db)):
    new_file_name = file.filename
    existing_task = db.query(Task).filter(Task.file_name == new_file_name).first()
    if existing_task:
        random_suffix = generate_random_suffix()
        base_name, ext = file.filename.rsplit('.', 1)
        new_file_name = f"{base_name}_{random_suffix}.{ext}"
    
    file_location = f"./work_dir/{new_file_name}"    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    new_task = Task(file_name=new_file_name,status="pending")
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    schedule_time=1 # in minutes
    gap_time=10 # in seconds
    main_task.apply_async(args=[file_location,schedule_time,gap_time])
    print("file uploaded successfully")
    return {"filename": file.filename}

    
