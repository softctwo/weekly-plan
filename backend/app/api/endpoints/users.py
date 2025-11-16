"""
用户管理API端点 - REQ-1.1, REQ-1.2, REQ-1.3, REQ-1.4
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...api.deps import get_db, get_current_admin, get_current_user
from ...core.security import get_password_hash
from ...models.user import User, Department
from ...models.role import UserRoleLink
from ...schemas import user as schemas

router = APIRouter()


# 用户管理 - REQ-1.1
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建用户（管理员）"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=400,
            detail="邮箱已存在"
        )

    # 创建用户
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        department_id=user_in.department_id,
        manager_id=user_in.manager_id,
        user_type=user_in.user_type
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@router.get("/", response_model=List[schemas.User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取用户列表（管理员）"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """获取指定用户信息（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """更新用户信息（管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新字段
    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# 用户-岗位关联 - REQ-1.3
@router.post("/{user_id}/roles/{role_id}")
def link_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """为用户关联岗位（管理员）"""
    # 检查用户和岗位是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查是否已关联
    existing = db.query(UserRoleLink).filter(
        UserRoleLink.user_id == user_id,
        UserRoleLink.role_id == role_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="该用户已关联此岗位")

    # 创建关联
    link = UserRoleLink(user_id=user_id, role_id=role_id)
    db.add(link)
    db.commit()

    return {"message": "岗位关联成功"}


@router.delete("/{user_id}/roles/{role_id}")
def unlink_user_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """解除用户岗位关联（管理员）"""
    link = db.query(UserRoleLink).filter(
        UserRoleLink.user_id == user_id,
        UserRoleLink.role_id == role_id
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="未找到该关联关系")

    db.delete(link)
    db.commit()

    return {"message": "岗位解除关联成功"}


# 部门管理 - REQ-1.2
@router.post("/departments/", response_model=schemas.Department, status_code=status.HTTP_201_CREATED)
def create_department(
    dept_in: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """创建部门（管理员）"""
    dept = Department(**dept_in.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@router.get("/departments/", response_model=List[schemas.Department])
def list_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取部门列表"""
    depts = db.query(Department).filter(Department.is_active == True).all()
    return depts
