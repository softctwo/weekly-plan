"""
API限流配置
使用slowapi实现请求频率限制，防止API滥用
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# 创建限流器实例
limiter = Limiter(
    key_func=get_remote_address,  # 使用客户端IP作为限流key
    default_limits=["200/minute"],  # 默认每分钟200次请求
    storage_uri="memory://",  # 使用内存存储（生产环境建议使用Redis）
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    限流异常处理器
    当请求超过限流阈值时返回429状态码
    """
    logger.warning(
        f"Rate limit exceeded for {request.client.host if request.client else 'unknown'} - "
        f"Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "请求过于频繁，请稍后再试",
            "retry_after": exc.detail
        }
    )
