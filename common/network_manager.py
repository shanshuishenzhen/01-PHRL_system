# -*- coding: utf-8 -*-
"""
网络通信工具模块

提供HTTP请求、WebSocket通信、模块间通信等功能。

更新日志：
- 2024-06-25：初始版本，提供基本网络通信功能
"""

import os
import sys
import json
import socket
import time
import threading
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.config_manager import load_config

# 创建日志记录器
logger = get_logger("network_manager", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "network_manager.log"))

# 尝试导入可选模块
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.warning("requests模块未安装，HTTP请求功能将不可用")

try:
    import websocket
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False
    logger.warning("websocket-client模块未安装，WebSocket通信功能将不可用")


class HTTPClient:
    """
    HTTP客户端，用于发送HTTP请求
    """
    def __init__(self, base_url="", timeout=10, headers=None):
        """
        初始化HTTP客户端
        
        Args:
            base_url (str, optional): 基础URL
            timeout (int, optional): 超时时间（秒）
            headers (dict, optional): 请求头
        """
        if not HAS_REQUESTS:
            raise ImportError("requests模块未安装，无法使用HTTP客户端")
        
        self.base_url = base_url
        self.timeout = timeout
        self.headers = headers or {}
        self.session = requests.Session()
    
    def get(self, url, params=None, **kwargs):
        """
        发送GET请求
        
        Args:
            url (str): 请求URL
            params (dict, optional): 查询参数
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        try:
            full_url = urljoin(self.base_url, url) if self.base_url else url
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", self.headers)
            
            response = self.session.get(full_url, params=params, **kwargs)
            return response
        except Exception as e:
            logger.error(f"GET请求失败: {url}, 错误: {str(e)}")
            raise
    
    def post(self, url, data=None, json=None, **kwargs):
        """
        发送POST请求
        
        Args:
            url (str): 请求URL
            data (dict, optional): 表单数据
            json (dict, optional): JSON数据
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        try:
            full_url = urljoin(self.base_url, url) if self.base_url else url
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", self.headers)
            
            response = self.session.post(full_url, data=data, json=json, **kwargs)
            return response
        except Exception as e:
            logger.error(f"POST请求失败: {url}, 错误: {str(e)}")
            raise
    
    def put(self, url, data=None, **kwargs):
        """
        发送PUT请求
        
        Args:
            url (str): 请求URL
            data (dict, optional): 请求数据
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        try:
            full_url = urljoin(self.base_url, url) if self.base_url else url
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", self.headers)
            
            response = self.session.put(full_url, data=data, **kwargs)
            return response
        except Exception as e:
            logger.error(f"PUT请求失败: {url}, 错误: {str(e)}")
            raise
    
    def delete(self, url, **kwargs):
        """
        发送DELETE请求
        
        Args:
            url (str): 请求URL
            **kwargs: 其他参数
            
        Returns:
            requests.Response: 响应对象
        """
        try:
            full_url = urljoin(self.base_url, url) if self.base_url else url
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", self.headers)
            
            response = self.session.delete(full_url, **kwargs)
            return response
        except Exception as e:
            logger.error(f"DELETE请求失败: {url}, 错误: {str(e)}")
            raise
    
    def download_file(self, url, save_path, chunk_size=8192, **kwargs):
        """
        下载文件
        
        Args:
            url (str): 文件URL
            save_path (str): 保存路径
            chunk_size (int, optional): 块大小
            **kwargs: 其他参数
            
        Returns:
            bool: 是否成功下载
        """
        try:
            full_url = urljoin(self.base_url, url) if self.base_url else url
            kwargs.setdefault("timeout", self.timeout)
            kwargs.setdefault("headers", self.headers)
            kwargs.setdefault("stream", True)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # 下载文件
            response = self.session.get(full_url, **kwargs)
            response.raise_for_status()
            
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"文件已下载: {save_path}")
            return True
        except Exception as e:
            logger.error(f"下载文件失败: {url}, 错误: {str(e)}")
            return False
    
    def close(self):
        """
        关闭会话
        """
        self.session.close()


class WebSocketClient:
    """
    WebSocket客户端，用于WebSocket通信
    """
    def __init__(self, url, on_message=None, on_error=None, on_close=None, on_open=None, headers=None):
        """
        初始化WebSocket客户端
        
        Args:
            url (str): WebSocket URL
            on_message (callable, optional): 消息回调函数
            on_error (callable, optional): 错误回调函数
            on_close (callable, optional): 关闭回调函数
            on_open (callable, optional): 打开回调函数
            headers (dict, optional): 请求头
        """
        if not HAS_WEBSOCKET:
            raise ImportError("websocket-client模块未安装，无法使用WebSocket客户端")
        
        self.url = url
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.on_open = on_open
        self.headers = headers or {}
        self.ws = None
        self.thread = None
        self.running = False
    
    def _on_message(self, ws, message):
        """
        消息回调函数
        
        Args:
            ws: WebSocket对象
            message: 消息内容
        """
        try:
            if self.on_message:
                self.on_message(message)
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {str(e)}")
    
    def _on_error(self, ws, error):
        """
        错误回调函数
        
        Args:
            ws: WebSocket对象
            error: 错误信息
        """
        logger.error(f"WebSocket错误: {str(error)}")
        try:
            if self.on_error:
                self.on_error(error)
        except Exception as e:
            logger.error(f"处理WebSocket错误失败: {str(e)}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """
        关闭回调函数
        
        Args:
            ws: WebSocket对象
            close_status_code: 关闭状态码
            close_msg: 关闭消息
        """
        logger.info(f"WebSocket已关闭: {close_status_code} {close_msg}")
        self.running = False
        try:
            if self.on_close:
                self.on_close(close_status_code, close_msg)
        except Exception as e:
            logger.error(f"处理WebSocket关闭失败: {str(e)}")
    
    def _on_open(self, ws):
        """
        打开回调函数
        
        Args:
            ws: WebSocket对象
        """
        logger.info(f"WebSocket已连接: {self.url}")
        self.running = True
        try:
            if self.on_open:
                self.on_open()
        except Exception as e:
            logger.error(f"处理WebSocket打开失败: {str(e)}")
    
    def connect(self, reconnect=False, reconnect_interval=5, max_reconnect=5):
        """
        连接WebSocket服务器
        
        Args:
            reconnect (bool, optional): 是否自动重连
            reconnect_interval (int, optional): 重连间隔（秒）
            max_reconnect (int, optional): 最大重连次数
            
        Returns:
            bool: 是否成功连接
        """
        try:
            # 创建WebSocket对象
            self.ws = websocket.WebSocketApp(
                self.url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open,
                header=self.headers
            )
            
            # 启动WebSocket线程
            self.thread = threading.Thread(target=self._run_forever, args=(reconnect, reconnect_interval, max_reconnect))
            self.thread.daemon = True
            self.thread.start()
            
            # 等待连接建立
            for _ in range(10):
                if self.running:
                    return True
                time.sleep(0.5)
            
            return self.running
        except Exception as e:
            logger.error(f"连接WebSocket失败: {self.url}, 错误: {str(e)}")
            return False
    
    def _run_forever(self, reconnect, reconnect_interval, max_reconnect):
        """
        运行WebSocket循环
        
        Args:
            reconnect (bool): 是否自动重连
            reconnect_interval (int): 重连间隔（秒）
            max_reconnect (int): 最大重连次数
        """
        reconnect_count = 0
        while True:
            try:
                self.ws.run_forever()
                
                # 如果不需要重连或已达到最大重连次数，退出循环
                if not reconnect or (max_reconnect > 0 and reconnect_count >= max_reconnect):
                    break
                
                # 重连
                reconnect_count += 1
                logger.info(f"正在重连WebSocket ({reconnect_count}/{max_reconnect})...")
                time.sleep(reconnect_interval)
            except Exception as e:
                logger.error(f"WebSocket循环异常: {str(e)}")
                break
    
    def send(self, message):
        """
        发送消息
        
        Args:
            message (str or dict): 消息内容，如果是字典则会转换为JSON字符串
            
        Returns:
            bool: 是否成功发送
        """
        try:
            if not self.ws or not self.running:
                logger.error("WebSocket未连接，无法发送消息")
                return False
            
            # 如果消息是字典，转换为JSON字符串
            if isinstance(message, dict):
                message = json.dumps(message)
            
            self.ws.send(message)
            return True
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {str(e)}")
            return False
    
    def close(self):
        """
        关闭WebSocket连接
        
        Returns:
            bool: 是否成功关闭
        """
        try:
            if self.ws:
                self.ws.close()
                self.running = False
                if self.thread and self.thread.is_alive():
                    self.thread.join(timeout=1)
                return True
            return False
        except Exception as e:
            logger.error(f"关闭WebSocket失败: {str(e)}")
            return False


class ModuleCommunicator:
    """
    模块通信器，用于系统内部模块间通信
    """
    def __init__(self):
        """
        初始化模块通信器
        """
        self.config = load_config()
        self.module_ports = self.config.get("module_ports", {})
    
    def get_module_url(self, module_name, endpoint=""):
        """
        获取模块URL
        
        Args:
            module_name (str): 模块名称
            endpoint (str, optional): 接口路径
            
        Returns:
            str: 模块URL
        """
        if module_name not in self.module_ports:
            logger.error(f"未知模块: {module_name}")
            return None
        
        port = self.module_ports[module_name]
        base_url = f"http://localhost:{port}"
        return urljoin(base_url, endpoint)
    
    def send_request(self, module_name, endpoint, method="GET", data=None, json_data=None, params=None, timeout=10):
        """
        向模块发送HTTP请求
        
        Args:
            module_name (str): 模块名称
            endpoint (str): 接口路径
            method (str, optional): 请求方法
            data (dict, optional): 表单数据
            json_data (dict, optional): JSON数据
            params (dict, optional): 查询参数
            timeout (int, optional): 超时时间（秒）
            
        Returns:
            dict: 响应数据，如果请求失败则返回None
        """
        if not HAS_REQUESTS:
            logger.error("requests模块未安装，无法发送HTTP请求")
            return None
        
        url = self.get_module_url(module_name, endpoint)
        if not url:
            return None
        
        try:
            client = HTTPClient(timeout=timeout)
            
            if method.upper() == "GET":
                response = client.get(url, params=params)
            elif method.upper() == "POST":
                response = client.post(url, data=data, json=json_data)
            elif method.upper() == "PUT":
                response = client.put(url, data=data if data else json_data)
            elif method.upper() == "DELETE":
                response = client.delete(url)
            else:
                logger.error(f"不支持的请求方法: {method}")
                return None
            
            response.raise_for_status()
            
            # 尝试解析JSON响应
            try:
                return response.json()
            except:
                return {"status": "success", "data": response.text}
        except Exception as e:
            logger.error(f"向模块 {module_name} 发送请求失败: {endpoint}, 错误: {str(e)}")
            return None
        finally:
            client.close()
    
    def check_module_status(self, module_name):
        """
        检查模块状态
        
        Args:
            module_name (str): 模块名称
            
        Returns:
            bool: 模块是否在线
        """
        if module_name not in self.module_ports:
            logger.error(f"未知模块: {module_name}")
            return False
        
        port = self.module_ports[module_name]
        
        try:
            # 尝试连接模块端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            
            return result == 0
        except Exception as e:
            logger.error(f"检查模块状态失败: {module_name}, 错误: {str(e)}")
            return False


def get_local_ip():
    """
    获取本机IP地址
    
    Returns:
        str: 本机IP地址
    """
    try:
        # 创建一个临时套接字连接到一个公共地址，以获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logger.error(f"获取本机IP地址失败: {str(e)}")
        # 如果上述方法失败，尝试获取所有网络接口
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception as e:
            logger.error(f"获取本机IP地址失败: {str(e)}")
            return "127.0.0.1"


def check_port_available(port, host="localhost"):
    """
    检查端口是否可用
    
    Args:
        port (int): 端口号
        host (str, optional): 主机名
        
    Returns:
        bool: 端口是否可用
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        # 如果结果为0，表示端口已被占用
        return result != 0
    except Exception as e:
        logger.error(f"检查端口可用性失败: {host}:{port}, 错误: {str(e)}")
        return False


def find_available_port(start_port=8000, end_port=9000, host="localhost"):
    """
    查找可用端口
    
    Args:
        start_port (int, optional): 起始端口
        end_port (int, optional): 结束端口
        host (str, optional): 主机名
        
    Returns:
        int: 可用端口，如果没有可用端口则返回None
    """
    for port in range(start_port, end_port + 1):
        if check_port_available(port, host):
            return port
    
    logger.error(f"在范围 {start_port}-{end_port} 内没有可用端口")
    return None


if __name__ == "__main__":
    # 测试网络通信功能
    print("本机IP地址:", get_local_ip())
    
    # 测试端口检查
    test_port = 8080
    print(f"端口 {test_port} 可用性:", check_port_available(test_port))
    
    # 测试查找可用端口
    available_port = find_available_port(8000, 8100)
    print(f"可用端口: {available_port}")
    
    # 测试HTTP客户端（如果有requests模块）
    if HAS_REQUESTS:
        try:
            client = HTTPClient(timeout=5)
            response = client.get("https://httpbin.org/get")
            print("HTTP GET响应:", response.status_code)
            client.close()
        except Exception as e:
            print(f"HTTP请求测试失败: {str(e)}")
    else:
        print("requests模块未安装，跳过HTTP客户端测试")
    
    # 测试WebSocket客户端（如果有websocket-client模块）
    if HAS_WEBSOCKET:
        try:
            def on_message(message):
                print(f"收到消息: {message}")
            
            def on_open():
                print("WebSocket已连接")
                client.send({"type": "ping"})
            
            client = WebSocketClient(
                "wss://echo.websocket.org",
                on_message=on_message,
                on_open=on_open
            )
            
            if client.connect():
                print("WebSocket连接成功")
                time.sleep(2)
                client.close()
            else:
                print("WebSocket连接失败")
        except Exception as e:
            print(f"WebSocket测试失败: {str(e)}")
    else:
        print("websocket-client模块未安装，跳过WebSocket客户端测试")