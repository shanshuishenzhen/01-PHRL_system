#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块间通信管理器

提供统一的模块间通信机制，支持：
- HTTP API通信
- 文件系统通信
- 消息队列通信
- 事件驱动通信
- 通信监控和日志
"""

import json
import time
import logging
import requests
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from queue import Queue, Empty
import sqlite3


@dataclass
class Message:
    """通信消息"""
    id: str
    from_module: str
    to_module: str
    message_type: str
    data: Dict[str, Any]
    timestamp: str
    priority: int = 1
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ModuleEndpoint:
    """模块端点配置"""
    module_name: str
    host: str
    port: int
    base_path: str = ""
    protocol: str = "http"
    timeout: int = 30
    
    @property
    def base_url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}{self.base_path}"


class CommunicationManager:
    """模块间通信管理器"""
    
    def __init__(self, config_path: str = "config/communication.json"):
        self.config_path = Path(config_path)
        self.setup_logging()
        
        # 通信配置
        self.endpoints: Dict[str, ModuleEndpoint] = {}
        self.message_queue = Queue()
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # 通信统计
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "failed_messages": 0,
            "api_calls": 0,
            "file_operations": 0
        }
        
        # 数据库连接
        self.db_path = Path("data/communication.db")
        self.init_database()
        
        # 加载配置
        self.load_config()
        
        # 启动消息处理线程
        self.running = True
        self.message_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.message_thread.start()
    
    def setup_logging(self):
        """设置日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.FileHandler(log_dir / "communication.log", encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def init_database(self):
        """初始化数据库"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    from_module TEXT,
                    to_module TEXT,
                    message_type TEXT,
                    data TEXT,
                    timestamp TEXT,
                    status TEXT,
                    retry_count INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS communication_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    event_type TEXT,
                    module_name TEXT,
                    details TEXT
                )
            """)
    
    def load_config(self):
        """加载通信配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载模块端点
                for module_name, endpoint_config in config.get("endpoints", {}).items():
                    endpoint = ModuleEndpoint(
                        module_name=module_name,
                        **endpoint_config
                    )
                    self.endpoints[module_name] = endpoint
                
                self.logger.info(f"加载通信配置: {len(self.endpoints)} 个模块端点")
                
            except Exception as e:
                self.logger.error(f"加载通信配置失败: {e}")
        else:
            # 创建默认配置
            self.create_default_config()
    
    def create_default_config(self):
        """创建默认配置"""
        default_config = {
            "endpoints": {
                "question_bank": {
                    "host": "localhost",
                    "port": 5000,
                    "base_path": "/api"
                },
                "exam_management": {
                    "host": "localhost", 
                    "port": 5001,
                    "base_path": "/api"
                },
                "grading_center": {
                    "host": "localhost",
                    "port": 3000,
                    "base_path": "/api"
                },
                "client": {
                    "host": "localhost",
                    "port": 8080,
                    "base_path": ""
                },
                "user_management": {
                    "host": "localhost",
                    "port": 5002,
                    "base_path": "/api"
                }
            },
            "file_communication": {
                "base_dir": "data/communication",
                "inbox_dir": "inbox",
                "outbox_dir": "outbox",
                "processed_dir": "processed"
            },
            "message_queue": {
                "max_size": 1000,
                "retry_interval": 5,
                "max_retries": 3
            }
        }
        
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        self.load_config()
    
    def register_endpoint(self, module_name: str, host: str, port: int, 
                         base_path: str = "", protocol: str = "http"):
        """注册模块端点"""
        endpoint = ModuleEndpoint(
            module_name=module_name,
            host=host,
            port=port,
            base_path=base_path,
            protocol=protocol
        )
        self.endpoints[module_name] = endpoint
        self.logger.info(f"注册模块端点: {module_name} -> {endpoint.base_url}")
    
    def send_api_request(self, to_module: str, endpoint: str, method: str = "GET",
                        data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """发送API请求"""
        if to_module not in self.endpoints:
            self.logger.error(f"未找到模块端点: {to_module}")
            return None
        
        endpoint_config = self.endpoints[to_module]
        url = f"{endpoint_config.base_url}{endpoint}"
        
        try:
            self.stats["api_calls"] += 1
            
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=endpoint_config.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, timeout=endpoint_config.timeout)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, timeout=endpoint_config.timeout)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=endpoint_config.timeout)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            response.raise_for_status()
            
            self.log_communication_event("api_request", to_module, 
                                        f"{method} {url} -> {response.status_code}")
            
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API请求失败: {method} {url} -> {e}")
            self.stats["failed_messages"] += 1
            return None
        except Exception as e:
            self.logger.error(f"API请求异常: {e}")
            return None
    
    def send_message(self, to_module: str, message_type: str, data: Dict,
                    from_module: str = "system", priority: int = 1):
        """发送消息"""
        message = Message(
            id=f"msg_{int(time.time() * 1000)}_{threading.get_ident()}",
            from_module=from_module,
            to_module=to_module,
            message_type=message_type,
            data=data,
            timestamp=datetime.now().isoformat(),
            priority=priority
        )
        
        self.message_queue.put(message)
        self.stats["messages_sent"] += 1
        
        # 保存到数据库
        self.save_message_to_db(message, "pending")
        
        self.logger.info(f"发送消息: {from_module} -> {to_module} ({message_type})")
    
    def _process_messages(self):
        """处理消息队列"""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1)
                self._handle_message(message)
                self.message_queue.task_done()
            except Empty:
                continue
            except Exception as e:
                self.logger.error(f"处理消息失败: {e}")
    
    def _handle_message(self, message: Message):
        """处理单个消息"""
        try:
            # 根据消息类型选择处理方式
            if message.message_type == "api_call":
                self._handle_api_message(message)
            elif message.message_type == "file_transfer":
                self._handle_file_message(message)
            elif message.message_type == "event":
                self._handle_event_message(message)
            else:
                self._handle_generic_message(message)
            
            self.save_message_to_db(message, "processed")
            self.stats["messages_received"] += 1
            
        except Exception as e:
            self.logger.error(f"处理消息失败: {message.id} -> {e}")
            message.retry_count += 1
            
            if message.retry_count < message.max_retries:
                # 重新加入队列
                time.sleep(5)  # 等待5秒后重试
                self.message_queue.put(message)
                self.save_message_to_db(message, "retry")
            else:
                self.save_message_to_db(message, "failed")
                self.stats["failed_messages"] += 1
    
    def _handle_api_message(self, message: Message):
        """处理API消息"""
        endpoint = message.data.get("endpoint", "")
        method = message.data.get("method", "GET")
        request_data = message.data.get("data", {})
        params = message.data.get("params", {})
        
        result = self.send_api_request(message.to_module, endpoint, method, request_data, params)
        
        # 如果有回调，发送结果
        if "callback" in message.data:
            callback_data = {
                "original_message_id": message.id,
                "result": result,
                "success": result is not None
            }
            self.send_message(message.from_module, "api_response", callback_data, message.to_module)
    
    def _handle_file_message(self, message: Message):
        """处理文件消息"""
        source_path = message.data.get("source_path", "")
        target_path = message.data.get("target_path", "")
        operation = message.data.get("operation", "copy")
        
        try:
            source = Path(source_path)
            target = Path(target_path)
            
            if operation == "copy" and source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(source, target)
                self.stats["file_operations"] += 1
                
            elif operation == "move" and source.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                source.rename(target)
                self.stats["file_operations"] += 1
                
            self.log_communication_event("file_operation", message.to_module,
                                        f"{operation} {source} -> {target}")
                                        
        except Exception as e:
            raise Exception(f"文件操作失败: {e}")
    
    def _handle_event_message(self, message: Message):
        """处理事件消息"""
        event_type = message.data.get("event_type", "")
        event_data = message.data.get("event_data", {})
        
        # 触发事件处理器
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    self.logger.error(f"事件处理器失败: {event_type} -> {e}")
    
    def _handle_generic_message(self, message: Message):
        """处理通用消息"""
        # 保存到文件系统
        comm_dir = Path("data/communication")
        inbox_dir = comm_dir / message.to_module / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        message_file = inbox_dir / f"{message.id}.json"
        with open(message_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(message), f, indent=2, ensure_ascii=False)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"注册事件处理器: {event_type}")
    
    def save_message_to_db(self, message: Message, status: str):
        """保存消息到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO messages 
                    (id, from_module, to_module, message_type, data, timestamp, status, retry_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id, message.from_module, message.to_module,
                    message.message_type, json.dumps(message.data),
                    message.timestamp, status, message.retry_count
                ))
        except Exception as e:
            self.logger.error(f"保存消息到数据库失败: {e}")
    
    def log_communication_event(self, event_type: str, module_name: str, details: str):
        """记录通信事件"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO communication_log (timestamp, event_type, module_name, details)
                    VALUES (?, ?, ?, ?)
                """, (datetime.now().isoformat(), event_type, module_name, details))
        except Exception as e:
            self.logger.error(f"记录通信事件失败: {e}")
    
    def get_communication_stats(self) -> Dict:
        """获取通信统计"""
        return {
            **self.stats,
            "active_endpoints": len(self.endpoints),
            "queue_size": self.message_queue.qsize(),
            "event_handlers": len(self.event_handlers)
        }
    
    def health_check(self) -> Dict:
        """健康检查"""
        results = {}
        
        for module_name, endpoint in self.endpoints.items():
            try:
                response = requests.get(f"{endpoint.base_url}/health", timeout=5)
                results[module_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                results[module_name] = {
                    "status": "unreachable",
                    "error": str(e)
                }
        
        return results
    
    def shutdown(self):
        """关闭通信管理器"""
        self.running = False
        if self.message_thread.is_alive():
            self.message_thread.join(timeout=5)
        self.logger.info("通信管理器已关闭")


# 全局通信管理器实例
_comm_manager = None

def get_communication_manager() -> CommunicationManager:
    """获取全局通信管理器实例"""
    global _comm_manager
    if _comm_manager is None:
        _comm_manager = CommunicationManager()
    return _comm_manager


def main():
    """主函数 - 测试通信管理器"""
    comm = CommunicationManager()
    
    print("🔗 模块间通信管理器测试")
    
    # 注册测试端点
    comm.register_endpoint("test_module", "localhost", 8000)
    
    # 发送测试消息
    comm.send_message("test_module", "test_message", {"content": "Hello World"})
    
    # 获取统计信息
    stats = comm.get_communication_stats()
    print(f"\n通信统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 健康检查
    health = comm.health_check()
    print(f"\n健康检查:")
    for module, status in health.items():
        print(f"  {module}: {status}")
    
    # 等待消息处理
    time.sleep(2)
    
    # 关闭
    comm.shutdown()


if __name__ == "__main__":
    main()
