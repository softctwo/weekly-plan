"""
任务和复盘Schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from ..models.task import TaskStatus, TaskSource, FollowUpAction


# WeeklyTask Schemas
class WeeklyTaskBase(BaseModel):
    """周任务基础Schema"""
    title: str
    description: Optional[str] = None
    source_type: TaskSource = TaskSource.RESPONSIBILITY
    linked_task_type_id: Optional[int] = None
    is_key_task: bool = False


class WeeklyTaskCreate(WeeklyTaskBase):
    """创建周任务 - REQ-3.1"""
    week_number: int
    year: int


class WeeklyTaskUpdate(BaseModel):
    """更新周任务"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    is_key_task: Optional[bool] = None


class WeeklyTask(WeeklyTaskBase):
    """周任务响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    week_number: int
    year: int
    status: TaskStatus
    assigned_by_manager_id: Optional[int] = None
    is_delayed_from_previous: bool
    original_week: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# TaskReview Schemas
class TaskReviewBase(BaseModel):
    """任务复盘基础Schema"""
    is_completed: bool
    incomplete_reason: Optional[str] = None
    follow_up_action: Optional[FollowUpAction] = None
    notes: Optional[str] = None


class TaskReviewCreate(TaskReviewBase):
    """创建任务复盘 - REQ-4.1 ~ REQ-4.4"""
    task_id: int


class TaskReview(TaskReviewBase):
    """任务复盘响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    reviewed_at: datetime


# ReportComment Schemas
class ReportCommentBase(BaseModel):
    """周报评论基础Schema"""
    content: str


class ReportCommentCreate(ReportCommentBase):
    """创建周报评论 - REQ-5.3"""
    user_id: int
    week_number: int
    year: int


class ReportComment(ReportCommentBase):
    """周报评论响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    week_number: int
    year: int
    manager_id: int
    is_reviewed: bool
    created_at: datetime
