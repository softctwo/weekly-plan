"""
任务和复盘模型
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from ..db.base import Base


class TaskStatus(str, Enum):
    """任务状态枚举"""
    TODO = "todo"  # 待办
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    DELAYED = "delayed"  # 已延期
    CANCELLED = "cancelled"  # 已取消


class TaskSource(str, Enum):
    """任务来源枚举"""
    RESPONSIBILITY = "responsibility"  # 来自职责
    MANAGER_ASSIGNED = "manager_assigned"  # 领导安排
    PERSONAL = "personal"  # 个人临时


class FollowUpAction(str, Enum):
    """后续动作枚举 - REQ-4.4"""
    DELAY_TO_NEXT_WEEK = "delay_to_next_week"  # 延期至下周
    CANCEL = "cancel"  # 取消任务


class WeeklyTask(Base):
    """周计划任务表 - REQ-3.1, REQ-3.3"""
    __tablename__ = "weekly_tasks"
    __table_args__ = (
        # 复合索引优化常见查询
        Index('idx_user_week', 'user_id', 'year', 'week_number'),  # 按用户和周次查询
        Index('idx_status_key', 'status', 'is_key_task'),  # 按状态和重点任务过滤
        Index('idx_user_status', 'user_id', 'status'),  # 按用户和状态查询
    )

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="所属用户ID")
    week_number = Column(Integer, nullable=False, index=True, comment="周次（如：202447）")
    year = Column(Integer, nullable=False, comment="年份")

    title = Column(String(500), nullable=False, comment="任务标题")
    description = Column(Text, comment="任务详细描述")

    # 任务来源与关联 - REQ-3.1.2
    source_type = Column(
        SQLEnum(TaskSource),
        nullable=False,
        default=TaskSource.RESPONSIBILITY,
        comment="任务来源"
    )
    linked_task_type_id = Column(
        Integer,
        ForeignKey("task_types.id"),
        nullable=True,
        comment="关联的标准任务类型ID（可追溯职责）"
    )

    # 领导指派 - REQ-5.4
    assigned_by_manager_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="指派该任务的管理者ID"
    )

    # 重点标识 - REQ-3.1.3, REQ-3.4
    is_key_task = Column(Boolean, default=False, comment="是否为重点工作")

    # 状态
    status = Column(
        SQLEnum(TaskStatus),
        nullable=False,
        default=TaskStatus.TODO,
        comment="任务状态"
    )

    # 延期标识 - REQ-3.2
    is_delayed_from_previous = Column(Boolean, default=False, comment="是否为上周延期任务")
    original_week = Column(Integer, nullable=True, comment="原始周次（延期任务）")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")

    # 关系
    user = relationship("User", back_populates="weekly_tasks", foreign_keys=[user_id])
    assigner = relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_by_manager_id])
    task_type = relationship("TaskType", back_populates="weekly_tasks")
    review = relationship("TaskReview", back_populates="task", uselist=False)


class TaskReview(Base):
    """任务复盘表 - REQ-4.1 ~ REQ-4.4"""
    __tablename__ = "task_reviews"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("weekly_tasks.id"), nullable=False, unique=True, comment="任务ID")

    # 复盘信息
    is_completed = Column(Boolean, nullable=False, comment="是否完成")

    # 未完成处理 - REQ-4.3, REQ-4.4
    incomplete_reason = Column(String(500), nullable=True, comment="未完成原因（未完成时必填）")
    follow_up_action = Column(
        SQLEnum(FollowUpAction),
        nullable=True,
        comment="后续动作（未完成时必填）"
    )

    # 其他信息
    notes = Column(Text, comment="复盘备注")
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now(), comment="复盘时间")

    # 关系
    task = relationship("WeeklyTask", back_populates="review")


class ReportComment(Base):
    """周报评论表 - REQ-5.3"""
    __tablename__ = "report_comments"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="被评论者ID")
    week_number = Column(Integer, nullable=False, comment="周次")
    year = Column(Integer, nullable=False, comment="年份")

    # 评论者（管理者）
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评论者（管理者）ID")

    # 评论内容
    content = Column(Text, nullable=False, comment="评论/辅导建议")

    # 审阅状态 - REQ-5.3.2
    is_reviewed = Column(Boolean, default=False, comment="是否已标记为已审阅")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    manager = relationship("User", back_populates="comments", foreign_keys=[manager_id])
