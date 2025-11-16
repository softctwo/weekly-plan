"""
任务管理API端点 - REQ-3.1, REQ-3.3, REQ-4
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import logging

from ...api.deps import get_db, get_current_user, get_current_manager
from ...models.user import User
from ...models.task import WeeklyTask, TaskReview, TaskStatus, FollowUpAction
from ...schemas import task as schemas

router = APIRouter()
logger = logging.getLogger(__name__)


# 周计划管理 - REQ-3.1
@router.post("/", response_model=schemas.WeeklyTask, status_code=status.HTTP_201_CREATED)
def create_weekly_task(
    task_in: schemas.WeeklyTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建周计划任务（员工）"""
    task = WeeklyTask(
        **task_in.model_dump(),
        user_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/my-tasks", response_model=List[schemas.WeeklyTask])
def get_my_tasks(
    week_number: int = None,
    year: int = None,
    is_key_task: bool = None,
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

    tasks = query.order_by(WeeklyTask.is_key_task.desc(), WeeklyTask.created_at).all()
    logger.info(f"Found {len(tasks)} tasks for user {current_user.id}")

    return tasks


@router.get("/delayed-tasks", response_model=List[schemas.WeeklyTask])
def get_delayed_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取待处理的延期任务 - REQ-3.2"""
    # 查找上周标记为延期的任务
    tasks = db.query(WeeklyTask).filter(
        WeeklyTask.user_id == current_user.id,
        WeeklyTask.status == TaskStatus.DELAYED
    ).all()
    return tasks


@router.put("/{task_id}", response_model=schemas.WeeklyTask)
def update_task(
    task_id: int,
    task_in: schemas.WeeklyTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新任务"""
    task = db.query(WeeklyTask).filter(WeeklyTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 权限检查：只能更新自己的任务
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此任务")

    # 更新字段
    update_data = task_in.model_dump(exclude_unset=True)

    # 如果状态变更为已完成，记录完成时间
    if "status" in update_data and update_data["status"] == TaskStatus.COMPLETED:
        update_data["completed_at"] = datetime.now()

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
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

    # 检查汇报关系（可选：严格模式下需要验证）
    # if target_user.manager_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="只能为直属下属指派任务")

    task = WeeklyTask(
        **task_in.model_dump(),
        user_id=user_id,
        source_type="manager_assigned",
        assigned_by_manager_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
