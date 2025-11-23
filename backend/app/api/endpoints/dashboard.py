"""
仪表盘API端点 - REQ-3.3, REQ-5.1, REQ-5.2, REQ-5.3
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ...api.deps import get_db, get_current_user, get_current_manager
from ...models.user import User
from ...models.task import WeeklyTask, TaskReview, ReportComment, TaskStatus
from ...models.role import TaskType, Responsibility
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
    source_type: Optional[str] = None,
    role_id: Optional[int] = None,
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
    query = db.query(WeeklyTask)

    # 按岗位过滤（通过任务类型关联的职责→岗位）
    if role_id:
        query = query.join(TaskType, WeeklyTask.linked_task_type_id == TaskType.id)\
            .join(Responsibility, Responsibility.id == TaskType.responsibility_id)\
            .filter(Responsibility.role_id == role_id)

    query = query.filter(
        WeeklyTask.user_id == user_id,
        WeeklyTask.week_number == week_number,
        WeeklyTask.year == year
    )

    # REQ-5.2.3: 过滤重点任务
    if is_key_task is not None:
        query = query.filter(WeeklyTask.is_key_task == is_key_task)
    if source_type:
        query = query.filter(WeeklyTask.source_type == source_type)

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


# 数据统计报表 - REQ-5.5
@router.get("/reports")
def get_reports(
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取数据统计报表"""
    try:
        # 解析日期
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # 确定查询范围 - 根据当前用户角色
        if current_user.user_type == "admin" or any("manager" in role.name.lower() for role in current_user.roles):
            # 管理者查看团队数据
            user_ids = db.query(User.id).filter(
                or_(
                    User.manager_id == current_user.id,
                    User.id == current_user.id
                )
            ).subquery()
        else:
            # 普通用户只看自己的数据
            user_ids = db.query(User.id).filter(User.id == current_user.id).subquery()

        # 基础统计查询
        base_query = db.query(WeeklyTask).filter(
            WeeklyTask.user_id.in_(user_ids),
            WeeklyTask.planned_start_time >= start_dt,
            WeeklyTask.planned_start_time <= end_dt
        )

        # 计算基础统计数据
        total_tasks = base_query.count()
        completed_tasks = base_query.filter(WeeklyTask.status == TaskStatus.COMPLETED).count()
        in_progress_tasks = base_query.filter(WeeklyTask.status == TaskStatus.IN_PROGRESS).count()
        todo_tasks = base_query.filter(WeeklyTask.status == TaskStatus.TODO).count()
        delayed_tasks = base_query.filter(WeeklyTask.status == TaskStatus.DELAYED).count()
        key_tasks = base_query.filter(WeeklyTask.is_key_task == True).count()
        key_completed_tasks = base_query.filter(
            WeeklyTask.is_key_task == True,
            WeeklyTask.status == TaskStatus.COMPLETED
        ).count()

        # 计算比率
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        key_completion_rate = (key_completed_tasks / key_tasks * 100) if key_tasks > 0 else 0
        delay_rate = (delayed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # 状态分布
        status_distribution = {
            "completed": completed_tasks,
            "in_progress": in_progress_tasks,
            "todo": todo_tasks,
            "delayed": delayed_tasks
        }

        # 周趋势数据
        weekly_trend = []
        current_week = start_dt.isocalendar().week
        current_year = start_dt.year
        end_week = end_dt.isocalendar().week
        end_year = end_dt.year

        while (current_year < end_year) or (current_year == end_year and current_week <= end_week):
            week_total = base_query.filter(
                WeeklyTask.week_number == current_week,
                WeeklyTask.year == current_year
            ).count()

            week_completed = base_query.filter(
                WeeklyTask.week_number == current_week,
                WeeklyTask.year == current_year,
                WeeklyTask.status == TaskStatus.COMPLETED
            ).count()

            week_rate = (week_completed / week_total * 100) if week_total > 0 else 0

            weekly_trend.append({
                "week": current_week,
                "year": current_year,
                "total": week_total,
                "completed": week_completed,
                "rate": round(week_rate, 1)
            })

            # 移动到下一周
            if current_week >= 52:
                current_week = 1
                current_year += 1
            else:
                current_week += 1

        # 团队成员绩效（仅管理者）
        member_performance = []
        if current_user.user_type == "admin" or any("manager" in role.name.lower() for role in current_user.roles):
            subordinates = db.query(User).filter(
                or_(
                    User.manager_id == current_user.id,
                    User.id == current_user.id
                ),
                User.is_active == True
            ).all()

            for member in subordinates:
                member_tasks = base_query.filter(WeeklyTask.user_id == member.id).all()
                member_total = len(member_tasks)
                member_completed = len([t for t in member_tasks if t.status == TaskStatus.COMPLETED])
                member_key_tasks = len([t for t in member_tasks if t.is_key_task])
                member_completion_rate = (member_completed / member_total * 100) if member_total > 0 else 0

                # 计算平均完成时间（简化版）
                avg_days = 0
                completed_with_time = [t for t in member_tasks if t.status == TaskStatus.COMPLETED and t.actual_start_time and t.actual_end_time]
                if completed_with_time:
                    total_days = sum([(t.actual_end_time - t.actual_start_time).days + 1 for t in completed_with_time])
                    avg_days = round(total_days / len(completed_with_time), 1)

                # 计算已复盘周数
                reviewed_weeks = db.query(TaskReview).join(WeeklyTask).filter(
                    WeeklyTask.user_id == member.id,
                    WeeklyTask.planned_start_time >= start_dt,
                    WeeklyTask.planned_start_time <= end_dt
                ).distinct(WeeklyTask.week_number, WeeklyTask.year).count()

                # 简单的绩效评分（基于完成率）
                performance_score = min(5, int(member_completion_rate / 20))

                member_performance.append({
                    "member_name": member.full_name,
                    "total_tasks": member_total,
                    "completed_tasks": member_completed,
                    "key_tasks": member_key_tasks,
                    "completion_rate": round(member_completion_rate, 1),
                    "avg_completion_days": avg_days,
                    "reviewed_weeks": reviewed_weeks,
                    "performance_score": performance_score
                })

        # 任务类型统计 - 简化版本避免复杂的SQL case语句
        task_type_stats = []
        all_tasks = base_query.all()

        # 按任务类型分组统计
        task_type_groups = {}
        for task in all_tasks:
            if task.task_type:
                task_type_name = task.task_type.name
                responsibility_name = task.task_type.responsibility.name if task.task_type.responsibility else "未分类"

                if task_type_name not in task_type_groups:
                    task_type_groups[task_type_name] = {
                        "task_type": task_type_name,
                        "responsibility": responsibility_name,
                        "count": 0,
                        "completed": 0,
                        "in_progress": 0,
                        "todo": 0,
                        "total_days": 0,
                        "completed_with_days": 0
                    }

                group = task_type_groups[task_type_name]
                group["count"] += 1

                if task.status == TaskStatus.COMPLETED:
                    group["completed"] += 1
                    if task.actual_start_time and task.actual_end_time:
                        days = (task.actual_end_time - task.actual_start_time).days + 1
                        group["total_days"] += days
                        group["completed_with_days"] += 1
                elif task.status == TaskStatus.IN_PROGRESS:
                    group["in_progress"] += 1
                elif task.status == TaskStatus.TODO:
                    group["todo"] += 1

        # 计算完成率和平均天数
        for group in task_type_groups.values():
            completion_rate = (group["completed"] / group["count"] * 100) if group["count"] > 0 else 0
            avg_days = (group["total_days"] / group["completed_with_days"]) if group["completed_with_days"] > 0 else 0

            task_type_stats.append({
                "task_type": group["task_type"],
                "responsibility": group["responsibility"],
                "count": group["count"],
                "completed": group["completed"],
                "in_progress": group["in_progress"],
                "todo": group["todo"],
                "completion_rate": round(completion_rate, 1),
                "avg_days": round(avg_days, 1)
            })

        return {
            "summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "key_tasks": key_tasks,
                "delayed_tasks": delayed_tasks,
                "completion_rate": round(completion_rate, 1),
                "key_completion_rate": round(key_completion_rate, 1),
                "delay_rate": round(delay_rate, 1)
            },
            "status_distribution": status_distribution,
            "weekly_trend": weekly_trend,
            "member_performance": member_performance,
            "task_type_stats": task_type_stats
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报表数据失败: {str(e)}")
