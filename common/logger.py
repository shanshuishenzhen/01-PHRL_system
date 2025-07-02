# -*- coding: utf-8 -*-
"""
日志工具模块

提供统一的日志记录功能，支持文件日志和控制台输出，可配置日志级别、文件大小和备份数量。

更新日志：
- 2024-06-25：初始版本，提供基本日志功能
"""

import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 默认配置
DEFAULT_CONFIG = {
    "level": "INFO",
    "max_file_size_mb": 10,
    "backup_count": 5,
    "console_output": True
}

# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


def setup_logger(name, log_file=None, config=None):
    """
    设置日志记录器
    
    Args:
        name (str): 日志记录器名称
        log_file (str, optional): 日志文件路径，如果为None则只输出到控制台
        config (dict, optional): 日志配置，包含level、max_file_size_mb、backup_count和console_output
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    # 加载配置
    if config is None:
        # 尝试从config.json加载配置
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json'), 'r', encoding='utf-8') as f:
                system_config = json.load(f)
                config = system_config.get('logging', DEFAULT_CONFIG)
        except (FileNotFoundError, json.JSONDecodeError):
            config = DEFAULT_CONFIG
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger
    
    # 设置日志级别
    log_level = LOG_LEVELS.get(config.get('level', 'INFO'), logging.INFO)
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 创建RotatingFileHandler
        max_bytes = config.get('max_file_size_mb', 10) * 1024 * 1024
        backup_count = config.get('backup_count', 5)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 如果配置了控制台输出，添加控制台处理器
    if config.get('console_output', True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name, log_file=None):
    """
    获取日志记录器，如果不存在则创建
    
    Args:
        name (str): 日志记录器名称
        log_file (str, optional): 日志文件路径
        
    Returns:
        logging.Logger: 日志记录器
    """
    return setup_logger(name, log_file)


def log_exception(logger, exc_info=None, level='ERROR'):
    """
    记录异常信息
    
    Args:
        logger (logging.Logger): 日志记录器
        exc_info (tuple, optional): 异常信息，如果为None则自动获取
        level (str, optional): 日志级别，默认为ERROR
    """
    if exc_info is None:
        exc_info = sys.exc_info()
    
    if level.upper() == 'CRITICAL':
        logger.critical("发生严重异常", exc_info=exc_info)
    elif level.upper() == 'ERROR':
        logger.error("发生异常", exc_info=exc_info)
    elif level.upper() == 'WARNING':
        logger.warning("发生警告", exc_info=exc_info)
    else:
        logger.error("发生异常", exc_info=exc_info)


def log_system_info(logger):
    """
    记录系统信息
    
    Args:
        logger (logging.Logger): 日志记录器
    """
    import platform
    
    logger.info("系统信息:")
    logger.info(f"  操作系统: {platform.system()} {platform.release()}")
    logger.info(f"  Python版本: {platform.python_version()}")
    logger.info(f"  系统架构: {platform.machine()}")
    logger.info(f"  处理器: {platform.processor()}")
    
    # 记录当前时间
    now = datetime.now()
    logger.info(f"  当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 尝试记录可用内存
    try:
        import psutil
        mem = psutil.virtual_memory()
        logger.info(f"  总内存: {mem.total / (1024**3):.2f} GB")
        logger.info(f"  可用内存: {mem.available / (1024**3):.2f} GB")
        logger.info(f"  内存使用率: {mem.percent}%")
        
        # 记录磁盘信息
        disk = psutil.disk_usage('/')
        logger.info(f"  磁盘总空间: {disk.total / (1024**3):.2f} GB")
        logger.info(f"  磁盘可用空间: {disk.free / (1024**3):.2f} GB")
        logger.info(f"  磁盘使用率: {disk.percent}%")
    except ImportError:
        logger.info("  未安装psutil模块，无法获取内存和磁盘信息")


if __name__ == "__main__":
    # 测试日志功能
    logger = get_logger("test_logger", "../logs/test.log")
    logger.debug("这是一条调试日志")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    logger.critical("这是一条严重错误日志")
    
    # 测试异常记录
    try:
        1 / 0
    except Exception:
        log_exception(logger)
    
    # 测试系统信息记录
    log_system_info(logger)
    
    print("日志测试完成，请查看logs/test.log文件")