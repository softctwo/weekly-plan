"""
任务和复盘Schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from ..models.task import TaskStatus, TaskSource, FollowUpAction


# WeeklyTask Schemas
class WeeklyTaskBase(BaseModel):
    """周任务基础Schema - 优化版：增加时间属性，强制岗责关联"""
    title: str
    description: Optional[str] = None
    source_type: TaskSource = TaskSource.RESPONSIBILITY
    linked_task_type_id: int  # 改为必填：强制关联岗责
    is_key_task: bool = False
    
    # 新增：时间属性
    planned_start_time: datetime  # 计划开始时间
    planned_end_time: datetime    # 计划结束时间
    planned_duration: Optional[int] = None  # 可选，由API自动计算


class WeeklyTaskCreate(WeeklyTaskBase):
    """创建周任务 - REQ-3.1"""
    week_number: int
    year: int


class WeeklyTaskUpdate(BaseModel):
    """更新周任务 - 支持时间属性更新"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    is_key_task: Optional[bool] = None
    
    # 新增：时间属性更新
    planned_start_time: Optional[datetime] = None
    planned_end_time: Optional[datetime] = None
    
    # 实际执行时间（复盘时更新）
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None


class WeeklyTask(WeeklyTaskBase):
    """周任务响应Schema - 包含时间属性"""
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
    
    # 新增：时间属性
    actual_start_time: Optional[datetime] = None
    actual_end_time: Optional[datetime] = None
    actual_duration: Optional[int] = None


class CarryOverRequest(BaseModel):
    """延期任务带入请求"""
    task_ids: List[int]
    target_week_number: int
    target_year: int


class CarryOverResult(BaseModel):
    """延期任务带入结果"""
    model_config = ConfigDict(from_attributes=True)

    created_task_ids: List[int]
    failed_task_ids: List[int] = []


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
