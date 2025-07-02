"""
测试辅助工具

提供测试中常用的辅助函数。
"""

import os
import sys
import json
import time
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager


def wait_for_condition(condition_func, timeout=30, interval=1):
    """
    等待条件满足
    
    Args:
        condition_func: 条件函数，返回True表示条件满足
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）
        
    Returns:
        bool: 是否在超时前满足条件
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False


def wait_for_port(port, host='localhost', timeout=30):
    """
    等待端口可用
    
    Args:
        port: 端口号
        host: 主机地址
        timeout: 超时时间（秒）
        
    Returns:
        bool: 端口是否可用
    """
    import socket
    
    def check_port():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    return wait_for_condition(check_port, timeout)


def wait_for_file(file_path, timeout=30):
    """
    等待文件存在
    
    Args:
        file_path: 文件路径
        timeout: 超时时间（秒）
        
    Returns:
        bool: 文件是否存在
    """
    return wait_for_condition(lambda: Path(file_path).exists(), timeout)


def create_test_file(file_path, content="", encoding="utf-8"):
    """
    创建测试文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 文件编码
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding=encoding)


def create_test_json_file(file_path, data):
    """
    创建测试JSON文件
    
    Args:
        file_path: 文件路径
        data: JSON数据
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def cleanup_test_files(*file_paths):
    """
    清理测试文件
    
    Args:
        *file_paths: 文件路径列表
    """
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)


@contextmanager
def temporary_file(content="", suffix=".txt", encoding="utf-8"):
    """
    临时文件上下文管理器
    
    Args:
        content: 文件内容
        suffix: 文件后缀
        encoding: 文件编码
        
    Yields:
        Path: 临时文件路径
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, 
                                   encoding=encoding, delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)
    
    try:
        yield temp_path
    finally:
        if temp_path.exists():
            temp_path.unlink()


@contextmanager
def temporary_directory():
    """
    临时目录上下文管理器
    
    Yields:
        Path: 临时目录路径
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


@contextmanager
def change_directory(path):
    """
    临时改变工作目录
    
    Args:
        path: 目标目录路径
        
    Yields:
        Path: 目标目录路径
    """
    original_cwd = Path.cwd()
    target_path = Path(path)
    os.chdir(target_path)
    try:
        yield target_path
    finally:
        os.chdir(original_cwd)


def run_command(command, cwd=None, timeout=30, capture_output=True):
    """
    运行命令
    
    Args:
        command: 命令字符串或列表
        cwd: 工作目录
        timeout: 超时时间（秒）
        capture_output: 是否捕获输出
        
    Returns:
        subprocess.CompletedProcess: 命令执行结果
    """
    if isinstance(command, str):
        command = command.split()
    
    return subprocess.run(
        command,
        cwd=cwd,
        timeout=timeout,
        capture_output=capture_output,
        text=True
    )


def is_port_in_use(port, host='localhost'):
    """
    检查端口是否被占用
    
    Args:
        port: 端口号
        host: 主机地址
        
    Returns:
        bool: 端口是否被占用
    """
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def find_free_port(start_port=8000, end_port=9000):
    """
    查找空闲端口
    
    Args:
        start_port: 起始端口
        end_port: 结束端口
        
    Returns:
        int: 空闲端口号，如果没有找到返回None
    """
    import socket
    
    for port in range(start_port, end_port + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            continue
    return None


def get_test_data_path(filename):
    """
    获取测试数据文件路径
    
    Args:
        filename: 文件名
        
    Returns:
        Path: 测试数据文件路径
    """
    return Path(__file__).parent.parent / "data" / filename


def load_test_data(filename):
    """
    加载测试数据
    
    Args:
        filename: 文件名
        
    Returns:
        dict: 测试数据
    """
    data_path = get_test_data_path(filename)
    if data_path.suffix.lower() == '.json':
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return data_path.read_text(encoding='utf-8')


def compare_json_files(file1, file2):
    """
    比较两个JSON文件
    
    Args:
        file1: 第一个文件路径
        file2: 第二个文件路径
        
    Returns:
        bool: 文件内容是否相同
    """
    try:
        with open(file1, 'r', encoding='utf-8') as f1:
            data1 = json.load(f1)
        with open(file2, 'r', encoding='utf-8') as f2:
            data2 = json.load(f2)
        return data1 == data2
    except:
        return False


def generate_test_id():
    """
    生成测试ID
    
    Returns:
        str: 唯一的测试ID
    """
    import uuid
    return str(uuid.uuid4())[:8]


class TestTimer:
    """测试计时器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
    
    def stop(self):
        """停止计时"""
        self.end_time = time.time()
    
    def elapsed(self):
        """获取耗时"""
        if self.start_time is None:
            return 0
        end = self.end_time or time.time()
        return end - self.start_time
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
