from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import List

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"
    
    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    task_internal_id: Mapped[str | None] = mapped_column(String(40))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    progress: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    total_sub_tasks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    remaining_sub_tasks: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="READY"
    )
    
    sub_tasks: Mapped[List["Sub_task"]] = relationship(
        "Sub_task",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    
    def __init__(self, file_name: str, status: str,task_internal_id: str) -> None:
        self.file_name = file_name
        self.status = status
        self.task_internal_id=task_internal_id
    
    def set_status(self, new_status: str) -> None:
        self.status = new_status
    
    def __repr__(self) -> str:
        return (f"Task(task_id={self.task_id}, "
                f"file_name={self.file_name}, "
                f"status={self.status})")



class Sub_task(Base):
    __tablename__ = "sub_tasks"
    
    sub_task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    main_task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    
    curr_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="PENDING" # pending, running, success, failure
    )
    
    task: Mapped["Task"] = relationship("Task", back_populates="sub_tasks")
    
    def __init__(self,main_task_id: str,curr_status: str) -> None:
        self.main_task_id = main_task_id
        self.curr_status = curr_status

    def set_status(self, new_status: str) -> None:
        self.curr_status = new_status
    
    def __repr__(self) -> str:
        return (f"Sub_task(sub_task_id={self.sub_task_id}, "
                f"task_id={self.task_id}, "
                f"created_at={self.created_at}, "
                f"status={self.curr_status})")