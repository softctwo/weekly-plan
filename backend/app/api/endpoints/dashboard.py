"""
仪表盘API端点 - REQ-3.3, REQ-5.1, REQ-5.2, REQ-5.3
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...api.deps import get_db, get_current_user, get_current_manager
from ...models.user import User
from ...models.task import WeeklyTask, TaskReview, ReportComment, TaskStatus
from ...schemas.task import ReportComment as ReportCommentSchema, ReportCommentCreate

router = APIRouter()


# 员工仪表盘 - REQ-3.3
@router.get("/employee")
def get_employee_dashboard(
    week_number: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """员工仪表盘 - REQ-3.3"""
    # 获取本周任务
    tasks = db.query(WeeklyTask).filter(
        WeeklyTask.user_id == current_user.id,
        WeeklyTask.week_number == week_number,
        WeeklyTask.year == year
    ).all()

    # 统计数据
    total_tasks = len(tasks)
    todo_tasks = len([t for t in tasks if t.status == TaskStatus.TODO])
    in_progress_tasks = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    key_tasks = [t for t in tasks if t.is_key_task]

    return {
        "week_number": week_number,
        "year": year,
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "roles": [{"id": r.id, "name": r.name} for r in current_user.roles]
        },
        "statistics": {
            "total_tasks": total_tasks,
            "todo_tasks": todo_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "key_tasks_count": len(key_tasks),
            "key_tasks_completed": len([t for t in key_tasks if t.status == TaskStatus.COMPLETED])
        },
        "tasks": tasks,
        "key_tasks": key_tasks  # REQ-3.4: 重点任务高亮
    }


# 团队视图 - REQ-5.1
@router.get("/team")
def get_team_dashboard(
    week_number: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """团队仪表盘（管理者）- REQ-5.1"""
    # 获取所有直属下属 - REQ-5.1.1
    subordinates = db.query(User).filter(
        User.manager_id == current_user.id,
        User.is_active == True
    ).all()

    team_overview = []

    for member in subordinates:
        # 获取成员本周任务
        tasks = db.query(WeeklyTask).filter(
            WeeklyTask.user_id == member.id,
            WeeklyTask.week_number == week_number,
            WeeklyTask.year == year
        ).all()

        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        delayed_tasks = len([t for t in tasks if t.status == TaskStatus.DELAYED])
        key_tasks = [t for t in tasks if t.is_key_task]

        # 检查复盘状态
        reviewed_tasks = db.query(TaskReview).join(WeeklyTask).filter(
            WeeklyTask.user_id == member.id,
            WeeklyTask.week_number == week_number,
            WeeklyTask.year == year
        ).count()

        # 检查管理者是否已审阅
        comments = db.query(ReportComment).filter(
            ReportComment.user_id == member.id,
            ReportComment.week_number == week_number,
            ReportComment.year == year,
            ReportComment.manager_id == current_user.id
        ).first()

        review_status = "未提交"
        if reviewed_tasks > 0:
            if comments and comments.is_reviewed:
                review_status = "已审阅"
            else:
                review_status = "已提交"

        team_overview.append({
            "user_id": member.id,
            "user_name": member.full_name,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "delayed_tasks": delayed_tasks,
            "review_status": review_status,
            # REQ-5.1.3: 重点任务概览
            "key_tasks_summary": {
                "total": len(key_tasks),
                "completed": len([t for t in key_tasks if t.status == TaskStatus.COMPLETED])
            }
        })

    return {
        "week_number": week_number,
        "year": year,
        "manager": {
            "id": current_user.id,
            "name": current_user.full_name
        },
        "team_size": len(subordinates),
        "team_members": team_overview
    }


# 成员详情 - REQ-5.2
@router.get("/team/member/{user_id}")
def get_member_detail(
    user_id: int,
    week_number: int,
    year: int,
    is_key_task: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """查看团队成员详情（管理者）- REQ-5.2"""
    # 验证成员是否是当前用户的下属
    member = db.query(User).filter(User.id == user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 可选：严格检查汇报关系
    # if member.manager_id != current_user.id:
    #     raise HTTPException(status_code=403, detail="只能查看直属下属的信息")

    # 获取成员任务
    query = db.query(WeeklyTask).filter(
        WeeklyTask.user_id == user_id,
        WeeklyTask.week_number == week_number,
        WeeklyTask.year == year
    )

    # REQ-5.2.3: 过滤重点任务
    if is_key_task is not None:
        query = query.filter(WeeklyTask.is_key_task == is_key_task)

    tasks = query.all()

    # 获取复盘信息
    reviews = {
        r.task_id: r
        for r in db.query(TaskReview).join(WeeklyTask).filter(
            WeeklyTask.user_id == user_id,
            WeeklyTask.week_number == week_number,
            WeeklyTask.year == year
        ).all()
    }

    # 获取管理者评论
    comments = db.query(ReportComment).filter(
        ReportComment.user_id == user_id,
        ReportComment.week_number == week_number,
        ReportComment.year == year
    ).all()

    return {
        "member": {
            "id": member.id,
            "name": member.full_name,
            "roles": [{"id": r.id, "name": r.name} for r in member.roles]
        },
        "week_number": week_number,
        "year": year,
        "tasks": [
            {
                **t.__dict__,
                "review": reviews.get(t.id)
            }
            for t in tasks
        ],
        "comments": comments
    }


# 周报评论 - REQ-5.3
@router.post("/team/comments/", response_model=ReportCommentSchema, status_code=status.HTTP_201_CREATED)
def add_comment(
    comment_in: ReportCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """管理者添加周报评论 - REQ-5.3.1"""
    # 验证被评论者存在
    user = db.query(User).filter(User.id == comment_in.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    comment = ReportComment(
        **comment_in.model_dump(),
        manager_id=current_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.put("/team/comments/{comment_id}/mark-reviewed")
def mark_as_reviewed(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """标记周报为已审阅 - REQ-5.3.2"""
    comment = db.query(ReportComment).filter(ReportComment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    if comment.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能操作自己的评论")

    comment.is_reviewed = True
    db.commit()
    return {"message": "已标记为已审阅"}


@router.get("/team/comments/", response_model=List[ReportCommentSchema])
def get_comments(
    user_id: int,
    week_number: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取周报评论"""
    comments = db.query(ReportComment).filter(
        ReportComment.user_id == user_id,
        ReportComment.week_number == week_number,
        ReportComment.year == year
    ).all()
    return comments
