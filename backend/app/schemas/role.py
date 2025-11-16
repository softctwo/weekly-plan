"""
岗位职责Schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# TaskType Schemas
class TaskTypeBase(BaseModel):
    """任务类型基础Schema"""
    name: str
    description: Optional[str] = None
    sort_order: int = 0


class TaskTypeCreate(TaskTypeBase):
    """创建任务类型"""
    responsibility_id: int


class TaskType(TaskTypeBase):
    """任务类型响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    responsibility_id: int
    is_active: bool
    created_at: datetime


# Responsibility Schemas
class ResponsibilityBase(BaseModel):
    """职责基础Schema"""
    name: str
    description: Optional[str] = None
    sort_order: int = 0


class ResponsibilityCreate(ResponsibilityBase):
    """创建职责"""
    role_id: int


class Responsibility(ResponsibilityBase):
    """职责响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role_id: int
    is_active: bool
    created_at: datetime
    task_types: List[TaskType] = []


# Role Schemas
class RoleBase(BaseModel):
    """岗位基础Schema"""
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """创建岗位"""
    pass


class Role(RoleBase):
    """岗位响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    responsibilities: List[Responsibility] = []
