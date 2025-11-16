"""
岗位职责库API端点 - REQ-2.1, REQ-2.2, REQ-2.3, REQ-2.4
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.deps import get_db, get_current_admin, get_current_user
from ...models.role import Role, Responsibility, TaskType
from ...schemas import role as schemas

router = APIRouter()


# 岗位管理 - REQ-2.1
@router.post("/", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: schemas.RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """创建岗位（管理员）"""
    # 检查岗位名称是否已存在
    if db.query(Role).filter(Role.name == role_in.name).first():
        raise HTTPException(status_code=400, detail="岗位名称已存在")

    role = Role(**role_in.model_dump())
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/", response_model=List[schemas.Role])
def list_roles(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取岗位列表"""
    query = db.query(Role)
    if not include_inactive:
        query = query.filter(Role.is_active == True)
    return query.all()


@router.get("/{role_id}", response_model=schemas.Role)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取岗位详情"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return role


@router.put("/{role_id}/deactivate")
def deactivate_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """停用岗位 - REQ-2.4（不支持物理删除）"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="岗位不存在")

    role.is_active = False
    db.commit()
    return {"message": "岗位已停用"}


# 职责管理 - REQ-2.2
@router.post("/responsibilities/", response_model=schemas.Responsibility, status_code=status.HTTP_201_CREATED)
def create_responsibility(
    resp_in: schemas.ResponsibilityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """创建职责（管理员）"""
    # 验证岗位存在
    role = db.query(Role).filter(Role.id == resp_in.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="岗位不存在")

    resp = Responsibility(**resp_in.model_dump())
    db.add(resp)
    db.commit()
    db.refresh(resp)
    return resp


@router.get("/responsibilities/", response_model=List[schemas.Responsibility])
def list_responsibilities(
    role_id: int = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取职责列表"""
    query = db.query(Responsibility)
    if role_id:
        query = query.filter(Responsibility.role_id == role_id)
    if not include_inactive:
        query = query.filter(Responsibility.is_active == True)
    return query.order_by(Responsibility.sort_order).all()


@router.put("/responsibilities/{resp_id}/deactivate")
def deactivate_responsibility(
    resp_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """停用职责 - REQ-2.4"""
    resp = db.query(Responsibility).filter(Responsibility.id == resp_id).first()
    if not resp:
        raise HTTPException(status_code=404, detail="职责不存在")

    resp.is_active = False
    db.commit()
    return {"message": "职责已停用"}


# 任务类型管理 - REQ-2.3
@router.post("/task-types/", response_model=schemas.TaskType, status_code=status.HTTP_201_CREATED)
def create_task_type(
    task_type_in: schemas.TaskTypeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """创建任务类型（管理员）"""
    # 验证职责存在
    resp = db.query(Responsibility).filter(Responsibility.id == task_type_in.responsibility_id).first()
    if not resp:
        raise HTTPException(status_code=404, detail="职责不存在")

    task_type = TaskType(**task_type_in.model_dump())
    db.add(task_type)
    db.commit()
    db.refresh(task_type)
    return task_type


@router.get("/task-types/", response_model=List[schemas.TaskType])
def list_task_types(
    responsibility_id: int = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取任务类型列表"""
    query = db.query(TaskType)
    if responsibility_id:
        query = query.filter(TaskType.responsibility_id == responsibility_id)
    if not include_inactive:
        query = query.filter(TaskType.is_active == True)
    return query.order_by(TaskType.sort_order).all()


@router.put("/task-types/{task_type_id}/deactivate")
def deactivate_task_type(
    task_type_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin)
):
    """停用任务类型 - REQ-2.4"""
    task_type = db.query(TaskType).filter(TaskType.id == task_type_id).first()
    if not task_type:
        raise HTTPException(status_code=404, detail="任务类型不存在")

    task_type.is_active = False
    db.commit()
    return {"message": "任务类型已停用"}
