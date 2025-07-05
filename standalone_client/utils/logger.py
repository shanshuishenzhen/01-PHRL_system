#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志管理

提供统一的日志记录功能。
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

# 日志配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 日志目录
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 全局日志配置
_logging_setup = False

def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = False,
    max_file_size: int = 10,  # MB
    backup_count: int = 5
) -> None:
    """设置全局日志配置"""
    global _logging_setup
    
    if _logging_setup:
        return
    
    # 设置根日志级别
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(numeric_level)
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # 文件日志处理器
    if log_to_file:
        log_file = LOG_DIR / "client.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size * 1024 * 1024,  # 转换为字节
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    # 控制台日志处理器
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
    
    _logging_setup = True

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    # 确保日志已设置
    if not _logging_setup:
        # 尝试从配置加载日志设置
        try:
            from core.config import client_config
            setup_logging(
                level=client_config.get('logging.level', 'INFO'),
                log_to_file=client_config.get('logging.log_to_file', True),
                log_to_console=client_config.get('logging.log_to_console', False),
                max_file_size=client_config.get('logging.max_file_size', 10),
                backup_count=client_config.get('logging.backup_count', 5)
            )
        except ImportError:
            # 如果配置不可用，使用默认设置
            setup_logging()
    
    return logging.getLogger(name)

class LoggerMixin:
    """日志记录器混入类"""
    
    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        return get_logger(self.__class__.__name__)

# 创建一些特定用途的日志记录器
def get_ui_logger() -> logging.Logger:
    """获取UI日志记录器"""
    return get_logger('ui')

def get_api_logger() -> logging.Logger:
    """获取API日志记录器"""
    return get_logger('api')

def get_security_logger() -> logging.Logger:
    """获取安全日志记录器"""
    return get_logger('security')

def get_exam_logger() -> logging.Logger:
    """获取考试日志记录器"""
    return get_logger('exam')

# 日志级别常量
class LogLevel:
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
