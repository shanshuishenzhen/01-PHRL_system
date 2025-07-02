#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL 在线考试系统启动脚本
提供系统检查、依赖验证和友好的启动界面

更新日志：
- 2024-07-01: 增加日志记录功能
- 2024-07-01: 增强错误处理
- 2024-07-01: 添加系统状态检查
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import subprocess
import threading
import time
import logging
import platform
import json
import ctypes
import tempfile
from datetime import datetime

# 配置日志
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'system_launcher.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class SystemLauncher:
    """系统启动器"""
    def __init__(self):
        logging.info("启动系统启动器")
        self.root = tk.Tk()
        self.root.title("PH&RL 在线考试系统 - 启动器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # 设置窗口图标（如果有的话）
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logging.warning(f"加载图标失败: {e}")
        
        # 设置主题颜色
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff'
        }
        
        # 系统状态
        self.system_status = {
            'python_version': False,
            'tkinter': False,
            'modules': False,
            'database': False,
            'dependencies': False,
            'disk_space': False
        }
        
        # 系统配置
        self.config = self.load_config()
        
        self.create_ui()
        self.check_system()
    
    def create_ui(self):
        """创建用户界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题区域
        self.create_header(main_frame)
        
        # 系统检查区域
        self.create_check_frame(main_frame)
        
        # 启动按钮区域
        self.create_launch_frame(main_frame)
        
        # 状态信息区域
        self.create_status_frame(main_frame)
    
    def create_header(self, parent):
        """创建标题区域"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 系统标题
        title_label = ttk.Label(
            header_frame, 
            text="🎓 PH&RL 在线考试系统", 
            font=("Microsoft YaHei", 24, "bold"),
            foreground=self.colors['primary']
        )
        title_label.pack()
        
        # 版本信息
        version_label = ttk.Label(
            header_frame, 
            text="v1.0.0 - 系统启动器", 
            font=("Microsoft YaHei", 12),
            foreground=self.colors['dark']
        )
        version_label.pack(pady=(5, 0))
    
    def create_check_frame(self, parent):
        """创建系统检查区域"""
        check_frame = ttk.LabelFrame(
            parent, 
            text="🔍 系统检查", 
            padding="15"
        )
        check_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 检查项目
        self.check_items = {}
        
        check_list = [
            ("Python版本", "python_version"),
            ("Tkinter界面库", "tkinter"),
            ("功能模块", "modules"),
            ("数据库连接", "database"),
            ("依赖项", "dependencies"),
            ("磁盘空间", "disk_space")
        ]
        
        for label, key in check_list:
            item_frame = ttk.Frame(check_frame)
            item_frame.pack(fill=tk.X, pady=2)
            
            # 检查项标签
            item_label = ttk.Label(
                item_frame, 
                text=f"• {label}:", 
                font=("Microsoft YaHei", 10),
                width=15
            )
            item_label.pack(side=tk.LEFT)
            
            # 状态标签
            status_label = ttk.Label(
                item_frame, 
                text="检查中...", 
                font=("Microsoft YaHei", 10),
                foreground=self.colors['warning']
            )
            status_label.pack(side=tk.LEFT, padx=(10, 0))
            
            self.check_items[key] = status_label
    
    def create_launch_frame(self, parent):
        """创建启动按钮区域"""
        launch_frame = ttk.Frame(parent)
        launch_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 启动按钮
        self.launch_button = tk.Button(
            launch_frame, 
            text="🚀 启动主控台", 
            command=self.launch_main_console,
            font=("Microsoft YaHei", 14, "bold"),
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=30,
            pady=15,
            cursor="hand2",
            state="disabled"
        )
        self.launch_button.pack()
        
        # 快速启动按钮
        quick_frame = ttk.Frame(launch_frame)
        quick_frame.pack(fill=tk.X, pady=(15, 0))
        
        quick_buttons = [
            ("📚 题库管理", self.launch_question_bank),
            ("👥 用户管理", self.launch_user_management),
            ("📊 成绩统计", self.launch_score_statistics),
            ("📝 考试管理", self.launch_exam_management),
            ("💻 客户机端", self.launch_client)
        ]
        
        for text, command in quick_buttons:
            btn = tk.Button(
                quick_frame, 
                text=text, 
                command=command,
                font=("Microsoft YaHei", 10),
                bg=self.colors['light'],
                fg=self.colors['dark'],
                activebackground=self.colors['primary'],
                activeforeground="white",
                relief="flat",
                borderwidth=1,
                padx=15,
                pady=8,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_status_frame(self, parent):
        """创建状态信息区域"""
        status_frame = ttk.LabelFrame(
            parent, 
            text="📋 系统信息", 
            padding="10"
        )
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # 系统信息
        info_items = [
            ("系统版本", f"v1.0.0"),
            ("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            ("运行平台", sys.platform),
            ("当前时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        for label, value in info_items:
            row_frame = ttk.Frame(status_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            ttk.Label(
                row_frame, 
                text=f"{label}:", 
                font=("Microsoft YaHei", 9, "bold")
            ).pack(side=tk.LEFT)
            
            ttk.Label(
                row_frame, 
                text=value, 
                font=("Microsoft YaHei", 9)
            ).pack(side=tk.RIGHT)
        
        # 分隔线
        ttk.Separator(status_frame, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # 帮助信息
        help_text = """
💡 使用提示：
• 首次使用请等待系统检查完成
• 点击"启动主控台"进入系统管理界面
• 或使用快速启动按钮直接启动特定模块
• 如遇问题请查看错误提示或联系技术支持
        """
        
        help_label = ttk.Label(
            status_frame, 
            text=help_text, 
            font=("Microsoft YaHei", 9),
            foreground=self.colors['dark'],
            justify=tk.LEFT
        )
        help_label.pack(anchor=tk.W)
    
    def load_config(self):
        """加载系统配置"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            "min_python_version": [3, 6],
            "required_disk_space_mb": 100,
            "check_dependencies": True,
            "auto_create_missing_files": True,
            "version": "1.0.0"
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
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
    
    def check_system(self):
        """检查系统状态"""
        def run_checks():
            logging.info("开始系统检查")
            # 检查Python版本
            self.check_python_version()
            time.sleep(0.5)
            
            # 检查Tkinter
            self.check_tkinter()
            time.sleep(0.5)
            
            # 检查功能模块
            self.check_modules()
            time.sleep(0.5)
            
            # 检查数据库
            self.check_database()
            time.sleep(0.5)
            
            # 检查依赖项
            self.check_dependencies()
            time.sleep(0.5)
            
            # 检查磁盘空间
            self.check_disk_space()
            time.sleep(0.5)
            
            # 更新启动按钮状态
            self.update_launch_button()
            logging.info("系统检查完成")
        
        threading.Thread(target=run_checks, daemon=True).start()
    
    def check_python_version(self):
        """检查Python版本"""
        try:
            min_version = tuple(self.config.get("min_python_version", [3, 6]))
            current_version = (sys.version_info.major, sys.version_info.minor)
            version_ok = current_version >= min_version
            self.system_status['python_version'] = version_ok
            
            version_str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            status_text = f"✅ {version_str}" if version_ok else f"❌ {version_str} (需要 {min_version[0]}.{min_version[1]}+)"
            status_color = self.colors['success'] if version_ok else self.colors['danger']
            
            self.check_items['python_version'].config(
                text=status_text,
                foreground=status_color
            )
            logging.info(f"Python版本检查: {version_str}, 结果: {'通过' if version_ok else '未通过'}")
        except Exception as e:
            self.system_status['python_version'] = False
            self.check_items['python_version'].config(
                text="❌ 检查失败",
                foreground=self.colors['danger']
            )
            logging.error(f"Python版本检查失败: {e}")
    
    def check_tkinter(self):
        """检查Tkinter"""
        try:
            import tkinter
            self.system_status['tkinter'] = True
            
            self.check_items['tkinter'].config(
                text="✅ 正常",
                foreground=self.colors['success']
            )
        except ImportError:
            self.system_status['tkinter'] = False
            self.check_items['tkinter'].config(
                text="❌ 未安装",
                foreground=self.colors['danger']
            )
    
    def check_modules(self):
        """检查功能模块"""
        try:
            modules = [
                'user_management/simple_user_manager.py',
                'score_statistics/simple_score_manager.py',
                'client/client_app.py',
                'exam_management/simple_exam_manager.py',
                'question_bank_web/app.py',
                'main_console.py'
            ]
            
            missing_modules = []
            for module in modules:
                if not os.path.exists(module):
                    missing_modules.append(module)
            
            if not missing_modules:
                self.system_status['modules'] = True
                self.check_items['modules'].config(
                    text="✅ 完整",
                    foreground=self.colors['success']
                )
                logging.info("模块检查: 所有模块完整")
            else:
                self.system_status['modules'] = False
                self.check_items['modules'].config(
                    text=f"❌ 缺失 {len(missing_modules)} 个",
                    foreground=self.colors['danger']
                )
                logging.warning(f"模块检查: 缺失 {len(missing_modules)} 个模块: {', '.join(missing_modules)}")
                
                # 显示缺失模块的详细信息
                if len(missing_modules) > 0:
                    missing_info = "\n".join(missing_modules)
                    messagebox.showwarning("模块缺失", f"以下模块文件缺失:\n\n{missing_info}\n\n请确保所有模块文件存在后再启动系统。")
        except Exception as e:
            self.system_status['modules'] = False
            self.check_items['modules'].config(
                text="❌ 检查失败",
                foreground=self.colors['danger']
            )
            logging.error(f"模块检查失败: {e}")
    
    def check_database(self):
        """检查数据库连接"""
        try:
            # 这里可以添加实际的数据库连接检查
            # 目前简单检查数据文件是否存在
            data_files = [
                'user_management/users.json',
                'score_statistics/scores.json'
            ]
            
            missing_files = []
            for file in data_files:
                if not os.path.exists(file):
                    missing_files.append(file)
            
            if not missing_files:
                self.system_status['database'] = True
                self.check_items['database'].config(
                    text="✅ 正常",
                    foreground=self.colors['success']
                )
            else:
                self.system_status['database'] = True  # 数据文件不存在不影响启动
                self.check_items['database'].config(
                    text="⚠️ 将创建默认数据",
                    foreground=self.colors['warning']
                )
        except Exception as e:
            self.system_status['database'] = True  # 检查失败不影响启动
            self.check_items['database'].config(
                text="⚠️ 检查失败",
                foreground=self.colors['warning']
            )
    
    def check_dependencies(self):
        """检查Python依赖项"""
        if not self.config.get("check_dependencies", True):
            self.system_status['dependencies'] = True
            return
            
        try:
            required_packages = [
                'flask', 'pandas', 'openpyxl', 'pillow', 'requests'
            ]
            
            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if not missing_packages:
                self.system_status['dependencies'] = True
                self.check_items['dependencies'].config(
                    text="✅ 已安装",
                    foreground=self.colors['success']
                )
                logging.info("依赖项检查: 所有依赖项已安装")
            else:
                self.system_status['dependencies'] = False
                self.check_items['dependencies'].config(
                    text=f"❌ 缺失 {len(missing_packages)} 个",
                    foreground=self.colors['danger']
                )
                logging.warning(f"依赖项检查: 缺失 {len(missing_packages)} 个包: {', '.join(missing_packages)}")
                
                # 提示安装缺失的依赖项
                if len(missing_packages) > 0:
                    if messagebox.askyesno("依赖项缺失", 
                                          f"以下Python包缺失:\n\n{', '.join(missing_packages)}\n\n是否自动安装这些依赖项？"):
                        self.install_dependencies(missing_packages)
        except Exception as e:
            self.system_status['dependencies'] = False
            self.check_items['dependencies'].config(
                text="❌ 检查失败",
                foreground=self.colors['danger']
            )
            logging.error(f"依赖项检查失败: {e}")
    
    def install_dependencies(self, packages):
        """安装缺失的依赖项，先官方源，失败再用清华镜像"""
        retry_count = 0
        success = False
        installed_packages = []
        pip_sources = [
            [sys.executable, "-m", "pip", "install"] + packages + ["-i", "https://pypi.org/simple/"],
            [sys.executable, "-m", "pip", "install"] + packages + ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple/"]
        ]
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("安装依赖项")
        progress_window.geometry("400x200")
        progress_window.resizable(False, False)
        tk.Label(progress_window, text="正在安装依赖项...", font=("Microsoft YaHei", 12)).pack(pady=10)
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        status_label = tk.Label(progress_window, text="", font=("Microsoft YaHei", 10))
        status_label.pack(pady=10)
        def update_progress(percent, message):
            progress_var.set(percent)
            status_label.config(text=message)
            progress_window.update()
        for cmd in pip_sources:
            retry_count += 1
            update_progress(0, f"尝试安装 (第 {retry_count} 源)...")
            try:
                with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                    process = subprocess.Popen(
                        cmd,
                        stdout=tmp,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        text=True
                    )
                    start_time = time.time()
                    while process.poll() is None:
                        elapsed = time.time() - start_time
                        progress = min(90, int(elapsed * 2))
                        update_progress(progress, f"正在安装依赖项({retry_count}/2)...")
                        time.sleep(0.5)
                    tmp.seek(0)
                    output_lines = tmp.readlines()
                if process.returncode == 0:
                    success = True
                    update_progress(100, "安装成功！")
                    for package in packages:
                        try:
                            __import__(package)
                            installed_packages.append(package)
                        except ImportError:
                            logging.error(f"安装后验证失败: {package}")
                    if len(installed_packages) == len(packages):
                        messagebox.showinfo("安装成功", "所有依赖项已成功安装并验证！\n请重新启动系统以应用更改。")
                        logging.info(f"依赖项安装成功: {', '.join(packages)}")
                        progress_window.destroy()
                        self.root.destroy()
                        return
                    else:
                        error_msg = f"部分包安装失败: {set(packages) - set(installed_packages)}"
                        update_progress(100, error_msg)
                        logging.error(error_msg)
                error_msg = '\n'.join(output_lines)
                update_progress(100, f"安装失败: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                update_progress(100, f"安装出错: {error_msg}")
                logging.error(f"安装尝试 {retry_count} 失败: {error_msg}")
            if success:
                break
            time.sleep(2)
        progress_window.destroy()
        # 提供手动安装指南
        manual_guide = f"""
无法自动安装依赖项，请手动安装：

1. 打开命令提示符/终端
2. 执行以下命令:
{sys.executable} -m pip install {' '.join(packages)}

如果提示权限不足:
- Windows: 以管理员身份运行命令提示符
- Mac/Linux: 在命令前加 sudo

常见问题解决:
1. 检查网络连接 (可尝试 ping pypi.org)
2. 确保Python环境正确 (当前使用: {sys.executable})
3. 可尝试单个安装: pip install 包名
4. 检查防火墙设置
5. 尝试使用国内镜像源:
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 包名
"""
        messagebox.showerror("安装失败", manual_guide)
        logging.error(f"所有安装尝试失败: {error_msg}")
    
    def check_disk_space(self):
        """检查磁盘空间"""
        try:
            required_space_mb = self.config.get("required_disk_space_mb", 100)
            free_mb = 0
            
            # 获取当前目录所在磁盘的可用空间
            if platform.system() == 'Windows':
                try:
                    free_bytes = ctypes.c_ulonglong(0)
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(os.getcwd()[:3]),
                                                              None, None, ctypes.pointer(free_bytes))
                    free_mb = free_bytes.value / (1024 * 1024)
                except Exception as e:
                    logging.warning(f"Windows磁盘空间检查失败: {e}")
                    free_mb = required_space_mb * 2  # 假设足够空间
            else:
                try:
                    st = os.statvfs(os.getcwd())
                    free_mb = st.f_bavail * st.f_frsize / (1024 * 1024)
                except AttributeError:  # 非Unix-like系统
                    logging.warning("当前平台不支持statvfs")
                    free_mb = required_space_mb * 2  # 假设足够空间
            
            space_ok = free_mb >= required_space_mb
            self.system_status['disk_space'] = space_ok
            
            if space_ok:
                self.check_items['disk_space'].config(
                    text=f"✅ {int(free_mb)} MB 可用",
                    foreground=self.colors['success']
                )
                logging.info(f"磁盘空间检查: {int(free_mb)} MB 可用, 结果: 通过")
            else:
                self.check_items['disk_space'].config(
                    text=f"❌ 仅 {int(free_mb)} MB 可用",
                    foreground=self.colors['danger']
                )
                logging.warning(f"磁盘空间检查: 仅 {int(free_mb)} MB 可用, 需要 {required_space_mb} MB")
        except Exception as e:
            # 如果检查失败，不影响系统启动
            self.system_status['disk_space'] = True
            self.check_items['disk_space'].config(
                text="⚠️ 检查失败",
                foreground=self.colors['warning']
            )
            logging.error(f"磁盘空间检查失败: {e}")
    
    def update_launch_button(self):
        """更新启动按钮状态"""
        # 检查关键组件是否正常
        critical_checks = ['python_version', 'tkinter', 'modules']
        all_ok = all(self.system_status[check] for check in critical_checks)
        
        if all_ok:
            self.launch_button.config(
                text="🚀 启动主控台",
                state="normal",
                bg=self.colors['success']
            )
            logging.info("系统检查通过，启动按钮已启用")
        else:
            self.launch_button.config(
                text="⚠️ 系统检查未通过",
                state="disabled",
                bg=self.colors['warning']
            )
            logging.warning("系统检查未通过，启动按钮已禁用")
    
    def launch_main_console(self):
        """启动主控台"""
        try:
            if os.path.exists('main_console.py'):
                logging.info("启动主控台")
                subprocess.Popen([sys.executable, 'main_console.py'])
                messagebox.showinfo("启动成功", "主控台已启动！")
                self.root.destroy()
            else:
                error_msg = "主控台文件未找到！"
                logging.error(error_msg)
                messagebox.showerror("错误", error_msg)
        except Exception as e:
            error_msg = f"启动主控台时发生错误：{e}"
            logging.error(error_msg)
            messagebox.showerror("启动失败", error_msg)
    
    def launch_question_bank(self):
        """启动题库管理"""
        try:
            flask_app_path = os.path.join('question_bank_web', 'app.py')
            if os.path.exists(flask_app_path):
                logging.info("启动题库管理")
                import webbrowser
                
                # 使用更可靠的启动方式
                def start_flask():
                    try:
                        command = f'start cmd /k "cd /d {os.path.join(os.getcwd(), "question_bank_web")} && {sys.executable} -m flask run"'
                        process = subprocess.Popen(command, shell=True)
                        
                        # 等待服务启动
                        time.sleep(3)
                        webbrowser.open("http://127.0.0.1:5000")
                        logging.info("题库管理Web界面已打开")
                    except Exception as e:
                        logging.error(f"启动Flask服务失败: {e}")
                
                threading.Thread(target=start_flask, daemon=True).start()
                messagebox.showinfo("启动成功", "题库管理已启动！\n\n如果浏览器未自动打开，请手动访问:\nhttp://127.0.0.1:5000")
            else:
                error_msg = "题库管理模块未找到！"
                logging.error(error_msg)
                messagebox.showerror("错误", error_msg)
        except Exception as e:
            error_msg = f"启动题库管理时发生错误：{e}"
            logging.error(error_msg)
            messagebox.showerror("启动失败", error_msg)
    
    def launch_user_management(self):
        """启动用户管理"""
        try:
            user_mgmt_path = 'user_management/simple_user_manager.py'
            if os.path.exists(user_mgmt_path):
                subprocess.Popen([sys.executable, user_mgmt_path])
                messagebox.showinfo("启动成功", "用户管理已启动！")
            else:
                messagebox.showerror("错误", "用户管理模块未找到！")
        except Exception as e:
            messagebox.showerror("启动失败", f"启动用户管理时发生错误：{e}")
    
    def launch_score_statistics(self):
        """启动成绩统计"""
        try:
            score_stats_path = 'score_statistics/simple_score_manager.py'
            if os.path.exists(score_stats_path):
                subprocess.Popen([sys.executable, score_stats_path])
                messagebox.showinfo("启动成功", "成绩统计已启动！")
            else:
                messagebox.showerror("错误", "成绩统计模块未找到！")
        except Exception as e:
            messagebox.showerror("启动失败", f"启动成绩统计时发生错误：{e}")
    
    def launch_exam_management(self):
        """启动考试管理"""
        try:
            exam_mgmt_path = 'exam_management/simple_exam_manager.py'
            if os.path.exists(exam_mgmt_path):
                subprocess.Popen([sys.executable, exam_mgmt_path])
                messagebox.showinfo("启动成功", "考试管理已启动！")
            else:
                messagebox.showerror("错误", "考试管理模块未找到！")
        except Exception as e:
            messagebox.showerror("启动失败", f"启动考试管理时发生错误：{e}")
    
    def launch_client(self):
        """启动客户机端"""
        try:
            client_path = 'client/client_app.py'
            if os.path.exists(client_path):
                subprocess.Popen([sys.executable, client_path])
                messagebox.showinfo("启动成功", "客户机端已启动！")
            else:
                messagebox.showerror("错误", "客户机端模块未找到！")
        except Exception as e:
            messagebox.showerror("启动失败", f"启动客户机端时发生错误：{e}")
    
    def run(self):
        """运行启动器"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        # 检查是否需要导入ctypes模块（用于磁盘空间检查）
        if platform.system() == 'Windows':
            import ctypes
            
        logging.info("=== 系统启动器开始运行 ===")
        launcher = SystemLauncher()
        launcher.run()
        logging.info("=== 系统启动器正常退出 ===\n")
    except Exception as e:
        logging.critical(f"系统启动器崩溃: {e}")
        print(f"系统启动器发生严重错误: {e}")
        # 在控制台显示错误信息
        import traceback
        traceback.print_exc()
        
        # 如果GUI已初始化，显示错误对话框
        try:
            messagebox.showerror("系统错误", f"启动器发生严重错误:\n\n{e}\n\n请查看日志文件了解详情。")
        except:
            pass