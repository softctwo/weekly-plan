"""
任务管理API端点 - REQ-3.1, REQ-3.3, REQ-4
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
import logging

from ...api.deps import get_db, get_current_user, get_current_manager
from ...models.user import User
from ...models.task import WeeklyTask, TaskReview, TaskStatus, FollowUpAction
from ...models.role import TaskType, Responsibility, Role
from ...schemas import task as schemas
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


# 周计划管理 - REQ-3.1
@router.post("/", response_model=schemas.WeeklyTask, status_code=status.HTTP_201_CREATED)
def create_weekly_task(
    task_in: schemas.WeeklyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建周计划任务（员工）- 优化版：强制岗责关联，增加时间属性"""
    
    # 验证任务类型存在且属于当前用户的岗位职责
    if task_in.linked_task_type_id:
        # 检查任务类型是否存在
        task_type = db.query(TaskType).filter(TaskType.id == task_in.linked_task_type_id).first()
        if not task_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的任务类型不存在"
            )
        
        # 验证该任务类型属于用户的某个岗位
        user_roles = db.query(Role).join(User.roles).filter(User.id == current_user.id).all()
        user_role_ids = [role.id for role in user_roles]
        
        # 检查任务类型是否属于用户的岗位职责
        responsibility = db.query(Responsibility).join(Responsibility.task_types).filter(
            Responsibility.role_id.in_(user_role_ids),
            TaskType.id == task_in.linked_task_type_id
        ).first()
        
        if not responsibility:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="该任务类型不属于您的岗位职责范围"
            )
    
    # 验证时间逻辑
    if task_in.planned_start_time >= task_in.planned_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="计划开始时间必须早于结束时间"
        )
    
    # 计算计划持续时间（分钟）
    planned_duration = int((task_in.planned_end_time - task_in.planned_start_time).total_seconds() / 60)
    
    task = WeeklyTask(
        **task_in.model_dump(exclude={'planned_duration'}),  # 排除重复的planned_duration
        user_id=current_user.id,
        planned_duration=planned_duration
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(f"用户 {current_user.id} 创建了任务 '{task.title}'，关联职责: {task_type.name if task_type else '无'}")
    return task


@router.get("/my-tasks", response_model=List[schemas.WeeklyTask])
def get_my_tasks(
    week_number: int = None,
    year: int = None,
    is_key_task: bool = None,
    source_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取我的任务列表 - REQ-3.3

    使用joinedload优化关联查询，避免N+1问题
    """
    logger.info(f"Fetching tasks for user {current_user.id}, week={week_number}, year={year}")

    # 使用joinedload预加载关联数据，避免N+1查询
    query = db.query(WeeklyTask).options(
        joinedload(WeeklyTask.task_type),
        joinedload(WeeklyTask.assigner),
        joinedload(WeeklyTask.review)
    ).filter(WeeklyTask.user_id == current_user.id)

    if week_number:
        query = query.filter(WeeklyTask.week_number == week_number)
    if year:
        query = query.filter(WeeklyTask.year == year)
    if is_key_task is not None:
        query = query.filter(WeeklyTask.is_key_task == is_key_task)
    if source_type:
        query = query.filter(WeeklyTask.source_type == source_type)

    tasks = query.order_by(WeeklyTask.is_key_task.desc(), WeeklyTask.created_at).all()
    logger.info(f"Found {len(tasks)} tasks for user {current_user.id}")

    return tasks


@router.get("/delayed-tasks", response_model=List[schemas.WeeklyTask])
def get_delayed_tasks(
    week_number: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取待处理的延期任务 - REQ-3.2"""
    # 默认使用当前周的上一周
    if not week_number or not year:
        today = datetime.utcnow().date()
        iso_year, iso_week, _ = today.isocalendar()
        base_dt = datetime.strptime(f"{iso_year}-W{iso_week}-1", "%G-W%V-%u")
        prev_dt = base_dt - timedelta(days=7)
        year = prev_dt.isocalendar()[0]
        week_number = prev_dt.isocalendar()[1]

    tasks = db.query(WeeklyTask).filter(
        WeeklyTask.user_id == current_user.id,
        WeeklyTask.status == TaskStatus.DELAYED,
        WeeklyTask.week_number == week_number,
        WeeklyTask.year == year,
    ).all()
    return tasks


@router.put("/{task_id}", response_model=schemas.WeeklyTask)
def update_task(
    task_id: int,
    task_in: schemas.WeeklyTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新任务 - 支持时间属性更新，智能计算持续时间"""
    task = db.query(WeeklyTask).filter(WeeklyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 权限检查：只能更新自己的任务
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此任务")

    # 更新字段
    update_data = task_in.model_dump(exclude_unset=True)

    # 验证时间逻辑
    if "planned_start_time" in update_data and "planned_end_time" in update_data:
        if update_data["planned_start_time"] >= update_data["planned_end_time"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划开始时间必须早于结束时间"
            )
        # 重新计算计划持续时间
        update_data["planned_duration"] = int(
            (update_data["planned_end_time"] - update_data["planned_start_time"]).total_seconds() / 60
        )
    elif "planned_start_time" in update_data:
        # 只更新了开始时间，重新计算持续时间
        end_time = update_data.get("planned_end_time", task.planned_end_time)
        if update_data["planned_start_time"] >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划开始时间必须早于结束时间"
            )
        update_data["planned_duration"] = int(
            (end_time - update_data["planned_start_time"]).total_seconds() / 60
        )
    elif "planned_end_time" in update_data:
        # 只更新了结束时间，重新计算持续时间
        start_time = update_data.get("planned_start_time", task.planned_start_time)
        if start_time >= update_data["planned_end_time"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="计划开始时间必须早于结束时间"
            )
        update_data["planned_duration"] = int(
            (update_data["planned_end_time"] - start_time).total_seconds() / 60
        )

    # 如果状态变更为已完成，记录完成时间和实际持续时间
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.now()
        if "actual_end_time" not in update_data:
            update_data["actual_end_time"] = datetime.now()
        # 如果有实际开始时间，计算实际持续时间
        if "actual_start_time" in update_data or task.actual_start_time:
            start_time = update_data.get("actual_start_time", task.actual_start_time)
            end_time = update_data.get("actual_end_time", update_data["completed_at"])
            if start_time and end_time:
                update_data["actual_duration"] = int((end_time - start_time).total_seconds() / 60)

    # 如果状态变更为进行中，记录实际开始时间
    if "status" in update_data and update_data["status"] == TaskStatus.IN_PROGRESS:
        if "actual_start_time" not in update_data and not task.actual_start_time:
            update_data["actual_start_time"] = datetime.now()

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    
    logger.info(f"用户 {current_user.id} 更新了任务 {task_id}，状态: {task.status}")
    return task


# 周复盘 - REQ-4
@router.post("/reviews/", response_model=schemas.TaskReview, status_code=status.HTTP_201_CREATED)
def create_task_review(
    review_in: schemas.TaskReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建任务复盘 - REQ-4.1 ~ REQ-4.4"""
    # 验证任务存在且属于当前用户
    task = db.query(WeeklyTask).filter(WeeklyTask.id == review_in.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限复盘此任务")

    # REQ-4.3, REQ-4.4: 未完成任务必须填写原因和后续动作
    if not review_in.is_completed:
        if not review_in.incomplete_reason:
            raise HTTPException(status_code=400, detail="未完成任务必须填写未完成原因")
        if not review_in.follow_up_action:
            raise HTTPException(status_code=400, detail="未完成任务必须选择后续动作")

    # 创建复盘记录
    review = TaskReview(**review_in.model_dump())
    db.add(review)

    # 更新任务状态
    if review_in.is_completed:
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
    else:
        # 根据后续动作更新任务状态
        if review_in.follow_up_action == FollowUpAction.DELAY_TO_NEXT_WEEK:
            task.status = TaskStatus.DELAYED
        elif review_in.follow_up_action == FollowUpAction.CANCEL:
            task.status = TaskStatus.CANCELLED

    db.commit()
    db.refresh(review)
    return review


class ReviewFallbackRequest(BaseModel):
    """未复盘兜底请求"""
    week_number: int
    year: int


@router.post("/reviews/fallback", response_model=schemas.CarryOverResult)
def apply_review_fallback(
    fallback_in: ReviewFallbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    未复盘兜底：将未复盘且未完成的任务标记为延期并自动滚动到下一周
    """
    tasks = db.query(WeeklyTask).filter(
        WeeklyTask.user_id == current_user.id,
        WeeklyTask.week_number == fallback_in.week_number,
        WeeklyTask.year == fallback_in.year,
        WeeklyTask.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
    ).all()

    created_ids: List[int] = []
    failed_ids: List[int] = []

    def _next_week(year: int, week: int):
        base = datetime.strptime(f"{year}-W{week}-1", "%G-W%V-%u")
        nxt = base + timedelta(days=7)
        return nxt.isocalendar()[0], nxt.isocalendar()[1]

    next_year, next_week = _next_week(fallback_in.year, fallback_in.week_number)

    for task in tasks:
        # 创建复盘记录，标记为未完成超时
        if db.query(TaskReview).filter(TaskReview.task_id == task.id).first():
            continue
        review = TaskReview(
            task_id=task.id,
            is_completed=False,
            incomplete_reason="超时未复盘",
            follow_up_action=FollowUpAction.DELAY_TO_NEXT_WEEK,
            notes=None
        )
        task.status = TaskStatus.DELAYED
        task.is_delayed_from_previous = True
        task.original_week = task.week_number
        db.add(review)

        try:
            new_task = WeeklyTask(
                title=task.title,
                description=task.description,
                user_id=task.user_id,
                week_number=next_week,
                year=next_year,
                status=TaskStatus.TODO,
                is_key_task=task.is_key_task,
                source_type=task.source_type,
                linked_task_type_id=task.linked_task_type_id,
                assigned_by_manager_id=task.assigned_by_manager_id,
                planned_start_time=task.planned_start_time + timedelta(days=7),
                planned_end_time=task.planned_end_time + timedelta(days=7),
                planned_duration=task.planned_duration,
                is_delayed_from_previous=True,
                original_week=task.week_number,
            )
            db.add(new_task)
            db.flush()
            created_ids.append(new_task.id)
        except Exception:
            failed_ids.append(task.id)

    db.commit()
    return schemas.CarryOverResult(created_task_ids=created_ids, failed_task_ids=failed_ids)


@router.get("/weekly-report")
def get_weekly_report(
    week_number: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成周报 - REQ-4.5"""
    # 获取本周所有任务
    tasks = db.query(WeeklyTask).filter(
        WeeklyTask.user_id == current_user.id,
        WeeklyTask.week_number == week_number,
        WeeklyTask.year == year
    ).all()

    # 统计数据
    completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    incomplete_tasks = [t for t in tasks if t.status in [TaskStatus.DELAYED, TaskStatus.CANCELLED]]
    key_tasks = [t for t in tasks if t.is_key_task]

    # 构建周报
    report = {
        "week_number": week_number,
        "year": year,
        "user": {
            "id": current_user.id,
            "name": current_user.full_name
        },
        "summary": {
            "total_tasks": len(tasks),
            "completed_count": len(completed_tasks),
            "incomplete_count": len(incomplete_tasks),
            "completion_rate": len(completed_tasks) / len(tasks) * 100 if tasks else 0,
            "key_tasks_count": len(key_tasks),
            "key_tasks_completed": len([t for t in key_tasks if t.status == TaskStatus.COMPLETED])
        },
        "key_tasks": [  # REQ-4.5.2: 重点工作置顶
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "is_completed": t.status == TaskStatus.COMPLETED,
                "review": db.query(TaskReview).filter(TaskReview.task_id == t.id).first()
            }
            for t in key_tasks
        ],
        "completed_tasks": [{"id": t.id, "title": t.title} for t in completed_tasks],
        "incomplete_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "review": db.query(TaskReview).filter(TaskReview.task_id == t.id).first()
            }
            for t in incomplete_tasks
        ]
    }

    return report


# 管理者指派任务 - REQ-5.4
@router.post("/assign/", response_model=schemas.WeeklyTask, status_code=status.HTTP_201_CREATED)
def assign_task(
    user_id: int,
    task_in: schemas.WeeklyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """管理者为下属指派任务 - REQ-5.4"""
    # 验证被指派者存在且是当前用户的下属
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查汇报关系（严格模式）
    if target_user.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能为直属下属指派任务")

    payload = task_in.model_dump()
    # 确保来源被覆盖为领导安排，防止请求体篡改
    payload.pop("source_type", None)

    # 计算计划时长
    if payload.get("planned_start_time") and payload.get("planned_end_time"):
        if payload["planned_start_time"] >= payload["planned_end_time"]:
            raise HTTPException(status_code=400, detail="计划开始时间必须早于结束时间")
        payload["planned_duration"] = int(
            (payload["planned_end_time"] - payload["planned_start_time"]).total_seconds() / 60
        )
    else:
        raise HTTPException(status_code=400, detail="缺少计划开始/结束时间")

    task = WeeklyTask(
        **payload,
        user_id=user_id,
        source_type="manager_assigned",
        assigned_by_manager_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.post("/carry-over", response_model=schemas.CarryOverResult)
def carry_over_tasks(
    payload: schemas.CarryOverRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    将上周延期任务自动带入新周计划
    """
    tasks = db.query(WeeklyTask).filter(
        WeeklyTask.id.in_(payload.task_ids),
        WeeklyTask.user_id == current_user.id
    ).all()

    created_task_ids: List[int] = []
    failed_task_ids: List[int] = []

    for task in tasks:
        if task.status != TaskStatus.DELAYED:
            failed_task_ids.append(task.id)
            continue

        try:
            new_task = WeeklyTask(
                title=task.title,
                description=task.description,
                user_id=current_user.id,
                week_number=payload.target_week_number,
                year=payload.target_year,
                status=TaskStatus.TODO,
                is_key_task=task.is_key_task,
                source_type=task.source_type,
                linked_task_type_id=task.linked_task_type_id,
                assigned_by_manager_id=task.assigned_by_manager_id,
                planned_start_time=task.planned_start_time + timedelta(days=7),
                planned_end_time=task.planned_end_time + timedelta(days=7),
                planned_duration=task.planned_duration,
                is_delayed_from_previous=True,
                original_week=task.week_number
            )
            db.add(new_task)
            db.flush()
            created_task_ids.append(new_task.id)
        except Exception:
            failed_task_ids.append(task.id)

    db.commit()
    return schemas.CarryOverResult(created_task_ids=created_task_ids, failed_task_ids=failed_task_ids)
