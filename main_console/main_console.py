# -*- coding: utf-8 -*-
"""
主控台模块

负责管理和监控整个系统的各个模块，提供统一的界面和控制功能。

更新日志：
- 2024-06-25：初始版本，提供基本管理和监控功能
"""

import os
import sys
import time
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import webbrowser
import psutil

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 导入项目模块
from common.logger import get_logger, log_system_info
from common.system_checker import (
    check_python_version, check_disk_space, check_module_exists,
    check_package_installed, install_package, check_all_dependencies,
    get_system_resources
)
from common.config_manager import ConfigManager
from common.process_manager import (
    start_module, stop_module, restart_module, check_module_status, 
    get_module_ports, get_module_path
)
from common.ui_components import (
    setup_theme, create_title_bar, create_button, create_card, 
    create_progress_bar, create_resource_monitor, update_resource_monitor,
    create_status_indicator
)
from common.error_handler import handle_error
from common.file_manager import ensure_dir
from common.i18n_manager import get_i18n_manager, _

# 创建日志记录器
logger = get_logger("main_console", os.path.join(project_root, "logs", "main_console.log"))

# 创建配置管理器
config_manager = ConfigManager()

# 创建国际化管理器
i18n_manager = get_i18n_manager()


class MainConsoleApp:
    """
    主控台应用
    """
    def __init__(self, root):
        """
        初始化主控台应用
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title(_("main_console.title", "PHRL系统主控台"))
        self.root.geometry("1024x768")
        self.root.minsize(1024, 768)
        
        # 设置UI主题
        setup_theme(self.root)
        
        # 创建变量
        self.status_var = tk.StringVar(value=_("main_console.initializing", "正在初始化..."))
        self.module_status = {
            "question_bank": {
                "status": "stopped",
                "pid": None,
                "port": None,
                "last_check": 0
            },
            "grading_center": {
                "status": "stopped",
                "pid": None,
                "port": None,
                "last_check": 0
            },
            "exam_management": {
                "status": "stopped",
                "pid": None,
                "port": None,
                "last_check": 0
            },
            "client": {
                "status": "stopped",
                "pid": None,
                "port": None,
                "last_check": 0
            }
        }
        
        # 资源监控变量
        self.resource_vars = {
            "cpu": tk.DoubleVar(value=0),
            "memory": tk.DoubleVar(value=0),
            "disk": tk.DoubleVar(value=0)
        }
        
        # 创建UI组件
        self.create_widgets()
        
        # 启动初始化线程
        self.init_thread = threading.Thread(target=self.initialize_system)
        self.init_thread.daemon = True
        self.init_thread.start()
        
        # 启动状态更新线程
        self.status_thread = threading.Thread(target=self.update_status_loop)
        self.status_thread.daemon = True
        self.status_thread.start()
        
        # 启动资源监控线程
        self.resource_thread = threading.Thread(target=self.update_resource_loop)
        self.resource_thread.daemon = True
        self.resource_thread.start()
    
    def create_widgets(self):
        """
        创建UI组件
        """
        # 创建标题栏
        title_frame = create_title_bar(self.root, _("main_console.title", "PHRL系统主控台"))
        title_frame.pack(fill="x")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # 创建左侧面板
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 创建系统信息卡片
        system_card = create_card(left_frame, _("main_console.system_info", "系统信息"))
        system_card.pack(fill="x", pady=5)
        
        # 系统信息内容
        system_info_frame = ttk.Frame(system_card)
        system_info_frame.pack(fill="x", padx=10, pady=5)
        
        # 系统名称
        system_name_label = ttk.Label(system_info_frame, text=_("main_console.system_name", "系统名称:"))
        system_name_label.grid(row=0, column=0, sticky="w", pady=2)
        system_name_value = ttk.Label(system_info_frame, text=config_manager.get("system_info.name", "PHRL系统"))
        system_name_value.grid(row=0, column=1, sticky="w", pady=2)
        
        # 系统版本
        system_version_label = ttk.Label(system_info_frame, text=_("main_console.system_version", "系统版本:"))
        system_version_label.grid(row=1, column=0, sticky="w", pady=2)
        system_version_value = ttk.Label(system_info_frame, text=config_manager.get("system_version", "1.0.0"))
        system_version_value.grid(row=1, column=1, sticky="w", pady=2)
        
        # 组织名称
        org_name_label = ttk.Label(system_info_frame, text=_("main_console.organization", "组织名称:"))
        org_name_label.grid(row=2, column=0, sticky="w", pady=2)
        org_name_value = ttk.Label(system_info_frame, text=config_manager.get("system_info.organization", "PHRL"))
        org_name_value.grid(row=2, column=1, sticky="w", pady=2)
        
        # 创建资源监控卡片
        resource_card = create_card(left_frame, _("main_console.resource_monitor", "资源监控"))
        resource_card.pack(fill="x", pady=5)
        
        # 资源监控内容
        self.resource_frame = create_resource_monitor(
            resource_card,
            self.resource_vars["cpu"],
            self.resource_vars["memory"],
            self.resource_vars["disk"]
        )
        self.resource_frame.pack(fill="x", padx=10, pady=5)
        
        # 创建操作卡片
        actions_card = create_card(left_frame, _("main_console.actions", "操作"))
        actions_card.pack(fill="x", pady=5)
        
        # 操作按钮
        actions_frame = ttk.Frame(actions_card)
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        # 启动所有模块按钮
        self.start_all_btn = create_button(
            actions_frame, 
            _("main_console.start_all", "启动所有模块"), 
            lambda: self.start_all_modules(),
            width=20
        )
        self.start_all_btn.pack(fill="x", pady=5)
        
        # 停止所有模块按钮
        self.stop_all_btn = create_button(
            actions_frame, 
            _("main_console.stop_all", "停止所有模块"), 
            lambda: self.stop_all_modules(),
            width=20
        )
        self.stop_all_btn.pack(fill="x", pady=5)
        
        # 重启所有模块按钮
        self.restart_all_btn = create_button(
            actions_frame, 
            _("main_console.restart_all", "重启所有模块"), 
            lambda: self.restart_all_modules(),
            width=20
        )
        self.restart_all_btn.pack(fill="x", pady=5)
        
        # 检查更新按钮
        self.check_update_btn = create_button(
            actions_frame, 
            _("main_console.check_update", "检查更新"), 
            lambda: self.check_update(),
            width=20
        )
        self.check_update_btn.pack(fill="x", pady=5)
        
        # 打开文档按钮
        self.open_docs_btn = create_button(
            actions_frame, 
            _("main_console.open_docs", "打开文档"), 
            lambda: self.open_documentation(),
            width=20
        )
        self.open_docs_btn.pack(fill="x", pady=5)
        
        # 系统设置按钮
        self.settings_btn = create_button(
            actions_frame, 
            _("main_console.settings", "系统设置"), 
            lambda: self.open_settings(),
            width=20
        )
        self.settings_btn.pack(fill="x", pady=5)
        
        # 创建右侧面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 创建模块状态卡片
        modules_card = create_card(right_frame, _("main_console.module_status", "模块状态"))
        modules_card.pack(fill="both", expand=True, pady=5)
        
        # 模块状态内容
        modules_frame = ttk.Frame(modules_card)
        modules_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建模块状态表格
        self.create_module_status_table(modules_frame)
        
        # 创建日志卡片
        logs_card = create_card(right_frame, _("main_console.logs", "系统日志"))
        logs_card.pack(fill="both", expand=True, pady=5)
        
        # 日志内容
        logs_frame = ttk.Frame(logs_card)
        logs_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 日志文本框
        self.log_text = tk.Text(logs_frame, wrap="word", height=10)
        self.log_text.pack(side="left", fill="both", expand=True)
        
        # 日志滚动条
        log_scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        log_scrollbar.pack(side="right", fill="y")
        
        # 设置日志文本框只读
        self.log_text.config(state="disabled")
        
        # 创建底部状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom")
        
        # 状态标签
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side="left", padx=10, pady=5)
    
    def create_module_status_table(self, parent_frame):
        """
        创建模块状态表格
        
        Args:
            parent_frame: 父框架
        """
        # 创建表格框架
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill="both", expand=True)
        
        # 创建模块状态表格
        columns = ("module", "status", "port", "actions")
        self.modules_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        self.modules_tree.heading("module", text=_("main_console.module", "模块"))
        self.modules_tree.heading("status", text=_("main_console.status", "状态"))
        self.modules_tree.heading("port", text=_("main_console.port", "端口"))
        self.modules_tree.heading("actions", text=_("main_console.actions", "操作"))
        
        # 设置列宽
        self.modules_tree.column("module", width=150)
        self.modules_tree.column("status", width=100)
        self.modules_tree.column("port", width=100)
        self.modules_tree.column("actions", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.modules_tree.yview)
        self.modules_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.modules_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加模块到表格
        self.update_module_tree()
        
        # 绑定表格点击事件
        self.modules_tree.bind("<Double-1>", self.on_module_double_click)
        
        # 创建操作按钮框架
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.pack(fill="x", pady=5)
        
        # 创建操作按钮
        start_btn = create_button(
            buttons_frame, 
            _("main_console.start", "启动"), 
            lambda: self.start_selected_module(),
            width=10
        )
        start_btn.pack(side="left", padx=5)
        
        stop_btn = create_button(
            buttons_frame, 
            _("main_console.stop", "停止"), 
            lambda: self.stop_selected_module(),
            width=10
        )
        stop_btn.pack(side="left", padx=5)
        
        restart_btn = create_button(
            buttons_frame, 
            _("main_console.restart", "重启"), 
            lambda: self.restart_selected_module(),
            width=10
        )
        restart_btn.pack(side="left", padx=5)
        
        view_log_btn = create_button(
            buttons_frame, 
            _("main_console.view_log", "查看日志"), 
            lambda: self.view_module_log(),
            width=10
        )
        view_log_btn.pack(side="left", padx=5)
        
        open_module_btn = create_button(
            buttons_frame, 
            _("main_console.open_module", "打开模块"), 
            lambda: self.open_module_interface(),
            width=10
        )
        open_module_btn.pack(side="left", padx=5)
    
    def update_module_tree(self):
        """
        更新模块状态表格
        """
        # 清空表格
        for item in self.modules_tree.get_children():
            self.modules_tree.delete(item)
        
        # 添加模块到表格
        modules = [
            {
                "id": "question_bank",
                "name": _("main_console.question_bank", "题库管理"),
                "status": self.module_status["question_bank"]["status"],
                "port": self.module_status["question_bank"]["port"]
            },
            {
                "id": "grading_center",
                "name": _("main_console.grading_center", "阅卷中心"),
                "status": self.module_status["grading_center"]["status"],
                "port": self.module_status["grading_center"]["port"]
            },
            {
                "id": "exam_management",
                "name": _("main_console.exam_management", "考试管理"),
                "status": self.module_status["exam_management"]["status"],
                "port": self.module_status["exam_management"]["port"]
            },
            {
                "id": "client",
                "name": _("main_console.client", "客户端"),
                "status": self.module_status["client"]["status"],
                "port": self.module_status["client"]["port"]
            }
        ]
        
        for module in modules:
            # 格式化状态文本
            status_text = {
                "running": _("main_console.running", "运行中"),
                "stopped": _("main_console.stopped", "已停止"),
                "starting": _("main_console.starting", "启动中"),
                "error": _("main_console.error", "错误")
            }.get(module["status"], _("main_console.unknown", "未知"))
            
            # 格式化端口文本
            port_text = str(module["port"]) if module["port"] else "-"
            
            # 添加到表格
            self.modules_tree.insert(
                "", "end", iid=module["id"], values=(module["name"], status_text, port_text, "")
            )
    
    def on_module_double_click(self, event):
        """
        处理模块双击事件
        
        Args:
            event: 事件对象
        """
        # 获取选中的模块
        selection = self.modules_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        module_id = item
        
        # 获取模块状态
        status = self.module_status[module_id]["status"]
        
        # 根据状态执行操作
        if status == "running":
            # 停止模块
            self.stop_module(module_id)
        elif status == "stopped":
            # 启动模块
            self.start_module(module_id)
    
    def start_selected_module(self):
        """
        启动选中的模块
        """
        # 获取选中的模块
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.no_module_selected", "请选择一个模块")
            )
            return
        
        item = selection[0]
        module_id = item
        
        # 启动模块
        self.start_module(module_id)
    
    def stop_selected_module(self):
        """
        停止选中的模块
        """
        # 获取选中的模块
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.no_module_selected", "请选择一个模块")
            )
            return
        
        item = selection[0]
        module_id = item
        
        # 停止模块
        self.stop_module(module_id)
    
    def restart_selected_module(self):
        """
        重启选中的模块
        """
        # 获取选中的模块
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.no_module_selected", "请选择一个模块")
            )
            return
        
        item = selection[0]
        module_id = item
        
        # 重启模块
        self.restart_module(module_id)
    
    def view_module_log(self):
        """
        查看模块日志
        """
        # 获取选中的模块
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.no_module_selected", "请选择一个模块")
            )
            return
        
        item = selection[0]
        module_id = item
        
        # 日志文件路径
        log_file = os.path.join(project_root, "logs", f"{module_id}.log")
        
        # 检查日志文件是否存在
        if not os.path.exists(log_file):
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.no_log_file", "日志文件不存在")
            )
            return
        
        # 创建日志查看窗口
        log_window = tk.Toplevel(self.root)
        log_window.title(_("main_console.module_log", f"{module_id}模块日志"))
        log_window.geometry("800x600")
        
        # 创建日志文本框
        log_text = tk.Text(log_window, wrap="word")
        log_text.pack(side="left", fill="both", expand=True)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(log_window, orient="vertical", command=log_text.yview)
        log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # 读取日志文件
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                log_content = f.read()
                log_text.insert("1.0", log_content)
        except Exception as e:
            messagebox.showerror(
                _("main_console.error", "错误"),
                _("main_console.error_reading_log", f"读取日志文件失败: {str(e)}")
            )
        
        # 设置日志文本框只读
        log_text.config(state="disabled")
        
        # 创建刷新按钮
        refresh_btn = create_button(
            log_window, 
            _("main_console.refresh", "刷新"), 
            lambda: self.refresh_log(log_text, log_file),
            width=10
        )
        refresh_btn.pack(side="bottom", pady=5)
    
    def refresh_log(self, log_text, log_file):
        """
        刷新日志
        
        Args:
            log_text: 日志文本框
            log_file: 日志文件路径
        """
        try:
            # 清空日志文本框
            log_text.config(state="normal")
            log_text.delete("1.0", "end")
            
            # 读取日志文件
            with open(log_file, "r", encoding="utf-8") as f:
                log_content = f.read()
                log_text.insert("1.0", log_content)
            
            # 设置日志文本框只读
            log_text.config(state="disabled")
        except Exception as e:
            messagebox.showerror(
                _("main_console.error", "错误"),
                _("main_console.error_reading_log", f"读取日志文件失败: {str(e)}")
            )
    
    def open_module_interface(self):
        """
        打开模块界面
        """
        # 获取选中的模块
        selection = self.modules_tree.selection()
        if not selection:
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.no_module_selected", "请选择一个模块")
            )
            return
        
        item = selection[0]
        module_id = item
        
        # 获取模块状态
        status = self.module_status[module_id]["status"]
        port = self.module_status[module_id]["port"]
        
        # 检查模块是否运行
        if status != "running":
            messagebox.showinfo(
                _("main_console.info", "信息"),
                _("main_console.module_not_running", "模块未运行，请先启动模块")
            )
            return
        
        # 打开模块界面
        try:
            url = f"http://localhost:{port}"
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror(
                _("main_console.error", "错误"),
                _("main_console.error_opening_module", f"打开模块界面失败: {str(e)}")
            )
    
    @handle_error
    def initialize_system(self):
        """
        初始化系统
        """
        try:
            # 更新状态
            self.status_var.set(_("main_console.checking_environment", "正在检查环境..."))
            
            # 记录系统信息
            log_system_info()
            
            # 检查Python版本
            min_python_version = config_manager.get("min_python_version", "3.6.0")
            if not check_python_version(min_python_version):
                self.show_error(_("main_console.error_python_version", f"Python版本不满足要求，需要 {min_python_version} 或更高版本"))
                return
            
            # 检查磁盘空间
            required_space = config_manager.get("required_disk_space", 500)  # MB
            if not check_disk_space(required_space):
                self.show_error(_("main_console.error_disk_space", f"磁盘空间不足，需要至少 {required_space} MB"))
                return
            
            # 检查模块文件是否存在
            modules = ["question_bank", "grading_center", "exam_management", "client"]
            for module in modules:
                if not check_module_exists(module):
                    self.show_error(_("main_console.error_module_missing", f"模块文件缺失: {module}"))
                    return
            
            # 检查依赖项
            self.status_var.set(_("main_console.checking_dependencies", "正在检查依赖项..."))
            if not check_all_dependencies():
                self.show_error(_("main_console.error_dependencies", "依赖项检查失败，请查看日志获取详细信息"))
                return
            
            # 确保必要的目录存在
            ensure_dir(os.path.join(project_root, "logs"))
            ensure_dir(os.path.join(project_root, "data"))
            ensure_dir(os.path.join(project_root, "temp"))
            
            # 获取模块端口配置
            module_ports = get_module_ports()
            for module, port in module_ports.items():
                if module in self.module_status:
                    self.module_status[module]["port"] = port
            
            # 更新模块状态表格
            self.update_module_tree()
            
            # 添加初始化完成日志
            self.add_log(_("main_console.system_initialized", "系统初始化完成"))
            
            self.status_var.set(_("main_console.ready", "系统就绪"))
            
            # 记录初始化完成
            logger.info("系统初始化完成")
        except Exception as e:
            logger.error(f"系统初始化失败: {str(e)}")
            self.show_error(_("main_console.error_initialization", f"系统初始化失败: {str(e)}"))
    
    def update_status_loop(self):
        """
        更新模块状态循环
        """
        while True:
            try:
                # 更新模块状态
                for module_id in self.module_status:
                    pid = self.module_status[module_id]["pid"]
                    port = self.module_status[module_id]["port"]
                    last_check = self.module_status[module_id]["last_check"]
                    
                    # 如果上次检查时间超过5秒，则重新检查
                    if time.time() - last_check > 5:
                        if pid is not None:
                            # 检查模块状态
                            status = check_module_status(pid, port)
                            self.module_status[module_id]["status"] = status
                        
                        # 更新上次检查时间
                        self.module_status[module_id]["last_check"] = time.time()
                
                # 更新模块状态表格
                self.update_module_tree()
                
                # 检查是否需要自动重启崩溃的模块
                auto_restart = config_manager.get("auto_restart_crashed_modules", True)
                if auto_restart:
                    for module_id in self.module_status:
                        if self.module_status[module_id]["status"] == "error" and self.module_status[module_id]["pid"] is not None:
                            # 添加日志
                            self.add_log(_("main_console.module_crashed", f"模块崩溃: {module_id}，正在自动重启..."))
                            
                            # 重启模块
                            self.restart_module(module_id)
            except Exception as e:
                logger.error(f"更新模块状态失败: {str(e)}")
            
            # 等待一段时间
            time.sleep(1)
    
    def update_resource_loop(self):
        """
        更新资源监控循环
        """
        while True:
            try:
                # 获取系统资源使用情况
                resources = get_system_resources()
                
                # 更新资源监控
                self.resource_vars["cpu"].set(resources["cpu_percent"])
                self.resource_vars["memory"].set(resources["memory_percent"])
                self.resource_vars["disk"].set(resources["disk_percent"])
                
                # 更新资源监控UI
                update_resource_monitor(
                    self.resource_frame,
                    self.resource_vars["cpu"].get(),
                    self.resource_vars["memory"].get(),
                    self.resource_vars["disk"].get()
                )
            except Exception as e:
                logger.error(f"更新资源监控失败: {str(e)}")
            
            # 等待一段时间
            time.sleep(2)
    
    @handle_error
    def start_module(self, module_id):
        """
        启动模块
        
        Args:
            module_id: 模块ID
        
        Returns:
            bool: 是否成功启动
        """
        try:
            # 检查模块是否已经运行
            if self.module_status[module_id]["status"] == "running":
                self.add_log(_("main_console.module_already_running", f"模块已经在运行中: {module_id}"))
                return True
            
            # 更新状态
            self.status_var.set(_("main_console.starting_module", f"正在启动模块: {module_id}..."))
            self.module_status[module_id]["status"] = "starting"
            self.update_module_tree()
            
            # 添加日志
            self.add_log(_("main_console.starting_module", f"正在启动模块: {module_id}..."))
            
            # 启动模块
            port = self.module_status[module_id]["port"]
            pid = start_module(module_id, port)
            
            if pid is None:
                self.module_status[module_id]["status"] = "error"
                self.status_var.set(_("main_console.error_starting_module", f"启动模块失败: {module_id}"))
                self.add_log(_("main_console.error_starting_module", f"启动模块失败: {module_id}"))
                return False
            
            # 更新状态
            self.module_status[module_id]["pid"] = pid
            self.module_status[module_id]["status"] = "running"
            self.status_var.set(_("main_console.module_started", f"模块已启动: {module_id}"))
            self.add_log(_("main_console.module_started", f"模块已启动: {module_id}"))
            self.update_module_tree()
            
            return True
        except Exception as e:
            logger.error(f"启动模块失败: {module_id}, 错误: {str(e)}")
            self.module_status[module_id]["status"] = "error"
            self.status_var.set(_("main_console.error_starting_module", f"启动模块失败: {module_id}"))
            self.add_log(_("main_console.error_starting_module", f"启动模块失败: {module_id}, 错误: {str(e)}"))
            self.update_module_tree()
            return False
    
    @handle_error
    def stop_module(self, module_id):
        """
        停止模块
        
        Args:
            module_id: 模块ID
        
        Returns:
            bool: 是否成功停止
        """
        try:
            # 获取模块PID
            pid = self.module_status[module_id]["pid"]
            if pid is None:
                self.add_log(_("main_console.module_not_running", f"模块未运行: {module_id}"))
                return True
            
            # 更新状态
            self.status_var.set(_("main_console.stopping_module", f"正在停止模块: {module_id}..."))
            self.add_log(_("main_console.stopping_module", f"正在停止模块: {module_id}..."))
            
            # 停止模块
            if not stop_module(pid):
                self.status_var.set(_("main_console.error_stopping_module", f"停止模块失败: {module_id}"))
                self.add_log(_("main_console.error_stopping_module", f"停止模块失败: {module_id}"))
                return False
            
            # 更新状态
            self.module_status[module_id]["pid"] = None
            self.module_status[module_id]["status"] = "stopped"
            self.status_var.set(_("main_console.module_stopped", f"模块已停止: {module_id}"))
            self.add_log(_("main_console.module_stopped", f"模块已停止: {module_id}"))
            self.update_module_tree()
            
            return True
        except Exception as e:
            logger.error(f"停止模块失败: {module_id}, 错误: {str(e)}")
            self.status_var.set(_("main_console.error_stopping_module", f"停止模块失败: {module_id}"))
            self.add_log(_("main_console.error_stopping_module", f"停止模块失败: {module_id}, 错误: {str(e)}"))
            return False
    
    @handle_error
    def restart_module(self, module_id):
        """
        重启模块
        
        Args:
            module_id: 模块ID
        
        Returns:
            bool: 是否成功重启
        """
        try:
            # 更新状态
            self.status_var.set(_("main_console.restarting_module", f"正在重启模块: {module_id}..."))
            self.add_log(_("main_console.restarting_module", f"正在重启模块: {module_id}..."))
            
            # 获取模块PID和端口
            pid = self.module_status[module_id]["pid"]
            port = self.module_status[module_id]["port"]
            
            # 重启模块
            new_pid = restart_module(module_id, pid, port)
            
            if new_pid is None:
                self.module_status[module_id]["status"] = "error"
                self.status_var.set(_("main_console.error_restarting_module", f"重启模块失败: {module_id}"))
                self.add_log(_("main_console.error_restarting_module", f"重启模块失败: {module_id}"))
                return False
            
            # 更新状态
            self.module_status[module_id]["pid"] = new_pid
            self.module_status[module_id]["status"] = "running"
            self.status_var.set(_("main_console.module_restarted", f"模块已重启: {module_id}"))
            self.add_log(_("main_console.module_restarted", f"模块已重启: {module_id}"))
            self.update_module_tree()
            
            return True
        except Exception as e:
            logger.error(f"重启模块失败: {module_id}, 错误: {str(e)}")
            self.module_status[module_id]["status"] = "error"
            self.status_var.set(_("main_console.error_restarting_module", f"重启模块失败: {module_id}"))
            self.add_log(_("main_console.error_restarting_module", f"重启模块失败: {module_id}, 错误: {str(e)}"))
            self.update_module_tree()
            return False
    
    @handle_error
    def start_all_modules(self):
        """
        启动所有模块
        
        Returns:
            bool: 是否成功启动所有模块
        """
        success = True
        
        # 添加日志
        self.add_log(_("main_console.starting_all_modules", "正在启动所有模块..."))
        
        # 启动所有模块
        for module_id in self.module_status:
            if not self.start_module(module_id):
                success = False
        
        # 添加日志
        if success:
            self.add_log(_("main_console.all_modules_started", "所有模块已启动"))
        else:
            self.add_log(_("main_console.error_starting_all_modules", "启动所有模块失败，请查看日志获取详细信息"))
        
        return success
    
    @handle_error
    def stop_all_modules(self):
        """
        停止所有模块
        
        Returns:
            bool: 是否成功停止所有模块
        """
        success = True
        
        # 添加日志
        self.add_log(_("main_console.stopping_all_modules", "正在停止所有模块..."))
        
        # 停止所有模块
        for module_id in self.module_status:
            if not self.stop_module(module_id):
                success = False
        
        # 添加日志
        if success:
            self.add_log(_("main_console.all_modules_stopped", "所有模块已停止"))
        else:
            self.add_log(_("main_console.error_stopping_all_modules", "停止所有模块失败，请查看日志获取详细信息"))
        
        return success
    
    @handle_error
    def restart_all_modules(self):
        """
        重启所有模块
        
        Returns:
            bool: 是否成功重启所有模块
        """
        success = True
        
        # 添加日志
        self.add_log(_("main_console.restarting_all_modules", "正在重启所有模块..."))
        
        # 重启所有模块
        for module_id in self.module_status:
            if not self.restart_module(module_id):
                success = False
        
        # 添加日志
        if success:
            self.add_log(_("main_console.all_modules_restarted", "所有模块已重启"))
        else:
            self.add_log(_("main_console.error_restarting_all_modules", "重启所有模块失败，请查看日志获取详细信息"))
        
        return success
    
    def check_update(self):
        """
        检查更新
        """
        # 更新状态
        self.status_var.set(_("main_console.checking_update", "正在检查更新..."))
        self.add_log(_("main_console.checking_update", "正在检查更新..."))
        
        # TODO: 实现检查更新功能
        
        # 显示消息
        messagebox.showinfo(
            _("main_console.update", "更新"),
            _("main_console.no_update", "当前已是最新版本")
        )
        
        # 更新状态
        self.status_var.set(_("main_console.ready", "系统就绪"))
        self.add_log(_("main_console.no_update", "当前已是最新版本"))
    
    def open_documentation(self):
        """
        打开文档
        """
        # 文档路径
        docs_path = os.path.join(project_root, "docs", "index.html")
        
        # 检查文档是否存在
        if os.path.exists(docs_path):
            # 打开文档
            webbrowser.open(f"file://{docs_path}")
            self.add_log(_("main_console.opening_documentation", "正在打开文档..."))
        else:
            # 显示错误消息
            messagebox.showerror(
                _("main_console.error", "错误"),
                _("main_console.error_docs_missing", "文档文件缺失")
            )
            self.add_log(_("main_console.error_docs_missing", "文档文件缺失"))
    
    def open_settings(self):
        """
        打开系统设置
        """
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title(_("main_console.settings", "系统设置"))
        settings_window.geometry("600x400")
        settings_window.minsize(600, 400)
        
        # 设置UI主题
        setup_theme(settings_window)
        
        # 创建标题栏
        title_frame = create_title_bar(settings_window, _("main_console.settings", "系统设置"))
        title_frame.pack(fill="x")
        
        # 创建设置框架
        settings_frame = ttk.Frame(settings_window, padding=10)
        settings_frame.pack(fill="both", expand=True)
        
        # 创建设置选项卡
        notebook = ttk.Notebook(settings_frame)
        notebook.pack(fill="both", expand=True)
        
        # 创建常规设置选项卡
        general_frame = ttk.Frame(notebook, padding=10)
        notebook.add(general_frame, text=_("main_console.general_settings", "常规设置"))
        
        # 创建模块设置选项卡
        modules_frame = ttk.Frame(notebook, padding=10)
        notebook.add(modules_frame, text=_("main_console.module_settings", "模块设置"))
        
        # 创建日志设置选项卡
        logs_frame = ttk.Frame(notebook, padding=10)
        notebook.add(logs_frame, text=_("main_console.log_settings", "日志设置"))
        
        # 创建关于选项卡
        about_frame = ttk.Frame(notebook, padding=10)
        notebook.add(about_frame, text=_("main_console.about", "关于"))
        
        # 常规设置内容
        self.create_general_settings(general_frame)
        
        # 模块设置内容
        self.create_module_settings(modules_frame)
        
        # 日志设置内容
        self.create_log_settings(logs_frame)
        
        # 关于内容
        self.create_about_settings(about_frame)
        
        # 创建按钮框架
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        # 创建保存按钮
        save_btn = create_button(
            button_frame, 
            _("main_console.save", "保存"), 
            lambda: self.save_settings(settings_window),
            width=10
        )
        save_btn.pack(side="right", padx=5)
        
        # 创建取消按钮
        cancel_btn = create_button(
            button_frame, 
            _("main_console.cancel", "取消"), 
            lambda: settings_window.destroy(),
            width=10
        )
        cancel_btn.pack(side="right", padx=5)
    
    def create_general_settings(self, parent_frame):
        """
        创建常规设置
        
        Args:
            parent_frame: 父框架
        """
        # 创建语言设置
        language_frame = ttk.Frame(parent_frame)
        language_frame.pack(fill="x", pady=5)
        
        language_label = ttk.Label(language_frame, text=_("main_console.language", "语言:"))
        language_label.pack(side="left")
        
        # 获取支持的语言列表
        languages = i18n_manager.get_supported_languages()
        language_values = [lang_info["name"] for lang_code, lang_info in languages.items()]
        
        # 创建语言下拉框
        self.language_var = tk.StringVar(value=i18n_manager.get_language_name())
        language_combobox = ttk.Combobox(language_frame, textvariable=self.language_var, values=language_values, state="readonly")
        language_combobox.pack(side="left", padx=5)
        
        # 创建自动重启崩溃模块设置
        auto_restart_frame = ttk.Frame(parent_frame)
        auto_restart_frame.pack(fill="x", pady=5)
        
        self.auto_restart_var = tk.BooleanVar(value=config_manager.get("auto_restart_crashed_modules", True))
        auto_restart_check = ttk.Checkbutton(
            auto_restart_frame, 
            text=_("main_console.auto_restart_crashed_modules", "自动重启崩溃的模块"),
            variable=self.auto_restart_var
        )
        auto_restart_check.pack(side="left")
        
        # 创建资源监控设置
        resource_monitor_frame = ttk.Frame(parent_frame)
        resource_monitor_frame.pack(fill="x", pady=5)
        
        self.resource_monitor_var = tk.BooleanVar(value=config_manager.get("resource_monitoring.enabled", True))
        resource_monitor_check = ttk.Checkbutton(
            resource_monitor_frame, 
            text=_("main_console.enable_resource_monitoring", "启用资源监控"),
            variable=self.resource_monitor_var
        )
        resource_monitor_check.pack(side="left")
        
        # 创建依赖管理设置
        dependency_frame = ttk.LabelFrame(parent_frame, text=_("main_console.dependency_settings", "依赖管理设置"))
        dependency_frame.pack(fill="x", pady=5)
        
        # 创建使用镜像源设置
        pip_mirror_frame = ttk.Frame(dependency_frame)
        pip_mirror_frame.pack(fill="x", pady=5, padx=5)
        
        self.use_pip_mirror_var = tk.BooleanVar(value=config_manager.get("use_pip_mirror", True))
        use_pip_mirror_check = ttk.Checkbutton(
            pip_mirror_frame, 
            text=_("main_console.use_pip_mirror", "使用国内镜像源安装依赖"),
            variable=self.use_pip_mirror_var
        )
        use_pip_mirror_check.pack(side="left")
        
        # 创建镜像源URL设置
        pip_mirror_url_frame = ttk.Frame(dependency_frame)
        pip_mirror_url_frame.pack(fill="x", pady=5, padx=5)
        
        pip_mirror_url_label = ttk.Label(pip_mirror_url_frame, text=_("main_console.pip_mirror_url", "镜像源URL:"))
        pip_mirror_url_label.pack(side="left")
        
        # 创建镜像源URL输入框
        self.pip_mirror_url_var = tk.StringVar(value=config_manager.get("pip_mirror_url", "https://pypi.tuna.tsinghua.edu.cn/simple"))
        pip_mirror_url_entry = ttk.Entry(pip_mirror_url_frame, textvariable=self.pip_mirror_url_var, width=40)
        pip_mirror_url_entry.pack(side="left", padx=5)
    
    def create_module_settings(self, parent_frame):
        """
        创建模块设置
        
        Args:
            parent_frame: 父框架
        """
        # 创建模块端口设置
        ports_frame = ttk.LabelFrame(parent_frame, text=_("main_console.module_ports", "模块端口"))
        ports_frame.pack(fill="x", pady=5)
        
        # 获取模块端口配置
        module_ports = get_module_ports()
        
        # 创建端口输入框
        self.port_vars = {}
        row = 0
        for module_id, port in module_ports.items():
            # 创建标签
            module_label = ttk.Label(ports_frame, text=f"{module_id}:")
            module_label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            # 创建端口输入框
            self.port_vars[module_id] = tk.IntVar(value=port)
            port_entry = ttk.Entry(ports_frame, textvariable=self.port_vars[module_id], width=10)
            port_entry.grid(row=row, column=1, sticky="w", padx=5, pady=2)
            
            row += 1
    
    def create_log_settings(self, parent_frame):
        """
        创建日志设置
        
        Args:
            parent_frame: 父框架
        """
        # 创建日志级别设置
        log_level_frame = ttk.Frame(parent_frame)
        log_level_frame.pack(fill="x", pady=5)
        
        log_level_label = ttk.Label(log_level_frame, text=_("main_console.log_level", "日志级别:"))
        log_level_label.pack(side="left")
        
        # 日志级别选项
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        # 创建日志级别下拉框
        self.log_level_var = tk.StringVar(value=config_manager.get("logging.level", "INFO"))
        log_level_combobox = ttk.Combobox(log_level_frame, textvariable=self.log_level_var, values=log_levels, state="readonly")
        log_level_combobox.pack(side="left", padx=5)
        
        # 创建日志文件大小设置
        log_size_frame = ttk.Frame(parent_frame)
        log_size_frame.pack(fill="x", pady=5)
        
        log_size_label = ttk.Label(log_size_frame, text=_("main_console.log_file_size", "日志文件大小 (MB):"))
        log_size_label.pack(side="left")
        
        # 创建日志文件大小输入框
        self.log_size_var = tk.IntVar(value=config_manager.get("logging.max_file_size_mb", 10))
        log_size_entry = ttk.Entry(log_size_frame, textvariable=self.log_size_var, width=10)
        log_size_entry.pack(side="left", padx=5)
        
        # 创建日志文件备份数量设置
        log_backup_frame = ttk.Frame(parent_frame)
        log_backup_frame.pack(fill="x", pady=5)
        
        log_backup_label = ttk.Label(log_backup_frame, text=_("main_console.log_backup_count", "日志文件备份数量:"))
        log_backup_label.pack(side="left")
        
        # 创建日志文件备份数量输入框
        self.log_backup_var = tk.IntVar(value=config_manager.get("logging.backup_count", 5))
        log_backup_entry = ttk.Entry(log_backup_frame, textvariable=self.log_backup_var, width=10)
        log_backup_entry.pack(side="left", padx=5)
        
        # 创建控制台日志输出设置
        console_log_frame = ttk.Frame(parent_frame)
        console_log_frame.pack(fill="x", pady=5)
        
        self.console_log_var = tk.BooleanVar(value=config_manager.get("logging.console_output", True))
        console_log_check = ttk.Checkbutton(
            console_log_frame, 
            text=_("main_console.console_log_output", "控制台日志输出"),
            variable=self.console_log_var
        )
        console_log_check.pack(side="left")
    
    def create_about_settings(self, parent_frame):
        """
        创建关于设置
        
        Args:
            parent_frame: 父框架
        """
        # 创建系统信息
        system_info_frame = ttk.Frame(parent_frame)
        system_info_frame.pack(fill="x", pady=5)
        
        # 系统名称
        system_name = config_manager.get("system_info.name", "PHRL系统")
        system_version = config_manager.get("system_version", "1.0.0")
        system_name_label = ttk.Label(
            system_info_frame, 
            text=f"{system_name} {system_version}",
            font=("Arial", 14, "bold")
        )
        system_name_label.pack(pady=10)
        
        # 组织名称
    
    def save_settings(self, settings_window):
        """
        保存系统设置
        
        Args:
            settings_window: 设置窗口
        """
        # 保存语言设置
        selected_language = self.language_var.get()
        language_code = i18n_manager.get_language_code_by_name(selected_language)
        if language_code:
            config_manager.set("language", language_code)
        
        # 保存自动重启设置
        config_manager.set("auto_restart_crashed_modules", self.auto_restart_var.get())
        
        # 保存资源监控设置
        config_manager.set("resource_monitoring.enabled", self.resource_monitor_var.get())
        
        # 保存模块端口设置
        module_ports = {}
        for module_id, port_var in self.port_vars.items():
            try:
                port = port_var.get()
                if port > 0 and port < 65536:  # 有效端口范围
                    module_ports[module_id] = port
            except (ValueError, tk.TclError):
                pass
        
        if module_ports:
            config_manager.set("module_ports", module_ports)
        
        # 保存日志设置
        config_manager.set("logging.level", self.log_level_var.get())
        
        try:
            log_size = self.log_size_var.get()
            if log_size > 0:
                config_manager.set("logging.max_file_size_mb", log_size)
        except (ValueError, tk.TclError):
            pass
        
        try:
            log_backup = self.log_backup_var.get()
            if log_backup >= 0:
                config_manager.set("logging.backup_count", log_backup)
        except (ValueError, tk.TclError):
            pass
        
        config_manager.set("logging.console_output", self.console_log_var.get())
        
        # 保存依赖管理设置
        config_manager.set("use_pip_mirror", self.use_pip_mirror_var.get())
        config_manager.set("pip_mirror_url", self.pip_mirror_url_var.get())
        
        # 保存配置
        if config_manager.save():
            # 显示成功消息
            messagebox.showinfo(
                _("main_console.success", "成功"),
                _("main_console.settings_saved", "设置已保存")
            )
            
            # 关闭设置窗口
            settings_window.destroy()
            
            # 更新日志配置
            setup_logging(
                level=config_manager.get("logging.level", "INFO"),
                max_file_size_mb=config_manager.get("logging.max_file_size_mb", 10),
                backup_count=config_manager.get("logging.backup_count", 5),
                console_output=config_manager.get("logging.console_output", True)
            )
            
            # 添加日志
            self.add_log(_("main_console.settings_saved", "设置已保存"))
        else:
            # 显示错误消息
            messagebox.showerror(
                _("main_console.error", "错误"),
                _("main_console.error_saving_settings", "保存设置失败")
            )
            
            # 添加日志
            self.add_log(_("main_console.error_saving_settings", "保存设置失败"))