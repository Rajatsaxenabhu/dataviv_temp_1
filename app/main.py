from fastapi import FastAPI, File, UploadFile
from Background_task.file_task import file_worker
import shutil
from datetime import datetime
app = FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"./work_dir/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    file_worker.apply_async(args=[file_location,datetime.now()])
    print("file uploaded successfully")
    return {"filename": file.filename}

    
