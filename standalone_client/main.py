#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL 独立客户端主入口

这是客户端的主入口文件，负责启动整个应用程序。
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# 添加项目根目录到系统路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

def setup_environment():
    """设置运行环境"""
    # 设置工作目录
    os.chdir(current_dir)
    
    # 创建必要的目录
    directories = [
        "logs",
        "cache", 
        "temp",
        "config"
    ]
    
    for directory in directories:
        dir_path = current_dir / directory
        dir_path.mkdir(exist_ok=True)

def main():
    """主函数"""
    try:
        # 设置环境
        setup_environment()
        
        # 导入核心应用
        from core.app import ExamClientApp
        
        # 创建主窗口
        root = tk.Tk()
        
        # 创建应用实例
        app = ExamClientApp(root)
        
        # 启动应用
        app.run()
        
    except ImportError as e:
        # 如果模块导入失败，显示错误信息
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "启动错误", 
            f"客户端启动失败：\n{e}\n\n请检查安装是否完整。"
        )
        sys.exit(1)
        
    except Exception as e:
        # 其他错误
        root = tk.Tk()
        root.withdraw()
        
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "未知错误", 
            f"客户端运行时发生错误：\n{e}\n\n请联系技术支持。"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
