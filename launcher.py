# -*- coding: utf-8 -*-
"""
系统启动器

负责启动和管理整个系统，包括检查环境、启动主控台和各个模块。

更新日志：
- 2024-06-25：初始版本，提供基本启动和管理功能
"""

import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import threading
import webbrowser
import subprocess

# 添加项目根目录到系统路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 导入项目模块
from common.logger import get_logger, log_system_info
from common.system_checker import (
    check_python_version, check_disk_space, check_module_exists
)
from common.config_manager import ConfigManager
from common.process_manager import start_module, stop_module, check_module_status, get_module_ports, get_module_path
from common.ui_components import setup_theme, create_title_bar, create_button, create_card, create_progress_bar
from common.error_handler import handle_error
from common.file_manager import ensure_dir
from common.i18n_manager import get_i18n_manager, _

# 创建日志记录器
logger = get_logger("launcher", os.path.join(project_root, "logs", "launcher.log"))

# 创建配置管理器
config_manager = ConfigManager()

# 创建国际化管理器
i18n_manager = get_i18n_manager()


class LauncherApp:
    """
    系统启动器应用
    """
    def __init__(self, root):
        """
        初始化启动器应用
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.root.title(_("launcher.title", "PHRL系统启动器"))
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # 设置UI主题
        setup_theme(self.root)
        
        # 创建变量
        self.progress_var = tk.DoubleVar(value=0)
        self.status_var = tk.StringVar(value=_("launcher.initializing", "正在初始化..."))
        self.module_status = {
            "main_console": {
                "status": "stopped",
                "pid": None,
                "port": None
            },
            "question_bank": {
                "status": "stopped",
                "pid": None,
                "port": None
            },
            "grading_center": {
                "status": "stopped",
                "pid": None,
                "port": 5173  # Vue.js前端端口，用于浏览器访问
            },
            "exam_management": {
                "status": "stopped",
                "pid": None,
                "port": None
            },
            "client": {
                "status": "stopped",
                "pid": None,
                "port": None
            },
            "user_management": {
                "status": "stopped",
                "pid": None,
                "port": None
            },
            "developer_tools": {
                "status": "stopped",
                "pid": None,
                "port": None
            }
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
    
    def create_widgets(self):
        """
        创建UI组件
        """
        # 创建标题栏
        title_frame = create_title_bar(self.root, _("launcher.title", "PHRL系统启动器"))
        title_frame.pack(fill="x")
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # 创建左侧面板
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 创建系统信息卡片
        system_card = create_card(left_frame, _("launcher.system_info", "系统信息"))
        system_card.pack(fill="x", pady=5)
        
        # 系统信息内容
        system_info_frame = ttk.Frame(system_card)
        system_info_frame.pack(fill="x", padx=10, pady=5)
        
        # 系统名称
        system_name_label = ttk.Label(system_info_frame, text=_("launcher.system_name", "系统名称:"))
        system_name_label.grid(row=0, column=0, sticky="w", pady=2)
        system_name_value = ttk.Label(system_info_frame, text=str(config_manager.get("system_info.name", "PHRL系统")))
        system_name_value.grid(row=0, column=1, sticky="w", pady=2)

        # 系统版本
        system_version_label = ttk.Label(system_info_frame, text=_("launcher.system_version", "系统版本:"))
        system_version_label.grid(row=1, column=0, sticky="w", pady=2)
        system_version_value = ttk.Label(system_info_frame, text=str(config_manager.get("system_version", "1.0.0")))
        system_version_value.grid(row=1, column=1, sticky="w", pady=2)

        # 组织名称
        org_name_label = ttk.Label(system_info_frame, text=_("launcher.organization", "组织名称:"))
        org_name_label.grid(row=2, column=0, sticky="w", pady=2)
        org_name_value = ttk.Label(system_info_frame, text=str(config_manager.get("system_info.organization", "PHRL")))
        org_name_value.grid(row=2, column=1, sticky="w", pady=2)
        
        # 创建操作卡片
        actions_card = create_card(left_frame, _("launcher.operations", "操作"))
        actions_card.pack(fill="x", pady=5)
        
        # 操作按钮
        actions_frame = ttk.Frame(actions_card)
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        # 启动主控台按钮
        self.start_console_btn = create_button(
            actions_frame, 
            _("launcher.start_main_console", "启动主控制台"), 
            lambda: self.start_main_console(),
            width=20
        )
        self.start_console_btn.pack(fill="x", pady=5)
        
        # 启动所有模块按钮
        self.start_all_btn = create_button(
            actions_frame, 
            _("launcher.start_all_modules", "启动所有模块"), 
            lambda: self.start_all_modules(),
            width=20
        )
        self.start_all_btn.pack(fill="x", pady=5)
        
        # 停止所有模块按钮
        self.stop_all_btn = create_button(
            actions_frame, 
            _("launcher.stop_all_modules", "停止所有模块"), 
            lambda: self.stop_all_modules(),
            width=20
        )
        self.stop_all_btn.pack(fill="x", pady=5)
        
        # 检查更新按钮
        self.check_update_btn = create_button(
            actions_frame, 
            _("launcher.check_update", "检查更新"), 
            lambda: self.check_update(),
            width=20
        )
        self.check_update_btn.pack(fill="x", pady=5)
        
        # 打开文档按钮
        self.open_docs_btn = create_button(
            actions_frame, 
            _("launcher.view_documentation", "查看文档"), 
            lambda: self.open_documentation(),
            width=20
        )
        self.open_docs_btn.pack(fill="x", pady=5)
        
        # 帮助按钮
        self.help_btn = create_button(
            actions_frame, 
            _("launcher.help", "帮助"), 
            lambda: self.show_help(),
            width=20
        )
        self.help_btn.pack(fill="x", pady=5)
        
        # 关于按钮
        self.about_btn = create_button(
            actions_frame, 
            _("launcher.about", "关于"), 
            lambda: self.show_about(),
            width=20
        )
        self.about_btn.pack(fill="x", pady=5)
        
        # 创建快速启动卡片
        quick_launch_card = create_card(left_frame, _("launcher.quick_launch", "快速启动"))
        quick_launch_card.pack(fill="x", pady=5)
        
        # 快速启动按钮
        quick_launch_frame = ttk.Frame(quick_launch_card)
        quick_launch_frame.pack(fill="x", padx=10, pady=5)
        
        # 题库管理按钮
        self.question_bank_btn = create_button(
            quick_launch_frame, 
            _("launcher.question_bank", "题库管理"), 
            lambda: self.start_question_bank(),
            width=20
        )
        self.question_bank_btn.pack(fill="x", pady=5)
        
        # 用户管理按钮
        self.user_management_btn = create_button(
            quick_launch_frame, 
            _("launcher.user_management", "用户管理"), 
            lambda: self.start_user_management(),
            width=20
        )
        self.user_management_btn.pack(fill="x", pady=5)
        
        # 考试管理按钮
        self.exam_management_btn = create_button(
            quick_launch_frame, 
            _("launcher.exam_management", "考试管理"), 
            lambda: self.start_exam_management(),
            width=20
        )
        self.exam_management_btn.pack(fill="x", pady=5)
        
        # 客户端按钮
        self.client_btn = create_button(
            quick_launch_frame,
            _("launcher.client", "客户端"),
            lambda: self.start_client(),
            width=20
        )
        self.client_btn.pack(fill="x", pady=5)

        # 开发工具按钮
        self.developer_tools_btn = create_button(
            quick_launch_frame,
            _("launcher.developer_tools", "开发工具"),
            lambda: self.start_developer_tools(),
            width=20
        )
        self.developer_tools_btn.pack(fill="x", pady=5)
        
        # 创建右侧面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # 创建模块状态卡片
        modules_card = create_card(right_frame, _("launcher.module_status", "模块状态"))
        modules_card.pack(fill="both", expand=True, pady=5)
        
        # 模块状态内容
        modules_frame = ttk.Frame(modules_card)
        modules_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 模块状态表格
        columns = ("module", "status", "port", "actions")
        self.modules_tree = ttk.Treeview(modules_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        self.modules_tree.heading("module", text=_("launcher.module", "模块"))
        self.modules_tree.heading("status", text=_("launcher.status", "状态"))
        self.modules_tree.heading("port", text=_("launcher.port", "端口"))
        self.modules_tree.heading("actions", text=_("launcher.actions", "操作"))
        
        # 设置列宽
        self.modules_tree.column("module", width=150)
        self.modules_tree.column("status", width=100)
        self.modules_tree.column("port", width=100)
        self.modules_tree.column("actions", width=200)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(modules_frame, orient="vertical", command=self.modules_tree.yview)
        self.modules_tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.modules_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加模块到表格
        self.update_module_tree()
        
        # 绑定表格点击事件
        self.modules_tree.bind("<Double-1>", self.on_module_double_click)
        
        # 创建底部状态栏
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom")
        
        # 状态标签
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(side="left", padx=10, pady=5)
        
        # 进度条
        progress_bar = create_progress_bar(status_frame, mode="determinate", length=200)
        progress_bar["variable"] = self.progress_var
        progress_bar.pack(side="right", padx=10, pady=5, fill="x", expand=True)
    
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
                "id": "main_console",
                "name": _("launcher.main_console", "主控台"),
                "status": self.module_status["main_console"]["status"],
                "port": self.module_status["main_console"]["port"]
            },
            {
                "id": "question_bank",
                "name": _("launcher.question_bank", "题库管理"),
                "status": self.module_status["question_bank"]["status"],
                "port": self.module_status["question_bank"]["port"]
            },
            {
                "id": "grading_center",
                "name": _("launcher.grading_center", "阅卷中心"),
                "status": self.module_status["grading_center"]["status"],
                "port": self.module_status["grading_center"]["port"]
            },
            {
                "id": "exam_management",
                "name": _("launcher.exam_management", "考试管理"),
                "status": self.module_status["exam_management"]["status"],
                "port": self.module_status["exam_management"]["port"]
            },
            {
                "id": "client",
                "name": _("launcher.client", "客户端"),
                "status": self.module_status["client"]["status"],
                "port": self.module_status["client"]["port"]
            },
            {
                "id": "user_management",
                "name": _("launcher.user_management", "用户管理"),
                "status": self.module_status["user_management"]["status"],
                "port": self.module_status["user_management"]["port"]
            },
            {
                "id": "developer_tools",
                "name": _("launcher.developer_tools", "开发工具"),
                "status": self.module_status["developer_tools"]["status"],
                "port": self.module_status["developer_tools"]["port"]
            }
        ]
        
        for module in modules:
            # 格式化状态文本
            status_text = {
                "running": _("launcher.running", "运行中"),
                "stopped": _("launcher.stopped", "已停止"),
                "starting": _("launcher.starting", "启动中"),
                "error": _("launcher.error", "错误")
            }.get(module["status"], _("launcher.unknown", "未知"))
            
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
        item = self.modules_tree.selection()[0]
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
    
    def create_question_bank_venv(self):
        """
        为题库管理模块创建专用虚拟环境并安装依赖
        
        Returns:
            bool: 是否成功创建虚拟环境并安装依赖
        """
        try:
            # 更新状态
            self.status_var.set('正在创建虚拟环境...')
            self.progress_var.set(10)
            
            # 虚拟环境路径
            venv_path = os.path.join(project_root, "venv_qb")
            
            # 检查是否已存在
            if os.path.exists(venv_path):
                logger.info(f"虚拟环境已存在: {venv_path}")
                return True
            
            # 创建虚拟环境
            logger.info(f"开始创建虚拟环境: {venv_path}")
            try:
                import venv
                venv.create(venv_path, with_pip=True)
            except ImportError:
                # 如果venv模块不可用，使用命令行创建
                # 使用venv模块创建虚拟环境（Python 3.3+内置）
                cmd = f"{sys.executable} -m venv {venv_path}"
                
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                _, stderr = process.communicate()

                if process.returncode != 0:
                    logger.error(f"创建虚拟环境失败: {stderr}")
                    messagebox.showerror(
                        '错误',
                        f'创建虚拟环境失败:\n{stderr}'
                    )
                    return False
            
            self.progress_var.set(30)
            self.status_var.set('正在安装依赖项...')
            
            # 获取pip路径
            if os.name == 'nt':  # Windows
                pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
            else:  # Linux/Mac
                pip_path = os.path.join(venv_path, "bin", "pip")
            
            # 检查pip是否存在
            if not os.path.exists(pip_path):
                logger.error(f"虚拟环境中pip不存在: {pip_path}")
                messagebox.showerror(
                    '错误',
                    '虚拟环境中pip不存在，请手动安装依赖项。'
                )
                return False
            
            # 安装依赖项
            # 1. 从requirements.txt安装
            requirements_path = os.path.join(project_root, "question_bank_web", "requirements.txt")
            if os.path.exists(requirements_path):
                logger.info(f"从requirements.txt安装依赖: {requirements_path}")
                
                cmd = f"\"{pip_path}\" install -r \"{requirements_path}\""
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                _, stderr = process.communicate()

                if process.returncode != 0:
                    logger.error(f"安装依赖项失败: {stderr}")
                    messagebox.showerror(
                        '错误',
                        f'安装依赖项失败:\n{stderr}'
                    )
                    return False
            else:
                # 2. 安装必要的包
                packages = ["flask", "pandas", "numpy", "openpyxl", "Pillow", "requests"]
                logger.info(f"安装必要的包: {', '.join(packages)}")
                
                cmd = f"\"{pip_path}\" install {' '.join(packages)}"
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                _, stderr = process.communicate()

                if process.returncode != 0:
                    logger.error(f"安装依赖项失败: {stderr}")
                    messagebox.showerror(
                        '错误',
                        f'安装依赖项失败:\n{stderr}'
                    )
                    return False
            
            self.progress_var.set(100)
            self.status_var.set('虚拟环境创建成功')

            messagebox.showinfo(
                '成功',
                '题库管理模块的虚拟环境创建成功，现在可以启动题库管理模块了。'
            )
            
            return True
        except Exception as e:
            logger.exception("创建虚拟环境时发生异常")
            messagebox.showerror(
                '错误',
                f'创建虚拟环境时发生错误:\n{str(e)}'
            )
            return False
    
    def check_numpy_import_issue(self):
        """
        检查numpy导入问题
        """
        try:
            # 检查题库管理模块的虚拟环境
            venv_path = os.path.join(project_root, "venv_qb")
            if os.path.exists(venv_path):
                logger.info(f"检测到题库管理模块的虚拟环境: {venv_path}")
                
                # 检查numpy是否已安装在虚拟环境中
                if os.name == 'nt':
                    pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
                    python_path = os.path.join(venv_path, "Scripts", "python.exe")
                else:
                    pip_path = os.path.join(venv_path, "bin", "pip")
                    python_path = os.path.join(venv_path, "bin", "python")
                
                if os.path.exists(pip_path) and os.path.exists(python_path):
                    # 检查numpy是否已安装
                    try:
                        result = subprocess.run(
                            [python_path, "-c", "import numpy; print('numpy已安装')"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if "numpy已安装" in result.stdout:
                            logger.info("虚拟环境中已安装numpy")
                            return True
                        else:
                            logger.warning(f"虚拟环境中numpy导入失败: {result.stderr}")
                    except subprocess.SubprocessError as e:
                        logger.warning(f"检查numpy安装状态失败: {str(e)}")
            
            return False
        except Exception as e:
            logger.error(f"检查numpy导入问题时出错: {str(e)}")
            return False
    
    def check_package_version(self, package_name, required_version=None):
        """
        检查包的版本是否符合要求
        
        Args:
            package_name (str): 包名称
            required_version (str, optional): 所需版本，格式如 '==1.0.0', '>=2.0.0', '<=3.0.0'
            
        Returns:
            tuple: (是否已安装, 是否版本符合要求, 当前版本)
        """
        try:
            # 尝试导入包
            module = __import__(package_name)
            
            # 获取版本号
            version = getattr(module, '__version__', None)
            if version is None and hasattr(module, 'version'):
                version = getattr(module, 'version', None)
            
            # 如果模块本身没有版本属性，尝试使用pkg_resources获取
            if version is None:
                try:
                    import pkg_resources
                    version = pkg_resources.get_distribution(package_name).version
                except (ImportError, pkg_resources.DistributionNotFound):
                    version = "未知"
            
            # 如果没有指定所需版本，则认为任何版本都符合要求
            if required_version is None:
                return True, True, version
            
            # 解析所需版本
            import re
            version_match = re.match(r'([=<>]+)(.+)', required_version)
            if not version_match:
                return True, True, version
            
            operator, ver = version_match.groups()
            
            # 比较版本
            from packaging import version as version_parser
            current_ver = version_parser.parse(version)
            required_ver = version_parser.parse(ver)
            
            if operator == '==' and current_ver == required_ver:
                return True, True, version
            elif operator == '>=' and current_ver >= required_ver:
                return True, True, version
            elif operator == '<=' and current_ver <= required_ver:
                return True, True, version
            elif operator == '>' and current_ver > required_ver:
                return True, True, version
            elif operator == '<' and current_ver < required_ver:
                return True, True, version
            else:
                return True, False, version
        except ImportError:
            return False, False, None
        except Exception as e:
            logger.warning(f"检查{package_name}版本时出错: {str(e)}")
            return True, False, "未知"
    
    @handle_error
    def ensure_dependencies(self):
        """
        确保必要的依赖已安装
        """
        try:
            # 核心依赖列表（必须安装的基础依赖）
            # 修复：使用正确的包名和导入名称映射
            core_packages = {
                "flask": "flask",
                "pandas": "pandas",
                "openpyxl": "openpyxl",
                "pillow": "PIL",  # Pillow包的导入名称是PIL
                "requests": "requests",
                "psutil": "psutil"
            }
            missing_packages = []
            outdated_packages = []
            
            # 检查核心依赖是否已安装
            for package_name, import_name in core_packages.items():
                try:
                    __import__(import_name)
                    logger.info(f"{package_name}库已安装 (导入为 {import_name})")
                except ImportError:
                    logger.warning(f"{package_name}库未安装，将添加到安装列表")
                    missing_packages.append(package_name)
            
            # 尝试从requirements.txt读取完整依赖列表
            requirements_path = os.path.join(project_root, "requirements.txt")
            if os.path.exists(requirements_path):
                logger.info("检测到requirements.txt文件，尝试读取完整依赖列表")
                try:
                    # 读取requirements.txt文件内容
                    with open(requirements_path, 'r', encoding='utf-8') as f:
                        requirements = f.readlines()
                    
                    # 解析依赖包名称和版本
                    for line in requirements:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # 解析包名和版本要求
                            import re
                            match = re.match(r'([\w\-\.]+)([=<>]+.+)?', line)
                            if match:
                                package_name, version_req = match.groups()
                                if package_name and package_name not in core_packages:
                                    installed, version_ok, version = self.check_package_version(package_name, version_req)
                                    if not installed:
                                        logger.warning(f"{package_name}库未安装，将添加到安装列表")
                                        missing_packages.append(line)  # 添加完整的依赖说明（包含版本号）
                                    elif not version_ok:
                                        logger.warning(f"{package_name}库版本不符合要求，当前版本: {version}, 需要: {version_req}")
                                        outdated_packages.append(line)  # 添加需要更新的包
                                    else:
                                        logger.info(f"{package_name}库已安装，版本: {version}，符合要求")
                except Exception as e:
                    logger.warning(f"读取requirements.txt文件时出错: {str(e)}")
            
            # 合并需要安装和需要更新的包
            packages_to_install = missing_packages + outdated_packages
            
            # 如果有缺失或过时的依赖，尝试安装
            if packages_to_install:
                logger.info(f"开始安装/更新依赖: {', '.join(packages_to_install)}")
                
                # 检查是否在虚拟环境中运行
                in_virtualenv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
                
                # 创建安装命令
                cmd = [sys.executable, "-m", "pip", "install"]
                if not in_virtualenv:
                    # 在非虚拟环境中使用--user参数
                    cmd.append("--user")
                
                # 检查是否使用镜像源
                use_mirror = config_manager.get('use_pip_mirror', True)
                if use_mirror:
                    mirror_url = str(config_manager.get('pip_mirror_url', 'https://pypi.tuna.tsinghua.edu.cn/simple'))
                    cmd.extend(["-i", mirror_url])
                    logger.info(f"使用镜像源: {mirror_url}")
                
                # 对于更新的包，添加--upgrade参数
                if outdated_packages:
                    cmd.append("--upgrade")
                
                # 安装所有缺失的依赖
                try:
                    cmd.extend(packages_to_install)
                    logger.info(f"执行命令: {' '.join(cmd)}")
                    subprocess.check_call(cmd)
                    logger.info("所有依赖安装/更新成功")
                except subprocess.CalledProcessError as e:
                    logger.error(f"依赖安装/更新失败: {str(e)}")
                    # 尝试逐个安装
                    success = True
                    for package in packages_to_install:
                        try:
                            install_cmd = cmd.copy()
                            if package in outdated_packages:
                                if "--upgrade" not in install_cmd:
                                    install_cmd.append("--upgrade")
                            install_cmd.append(package)
                            logger.info(f"尝试单独安装/更新: {' '.join(install_cmd)}")
                            subprocess.check_call(install_cmd)
                            logger.info(f"{package}安装/更新成功")
                        except subprocess.CalledProcessError as e:
                            logger.error(f"{package}安装/更新失败: {str(e)}")
                            success = False
                    if not success:
                        return False
            else:
                logger.info("所有依赖已安装且版本符合要求")
            
            return True
        except Exception as e:
            logger.error(f"安装依赖时出错: {str(e)}")
            return False

    def run_data_sync(self):
        """
        运行数据同步
        """
        try:
            logger.info("开始运行数据同步...")

            # 导入数据同步管理器
            from common.data_sync_manager import DataSyncManager

            sync_manager = DataSyncManager()

            # 同步试卷到考试系统
            if sync_manager.sync_published_papers_to_exam_system():
                logger.info("试卷同步成功")
            else:
                logger.warning("试卷同步失败，但系统可以继续运行")

            # 处理待阅卷的考试
            try:
                from grading_center.auto_grader import AutoGrader
                grader = AutoGrader()
                processed_count = grader.process_pending_exams()
                if processed_count > 0:
                    logger.info(f"成功处理 {processed_count} 个待阅卷考试")
            except Exception as e:
                logger.warning(f"自动阅卷处理失败: {e}")

            # 同步阅卷结果到成绩统计
            if sync_manager.sync_grading_results_to_statistics():
                logger.info("成绩同步成功")
            else:
                logger.warning("成绩同步失败，但系统可以继续运行")

            logger.info("数据同步完成")

        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            # 数据同步失败不应该阻止系统启动
    
    def initialize_system(self):
        """
        初始化系统
        """
        try:
            # 更新状态
            self.status_var.set(_('launcher.checking_environment', '正在检查环境...'))
            self.progress_var.set(10)
            
            # 确保必要的依赖已安装
            self.ensure_dependencies()
            
            # 记录系统信息
            log_system_info(logger)
            
            # 检查Python版本
            min_python_version = config_manager.get('min_python_version', '3.6.0')
            if not check_python_version(min_python_version):
                self.show_error(_('launcher.error_python_version', f'Python版本不满足要求，需要 {min_python_version} 或更高版本'))
                return
            
            self.progress_var.set(15)
            
            # 检查numpy导入问题
            numpy_check_result = self.check_numpy_import_issue()
            if numpy_check_result:
                logger.info("numpy导入问题检查通过")
            else:
                logger.warning("numpy导入问题检查未通过，可能需要特殊处理")
            
            self.progress_var.set(20)
            
            # 检查磁盘空间
            required_space = config_manager.get('required_disk_space', 500)  # MB
            if not check_disk_space(required_space):
                self.show_error(_('launcher.error_disk_space', f'磁盘空间不足，需要至少 {required_space} MB'))
                return
            
            self.progress_var.set(30)
            
            # 检查模块文件是否存在
            modules = ["main_console", "question_bank", "grading_center", "exam_management", "client", "user_management"]
            missing_modules = []
            for module in modules:
                module_path = get_module_path(module)
                if not module_path or not check_module_exists(module_path):
                    missing_modules.append(module)
            
            if missing_modules:
                # 显示缺失模块的详细信息
                missing_info = ", ".join(missing_modules)
                logger.warning(f"模块检查: 缺失 {len(missing_modules)} 个模块: {missing_info}")
                if messagebox.askyesno(_("launcher.warning", "警告"),
                                     _("launcher.error_module_missing", f"以下模块文件缺失:\n\n{missing_info}\n\n是否继续启动系统？")):
                    # 用户选择继续
                    logger.info("用户选择继续启动系统，尽管有模块缺失")
                else:
                    # 用户选择取消
                    return
            
            self.progress_var.set(40)

            # 运行数据同步
            self.status_var.set("正在同步系统数据...")
            self.run_data_sync()

            self.progress_var.set(50)

            # 检查依赖项
            self.status_var.set(_("launcher.checking_dependencies", "正在检查依赖项..."))
            # 修复：使用正确的导入名称映射
            required_packages = {
                "flask": "flask",
                "pandas": "pandas",
                "openpyxl": "openpyxl",
                "pillow": "PIL",  # Pillow包的导入名称是PIL
                "requests": "requests"
            }
            missing_packages = []

            for package_name, import_name in required_packages.items():
                try:
                    __import__(import_name)
                    logger.debug(f"依赖检查通过: {package_name} (导入为 {import_name})")
                except ImportError:
                    logger.warning(f"依赖检查失败: {package_name} (尝试导入 {import_name})")
                    missing_packages.append(package_name)
            
            if missing_packages:
                # 提示安装缺失的依赖项
                missing_info = ", ".join(missing_packages)
                logger.warning(f"依赖项检查: 缺失 {len(missing_packages)} 个包: {missing_info}")
                if messagebox.askyesno(_("launcher.warning", "警告"), 
                                     _("launcher.error_dependencies", f"以下Python包缺失:\n\n{missing_info}\n\n是否自动安装这些依赖项？")):
                    # 安装依赖项
                    if self.install_dependencies(missing_packages):
                        # 安装成功，继续执行
                        logger.info("依赖项安装成功，继续执行")
                    else:
                        # 安装失败，提示用户手动安装
                        self.show_error(_("launcher.error_dependencies", f"依赖项安装失败，请手动安装: {', '.join(missing_packages)}"))
                        return
                else:
                    # 用户选择不安装
                    if messagebox.askyesno(_("launcher.warning", "警告"),
                                         _("launcher.continue_without_dependencies", "是否继续启动系统？缺少依赖项可能导致某些功能无法正常使用。")):
                        # 用户选择继续
                        logger.info("用户选择继续启动系统，尽管有依赖项缺失")
                    else:
                        # 用户选择取消
                        return
            
            self.progress_var.set(60)
            
            # 确保必要的目录存在
            ensure_dir(os.path.join(project_root, "logs"))
            ensure_dir(os.path.join(project_root, "data"))
            ensure_dir(os.path.join(project_root, "temp"))
            
            self.progress_var.set(80)
            
            # 获取模块端口配置
            module_ports = get_module_ports()
            for module, port in module_ports.items():
                if module in self.module_status:
                    self.module_status[module]["port"] = port
            
            # 更新模块状态表格
            self.update_module_tree()
            
            self.progress_var.set(100)
            self.status_var.set(_("launcher.ready", "系统就绪"))
            
            # 记录初始化完成
            logger.info("系统初始化完成")
        except Exception as e:
            logger.error(f"系统初始化失败: {str(e)}")
            self.show_error(_("launcher.error_initialization", f"系统初始化失败: {str(e)}"))
    
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
                    
                    if pid is not None:
                        # 检查模块状态
                        status = check_module_status(pid, port)
                        self.module_status[module_id]["status"] = status
                
                # 更新模块状态表格
                self.update_module_tree()
            except Exception as e:
                logger.error(f"更新模块状态失败: {str(e)}")
            
            # 等待一段时间
            time.sleep(5)
    
    @handle_error
    def start_module(self, module_id, open_browser=True):
        """
        启动模块
        
        Args:
            module_id: 模块ID
            open_browser: 是否自动打开浏览器
        
        Returns:
            bool: 是否成功启动
        """
        try:
            # 更新状态
            self.status_var.set(_("launcher.starting_module", f"正在启动模块: {module_id}..."))
            self.module_status[module_id]["status"] = "starting"
            self.update_module_tree()
            
            # 启动模块
            port = self.module_status[module_id]["port"]
            module_path = get_module_path(module_id)
            module_info = start_module(module_id, module_path, port)
            
            if module_info["pid"] is None:
                self.module_status[module_id]["status"] = "error"
                self.status_var.set(_("launcher.error_starting_module", f"启动模块失败: {module_id}"))
                return False
            
            # 更新状态
            self.module_status[module_id]["pid"] = module_info["pid"]
            self.module_status[module_id]["status"] = "running"
            self.status_var.set(_("launcher.module_started", f"模块已启动: {module_id}"))
            self.update_module_tree()
            
            # 如果需要自动打开浏览器
            if open_browser and port is not None:
                try:
                    import webbrowser
                    url = f"http://127.0.0.1:{port}"
                    webbrowser.open_new(url)
                except ImportError:
                    pass
            
            return True
        except Exception as e:
            logger.error(f"启动模块失败: {module_id}, 错误: {str(e)}")
            self.module_status[module_id]["status"] = "error"
            self.status_var.set(_("launcher.error_starting_module", f"启动模块失败: {module_id}"))
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
                return True
            
            # 更新状态
            self.status_var.set(_("launcher.stopping_module", f"正在停止模块: {module_id}..."))
            
            # 停止模块
            if not stop_module(pid):
                self.status_var.set(_("launcher.error_stopping_module", f"停止模块失败: {module_id}"))
                return False
            
            # 更新状态
            self.module_status[module_id]["pid"] = None
            self.module_status[module_id]["status"] = "stopped"
            self.status_var.set(_("launcher.module_stopped", f"模块已停止: {module_id}"))
            self.update_module_tree()
            
            return True
        except Exception as e:
            logger.error(f"停止模块失败: {module_id}, 错误: {str(e)}")
            self.status_var.set(_("launcher.error_stopping_module", f"停止模块失败: {module_id}"))
            return False
    
    @handle_error
    def start_main_console(self):
        """
        启动主控台
        
        Returns:
            bool: 是否成功启动
        """
        return self.start_module("main_console")
    
    @handle_error
    def start_question_bank(self):
        """
        启动题库管理
        
        Returns:
            bool: 是否成功启动
        """
        # 检查numpy导入问题
        numpy_check_result = self.check_numpy_import_issue()
        
        # 如果检查未通过，显示提示信息
        if not numpy_check_result:
            # 检查是否存在虚拟环境
            venv_path = os.path.join(project_root, "venv_qb")
            if not os.path.exists(venv_path):
                # 提示创建虚拟环境
                if messagebox.askyesno(
                    _('launcher.warning', '警告'),
                    _('launcher.numpy_issue', '检测到可能存在numpy导入问题，这可能导致题库管理模块无法正常运行。\n\n是否创建专用虚拟环境并安装依赖项？')
                ):
                    # 创建虚拟环境并安装依赖
                    if not self.create_question_bank_venv():
                        messagebox.showerror(
                            _('launcher.error', '错误'),
                            _('launcher.venv_creation_failed', '创建虚拟环境失败，题库管理模块可能无法正常运行。')
                        )
                    # 重新检查
                    numpy_check_result = self.check_numpy_import_issue()
            else:
                # 提示激活虚拟环境
                messagebox.showinfo(
                    _('launcher.info', '提示'),
                    _('launcher.numpy_issue_solution', '检测到可能存在numpy导入问题。\n\n系统将使用专用虚拟环境启动题库管理模块，以避免numpy导入冲突。')
                )
        
        # 更新状态
        self.status_var.set(_('launcher.starting_module', '正在启动题库管理模块...'))
        self.module_status["question_bank"]["status"] = "starting"
        self.update_module_tree()
        
        # 获取模块信息
        module_path = get_module_path("question_bank")
        # 注意：question_bank_web/run.py中硬编码了端口5000
        port = 5000  # 使用硬编码的端口5000
        self.module_status["question_bank"]["port"] = port  # 更新状态中的端口
        cwd = os.path.dirname(module_path)
        
        # 启动Web模块，使用process_manager中的start_web_module函数
        # 这个函数会自动处理numpy导入问题，使用虚拟环境启动
        from common.process_manager import start_web_module
        module_info = start_web_module("question_bank", module_path, port, cwd=cwd, open_browser=True)
        
        if module_info["pid"] is None:
            self.module_status["question_bank"]["status"] = "error"
            self.status_var.set(_('launcher.error_starting_module', '启动题库管理模块失败'))
            self.update_module_tree()
            return False
        
        # 更新状态
        self.module_status["question_bank"]["pid"] = module_info["pid"]
        self.module_status["question_bank"]["status"] = "running"
        self.status_var.set(_('launcher.module_started', '题库管理模块已启动'))
        self.update_module_tree()
        
        # 等待服务启动并验证端口
        def check_port_listening(host, port, max_attempts=30):
            import socket
            import time
            import requests
            logger.info(f"开始检查端口 {port} 是否开放，最多尝试 {max_attempts} 次")
            
            for attempt in range(max_attempts):
                # 方法1：使用socket检查端口
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    if result == 0:  # 端口已开放
                        logger.info(f"端口 {port} 已开放 (socket检查)")
                        
                        # 方法2：尝试HTTP请求确认服务可访问
                        try:
                            url = f"http://{host}:{port}"
                            logger.info(f"尝试HTTP请求: {url}")
                            response = requests.get(url, timeout=2)
                            logger.info(f"HTTP请求成功: 状态码 {response.status_code}")
                            return True
                        except Exception as e:
                            logger.warning(f"端口已开放但HTTP请求失败: {str(e)}")
                            # 即使HTTP请求失败，只要端口开放就返回True
                            return True
                    
                    logger.info(f"等待端口 {port} 开放，尝试 {attempt+1}/{max_attempts}")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"检查端口时出错: {str(e)}")
                    time.sleep(1)
            
            logger.error(f"端口 {port} 在 {max_attempts} 次尝试后仍未开放")
            return False
        
        # 等待服务启动 - 增加等待时间和尝试次数
        logger.info(f"等待题库管理服务启动在端口 {port}...")
        if check_port_listening('127.0.0.1', port):
            logger.info(f"题库管理服务已在端口 {port} 上启动")
            # 手动尝试打开浏览器 - 多次尝试
            for attempt in range(3):
                try:
                    import webbrowser
                    url = f"http://127.0.0.1:{port}"
                    # 使用不同的浏览器打开方法
                    browsers = [
                        lambda u: webbrowser.open_new(u),
                        lambda u: webbrowser.open_new_tab(u),
                        lambda u: webbrowser.get().open(u),
                        lambda u: os.system(f'start {u}')
                    ]
                    
                    # 尝试不同的方法打开浏览器
                    for i, browser_func in enumerate(browsers):
                        try:
                            logger.info(f"尝试打开浏览器方法 {i+1}: {url}")
                            result = browser_func(url)
                            logger.info(f"打开浏览器方法 {i+1} 结果: {result}")
                            if result or i == len(browsers) - 1:  # 最后一个方法是os.system，总是返回状态码
                                break
                        except Exception as e:
                            logger.warning(f"打开浏览器方法 {i+1} 失败: {str(e)}")
                    
                    # 如果成功打开或已尝试所有方法，则退出循环
                    break
                    
                except Exception as e:
                    logger.error(f"手动打开浏览器失败: {str(e)}")
                    time.sleep(1)
            
            # 显示成功消息和访问地址
            messagebox.showinfo(
                _('launcher.success', '成功'),
                _('launcher.module_started_with_url', f'题库管理模块已启动，请访问: http://127.0.0.1:{port}')
            )
        else:
            logger.error(f"题库管理服务未能在端口 {port} 上启动")
        
        return True
        
    @handle_error
    def start_user_management(self):
        """
        启动用户管理
        
        Returns:
            bool: 是否成功启动
        """
        return self.start_module("user_management")
        
    @handle_error
    def start_exam_management(self):
        """
        启动考试管理
        
        Returns:
            bool: 是否成功启动
        """
        return self.start_module("exam_management")
        
    @handle_error
    def start_client(self):
        """
        启动客户端

        Returns:
            bool: 是否成功启动
        """
        return self.start_module("client")

    @handle_error
    def start_developer_tools(self):
        """
        启动开发工具

        Returns:
            bool: 是否成功启动
        """
        try:
            # 检查开发工具是否已经在运行
            if self.module_status["developer_tools"]["status"] == "running":
                messagebox.showinfo("提示", "开发工具已经在运行中")
                return True

            # 更新状态
            self.status_var.set("正在启动开发工具...")
            self.module_status["developer_tools"]["status"] = "starting"
            self.update_module_tree()

            # 获取开发工具脚本路径
            developer_tools_path = os.path.join(project_root, "developer_tools.py")
            if not os.path.exists(developer_tools_path):
                messagebox.showerror("错误", "找不到开发工具文件")
                self.module_status["developer_tools"]["status"] = "stopped"
                self.update_module_tree()
                return False

            # 启动开发工具进程
            if os.name == 'nt':  # Windows
                cmd = f'start cmd /k "cd /d {project_root} && python developer_tools.py"'
                process = subprocess.Popen(cmd, shell=True)
            else:  # Linux/Mac
                process = subprocess.Popen([sys.executable, developer_tools_path])

            # 等待一下确保进程启动
            time.sleep(1)

            # 更新模块状态
            self.module_status["developer_tools"]["pid"] = process.pid
            self.module_status["developer_tools"]["status"] = "running"

            self.update_module_tree()
            self.status_var.set("开发工具已启动")
            messagebox.showinfo("成功", "开发工具已启动")

            return True

        except Exception as e:
            logger.error(f"启动开发工具失败: {e}")
            messagebox.showerror("错误", f"启动开发工具失败: {str(e)}")
            self.module_status["developer_tools"]["status"] = "stopped"
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
        
        # 启动主控台
        if not self.start_module("main_console"):
            success = False
        
        # 启动题库管理模块（使用特殊处理）
        if not self.start_question_bank():
            success = False
        
        # 启动其他模块
        for module_id in ["grading_center", "exam_management", "client", "user_management"]:
            if not self.start_module(module_id):
                success = False

        # 启动开发工具（可选）
        if not self.start_developer_tools():
            # 开发工具启动失败不影响整体成功状态
            logger.warning("开发工具启动失败，但不影响系统运行")
        
        return success
    
    @handle_error
    def stop_all_modules(self):
        """
        停止所有模块
        
        Returns:
            bool: 是否成功停止所有模块
        """
        success = True
        
        # 停止所有模块
        for module_id in self.module_status:
            if not self.stop_module(module_id):
                success = False
        
        return success
    
    def check_update(self):
        """
        检查更新
        """
        # 更新状态
        self.status_var.set(_("launcher.checking_update", "正在检查更新..."))
        
        # TODO: 实现检查更新功能
        
        # 显示消息
        messagebox.showinfo(
            _("launcher.update", "更新"),
            _("launcher.no_update", "当前已是最新版本")
        )
        
        # 更新状态
        self.status_var.set(_("launcher.ready", "系统就绪"))
    
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
        else:
            # 显示错误消息
            messagebox.showerror(
                _("launcher.error", "错误"),
                _("launcher.error_docs_missing", "文档文件缺失")
            )
    
    def show_help(self):
        """
        显示帮助信息
        """
        help_text = """
系统启动器 - 帮助信息

【快速开始】
1. 点击"启动主控制台"按钮启动主控制台
2. 或者使用快速启动按钮启动特定模块
3. 在模块状态表格中查看各模块运行状态

【模块说明】
• 主控制台：系统的主界面，提供各模块的集中管理
• 题库管理：管理考试题目和题库
• 用户管理：管理用户账户和权限
• 成绩统计：分析考试成绩数据
• 阅卷中心：在线阅卷和评分
• 客户机端：考试答题界面
• 考试管理：考试管理和配置

【注意事项】
• 首次使用请确保已安装所需依赖
• 某些模块需要网络连接
• 如遇问题请查看错误提示

【技术支持】
• 邮箱：support@phrl-edu.com
• 电话：400-123-4567
• 工作时间：周一至周五 9:00-18:00
        """
        messagebox.showinfo(_("launcher.help", "帮助信息"), help_text)
    
    def show_about(self):
        """
        显示关于信息
        """
        system_info_raw = config_manager.get("system_info", {
            "name": "PH&RL在线考试系统",
            "version": "1.0.0",
            "copyright": "© 2024 PH&RL教育科技",
            "website": "https://www.phrl-edu.com"
        })

        # 确保system_info是字典类型
        if isinstance(system_info_raw, dict):
            system_info = system_info_raw
        else:
            system_info = {
                "name": "PH&RL在线考试系统",
                "version": "1.0.0",
                "copyright": "© 2024 PH&RL教育科技",
                "website": "https://www.phrl-edu.com"
            }

        about_text = f"""
{system_info.get('name', 'PH&RL在线考试系统')} v{system_info.get('version', '1.0.0')}

【系统简介】
PH&RL 在线考试系统是一个基于 Python 的模块化考试管理平台，
提供完整的在线考试解决方案。

【主要功能】
• 题库管理：支持多种题型的题库管理
• 用户管理：完整的用户权限管理体系
• 考试管理：灵活的考试配置和管理
• 成绩统计：多维度成绩分析和统计
• 阅卷中心：专业的在线阅卷平台
• 客户机端：安全稳定的考试界面

【技术架构】
• 后端：Python + Node.js
• 前端：Tkinter + Vue.js
• 数据库：MySQL + JSON
• 通信：HTTP API + 本地文件

{system_info.get('copyright', '© 2024 PH&RL教育科技')}
{system_info.get('website', 'https://www.phrl-edu.com')}
        """
        messagebox.showinfo(_("launcher.about", "关于系统"), about_text)
    
    def show_error(self, message):
        """
        显示错误消息
        
        Args:
            message: 错误消息
        """
        logger.error(message)
        messagebox.showerror(_("launcher.error", "错误"), message)
        self.status_var.set(_("launcher.error_occurred", "发生错误"))
        self.progress_var.set(0)
        
    def handle_dependency_error(self, error_output, packages, is_exception=False):
        """
        处理依赖安装错误并提供解决方案
        
        Args:
            error_output (str): 错误输出信息
            packages (list): 依赖包列表
            is_exception (bool): 是否为异常错误
            
        Returns:
            tuple: (错误消息, 解决方案消息)
        """
        error_message = error_output
        solution_message = ""
        
        # 将包列表转换为字符串
        packages_str = ' '.join(packages)
        
        # 检查常见错误
        if not is_exception:
            # pip安装错误
            if "--user" in error_output and ("not supported" in error_output.lower() or "not visible in this virtualenv" in error_output.lower()):
                solution_message = "\n\n解决方案: 请尝试手动安装依赖项，执行以下命令:\n"
                solution_message += f"pip install {packages_str}"
            elif "permission denied" in error_output.lower() or "access is denied" in error_output.lower():
                solution_message = "\n\n解决方案: 请尝试以管理员身份运行程序，或使用以下命令手动安装:\n"
                solution_message += f"pip install --user {packages_str}"
            elif "connection error" in error_output.lower() or "network" in error_output.lower() or "timeout" in error_output.lower():
                solution_message = "\n\n解决方案: 请检查网络连接后重试，或尝试使用国内镜像源:\n"
                solution_message += f"pip install -i https://pypi.tuna.tsinghua.edu.cn/simple {packages_str}"
            elif "could not find a version that satisfies the requirement" in error_output.lower():
                solution_message = "\n\n解决方案: 请检查包名称是否正确，或尝试安装较低版本的包。\n"
                solution_message += "您也可以尝试更新pip: pip install --upgrade pip"
            elif "conflicting dependencies" in error_output.lower() or "incompatible" in error_output.lower():
                solution_message = "\n\n解决方案: 存在依赖冲突，请尝试以下方法:\n"
                solution_message += "1. 创建虚拟环境后安装依赖\n"
                solution_message += "2. 使用 pip install --upgrade 更新相关包\n"
                solution_message += "3. 联系系统管理员解决依赖冲突"
            else:
                solution_message = "\n\n解决方案: 请尝试手动安装这些依赖项，或联系系统管理员获取帮助。\n"
                solution_message += f"pip install {packages_str}"
        else:
            # 异常错误
            if "No module named 'pip'" in error_output:
                solution_message = "\n\n解决方案: 请先安装pip工具，然后重试。\n"
                solution_message += "在Windows上，可以下载get-pip.py并运行: python get-pip.py"
            elif "Permission denied" in error_output or "Access is denied" in error_output:
                solution_message = "\n\n解决方案: 请尝试以管理员身份运行程序，或手动安装依赖项。"
            else:
                solution_message = f"\n\n解决方案: 请手动安装以下依赖项:\n"
                solution_message += f"pip install {packages_str}"
        
        return error_message, solution_message
    
    def install_dependencies(self, packages):
        """
        安装缺失的依赖项
        """
        try:
            # 确保subprocess模块可用
            import subprocess
            
            self.status_var.set("正在安装依赖项...")
            logger.info(f"开始安装依赖项: {', '.join(packages)}")

            # 检查是否在虚拟环境中运行
            in_virtualenv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            logger.info(f"运行环境: {'虚拟环境' if in_virtualenv else '系统环境'}")
            
            # 创建命令
            cmd = [sys.executable, "-m", "pip", "install"]
            # 在非虚拟环境中可以使用--user参数
            if not in_virtualenv:
                # 尝试使用--user参数，但不强制
                logger.info("非虚拟环境，尝试使用--user参数")
                try:
                    # 先检查pip版本，确保支持--user
                    pip_version_process = subprocess.Popen(
                        [sys.executable, "-m", "pip", "--version"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True
                    )
                    pip_version_output, _ = pip_version_process.communicate()
                    if pip_version_process.returncode == 0:
                        logger.info(f"pip版本: {pip_version_output.strip()}")
                        cmd.append("--user")
                except Exception as e:
                    logger.warning(f"检查pip版本失败: {str(e)}")
            
            # 尝试使用国内镜像源（如果网络连接不稳定）
            use_mirror = config_manager.get('use_pip_mirror', False)
            if use_mirror:
                cmd.extend(["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"])
                logger.info("使用清华大学镜像源")
            
            # 添加包列表
            cmd.extend(packages)
            
            # 执行安装
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 获取输出
            _, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("依赖项安装成功")
                messagebox.showinfo(
                    "成功",
                    "依赖项安装成功，请重启系统以应用更改。"
                )
                return True
            else:
                # 记录详细错误信息
                logger.error(f"依赖项安装失败: {stderr}")
                
                # 处理错误并获取解决方案
                error_message, solution_message = self.handle_dependency_error(stderr, packages)
                
                # 如果使用了镜像源但仍然失败，尝试不使用镜像源
                if use_mirror and ("connection error" in stderr.lower() or "timeout" in stderr.lower()):
                    logger.info("镜像源连接失败，尝试使用默认源")
                    # 移除镜像源参数
                    cmd = [item for item in cmd if item != "-i" and item != "https://pypi.tuna.tsinghua.edu.cn/simple"]
                    
                    # 重新执行安装
                    try:
                        logger.info(f"使用默认源重试: {' '.join(cmd)}")
                        retry_process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True
                        )
                        _, retry_stderr = retry_process.communicate()
                        
                        if retry_process.returncode == 0:
                            logger.info("使用默认源安装成功")
                            messagebox.showinfo(
                                "成功",
                                "依赖项安装成功，请重启系统以应用更改。"
                            )
                            return True
                        else:
                            logger.error(f"使用默认源安装失败: {retry_stderr}")
                            error_message, solution_message = self.handle_dependency_error(retry_stderr, packages)
                    except Exception as e:
                        logger.error(f"重试安装时出错: {str(e)}")
                
                # 显示错误信息和解决方案
                messagebox.showerror(
                    "错误",
                    f"依赖项安装失败:\n{error_message}{solution_message}"
                )
                return False
        except Exception as e:
            error_msg = str(e)
            logger.exception("安装依赖项时发生异常")
            
            # 处理异常错误并获取解决方案
            error_message, solution_message = self.handle_dependency_error(error_msg, packages, is_exception=True)
            
            # 显示错误信息和解决方案
            messagebox.showerror(
                "错误",
                f"安装依赖项时发生错误:\n{error_message}{solution_message}"
            )
            return False


def main():
    """
    主函数
    """
    try:
        # 创建根窗口
        root = tk.Tk()
        
        # 创建启动器应用
        LauncherApp(root)

        # 运行应用
        root.mainloop()
    except Exception as e:
        logger.error(f"启动器运行失败: {str(e)}")
        messagebox.showerror("错误", f"启动器运行失败: {str(e)}")


if __name__ == "__main__":
    main()