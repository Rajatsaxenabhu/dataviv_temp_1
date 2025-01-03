from Background_task.file_task import runn_background_task

def calling_background_task():
    print("fastapi main calling background task")
    runn_background_task.delay()
    return {"message": "main app return "}