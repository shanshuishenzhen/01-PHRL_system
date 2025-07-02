# -*- coding: utf-8 -*-
"""
进程管理工具模块

提供系统模块的启动、停止和状态监控功能。

更新日志：
- 2024-06-25：初始版本，提供基本进程管理功能
"""

import os
import sys
import time
import signal
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

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.config_manager import load_config, ConfigManager

# 创建配置管理器实例
config_manager = ConfigManager()
from common.system_checker import check_port_available

# 创建配置管理器实例
config_manager = ConfigManager()


def start_module(module_name, module_path, port=None, cwd=None, auto_restart=False):
    """
    启动系统模块
    
    Args:
        module_name (str): 模块名称
        module_path (str): 模块文件路径
        port (int, optional): 模块使用的端口
        cwd (str, optional): 工作目录
        auto_restart (bool, optional): 是否自动重启
        
    Returns:
        dict: 模块信息，包括进程ID、启动时间等
    """
    # 检查模块文件是否存在
    if not os.path.exists(module_path):
        return {
            "status": "error",
            "message": f"模块文件不存在: {module_path}",
            "pid": None,
            "start_time": None
        }
    
    # 如果指定了端口，检查端口是否可用
    if port is not None and not check_port_available(port):
        return {
            "status": "error",
            "message": f"端口 {port} 已被占用",
            "pid": None,
            "start_time": None
        }
    
    # 设置工作目录
    if cwd is None:
        cwd = os.path.dirname(module_path)
    
    # 根据操作系统选择启动方式
    if os.name == 'nt':  # Windows
        # 在新的命令行窗口中启动模块
        cmd = f"start cmd /k python \"{module_path}\""
        process = subprocess.Popen(cmd, shell=True, cwd=cwd)
    else:  # Linux/Mac
        # 在后台启动模块
        process = subprocess.Popen(
            [sys.executable, module_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
        )
    
    # 等待一段时间，确保进程启动
    time.sleep(1)
    
    # 获取进程ID和启动时间
    pid = process.pid
    start_time = time.time()
    
    return {
        "status": "starting",
        "message": f"模块 {module_name} 正在启动",
        "pid": pid,
        "start_time": start_time,
        "auto_restart": auto_restart
    }


def check_numpy_import_issue(module_name, cwd):
    """
    检查并解决numpy导入问题
    
    Args:
        module_name (str): 模块名称
        cwd (str): 工作目录
        
    Returns:
        tuple: (是否需要特殊处理, 环境变量字典)
    """
    # 只对题库管理模块进行特殊处理
    if module_name != "question_bank":
        return False, {}
    
    # 检查是否存在虚拟环境
    venv_path = os.path.join(os.path.dirname(cwd), "venv_qb")
    if not os.path.exists(venv_path):
        return False, {}
    
    # 创建环境变量字典，确保在正确的环境中运行
    env_vars = os.environ.copy()
    
    # 设置PYTHONPATH，避免从当前目录导入numpy
    if "PYTHONPATH" in env_vars:
        # 移除可能导致冲突的路径
        paths = env_vars["PYTHONPATH"].split(os.pathsep)
        filtered_paths = [p for p in paths if not os.path.basename(p).lower() == "numpy"]
        env_vars["PYTHONPATH"] = os.pathsep.join(filtered_paths)
    
    # 在Windows上，设置虚拟环境的Python解释器路径
    if os.name == 'nt':
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        if os.path.exists(python_exe):
            return True, env_vars, python_exe
    else:  # Linux/Mac
        python_exe = os.path.join(venv_path, "bin", "python")
        if os.path.exists(python_exe):
            return True, env_vars, python_exe
    
    return False, {}, sys.executable


def start_web_module(module_name, module_path, port, host="127.0.0.1", cwd=None, auto_restart=False, open_browser=False):
    """
    启动Web模块
    
    Args:
        module_name (str): 模块名称
        module_path (str): 模块文件路径
        port (int): 模块使用的端口
        host (str, optional): 主机地址
        cwd (str, optional): 工作目录
        auto_restart (bool, optional): 是否自动重启
        open_browser (bool, optional): 是否自动打开浏览器
        
    Returns:
        dict: 模块信息，包括进程ID、启动时间等
    """
    # 检查模块文件是否存在
    if not os.path.exists(module_path):
        return {
            "status": "error",
            "message": f"模块文件不存在: {module_path}",
            "pid": None,
            "start_time": None
        }
    
    # 检查端口是否可用
    if not check_port_available(port):
        return {
            "status": "error",
            "message": f"端口 {port} 已被占用",
            "pid": None,
            "start_time": None
        }
    
    # 设置工作目录
    if cwd is None:
        cwd = os.path.dirname(module_path)
    
    # 检查并解决numpy导入问题
    result = check_numpy_import_issue(module_name, cwd)
    use_special_env = result[0]
    env_vars = result[1] if len(result) > 1 else {}
    python_exe = result[2] if len(result) > 2 else sys.executable
    
    # 记录启动信息
    print(f"启动Web模块: {module_name}")
    print(f"模块路径: {module_path}")
    print(f"工作目录: {cwd}")
    print(f"端口: {port}")
    print(f"使用特殊环境: {use_special_env}")
    if use_special_env:
        print(f"Python解释器: {python_exe}")
    
    # 根据操作系统选择启动方式
    if os.name == 'nt':  # Windows
        # 在新的命令行窗口中启动Flask应用
        if module_name == "question_bank":
            if use_special_env:
                # 使用虚拟环境的Python解释器
                run_script = os.path.join(cwd, "run.py")
                if os.path.exists(run_script):
                    # 使用/k保持窗口打开，便于查看错误信息
                    # 注意：run.py中硬编码了端口5000，所以这里不需要指定端口
                    cmd = f"start cmd /k cd {cwd} && \"{python_exe}\" \"{run_script}\""
                    print(f"使用run.py脚本启动: {run_script}")
                    # 更新端口为5000，因为run.py中硬编码了这个端口
                    port = 5000
                else:
                    cmd = f"start cmd /k cd {cwd} && \"{python_exe}\" -m flask run --host={host} --port={port}"
                    print("使用flask命令启动")
            else:
                cmd = f"start cmd /k cd {cwd} && python -m flask run --host={host} --port={port}"
                print("使用系统Python启动flask")
        else:
            cmd = f"start cmd /k python \"{module_path}\" --host={host} --port={port}"
        
        # 记录启动命令
        print(f"启动命令: {cmd}")
        
        process = subprocess.Popen(cmd, shell=True, cwd=cwd, env=env_vars if use_special_env else None)
    else:  # Linux/Mac
        # 在后台启动Flask应用
        if module_name == "question_bank":
            if use_special_env:
                # 使用虚拟环境的Python解释器
                run_script = os.path.join(cwd, "run.py")
                if os.path.exists(run_script):
                    process = subprocess.Popen(
                        [python_exe, run_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=cwd,
                        env=env_vars
                    )
                else:
                    process = subprocess.Popen(
                        [python_exe, "-m", "flask", "run", f"--host={host}", f"--port={port}"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=cwd,
                        env=env_vars
                    )
            else:
                process = subprocess.Popen(
                    [sys.executable, "-m", "flask", "run", f"--host={host}", f"--port={port}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd
                )
        else:
            process = subprocess.Popen(
                [sys.executable, module_path, f"--host={host}", f"--port={port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd
            )
    
    # 等待一段时间，确保进程启动
    time.sleep(2)
    
    # 获取进程ID和启动时间
    pid = process.pid
    start_time = time.time()
    
    # 如果需要自动打开浏览器
    if open_browser:
        try:
            import webbrowser
            url = f"http://{host}:{port}"
            webbrowser.open_new(url)
        except ImportError:
            pass
    
    return {
        "status": "starting",
        "message": f"模块 {module_name} 正在启动",
        "pid": pid,
        "start_time": start_time,
        "url": f"http://{host}:{port}",
        "auto_restart": auto_restart
    }


def stop_module(pid):
    """
    停止系统模块
    
    Args:
        pid (int): 进程ID
        
    Returns:
        bool: 是否成功停止
    """
    if not pid:
        return False
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
        else:  # Linux/Mac
            os.kill(pid, signal.SIGTERM)
        return True
    except (subprocess.SubprocessError, OSError):
        return False


def check_module_status(module_name, pid=None, port=None):
    """
    检查模块状态
    
    Args:
        module_name (str): 模块名称
        pid (int, optional): 进程ID
        port (int, optional): 模块使用的端口
        
    Returns:
        str: 模块状态，可能的值有'running', 'starting', 'stopped', 'error'
    """
    # 如果没有提供进程ID和端口，无法检查状态
    if pid is None and port is None:
        return "unknown"
    
    # 检查进程是否在运行
    process_running = False
    if pid is not None and HAS_PSUTIL:
        try:
            process = psutil.Process(pid)
            process_running = process.is_running()
        except psutil.NoSuchProcess:
            process_running = False
    
    # 检查端口是否被占用
    port_in_use = False
    if port is not None and HAS_SOCKET:
        port_in_use = not check_port_available(port)
    
    # 根据进程和端口状态判断模块状态
    if process_running and port_in_use:
        return "running"
    elif process_running and not port_in_use:
        return "starting"
    elif not process_running and port_in_use:
        return "error"  # 进程不在运行但端口被占用
    else:
        return "stopped"


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


def get_module_path(module_name):
    """
    获取模块文件路径
    
    Args:
        module_name (str): 模块名称
        
    Returns:
        str: 模块文件路径
    """
    base_dir = Path(__file__).parent.parent
    
    module_paths = {
        "main_console": base_dir / "main_console.py",
        "question_bank": base_dir / "question_bank_web" / "app.py",
        "grading_center": base_dir / "grading_center" / "server" / "app.js",
        "exam_management": base_dir / "exam_management" / "simple_exam_manager.py",
        "client": base_dir / "client" / "client_app.py",
        "user_management": base_dir / "user_management" / "simple_user_manager.py",
        "developer_tools": base_dir / "developer_tools.py"
    }
    
    return str(module_paths.get(module_name, ""))


def get_module_working_dir(module_name):
    """
    获取模块工作目录
    
    Args:
        module_name (str): 模块名称
        
    Returns:
        str: 模块工作目录
    """
    base_dir = Path(__file__).parent.parent
    
    module_dirs = {
        "question_bank": base_dir / "question_bank_web",
        "grading_center": base_dir / "grading_center" / "server",
        "exam_management": base_dir / "exam_management",
        "client": base_dir / "client",
        "developer_tools": base_dir
    }
    
    return str(module_dirs.get(module_name, base_dir))


def restart_module(module_name, pid=None, port=None):
    """
    重启系统模块
    
    Args:
        module_name (str): 模块名称
        pid (int, optional): 进程ID
        port (int, optional): 模块使用的端口
        
    Returns:
        dict: 模块信息，包括进程ID、启动时间等
    """
    # 如果提供了进程ID，先停止模块
    if pid is not None:
        stop_module(pid)
    
    # 获取模块路径和端口
    module_path = get_module_path(module_name)
    if not port:
        module_ports = get_module_ports()
        port = module_ports.get(module_name)
    
    # 获取模块工作目录
    cwd = get_module_working_dir(module_name)
    
    # 获取自动重启设置并确保为布尔值
    auto_restart = bool(config_manager.get("auto_restart_crashed_modules", False))
    
    # 启动模块
    if module_name in ["question_bank", "grading_center", "exam_management"]:
        return start_web_module(
            module_name,
            module_path,
            port,
            cwd=cwd,
            auto_restart=auto_restart
        )
    else:
        return start_module(
            module_name,
            module_path,
            port=port,
            cwd=cwd,
            auto_restart=auto_restart
        )


if __name__ == "__main__":
    # 测试进程管理功能
    print("模块端口配置:")
    ports = get_module_ports()
    for module, port in ports.items():
        print(f"{module}: {port}")
    
    # 测试获取模块路径
    print("\n模块文件路径:")
    for module in ports.keys():
        path = get_module_path(module)
        print(f"{module}: {path}")
        print(f"  文件存在: {os.path.exists(path)}")
    
    # 测试端口可用性
    print("\n端口可用性:")
    for module, port in ports.items():
        available = check_port_available(port)
        print(f"{module} (端口 {port}): {'可用' if available else '被占用'}")