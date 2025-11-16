"""
认证相关Schemas
"""
from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """访问令牌"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[int] = None
