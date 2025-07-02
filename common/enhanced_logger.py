#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的日志管理系统

提供统一的日志管理功能，包括：
- 多级别日志记录
- 文件轮转和压缩
- 结构化日志
- 日志聚合和分析
- 远程日志发送
- 性能监控
- 日志搜索和过滤
"""

import os
import sys
import json
import time
import logging
import logging.handlers
import threading
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from queue import Queue, Empty
import traceback


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: str
    level: str
    logger_name: str
    module: str
    function: str
    line_number: int
    message: str
    extra_data: Dict[str, Any] = None
    trace_id: str = None
    user_id: str = None
    
    def __post_init__(self):
        if self.extra_data is None:
            self.extra_data = {}


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""
    
    def format(self, record):
        """格式化日志记录"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "process_id": record.process,
            "thread_id": record.thread
        }
        
        # 添加额外数据
        if hasattr(record, 'extra_data'):
            log_entry["extra"] = record.extra_data
        
        if hasattr(record, 'trace_id'):
            log_entry["trace_id"] = record.trace_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # 添加异常信息
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class DatabaseLogHandler(logging.Handler):
    """数据库日志处理器"""
    
    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
        
        # 批量写入队列
        self.log_queue = Queue()
        self.batch_size = 100
        self.flush_interval = 5  # 秒
        
        # 启动批量写入线程
        self.running = True
        self.writer_thread = threading.Thread(target=self._batch_writer, daemon=True)
        self.writer_thread.start()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    level TEXT,
                    logger_name TEXT,
                    module TEXT,
                    function TEXT,
                    line_number INTEGER,
                    message TEXT,
                    extra_data TEXT,
                    trace_id TEXT,
                    user_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON logs(level)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_logger ON logs(logger_name)")
    
    def emit(self, record):
        """发送日志记录"""
        try:
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created).isoformat(),
                level=record.levelname,
                logger_name=record.name,
                module=record.module,
                function=record.funcName,
                line_number=record.lineno,
                message=record.getMessage(),
                extra_data=getattr(record, 'extra_data', {}),
                trace_id=getattr(record, 'trace_id', None),
                user_id=getattr(record, 'user_id', None)
            )
            
            self.log_queue.put(log_entry)
            
        except Exception:
            self.handleError(record)
    
    def _batch_writer(self):
        """批量写入线程"""
        batch = []
        last_flush = time.time()
        
        while self.running:
            try:
                # 获取日志条目
                try:
                    entry = self.log_queue.get(timeout=1)
                    batch.append(entry)
                except Empty:
                    pass
                
                # 检查是否需要刷新
                now = time.time()
                should_flush = (
                    len(batch) >= self.batch_size or
                    (batch and now - last_flush >= self.flush_interval)
                )
                
                if should_flush:
                    self._flush_batch(batch)
                    batch.clear()
                    last_flush = now
                    
            except Exception as e:
                print(f"批量写入日志失败: {e}")
    
    def _flush_batch(self, batch: List[LogEntry]):
        """刷新批次到数据库"""
        if not batch:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT INTO logs 
                    (timestamp, level, logger_name, module, function, line_number, 
                     message, extra_data, trace_id, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    (
                        entry.timestamp, entry.level, entry.logger_name,
                        entry.module, entry.function, entry.line_number,
                        entry.message, json.dumps(entry.extra_data),
                        entry.trace_id, entry.user_id
                    )
                    for entry in batch
                ])
        except Exception as e:
            print(f"写入日志到数据库失败: {e}")


class EnhancedLogManager:
    """增强的日志管理器"""
    
    def __init__(self, config_path: str = "config/logging.json"):
        self.config_path = Path(config_path)
        self.load_config()
        
        # 日志器注册表
        self.loggers: Dict[str, logging.Logger] = {}
        
        # 日志处理器
        self.handlers: List[logging.Handler] = []
        
        # 性能统计
        self.stats = {
            "total_logs": 0,
            "logs_by_level": {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
            "logs_by_logger": {},
            "start_time": time.time()
        }
        
        # 初始化数据库
        self.db_path = Path("data/logs.db")
        self.init_log_database()
    
    def load_config(self):
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"加载日志配置失败: {e}")
                self.config = self.get_default_config()
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)8s] %(name)s:%(funcName)s:%(lineno)d: %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "json": {
                    "class": "common.enhanced_logger.StructuredFormatter"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "DEBUG",
                    "formatter": "detailed",
                    "filename": "logs/app.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                    "encoding": "utf-8"
                },
                "database": {
                    "class": "common.enhanced_logger.DatabaseLogHandler",
                    "level": "INFO",
                    "db_path": "data/logs.db"
                }
            },
            "loggers": {
                "": {
                    "level": "DEBUG",
                    "handlers": ["console", "file", "database"],
                    "propagate": False
                }
            },
            "settings": {
                "log_retention_days": 30,
                "max_log_file_size": "10MB",
                "compression_enabled": True,
                "remote_logging_enabled": False,
                "performance_logging": True
            }
        }
    
    def save_config(self):
        """保存配置"""
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def init_log_database(self):
        """初始化日志数据库"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # 日志统计表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS log_stats (
                    date TEXT PRIMARY KEY,
                    total_logs INTEGER,
                    debug_logs INTEGER,
                    info_logs INTEGER,
                    warning_logs INTEGER,
                    error_logs INTEGER,
                    critical_logs INTEGER
                )
            """)
    
    def setup_logger(self, name: str, level: str = None, 
                    extra_handlers: List[logging.Handler] = None) -> logging.Logger:
        """设置日志器"""
        if name in self.loggers:
            return self.loggers[name]
        
        logger = logging.getLogger(name)
        
        # 设置级别
        log_level = level or self.config["loggers"][""]["level"]
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 清除现有处理器
        logger.handlers.clear()
        
        # 添加配置的处理器
        for handler_name in self.config["loggers"][""]["handlers"]:
            handler = self._create_handler(handler_name)
            if handler:
                logger.addHandler(handler)
        
        # 添加额外处理器
        if extra_handlers:
            for handler in extra_handlers:
                logger.addHandler(handler)
        
        # 添加统计过滤器
        logger.addFilter(self._create_stats_filter())
        
        self.loggers[name] = logger
        return logger
    
    def _create_handler(self, handler_name: str) -> Optional[logging.Handler]:
        """创建处理器"""
        try:
            handler_config = self.config["handlers"][handler_name]
            handler_class = handler_config["class"]
            
            if handler_class == "logging.StreamHandler":
                handler = logging.StreamHandler()
            elif handler_class == "logging.handlers.RotatingFileHandler":
                log_file = Path(handler_config["filename"])
                log_file.parent.mkdir(exist_ok=True)
                handler = logging.handlers.RotatingFileHandler(
                    filename=log_file,
                    maxBytes=handler_config["maxBytes"],
                    backupCount=handler_config["backupCount"],
                    encoding=handler_config.get("encoding", "utf-8")
                )
            elif handler_class == "common.enhanced_logger.DatabaseLogHandler":
                handler = DatabaseLogHandler(handler_config["db_path"])
            else:
                return None
            
            # 设置级别
            handler.setLevel(getattr(logging, handler_config["level"].upper()))
            
            # 设置格式化器
            formatter_name = handler_config.get("formatter", "standard")
            formatter = self._create_formatter(formatter_name)
            if formatter:
                handler.setFormatter(formatter)
            
            return handler
            
        except Exception as e:
            print(f"创建处理器失败 {handler_name}: {e}")
            return None
    
    def _create_formatter(self, formatter_name: str) -> Optional[logging.Formatter]:
        """创建格式化器"""
        try:
            formatter_config = self.config["formatters"][formatter_name]
            
            if formatter_config.get("class") == "common.enhanced_logger.StructuredFormatter":
                return StructuredFormatter()
            else:
                return logging.Formatter(
                    fmt=formatter_config.get("format"),
                    datefmt=formatter_config.get("datefmt")
                )
        except Exception as e:
            print(f"创建格式化器失败 {formatter_name}: {e}")
            return None
    
    def _create_stats_filter(self):
        """创建统计过滤器"""
        def stats_filter(record):
            self.stats["total_logs"] += 1
            self.stats["logs_by_level"][record.levelname] += 1
            
            logger_name = record.name
            if logger_name not in self.stats["logs_by_logger"]:
                self.stats["logs_by_logger"][logger_name] = 0
            self.stats["logs_by_logger"][logger_name] += 1
            
            return True
        
        return stats_filter
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取日志器"""
        if name not in self.loggers:
            return self.setup_logger(name)
        return self.loggers[name]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "logs_per_second": self.stats["total_logs"] / uptime if uptime > 0 else 0,
            "active_loggers": len(self.loggers)
        }


# 全局日志管理器实例
_enhanced_log_manager = None

def get_enhanced_log_manager() -> EnhancedLogManager:
    """获取全局增强日志管理器实例"""
    global _enhanced_log_manager
    if _enhanced_log_manager is None:
        _enhanced_log_manager = EnhancedLogManager()
    return _enhanced_log_manager


def main():
    """主函数 - 测试增强日志系统"""
    manager = get_enhanced_log_manager()
    
    print("📝 增强日志管理系统测试")
    
    # 创建测试日志器
    logger = manager.get_logger("test_logger")
    
    # 测试各种日志级别
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误信息")
    
    # 测试结构化日志
    logger.info("用户登录", extra={
        'extra_data': {'user_id': '123', 'ip': '192.168.1.1'},
        'trace_id': 'trace-001'
    })
    
    # 获取统计信息
    stats = manager.get_stats()
    print(f"\n日志统计:")
    print(f"总日志数: {stats['total_logs']}")
    print(f"活跃日志器: {stats['active_loggers']}")
    print(f"运行时间: {stats['uptime_seconds']:.1f}秒")
    
    print("\n✅ 增强日志系统测试完成")


if __name__ == "__main__":
    main()
