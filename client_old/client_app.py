import tkinter as tk
from tkinter import messagebox
from api import *  # 改为绝对导入
import time
import json
import os

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
        
        # 准考证号输入
        username_frame = tk.Frame(form_frame, bg=self.colors['white'])
        username_frame.pack(fill=tk.X, pady=10)
        
        username_label = tk.Label(
            username_frame, 
            text="📋 准考证号:", 
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

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("错误", "准考证号和密码不能为空！")
            return

        user_info = api.login(username, password)

        if user_info:
            messagebox.showinfo("成功", f"欢迎，{user_info['username']}！")
            # 登录成功，通知主应用切换到考试列表页面
            self.show_exam_list(user_info)
        else:
            messagebox.showerror("登录失败", "准考证号或密码错误！")


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
        
        # 欢迎信息
        welcome_text = f"👋 欢迎, {self.user_info['username']}！"
        welcome_label = tk.Label(
            title_frame, 
            text=welcome_text, 
            font=("Microsoft YaHei", 20, "bold"),
            fg=self.colors['primary'],
            bg=self.colors['light']
        )
        welcome_label.pack()
        
        subtitle_label = tk.Label(
            title_frame, 
            text="请选择一场考试：", 
            font=("Microsoft YaHei", 14),
            fg=self.colors['dark'],
            bg=self.colors['light']
        )
        subtitle_label.pack(pady=(5, 0))

        # 考试列表容器
        list_container = tk.Frame(self, bg=self.colors['light'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # 获取并显示考试列表
        self.display_exams(list_container)

    def display_exams(self, container):
        exams = api.get_exams_for_student(self.user_info['id'])
        
        if not exams:
            # 没有考试时的提示
            no_exam_frame = tk.Frame(container, bg=self.colors['white'], relief="solid", borderwidth=1)
            no_exam_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            no_exam_label = tk.Label(
                no_exam_frame, 
                text="📝 暂无可用考试", 
                font=("Microsoft YaHei", 16),
                fg=self.colors['dark'],
                bg=self.colors['white']
            )
            no_exam_label.pack(expand=True)
            
            return
        
        for exam in exams:
            exam_frame = tk.Frame(
                container, 
                bg=self.colors['white'],
                relief="solid", 
                borderwidth=1
            )
            exam_frame.pack(fill=tk.X, padx=10, pady=5, expand=True)

            # 考试信息区域
            info_frame = tk.Frame(exam_frame, bg=self.colors['white'])
            info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)

            # 考试名称
            exam_name_label = tk.Label(
                info_frame, 
                text=exam['name'], 
                font=("Microsoft YaHei", 14, "bold"),
                fg=self.colors['dark'],
                bg=self.colors['white']
            )
            exam_name_label.pack(anchor=tk.W)
            
            # 获取考试详情，包括总分和及格分
            exam_details = api.get_exam_details(exam['id'])
            total_score = exam_details.get('total_score', 100)
            pass_score = exam_details.get('pass_score', 60)
            
            # 显示分数信息
            score_info_text = f"总分: {total_score} | 及格分: {pass_score}"
            score_info_label = tk.Label(
                info_frame, 
                text=score_info_text, 
                font=("Microsoft YaHei", 10),
                fg=self.colors['info'],
                bg=self.colors['white']
            )
            score_info_label.pack(anchor=tk.W, pady=(5, 0))
            
            # 考试状态
            status_text = "🟢 可参加" if exam['status'] == 'available' else "🔴 已完成"
            status_color = self.colors['success'] if exam['status'] == 'available' else self.colors['danger']
            
            status_label = tk.Label(
                info_frame, 
                text=status_text, 
                font=("Microsoft YaHei", 10),
                fg=status_color,
                bg=self.colors['white']
            )
            status_label.pack(anchor=tk.W, pady=(5, 0))

            # 按钮区域
            button_frame = tk.Frame(exam_frame, bg=self.colors['white'])
            button_frame.pack(side=tk.RIGHT, padx=15, pady=15)

            if exam['status'] == 'available':
                enter_button = tk.Button(
                    button_frame, 
                    text="🚀 进入考试", 
                    command=lambda e=exam: self.enter_exam(e),
                    font=("Microsoft YaHei", 12, "bold"),
                    bg=self.colors['primary'],
                    fg="white",
                    activebackground=self.colors['primary'],
                    activeforeground="white",
                    relief="flat",
                    borderwidth=0,
                    padx=20,
                    pady=8,
                    cursor="hand2"
                )
                enter_button.pack()
            else:
                status_label = tk.Label(
                    button_frame, 
                    text="✅ 已完成", 
                    font=("Microsoft YaHei", 12),
                    fg=self.colors['dark'],
                    bg=self.colors['light'],
                    relief="solid",
                    borderwidth=1,
                    padx=15,
                    pady=5
                )
                status_label.pack()
    
    def enter_exam(self, exam):
        # 获取考试详情，包括总分和及格分
        exam_details = api.get_exam_details(exam['id'])
        total_score = exam_details.get('total_score', 100)
        pass_score = exam_details.get('pass_score', 60)
        
        # 确认对话框，显示总分和及格分
        if messagebox.askyesno("确认", f"您确定要进入考试 '{exam['name']}' 吗？\n\n总分: {total_score}\n及格分: {pass_score}\n\n进入后将开始计时。"):
            # 通知主应用切换到答题页面
            self.show_exam_page(self.user_info, exam)


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
        
        self.exam_details = api.get_exam_details(self.exam_info['id'])
        self.questions = self.exam_details.get('questions', [])
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
                messagebox.showinfo("进度恢复", "检测到您有未完成的答题记录，已为您自动恢复。")
            except Exception as e:
                print(f"加载本地备份文件失败: {e}")
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
        except Exception as e:
            print(f"自动保存答案到本地文件失败: {e}")
    
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

    def show_question(self):
        # 清空上一题的内容
        for widget in self.question_frame.winfo_children():
            widget.destroy()

        if not self.questions:
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
        
        # 更新导航标签
        self.question_nav_label.config(text=f"第 {self.current_question_index + 1} / {len(self.questions)} 题")

        # 显示题干
        q_text = f"{self.current_question_index + 1}. ({question.get('type')}) {question.get('content')}"
        tk.Label(self.question_frame, text=q_text, font=("Microsoft YaHei", 14), justify=tk.LEFT, wraplength=700).pack(anchor='w', pady=10)
        
        # 根据题型创建选项
        q_type = question.get('type')
        options = question.get('options', [])

        if q_type == 'single' or q_type == 'true_false':
            # 单选或判断
            var = tk.StringVar(value=self.answers.get(q_id))
            self.answers[q_id] = var # 存储tk变量本身，方便之后获取值
            
            # 判断题的特殊处理
            if q_type == 'true_false':
                options = ['正确', '错误']

            for opt in options:
                rb = tk.Radiobutton(self.question_frame, text=opt, variable=var, value=opt, font=("Microsoft YaHei", 12))
                rb.pack(anchor='w', padx=20)

        elif q_type == 'multiple':
            # 多选
            vars = {}
            current_answers = self.answers.get(q_id, [])
            for opt in options:
                var = tk.BooleanVar(value=opt in current_answers)
                cb = tk.Checkbutton(self.question_frame, text=opt, variable=var, font=("Microsoft YaHei", 12))
                cb.pack(anchor='w', padx=20)
                vars[opt] = var
            self.answers[q_id] = vars # 存储所有选项的tk变量

        # 更新按钮状态
        self.prev_button.config(state=tk.NORMAL if self.current_question_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_question_index < len(self.questions) - 1 else tk.DISABLED)

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

    def next_question(self):
        self._save_current_answer()
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.show_question()

    def prev_question(self):
        self._save_current_answer()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.show_question()

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
        else:
            confirmed = messagebox.askyesno("确认交卷", "您确定要提交答卷吗？提交后将无法修改。")
        
        if confirmed:
            final_answers = self._get_clean_answers()

            result = api.submit_answers(self.exam_info['id'], self.user_info['id'], final_answers)
            if result and result.get("success"):
                # 获取考试详情，包括总分和及格分
                total_score = self.exam_details.get('total_score', 100)
                pass_score = self.exam_details.get('pass_score', 60)
                
                # 获取得分
                score = result.get("score", 0)
                
                # 判断是否及格
                pass_status = "及格" if score >= pass_score else "不及格"
                pass_color = "green" if score >= pass_score else "red"
                
                # 提交成功后，删除本地备份文件
                try:
                    if os.path.exists(self.backup_filepath):
                        os.remove(self.backup_filepath)
                except Exception as e:
                    print(f"删除本地备份文件失败: {e}")

                # 显示考试结果页面
                self.on_submit_callback(self.user_info, {
                    "exam_name": self.exam_details.get('name', '在线考试'),
                    "score": score,
                    "total_score": total_score,
                    "pass_score": pass_score,
                    "pass_status": pass_status,
                    "pass_color": "green" if score >= pass_score else "red"
                })
            else:
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
            text="考试结果", 
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
        
        # 得分信息
        score_frame = tk.Frame(result_frame, bg=self.colors['white'])
        score_frame.pack(pady=20)
        
        score = self.result_info.get('score', 0)
        total_score = self.result_info.get('total_score', 100)
        pass_score = self.result_info.get('pass_score', 60)
        pass_status = self.result_info.get('pass_status', '未知')
        pass_color = self.colors['success'] if score >= pass_score else self.colors['danger']
        
        # 大分数显示
        big_score_label = tk.Label(
            score_frame, 
            text=f"{score}", 
            font=("Microsoft YaHei", 48, "bold"),
            fg=pass_color,
            bg=self.colors['white']
        )
        big_score_label.pack()
        
        # 总分显示
        total_score_label = tk.Label(
            score_frame, 
            text=f"总分: {total_score}", 
            font=("Microsoft YaHei", 14),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        total_score_label.pack(pady=(0, 10))
        
        # 及格分显示
        pass_score_label = tk.Label(
            score_frame, 
            text=f"及格分: {pass_score}", 
            font=("Microsoft YaHei", 14),
            fg=self.colors['dark'],
            bg=self.colors['white']
        )
        pass_score_label.pack()
        
        # 及格状态
        pass_status_label = tk.Label(
            score_frame, 
            text=f"考试结果: {pass_status}", 
            font=("Microsoft YaHei", 16, "bold"),
            fg=pass_color,
            bg=self.colors['white']
        )
        pass_status_label.pack(pady=10)
        
        # 返回按钮
        back_button = tk.Button(
            result_frame, 
            text="返回考试列表", 
            command=lambda: self.on_back_callback(self.user_info),
            font=("Microsoft YaHei", 12),
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        back_button.pack(pady=30)


class ExamClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PH&RL 考试系统 - 客户机")
        self.geometry("800x600")
        self.current_frame = None
        self.user_info = None
        self.is_fullscreen = False # 增加一个全屏状态的标志
        self.show_login_view()

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

    def show_login_view(self):
        self.set_fullscreen_mode(False) # 确保登录页不是全屏
        self.switch_frame(LoginView, self.show_exam_list_view)

    def show_exam_list_view(self, user_info):
        """显示考试列表页面"""
        self.set_fullscreen_mode(False) # 确保考试列表页不是全屏
        self.user_info = user_info
        self.switch_frame(ExamListView, user_info, self.show_exam_page_view)

    def show_exam_page_view(self, user_info, exam_info):
        """显示答题页面"""
        self.set_fullscreen_mode(True) # 进入答题页，开启全屏
        self.user_info = user_info
        # 传入 self.show_exam_result_view 作为交卷后的回调
        self.switch_frame(ExamPageView, user_info, exam_info, self.show_exam_result_view)
    
    def show_exam_result_view(self, user_info, result_info=None):
        """显示考试结果页面"""
        self.set_fullscreen_mode(False) # 确保结果页不是全屏
        if result_info:
            self.switch_frame(ExamResultView, user_info, result_info, self.show_exam_list_view)
        else:
            self.show_exam_list_view(user_info)


if __name__ == "__main__":
    # 新增调试模式入口
    if __name__ == "__main__":
        app = ExamClient()
        app.run(debug=True)  # 启用详细日志输出
        app.mainloop()