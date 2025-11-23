"""
用户和组织架构Schemas
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from .role import Responsibility, TaskType


# Department Schemas
class DepartmentBase(BaseModel):
    """部门基础Schema"""
    name: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    """创建部门"""
    pass


class Department(DepartmentBase):
    """部门响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


# User Schemas
class UserBase(BaseModel):
    """用户基础Schema"""
    username: str
    email: EmailStr
    full_name: str
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    user_type: str = "employee"


class UserCreate(UserBase):
    """创建用户"""
    password: str


class UserUpdate(BaseModel):
    """更新用户"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    user_type: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRoleLink(BaseModel):
    """用户岗位关联"""
    role_id: int


class User(UserBase):
    """用户响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class UserInDB(User):
    """数据库中的用户（包含密码哈希）"""
    hashed_password: str


class Role(BaseModel):
    """角色Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_en: str
    description: str


class UserWithRoles(User):
    """包含角色信息的用户Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    user_type: str
    is_active: bool
    created_at: datetime
    roles: List[Role] = []


class UserRoleWithResponsibilities(BaseModel):
    """用户角色包含职责和任务类型"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_en: str
    description: str
    responsibilities: List[Responsibility] = []


class UserWithFullInfo(User):
    """包含完整信息的用户Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    user_type: str
    is_active: bool
    created_at: datetime
    roles: List[UserRoleWithResponsibilities] = []
