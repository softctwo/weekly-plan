"""
认证API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from ...core.security import verify_password, create_access_token
from ...core.rate_limit import limiter
from ...core.config import settings
from ...db.base import get_db
from ...models.user import User
from ...schemas.auth import Token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    用户登录
    OAuth2兼容的令牌登录，获取访问令牌

    限流策略：每分钟最多5次登录尝试，防止暴力破解（生产环境）
    """
    # 生产环境下启用限流
    if not settings.TESTING:
        return limiter.limit("5/minute")(login_internal)(request, db, form_data)
    else:
        return login_internal(request, db, form_data)


def login_internal(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """内部登录函数"""
    logger.info(f"Login attempt for username: {form_data.username}")

    try:
        # 查找用户
        user = db.query(User).filter(User.username == form_data.username).first()

        # 验证用户名和密码
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Failed login attempt for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 检查用户是否激活
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户账户已被停用"
            )

        # 创建访问令牌
        access_token = create_access_token(subject=user.id)

        logger.info(f"Successful login for user: {form_data.username} (ID: {user.id})")

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="数据库错误，请稍后重试"
        )
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )
