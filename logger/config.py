"""日志配置模块

提供统一的日志配置和管理。
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "mori",
    level: str = "INFO",
    log_dir: Optional[str] = "logs",
    console: bool = True,
) -> logging.Logger:
    """配置并返回日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: 日志文件目录，如果为None则不写入文件
        console: 是否输出到控制台

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除已有的处理器
    logger.handlers.clear()

    # 创建格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 文件处理器
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path / f"{name}.log", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
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
