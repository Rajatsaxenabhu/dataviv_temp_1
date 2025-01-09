from app.routes.task_routers import router as task_router

from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(
    task_router,
    prefix='/tasks',
    tags=['Tasks']
)
