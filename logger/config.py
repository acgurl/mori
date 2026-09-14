"""日志配置模块

提供统一的日志配置和管理，支持：
- 结构化日志（JSON格式）
- 日志轮转（按文件大小）
- 上下文信息（request_id, session_id等）
- 人类可读的控制台输出
"""

import json
import logging
import sys
from contextvars import ContextVar, Token
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# 上下文变量，用于存储请求级别的信息
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})


class JSONFormatter(logging.Formatter):
    """JSON格式化器，用于结构化日志输出"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为JSON格式

        Args:
            record: 日志记录对象

        Returns:
            JSON格式的日志字符串
        """
        # 基础日志信息
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加上下文信息
        context = _log_context.get()
        if context:
            log_data["context"] = context

        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


class HumanReadableFormatter(logging.Formatter):
    """人类可读的格式化器，用于控制台输出"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为人类可读格式

        Args:
            record: 日志记录对象

        Returns:
            格式化后的日志字符串
        """
        # 基础格式
        formatted = super().format(record)

        # 添加上下文信息（如果存在）
        context = _log_context.get()
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            formatted = f"{formatted} | {context_str}"

        return formatted


def setup_logger(
    name: str = "mori",
    level: str = "INFO",
    log_dir: str | None = "logs",
    console: bool = True,
    json_format: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """配置并返回日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志文件目录，如果为None则不写入文件
        console: 是否输出到控制台
        json_format: 文件日志是否使用JSON格式（控制台始终使用人类可读格式）
        max_bytes: 单个日志文件最大字节数（默认10MB）
        backup_count: 保留的旧日志文件数量

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除已有的处理器
    logger.handlers.clear()

    # 文件处理器（带轮转）
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # 主日志文件（所有级别）
        file_handler = RotatingFileHandler(
            log_path / f"{name}.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)

        file_formatter: logging.Formatter
        if json_format:
            file_formatter = JSONFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        else:
            file_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # 错误日志文件（仅ERROR及以上）
        error_handler = RotatingFileHandler(
            log_path / f"{name}_error.log",
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)

        error_formatter: logging.Formatter
        if json_format:
            error_formatter = JSONFormatter(datefmt="%Y-%m-%d %H:%M:%S")
        else:
            error_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        error_handler.setFormatter(error_formatter)
        logger.addHandler(error_handler)

    # 控制台处理器（始终使用人类可读格式）
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = HumanReadableFormatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "mori") -> logging.Logger:
    """获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return logging.getLogger(name)


def set_log_context(**kwargs: Any) -> None:
    """设置日志上下文信息

    使用示例:
        set_log_context(request_id="req-123", user_id="user-456")

    Args:
        **kwargs: 要设置的上下文键值对
    """
    current = _log_context.get().copy()
    current.update(kwargs)
    _log_context.set(current)


def clear_log_context() -> None:
    """清除当前的日志上下文信息"""
    _log_context.set({})


def get_log_context() -> dict[str, Any]:
    """获取当前的日志上下文信息

    Returns:
        当前的上下文字典
    """
    return _log_context.get().copy()


class LogContext:
    """日志上下文管理器

    使用示例:
        with LogContext(request_id="req-123", user_id="user-456"):
            logger.info("处理请求")  # 日志会自动包含上下文信息
    """

    def __init__(self, **kwargs: Any):
        """初始化上下文管理器

        Args:
            **kwargs: 要设置的上下文键值对
        """
        self.context = kwargs
        self.token: Token[dict[str, Any]] | None = None

    def __enter__(self) -> "LogContext":
        """进入上下文"""
        current = _log_context.get().copy()
        current.update(self.context)
        self.token = _log_context.set(current)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """退出上下文"""
        if self.token:
            _log_context.reset(self.token)
