"""
岗位职责模型
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.base import Base


class UserRoleLink(Base):
    """用户-岗位关联表 - REQ-1.3 (多对多)"""
    __tablename__ = "user_role_links"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Role(Base):
    """岗位库/模板表 - REQ-2.1"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, comment="岗位名称")
    name_en = Column(String(100), comment="岗位英文名/缩写")
    description = Column(String(500), comment="岗位描述")

    # 停用规则 - REQ-2.4
    is_active = Column(Boolean, default=True, comment="是否启用（停用后不在创建计划时出现）")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    responsibilities = relationship("Responsibility", back_populates="role", cascade="all, delete-orphan")
    users = relationship("User", secondary="user_role_links", back_populates="roles")


class Responsibility(Base):
    """职责库 - REQ-2.2"""
    __tablename__ = "responsibilities"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="所属岗位ID")
    name = Column(String(200), nullable=False, comment="职责名称")
    description = Column(String(500), comment="职责描述")
    sort_order = Column(Integer, default=0, comment="排序序号")

    # 停用规则 - REQ-2.4
    is_active = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    role = relationship("Role", back_populates="responsibilities")
    task_types = relationship("TaskType", back_populates="responsibility", cascade="all, delete-orphan")


class TaskType(Base):
    """标准任务类型库 - REQ-2.3"""
    __tablename__ = "task_types"

    id = Column(Integer, primary_key=True, index=True)
    responsibility_id = Column(Integer, ForeignKey("responsibilities.id"), nullable=False, comment="所属职责ID")
    name = Column(String(200), nullable=False, comment="任务类型名称")
    description = Column(String(500), comment="任务类型描述")
    sort_order = Column(Integer, default=0, comment="排序序号")

    # 停用规则 - REQ-2.4
    is_active = Column(Boolean, default=True, comment="是否启用")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    responsibility = relationship("Responsibility", back_populates="task_types")
    weekly_tasks = relationship("WeeklyTask", back_populates="task_type")
