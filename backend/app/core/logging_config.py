"""
日志配置模块
提供统一的日志记录功能
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from .config import settings


# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    """
    配置应用日志系统

    日志级别：
    - DEBUG: 详细的调试信息
    - INFO: 一般信息
    - WARNING: 警告信息
    - ERROR: 错误信息
    - CRITICAL: 严重错误
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器 - 输出到终端
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 文件处理器 - 应用日志（按大小轮转）
    app_file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    app_file_handler.setLevel(logging.INFO)
    app_file_handler.setFormatter(console_formatter)
    root_logger.addHandler(app_file_handler)

    # 错误日志处理器 - 只记录ERROR及以上级别
    error_file_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(console_formatter)
    root_logger.addHandler(error_file_handler)

    # 访问日志处理器 - 按天轮转
    access_file_handler = TimedRotatingFileHandler(
        log_dir / "access.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    access_file_handler.setLevel(logging.INFO)
    access_formatter = logging.Formatter(
        "%(asctime)s - %(message)s",
        DATE_FORMAT
    )
    access_file_handler.setFormatter(access_formatter)

    # 为访问日志创建专用logger
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_file_handler)
    access_logger.propagate = False  # 不传播到根logger

    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logging.info("日志系统初始化完成")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称（通常使用 __name__）

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)
