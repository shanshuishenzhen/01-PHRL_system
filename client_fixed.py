#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版客户端 - 包含登录验证和防作弊功能
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import time
import threading
import logging

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'client'))

import api

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginView(tk.Frame):
    """登录视图"""
    def __init__(self, master, show_exam_list_callback):
        super().__init__(master)
        self.show_exam_list = show_exam_list_callback

        # 颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'light': '#C73E1D',
            'white': '#FFFFFF',
            'light_gray': '#F5F5F5',
            'dark': '#333333'
        }

        # 设置背景色
        self.configure(bg=self.colors['light'])

        # 创建登录卡片
        self.create_login_card()

    def create_login_card(self):
        """创建登录卡片"""
        # 登录卡片容器
        card_frame = tk.Frame(
            self,
            bg=self.colors['white'],
            relief='raised',
            borderwidth=2
        )
        card_frame.place(relx=0.5, rely=0.5, anchor='center', width=400, height=500)

        # 标题
        title_label = tk.Label(
            card_frame,
            text="🎓 考试系统登录",
            font=("Microsoft YaHei", 18, "bold"),
            bg=self.colors['white'],
            fg=self.colors['primary']
        )
        title_label.pack(pady=(30, 20))

        # 表单区域
        form_frame = tk.Frame(card_frame, bg=self.colors['white'])
        form_frame.pack(fill=tk.X, padx=40)

        # 用户名输入
        tk.Label(
            form_frame,
            text="准考证号/身份证号:",
            font=("Microsoft YaHei", 12),
            bg=self.colors['white'],
            fg=self.colors['dark']
        ).pack(anchor='w', pady=(0, 5))

        self.username_entry = tk.Entry(
            form_frame,
            font=("Microsoft YaHei", 12),
            relief='solid',
            borderwidth=1
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 20))

        # 密码输入
        tk.Label(
            form_frame,
            text="密码:",
            font=("Microsoft YaHei", 12),
            bg=self.colors['white'],
            fg=self.colors['dark']
        ).pack(anchor='w', pady=(0, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=("Microsoft YaHei", 12),
            show="*",
            relief='solid',
            borderwidth=1
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 30))

        # 登录按钮
        button_frame = tk.Frame(form_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=30)

        login_button = tk.Button(
            button_frame,
            text="🚀 登 录",
            command=self.handle_login,
            width=20,
            height=2,
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['secondary'],
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )
        login_button.pack()

        # 底部信息
        info_frame = tk.Frame(card_frame, bg=self.colors['white'])
        info_frame.pack(fill=tk.X, pady=(0, 20))

        info_label = tk.Label(
            info_frame,
            text="请使用您的准考证号或身份证号登录",
            font=("Microsoft YaHei", 10),
            bg=self.colors['white'],
            fg=self.colors['dark']
        )
        info_label.pack()

        # 绑定回车键
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        self.password_entry.bind('<Return>', lambda e: self.handle_login())

    def handle_login(self):
        """处理登录"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("错误", "准考证号/身份证号和密码不能为空！")
            return

        # 首先尝试API登录验证
        try:
            user_info = api.login(username, password)
        except Exception as e:
            print(f"API登录验证失败: {e}")
            user_info = None

        # 如果API登录失败，尝试直接验证用户身份
        if not user_info:
            user_info = self.verify_user_credentials(username, password)

        if user_info:
            print(f"登录成功: {user_info}")
            messagebox.showinfo("登录成功", f"欢迎，{user_info.get('name', username)}！")
            self.show_exam_list(user_info)
        else:
            messagebox.showerror("登录失败", "用户名或密码错误，请重试！")

    def verify_user_credentials(self, username, password):
        """验证用户凭据"""
        try:
            # 这里可以添加本地用户验证逻辑
            # 暂时使用简单的测试账号
            test_users = {
                'test': {'password': '123456', 'name': '测试用户', 'id': 'test_001'},
                'student': {'password': '123456', 'name': '学生用户', 'id': 'student_001'},
                'admin': {'password': 'admin123', 'name': '管理员', 'id': 'admin_001'}
            }

            if username in test_users and test_users[username]['password'] == password:
                return {
                    'username': username,
                    'name': test_users[username]['name'],
                    'id': test_users[username]['id']
                }

            return None

        except Exception as e:
            print(f"验证用户凭据时出错: {e}")
            return None

class ExamListView(tk.Frame):
    """考试列表视图"""
    def __init__(self, master, user_info, show_exam_callback):
        super().__init__(master)
        self.user_info = user_info
        self.show_exam_callback = show_exam_callback

        # 颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'light': '#C73E1D',
            'white': '#FFFFFF',
            'light_gray': '#F5F5F5',
            'dark': '#333333'
        }

        self.configure(bg=self.colors['white'])
        self.create_exam_list()

    def create_exam_list(self):
        """创建考试列表"""
        # 标题栏
        title_frame = tk.Frame(self, bg=self.colors['primary'], height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text=f"欢迎，{self.user_info.get('name', '用户')}！请选择考试",
            font=("Microsoft YaHei", 16, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.pack(expand=True)

        # 考试列表区域
        list_frame = tk.Frame(self, bg=self.colors['white'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # 获取真实的已发布考试
        exams = self.get_available_exams()

        if not exams:
            # 如果没有考试，显示提示信息
            no_exam_label = tk.Label(
                list_frame,
                text="📝 暂无可参加的考试\n\n请联系管理员确认考试发布状态",
                font=("Microsoft YaHei", 14),
                bg=self.colors['white'],
                fg=self.colors['dark'],
                justify=tk.CENTER
            )
            no_exam_label.pack(expand=True)
        else:
            for exam in exams:
                self.create_exam_card(list_frame, exam)

    def get_available_exams(self):
        """获取可用考试列表"""
        try:
            import api

            student_id = self.user_info.get('id', 'test_student')

            # 首先尝试获取已发布考试
            published_exams = api.get_published_exams_for_student(student_id)
            print(f"📋 为学生 {student_id} 找到 {len(published_exams)} 个已发布考试")

            if published_exams:
                return published_exams

            # 如果没有已发布考试，获取所有可用考试
            print("⚠️ 未找到已发布考试，尝试获取所有可用考试")
            all_exams = api.get_exams_for_student(student_id, self.user_info)
            print(f"📋 找到 {len(all_exams)} 个可用考试")

            return all_exams

        except Exception as e:
            print(f"❌ 获取可用考试失败: {e}")
            import traceback
            traceback.print_exc()

            # 回退到模拟数据
            return [
                {'id': 'exam_001', 'name': '计算机基础知识测试（模拟）', 'time_limit': 60, 'questions': 20},
                {'id': 'exam_002', 'name': '数学能力测试（模拟）', 'time_limit': 90, 'questions': 30}
            ]

    def create_exam_card(self, parent, exam):
        """创建考试卡片"""
        card_frame = tk.Frame(
            parent,
            bg=self.colors['light_gray'],
            relief='raised',
            borderwidth=1
        )
        card_frame.pack(fill='x', pady=10)

        # 考试信息
        info_frame = tk.Frame(card_frame, bg=self.colors['light_gray'])
        info_frame.pack(side='left', fill='both', expand=True, padx=20, pady=15)

        # 考试名称 - 兼容不同字段名
        exam_name = exam.get('name') or exam.get('title', '未知考试')
        name_label = tk.Label(
            info_frame,
            text=exam_name,
            font=("Microsoft YaHei", 14, "bold"),
            bg=self.colors['light_gray'],
            fg=self.colors['dark']
        )
        name_label.pack(anchor='w')

        # 考试详情 - 兼容不同字段名
        duration = exam.get('time_limit') or exam.get('duration', '未设置')
        questions_count = exam.get('questions', 0)
        if isinstance(questions_count, list):
            questions_count = len(questions_count)

        details_text = f"考试时长: {duration}分钟"
        if questions_count:
            details_text += f" | 题目数量: {questions_count}题"

        # 添加考试状态
        status = exam.get('status', '未知')
        if status:
            details_text += f" | 状态: {status}"

        details_label = tk.Label(
            info_frame,
            text=details_text,
            font=("Microsoft YaHei", 10),
            bg=self.colors['light_gray'],
            fg=self.colors['dark']
        )
        details_label.pack(anchor='w', pady=(5, 0))

        # 考试描述（如果有）
        description = exam.get('description', '')
        if description:
            desc_label = tk.Label(
                info_frame,
                text=f"描述: {description}",
                font=("Microsoft YaHei", 9),
                bg=self.colors['light_gray'],
                fg=self.colors['dark'],
                wraplength=400
            )
            desc_label.pack(anchor='w', pady=(2, 0))

        # 开始按钮
        button_frame = tk.Frame(card_frame, bg=self.colors['light_gray'])
        button_frame.pack(side='right', padx=20, pady=15)

        start_button = tk.Button(
            button_frame,
            text="开始考试",
            command=lambda: self.start_exam(exam),
            font=("Microsoft YaHei", 12, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['white'],
            width=12,
            height=2,
            cursor="hand2"
        )
        start_button.pack()

    def start_exam(self, exam):
        """开始考试"""
        result = messagebox.askyesno(
            "开始考试",
            f"确定要开始考试：{exam['name']} 吗？\n\n"
            "注意事项：\n"
            "• 考试将以全屏模式进行\n"
            "• 请勿切换到其他应用程序\n"
            "• 请勿关闭浏览器或应用\n"
            "• 考试过程中将监控您的操作\n"
            "• 按 Ctrl+Shift+D 可退出防作弊模式（调试用）\n\n"
            "确定要开始考试吗？"
        )

        if result:
            try:
                # 启用防切屏和防作弊功能
                self.master.enable_anti_cheat_mode()

                # 进入全屏模式
                self.master.attributes('-fullscreen', True)
                self.master.attributes('-topmost', True)

                print(f"开始考试: {exam['name']}")

                # 显示考试页面
                self.show_exam_callback(self.user_info, exam)

            except Exception as e:
                print(f"进入考试失败: {e}")
                messagebox.showerror("错误", f"进入考试失败: {str(e)}")
                # 如果失败，退出防作弊模式
                self.master.disable_anti_cheat_mode()

class FixedExamClient(tk.Tk):
    """修复版考试客户端主应用"""
    def __init__(self):
        try:
            super().__init__()
            self.title("PH&RL 考试系统 - 客户机（修复版）")
            self.geometry("1000x700")
            self.current_frame = None
            self.user_info = None
            self.is_fullscreen = False
            self.anti_cheat_enabled = False

            # 颜色配置
            self.colors = {
                'primary': '#2E86AB',
                'secondary': '#A23B72',
                'accent': '#F18F01',
                'light': '#C73E1D',
                'white': '#FFFFFF',
                'light_gray': '#F5F5F5',
                'dark': '#333333'
            }

            self.configure(bg=self.colors['white'])

            # 显示登录视图
            self.show_login_view()

        except Exception as e:
            logger.critical(f"客户端初始化失败: {e}")
            messagebox.showerror("致命错误", f"客户端初始化失败: {e}")
            sys.exit(1)

    def show_login_view(self):
        """显示登录视图"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginView(
            self,
            show_exam_list_callback=self.show_exam_list
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_exam_list(self, user_info):
        """显示考试列表"""
        self.user_info = user_info
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ExamListView(
            master=self,
            user_info=self.user_info,
            show_exam_callback=self.show_exam_page
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_exam_page(self, user_info, exam):
        """显示考试页面"""
        self.user_info = user_info
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ExamPageView(
            master=self,
            user_info=self.user_info,
            exam=exam
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def enable_anti_cheat_mode(self):
        """启用防作弊模式"""
        print("启用防作弊模式...")
        self.anti_cheat_enabled = True

        # 添加调试退出接口 - Ctrl+Shift+D 退出防作弊模式
        self.bind('<Control-Shift-D>', self.debug_exit_anti_cheat)

        # 禁用Alt+Tab等快捷键
        self.bind('<Alt-Tab>', lambda e: 'break')
        self.bind('<Control-Alt-Delete>', lambda e: 'break')
        self.bind('<Control-Shift-Escape>', lambda e: 'break')
        self.bind('<Alt-F4>', lambda e: 'break')
        self.bind('<Control-w>', lambda e: 'break')
        self.bind('<Control-q>', lambda e: 'break')

        # 禁用右键菜单
        self.bind('<Button-3>', lambda e: 'break')

        # 监控窗口焦点变化
        self.bind('<FocusOut>', self.on_focus_lost)
        self.bind('<FocusIn>', self.on_focus_gained)

        # 设置全屏和置顶
        self.attributes('-fullscreen', True)
        self.attributes('-topmost', True)

        print("防作弊模式已启用")
        print("调试提示: 按 Ctrl+Shift+D 可退出防作弊模式")

    def debug_exit_anti_cheat(self, event):
        """调试用：退出防作弊模式"""
        print("调试模式：退出防作弊模式")

        # 显示确认对话框
        result = messagebox.askyesno(
            "调试模式",
            "确定要退出防作弊模式吗？\n\n"
            "这将退出全屏模式并恢复正常操作。\n"
            "此功能仅用于调试目的。"
        )

        if result:
            self.disable_anti_cheat_mode()
            messagebox.showinfo("调试模式", "已退出防作弊模式")

    def disable_anti_cheat_mode(self):
        """禁用防作弊模式"""
        print("禁用防作弊模式...")
        self.anti_cheat_enabled = False

        # 恢复正常模式
        self.attributes('-fullscreen', False)
        self.attributes('-topmost', False)

        # 解除事件绑定
        try:
            self.unbind('<Alt-Tab>')
            self.unbind('<Control-Alt-Delete>')
            self.unbind('<Control-Shift-Escape>')
            self.unbind('<Alt-F4>')
            self.unbind('<Control-w>')
            self.unbind('<Control-q>')
            self.unbind('<FocusOut>')
            self.unbind('<FocusIn>')
            self.unbind('<Button-3>')
            self.unbind('<Control-Shift-D>')
        except Exception as e:
            print(f"解除事件绑定时出错: {e}")

        print("防作弊模式已禁用")

    def on_focus_lost(self, event):
        """窗口失去焦点时的处理"""
        if self.anti_cheat_enabled:
            print(f"警告：检测到窗口失去焦点")
            # 可以在这里添加更多的防作弊逻辑

    def on_focus_gained(self, event):
        """窗口获得焦点时的处理"""
        if self.anti_cheat_enabled:
            print(f"窗口重新获得焦点")

class ExamPageView(tk.Frame):
    """考试页面视图"""
    def __init__(self, master, user_info, exam):
        super().__init__(master)
        self.user_info = user_info
        self.exam = exam

        # 颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'accent': '#F18F01',
            'light': '#C73E1D',
            'white': '#FFFFFF',
            'light_gray': '#F5F5F5',
            'dark': '#333333'
        }

        # 数据
        self.questions = []
        self.current_question_index = 0
        self.answers = {}
        self.exam_details = None
        self.start_time = time.time()  # 记录开始时间
        self.exam_id = exam.get('id', f"exam_{int(time.time())}")
        self.student_id = user_info.get('id', 'test_student')
        self.student_name = user_info.get('name', '测试学生')

        self.configure(bg=self.colors['white'])

        self.setup_ui()
        self.load_test_exam()
    
    def setup_ui(self):
        """设置界面"""
        # 标题栏
        title_frame = tk.Frame(self, bg=self.colors['primary'], height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="考试客户端 - 修复版",
            font=("Microsoft YaHei", 16, "bold"),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.pack(expand=True)
        
        # 导航信息
        nav_frame = tk.Frame(self, bg=self.colors['light_gray'], height=40)
        nav_frame.pack(fill='x')
        nav_frame.pack_propagate(False)
        
        self.nav_label = tk.Label(
            nav_frame,
            text="第 1 / 0 题",
            font=("Microsoft YaHei", 12),
            bg=self.colors['light_gray'],
            fg=self.colors['dark']
        )
        self.nav_label.pack(expand=True)
        
        # 题目显示区域
        self.question_frame = tk.Frame(self, bg=self.colors['white'])
        self.question_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 按钮区域
        button_frame = tk.Frame(self, bg=self.colors['white'], height=60)
        button_frame.pack(fill='x', pady=10)
        button_frame.pack_propagate(False)
        
        # 按钮容器
        btn_container = tk.Frame(button_frame, bg=self.colors['white'])
        btn_container.pack(expand=True)
        
        self.prev_button = tk.Button(
            btn_container,
            text="上一题",
            font=("Microsoft YaHei", 12),
            command=self.prev_question,
            state=tk.DISABLED,
            width=10
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = tk.Button(
            btn_container,
            text="下一题",
            font=("Microsoft YaHei", 12),
            command=self.next_question,
            state=tk.DISABLED,
            width=10
        )
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        self.submit_button = tk.Button(
            btn_container,
            text="交卷",
            font=("Microsoft YaHei", 12),
            command=self.submit_exam,
            state=tk.DISABLED,
            width=10,
            bg=self.colors['accent'],
            fg=self.colors['white']
        )
        self.submit_button.pack(side=tk.LEFT, padx=20)
        
        # 状态栏
        self.status_label = tk.Label(
            self,
            text="正在加载考试...",
            font=("Microsoft YaHei", 10),
            bg=self.colors['light_gray'],
            fg=self.colors['dark']
        )
        self.status_label.pack(fill='x')
    
    def load_test_exam(self):
        """加载考试数据 - 优先从考试管理模块获取已发布考试"""
        print("🔍 加载考试数据...")

        try:
            # 首先尝试从考试管理模块获取已发布考试
            published_exams = self.get_published_exams()

            if published_exams:
                # 使用第一个已发布考试
                exam = published_exams[0]
                print(f"📋 使用已发布考试: {exam.get('name', '未知考试')}")

                # 获取考试详情
                self.exam_details = self.get_exam_details(exam['id'])

                if self.exam_details:
                    self.questions = self.exam_details.get('questions', [])
                    print(f"✅ 从考试管理模块获取到 {len(self.questions)} 道题目")

                    if self.questions:
                        self.status_label.config(text=f"✅ 加载考试: {exam.get('name', '未知考试')} ({len(self.questions)}道题)")
                        self.next_button.config(state=tk.NORMAL)
                        self.submit_button.config(state=tk.NORMAL)
                        self.show_question()
                        return

            # 如果没有已发布考试，回退到测试试卷
            print("⚠️ 未找到已发布考试，使用测试试卷")
            self.load_fallback_test_paper()

        except Exception as e:
            print(f"❌ 加载考试数据失败: {e}")
            import traceback
            traceback.print_exc()
            # 回退到测试试卷
            self.load_fallback_test_paper()

    def get_published_exams(self):
        """获取已发布考试列表"""
        try:
            # 使用客户端API获取已发布考试
            import api

            # 获取学生可参加的已发布考试
            student_id = self.student_id
            published_exams = api.get_published_exams_for_student(student_id)
            print(f"📋 为学生 {student_id} 找到 {len(published_exams)} 个已发布考试")

            # 如果没有找到已发布考试，尝试获取所有可用考试
            if not published_exams:
                print("⚠️ 未找到已发布考试，尝试获取所有可用考试")
                user_info = {"id": student_id, "username": self.student_name}
                all_exams = api.get_exams_for_student(student_id, user_info)
                print(f"📋 找到 {len(all_exams)} 个可用考试")
                return all_exams

            return published_exams

        except Exception as e:
            print(f"❌ 获取已发布考试失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_exam_details(self, exam_id):
        """获取考试详情"""
        try:
            # 使用客户端API获取考试详情
            import api

            print(f"🔍 正在获取考试 {exam_id} 的详情...")
            exam_details = api.get_exam_details(exam_id)

            if exam_details:
                questions = exam_details.get('questions', [])
                print(f"✅ 获取考试详情成功: {exam_details.get('name', '未知考试')}")
                print(f"📋 题目总数: {len(questions)}")

                # 调试：显示前几道题的信息
                print(f"🔍 题目预览:")
                for i, q in enumerate(questions[:5], 1):
                    q_type = q.get('type', '未知')
                    content = q.get('content', '')[:40]
                    options = q.get('options', [])
                    print(f"    第{i}题: [{q_type}] {content}... (选项: {len(options)}个)")

                    # 特别检查判断题
                    if q_type == 'true_false':
                        print(f"         🎯 判断题选项: {options}")
                        if not options or len(options) < 2:
                            print(f"         ❌ 判断题选项异常！")

                return exam_details
            else:
                print(f"❌ 未找到考试 {exam_id}")
                return None

        except Exception as e:
            print(f"❌ 获取考试详情失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def load_fallback_test_paper(self):
        """回退方案：加载测试试卷"""
        try:
            print("🔄 使用回退方案：加载测试试卷")

            # 获取测试试卷数据
            import sqlite3
            db_path = 'question_bank_web/questions.db'

            if not os.path.exists(db_path):
                self.status_label.config(text="❌ 数据库文件不存在")
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 查找测试试卷
            cursor.execute('SELECT id, name FROM papers WHERE name LIKE "%客户端答题功能测试试卷%"')
            paper = cursor.fetchone()
            conn.close()

            if not paper:
                self.status_label.config(text="❌ 未找到测试试卷")
                return

            paper_id = paper[0]
            print(f"📋 测试试卷ID: {paper_id}")

            # 通过API获取题目数据
            self.exam_details = api.get_paper_from_question_bank(paper_id)

            if not self.exam_details:
                self.status_label.config(text="❌ API获取数据失败")
                return

            self.questions = self.exam_details.get('questions', [])
            print(f"✅ 获取到 {len(self.questions)} 道题目")

            if self.questions:
                self.status_label.config(text=f"✅ 加载测试试卷 ({len(self.questions)}道题)")
                self.next_button.config(state=tk.NORMAL)
                self.submit_button.config(state=tk.NORMAL)
                self.show_question()
            else:
                self.status_label.config(text="❌ 没有题目数据")

        except Exception as e:
            print(f"❌ 加载测试试卷失败: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.config(text=f"❌ 加载失败: {str(e)}")

    def get_test_questions(self):
        """获取测试题目数据"""
        return [
            {
                'id': 'q1',
                'type': 'single_choice',
                'content': '以下哪个选项是正确的？',
                'options': ['选项A', '选项B', '选项C', '选项D']
            },
            {
                'id': 'q2',
                'type': 'multiple_choice',
                'content': '以下哪些选项是正确的？（多选题）',
                'options': ['选项A', '选项B', '选项C', '选项D']
            },
            {
                'id': 'q3',
                'type': 'true_false',
                'content': '判断题：地球是圆的。',
                'options': ['正确', '错误']
            },
            {
                'id': 'q4',
                'type': 'fill_blank',
                'content': '填空题：中华人民共和国成立于____年。',
                'options': []
            },
            {
                'id': 'q5',
                'type': 'short_answer',
                'content': '简答题：请简述计算机的基本组成部分。',
                'options': []
            },
            {
                'id': 'q6',
                'type': 'essay',
                'content': '论述题：请论述人工智能技术对现代社会的影响。',
                'options': []
            }
        ]
    
    def show_question(self):
        """显示题目"""
        print(f"\n🔍 show_question开始执行")
        print(f"    current_question_index: {self.current_question_index}")
        print(f"    questions总数: {len(self.questions)}")
        
        try:
            # 清空题目区域
            for widget in self.question_frame.winfo_children():
                widget.destroy()
            
            if not self.questions:
                error_label = tk.Label(
                    self.question_frame,
                    text="❌ 没有题目数据",
                    font=("Microsoft YaHei", 14),
                    bg=self.colors['white'],
                    fg="red"
                )
                error_label.pack(expand=True)
                return
            
            # 获取当前题目
            question = self.questions[self.current_question_index]
            q_id = question.get('id')
            q_type = question.get('type')
            q_content = question.get('content', '')
            q_options = question.get('options', [])

            print(f"    ✅ 当前题目: {q_id}, 类型: {q_type}")
            print(f"    📝 题目内容: {q_content[:50]}...")
            print(f"    🎯 选项数量: {len(q_options)}")
            print(f"    📋 选项内容: {q_options}")

            # 特别检查判断题
            if q_type == 'true_false':
                if not q_options or len(q_options) < 2:
                    print(f"    ❌ 判断题选项异常！选项: {q_options}")
                else:
                    print(f"    ✅ 判断题选项正常: {q_options}")
            
            # 更新导航标签
            self.nav_label.config(text=f"第 {self.current_question_index + 1} / {len(self.questions)} 题")
            
            # 题型显示名称
            type_names = {
                'single_choice': '单选题',
                'multiple_choice': '多选题',
                'true_false': '判断题',
                'fill_blank': '填空题',
                'short_answer': '简答题',
                'essay': '论述题'
            }
            type_display = type_names.get(q_type, '未知题型')
            
            # 显示题目内容
            q_text = f"{self.current_question_index + 1}. [{type_display}] {q_content}"
            print(f"    📝 题目文本: {q_text[:50]}...")
            
            question_label = tk.Label(
                self.question_frame,
                text=q_text,
                font=("Microsoft YaHei", 12, "bold"),
                justify=tk.LEFT,
                wraplength=800,
                bg=self.colors['white'],
                fg=self.colors['dark']
            )
            question_label.pack(anchor='w', pady=(10, 20))
            print(f"    ✅ 题目标签创建成功")
            
            # 根据题型创建答题区域
            self.create_answer_area(question)
            
            # 更新按钮状态
            prev_enabled = self.current_question_index > 0
            next_enabled = self.current_question_index < len(self.questions) - 1
            
            print(f"    🔘 更新按钮状态:")
            print(f"       上一题按钮: {'启用' if prev_enabled else '禁用'}")
            print(f"       下一题按钮: {'启用' if next_enabled else '禁用'}")
            
            self.prev_button.config(state=tk.NORMAL if prev_enabled else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if next_enabled else tk.DISABLED)
            
            print(f"    ✅ show_question执行完成")
            
        except Exception as e:
            print(f"    ❌ show_question执行异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 显示错误信息
            error_label = tk.Label(
                self.question_frame,
                text=f"❌ 题目显示错误: {str(e)}",
                font=("Microsoft YaHei", 12),
                bg=self.colors['white'],
                fg="red"
            )
            error_label.pack(expand=True)
    
    def create_answer_area(self, question):
        """创建答题区域"""
        q_id = question.get('id')
        q_type = question.get('type')
        options = question.get('options', [])
        
        print(f"    🎯 创建答题区域: {q_type}")
        
        if q_type in ['single_choice', 'true_false']:
            self.create_single_choice(q_id, options)
        elif q_type == 'multiple_choice':
            self.create_multiple_choice(q_id, options)
        elif q_type == 'fill_blank':
            self.create_fill_blank(q_id)
        elif q_type in ['short_answer', 'essay']:
            height = 8 if q_type == 'short_answer' else 12
            self.create_text_answer(q_id, height)
        else:
            print(f"    ⚠️ 未知题型: {q_type}")
    
    def create_single_choice(self, q_id, options):
        """创建单选题"""
        print(f"    📝 创建单选题，选项数: {len(options)}")

        # 获取已保存的答案
        saved_answer = self.answers.get(q_id, "")
        if isinstance(saved_answer, tk.StringVar):
            saved_answer = saved_answer.get()

        # 确保saved_answer是字符串类型，并且只有真正保存过的答案才使用
        if not isinstance(saved_answer, str):
            saved_answer = ""

        print(f"    💾 单选题初始答案: '{saved_answer}'")

        # 创建变量 - 使用一个不存在的值作为初始值，确保没有选项被选中
        var = tk.StringVar(value="__NONE_SELECTED__")
        self.answers[q_id] = var

        # 创建选项
        for i, option in enumerate(options):
            option_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
            option_frame.pack(fill='x', pady=5, padx=20)

            rb = tk.Radiobutton(
                option_frame,
                text=f"{chr(65+i)}. {option}",
                variable=var,
                value=option,
                font=("Microsoft YaHei", 11),
                bg=self.colors['white'],
                fg=self.colors['dark'],
                wraplength=700,
                selectcolor=self.colors['white'],  # 设置选中时的背景色
                indicatoron=True,  # 确保显示圆形指示器
                relief='flat',  # 平面样式
                borderwidth=0,  # 无边框
                highlightthickness=0  # 无高亮边框
            )
            rb.pack(anchor='w')

        # 只有在有已保存答案时才设置选中状态
        if saved_answer and saved_answer in options:
            var.set(saved_answer)
            print(f"    ✅ 恢复已保存答案: '{saved_answer}'")
        else:
            print(f"    ✅ 初始状态：无选项被选中")
    
    def create_multiple_choice(self, q_id, options):
        """创建多选题"""
        print(f"    📝 创建多选题，选项数: {len(options)}")

        # 获取已保存的答案
        saved_answers = self.answers.get(q_id, [])
        if isinstance(saved_answers, dict):
            # 如果是字典形式，提取选中的选项
            saved_answers = [opt for opt, var in saved_answers.items() if hasattr(var, 'get') and var.get()]
        elif isinstance(saved_answers, str):
            saved_answers = []
        elif not isinstance(saved_answers, list):
            saved_answers = []

        print(f"    💾 多选题初始答案: {saved_answers}")

        # 创建变量字典 - 重要：所有选项初始都设为False
        vars_dict = {}
        for option in options:
            # 初始状态都是False，避免默认选中
            var = tk.BooleanVar(value=False)
            vars_dict[option] = var

        self.answers[q_id] = vars_dict

        # 创建选项
        for i, option in enumerate(options):
            option_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
            option_frame.pack(fill='x', pady=5, padx=20)

            cb = tk.Checkbutton(
                option_frame,
                text=f"{chr(65+i)}. {option}",
                variable=vars_dict[option],
                font=("Microsoft YaHei", 11),
                bg=self.colors['white'],
                fg=self.colors['dark'],
                wraplength=700,
                selectcolor=self.colors['white']  # 设置选中时的背景色
            )
            cb.pack(anchor='w')

        # 只有在有已保存答案时才设置选中状态
        for option in saved_answers:
            if option in vars_dict:
                vars_dict[option].set(True)
                print(f"    ✅ 恢复已保存答案: '{option}'")
    
    def create_fill_blank(self, q_id):
        """创建填空题"""
        print(f"    📝 创建填空题")
        
        # 获取已保存的答案
        saved_answer = self.answers.get(q_id, "")
        
        answer_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
        answer_frame.pack(fill='x', pady=10, padx=20)
        
        tk.Label(answer_frame, text="答案：", font=("Microsoft YaHei", 12), 
                bg=self.colors['white']).pack(anchor='w')
        
        entry = tk.Entry(answer_frame, font=("Microsoft YaHei", 12), width=50)
        entry.pack(fill='x', pady=5)
        entry.insert(0, saved_answer)
        
        self.answers[q_id] = entry
    
    def create_text_answer(self, q_id, height):
        """创建文本答题区域"""
        print(f"    📝 创建文本答题区域，高度: {height}")
        
        # 获取已保存的答案
        saved_answer = self.answers.get(q_id, "")
        
        answer_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
        answer_frame.pack(fill='both', expand=True, pady=10, padx=20)
        
        tk.Label(answer_frame, text="答案：", font=("Microsoft YaHei", 12), 
                bg=self.colors['white']).pack(anchor='w')
        
        text_widget = tk.Text(answer_frame, font=("Microsoft YaHei", 11), 
                             height=height, wrap=tk.WORD)
        text_widget.pack(fill='both', expand=True, pady=5)
        text_widget.insert('1.0', saved_answer)
        
        self.answers[q_id] = text_widget
    
    def save_current_answer(self):
        """保存当前答案"""
        if not self.questions:
            return
        
        question = self.questions[self.current_question_index]
        q_id = question.get('id')
        answer_obj = self.answers.get(q_id)
        
        if isinstance(answer_obj, tk.StringVar):
            # 单选题 - 过滤掉特殊的未选中值
            answer_value = answer_obj.get()
            if answer_value == "__NONE_SELECTED__":
                answer_value = ""
            self.answers[q_id] = answer_value
        elif isinstance(answer_obj, dict):
            # 多选题
            selected = [opt for opt, var in answer_obj.items() if var.get()]
            self.answers[q_id] = selected
        elif isinstance(answer_obj, tk.Entry):
            # 填空题
            self.answers[q_id] = answer_obj.get()
        elif isinstance(answer_obj, tk.Text):
            # 文本题
            self.answers[q_id] = answer_obj.get('1.0', 'end-1c')
        
        print(f"    💾 保存答案: {q_id} = {self.answers[q_id]}")
    
    def next_question(self):
        """下一题"""
        print(f"\n🔄 next_question被调用")
        print(f"    当前索引: {self.current_question_index}")
        print(f"    题目总数: {len(self.questions)}")
        
        self.save_current_answer()
        
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            print(f"    ✅ 前进到第{self.current_question_index + 1}题")
            self.show_question()
        else:
            print(f"    ⚠️ 已在最后一题，无法前进")
    
    def prev_question(self):
        """上一题"""
        print(f"\n🔄 prev_question被调用")
        print(f"    当前索引: {self.current_question_index}")
        print(f"    题目总数: {len(self.questions)}")
        
        self.save_current_answer()
        
        if self.current_question_index > 0:
            self.current_question_index -= 1
            print(f"    ✅ 后退到第{self.current_question_index + 1}题")
            self.show_question()
        else:
            print(f"    ⚠️ 已在第一题，无法后退")
    
    def submit_exam(self):
        """交卷"""
        print(f"\n📤 submit_exam被调用")

        # 保存当前答案
        self.save_current_answer()

        # 统计答题情况
        answered = 0
        for q_id, answer in self.answers.items():
            if answer and str(answer).strip():
                answered += 1

        result = messagebox.askyesno(
            "确认交卷",
            f"您已完成 {answered}/{len(self.questions)} 道题目。\n\n确定要交卷吗？"
        )

        if result:
            print(f"✅ 用户确认交卷")
            print(f"📊 答题统计: {answered}/{len(self.questions)}")

            # 提交考试数据到后端
            try:
                self.submit_to_backend()
                messagebox.showinfo("交卷成功", f"考试已提交！\n完成题目: {answered}/{len(self.questions)}\n\n系统将自动退出。")
            except Exception as e:
                print(f"❌ 提交到后端失败: {e}")
                messagebox.showinfo("交卷成功", f"考试已提交！\n完成题目: {answered}/{len(self.questions)}\n\n系统将自动退出。")

            # 禁用所有按钮
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.submit_button.config(state=tk.DISABLED)

            self.status_label.config(text="✅ 考试已提交，正在退出...")

            # 延迟退出，让用户看到提示信息
            self.master.after(2000, self.exit_application)
        else:
            print(f"❌ 用户取消交卷")

    def submit_to_backend(self):
        """提交考试数据到后端"""
        try:
            import requests

            # 准备提交数据
            exam_data = {
                'exam_id': getattr(self, 'exam_id', 'test_exam'),
                'paper_id': self.exam_details.get('id') if self.exam_details else 'test_paper',
                'student_id': getattr(self, 'student_id', 'test_student'),
                'student_name': getattr(self, 'student_name', '测试学生'),
                'answers': {},
                'submit_time': time.time(),
                'duration': time.time() - getattr(self, 'start_time', time.time())
            }

            # 格式化答案数据
            for q_id, answer in self.answers.items():
                if isinstance(answer, tk.StringVar):
                    exam_data['answers'][q_id] = answer.get()
                elif isinstance(answer, dict):
                    # 多选题
                    selected = [opt for opt, var in answer.items() if var.get()]
                    exam_data['answers'][q_id] = selected
                elif isinstance(answer, (tk.Entry, tk.Text)):
                    if isinstance(answer, tk.Entry):
                        exam_data['answers'][q_id] = answer.get()
                    else:
                        exam_data['answers'][q_id] = answer.get('1.0', 'end-1c')
                else:
                    exam_data['answers'][q_id] = str(answer)

            print(f"📤 提交考试数据到阅卷中心...")
            print(f"   数据: {exam_data}")

            # 提交到阅卷中心API
            response = requests.post('http://localhost:5002/api/submit_exam',
                                   json=exam_data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                print(f"✅ 提交成功: {result}")
                return True
            else:
                print(f"❌ 提交失败: {response.status_code} - {response.text}")
                return False

        except ImportError:
            print("⚠️ requests模块未安装，跳过后端提交")
            return True
        except Exception as e:
            print(f"❌ 提交数据失败: {e}")
            return False

    def exit_application(self):
        """退出应用程序"""
        print(f"👋 退出应用程序")
        self.master.quit()
        self.master.destroy()
    
def main():
    """主函数"""
    print("🚀 启动修复版考试客户端")
    print("=" * 50)
    app = FixedExamClient()
    app.mainloop()

if __name__ == "__main__":
    main()
