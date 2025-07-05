import tkinter as tk
import sys
import os
import time
import json
import logging
import shutil
from tkinter import messagebox

try:
    import api # 导入我们的模拟API
except ImportError as e:
    messagebox.showerror("初始化错误", f"无法导入API模块: {e}\n请确保系统已正确安装")
    sys.exit(1)

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='client_debug.log',
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger('client_app')

# 检查配置文件
config_path = os.path.join(os.path.dirname(__file__), 'config', 'client_config.json')
if not os.path.exists(config_path):
    logger.error(f"配置文件未找到: {config_path}")
    messagebox.showerror("配置错误", f"客户端配置文件未找到: {config_path}")
    sys.exit(1)

class LoginView(tk.Frame):
    """登录视图"""
    def __init__(self, master, show_exam_list_callback):
        super().__init__(master)
        self.show_exam_list = show_exam_list_callback
        
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

        # 布局
        self.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        
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
            relief="raised",
            borderwidth=2
        )
        card_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # 标题区域
        title_frame = tk.Frame(card_frame, bg=self.colors['white'])
        title_frame.pack(fill=tk.X, pady=(30, 20))
        
        # 系统图标和标题
        title_label = tk.Label(
            title_frame, 
            text="🎓 PH&RL 在线考试系统", 
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.colors['primary'],
            bg=self.colors['white']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame, 
            text="考生登录", 
            font=("Microsoft YaHei", 16),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        subtitle_label.pack(pady=(5, 0))

        # 表单区域
        form_frame = tk.Frame(card_frame, bg=self.colors['white'])
        form_frame.pack(expand=True, fill="both", padx=40, pady=20)
        
        # 准考证号/身份证号输入
        username_frame = tk.Frame(form_frame, bg=self.colors['white'])
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = tk.Label(
            username_frame, 
            text="📋 准考证号/身份证号:", 
            font=("Microsoft YaHei", 12, "bold"),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        username_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = tk.Entry(
            username_frame, 
            width=30,
            font=("Microsoft YaHei", 12),
            relief="solid",
            borderwidth=1,
            bg=self.colors['light']
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 10))
        self.username_entry.insert(0, "student") # 默认值方便测试

        # 密码输入
        password_frame = tk.Frame(form_frame, bg=self.colors['white'])
        password_frame.pack(fill=tk.X, pady=10)
        
        password_label = tk.Label(
            password_frame, 
            text="🔒 密码:", 
            font=("Microsoft YaHei", 12, "bold"),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = tk.Entry(
            password_frame, 
            show="*", 
            width=30,
            font=("Microsoft YaHei", 12),
            relief="solid",
            borderwidth=1,
            bg=self.colors['light']
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 10))
        self.password_entry.insert(0, "123456") # 默认值方便测试

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
            activebackground=self.colors['primary'],
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
            text="© 2024 PH&RL 在线考试系统 - 让考试更简单、更高效！", 
            font=("Microsoft YaHei", 9),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        info_label.pack()

    def verify_user_credentials(self, username, password):
        """验证用户凭据"""
        try:
            # 尝试从数据库验证用户
            users_file_path = api.get_absolute_path('user_management/users.json')
            db_path = os.path.join(os.path.dirname(users_file_path), 'users.db')

            if os.path.exists(db_path):
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    # 查找匹配的用户（通过用户名或身份证号）
                    cursor.execute("""
                        SELECT * FROM users
                        WHERE (username = ? OR id_card = ?) AND password = ?
                    """, (username, username, password))

                    user = cursor.fetchone()
                    if user:
                        user_info = {
                            'id': user['id'],
                            'username': user['username'],
                            'real_name': user['real_name'],
                            'role': user.get('role', 'student'),
                            'id_card': user.get('id_card'),
                            'token': f"token-{user['id']}"
                        }
                        conn.close()
                        return user_info
                    conn.close()
                except Exception as e:
                    print(f"从数据库读取用户数据失败: {e}")

            # 如果数据库验证失败，尝试从JSON文件验证
            if os.path.exists(users_file_path):
                try:
                    with open(users_file_path, 'r', encoding='utf-8') as f:
                        users_data = json.load(f)
                        users = users_data.get("users", [])

                        for user in users:
                            if ((user.get("username") == username or user.get("ID") == username) and
                                (user.get("password") == password or user.get("password_hash") == password)):
                                user_info = {
                                    'id': user.get('id') or user.get('ID'),
                                    'username': user.get('username'),
                                    'real_name': user.get('real_name') or user.get('name'),
                                    'role': user.get('role', 'student'),
                                    'id_card': user.get('id_card') or user.get('ID'),
                                    'token': f"token-{user.get('id') or user.get('ID')}"
                                }
                                return user_info
                except Exception as e:
                    print(f"读取JSON用户数据失败: {e}")

            return None

        except Exception as e:
            print(f"验证用户凭据时出错: {e}")
            return None

    def handle_login(self):
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

        if not user_info:
            messagebox.showerror("登录失败", "准考证号/身份证号或密码错误！")
            return

        # 检查用户角色和权限
        user_role = user_info.get('role', 'student')

        # 管理员、考评员、超级用户可以直接登录查看所有考试
        if user_role in ['admin', 'supervisor', 'evaluator', 'super_user']:
            welcome_message = f"欢迎，{user_info.get('real_name') or user_info.get('username')}！"
            messagebox.showinfo("登录成功", welcome_message)
            self.show_exam_list(user_info)
            return

        # 考生需要检查是否有分配的考试
        if user_role == 'student':
            # 检查是否有可用考试
            exams = []
            try:
                print(f"正在为考生 {user_info.get('username')} (ID: {user_info.get('id')}) 获取考试列表...")
                exams = api.get_exams_for_student(user_info.get('id'), user_info)
                print(f"获取到 {len(exams)} 个考试")
            except Exception as e:
                print(f"获取考试列表时出错: {e}")
                exams = []

            if not exams:
                messagebox.showerror("登录失败",
                    f"您没有可参加的考试，请联系管理员！\n"
                    f"用户: {user_info.get('real_name') or user_info.get('username')}\n"
                    f"ID: {user_info.get('id')}")
                return

            # 有考试才允许考生登录
            welcome_message = f"欢迎，{user_info.get('real_name') or user_info.get('username')}！"
            messagebox.showinfo("登录成功", welcome_message)
            self.show_exam_list(user_info)
            return

        # 设置登录超时
        import threading
        login_timeout = False

        def login_timer():
            nonlocal login_timeout
            login_timeout = True
            messagebox.showerror("登录超时", "登录请求超时，请检查网络连接或稍后再试！")
        
        # 设置5秒超时
        timer = threading.Timer(5.0, login_timer)
        timer.start()

        # 取消超时计时器
        timer.cancel()

        # 如果已经超时，不再处理
        if login_timeout:
            return


class ExamListView(tk.Frame):
    """考试列表视图"""
    def __init__(self, master, user_info, show_exam_callback):
        super().__init__(master)
        self.user_info = user_info
        self.show_exam_page = show_exam_callback
        
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

        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 设置背景色
        self.configure(bg=self.colors['light'])

        # 创建考试列表界面
        self.create_exam_list_ui()

    def create_exam_list_ui(self):
        """创建考试列表界面"""
        # 顶部标题区域
        title_frame = tk.Frame(self, bg=self.colors['light'])
        title_frame.pack(fill=tk.X, pady=(0, 20))

        # 欢迎信息 - 优先显示真实姓名
        if self.user_info:
            display_name = self.user_info.get('real_name') or self.user_info.get('username') or '考生'
        else:
            display_name = '考生'
        welcome_text = f"👋 欢迎, {display_name}！"
        welcome_label = tk.Label(
            title_frame,
            text=welcome_text,
            font=("Microsoft YaHei", 20, "bold"),
            fg=self.colors['primary'],
            bg=self.colors['light']
        )
        welcome_label.pack()

        # 如果有部门信息，显示部门
        if self.user_info and self.user_info.get('department'):
            department_text = f"部门: {self.user_info.get('department')}"
            department_label = tk.Label(
                title_frame,
                text=department_text,
                font=("Microsoft YaHei", 12),
                fg=self.colors['info'],
                bg=self.colors['light']
            )
            department_label.pack(pady=(5, 0))

        # 根据用户角色显示不同的提示文本
        user_role = self.user_info.get('role', 'student') if self.user_info else 'student'
        if user_role in ['admin', 'supervisor', 'evaluator', 'super_user']:
            subtitle_text = "考试管理："
        else:
            subtitle_text = "您可以参加的考试："

        subtitle_label = tk.Label(
            title_frame,
            text=subtitle_text,
            font=("Microsoft YaHei", 14),
            fg=self.colors['dark'],
            bg=self.colors['light']
        )
        subtitle_label.pack(pady=(5, 0))

        # 创建带滚动条的考试列表容器
        self.create_scrollable_exam_list()

    def create_scrollable_exam_list(self):
        """创建带滚动条的考试列表"""
        # 创建主容器
        main_container = tk.Frame(self, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 创建Canvas和滚动条
        canvas = tk.Canvas(main_container, bg=self.colors['light'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['light'])

        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 获取并显示考试列表
        self.display_exams(self.scrollable_frame)

    def display_exams(self, container):
        print("=== display_exams 被调用 ===")
        print(f"用户信息: {self.user_info}")
        for widget in container.winfo_children():
            widget.destroy()
        exams = []
        if self.user_info and self.user_info.get('id'):
            try:
                print(f"正在获取用户 {self.user_info.get('username')} 的考试列表...")
                exams = api.get_exams_for_student(self.user_info['id'], self.user_info)
                print(f"display_exams: 获取到 {len(exams)} 个考试")
            except Exception as e:
                print(f"display_exams: 获取考试列表出错: {e}")
                exams = []
        else:
            print("display_exams: 用户信息无效或缺少ID")

        # 获取用户角色
        user_role = self.user_info.get('role', 'student') if self.user_info else 'student'
        is_admin_user = user_role in ['admin', 'supervisor', 'evaluator', 'super_user']

        if exams:
            print(f"for exam in exams: 之前，exams={exams}")

            # 根据用户角色过滤考试
            filtered_exams = []
            for exam in exams:
                status = exam.get('status')
                if is_admin_user:
                    # 管理员可以看到所有考试
                    filtered_exams.append(exam)
                else:
                    # 考生只能看到可参加的考试
                    if status in ['available', 'published']:
                        filtered_exams.append(exam)
                    else:
                        print(f"过滤掉考试: {exam.get('name')} (状态: {status})")

            print(f"过滤后的考试数量: {len(filtered_exams)}")

            for exam in filtered_exams:
                print(f"渲染考试卡片: {exam.get('name')} status={exam.get('status')}")
                card = tk.Frame(container, bg=self.colors['white'], relief="solid", borderwidth=1)
                card.pack(fill=tk.X, padx=0, pady=10)

                # 考试名称
                name_label = tk.Label(card, text=exam.get('name', '未知考试'), font=("Microsoft YaHei", 14, "bold"), fg=self.colors['primary'], bg=self.colors['white'])
                name_label.pack(anchor="w", padx=10, pady=(10, 0))

                # 状态提示
                status = exam.get('status')
                if is_admin_user:
                    # 管理员用户看到更详细的状态
                    status_text = {
                        'available': '已发布 - 可参加',
                        'draft': '草稿 - 未发布',
                        'completed': '已完成',
                        'in_progress': '进行中',
                        'published': '已发布'
                    }.get(status, f"状态：{status}")
                else:
                    # 考生只看到简化的状态
                    status_text = {
                        'available': '可参加',
                        'published': '可参加'
                    }.get(status, f"状态：{status}")

                status_color = {
                    'available': self.colors['success'],
                    'published': self.colors['success'],
                    'draft': self.colors['warning'],
                    'completed': self.colors['danger'],
                    'in_progress': self.colors['info']
                }.get(status, self.colors['dark'])

                status_label = tk.Label(card, text=status_text, font=("Microsoft YaHei", 12), fg=status_color, bg=self.colors['white'])
                status_label.pack(anchor="w", padx=10, pady=(0, 10))

                # 按钮区域
                btn_frame = tk.Frame(card, bg=self.colors['white'])
                btn_frame.pack(anchor="e", padx=10, pady=(0, 10))

                # 根据用户角色和考试状态显示不同的按钮
                if is_admin_user:
                    # 管理员用户：点击后界面不变，只显示查看按钮
                    btn = tk.Button(btn_frame, text="查看详情", font=("Microsoft YaHei", 12),
                                  bg=self.colors['info'], fg=self.colors['white'],
                                  command=lambda e=exam: self.view_exam_details(e))
                    btn.pack(side=tk.RIGHT)
                else:
                    # 考生用户：只有可参加的考试才能进入
                    btn = tk.Button(btn_frame, text="进入考试", font=("Microsoft YaHei", 12),
                                  bg=self.colors['primary'], fg=self.colors['white'],
                                  command=lambda e=exam: self.enter_exam_fullscreen(e))
                    btn.pack(side=tk.RIGHT)
            print("for exam in exams: 之后")
        else:
            # 没有考试时的提示
            user_role = self.user_info.get('role', 'student') if self.user_info else 'student'
            if user_role in ['admin', 'supervisor', 'evaluator', 'super_user']:
                no_exam_text = "📝 暂无考试项目"
            else:
                no_exam_text = "📝 暂无可参加的考试，请联系管理员"

            no_exam_frame = tk.Frame(container, bg=self.colors['white'], relief="solid", borderwidth=1)
            no_exam_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            no_exam_label = tk.Label(
                no_exam_frame,
                text=no_exam_text,
                font=("Microsoft YaHei", 16),
                fg=self.colors['dark'],
                bg=self.colors['white']
            )
            no_exam_label.pack(expand=True)
            info_label = tk.Label(
                no_exam_frame, 
                text="您当前没有被分配任何考试，或者所有考试已经结束。\n如需参加考试，请联系考试管理员。", 
                font=("Microsoft YaHei", 10),
                fg=self.colors['info'],
                bg=self.colors['white']
            )
            info_label.pack(pady=(0, 10))

    def enter_exam(self, exam):
        # 获取考试详情，包括总分和及格分
        exam_details = api.get_exam_details(exam['id'])
        total_score = exam_details.get('total_score', 100)
        pass_score = exam_details.get('pass_score', 60)

        # 确认对话框，显示总分和及格分
        if messagebox.askyesno("确认", f"您确定要进入考试 '{exam['name']}' 吗？\n\n总分: {total_score}\n及格分: {pass_score}\n\n进入后将开始计时。"):
            # 通知主应用切换到答题页面
            self.show_exam_page(self.user_info, exam)

    def view_exam_details(self, exam):
        """管理员查看考试详情（界面不变）"""
        print(f"管理员查看考试详情: {exam.get('name')}")
        # 显示考试详情对话框
        details = f"""考试名称: {exam.get('name', '未知')}
考试状态: {exam.get('status', '未知')}
考试ID: {exam.get('id', '未知')}
创建时间: {exam.get('created_at', '未知')}
题目数量: {len(exam.get('questions', []))}
考试时长: {exam.get('duration', '未设置')} 分钟"""

        messagebox.showinfo("考试详情", details)

    def enter_exam_fullscreen(self, exam):
        """考生进入全屏考试模式"""
        print(f"考生进入全屏考试: {exam.get('name')}")

        # 获取考试详情，包括总分和及格分
        try:
            exam_details = api.get_exam_details(exam['id'])
            total_score = exam_details.get('total_score', 100)
            pass_score = exam_details.get('pass_score', 60)
            time_limit = exam_details.get('time_limit', 60)
            questions_count = len(exam_details.get('questions', []))
        except Exception as e:
            print(f"获取考试详情失败: {e}")
            total_score = 100
            pass_score = 60
            time_limit = 60
            questions_count = 0

        # 显示进入考试确认对话框
        result = messagebox.askyesno(
            "进入考试",
            f"即将进入考试：{exam.get('name')}\n\n"
            f"考试信息：\n"
            f"• 题目数量：{questions_count} 题\n"
            f"• 考试时长：{time_limit} 分钟\n"
            f"• 总分：{total_score} 分\n"
            f"• 及格分：{pass_score} 分\n\n"
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
                self.enable_anti_cheat_mode()

                # 进入全屏模式
                self.master.attributes('-fullscreen', True)
                self.master.attributes('-topmost', True)

                # 显示考试页面
                print(f"正在跳转到考试页面: {exam.get('name')}")
                self.show_exam_page(self.user_info, exam)

            except Exception as e:
                print(f"进入考试失败: {e}")
                messagebox.showerror("错误", f"进入考试失败: {str(e)}")
                # 如果失败，退出防作弊模式
                self.disable_anti_cheat_mode()

    def enable_anti_cheat_mode(self):
        """启用防作弊模式"""
        print("启用防作弊模式...")

        # 添加调试退出接口 - Ctrl+Shift+D 退出防作弊模式
        self.master.bind('<Control-Shift-D>', self.debug_exit_anti_cheat)

        # 禁用Alt+Tab等快捷键
        self.master.bind('<Alt-Tab>', lambda e: 'break')
        self.master.bind('<Control-Alt-Delete>', lambda e: 'break')
        self.master.bind('<Alt-F4>', lambda e: 'break')
        self.master.bind('<Control-Shift-Escape>', lambda e: 'break')

        # 使用更精确的窗口状态监控，而不是焦点变化
        self.master.bind('<Unmap>', self.on_window_minimized)  # 窗口最小化
        self.master.bind('<Map>', self.on_window_restored)     # 窗口恢复

        # 监控窗口激活状态变化（更准确的切屏检测）
        self.master.bind('<Deactivate>', self.on_window_deactivated)
        self.master.bind('<Activate>', self.on_window_activated)

        # 禁用右键菜单
        self.master.bind('<Button-3>', lambda e: 'break')

        # 设置全屏和置顶
        self.master.attributes('-fullscreen', True)
        self.master.attributes('-topmost', True)

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

        # 恢复正常模式
        self.master.attributes('-fullscreen', False)
        self.master.attributes('-topmost', False)

        # 解除快捷键绑定
        try:
            self.master.unbind('<Alt-Tab>')
            self.master.unbind('<Control-Alt-Delete>')
            self.master.unbind('<Alt-F4>')
            self.master.unbind('<Control-Shift-Escape>')
            self.master.unbind('<Unmap>')
            self.master.unbind('<Map>')
            self.master.unbind('<Deactivate>')
            self.master.unbind('<Activate>')
            self.master.unbind('<Button-3>')
            self.master.unbind('<Control-Shift-D>')
        except Exception as e:
            print(f"解除事件绑定时出错: {e}")

        print("防作弊模式已禁用")

    def on_focus_lost(self, event):
        """窗口失去焦点时的处理"""
        print(f"焦点变化事件: {event.widget if hasattr(event, 'widget') else 'unknown'}")

        # 检查是否是真正的切屏行为
        # 如果焦点转移到了其他应用程序，才触发警告
        try:
            # 获取当前活动窗口
            import tkinter as tk
            current_focus = self.master.focus_get()

            # 如果焦点完全丢失（切换到其他应用），才触发警告
            if current_focus is None:
                print("警告：检测到真正的切屏行为！")
                # 记录切屏行为
                self.log_cheat_attempt("窗口失去焦点")

                # 延迟处理，避免与正常操作冲突
                self.master.after(100, self.handle_real_focus_loss)
            else:
                print(f"焦点转移到内部组件: {current_focus}")

        except Exception as e:
            print(f"焦点检查异常: {e}")

    def handle_real_focus_loss(self):
        """处理真正的焦点丢失"""
        try:
            # 再次检查焦点状态
            current_focus = self.master.focus_get()
            if current_focus is None:
                print("确认为真正的切屏行为，显示警告")

                # 强制回到前台
                self.master.lift()
                self.master.focus_force()

                # 显示警告
                messagebox.showwarning(
                    "考试警告",
                    "检测到您切换了应用程序！\n"
                    "这可能被视为作弊行为。\n"
                    "请专心完成考试。"
                )
            else:
                print("焦点已恢复，取消警告")
        except Exception as e:
            print(f"处理焦点丢失异常: {e}")

    def on_window_minimized(self, event):
        """窗口被最小化时的处理"""
        print("警告：检测到窗口最小化！")
        self.log_cheat_attempt("窗口最小化")

        # 立即恢复窗口
        self.master.deiconify()
        self.master.lift()
        self.master.focus_force()

        messagebox.showwarning(
            "考试警告",
            "检测到窗口最小化！\n"
            "考试期间不允许最小化窗口。\n"
            "请专心完成考试。"
        )

    def on_window_restored(self, event):
        """窗口恢复时的处理"""
        print("窗口已恢复")

    def on_window_deactivated(self, event):
        """窗口失去激活状态时的处理"""
        print("窗口失去激活状态")
        # 延迟检查，避免误报
        self.master.after(200, self.check_window_activation)

    def on_window_activated(self, event):
        """窗口获得激活状态时的处理"""
        print("窗口获得激活状态")

    def check_window_activation(self):
        """检查窗口激活状态"""
        try:
            # 检查窗口是否仍然失去激活状态
            if not self.master.focus_get():
                print("警告：检测到切换到其他应用程序！")
                self.log_cheat_attempt("切换应用程序")

                # 强制回到前台
                self.master.lift()
                self.master.focus_force()

                messagebox.showwarning(
                    "考试警告",
                    "检测到切换到其他应用程序！\n"
                    "考试期间请保持在考试界面。\n"
                    "请专心完成考试。"
                )
        except Exception as e:
            print(f"检查窗口激活状态异常: {e}")

    def on_focus_gained(self, event):
        """窗口获得焦点时的处理"""
        print("窗口重新获得焦点")

    def log_cheat_attempt(self, action):
        """记录可疑的作弊行为"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] 用户: {self.user_info.get('username', 'unknown')} - 行为: {action}"
        print(f"作弊日志: {log_entry}")

        # 这里可以将日志发送到服务器
        # api.log_cheat_attempt(self.user_info.get('id'), action, timestamp)


class ExamPageView(tk.Frame):
    """答题页面视图"""
    def __init__(self, master, user_info, exam_info, on_submit_callback):
        super().__init__(master)
        self.user_info = user_info
        self.exam_info = exam_info
        self.on_submit_callback = on_submit_callback
        
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
        
        logger.debug(f"=== 调试信息：开始加载考试 {self.exam_info['id']} 的详情 ===")
        self.exam_details = api.get_exam_details(self.exam_info['id'])
        self.questions = self.exam_details.get('questions', [])
        logger.debug(f"=== 调试信息：已加载考试详情，试题数量: {len(self.questions)} ===")
        if self.questions:
            logger.debug(f"第一道题内容: {self.questions[0].get('content', '无内容')}")
            logger.debug(f"试卷名称: {self.exam_details.get('name', '未知')}")
        self.current_question_index = 0
        self.answers = {}

        # 本地备份文件路径
        self.backup_filepath = f"exam_backup_user_{self.user_info['id']}_exam_{self.exam_info['id']}.json"

        # 尝试从本地文件加载答案
        self._load_answers_from_local_file()

        # 倒计时功能
        duration_minutes = self.exam_details.get("duration_minutes", 30)
        self.end_time = time.time() + duration_minutes * 60

        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.configure(bg=self.colors['light'])
        
        self._build_ui()
        self.show_question()
        self.update_timer()
        self._periodic_local_save() # 启动周期性本地保存

    def _load_answers_from_local_file(self):
        """如果存在备份文件，则加载答案"""
        if os.path.exists(self.backup_filepath):
            try:
                with open(self.backup_filepath, 'r') as f:
                    self.answers = json.load(f)
                logger.info(f"从本地文件 {self.backup_filepath} 恢复了答题记录")
                messagebox.showinfo("进度恢复", "检测到您有未完成的答题记录，已为您自动恢复。")
            except Exception as e:
                logger.error(f"加载本地备份文件失败: {e}")
                self.answers = {} # 如果文件损坏，则从头开始

    def _get_clean_answers(self):
        """将包含Tkinter变量的答案字典转换为可序列化的纯Python字典"""
        clean_answers = {}
        # 先保存当前正在查看的题目答案
        self._save_current_answer()
        for q_id, answer_obj in self.answers.items():
            if isinstance(answer_obj, tk.StringVar):
                clean_answers[q_id] = answer_obj.get()
            elif isinstance(answer_obj, dict): # 处理多选题
                selected_options = [opt for opt, var in answer_obj.items() if var.get()]
                clean_answers[q_id] = selected_options
            else: # 已经是纯净的答案
                clean_answers[q_id] = answer_obj
        return clean_answers

    def _save_answers_to_local_file(self):
        """将当前答案保存到本地JSON文件"""
        try:
            answers_to_save = self._get_clean_answers()
            with open(self.backup_filepath, 'w') as f:
                json.dump(answers_to_save, f)
            logger.debug(f"已将答案保存到本地文件 {self.backup_filepath}")
        except Exception as e:
            logger.error(f"自动保存答案到本地文件失败: {e}")
    
    def _periodic_local_save(self):
        """每隔30秒保存一次答案"""
        self._save_answers_to_local_file()
        self.after(30000, self._periodic_local_save)

    def _build_ui(self):
        # 顶部信息栏
        top_frame = tk.Frame(self, bg=self.colors['white'], relief="solid", borderwidth=1)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 左侧信息区域
        left_info_frame = tk.Frame(top_frame, bg=self.colors['white'])
        left_info_frame.pack(side=tk.LEFT, padx=15, pady=10)
        
        # 考试标题
        exam_title_label = tk.Label(
            left_info_frame, 
            text=self.exam_details.get('name', '在线考试'), 
            font=("Microsoft YaHei", 16, "bold"),
            fg=self.colors['primary'],
            bg=self.colors['white']
        )
        exam_title_label.pack(anchor=tk.W)
        
        # 分数信息
        total_score = self.exam_details.get('total_score', 100)
        pass_score = self.exam_details.get('pass_score', 60)
        score_info_text = f"总分: {total_score} | 及格分: {pass_score}"
        
        score_info_label = tk.Label(
            left_info_frame, 
            text=score_info_text, 
            font=("Microsoft YaHei", 10),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        score_info_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 右侧信息区域
        right_info_frame = tk.Frame(top_frame, bg=self.colors['white'])
        right_info_frame.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # 倒计时
        self.timer_label = tk.Label(
            right_info_frame, 
            text="", 
            font=("Microsoft YaHei", 12, "bold"), 
            fg=self.colors['danger'],
            bg=self.colors['white']
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)
        
        # 题目导航
        self.question_nav_label = tk.Label(
            right_info_frame, 
            text="", 
            font=("Microsoft YaHei", 12),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        self.question_nav_label.pack(side=tk.LEFT)

        # 题目显示区
        self.question_frame = tk.Frame(
            self, 
            bg=self.colors['white'],
            relief="solid", 
            borderwidth=1
        )
        self.question_frame.pack(fill="both", expand=True, pady=10)

        # 底部导航栏
        bottom_frame = tk.Frame(self, bg=self.colors['white'], relief="solid", borderwidth=1)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 按钮样式
        button_style = {
            "font": ("Microsoft YaHei", 11),
            "relief": "flat",
            "borderwidth": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        self.prev_button = tk.Button(
            bottom_frame, 
            text="◀ 上一题", 
            command=self.prev_question,
            bg=self.colors['info'],
            fg="white",
            activebackground=self.colors['info'],
            activeforeground="white",
            **button_style
        )
        self.prev_button.pack(side=tk.LEFT, padx=15, pady=10)
        
        self.next_button = tk.Button(
            bottom_frame, 
            text="下一题 ▶", 
            command=self.next_question,
            bg=self.colors['info'],
            fg="white",
            activebackground=self.colors['info'],
            activeforeground="white",
            **button_style
        )
        self.next_button.pack(side=tk.LEFT, padx=5, pady=10)

        self.submit_button = tk.Button(
            bottom_frame, 
            text="📤 交卷", 
            command=self.submit_exam, 
            bg=self.colors['danger'], 
            fg="white",
            activebackground=self.colors['danger'],
            activeforeground="white",
            font=("Microsoft YaHei", 12, "bold"),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.submit_button.pack(side=tk.RIGHT, padx=15, pady=10)

        # 为按钮设置事件处理，防止触发防作弊警告
        self.setup_button_events(self.prev_button)
        self.setup_button_events(self.next_button)
        self.setup_button_events(self.submit_button)

    def update_multiple_choice(self, question_id, option, is_selected):
        """更新多选题的答案"""
        if question_id in self.answers and isinstance(self.answers[question_id], dict):
            # 确保选项的状态与UI一致
            if option in self.answers[question_id]:
                self.answers[question_id][option].set(is_selected)
                
    def update_single_choice(self, question_id, option):
        """更新单选题或判断题的答案"""
        if question_id in self.answers and isinstance(self.answers[question_id], tk.StringVar):
            # 设置选中的选项
            # 如果当前选项已经被选中，点击时不做任何操作（避免取消选择）
            if self.answers[question_id].get() != option:
                self.answers[question_id].set(option)
            # 注意：不添加else分支，这样就不会取消选择
    
    def show_question(self):
        try:
            print(f"🔍 [DEBUG] show_question开始执行")
            print(f"    current_question_index: {self.current_question_index}")
            print(f"    questions总数: {len(self.questions) if self.questions else 0}")

            # 清空上一题的内容
            for widget in self.question_frame.winfo_children():
                widget.destroy()

            if not self.questions:
                print(f"    ❌ 没有题目数据")
                no_question_label = tk.Label(
                    self.question_frame,
                    text="📝 本次考试没有题目。",
                    font=("Microsoft YaHei", 14),
                    fg=self.colors['dark'],
                    bg=self.colors['white']
                )
                no_question_label.pack(expand=True)
                return

            # 获取当前题目
            question = self.questions[self.current_question_index]
            q_id = question.get('id')
            q_type = question.get('type')

            print(f"    ✅ 当前题目: {q_id}, 类型: {q_type}")

            # 更新导航标签
            self.question_nav_label.config(text=f"第 {self.current_question_index + 1} / {len(self.questions)} 题")

            # 显示题干
            if q_type in ['single', 'single_choice']:
                q_type_display = "(单选题)"
            elif q_type in ['multiple', 'multiple_choice']:
                q_type_display = "(多选题)"
            elif q_type == 'true_false':
                q_type_display = "(判断题)"
            elif q_type == 'fill_blank':
                q_type_display = "(填空题)"
            elif q_type == 'short_answer':
                q_type_display = "(简答题)"
            elif q_type == 'essay':
                q_type_display = "(论述题)"
            else:
                q_type_display = "(未知题型)"

            q_text = f"{self.current_question_index + 1}. {q_type_display} {question.get('content')}"
            print(f"    📝 创建题目标签: {q_text[:50]}...")

            question_label = tk.Label(
                self.question_frame,
                text=q_text,
                font=("Microsoft YaHei", 14),
                justify=tk.LEFT,
                wraplength=700,
                bg=self.colors['white'],
                fg=self.colors['dark']
            )
            question_label.pack(anchor='w', pady=10)
            print(f"    ✅ 题目标签创建成功")

            # 根据题型创建选项
            options = question.get('options', [])

            # 处理不同类型的题目
            if q_type in ['single', 'single_choice'] or q_type == 'true_false':
                # 单选或判断
                # 创建一个新的StringVar，确保初始状态为未选中
                var = tk.StringVar(value="")

                # 获取已保存的答案（如果有）
                saved_answer = ""
                answer_obj = self.answers.get(q_id)
                if answer_obj is not None:
                    if isinstance(answer_obj, tk.StringVar):
                        saved_answer = answer_obj.get()
                    elif isinstance(answer_obj, str):
                        saved_answer = answer_obj

                # 存储变量以便后续获取值
                self.answers[q_id] = var

                # 判断题特殊处理
                if q_type == 'true_false':
                    # 确保判断题的选项是标准的
                    options = ["正确", "错误"] if not options else options

                # 创建一个Frame来容纳选项
                options_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
                options_frame.pack(fill='x', padx=10, pady=5)

                # 创建自定义单选按钮组
                selected_option = None
                option_buttons = []

                # 创建选项按钮
                for opt in options:
                    # 创建一个Frame来容纳每个选项
                    option_frame = tk.Frame(options_frame, bg=self.colors['white'])
                    option_frame.pack(fill='x', pady=2, anchor='w')

                    # 检查是否是已保存的答案
                    is_selected = (saved_answer == opt)
                    if is_selected:
                        var.set(opt)  # 设置已保存的答案
                        selected_option = opt

                    # 创建一个自定义的单选按钮（使用Label + 圆形指示器）
                    button_frame = tk.Frame(option_frame, bg=self.colors['white'])
                    button_frame.pack(side='left', fill='x')

                    # 创建圆形指示器
                    indicator = tk.Label(button_frame, text="○" if not is_selected else "●",
                                        font=("Microsoft YaHei", 12),
                                        bg=self.colors['white'], fg="black")
                    indicator.pack(side='left', padx=(5, 2))

                    # 创建选项文本
                    label = tk.Label(button_frame, text=opt,
                                    font=("Microsoft YaHei", 12),
                                    bg=self.colors['white'], fg="black")
                    label.pack(side='left', padx=2)

                    # 存储按钮组件，以便后续更新
                    option_buttons.append((opt, indicator, label))

                    # 为整个按钮区域添加点击事件
                    def select_option(event, o=opt, buttons=option_buttons, v=var):
                        # 更新所有按钮的状态
                        for opt_text, ind, _ in buttons:
                            ind.config(text="○" if opt_text != o else "●")
                        # 设置变量值
                        v.set(o)
                        # 调用更新函数
                        self.update_single_choice(q_id, o)
                        return 'break'

                    # 为按钮的所有部分绑定点击事件
                    button_frame.bind('<Button-1>', select_option)
                    indicator.bind('<Button-1>', select_option)
                    label.bind('<Button-1>', select_option)

            elif q_type in ['multiple', 'multiple_choice']:
                # 多选
                vars = {}
                # 确保current_answers是一个空列表，避免默认选中
                current_answers = []
                answer_obj = self.answers.get(q_id)
                if isinstance(answer_obj, dict):
                    # 如果已经有保存的答案，从字典中提取选中的选项
                    current_answers = [opt for opt, var in answer_obj.items() if isinstance(var, tk.BooleanVar) and var.get()]
                elif isinstance(answer_obj, list):
                    current_answers = self.answers.get(q_id)

                # 创建一个Frame来容纳选项
                options_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
                options_frame.pack(fill='x', padx=10, pady=5)

                for opt in options:
                    # 创建一个Frame来容纳每个选项
                    option_frame = tk.Frame(options_frame, bg=self.colors['white'])
                    option_frame.pack(fill='x', pady=2, anchor='w')

                    var = tk.BooleanVar(value=False)  # 确保初始状态为未选中
                    if opt in current_answers:  # 只有当有已保存的答案时才设置为选中
                        var.set(True)

                    # 使用Checkbutton显示选项文本，添加command回调函数
                    cb = tk.Checkbutton(option_frame, text=opt, variable=var,
                                       font=("Microsoft YaHei", 12),
                                       takefocus=False, indicatoron=True,
                                       bg=self.colors['white'], fg="black",
                                       activebackground=self.colors['white'],
                                       selectcolor="#d9d9d9",
                                       highlightthickness=0,
                                       command=lambda v=var, o=opt: self.update_multiple_choice(q_id, o, v.get()))
                    cb.pack(side='left', padx=5, fill='x')

                    vars[opt] = var
                self.answers[q_id] = vars # 存储所有选项的tk变量

            elif q_type == 'fill_blank':
                # 填空题
                current_answer = self.answers.get(q_id, '')
                answer_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
                answer_frame.pack(fill='x', padx=20, pady=10)

                answer_label = tk.Label(answer_frame, text="答案：", font=("Microsoft YaHei", 12), bg=self.colors['white'])
                answer_label.pack(side='left')

                answer_entry = tk.Entry(answer_frame, font=("Microsoft YaHei", 12), width=30)
                answer_entry.pack(side='left', padx=5)
                answer_entry.insert(0, current_answer)

                # 为输入框绑定事件，防止触发防作弊警告
                self.setup_input_widget_events(answer_entry)

                # 将Entry对象存储到answers字典中
                self.answers[q_id] = answer_entry

            elif q_type == 'short_answer':
                # 简答题
                current_answer = self.answers.get(q_id, '')
                answer_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
                answer_frame.pack(fill='x', padx=20, pady=10)

                answer_label = tk.Label(answer_frame, text="答案：", font=("Microsoft YaHei", 12), bg=self.colors['white'])
                answer_label.pack(anchor='w')

                answer_text = tk.Text(answer_frame, font=("Microsoft YaHei", 12), width=50, height=10)
                answer_text.pack(fill='both', expand=True, padx=5, pady=5)
                answer_text.insert('1.0', current_answer)

                # 为文本框绑定事件，防止触发防作弊警告
                self.setup_input_widget_events(answer_text)

                # 将Text对象存储到answers字典中
                self.answers[q_id] = answer_text

            elif q_type == 'essay':
                # 论述题
                current_answer = self.answers.get(q_id, '')
                answer_frame = tk.Frame(self.question_frame, bg=self.colors['white'])
                answer_frame.pack(fill='x', padx=20, pady=10)

                answer_label = tk.Label(answer_frame, text="答案：", font=("Microsoft YaHei", 12), bg=self.colors['white'])
                answer_label.pack(anchor='w')

                # 论述题使用更大的文本框
                answer_text = tk.Text(answer_frame, font=("Microsoft YaHei", 12), width=60, height=15)
                answer_text.pack(fill='both', expand=True, padx=5, pady=5)
                answer_text.insert('1.0', current_answer)

                # 为文本框绑定事件，防止触发防作弊警告
                self.setup_input_widget_events(answer_text)

                # 将Text对象存储到answers字典中
                self.answers[q_id] = answer_text

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
                fg="red",
                bg=self.colors['white']
            )
            error_label.pack(expand=True)

    def setup_input_widget_events(self, widget):
        """为输入组件设置事件处理，防止触发防作弊警告"""
        def on_widget_focus_in(event):
            print(f"输入组件获得焦点: {widget.__class__.__name__}")
            # 阻止事件冒泡到父窗口
            return "break"

        def on_widget_focus_out(event):
            print(f"输入组件失去焦点: {widget.__class__.__name__}")
            # 阻止事件冒泡到父窗口
            return "break"

        def on_widget_click(event):
            print(f"点击输入组件: {widget.__class__.__name__}")
            # 阻止事件冒泡到父窗口
            return "break"

        # 绑定事件
        widget.bind('<FocusIn>', on_widget_focus_in)
        widget.bind('<FocusOut>', on_widget_focus_out)
        widget.bind('<Button-1>', on_widget_click)

    def setup_button_events(self, button):
        """为按钮设置事件处理，防止触发防作弊警告"""
        def on_button_click(event):
            print(f"点击按钮: {button.cget('text')}")
            # 阻止事件冒泡到父窗口
            return "break"

        def on_button_focus_in(event):
            print(f"按钮获得焦点: {button.cget('text')}")
            # 阻止事件冒泡到父窗口
            return "break"

        def on_button_focus_out(event):
            print(f"按钮失去焦点: {button.cget('text')}")
            # 阻止事件冒泡到父窗口
            return "break"

        # 绑定事件
        button.bind('<Button-1>', on_button_click)
        button.bind('<FocusIn>', on_button_focus_in)
        button.bind('<FocusOut>', on_button_focus_out)

    def _save_current_answer(self):
        """在切换题目或交卷前，保存当前题目的答案"""
        if not self.questions:
            return
            
        question = self.questions[self.current_question_index]
        q_id = question.get('id')
        answer_obj = self.answers.get(q_id)

        if isinstance(answer_obj, tk.StringVar):
            # 单选或判断题
            self.answers[q_id] = answer_obj.get()
        elif isinstance(answer_obj, dict):
            # 多选题
            selected_options = [opt for opt, var in answer_obj.items() if var.get()]
            self.answers[q_id] = selected_options
        elif isinstance(answer_obj, tk.Entry):
            # 填空题
            self.answers[q_id] = answer_obj.get()
        elif isinstance(answer_obj, tk.Text):
            # 简答题
            self.answers[q_id] = answer_obj.get('1.0', 'end-1c')

    def next_question(self):
        print(f"🔄 [DEBUG] next_question被调用")
        print(f"    当前索引: {self.current_question_index}")
        print(f"    题目总数: {len(self.questions)}")

        self._save_current_answer()
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            print(f"    ✅ 前进到第{self.current_question_index + 1}题")
            self.show_question()
        else:
            print(f"    ⚠️ 已在最后一题，无法前进")

    def prev_question(self):
        print(f"🔄 [DEBUG] prev_question被调用")
        print(f"    当前索引: {self.current_question_index}")
        print(f"    题目总数: {len(self.questions)}")

        self._save_current_answer()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            print(f"    ✅ 后退到第{self.current_question_index + 1}题")
            self.show_question()
        else:
            print(f"    ⚠️ 已在第一题，无法后退")

    def update_timer(self):
        """更新倒计时显示"""
        remaining_seconds = int(self.end_time - time.time())
        if remaining_seconds > 0:
            minutes, seconds = divmod(remaining_seconds, 60)
            self.timer_label.config(text=f"剩余时间: {minutes:02d}:{seconds:02d}")
            # 每1000毫秒（1秒）后再次调用自身
            self.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="时间到！", fg="red")
            messagebox.showwarning("时间到", "考试时间已到，系统将自动为您提交答卷。")
            self.submit_exam(force_submit=True)

    def submit_exam(self, force_submit=False):
        # force_submit 参数用于区分是时间到了自动交卷还是用户手动交卷
        confirmed = False
        if force_submit:
            confirmed = True
            logger.info(f"考试时间到，自动提交考试 {self.exam_info['id']} 的答卷")
        else:
            confirmed = messagebox.askyesno("确认交卷", "您确定要提交答卷吗？提交后将无法修改。")
            if confirmed:
                logger.info(f"用户确认提交考试 {self.exam_info['id']} 的答卷")
        
        if confirmed:
            final_answers = self._get_clean_answers()
            logger.debug(f"准备提交考试 {self.exam_info['id']} 的答案，共 {len(final_answers)} 道题")

            result = api.submit_answers(self.exam_info['id'], self.user_info['id'], final_answers)
            if result and result.get("success"):
                logger.info(f"成功提交考试 {self.exam_info['id']} 的答卷")
                # 提交成功后，删除本地备份文件
                try:
                    if os.path.exists(self.backup_filepath):
                        os.remove(self.backup_filepath)
                        logger.debug(f"已删除本地备份文件 {self.backup_filepath}")
                except Exception as e:
                    logger.error(f"删除本地备份文件失败: {e}")

                # 显示考试完成页面，不显示分数信息
                self.on_submit_callback(self.user_info, {
                    "exam_name": self.exam_details.get('name', '在线考试')
                })
            else:
                logger.error(f"提交考试 {self.exam_info['id']} 的答卷失败: {result}")
                messagebox.showerror("提交失败", "提交答卷时发生错误，请联系管理员。您的答题记录已保存在本地。")


class ExamResultView(tk.Frame):
    """考试结果显示页面"""
    def __init__(self, master, user_info, result_info, on_back_callback):
        super().__init__(master)
        self.user_info = user_info
        self.result_info = result_info
        self.on_back_callback = on_back_callback
        
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
        
        self.pack(fill="both", expand=True, padx=20, pady=20)
        self.configure(bg=self.colors['light'])
        
        self._build_ui()
    
    def _build_ui(self):
        # 创建一个居中的结果卡片
        result_frame = tk.Frame(
            self, 
            bg=self.colors['white'],
            relief="solid", 
            borderwidth=1
        )
        result_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)
        
        # 标题
        title_label = tk.Label(
            result_frame, 
            text="考试完成", 
            font=("Microsoft YaHei", 24, "bold"),
            fg=self.colors['primary'],
            bg=self.colors['white']
        )
        title_label.pack(pady=(30, 20))
        
        # 考试名称
        exam_name_label = tk.Label(
            result_frame, 
            text=self.result_info.get('exam_name', '在线考试'), 
            font=("Microsoft YaHei", 16),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        exam_name_label.pack(pady=(0, 30))
        
        # 分割线
        separator = tk.Frame(result_frame, height=2, bg=self.colors['light'])
        separator.pack(fill="x", padx=50, pady=10)
        
        # 完成信息
        complete_label = tk.Label(
            result_frame, 
            text="您已完成考试，可以离开了。", 
            font=("Microsoft YaHei", 14),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        complete_label.pack(pady=30)


class ExamClient(tk.Tk):
    def check_main_console_running(self):
        """检查主控台是否在运行"""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'python.exe' and 'main_console.py' in ' '.join(proc.cmdline()):
                    return True
            return False
        except Exception as e:
            logger.warning(f"检查主控台状态失败: {e}")
            return True  # 如果检查失败，假设主控台在运行

    def ensure_config_exists(self):
        """确保配置目录和配置文件存在"""
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        config_path = os.path.join(config_dir, 'client_config.json')
        # 创建config目录
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        # 如果config.json不存在，尝试从client目录复制一份或创建默认
        if not os.path.exists(config_path):
            default_path = os.path.join(os.path.dirname(__file__), 'client_config.json')
            if os.path.exists(default_path):
                shutil.copy(default_path, config_path)
            else:
                # 创建一个最简默认配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write('{\n    "server": {"host": "127.0.0.1", "port": 5000, "protocol": "http"}\n}')

    def show_exam(self, exam_id):
        """显示考试视图（通过考试ID）"""
        if self.current_frame:
            self.current_frame.destroy()
        exam_info = {'id': exam_id}
        self.current_frame = ExamPageView(
            master=self,
            user_info=self.user_info,
            exam_info=exam_info,
            on_submit_callback=lambda: self.show_exam_list()
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_exam_page(self, user_info, exam):
        """显示考试页面（通过考试对象）"""
        print(f"show_exam_page被调用: 用户={user_info.get('username')}, 考试={exam.get('name')}")

        if self.current_frame:
            self.current_frame.destroy()

        # 使用完整的考试信息
        self.current_frame = ExamPageView(
            master=self,
            user_info=user_info,
            exam_info=exam,
            on_submit_callback=lambda: self.show_exam_list()
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        print(f"考试页面已创建并显示: {exam.get('name')}")

    def show_exam_list(self, user_info=None):
        """显示考试列表视图"""
        # 如果传入了用户信息，则设置到实例变量中
        if user_info:
            self.user_info = user_info
            print(f"设置用户信息: {user_info.get('username')} (ID: {user_info.get('id')})")

        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ExamListView(
            master=self,
            user_info=self.user_info,
            show_exam_callback=self.show_exam_page
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_login_view(self):
        """显示登录视图"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginView(
            self,
            show_exam_list_callback=self.show_exam_list
        )
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def __init__(self):
        try:
            super().__init__()
            self.title("PH&RL 考试系统 - 客户机")
            self.geometry("800x600")
            self.current_frame = None
            self.user_info = None
            self.is_fullscreen = False # 增加一个全屏状态的标志
            
            # 检查主控台是否运行
            if not self.check_main_console_running():
                logger.error("主控台未运行")
                messagebox.showerror("启动错误", "主控台未运行，请先启动主控台")
                self.destroy()
                return
            
            # 确保配置目录存在
            self.ensure_config_exists()
            
            # 显示登录视图
            self.show_login_view()
            
        except Exception as e:
            logger.critical(f"客户端初始化失败: {e}")
            messagebox.showerror("致命错误", f"客户端初始化失败: {e}\n请查看日志文件")
            self.destroy()
            sys.exit(1)
    
    

    def switch_frame(self, frame_class, *args):
        """用于切换页面的辅助函数"""
        if self.current_frame:
            self.current_frame.destroy()
        # 将 self (ExamClient 实例) 作为 master 传递给 Frame
        self.current_frame = frame_class(self, *args)
        # 将新 frame 打包到窗口中使其可见
        self.current_frame.pack(fill="both", expand=True)

    def set_fullscreen_mode(self, is_exam_page):
        """设置或退出全屏/防作弊模式"""
        if is_exam_page and not self.is_fullscreen:
            self.attributes('-fullscreen', True)
            self.attributes('-topmost', True) # 保持窗口在最前
            self.is_fullscreen = True
        elif not is_exam_page and self.is_fullscreen:
            self.attributes('-fullscreen', False)
            self.attributes('-topmost', False)
            self.is_fullscreen = False





if __name__ == "__main__":
    app = ExamClient()
    app.mainloop()