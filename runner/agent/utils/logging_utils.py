"""
MidsceneAgent 日志工具
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    设置日志配置。

    Args:
        level: 日志级别（默认: logging.INFO）
        format_string: 自定义格式字符串（可选）
        log_file: 日志文件（可选）
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 创建记录器
    logger = logging.getLogger()
    logger.setLevel(level)

    # 创建格式化器
    formatter = logging.Formatter(format_string)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（如果指定）
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取记录器实例。

    Args:
        name: 记录器名称（通常使用 __name__）

    Returns:
        记录器实例
    """
    return logging.getLogger(name)
