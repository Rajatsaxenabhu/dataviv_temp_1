from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone
from enum import Enum

class Base(DeclarativeBase):
    pass

class Sub_status(Enum):
    created = "created"
    pending = "pending"
    completed = "completed"
    failed = "failed"

class Task_status(Sub_status):
    other = "other"

class Task(Base):
    __tablename__ = 'tasks'
    
    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    status: Mapped[Task_status] = mapped_column( 
        Enum(Task_status),
        nullable=False,
        default=Task_status.other
    )
    
    sub_tasks = relationship("Sub_task", back_populates="task")
    
    def __init__(self, name: str):
        self.name = name
        self.status = Task_status.other
    
    
    def set_status(self, new_status: Task_status) -> None: 
        if isinstance(new_status, Task_status): 
            self.status = new_status
    
    def __repr__(self):
        return f"Task(task_id={self.task_id}, name={self.name}, created_at={self.created_at}, status={self.status})"

class Sub_task(Base):
    __tablename__ = 'sub_tasks'
    
    sub_task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('tasks.task_id', ondelete='CASCADE'),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc)

    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )
    curr_status: Mapped[Sub_status] = mapped_column(  #
        Enum(Sub_status),
        nullable=False,
        default=Sub_status.created
    )
    
    task = relationship("Task", back_populates="sub_tasks")
    
    
    def set_status(self, new_status: Sub_status) -> None:  
        if isinstance(new_status, Sub_status): 
            self.curr_status = new_status
    
    def __repr__(self):
        return f"Sub_task(sub_task_id={self.sub_task_id}, task_id={self.task_id}, created_at={self.created_at}, curr_status={self.curr_status})"