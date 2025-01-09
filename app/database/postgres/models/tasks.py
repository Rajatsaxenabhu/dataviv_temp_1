from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from datetime import datetime, timezone
from typing import List
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.database.postgres.models.base import Base


class CeleryTaskModel(Base):
    __tablename__ = "celery_tasks"
    uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), index=True, unique=True,nullable=False)

    file_name: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=False)
    
    file_unique_name: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now())    
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    total_sub_tasks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    remaining_sub_tasks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="READY")

    task_group_id: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True)
    
    error_message: Mapped[str] = mapped_column(
        String(1000), nullable=True)

    #relationship
    sub_tasks: Mapped[List["CelerySubTaskModel"]] = relationship(
        "CelerySubTaskModel", backref=backref("parent_task", passive_deletes=True),cascade="all, delete-orphan")

    def __init__(self, file_name: str, status: str, task_group_id: str,file_unique_name: str, file_path: str) -> None:
        self.file_name = file_name
        self.status = status
        self.task_group_id = task_group_id
        self.file_unique_name = file_unique_name
        self.file_path = file_path
        self.uid = uuid.uuid4()


    #pending, running, success, failure
    def set_status(self, new_status: str) -> None:
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def update_progress(self) -> None:
        self.remaining_sub_tasks=self.remaining_sub_tasks - 1 if self.remaining_sub_tasks > 0 else 0 
        self.progress=int((self.total_sub_tasks - self.remaining_sub_tasks)/self.total_sub_tasks*100)
        if self.progress == 100:
            self.status = "SUCCESS"
         
        
    
    def __repr__(self) -> str:
        return (f"Task(task_id={self.task_id}, "
                f"file_name={self.file_name}, "
                f"status={self.status})")


class CelerySubTaskModel(Base):
    __tablename__ = "celery_sub_tasks"

    uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), index=True, unique=True)

    sub_task_group_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        "celery_tasks.id", ondelete="CASCADE"), nullable=False)
    
    sub_task_id: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True)    

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now())
    
    # pending, running, success, failure
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING")

    task: Mapped["CeleryTaskModel"] = relationship(
        "CeleryTaskModel", backref=backref("celery_sub_tasks", passive_deletes=True))

    def __init__(self, task_group_id: str,sub_task_group_id: str, curr_status: str) -> None:
        self.task_group_id = task_group_id
        self.curr_status = curr_status
        self.uid = uuid.uuid4()
        self.sub_task_group_id = sub_task_group_id


    def set_status(self, new_status: str) -> None:
        self.curr_status = new_status

    def __repr__(self) -> str:
        return (f"Sub_task(sub_task_id={self.sub_task_id}, "
                f"task_id={self.task_id}, "
                f"created_at={self.created_at}, "
                f"status={self.curr_status})")
