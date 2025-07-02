# -*- coding: utf-8 -*-
"""
系统检查工具模块

提供系统依赖检查、资源状态监控和端口可用性检查等功能。

更新日志：
- 2024-06-25：初始版本，提供基本系统检查功能
"""

import os
import sys
import json
import platform
import importlib
import subprocess
from pathlib import Path

# 尝试导入可选模块
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import socket
    HAS_SOCKET = True
except ImportError:
    HAS_SOCKET = False


def load_config():
    """
    加载系统配置
    
    Returns:
        dict: 系统配置字典，如果加载失败则返回默认配置
    """
    # 默认配置
    default_config = {
        "version": "1.0.0",
        "min_python_version": [3, 6],
        "required_disk_space_mb": 100,
        "check_dependencies": True,
        "module_ports": {
            "question_bank": 5000,
            "grading_center": 5173,
            "exam_management": 5001,
            "client": 8080
        }
    }
    
    # 尝试加载配置文件
    try:
        config_path = Path(__file__).parent.parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        return default_config


def check_python_version(min_version=None):
    """
    检查Python版本是否满足要求
    
    Args:
        min_version (list, optional): 最低Python版本要求，如[3, 6]
        
    Returns:
        tuple: (是否满足要求, 当前版本, 最低要求版本)
    """
    if min_version is None:
        config = load_config()
        min_version = config.get("min_python_version", [3, 6])
    
    current_version = list(sys.version_info[:3])
    min_version_str = ".".join(map(str, min_version))
    current_version_str = ".".join(map(str, current_version[:len(min_version)]))
    
    # 比较版本
    for i in range(len(min_version)):
        if i >= len(current_version):
            return False, current_version_str, min_version_str
        if current_version[i] > min_version[i]:
            return True, current_version_str, min_version_str
        if current_version[i] < min_version[i]:
            return False, current_version_str, min_version_str
    
    return True, current_version_str, min_version_str


def check_module_exists(module_path):
    """
    检查模块文件是否存在
    
    Args:
        module_path (str): 模块文件路径
        
    Returns:
        bool: 模块文件是否存在
    """
    return os.path.exists(module_path)


def check_package_installed(package_name):
    """
    检查Python包是否已安装
    
    Args:
        package_name (str): 包名称
        
    Returns:
        bool: 包是否已安装
    """
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False


def install_package(package_name):
    """
    安装Python包
    
    Args:
        package_name (str): 包名称
        
    Returns:
        bool: 安装是否成功
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return True
    except subprocess.CalledProcessError:
        return False


def check_disk_space(required_mb=None):
    """
    检查磁盘空间是否足够
    
    Args:
        required_mb (int, optional): 所需磁盘空间（MB）
        
    Returns:
        tuple: (是否足够, 可用空间(MB), 所需空间(MB))
    """
    if required_mb is None:
        config = load_config()
        required_mb = config.get("required_disk_space_mb", 100)
    
    if HAS_PSUTIL:
        # 获取当前目录所在磁盘的可用空间
        current_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        disk_usage = psutil.disk_usage(current_dir)
        free_mb = disk_usage.free / (1024 * 1024)  # 转换为MB
        return free_mb >= required_mb, free_mb, required_mb
    else:
        # 如果没有psutil模块，使用平台特定的方法检查
        try:
            if platform.system() == 'Windows':
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(os.getcwd()[:3]), 
                                                          None, None, ctypes.pointer(free_bytes))
                free_mb = free_bytes.value / (1024 * 1024)  # 转换为MB
            else:
                st = os.statvfs(os.getcwd())
                free_mb = st.f_bavail * st.f_frsize / (1024 * 1024)  # 转换为MB
            
            return free_mb >= required_mb, free_mb, required_mb
        except Exception as e:
            # 如果检查失败，假设空间足够
            return True, 0, required_mb


def check_port_available(port):
    """
    检查端口是否可用
    
    Args:
        port (int): 端口号
        
    Returns:
        bool: 端口是否可用
    """
    if not HAS_SOCKET:
        return True
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            return result != 0  # 如果结果不为0，表示连接失败，端口可用
    except socket.error:
        return True  # 发生错误，假设端口可用


def get_system_resources():
    """
    获取系统资源使用情况
    
    Returns:
        dict: 系统资源使用情况，包括CPU、内存和磁盘
    """
    resources = {
        "cpu_percent": 0,
        "memory_percent": 0,
        "disk_percent": 0
    }
    
    if HAS_PSUTIL:
        # CPU使用率
        resources["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        resources["memory_percent"] = memory.percent
        
        # 磁盘使用率
        current_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        disk = psutil.disk_usage(current_dir)
        resources["disk_percent"] = disk.percent
    
    return resources


def check_process_running(pid):
    """
    检查进程是否在运行
    
    Args:
        pid (int): 进程ID
        
    Returns:
        bool: 进程是否在运行
    """
    if not HAS_PSUTIL:
        return False
    
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        return False


def get_module_ports():
    """
    获取模块端口配置
    
    Returns:
        dict: 模块端口配置
    """
    config = load_config()
    return config.get("module_ports", {
        "question_bank": 5000,
        "grading_center": 5173,
        "exam_management": 5001,
        "client": 8080
    })


def check_all_dependencies():
    """
    检查所有依赖项
    
    Returns:
        dict: 依赖项检查结果
    """
    dependencies = {
        "flask": check_package_installed("flask"),
        "pandas": check_package_installed("pandas"),
        "openpyxl": check_package_installed("openpyxl"),
        "pillow": check_package_installed("PIL"),
        "requests": check_package_installed("requests"),
        "psutil": check_package_installed("psutil")
    }
    
    return dependencies


if __name__ == "__main__":
    # 测试系统检查功能
    print("系统信息:")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    
    # 检查Python版本
    version_ok, current_version, min_version = check_python_version()
    print(f"Python版本检查: {'通过' if version_ok else '不通过'} (当前: {current_version}, 最低要求: {min_version})")
    
    # 检查依赖项
    dependencies = check_all_dependencies()
    print("\n依赖项检查:")
    for package, installed in dependencies.items():
        print(f"{package}: {'已安装' if installed else '未安装'}")
    
    # 检查磁盘空间
    space_ok, free_mb, required_mb = check_disk_space()
    print(f"\n磁盘空间检查: {'通过' if space_ok else '不通过'} (可用: {free_mb:.2f} MB, 需要: {required_mb} MB)")
    
    # 检查端口可用性
    module_ports = get_module_ports()
    print("\n端口可用性检查:")
    for module, port in module_ports.items():
        available = check_port_available(port)
        print(f"{module} (端口 {port}): {'可用' if available else '被占用'}")
    
    # 获取系统资源使用情况
    if HAS_PSUTIL:
        resources = get_system_resources()
        print("\n系统资源使用情况:")
        print(f"CPU使用率: {resources['cpu_percent']}%")
        print(f"内存使用率: {resources['memory_percent']}%")
        print(f"磁盘使用率: {resources['disk_percent']}%")
    else:
        print("\n未安装psutil模块，无法获取系统资源使用情况")