"""
用户和组织架构模型
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class Department(Base):
    """部门表 - REQ-1.2"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="部门名称")
    parent_id = Column(Integer, ForeignKey("departments.id"), nullable=True, comment="父部门ID")
    description = Column(String(500), comment="部门描述")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    parent = relationship("Department", remote_side=[id], backref="children")
    users = relationship("User", back_populates="department")


class User(Base):
    """用户表 - REQ-1.1"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="密码哈希")
    full_name = Column(String(100), nullable=False, comment="姓名")

    # 组织关系 - REQ-1.2
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # 汇报关系 - REQ-1.4
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="直属上级ID")

    # 用户角色
    user_type = Column(String(20), default="employee", comment="用户类型: admin/manager/employee")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    department = relationship("Department", back_populates="users")
    manager = relationship("User", remote_side=[id], backref="subordinates")

    # 多对多关系：用户-岗位 - REQ-1.3
    roles = relationship("Role", secondary="user_role_links", back_populates="users")

    # 一对多关系
    weekly_tasks = relationship("WeeklyTask", back_populates="user", foreign_keys="WeeklyTask.user_id")
    assigned_tasks = relationship("WeeklyTask", back_populates="assigner", foreign_keys="WeeklyTask.assigned_by_manager_id")
    comments = relationship("ReportComment", back_populates="manager")
