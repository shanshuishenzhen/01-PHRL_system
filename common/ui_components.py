# -*- coding: utf-8 -*-
"""
用户界面组件模块

提供统一的UI风格和常用组件，包括主题设置、状态指示器、信息卡片等。

更新日志：
- 2024-06-25：初始版本，提供基本UI组件
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.config_manager import ConfigManager

# 创建配置管理器实例
config_manager = ConfigManager()

# 颜色主题
COLORS = {
    "primary": "#4a6baf",  # 主色调（蓝色）
    "secondary": "#6c757d",  # 次要色调（灰色）
    "success": "#28a745",  # 成功色调（绿色）
    "danger": "#dc3545",  # 危险色调（红色）
    "warning": "#ffc107",  # 警告色调（黄色）
    "info": "#17a2b8",  # 信息色调（青色）
    "light": "#f8f9fa",  # 浅色
    "dark": "#343a40",  # 深色
    "white": "#ffffff",  # 白色
    "transparent": "#ffffff",  # 透明（在Tkinter中用白色代替）
    "bg_light": "#f5f5f5",  # 浅色背景
    "bg_dark": "#212529"  # 深色背景
}

# 字体设置
FONTS = {
    "title": ("Microsoft YaHei UI", 16, "bold"),  # 标题字体
    "subtitle": ("Microsoft YaHei UI", 14, "bold"),  # 副标题字体
    "heading": ("Microsoft YaHei UI", 12, "bold"),  # 标题字体
    "normal": ("Microsoft YaHei UI", 10),  # 正文字体
    "small": ("Microsoft YaHei UI", 9),  # 小字体
    "button": ("Microsoft YaHei UI", 10),  # 按钮字体
    "status": ("Microsoft YaHei UI", 9, "italic")  # 状态字体
}

# 图标路径
ICON_PATH = Path(__file__).parent.parent / "assets" / "icons"


def setup_theme(root):
    """
    设置应用程序主题
    
    Args:
        root (tk.Tk): 根窗口
    """
    # 创建自定义样式
    style = ttk.Style(root)
    
    # 配置通用样式
    style.configure("TFrame", background=COLORS["white"])
    style.configure("TLabel", background=COLORS["white"], font=FONTS["normal"])
    style.configure("TButton", font=FONTS["button"])
    style.configure("TEntry", font=FONTS["normal"])
    
    # 配置标题样式
    style.configure("Title.TLabel", font=FONTS["title"], foreground=COLORS["primary"])
    style.configure("Subtitle.TLabel", font=FONTS["subtitle"], foreground=COLORS["secondary"])
    style.configure("Heading.TLabel", font=FONTS["heading"], foreground=COLORS["dark"])
    
    # 配置按钮样式
    style.configure("Primary.TButton", background=COLORS["primary"], foreground=COLORS["white"])
    style.configure("Success.TButton", background=COLORS["success"], foreground=COLORS["white"])
    style.configure("Danger.TButton", background=COLORS["danger"], foreground=COLORS["white"])
    style.configure("Warning.TButton", background=COLORS["warning"], foreground=COLORS["dark"])
    style.configure("Info.TButton", background=COLORS["info"], foreground=COLORS["white"])
    
    # 配置状态指示器样式
    style.configure("Running.TLabel", foreground=COLORS["success"], font=FONTS["status"])
    style.configure("Stopped.TLabel", foreground=COLORS["danger"], font=FONTS["status"])
    style.configure("Starting.TLabel", foreground=COLORS["warning"], font=FONTS["status"])
    style.configure("Unknown.TLabel", foreground=COLORS["secondary"], font=FONTS["status"])
    
    # 配置卡片样式
    style.configure("Card.TFrame", background=COLORS["white"], relief="raised", borderwidth=1)
    
    # 配置分隔线样式
    style.configure("Separator.TFrame", background=COLORS["secondary"])
    
    return style


def create_title_bar(parent, title=None, icon_path=None):
    """
    创建标题栏
    
    Args:
        parent (tk.Widget): 父窗口
        title (str, optional): 标题文本
        icon_path (str, optional): 图标路径
        
    Returns:
        ttk.Frame: 标题栏框架
    """
    # 如果没有提供标题，使用系统名称
    if title is None:
        system_info = config_manager.get("system_info", {
            "name": "PH&RL在线考试系统",
            "version": "1.0.0",
            "copyright": "© 2024 PH&RL教育科技",
            "website": "https://www.phrl-edu.com",
            "support_email": "support@phrl-edu.com"
        })
        title = system_info["name"]
    
    # 创建标题栏框架
    title_frame = ttk.Frame(parent)
    title_frame.pack(fill="x", padx=10, pady=5)
    
    # 如果提供了图标路径，显示图标
    if icon_path and os.path.exists(icon_path):
        try:
            icon_img = tk.PhotoImage(file=icon_path)
            icon_img = icon_img.subsample(2, 2)  # 缩小图标
            icon_label = ttk.Label(title_frame, image=icon_img)
            icon_label.image = icon_img  # 保持引用
            icon_label.pack(side="left", padx=(0, 10))
        except tk.TclError:
            pass  # 图标加载失败，忽略
    
    # 显示标题
    title_label = ttk.Label(title_frame, text=title, style="Title.TLabel")
    title_label.pack(side="left")
    
    return title_frame


def create_status_indicator(parent, status="unknown", text="未知"):
    """
    创建状态指示器
    
    Args:
        parent (tk.Widget): 父窗口
        status (str, optional): 状态，可选值有'running', 'stopped', 'starting', 'unknown'
        text (str, optional): 状态文本
        
    Returns:
        ttk.Label: 状态指示器标签
    """
    # 根据状态选择样式
    if status.lower() == "running":
        style = "Running.TLabel"
    elif status.lower() == "stopped":
        style = "Stopped.TLabel"
    elif status.lower() == "starting":
        style = "Starting.TLabel"
    else:
        style = "Unknown.TLabel"
    
    # 创建状态标签
    status_label = ttk.Label(parent, text=text, style=style)
    
    return status_label


def create_card(parent, title, content=None, footer=None, width=None, height=None):
    """
    创建信息卡片
    
    Args:
        parent (tk.Widget): 父窗口
        title (str): 卡片标题
        content (str, optional): 卡片内容
        footer (str, optional): 卡片页脚
        width (int, optional): 卡片宽度
        height (int, optional): 卡片高度
        
    Returns:
        ttk.Frame: 卡片框架
    """
    # 创建卡片框架
    card_frame = ttk.Frame(parent, style="Card.TFrame")
    
    # 设置卡片大小
    if width and height:
        card_frame.configure(width=width, height=height)
    
    # 创建卡片标题
    title_label = ttk.Label(card_frame, text=title, style="Heading.TLabel")
    title_label.pack(fill="x", padx=10, pady=5)
    
    # 创建分隔线
    separator = ttk.Frame(card_frame, height=1, style="Separator.TFrame")
    separator.pack(fill="x", padx=5)
    
    # 如果提供了内容，创建内容标签
    if content:
        content_label = ttk.Label(card_frame, text=content, wraplength=width-20 if width else 300)
        content_label.pack(fill="both", expand=True, padx=10, pady=5)
    
    # 如果提供了页脚，创建页脚标签
    if footer:
        # 创建分隔线
        footer_separator = ttk.Frame(card_frame, height=1, style="Separator.TFrame")
        footer_separator.pack(fill="x", padx=5)
        
        footer_label = ttk.Label(card_frame, text=footer, style="Small.TLabel")
        footer_label.pack(fill="x", padx=10, pady=5)
    
    return card_frame


def create_button(parent, text, command=None, style="TButton", width=None):
    """
    创建按钮
    
    Args:
        parent (tk.Widget): 父窗口
        text (str): 按钮文本
        command (callable, optional): 按钮点击事件处理函数
        style (str, optional): 按钮样式
        width (int, optional): 按钮宽度
        
    Returns:
        ttk.Button: 按钮
    """
    # 创建按钮
    button = ttk.Button(parent, text=text, command=command, style=style)
    
    # 设置按钮宽度
    if width:
        button.configure(width=width)
    
    return button


def create_info_dialog(title, message, detail=None, icon="info"):
    """
    创建信息对话框
    
    Args:
        title (str): 对话框标题
        message (str): 对话框消息
        detail (str, optional): 详细信息
        icon (str, optional): 对话框图标，可选值有'info', 'warning', 'error', 'question'
    """
    # 根据图标类型选择对话框类型
    if icon.lower() == "info":
        messagebox.showinfo(title, message, detail=detail)
    elif icon.lower() == "warning":
        messagebox.showwarning(title, message, detail=detail)
    elif icon.lower() == "error":
        messagebox.showerror(title, message, detail=detail)
    elif icon.lower() == "question":
        return messagebox.askquestion(title, message, detail=detail)
    else:
        messagebox.showinfo(title, message, detail=detail)


def create_confirm_dialog(title, message, detail=None):
    """
    创建确认对话框
    
    Args:
        title (str): 对话框标题
        message (str): 对话框消息
        detail (str, optional): 详细信息
        
    Returns:
        bool: 用户是否确认
    """
    return messagebox.askyesno(title, message, detail=detail)


def create_file_dialog(title, filetypes=None, initialdir=None, mode="open"):
    """
    创建文件对话框
    
    Args:
        title (str): 对话框标题
        filetypes (list, optional): 文件类型列表
        initialdir (str, optional): 初始目录
        mode (str, optional): 对话框模式，可选值有'open', 'save', 'directory'
        
    Returns:
        str: 选择的文件或目录路径
    """
    # 如果没有提供文件类型，使用默认值
    if filetypes is None:
        filetypes = [("所有文件", "*.*")]
    
    # 如果没有提供初始目录，使用当前目录
    if initialdir is None:
        initialdir = os.getcwd()
    
    # 根据模式选择对话框类型
    if mode.lower() == "open":
        return filedialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir)
    elif mode.lower() == "save":
        return filedialog.asksaveasfilename(title=title, filetypes=filetypes, initialdir=initialdir)
    elif mode.lower() == "directory":
        return filedialog.askdirectory(title=title, initialdir=initialdir)
    else:
        return filedialog.askopenfilename(title=title, filetypes=filetypes, initialdir=initialdir)


def create_progress_bar(parent, mode="determinate", length=None):
    """
    创建进度条
    
    Args:
        parent (tk.Widget): 父窗口
        mode (str, optional): 进度条模式，可选值有'determinate', 'indeterminate'
        length (int, optional): 进度条长度
        
    Returns:
        ttk.Progressbar: 进度条
    """
    # 创建进度条
    progress_bar = ttk.Progressbar(parent, mode=mode)
    
    # 设置进度条长度
    if length:
        progress_bar.configure(length=length)
    
    return progress_bar


def create_resource_monitor(parent):
    """
    创建资源监视器
    
    Args:
        parent (tk.Widget): 父窗口
        
    Returns:
        dict: 资源监视器组件字典
    """
    # 创建资源监视器框架
    monitor_frame = ttk.Frame(parent)
    
    # 创建CPU使用率标签和进度条
    cpu_label = ttk.Label(monitor_frame, text="CPU使用率:")
    cpu_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
    
    cpu_progress = ttk.Progressbar(monitor_frame, length=150)
    cpu_progress.grid(row=0, column=1, sticky="w", padx=5, pady=2)
    
    cpu_value = ttk.Label(monitor_frame, text="0%")
    cpu_value.grid(row=0, column=2, sticky="w", padx=5, pady=2)
    
    # 创建内存使用率标签和进度条
    memory_label = ttk.Label(monitor_frame, text="内存使用率:")
    memory_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
    
    memory_progress = ttk.Progressbar(monitor_frame, length=150)
    memory_progress.grid(row=1, column=1, sticky="w", padx=5, pady=2)
    
    memory_value = ttk.Label(monitor_frame, text="0%")
    memory_value.grid(row=1, column=2, sticky="w", padx=5, pady=2)
    
    # 创建磁盘使用率标签和进度条
    disk_label = ttk.Label(monitor_frame, text="磁盘使用率:")
    disk_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
    
    disk_progress = ttk.Progressbar(monitor_frame, length=150)
    disk_progress.grid(row=2, column=1, sticky="w", padx=5, pady=2)
    
    disk_value = ttk.Label(monitor_frame, text="0%")
    disk_value.grid(row=2, column=2, sticky="w", padx=5, pady=2)
    
    # 返回资源监视器组件字典
    return {
        "frame": monitor_frame,
        "cpu": {
            "progress": cpu_progress,
            "value": cpu_value
        },
        "memory": {
            "progress": memory_progress,
            "value": memory_value
        },
        "disk": {
            "progress": disk_progress,
            "value": disk_value
        }
    }


def update_resource_monitor(monitor, resources):
    """
    更新资源监视器
    
    Args:
        monitor (dict): 资源监视器组件字典
        resources (dict): 资源使用情况字典，包括cpu_percent, memory_percent, disk_percent
    """
    # 更新CPU使用率
    cpu_percent = resources.get("cpu_percent", 0)
    monitor["cpu"]["progress"]["value"] = cpu_percent
    monitor["cpu"]["value"].configure(text=f"{cpu_percent:.1f}%")
    
    # 更新内存使用率
    memory_percent = resources.get("memory_percent", 0)
    monitor["memory"]["progress"]["value"] = memory_percent
    monitor["memory"]["value"].configure(text=f"{memory_percent:.1f}%")
    
    # 更新磁盘使用率
    disk_percent = resources.get("disk_percent", 0)
    monitor["disk"]["progress"]["value"] = disk_percent
    monitor["disk"]["value"].configure(text=f"{disk_percent:.1f}%")


if __name__ == "__main__":
    # 测试UI组件
    root = tk.Tk()
    root.title("UI组件测试")
    root.geometry("800x600")
    
    # 设置主题
    style = setup_theme(root)
    
    # 创建标题栏
    create_title_bar(root, "UI组件测试")
    
    # 创建主框架
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # 创建卡片
    card1 = create_card(
        main_frame,
        "信息卡片",
        "这是一个信息卡片示例，用于展示信息。\n可以包含多行文本内容。",
        "页脚信息",
        width=300,
        height=150
    )
    card1.pack(side="left", padx=10, pady=10)
    
    # 创建按钮
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(side="left", padx=10, pady=10)
    
    primary_button = create_button(
        button_frame,
        "主要按钮",
        lambda: create_info_dialog("信息", "这是一个信息对话框"),
        style="Primary.TButton",
        width=15
    )
    primary_button.pack(pady=5)
    
    success_button = create_button(
        button_frame,
        "成功按钮",
        lambda: create_info_dialog("成功", "操作成功完成", icon="info"),
        style="Success.TButton",
        width=15
    )
    success_button.pack(pady=5)
    
    danger_button = create_button(
        button_frame,
        "危险按钮",
        lambda: create_info_dialog("错误", "发生错误", icon="error"),
        style="Danger.TButton",
        width=15
    )
    danger_button.pack(pady=5)
    
    warning_button = create_button(
        button_frame,
        "警告按钮",
        lambda: create_info_dialog("警告", "这是一个警告", icon="warning"),
        style="Warning.TButton",
        width=15
    )
    warning_button.pack(pady=5)
    
    # 创建状态指示器
    status_frame = ttk.Frame(main_frame)
    status_frame.pack(side="left", padx=10, pady=10)
    
    running_status = create_status_indicator(status_frame, "running", "运行中")
    running_status.pack(pady=5)
    
    stopped_status = create_status_indicator(status_frame, "stopped", "已停止")
    stopped_status.pack(pady=5)
    
    starting_status = create_status_indicator(status_frame, "starting", "启动中")
    starting_status.pack(pady=5)
    
    unknown_status = create_status_indicator(status_frame, "unknown", "未知")
    unknown_status.pack(pady=5)
    
    # 创建资源监视器
    monitor = create_resource_monitor(root)
    monitor["frame"].pack(fill="x", padx=10, pady=10)
    
    # 更新资源监视器
    update_resource_monitor(monitor, {
        "cpu_percent": 25.5,
        "memory_percent": 50.0,
        "disk_percent": 75.5
    })
    
    # 启动主循环
    root.mainloop()