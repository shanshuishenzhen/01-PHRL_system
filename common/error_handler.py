# -*- coding: utf-8 -*-
"""
错误处理工具模块

提供统一的错误处理和异常捕获功能，包括错误日志记录、错误对话框显示等。

更新日志：
- 2024-06-25：初始版本，提供基本错误处理功能
- 2025-01-07：增强异常处理机制，添加重试、降级、监控功能
"""

import os
import sys
import traceback
import time
import functools
from pathlib import Path
from typing import Optional, Callable, Any, Tuple, Dict, List
from enum import Enum

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger, log_exception


class ErrorLevel(Enum):
    """错误级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorCode(Enum):
    """错误代码枚举"""
    UNKNOWN_ERROR = 1000
    NETWORK_ERROR = 1001
    DATABASE_ERROR = 1002
    FILE_ERROR = 1003
    PERMISSION_ERROR = 1004
    VALIDATION_ERROR = 1005
    CONFIGURATION_ERROR = 1006
    DEPENDENCY_ERROR = 1007
    TIMEOUT_ERROR = 1008
    RESOURCE_ERROR = 1009


class SystemError(Exception):
    """系统自定义异常基类"""
    def __init__(self, message: str, error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()


class NetworkError(SystemError):
    """网络错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.NETWORK_ERROR, details)


class DatabaseError(SystemError):
    """数据库错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.DATABASE_ERROR, details)


class FileError(SystemError):
    """文件操作错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.FILE_ERROR, details)


class ValidationError(SystemError):
    """数据验证错误"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, ErrorCode.VALIDATION_ERROR, details)

# 创建日志记录器
logger = get_logger("error_handler", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "error.log"))


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理函数
    
    Args:
        exc_type: 异常类型
        exc_value: 异常值
        exc_traceback: 异常回溯
    """
    # 忽略键盘中断异常
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # 记录异常信息
    logger.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
    
    # 尝试显示错误对话框
    try:
        from tkinter import messagebox
        error_message = f"{exc_type.__name__}: {exc_value}"
        detail = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        messagebox.showerror("系统错误", error_message, detail=detail)
    except ImportError:
        # 如果无法导入tkinter，则打印错误信息
        print(f"系统错误: {exc_type.__name__}: {exc_value}")
        traceback.print_exception(exc_type, exc_value, exc_traceback)


def setup_exception_handling():
    """
    设置全局异常处理
    """
    sys.excepthook = handle_exception


def log_error(message, exc_info=None, level="ERROR"):
    """
    记录错误信息
    
    Args:
        message (str): 错误消息
        exc_info (tuple, optional): 异常信息，如果为None则自动获取
        level (str, optional): 日志级别，默认为ERROR
    """
    if exc_info is None and sys.exc_info()[0] is not None:
        exc_info = sys.exc_info()
    
    if exc_info and exc_info[0] is not None:
        log_exception(logger, exc_info, level)
    else:
        if level.upper() == "CRITICAL":
            logger.critical(message)
        elif level.upper() == "ERROR":
            logger.error(message)
        elif level.upper() == "WARNING":
            logger.warning(message)
        else:
            logger.error(message)


def show_error_dialog(title, message, detail=None):
    """
    显示错误对话框
    
    Args:
        title (str): 对话框标题
        message (str): 错误消息
        detail (str, optional): 详细错误信息
    """
    try:
        from tkinter import messagebox
        messagebox.showerror(title, message, detail=detail)
    except ImportError:
        # 如果无法导入tkinter，则打印错误信息
        print(f"{title}: {message}")
        if detail:
            print(detail)


def format_exception(exc_info=None):
    """
    格式化异常信息
    
    Args:
        exc_info (tuple, optional): 异常信息，如果为None则自动获取
        
    Returns:
        str: 格式化后的异常信息
    """
    if exc_info is None:
        exc_info = sys.exc_info()
    
    if exc_info[0] is None:
        return ""
    
    return "".join(traceback.format_exception(*exc_info))


def handle_error(func):
    """
    错误处理装饰器
    
    Args:
        func (callable): 要装饰的函数
        
    Returns:
        callable: 装饰后的函数
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录错误
            log_error(f"函数 {func.__name__} 执行出错: {str(e)}")
            
            # 显示错误对话框
            error_message = f"操作失败: {str(e)}"
            detail = format_exception()
            show_error_dialog("错误", error_message, detail)
            
            # 返回None表示操作失败
            return None
    
    return wrapper


def safe_call(func, *args, **kwargs):
    """
    安全调用函数

    Args:
        func (callable): 要调用的函数
        *args: 位置参数
        **kwargs: 关键字参数

    Returns:
        tuple: (是否成功, 返回值或异常)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        # 记录错误
        log_error(f"函数 {func.__name__} 执行出错: {str(e)}")
        return False, e


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: Tuple = (Exception,)):
    """
    重试装饰器

    Args:
        max_attempts: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff: 延迟时间倍数
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        log_error(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败，{current_delay}秒后重试: {str(e)}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        log_error(f"函数 {func.__name__} 重试 {max_attempts} 次后仍然失败: {str(e)}")

            raise last_exception
        return wrapper
    return decorator


def timeout(seconds: float):
    """
    超时装饰器

    Args:
        seconds: 超时时间（秒）
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"函数 {func.__name__} 执行超时（{seconds}秒）")

            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # 恢复原来的信号处理器
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        return wrapper
    return decorator


def fallback(fallback_func: Callable, exceptions: Tuple = (Exception,)):
    """
    降级装饰器

    Args:
        fallback_func: 降级函数
        exceptions: 需要降级的异常类型
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                log_error(f"函数 {func.__name__} 执行失败，使用降级方案: {str(e)}")
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0):
    """
    断路器装饰器

    Args:
        failure_threshold: 失败阈值
        recovery_timeout: 恢复超时时间（秒）
    """
    def decorator(func):
        func._failure_count = 0
        func._last_failure_time = None
        func._is_open = False

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 检查断路器状态
            if func._is_open:
                if time.time() - func._last_failure_time > recovery_timeout:
                    func._is_open = False
                    func._failure_count = 0
                    log_error(f"断路器 {func.__name__} 恢复正常")
                else:
                    raise SystemError(f"断路器 {func.__name__} 处于开启状态", ErrorCode.RESOURCE_ERROR)

            try:
                result = func(*args, **kwargs)
                # 成功时重置失败计数
                if func._failure_count > 0:
                    func._failure_count = 0
                return result
            except Exception as e:
                func._failure_count += 1
                func._last_failure_time = time.time()

                if func._failure_count >= failure_threshold:
                    func._is_open = True
                    log_error(f"断路器 {func.__name__} 开启，失败次数: {func._failure_count}")

                raise e

        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试错误处理功能
    setup_exception_handling()
    
    # 测试日志记录
    log_error("测试错误消息")
    
    # 测试异常捕获
    try:
        1 / 0
    except Exception as e:
        log_error(f"发生异常: {str(e)}")
    
    # 测试错误处理装饰器
    @handle_error
    def test_function():
        raise ValueError("测试异常")
    
    test_function()
    
    # 测试安全调用
    success, result = safe_call(lambda x: 10 / x, 0)
    print(f"安全调用结果: 成功={success}, 结果={result}")
    
    # 测试全局异常处理
    # 取消注释下面的代码将触发全局异常处理
    # raise RuntimeError("测试全局异常处理")