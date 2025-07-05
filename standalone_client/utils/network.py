#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络工具

提供网络连接检测、状态监控等功能。
"""

import socket
import requests
import threading
import time
from typing import Callable, Optional, Dict, Any
from .logger import get_logger

logger = get_logger(__name__)

class NetworkUtils:
    """网络工具类"""
    
    @staticmethod
    def check_internet_connection(timeout: int = 5) -> bool:
        """检查互联网连接"""
        try:
            # 尝试连接到公共DNS服务器
            socket.create_connection(("8.8.8.8", 53), timeout)
            return True
        except OSError:
            return False
    
    @staticmethod
    def check_server_connection(host: str, port: int, timeout: int = 5) -> bool:
        """检查服务器连接"""
        try:
            socket.create_connection((host, port), timeout)
            return True
        except OSError:
            return False
    
    @staticmethod
    def ping_server(url: str, timeout: int = 5) -> Optional[float]:
        """Ping服务器，返回响应时间（毫秒）"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            
            if response.status_code == 200:
                return (end_time - start_time) * 1000  # 转换为毫秒
            else:
                return None
                
        except Exception:
            return None
    
    @staticmethod
    def get_local_ip() -> str:
        """获取本地IP地址"""
        try:
            # 连接到远程地址来获取本地IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    @staticmethod
    def test_port_open(host: str, port: int, timeout: int = 3) -> bool:
        """测试端口是否开放"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

class NetworkMonitor:
    """网络状态监控器"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 状态回调
        self.on_connection_lost: Optional[Callable] = None
        self.on_connection_restored: Optional[Callable] = None
        self.on_server_unreachable: Optional[Callable] = None
        self.on_server_restored: Optional[Callable] = None
        
        # 状态变量
        self.last_internet_status = True
        self.last_server_status = True
        self.server_url = ""
        
        logger.debug("网络监控器已初始化")
    
    def set_server_url(self, url: str):
        """设置要监控的服务器URL"""
        self.server_url = url
        logger.debug(f"设置监控服务器: {url}")
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("网络监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("网络监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                # 检查互联网连接
                internet_ok = NetworkUtils.check_internet_connection()
                if internet_ok != self.last_internet_status:
                    if internet_ok:
                        logger.info("互联网连接已恢复")
                        if self.on_connection_restored:
                            self.on_connection_restored()
                    else:
                        logger.warning("互联网连接已断开")
                        if self.on_connection_lost:
                            self.on_connection_lost()
                    
                    self.last_internet_status = internet_ok
                
                # 检查服务器连接
                if self.server_url and internet_ok:
                    server_ok = NetworkUtils.ping_server(self.server_url) is not None
                    if server_ok != self.last_server_status:
                        if server_ok:
                            logger.info("服务器连接已恢复")
                            if self.on_server_restored:
                                self.on_server_restored()
                        else:
                            logger.warning("服务器连接不可达")
                            if self.on_server_unreachable:
                                self.on_server_unreachable()
                        
                        self.last_server_status = server_ok
                
                # 等待下次检查
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"网络监控异常: {e}")
                time.sleep(self.check_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前网络状态"""
        return {
            "internet_connected": self.last_internet_status,
            "server_reachable": self.last_server_status,
            "monitoring": self.is_monitoring,
            "server_url": self.server_url
        }

class ConnectionManager:
    """连接管理器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.retry_count = 3
        self.retry_delay = 5
        self.timeout = 30
        
        # 设置连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0  # 我们自己处理重试
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        logger.debug("连接管理器已初始化")
    
    def configure(self, timeout: int = 30, retry_count: int = 3, retry_delay: int = 5):
        """配置连接参数"""
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        logger.debug(f"连接参数已配置: timeout={timeout}, retry={retry_count}")
    
    def request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """发起HTTP请求（带重试）"""
        kwargs.setdefault('timeout', self.timeout)
        
        for attempt in range(self.retry_count):
            try:
                logger.debug(f"发起请求: {method} {url} (尝试 {attempt + 1}/{self.retry_count})")
                response = self.session.request(method, url, **kwargs)
                
                # 检查响应状态
                if response.status_code < 500:  # 4xx和2xx都认为是成功的请求
                    return response
                else:
                    logger.warning(f"服务器错误: {response.status_code}")
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"连接错误: {e}")
            except requests.exceptions.Timeout as e:
                logger.warning(f"请求超时: {e}")
            except Exception as e:
                logger.error(f"请求异常: {e}")
                break  # 对于其他异常，不重试
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.retry_count - 1:
                logger.debug(f"等待 {self.retry_delay} 秒后重试")
                time.sleep(self.retry_delay)
        
        logger.error(f"请求失败，已尝试 {self.retry_count} 次: {method} {url}")
        return None
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET请求"""
        return self.request('GET', url, **kwargs)
    
    def post(self, url: str, **kwargs) -> Optional[requests.Response]:
        """POST请求"""
        return self.request('POST', url, **kwargs)
    
    def put(self, url: str, **kwargs) -> Optional[requests.Response]:
        """PUT请求"""
        return self.request('PUT', url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> Optional[requests.Response]:
        """DELETE请求"""
        return self.request('DELETE', url, **kwargs)
    
    def close(self):
        """关闭连接"""
        self.session.close()
        logger.debug("连接管理器已关闭")

# 全局实例
network_monitor = NetworkMonitor()
connection_manager = ConnectionManager()
