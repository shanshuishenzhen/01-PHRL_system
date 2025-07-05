#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PH&RL 考试系统 - 独立客户机端
完全独立运行，不依赖主控台，支持局域网服务器通信
"""

import tkinter as tk
import sys
import os
import time
import json
import logging
import requests
import sqlite3
from tkinter import messagebox, ttk
from datetime import datetime
import threading

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('standalone_client.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('standalone_client')

class StandaloneClientConfig:
    """独立客户端配置管理"""
    
    def __init__(self):
        self.config_file = 'client_config.json'
        self.default_config = {
            "server": {
                "host": "127.0.0.1",
                "port": 5000,
                "protocol": "http",
                "api_base": "/api"
            },
            "client": {
                "name": "PH&RL 考试客户端",
                "version": "2.0.0",
                "auto_save_interval": 30,
                "connection_timeout": 10,
                "retry_attempts": 3
            },
            "ui": {
                "fullscreen": True,
                "disable_shortcuts": True,
                "font_size": 12,
                "theme": "light"
            },
            "security": {
                "session_timeout": 3600,
                "anti_cheat": True
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                return self.merge_config(self.default_config, config)
            else:
                # 创建默认配置文件
                self.save_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return self.default_config.copy()
    
    def merge_config(self, default, user):
        """合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config=None):
        """保存配置文件"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
            logger.info("配置已保存")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def get_server_url(self):
        """获取服务器URL"""
        server = self.config['server']
        return f"{server['protocol']}://{server['host']}:{server['port']}{server.get('api_base', '')}"

class StandaloneAPI:
    """独立客户端API管理"""
    
    def __init__(self, config):
        self.config = config
        self.server_url = config.get_server_url()
        self.session = requests.Session()
        self.session.timeout = config.config['client']['connection_timeout']
        
    def test_connection(self):
        """测试服务器连接"""
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"服务器连接测试失败: {e}")
            return False
    
    def login(self, username, password):
        """用户登录"""
        try:
            data = {
                "username": username,
                "password": password
            }
            response = self.session.post(f"{self.server_url}/login", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"用户 {username} 登录成功")
                    return result.get('user_info')
            
            logger.warning(f"用户 {username} 登录失败")
            return None
            
        except Exception as e:
            logger.error(f"登录请求失败: {e}")
            return None
    
    def get_exams(self, user_id):
        """获取用户可参加的考试"""
        try:
            response = self.session.get(f"{self.server_url}/exams/user/{user_id}")
            
            if response.status_code == 200:
                result = response.json()
                return result.get('exams', [])
            
            return []
            
        except Exception as e:
            logger.error(f"获取考试列表失败: {e}")
            return []
    
    def get_exam_details(self, exam_id):
        """获取考试详情"""
        try:
            response = self.session.get(f"{self.server_url}/exams/{exam_id}")
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"获取考试详情失败: {e}")
            return None
    
    def submit_answers(self, exam_id, user_id, answers):
        """提交答案"""
        try:
            data = {
                "exam_id": exam_id,
                "user_id": user_id,
                "answers": answers,
                "submit_time": datetime.now().isoformat()
            }
            
            response = self.session.post(f"{self.server_url}/exams/{exam_id}/submit", json=data)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"答案提交成功: {exam_id}")
                return result
            
            logger.error(f"答案提交失败: HTTP {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"提交答案请求失败: {e}")
            return None

class ServerConfigDialog:
    """服务器配置对话框"""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("服务器配置")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
        
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="服务器配置", font=("Microsoft YaHei", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 服务器地址
        ttk.Label(main_frame, text="服务器地址:").pack(anchor='w')
        self.host_var = tk.StringVar(value=self.config.config['server']['host'])
        host_entry = ttk.Entry(main_frame, textvariable=self.host_var, width=30)
        host_entry.pack(fill='x', pady=(5, 10))
        
        # 端口
        ttk.Label(main_frame, text="端口:").pack(anchor='w')
        self.port_var = tk.StringVar(value=str(self.config.config['server']['port']))
        port_entry = ttk.Entry(main_frame, textvariable=self.port_var, width=30)
        port_entry.pack(fill='x', pady=(5, 10))
        
        # 协议
        ttk.Label(main_frame, text="协议:").pack(anchor='w')
        self.protocol_var = tk.StringVar(value=self.config.config['server']['protocol'])
        protocol_frame = ttk.Frame(main_frame)
        protocol_frame.pack(fill='x', pady=(5, 10))
        
        ttk.Radiobutton(protocol_frame, text="HTTP", variable=self.protocol_var, value="http").pack(side='left')
        ttk.Radiobutton(protocol_frame, text="HTTPS", variable=self.protocol_var, value="https").pack(side='left', padx=(20, 0))
        
        # 测试连接按钮
        test_button = ttk.Button(main_frame, text="测试连接", command=self.test_connection)
        test_button.pack(pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="", foreground="blue")
        self.status_label.pack(pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side='right')
        
    def test_connection(self):
        """测试连接"""
        self.status_label.config(text="正在测试连接...", foreground="blue")
        self.dialog.update()
        
        # 创建临时配置
        temp_config = self.config.config.copy()
        temp_config['server']['host'] = self.host_var.get()
        temp_config['server']['port'] = int(self.port_var.get())
        temp_config['server']['protocol'] = self.protocol_var.get()
        
        temp_config_obj = StandaloneClientConfig()
        temp_config_obj.config = temp_config
        
        # 测试连接
        api = StandaloneAPI(temp_config_obj)
        if api.test_connection():
            self.status_label.config(text="✅ 连接成功", foreground="green")
        else:
            self.status_label.config(text="❌ 连接失败", foreground="red")
    
    def ok_clicked(self):
        """确定按钮点击"""
        try:
            # 验证输入
            host = self.host_var.get().strip()
            port = int(self.port_var.get())
            protocol = self.protocol_var.get()
            
            if not host:
                messagebox.showerror("错误", "请输入服务器地址")
                return
            
            if not (1 <= port <= 65535):
                messagebox.showerror("错误", "端口号必须在1-65535之间")
                return
            
            # 更新配置
            self.config.config['server']['host'] = host
            self.config.config['server']['port'] = port
            self.config.config['server']['protocol'] = protocol
            
            self.result = True
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("错误", "端口号必须是数字")
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.result = False
        self.dialog.destroy()

class LoginFrame(ttk.Frame):
    """登录界面"""

    def __init__(self, parent, config, api, on_login_success):
        super().__init__(parent)
        self.config = config
        self.api = api
        self.on_login_success = on_login_success

        self.create_widgets()

    def create_widgets(self):
        """创建登录界面"""
        # 主框架
        main_frame = ttk.Frame(self, padding="50")
        main_frame.pack(expand=True, fill='both')

        # 标题
        title_label = ttk.Label(main_frame, text="PH&RL 考试系统", font=("Microsoft YaHei", 20, "bold"))
        title_label.pack(pady=(0, 30))

        # 登录表单
        form_frame = ttk.Frame(main_frame)
        form_frame.pack()

        # 用户名
        ttk.Label(form_frame, text="准考证号/身份证号:", font=("Microsoft YaHei", 12)).pack(anchor='w', pady=(0, 5))
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(form_frame, textvariable=self.username_var, font=("Microsoft YaHei", 12), width=25)
        username_entry.pack(pady=(0, 15))
        username_entry.focus()

        # 密码
        ttk.Label(form_frame, text="密码:", font=("Microsoft YaHei", 12)).pack(anchor='w', pady=(0, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(form_frame, textvariable=self.password_var, show="*", font=("Microsoft YaHei", 12), width=25)
        password_entry.pack(pady=(0, 20))

        # 绑定回车键
        username_entry.bind('<Return>', lambda e: password_entry.focus())
        password_entry.bind('<Return>', lambda e: self.login())

        # 登录按钮
        login_button = ttk.Button(form_frame, text="登录", command=self.login, width=20)
        login_button.pack(pady=(0, 10))

        # 服务器配置按钮
        config_button = ttk.Button(form_frame, text="服务器配置", command=self.show_server_config, width=20)
        config_button.pack()

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(20, 0))

        # 版本信息
        version_label = ttk.Label(main_frame, text=f"版本 {self.config.config['client']['version']}",
                                 font=("Microsoft YaHei", 9), foreground="gray")
        version_label.pack(side='bottom', pady=(20, 0))

    def login(self):
        """执行登录"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            self.status_label.config(text="请输入用户名和密码")
            return

        self.status_label.config(text="正在登录...", foreground="blue")
        self.update()

        # 在后台线程中执行登录
        def login_thread():
            user_info = self.api.login(username, password)

            # 在主线程中更新UI
            self.after(0, lambda: self.login_callback(user_info))

        threading.Thread(target=login_thread, daemon=True).start()

    def login_callback(self, user_info):
        """登录回调"""
        if user_info:
            self.status_label.config(text="登录成功", foreground="green")
            self.on_login_success(user_info)
        else:
            self.status_label.config(text="登录失败，请检查用户名和密码", foreground="red")

    def show_server_config(self):
        """显示服务器配置对话框"""
        dialog = ServerConfigDialog(self.winfo_toplevel(), self.config)
        self.wait_window(dialog.dialog)

        if dialog.result:
            # 保存配置
            self.config.save_config()
            # 更新API
            self.api.server_url = self.config.get_server_url()
            messagebox.showinfo("成功", "服务器配置已更新")

class ExamListFrame(ttk.Frame):
    """考试列表界面"""

    def __init__(self, parent, config, api, user_info, on_exam_selected, on_logout):
        super().__init__(parent)
        self.config = config
        self.api = api
        self.user_info = user_info
        self.on_exam_selected = on_exam_selected
        self.on_logout = on_logout
        self.exams = []

        self.create_widgets()
        self.load_exams()

    def create_widgets(self):
        """创建考试列表界面"""
        # 顶部框架
        top_frame = ttk.Frame(self, padding="20")
        top_frame.pack(fill='x')

        # 用户信息
        user_label = ttk.Label(top_frame, text=f"欢迎，{self.user_info.get('username', '考生')}",
                              font=("Microsoft YaHei", 14))
        user_label.pack(side='left')

        # 退出按钮
        logout_button = ttk.Button(top_frame, text="退出", command=self.on_logout)
        logout_button.pack(side='right')

        # 刷新按钮
        refresh_button = ttk.Button(top_frame, text="刷新", command=self.load_exams)
        refresh_button.pack(side='right', padx=(0, 10))

        # 考试列表框架
        list_frame = ttk.Frame(self, padding="20")
        list_frame.pack(fill='both', expand=True)

        # 标题
        title_label = ttk.Label(list_frame, text="可参加的考试", font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 考试列表
        self.exam_listbox = tk.Listbox(list_frame, font=("Microsoft YaHei", 12), height=10)
        self.exam_listbox.pack(fill='both', expand=True, pady=(0, 20))
        self.exam_listbox.bind('<Double-Button-1>', self.on_exam_double_click)

        # 按钮框架
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill='x')

        # 开始考试按钮
        start_button = ttk.Button(button_frame, text="开始考试", command=self.start_exam)
        start_button.pack(side='right')

        # 查看详情按钮
        detail_button = ttk.Button(button_frame, text="查看详情", command=self.show_exam_detail)
        detail_button.pack(side='right', padx=(0, 10))

        # 状态标签
        self.status_label = ttk.Label(list_frame, text="", foreground="blue")
        self.status_label.pack(pady=(10, 0))

    def load_exams(self):
        """加载考试列表"""
        self.status_label.config(text="正在加载考试列表...", foreground="blue")
        self.update()

        def load_thread():
            exams = self.api.get_exams(self.user_info['id'])
            self.after(0, lambda: self.load_exams_callback(exams))

        threading.Thread(target=load_thread, daemon=True).start()

    def load_exams_callback(self, exams):
        """加载考试列表回调"""
        self.exams = exams
        self.exam_listbox.delete(0, tk.END)

        if exams:
            for exam in exams:
                exam_text = f"{exam.get('name', '未知考试')} - {exam.get('duration', '未知')}分钟"
                self.exam_listbox.insert(tk.END, exam_text)
            self.status_label.config(text=f"找到 {len(exams)} 个可参加的考试", foreground="green")
        else:
            self.status_label.config(text="暂无可参加的考试", foreground="orange")

    def on_exam_double_click(self, event):
        """考试双击事件"""
        self.start_exam()

    def start_exam(self):
        """开始考试"""
        selection = self.exam_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请选择一个考试")
            return

        exam = self.exams[selection[0]]

        # 确认开始考试
        result = messagebox.askyesno("确认", f"确定要开始考试：{exam.get('name')}？\n\n考试开始后将进入全屏模式，请确保准备就绪。")
        if result:
            self.on_exam_selected(exam)

    def show_exam_detail(self):
        """显示考试详情"""
        selection = self.exam_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请选择一个考试")
            return

        exam = self.exams[selection[0]]

        detail_text = f"""考试名称：{exam.get('name', '未知')}
考试时长：{exam.get('duration', '未知')}分钟
题目数量：{exam.get('question_count', '未知')}题
总分：{exam.get('total_score', '未知')}分
及格分：{exam.get('pass_score', '未知')}分

考试说明：
{exam.get('description', '暂无说明')}"""

        messagebox.showinfo("考试详情", detail_text)

class ExamFrame(ttk.Frame):
    """考试界面"""

    def __init__(self, parent, config, api, user_info, exam_info, on_exam_finished):
        super().__init__(parent)
        self.config = config
        self.api = api
        self.user_info = user_info
        self.exam_info = exam_info
        self.on_exam_finished = on_exam_finished

        self.questions = []
        self.current_question_index = 0
        self.answers = {}
        self.start_time = time.time()
        self.end_time = None

        self.create_widgets()
        self.load_exam_details()

    def create_widgets(self):
        """创建考试界面"""
        # 顶部信息栏
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill='x')

        # 考试信息
        self.exam_label = ttk.Label(top_frame, text=f"考试：{self.exam_info.get('name', '未知考试')}",
                                   font=("Microsoft YaHei", 12, "bold"))
        self.exam_label.pack(side='left')

        # 时间显示
        self.time_label = ttk.Label(top_frame, text="剩余时间：计算中...",
                                   font=("Microsoft YaHei", 12), foreground="red")
        self.time_label.pack(side='right')

        # 题目导航
        nav_frame = ttk.Frame(self, padding="10")
        nav_frame.pack(fill='x')

        self.nav_label = ttk.Label(nav_frame, text="题目 0 / 0", font=("Microsoft YaHei", 12))
        self.nav_label.pack(side='left')

        # 题目内容区域
        self.question_frame = ttk.Frame(self, padding="20")
        self.question_frame.pack(fill='both', expand=True)

        # 底部按钮
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill='x')

        self.prev_button = ttk.Button(button_frame, text="上一题", command=self.prev_question, state='disabled')
        self.prev_button.pack(side='left')

        self.next_button = ttk.Button(button_frame, text="下一题", command=self.next_question, state='disabled')
        self.next_button.pack(side='left', padx=(10, 0))

        self.submit_button = ttk.Button(button_frame, text="交卷", command=self.submit_exam)
        self.submit_button.pack(side='right')

        # 状态标签
        self.status_label = ttk.Label(self, text="正在加载考试...", foreground="blue")
        self.status_label.pack(pady=10)

    def load_exam_details(self):
        """加载考试详情"""
        def load_thread():
            exam_details = self.api.get_exam_details(self.exam_info['id'])
            self.after(0, lambda: self.load_exam_details_callback(exam_details))

        threading.Thread(target=load_thread, daemon=True).start()

    def load_exam_details_callback(self, exam_details):
        """加载考试详情回调"""
        if exam_details and exam_details.get('questions'):
            self.questions = exam_details['questions']
            self.end_time = self.start_time + (exam_details.get('duration', 60) * 60)

            self.status_label.config(text=f"考试加载成功，共 {len(self.questions)} 道题", foreground="green")
            self.show_question()
            self.update_timer()

            # 启用按钮
            if len(self.questions) > 1:
                self.next_button.config(state='normal')
        else:
            self.status_label.config(text="考试加载失败", foreground="red")
            messagebox.showerror("错误", "无法加载考试内容，请联系管理员")

    def show_question(self):
        """显示当前题目"""
        if not self.questions:
            return

        # 清空题目区域
        for widget in self.question_frame.winfo_children():
            widget.destroy()

        question = self.questions[self.current_question_index]
        q_id = question.get('id')
        q_type = question.get('type')
        q_content = question.get('content', '')
        q_options = question.get('options', [])

        # 更新导航
        self.nav_label.config(text=f"题目 {self.current_question_index + 1} / {len(self.questions)}")

        # 题目标题
        type_names = {
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'true_false': '判断题',
            'fill_blank': '填空题',
            'short_answer': '简答题',
            'essay': '论述题'
        }

        title_text = f"{self.current_question_index + 1}. [{type_names.get(q_type, '未知题型')}] {q_content}"
        title_label = ttk.Label(self.question_frame, text=title_text, font=("Microsoft YaHei", 12),
                               wraplength=600, justify='left')
        title_label.pack(anchor='w', pady=(0, 20))

        # 根据题型创建答题区域
        if q_type in ['single_choice', 'true_false']:
            self.create_single_choice(q_id, q_options)
        elif q_type == 'multiple_choice':
            self.create_multiple_choice(q_id, q_options)
        elif q_type == 'fill_blank':
            self.create_fill_blank(q_id)
        elif q_type in ['short_answer', 'essay']:
            self.create_text_answer(q_id, q_type == 'essay')

        # 更新按钮状态
        self.prev_button.config(state='normal' if self.current_question_index > 0 else 'disabled')
        self.next_button.config(state='normal' if self.current_question_index < len(self.questions) - 1 else 'disabled')

    def create_single_choice(self, q_id, options):
        """创建单选题"""
        # 判断题特殊处理
        if not options:
            options = ['正确', '错误']

        var = tk.StringVar()
        if q_id in self.answers:
            var.set(self.answers[q_id])

        for i, option in enumerate(options):
            rb = ttk.Radiobutton(self.question_frame, text=f"{chr(65+i)}. {option}",
                               variable=var, value=option,
                               command=lambda: self.save_answer(q_id, var.get()))
            rb.pack(anchor='w', pady=5)

        self.answers[q_id] = var

    def create_multiple_choice(self, q_id, options):
        """创建多选题"""
        if q_id not in self.answers:
            self.answers[q_id] = {}

        for i, option in enumerate(options):
            var = tk.BooleanVar()
            if option in self.answers[q_id]:
                var.set(self.answers[q_id][option])

            cb = ttk.Checkbutton(self.question_frame, text=f"{chr(65+i)}. {option}",
                               variable=var,
                               command=lambda o=option, v=var: self.save_multiple_answer(q_id, o, v.get()))
            cb.pack(anchor='w', pady=5)

            self.answers[q_id][option] = var

    def create_fill_blank(self, q_id):
        """创建填空题"""
        entry = ttk.Entry(self.question_frame, font=("Microsoft YaHei", 12), width=50)
        entry.pack(anchor='w', pady=10)

        if q_id in self.answers:
            entry.insert(0, self.answers[q_id])

        entry.bind('<KeyRelease>', lambda e: self.save_answer(q_id, entry.get()))
        self.answers[q_id] = entry

    def create_text_answer(self, q_id, is_essay=False):
        """创建文本答题区域"""
        height = 15 if is_essay else 8
        text_widget = tk.Text(self.question_frame, font=("Microsoft YaHei", 12),
                             width=70, height=height, wrap='word')
        text_widget.pack(anchor='w', pady=10, fill='both', expand=True)

        if q_id in self.answers:
            text_widget.insert('1.0', self.answers[q_id])

        text_widget.bind('<KeyRelease>', lambda e: self.save_answer(q_id, text_widget.get('1.0', 'end-1c')))
        self.answers[q_id] = text_widget

    def save_answer(self, q_id, answer):
        """保存答案"""
        self.answers[q_id] = answer

    def save_multiple_answer(self, q_id, option, selected):
        """保存多选题答案"""
        if q_id not in self.answers:
            self.answers[q_id] = {}
        self.answers[q_id][option] = selected

    def prev_question(self):
        """上一题"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()

    def next_question(self):
        """下一题"""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.show_question()

    def update_timer(self):
        """更新计时器"""
        if self.end_time:
            remaining = int(self.end_time - time.time())
            if remaining > 0:
                minutes, seconds = divmod(remaining, 60)
                self.time_label.config(text=f"剩余时间：{minutes:02d}:{seconds:02d}")
                self.after(1000, self.update_timer)
            else:
                self.time_label.config(text="时间到！")
                self.submit_exam(auto_submit=True)

    def submit_exam(self, auto_submit=False):
        """提交考试"""
        if not auto_submit:
            result = messagebox.askyesno("确认", "确定要提交考试吗？提交后无法修改。")
            if not result:
                return

        # 整理答案
        final_answers = {}
        for q_id, answer in self.answers.items():
            if isinstance(answer, tk.StringVar):
                final_answers[q_id] = answer.get()
            elif isinstance(answer, dict):
                # 多选题
                selected = [opt for opt, var in answer.items() if var.get()]
                final_answers[q_id] = selected
            elif isinstance(answer, (tk.Entry, tk.Text)):
                final_answers[q_id] = answer.get() if isinstance(answer, tk.Entry) else answer.get('1.0', 'end-1c')
            else:
                final_answers[q_id] = str(answer)

        self.status_label.config(text="正在提交答案...", foreground="blue")

        def submit_thread():
            result = self.api.submit_answers(self.exam_info['id'], self.user_info['id'], final_answers)
            self.after(0, lambda: self.submit_callback(result, auto_submit))

        threading.Thread(target=submit_thread, daemon=True).start()

    def submit_callback(self, result, auto_submit):
        """提交回调"""
        if result:
            message = "考试已自动提交！" if auto_submit else "考试提交成功！"
            messagebox.showinfo("提交成功", message)
            self.on_exam_finished()
        else:
            self.status_label.config(text="提交失败，请重试", foreground="red")
            if not auto_submit:
                messagebox.showerror("提交失败", "网络错误，请检查网络连接后重试")

class StandaloneExamClient(tk.Tk):
    """独立考试客户端主应用"""

    def __init__(self):
        super().__init__()

        # 基本设置
        self.title("PH&RL 考试系统 - 独立客户端")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # 初始化组件
        self.config = StandaloneClientConfig()
        self.api = StandaloneAPI(self.config)
        self.current_frame = None
        self.user_info = None
        self.is_fullscreen = False

        # 设置图标（如果有的话）
        try:
            # self.iconbitmap('icon.ico')  # 如果有图标文件
            pass
        except:
            pass

        # 设置关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 显示登录界面
        self.show_login()

        logger.info("独立客户端启动成功")

    def show_login(self):
        """显示登录界面"""
        self.clear_frame()
        self.current_frame = LoginFrame(self, self.config, self.api, self.on_login_success)
        self.current_frame.pack(fill='both', expand=True)

        # 退出全屏模式
        if self.is_fullscreen:
            self.attributes('-fullscreen', False)
            self.is_fullscreen = False

    def on_login_success(self, user_info):
        """登录成功回调"""
        self.user_info = user_info
        logger.info(f"用户 {user_info.get('username')} 登录成功")
        self.show_exam_list()

    def show_exam_list(self):
        """显示考试列表"""
        self.clear_frame()
        self.current_frame = ExamListFrame(self, self.config, self.api, self.user_info,
                                         self.on_exam_selected, self.on_logout)
        self.current_frame.pack(fill='both', expand=True)

    def on_exam_selected(self, exam_info):
        """考试选择回调"""
        logger.info(f"开始考试: {exam_info.get('name')}")

        # 进入全屏模式
        if self.config.config['ui']['fullscreen']:
            self.attributes('-fullscreen', True)
            self.is_fullscreen = True

        # 显示考试界面
        self.clear_frame()
        self.current_frame = ExamFrame(self, self.config, self.api, self.user_info,
                                     exam_info, self.on_exam_finished)
        self.current_frame.pack(fill='both', expand=True)

        # 绑定防作弊快捷键
        if self.config.config['security']['anti_cheat']:
            self.bind_anti_cheat_keys()

    def on_exam_finished(self):
        """考试完成回调"""
        logger.info("考试完成")

        # 退出全屏模式
        if self.is_fullscreen:
            self.attributes('-fullscreen', False)
            self.is_fullscreen = False

        # 解除快捷键绑定
        self.unbind_anti_cheat_keys()

        # 返回考试列表
        self.show_exam_list()

    def on_logout(self):
        """退出登录"""
        self.user_info = None
        logger.info("用户退出登录")
        self.show_login()

    def clear_frame(self):
        """清空当前框架"""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None

    def bind_anti_cheat_keys(self):
        """绑定防作弊快捷键"""
        try:
            # 禁用常见的切换快捷键
            self.bind('<Alt-Tab>', lambda e: 'break')
            self.bind('<Control-Alt-Delete>', lambda e: 'break')
            self.bind('<Alt-F4>', lambda e: 'break')
            self.bind('<Control-Shift-Escape>', lambda e: 'break')
            self.bind('<Control-Escape>', lambda e: 'break')

            # 调试用退出快捷键
            self.bind('<Control-Shift-D>', self.debug_exit)

            logger.info("防作弊快捷键已绑定")
        except Exception as e:
            logger.error(f"绑定防作弊快捷键失败: {e}")

    def unbind_anti_cheat_keys(self):
        """解除防作弊快捷键绑定"""
        try:
            self.unbind('<Alt-Tab>')
            self.unbind('<Control-Alt-Delete>')
            self.unbind('<Alt-F4>')
            self.unbind('<Control-Shift-Escape>')
            self.unbind('<Control-Escape>')
            self.unbind('<Control-Shift-D>')

            logger.info("防作弊快捷键已解除")
        except Exception as e:
            logger.error(f"解除防作弊快捷键失败: {e}")

    def debug_exit(self, event=None):
        """调试用退出"""
        result = messagebox.askyesno("调试退出", "确定要退出防作弊模式吗？\n\n这将结束当前考试。")
        if result:
            self.on_exam_finished()

    def on_closing(self):
        """窗口关闭事件"""
        if self.current_frame and isinstance(self.current_frame, ExamFrame):
            # 如果正在考试，询问是否确定退出
            result = messagebox.askyesno("确认退出", "正在进行考试，确定要退出吗？\n\n退出将丢失未保存的答案。")
            if not result:
                return

        logger.info("客户端正在关闭")
        self.destroy()

def main():
    """主函数"""
    try:
        # 创建并运行应用
        app = StandaloneExamClient()
        app.mainloop()

    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        messagebox.showerror("启动错误", f"应用启动失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
