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
        UUID(as_uuid=True), index=True, unique=True)

    file_name: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True)

    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    total_sub_tasks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    remaining_sub_tasks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="READY")

    sub_tasks: Mapped[List["CelerySubTaskModel"]] = relationship(
        "CelerySubTaskModel", backref=backref("celery_tasks", passive_deletes=True))

    def __init__(self, file_name: str, status: str, task_internal_id: str) -> None:
        self.file_name = file_name
        self.status = status
        self.task_internal_id = task_internal_id

    def set_status(self, new_status: str) -> None:
        self.status = new_status

    def __repr__(self) -> str:
        return (f"Task(task_id={self.task_id}, "
                f"file_name={self.file_name}, "
                f"status={self.status})")


class CelerySubTaskModel(Base):
    __tablename__ = "celery_sub_tasks"

    uid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), index=True, unique=True)

    task_id: Mapped[int] = mapped_column(Integer, ForeignKey(
        "celery_tasks.id", ondelete="CASCADE"), nullable=False)

    # pending, running, success, failure
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PENDING")

    task: Mapped["CeleryTaskModel"] = relationship(
        "CeleryTaskModel", backref=backref("celery_sub_tasks", passive_deletes=True))

    def __init__(self, main_task_id: str, curr_status: str) -> None:
        self.main_task_id = main_task_id
        self.curr_status = curr_status

    def set_status(self, new_status: str) -> None:
        self.curr_status = new_status

    def __repr__(self) -> str:
        return (f"Sub_task(sub_task_id={self.sub_task_id}, "
                f"task_id={self.task_id}, "
                f"created_at={self.created_at}, "
                f"status={self.curr_status})")
