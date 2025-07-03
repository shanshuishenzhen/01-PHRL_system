#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局总控模块 - 主入口文件
负责系统的统一调度、权限分发、模块间通信和全局配置管理

更新日志：
- 2024-07-01: 增加日志记录功能
- 2024-07-01: 增强错误处理
- 2024-07-01: 添加模块状态监控
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
import subprocess
import webbrowser
import time
import threading
import logging
import platform
import json
import socket
import psutil
import csv
from datetime import datetime

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'main_console.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class MainConsole:
    def __init__(self):
        """初始化主控台窗口"""
        logging.info("初始化主控台")
        self.root = tk.Tk()
        self.root.title("PH&RL 在线考试系统 - 主控台")
        
        # 设置窗口大小和位置 - 调整为更大的默认尺寸
        self.root.geometry("960x720")
        self.root.resizable(True, True)
        
        # 设置窗口图标（如果有的话）
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logging.warning(f"加载图标失败: {e}")
        
        # 加载配置
        self.config = self.load_config()
        
        # 模块状态跟踪
        self.module_status = {
            "question_bank": {"status": "未启动", "process": None, "port": 5000, "pid": None, "start_time": None},
            "user_management": {"status": "未启动", "process": None, "pid": None, "start_time": None},
            "score_statistics": {"status": "未启动", "process": None, "pid": None, "start_time": None},
            "grading_center": {"status": "未启动", "process": None, "port": 3000, "pid": None, "start_time": None},
            "client": {"status": "未启动", "process": None, "pid": None, "start_time": None},
            "exam_management": {"status": "未启动", "process": None, "pid": None, "start_time": None},
            "conversation": {"status": "未启动", "process": None, "pid": None, "start_time": None},
            "developer_tools": {"status": "未启动", "process": None, "pid": None, "start_time": None}
        }
        
        # 系统资源监控数据
        self.system_resources = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0
        }
        
        # 创建并放置控件
        self.create_widgets()
        
        # 启动状态更新线程
        self.start_status_update()

    def create_widgets(self):
        """创建主界面控件"""
        # 主容器
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题区域
        self.create_header(main_container)
        
        # 主要内容区域
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # 左侧：模块按钮区域
        self.create_module_buttons(content_frame)
        
        # 右侧：状态信息区域
        self.create_status_panel(content_frame)
        
        # 底部：系统信息区域
        self.create_footer(main_container)

    def create_header(self, parent):
        """创建顶部标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 系统标题
        title_label = ttk.Label(
            header_frame, 
            text="PH&RL 在线考试系统", 
            font=("Microsoft YaHei", 24, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack(side=tk.LEFT)
        
        # 版本信息
        version_label = ttk.Label(
            header_frame, 
            text="v1.0.0", 
            font=("Microsoft YaHei", 10),
            foreground="#7f8c8d"
        )
        version_label.pack(side=tk.RIGHT, pady=(10, 0))
        
        # 当前时间
        self.time_label = ttk.Label(
            header_frame, 
            text="", 
            font=("Microsoft YaHei", 10),
            foreground="#7f8c8d"
        )
        self.time_label.pack(side=tk.RIGHT, padx=(0, 20), pady=(10, 0))

    def create_module_buttons(self, parent):
        """创建模块按钮区域"""
        # 左侧容器
        left_frame = ttk.Frame(parent)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 模块按钮标题
        ttk.Label(
            left_frame, 
            text="功能模块", 
            font=("Microsoft YaHei", 14, "bold"),
            foreground="#34495e"
        ).pack(pady=(0, 15))
        
        # 按钮网格容器
        button_grid = ttk.Frame(left_frame)
        button_grid.pack(fill=tk.BOTH, expand=True)
        
        # 配置按钮样式
        button_style = {
            "font": ("Microsoft YaHei", 11),
            "relief": "flat",
            "borderwidth": 0,
            "padx": 20,
            "pady": 15,
            "cursor": "hand2"
        }
        
        # 模块按钮配置
        modules = [
            { "name": "题库管理", "key": "question_bank", "command": self.start_question_bank, "description": "题目和题库管理", "icon": "📚", "color": "#3498db" },
            { "name": "用户管理", "key": "user_management", "command": self.start_user_management, "description": "用户账户和权限管理", "icon": "👥", "color": "#e74c3c" },
            { "name": "成绩统计", "key": "score_statistics", "command": self.start_score_statistics, "description": "成绩分析和统计", "icon": "📊", "color": "#f39c12" },
            { "name": "阅卷中心", "key": "grading_center", "command": self.start_grading_center, "description": "在线阅卷和评分", "icon": "📝", "color": "#9b59b6" },
            { "name": "客户机端", "key": "client", "command": self.start_client, "description": "考试答题界面", "icon": "💻", "color": "#27ae60" },
            { "name": "考试管理", "key": "exam_management", "command": self.start_exam_management, "description": "考试管理和配置", "icon": "📅", "color": "#2ecc71" },
            { "name": "对话记录", "key": "conversation", "command": self.start_conversation_manager, "description": "对话上下文记录管理", "icon": "💬", "color": "#1abc9c" },
            { "name": "开发工具", "key": "developer_tools", "command": self.start_developer_tools, "description": "生成测试数据和工具", "icon": "🛠️", "color": "#7f8c8d" }
        ]
        
        # 创建按钮网格 (调整布局以适应7个按钮)
        for i, module in enumerate(modules):
            row = i // 2
            col = i % 2
            
            button_container = ttk.Frame(button_grid, relief="solid", borderwidth=1)
            
            button_container.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
                
            button_container.configure(style="Module.TFrame")
            
            # 按钮
            btn = tk.Button(
                button_container,
                text=f"{module['icon']} {module['name']}",
                command=module["command"],
                bg=module["color"],
                fg="white",
                activebackground=module["color"],
                activeforeground="white",
                **button_style
            )
            btn.pack(fill=tk.X, padx=5, pady=5)
            
            # 描述标签
            desc_label = ttk.Label(
                button_container,
                text=module["description"],
                font=("Microsoft YaHei", 9),
                foreground="#7f8c8d",
                wraplength=150
            )
            desc_label.pack(pady=(0, 5))
            
            # 状态标签
            status_label = ttk.Label(
                button_container,
                text="未启动",
                font=("Microsoft YaHei", 8),
                foreground="#e74c3c"
            )
            status_label.pack(pady=(0, 5))
            
            # 保存状态标签引用
            self.module_status[module["key"]]["label"] = status_label

    def load_config(self):
        """加载系统配置"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            "version": "1.0.0",
            "update_interval": 5,  # 状态更新间隔（秒）
            "module_ports": {
                "question_bank": 5000,
                "grading_center": 5173,
                "exam_management": 5001
            },
            "enable_resource_monitoring": True,
            "auto_restart_crashed_modules": False
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logging.info("已加载配置文件")
                    return config
            except Exception as e:
                logging.error(f"加载配置文件失败: {e}")
                return default_config
        else:
            # 创建默认配置文件
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
                logging.info("已创建默认配置文件")
            except Exception as e:
                logging.error(f"创建配置文件失败: {e}")
            return default_config
    
    def create_status_panel(self, parent):
        """创建状态信息面板"""
        # 右侧容器
        right_frame = ttk.LabelFrame(parent, text="系统状态", padding="15")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        
        # 系统信息
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 系统状态信息
        status_info = [
            ("系统版本", f"v{self.config.get('version', '1.0.0')}"),
            ("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ("运行平台", f"{platform.system()} {platform.release()}"),
            ("当前用户", os.getenv("USERNAME", "未知")),
            ("工作目录", os.getcwd())
        ]
        
        for label, value in status_info:
            row_frame = ttk.Frame(info_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(row_frame, text=f"{label}:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
            ttk.Label(row_frame, text=value, font=("Microsoft YaHei", 9)).pack(side=tk.RIGHT)
            
        # 系统资源使用情况
        if self.config.get('enable_resource_monitoring', True):
            resource_frame = ttk.LabelFrame(right_frame, text="系统资源", padding="5")
            resource_frame.pack(fill=tk.X, pady=5)
            
            # CPU使用率
            self.cpu_label = ttk.Label(
                resource_frame, 
                text="CPU使用率: 获取中...",
                font=("Arial", 10)
            )
            self.cpu_label.pack(anchor=tk.W, pady=2)
            
            # 内存使用率
            self.memory_label = ttk.Label(
                resource_frame, 
                text="内存使用率: 获取中...",
                font=("Arial", 10)
            )
            self.memory_label.pack(anchor=tk.W, pady=2)
            
            # 磁盘使用率
            self.disk_label = ttk.Label(
                resource_frame, 
                text="磁盘使用率: 获取中...",
                font=("Arial", 10)
            )
            self.disk_label.pack(anchor=tk.W, pady=2)
        
        # 分隔线
        ttk.Separator(right_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # 快速操作
        ttk.Label(right_frame, text="快速操作", font=("Microsoft YaHei", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        quick_buttons = [
            ("📖 查看文档", self.open_documentation),
            ("⚙️ 系统设置", self.open_settings),
            ("❓ 帮助信息", self.show_help),
            ("ℹ️ 关于系统", self.show_about)
        ]
        
        for text, command in quick_buttons:
            btn = ttk.Button(right_frame, text=text, command=command, width=20)
            btn.pack(fill=tk.X, pady=2)

    def create_footer(self, parent):
        """创建底部信息区域"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        # 分隔线
        ttk.Separator(footer_frame, orient="horizontal").pack(fill=tk.X, pady=(0, 10))
        
        # 版权信息
        copyright_label = ttk.Label(
            footer_frame,
            text="© 2024 PH&RL 在线考试系统 - 让考试管理更简单、更高效！",
            font=("Microsoft YaHei", 9),
            foreground="#7f8c8d"
        )
        copyright_label.pack(side=tk.LEFT)
        
        # 技术支持
        support_label = ttk.Label(
            footer_frame,
            text="技术支持: support@phrl-exam.com",
            font=("Microsoft YaHei", 9),
            foreground="#3498db",
            cursor="hand2"
        )
        support_label.pack(side=tk.RIGHT)
        support_label.bind("<Button-1>", lambda e: webbrowser.open("mailto:support@phrl-exam.com"))

    def start_status_update(self):
        """启动状态更新线程"""
        def update_loop():
            while True:
                try:
                    # 更新时间
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.time_label.config(text=current_time)
                    
                    # 更新模块状态
                    self.update_module_status()
                    
                    # 更新系统资源使用情况
                    if self.config.get('enable_resource_monitoring', True):
                        self.update_system_resources()
                    
                    # 检查是否需要自动重启崩溃的模块
                    if self.config.get('auto_restart_crashed_modules', False):
                        self.check_crashed_modules()
                        
                except Exception as e:
                    logging.error(f"状态更新线程出错: {e}")
                
                time.sleep(self.config.get('update_interval', 5))  # 根据配置更新间隔
        
        threading.Thread(target=update_loop, daemon=True).start()
        logging.info("状态更新线程已启动")

    def update_system_resources(self):
        """更新系统资源使用情况"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.system_resources['cpu_usage'] = cpu_percent
            self.cpu_label.config(text=f"CPU使用率: {cpu_percent:.1f}%")
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.system_resources['memory_usage'] = memory_percent
            self.memory_label.config(text=f"内存使用率: {memory_percent:.1f}% ({memory.used // (1024*1024)} MB / {memory.total // (1024*1024)} MB)")
            
            # 磁盘使用率
            disk = psutil.disk_usage(os.getcwd())
            disk_percent = disk.percent
            self.system_resources['disk_usage'] = disk_percent
            self.disk_label.config(text=f"磁盘使用率: {disk_percent:.1f}% ({disk.used // (1024*1024*1024):.1f} GB / {disk.total // (1024*1024*1024):.1f} GB)")
        except Exception as e:
            logging.error(f"更新系统资源信息失败: {e}")
    
    def check_crashed_modules(self):
        """检查并重启崩溃的模块"""
        for module_name, module_info in self.module_status.items():
            if module_info['status'] == "运行中" and module_info['process'] is not None:
                # 检查进程是否仍在运行
                if module_info['process'].poll() is not None:  # 进程已结束
                    logging.warning(f"模块 {module_name} 已崩溃，尝试重启")
                    messagebox.showwarning("模块崩溃", f"模块 {module_name} 已崩溃，正在尝试重启...")
                    
                    # 根据模块名称调用相应的启动方法
                    start_method = getattr(self, f"start_{module_name}", None)
                    if start_method:
                        start_method(auto_restart=True)
    
    def update_module_status(self):
        """更新模块状态显示"""
        for module_key, status_info in self.module_status.items():
            if "label" in status_info:
                label = status_info["label"]
                status = status_info["status"]
                
                # 检查进程状态
                if status == "运行中" and status_info['process'] is not None:
                    # 检查进程是否仍在运行
                    if status_info['process'].poll() is None:  # 进程仍在运行
                        # 检查端口是否可用（如果模块有端口）
                        if 'port' in status_info and status_info['port'] is not None:
                            port_available = self.check_port_available(status_info['port'])
                            if port_available:
                                label.config(text="● 运行中 (端口可用)", foreground="#27ae60")
                            else:
                                label.config(text="● 运行中 (端口占用)", foreground="#f39c12")
                        else:
                            label.config(text="● 运行中", foreground="#27ae60")
                    else:  # 进程已结束
                        status_info['status'] = "未启动"
                        label.config(text="● 已停止", foreground="#e74c3c")
                        logging.warning(f"模块 {module_key} 已停止运行")
                elif status == "启动中":
                    label.config(text="● 启动中", foreground="#f39c12")
                else:
                    label.config(text="● 未启动", foreground="#e74c3c")

    def check_module_files(self, module_name, required_files):
        """检查模块所需文件是否存在
        
        Args:
            module_name (str): 模块名称
            required_files (list): 所需文件路径列表，相对于项目根目录
            
        Returns:
            bool: 所有文件都存在返回True，否则返回False
        """
        missing_files = []
        for file_path in required_files:
            abs_path = os.path.join(os.path.dirname(__file__), file_path)
            if not os.path.exists(abs_path):
                missing_files.append(file_path)
        
        if missing_files:
            error_msg = f"{module_name}模块所需文件未找到：\n" + "\n".join(missing_files)
            messagebox.showerror("错误", error_msg)
            self.module_status[module_name]["status"] = "启动失败"
            logging.error(error_msg)
            return False
        
        return True
        
    def check_port_available(self, port):
        """检查端口是否可用"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0  # 0表示连接成功，端口被占用
        except Exception as e:
            logging.error(f"检查端口 {port} 时出错: {e}")
            return False
    
    def start_question_bank(self, auto_restart=False):
        """启动题库管理模块"""
        if self.module_status["question_bank"]["status"] == "运行中" and not auto_restart:
            messagebox.showinfo("提示", "题库管理模块已在运行中")
            return
            
        try:
            # 检查文件路径
            flask_app_path = os.path.join(os.path.dirname(__file__), 'question_bank_web', 'app.py')
            if not os.path.exists(flask_app_path):
                messagebox.showerror("错误", "题库管理应用 'question_bank_web/app.py' 未找到！")
                self.module_status["question_bank"]["status"] = "启动失败"
                return

            # 更新状态
            self.module_status["question_bank"]["status"] = "启动中"
            self.update_module_status()
            logging.info("开始启动题库管理模块")
            
            # 启动Flask应用
            def start_flask():
                try:
                    # 使用更可靠的启动方式
                    command = f'start cmd /k "cd /d {os.path.join(os.getcwd(), "question_bank_web")} && {sys.executable} -m flask run"'
                    process = subprocess.Popen(command, shell=True)
                    
                    self.module_status["question_bank"]["process"] = process
                    self.module_status["question_bank"]["status"] = "运行中"
                    self.module_status["question_bank"]["start_time"] = datetime.now()
                    self.update_module_status()
                    logging.info("题库管理模块已启动")
                    
                    # 等待服务启动
                    time.sleep(3)
                    
                    # 检查端口是否可用
                    port = self.module_status["question_bank"]["port"]
                    port_available = self.check_port_available(port)
                    
                    if port_available:
                        # 打开浏览器
                        webbrowser.open(f"http://127.0.0.1:{port}")
                        logging.info(f"已打开题库管理Web界面: http://127.0.0.1:{port}")
                    else:
                        logging.warning(f"端口 {port} 不可用，无法打开Web界面")
                        if not auto_restart:
                            messagebox.showwarning("端口问题", f"端口 {port} 不可用，请手动访问题库管理Web界面")
                except Exception as e:
                    error_msg = f"启动题库管理模块时发生错误：{e}"
                    logging.error(error_msg)
                    self.module_status["question_bank"]["status"] = "未启动"
                    self.update_module_status()
                    if not auto_restart:
                        messagebox.showerror("启动失败", error_msg)
            
            threading.Thread(target=start_flask, daemon=True).start()
            if not auto_restart:
                messagebox.showinfo("启动中", "题库管理模块正在启动，请稍候...")

        except Exception as e:
            error_msg = f"启动题库管理失败: {e}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)
            self.module_status["question_bank"]["status"] = "启动失败"

    def start_user_management(self):
        """启动用户管理模块"""
        try:
            # 启动用户管理模块
            process = subprocess.Popen([sys.executable, os.path.join("user_management", "simple_user_manager.py")])
            
            # 更新模块状态
            self.module_status["user_management"]["process"] = process
            self.module_status["user_management"]["status"] = "运行中"
            self.module_status["user_management"]["start_time"] = datetime.now()
            self.update_module_status()
        except Exception as e:
            messagebox.showerror("错误", f"启动用户管理模块失败: {e}")

    def start_score_statistics(self):
        """启动成绩统计模块"""
        try:
            # 启动成绩统计模块
            process = subprocess.Popen([sys.executable, os.path.join("score_statistics", "simple_score_manager.py")])
            
            # 更新模块状态
            self.module_status["score_statistics"]["process"] = process
            self.module_status["score_statistics"]["status"] = "运行中"
            self.module_status["score_statistics"]["start_time"] = datetime.now()
            self.update_module_status()
        except Exception as e:
            messagebox.showerror("错误", f"启动成绩统计模块失败: {e}")

    def start_grading_center(self, auto_restart=False):
        """启动阅卷中心模块"""
        if self.module_status["grading_center"]["status"] == "运行中" and not auto_restart:
            messagebox.showinfo("提示", "阅卷中心模块已在运行中")
            return
            
        try:
            # 检查必要文件
            required_files = [
                os.path.join('grading_center', 'server', 'app.js'),
                os.path.join('grading_center', 'client', 'package.json')
            ]
            
            if not self.check_module_files("grading_center", required_files):
                return

            self.module_status["grading_center"]["status"] = "启动中"
            self.update_module_status()
            logging.info("开始启动阅卷中心模块")
            
            def start_grading_center():
                try:
                    # 启动Node.js后端
                    backend_dir = os.path.join(os.path.dirname(__file__), 'grading_center', 'server')
                    backend_app_path = os.path.join(backend_dir, 'app.js')
                    logging.info(f"启动阅卷中心后端，路径: {backend_app_path}")
                    # 使用shell=True确保在Windows环境下正确执行node命令
                    backend_process = subprocess.Popen(
                        f'node "{backend_app_path}"',
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    logging.info("阅卷中心后端服务已启动")
                    
                    # 启动Vue前端
                    frontend_dir = os.path.join(os.path.dirname(__file__), 'grading_center', 'client')
                    logging.info(f"启动阅卷中心前端，路径: {frontend_dir}")
                    # 使用PowerShell启动npm命令，并添加--host参数以允许外部访问
                    frontend_process = subprocess.Popen(
                        ['powershell', '-Command', f'cd "{frontend_dir}"; npm run dev -- --host'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    logging.info("阅卷中心前端服务已启动")
                    
                    # 保存进程引用
                    self.module_status["grading_center"]["process"] = frontend_process
                    self.module_status["grading_center"]["backend_process"] = backend_process
                    self.module_status["grading_center"]["status"] = "运行中"
                    self.module_status["grading_center"]["start_time"] = datetime.now()
                    self.update_module_status()
                    
                    # 等待服务启动
                    time.sleep(5)
                    
                    # 检查后端端口是否可用
                    backend_port = self.module_status["grading_center"]["port"]
                    backend_available = self.check_port_available(backend_port)
                    
                    # 检查前端端口是否可用
                    frontend_port = self.config.get("module_ports", {}).get("grading_center_frontend", 5173)
                    frontend_available = self.check_port_available(frontend_port)
                    
                    if backend_available and frontend_available:
                        # 打开浏览器访问前端
                        webbrowser.open(f"http://localhost:{frontend_port}")
                        logging.info(f"已打开阅卷中心Web界面: http://localhost:{frontend_port}")
                    else:
                        if not backend_available:
                            logging.warning(f"后端端口 {backend_port} 不可用，无法打开Web界面")
                        if not frontend_available:
                            logging.warning(f"前端端口 {frontend_port} 不可用，无法打开Web界面")
                        if not auto_restart:
                            messagebox.showwarning("端口问题", f"阅卷中心服务端口不可用，请手动访问阅卷中心Web界面: http://localhost:{frontend_port}")
                except Exception as e:
                    error_msg = f"启动阅卷中心模块时发生错误：{e}"
                    logging.error(error_msg)
                    self.module_status["grading_center"]["status"] = "未启动"
                    self.update_module_status()
                    if not auto_restart:
                        messagebox.showerror("启动失败", error_msg)
            
            threading.Thread(target=start_grading_center, daemon=True).start()
            if not auto_restart:
                frontend_port = self.config.get("module_ports", {}).get("grading_center_frontend", 5173)
                messagebox.showinfo("启动中", f"阅卷中心模块正在启动，请稍候...\n\n如果浏览器未自动打开，请手动访问:\nhttp://localhost:{frontend_port}")

        except Exception as e:
            error_msg = f"启动阅卷中心失败: {e}"
            logging.error(error_msg)
            messagebox.showerror("错误", error_msg)
            self.module_status["grading_center"]["status"] = "启动失败"

    def start_client(self):
        """启动客户机端模块"""
        try:
            # 启动客户机端模块
            process = subprocess.Popen([sys.executable, os.path.join("client", "client_app.py")])
            
            # 更新模块状态
            self.module_status["client"]["process"] = process
            self.module_status["client"]["status"] = "运行中"
            self.module_status["client"]["start_time"] = datetime.now()
            self.update_module_status()
        except Exception as e:
            messagebox.showerror("错误", f"启动客户机端模块失败: {e}")

    def start_exam_management(self):
        """启动考试管理模块"""
        # 启动考试管理模块
        self.module_status["exam_management"]["process"] = subprocess.Popen(
            [sys.executable, "-m", "exam_management.simple_exam_manager"]
        )
        
        # 更新模块状态
        self.module_status["exam_management"]["status"] = "运行中"
        self.module_status["exam_management"]["start_time"] = datetime.now()
        self.update_module_status()
        
    def show_all_exams(self):
        """显示所有考试"""
        try:
            # 检查是否已经有考试列表窗口打开
            for window in self.root.winfo_children():
                if isinstance(window, tk.Toplevel) and getattr(window, 'is_exams_window', False):
                    window.focus_set()  # 如果已经打开，则将焦点设置到该窗口
                    return
                    
            # 加载考试数据
            exams_path = os.path.join('exam_management', 'exams.json')
            if not os.path.exists(exams_path):
                messagebox.showinfo("提示", "考试数据文件不存在，请先创建考试")
                return
                
            with open(exams_path, 'r', encoding='utf-8') as f:
                exams_data = json.load(f)
                
            exams = exams_data.get("exams", [])
            if not exams:
                messagebox.showinfo("提示", "暂无考试数据")
                return
                
            # 创建考试列表窗口
            exams_window = tk.Toplevel(self.root)
            exams_window.title("所有考试列表 - PH&RL 在线考试系统")
            exams_window.geometry("1200x600")
            exams_window.transient(self.root)
            setattr(exams_window, 'is_exams_window', True)  # 标记这是考试列表窗口
            
            # 创建标题
            header_frame = ttk.Frame(exams_window, padding="10")
            header_frame.pack(fill=tk.X)
            
            ttk.Label(
                header_frame, 
                text="所有考试列表", 
                font=("Microsoft YaHei", 16, "bold")
            ).pack(side=tk.LEFT)
            
            # 添加搜索框
            search_frame = ttk.Frame(header_frame)
            search_frame.pack(side=tk.RIGHT, padx=20)
            
            ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
            search_var = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=search_var, width=20)
            search_entry.pack(side=tk.LEFT)
            
            search_button = ttk.Button(
                search_frame,
                text="搜索",
                command=lambda: self.search_exams(tree, search_var.get(), exams_path, exam_statuses, exam_types, status_label)
            )
            search_button.pack(side=tk.LEFT, padx=5)
            
            # 添加清除搜索按钮
            clear_button = ttk.Button(
                search_frame,
                text="清除",
                command=lambda: [search_var.set(""), self.refresh_exams_list(tree, exams_path, exam_statuses, exam_types, auto_refresh_var, exams_window, status_label)]
            )
            clear_button.pack(side=tk.LEFT, padx=5)
            
            # 绑定回车键触发搜索
            search_entry.bind("<Return>", lambda event: self.search_exams(tree, search_var.get(), exams_path, exam_statuses, exam_types, status_label))
            
            # 添加自动刷新选项
            auto_refresh_var = tk.BooleanVar(value=True)
            auto_refresh_check = ttk.Checkbutton(
                header_frame,
                text="自动刷新",
                variable=auto_refresh_var
            )
            auto_refresh_check.pack(side=tk.RIGHT)
            
            # 添加状态栏，显示最后刷新时间
            status_frame = ttk.Frame(exams_window, padding="5")
            status_frame.pack(fill=tk.X, side=tk.BOTTOM)
            
            status_label = ttk.Label(status_frame, text="准备加载考试数据...")
            status_label.pack(side=tk.LEFT)
            
            # 创建考试列表
            list_frame = ttk.Frame(exams_window, padding="10")
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建表格
            columns = ("id", "name", "type", "status", "start_time", "end_time", "participants", "created_at")
            tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
            
            # 设置列标题并添加排序功能
            for col in columns:
                tree.heading(col, text={
                    "id": "ID",
                    "name": "考试名称",
                    "type": "类型",
                    "status": "状态",
                    "start_time": "开始时间",
                    "end_time": "结束时间",
                    "participants": "参与人数",
                    "created_at": "创建时间"
                }[col], command=lambda _col=col: self.treeview_sort_column(tree, _col, False))
            
            # 设置列宽
            tree.column("id", width=50)
            tree.column("name", width=250)
            tree.column("type", width=100)
            tree.column("status", width=100)
            tree.column("start_time", width=150)
            tree.column("end_time", width=150)
            tree.column("participants", width=100)
            tree.column("created_at", width=150)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)
            
            # 绑定双击事件
            tree.bind("<Double-1>", lambda event: self.show_exam_details(tree, exams_path))
            
            # 创建右键菜单
            context_menu = tk.Menu(tree, tearoff=0)
            context_menu.add_command(label="查看详情", command=lambda: self.show_exam_details(tree, exams_path))
            context_menu.add_command(label="导出选中项", command=lambda: self.export_selected_exam(tree))
            context_menu.add_separator()
            context_menu.add_command(label="刷新列表", command=lambda: self.refresh_exams_list(tree, exams_path, exam_statuses, exam_types, auto_refresh_var, exams_window, status_label))
            context_menu.add_command(label="打开考试管理", command=lambda: [exams_window.destroy(), self.start_exam_management()])
            context_menu.add_command(label="打开考试文件夹", command=lambda: self.open_exam_folder())
            
            # 绑定右键点击事件
            tree.bind("<Button-3>", lambda event: self.show_context_menu(event, context_menu, tree))
            
            # 考试状态和类型映射
            exam_statuses = {
                'draft': '草稿',
                'published': '已发布',
                'ongoing': '进行中',
                'completed': '已完成',
                'archived': '已归档'
            }
            
            exam_types = {
                'practice': '练习考试',
                'formal': '正式考试',
                'mock': '模拟考试',
                'quiz': '小测验'
            }
            
            # 填充数据
            for exam in exams:
                tree.insert("", tk.END, values=(
                    exam.get("id"),
                    exam.get("name"),
                    exam_types.get(exam.get("type"), exam.get("type")),
                    exam_statuses.get(exam.get("status"), exam.get("status")),
                    exam.get("start_time"),
                    exam.get("end_time"),
                    f"{exam.get('current_participants', 0)}/{exam.get('max_participants', 'N/A')}",
                    exam.get("created_at")
                ))
                
            # 添加底部按钮
            button_frame = ttk.Frame(exams_window, padding="10")
            button_frame.pack(fill=tk.X)
            
            ttk.Button(
                button_frame, 
                text="关闭", 
                command=exams_window.destroy
            ).pack(side=tk.RIGHT)
            
            # 添加刷新按钮
            ttk.Button(
                button_frame, 
                text="刷新", 
                command=lambda: self.refresh_exams_list(tree, exams_path, exam_statuses, exam_types, auto_refresh_var, exams_window, status_label)
            ).pack(side=tk.RIGHT, padx=10)
            
            # 添加导出CSV按钮
            ttk.Button(
                button_frame, 
                text="导出CSV", 
                command=lambda: self.export_exams_to_csv(tree)
            ).pack(side=tk.RIGHT, padx=10)
            
            # 添加打开文件夹按钮
            ttk.Button(
                button_frame, 
                text="打开考试文件夹", 
                command=lambda: self.open_exam_folder()
            ).pack(side=tk.LEFT, padx=10)
            
            # 启动自动刷新
            if auto_refresh_var.get():
                self.refresh_exams_list(tree, exams_path, exam_statuses, exam_types, auto_refresh_var, exams_window, status_label)
            
        except Exception as e:
            messagebox.showerror("错误", f"加载考试数据失败: {e}")
    
    def search_exams(self, tree, search_text, exams_path, exam_statuses, exam_types, status_label=None):
        """搜索考试"""
        try:
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
                
            # 如果搜索文本为空，显示所有考试
            if not search_text.strip():
                self.refresh_exams_list(tree, exams_path, exam_statuses, exam_types)
                return
                
            # 加载考试数据
            with open(exams_path, 'r', encoding='utf-8') as f:
                exams_data = json.load(f)
                
            exams = exams_data.get("exams", [])
            
            # 搜索匹配的考试
            search_text = search_text.lower()
            matched_exams = []
            
            for exam in exams:
                # 检查各个字段是否匹配搜索文本
                if any(search_text in str(value).lower() for value in [
                    exam.get("id"),
                    exam.get("name", ""),
                    exam_types.get(exam.get("type"), exam.get("type", "")),
                    exam_statuses.get(exam.get("status"), exam.get("status", "")),
                    exam.get("start_time", ""),
                    exam.get("end_time", ""),
                    exam.get("created_at", "")
                ]):
                    matched_exams.append(exam)
            
            # 填充数据
            for exam in matched_exams:
                tree.insert("", tk.END, values=(
                    exam.get("id"),
                    exam.get("name"),
                    exam_types.get(exam.get("type"), exam.get("type")),
                    exam_statuses.get(exam.get("status"), exam.get("status")),
                    exam.get("start_time"),
                    exam.get("end_time"),
                    f"{exam.get('current_participants', 0)}/{exam.get('max_participants', 'N/A')}",
                    exam.get("created_at")
                ))
                
            # 更新状态栏显示搜索结果
            if status_label:
                if matched_exams:
                    status_label.config(text=f"搜索结果: 找到 {len(matched_exams)} 个匹配的考试 | 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    status_label.config(text=f"搜索结果: 未找到匹配的考试 | 搜索时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                # 如果没有状态栏，则使用消息框
                if matched_exams:
                    messagebox.showinfo("搜索结果", f"找到 {len(matched_exams)} 个匹配的考试")
                else:
                    messagebox.showinfo("搜索结果", "未找到匹配的考试")
                
        except Exception as e:
            messagebox.showerror("错误", f"搜索考试失败: {e}")

    def refresh_exams_list(self, tree, exams_path, exam_statuses, exam_types, auto_refresh_var=None, exams_window=None, status_label=None):
        """刷新考试列表"""
        try:
            # 清空现有数据
            for item in tree.get_children():
                tree.delete(item)
            # 重新加载考试数据
            with open(exams_path, 'r', encoding='utf-8') as f:
                exams_data = json.load(f)
            exams = exams_data.get("exams", [])
            # 填充数据
            for exam in exams:
                tree.insert("", tk.END, values=(
                    exam.get("id"),
                    exam.get("name"),
                    exam_types.get(exam.get("type"), exam.get("type")),
                    exam_statuses.get(exam.get("status"), exam.get("status")),
                    exam.get("start_time"),
                    exam.get("end_time"),
                    f"{exam.get('current_participants', 0)}/{exam.get('max_participants', 'N/A')}",
                    exam.get("created_at")
                ))
            # 更新状态栏
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if status_label and status_label.winfo_exists():
                status_label.config(text=f"最后刷新时间: {current_time} | 共 {len(exams)} 个考试")
            # 如果启用了自动刷新，设置定时器
            if auto_refresh_var and auto_refresh_var.get() and exams_window and exams_window.winfo_exists():
                exams_window.after(5000, lambda: self.refresh_exams_list(tree, exams_path, exam_statuses, exam_types, auto_refresh_var, exams_window, status_label))
        except Exception as e:
            messagebox.showerror("错误", f"刷新考试数据失败: {e}")

    def treeview_sort_column(self, tree, col, reverse):
        """点击列标题排序功能"""
        try:
            data = [(tree.set(item, col), item) for item in tree.get_children('')]
            if col == "participants":
                data = [(int(value.split('/')[0]), item) for value, item in data]
            elif col == "id":
                data = [(int(value), item) for value, item in data]
            data.sort(reverse=reverse)
            for idx, (_, item) in enumerate(data):
                tree.move(item, '', idx)
            tree.heading(col, command=lambda: self.treeview_sort_column(tree, col, not reverse))
        except Exception as e:
            logging.error(f"排序失败: {e}")

    def show_exam_details(self, tree, exams_path):
        messagebox.showinfo("提示", "考试详情功能开发中...")

    def export_selected_exam(self, tree):
        messagebox.showinfo("提示", "导出选中考试功能开发中...")

    def open_exam_folder(self):
        try:
            exam_folder = os.path.join(os.path.dirname(__file__), 'exam_management')
            if os.path.exists(exam_folder):
                if platform.system() == "Windows":
                    os.startfile(exam_folder)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", exam_folder])
                else:
                    subprocess.Popen(["xdg-open", exam_folder])
            else:
                messagebox.showinfo("提示", f"考试文件夹不存在: {exam_folder}")
        except Exception as e:
            messagebox.showerror("错误", f"打开考试文件夹失败: {e}")

    def export_exams_to_csv(self, tree):
        messagebox.showinfo("提示", "导出考试列表功能开发中...")

    def show_context_menu(self, event, menu, tree):
        try:
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                menu.post(event.x_root, event.y_root)
        except Exception as e:
            logging.error(f"显示右键菜单失败: {e}")

    def open_documentation(self):
        messagebox.showinfo("提示", "文档功能开发中...")

    def open_settings(self):
        messagebox.showinfo("提示", "系统设置功能开发中...")

    def show_help(self):
        messagebox.showinfo("帮助信息", "帮助信息开发中...")

    def show_about(self):
        messagebox.showinfo("关于系统", "PH&RL 在线考试系统 v1.0.0\n\n© 2024 PH&RL 在线考试系统")

    def start_conversation_manager(self):
        messagebox.showinfo("提示", "对话上下文管理功能开发中...")

    def start_developer_tools(self):
        """启动开发工具"""
        try:
            # 检查开发工具是否已经在运行
            if self.modules["developer_tools"]["status"] == "运行中":
                messagebox.showinfo("提示", "开发工具已经在运行中")
                return

            # 更新状态
            self.modules["developer_tools"]["status"] = "启动中"
            self.update_module_status()

            # 启动开发工具
            import subprocess
            import sys
            import os

            # 获取开发工具脚本路径
            developer_tools_path = os.path.join(os.path.dirname(__file__), "..", "developer_tools.py")
            if not os.path.exists(developer_tools_path):
                developer_tools_path = os.path.join(os.path.dirname(__file__), "developer_tools.py")

            if not os.path.exists(developer_tools_path):
                messagebox.showerror("错误", "找不到开发工具文件")
                self.modules["developer_tools"]["status"] = "未启动"
                self.update_module_status()
                return

            # 启动开发工具进程
            if os.name == 'nt':  # Windows
                cmd = f'start cmd /k "cd /d {os.path.dirname(developer_tools_path)} && python {os.path.basename(developer_tools_path)}"'
                process = subprocess.Popen(cmd, shell=True)
            else:  # Linux/Mac
                process = subprocess.Popen([sys.executable, developer_tools_path])

            # 更新模块状态
            self.modules["developer_tools"]["process"] = process
            self.modules["developer_tools"]["pid"] = process.pid
            self.modules["developer_tools"]["status"] = "运行中"
            self.modules["developer_tools"]["start_time"] = time.time()

            self.update_module_status()
            messagebox.showinfo("成功", "开发工具已启动")

        except Exception as e:
            logger.error(f"启动开发工具失败: {e}")
            messagebox.showerror("错误", f"启动开发工具失败: {str(e)}")
            self.modules["developer_tools"]["status"] = "未启动"
            self.update_module_status()

if __name__ == '__main__':
    app = MainConsole()
    app.root.mainloop()