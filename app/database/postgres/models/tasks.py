from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, backref
from datetime import datetime, timezone, timedelta
from typing import List
import uuid
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.ext.hybrid import hybrid_property
from app.database.postgres.models.base import Base

def get_ist_time():
    # this is the india time
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)

class CeleryTaskModel(Base):
    __tablename__ = "celery_tasks"
    
    uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), 
        index=True, 
        unique=True,
        nullable=False,
        default=uuid.uuid4
    )

    file_name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=False)

    file_unique_name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
        
    file_path: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=False)
    
    progress: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1)

    total_sub_tasks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    remaining_sub_tasks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="READY")

    main_task_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=get_ist_time
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False,
        default=get_ist_time,
        onupdate=get_ist_time
    )

    # relationship
    sub_tasks: Mapped[List["CelerySubTaskModel"]] = relationship(
        "CelerySubTaskModel", 
        backref=backref("celery_task", passive_deletes=True),
        cascade="all, delete-orphan"
    )

    def __init__(self, file_name: str, file_unique_name: str, file_path: str, 
                 total_sub_tasks: int, main_task_id: str) -> None:
        self.file_name = file_name
        self.file_path = file_path
        self.file_unique_name = file_unique_name
        self.main_task_id = main_task_id
        self.remaining_sub_tasks = total_sub_tasks
        self.progress = 0
        self.total_sub_tasks = total_sub_tasks
        self.status = "RUNNING"

    
    def set_status(self, new_status: str) -> None:
        self.status = new_status

    def __repr__(self) -> str:
        return (f"Task(task_id={self.main_task_id}, "
                f"file_name={self.file_name}, "
                f"status={self.status})")

class CelerySubTaskModel(Base):
    __tablename__ = "celery_sub_tasks"

    uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), 
        index=True, 
        unique=True,
        nullable=False,
        default=uuid.uuid4
    )

    sub_task_main_id: Mapped[str] = mapped_column(
        String(255), 
        ForeignKey("celery_tasks.main_task_id", ondelete="CASCADE"), 
        nullable=False
    )
    
    sub_task_id: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=get_ist_time
    )
    
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING")

    def __init__(self, sub_task_id: str, sub_task_main_id: str) -> None:
        self.sub_task_id = sub_task_id
        self.sub_task_main_id = sub_task_main_id
        self.status = "PENDING"   

    def __repr__(self) -> str:
        return (f"Sub_task(sub_task_id={self.sub_task_id}, "
                f"task_id={self.sub_task_id}, "
                f"created_at={self.created_at}, "
                f"status={self.status})")  # Fixed from curr_status