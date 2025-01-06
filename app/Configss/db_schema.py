from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone
from enum import Enum

class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = 'tasks'
    
    task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_name: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc)
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="other"
    )
    
    # sub_tasks = relationship("Sub_task", back_populates="task")
    
    def __init__(self, file_name: str, status: str = "other"):
        self.file_name = file_name
        self.status = status
    
    
    def set_status(self, new_status: str) -> None: 
        if isinstance(new_status, str): 
            self.status = new_status
    
    def __repr__(self):
        return f"Task(task_id={self.task_id}, name={self.file_name}, created_at={self.created_at}, status={self.status})"



# class Sub_task(Base):
#     __tablename__ = 'sub_tasks'
    
#     sub_task_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     task_id: Mapped[int] = mapped_column(
#         Integer,
#         ForeignKey('tasks.task_id', ondelete='CASCADE'),
#         nullable=False
#     )
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         nullable=False,
#         default=datetime.now(timezone.utc)

#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime,
#         nullable=False,
#         default=datetime.now(timezone.utc),
#         onupdate=datetime.now(timezone.utc)
#     )
#     curr_status: Mapped[Sub_status] = mapped_column(  #
#         Enum(Sub_status),
#         nullable=False,
#         default=Sub_status.created
#     )
    
#     task = relationship("Task", back_populates="sub_tasks")
    
    
#     def set_status(self, new_status: Sub_status) -> None:  
#         if isinstance(new_status, Sub_status): 
#             self.curr_status = new_status
    
#     def __repr__(self):
#         return f"Sub_task(sub_task_id={self.sub_task_id}, task_id={self.task_id}, created_at={self.created_at}, curr_status={self.curr_status})"