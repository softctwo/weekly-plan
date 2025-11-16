"""
认证API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...core.security import verify_password, create_access_token
from ...db.base import get_db
from ...models.user import User
from ...schemas.auth import Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    用户登录
    OAuth2兼容的令牌登录，获取访问令牌
    """
    # 查找用户
    user = db.query(User).filter(User.username == form_data.username).first()

    # 验证用户名和密码
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被停用"
        )

    # 创建访问令牌
    access_token = create_access_token(subject=user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
