#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试答题界面

考试答题界面，支持多种题型答题、自动保存、时间控制等功能。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import TYPE_CHECKING, Dict, Any, List

from core.config import client_config
from core.auth import auth_manager
from core.api import api_client
from utils.logger import get_logger
from utils.storage import local_storage
from .components import QuestionNavigator

if TYPE_CHECKING:
    from core.app import ExamClientApp

logger = get_logger(__name__)

class ExamWindowView:
    """考试答题视图"""
    
    def __init__(self, parent: tk.Widget, app: 'ExamClientApp', exam_id: str):
        self.parent = parent
        self.app = app
        self.exam_id = exam_id
        self.exam_data = None
        self.questions = []
        self.current_question_index = 0
        self.answers = {}
        self.start_time = time.time()
        self.is_exam_active = True
        self.timer_job = None
        self.debug_mode = False
        
        # 创建主框架
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True)
        
        # 创建界面
        self._create_widgets()
        
        # 加载考试数据
        self._load_exam_data()
        
        # 启用防作弊模式
        self._enable_anti_cheat()
        
        logger.debug(f"考试答题界面已创建: {exam_id}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 顶部信息栏
        info_bar = ttk.Frame(self.frame, padding="10")
        info_bar.pack(fill='x')
        
        # 考试标题
        self.title_label = ttk.Label(
            info_bar,
            text="正在加载考试...",
            font=('Microsoft YaHei', 14, 'bold')
        )
        self.title_label.pack(side='left')
        
        # 时间显示
        self.time_label = ttk.Label(
            info_bar,
            text="剩余时间: --:--",
            font=('Microsoft YaHei', 12),
            foreground='red'
        )
        self.time_label.pack(side='right')
        
        # 分隔线
        separator1 = ttk.Separator(self.frame, orient='horizontal')
        separator1.pack(fill='x')
        
        # 题目导航区域（占位符）
        self.nav_frame = ttk.Frame(self.frame)
        self.nav_frame.pack(fill='x', padx=10, pady=5)
        
        # 分隔线
        separator2 = ttk.Separator(self.frame, orient='horizontal')
        separator2.pack(fill='x')
        
        # 题目内容区域
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 题目信息
        question_info_frame = ttk.Frame(content_frame)
        question_info_frame.pack(fill='x', pady=(0, 10))
        
        self.question_info_label = ttk.Label(
            question_info_frame,
            text="题目 1/20 (单选题)",
            font=('Microsoft YaHei', 12, 'bold')
        )
        self.question_info_label.pack(side='left')
        
        self.question_score_label = ttk.Label(
            question_info_frame,
            text="(5分)",
            font=('Microsoft YaHei', 10),
            foreground='blue'
        )
        self.question_score_label.pack(side='left', padx=(10, 0))
        
        # 题目内容
        self.question_text = tk.Text(
            content_frame,
            height=6,
            wrap='word',
            font=('Microsoft YaHei', 11),
            state='disabled',
            bg='#f8f9fa',
            relief='flat'
        )
        self.question_text.pack(fill='x', pady=(0, 20))
        
        # 答案区域
        self.answer_frame = ttk.LabelFrame(content_frame, text="请选择答案", padding="15")
        self.answer_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # 底部按钮区域
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill='x')
        
        # 上一题按钮
        self.prev_button = ttk.Button(
            button_frame,
            text="上一题",
            command=self._prev_question,
            state='disabled'
        )
        self.prev_button.pack(side='left')
        
        # 下一题按钮
        self.next_button = ttk.Button(
            button_frame,
            text="下一题",
            command=self._next_question
        )
        self.next_button.pack(side='left', padx=(10, 0))
        
        # 交卷按钮
        submit_button = ttk.Button(
            button_frame,
            text="交卷",
            command=self._submit_exam,
            style='Accent.TButton'
        )
        submit_button.pack(side='right')
        
        # 保存答案按钮
        save_button = ttk.Button(
            button_frame,
            text="保存答案",
            command=self._save_current_answer
        )
        save_button.pack(side='right', padx=(0, 10))
    
    def _load_exam_data(self):
        """加载考试数据"""
        def load_thread():
            try:
                # 模拟考试数据
                mock_exam_data = {
                    'id': self.exam_id,
                    'title': 'Python基础知识测试',
                    'duration': 60,  # 分钟
                    'questions': [
                        {
                            'id': 'q1',
                            'type': 'single_choice',
                            'content': 'Python中哪个关键字用于定义函数？',
                            'options': ['A. def', 'B. function', 'C. func', 'D. define'],
                            'score': 5
                        },
                        {
                            'id': 'q2',
                            'type': 'multiple_choice',
                            'content': 'Python中哪些是可变数据类型？（多选）',
                            'options': ['A. list', 'B. tuple', 'C. dict', 'D. set'],
                            'score': 10
                        },
                        {
                            'id': 'q3',
                            'type': 'true_false',
                            'content': 'Python是一种解释型语言。',
                            'options': ['A. 正确', 'B. 错误'],
                            'score': 5
                        }
                    ]
                }
                
                # 在主线程中更新UI
                self.parent.after(0, lambda: self._update_exam_data(mock_exam_data))
                
            except Exception as e:
                logger.error(f"加载考试数据失败: {e}")
                self.parent.after(0, lambda: self._show_error(f"加载考试数据失败: {e}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _update_exam_data(self, exam_data: Dict[str, Any]):
        """更新考试数据"""
        try:
            self.exam_data = exam_data
            self.questions = exam_data.get('questions', [])
            
            # 更新标题
            self.title_label.config(text=exam_data.get('title', '未知考试'))
            
            # 创建题目导航
            if self.questions:
                self.navigator = QuestionNavigator(
                    self.nav_frame,
                    len(self.questions),
                    self._on_question_navigate
                )
            
            # 加载保存的答案
            self._load_saved_answers()
            
            # 显示第一题
            if self.questions:
                self._show_question(0)
            
            # 启动计时器
            self._start_timer()
            
        except Exception as e:
            logger.error(f"更新考试数据失败: {e}")
            self._show_error(f"更新考试数据失败: {e}")
    
    def _show_question(self, index: int):
        """显示指定题目"""
        try:
            if not self.questions or index < 0 or index >= len(self.questions):
                return
            
            self.current_question_index = index
            question = self.questions[index]
            
            # 更新题目信息
            question_type_map = {
                'single_choice': '单选题',
                'multiple_choice': '多选题',
                'true_false': '判断题',
                'fill_blank': '填空题',
                'short_answer': '简答题',
                'essay': '论述题'
            }
            
            question_type = question_type_map.get(question.get('type'), '未知题型')
            self.question_info_label.config(
                text=f"题目 {index + 1}/{len(self.questions)} ({question_type})"
            )
            self.question_score_label.config(text=f"({question.get('score', 0)}分)")
            
            # 更新题目内容
            self.question_text.config(state='normal')
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(1.0, question.get('content', ''))
            self.question_text.config(state='disabled')
            
            # 更新答案区域
            self._update_answer_area(question)
            
            # 更新按钮状态
            self.prev_button.config(state='normal' if index > 0 else 'disabled')
            self.next_button.config(state='normal' if index < len(self.questions) - 1 else 'disabled')
            
            # 更新导航器
            if hasattr(self, 'navigator'):
                self.navigator.set_current_question(index)
            
        except Exception as e:
            logger.error(f"显示题目失败: {e}")
    
    def _update_answer_area(self, question: Dict[str, Any]):
        """更新答案区域"""
        # 清除现有组件
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
        
        question_type = question.get('type')
        question_id = question.get('id')
        
        if question_type in ['single_choice', 'true_false']:
            # 单选题/判断题
            self.answer_var = tk.StringVar()
            
            # 恢复保存的答案
            saved_answer = self.answers.get(question_id)
            if saved_answer:
                self.answer_var.set(saved_answer)
            
            for option in question.get('options', []):
                radio = ttk.Radiobutton(
                    self.answer_frame,
                    text=option,
                    variable=self.answer_var,
                    value=option,
                    command=self._on_answer_changed
                )
                radio.pack(anchor='w', pady=2)
                
        elif question_type == 'multiple_choice':
            # 多选题
            self.answer_vars = {}
            saved_answer = self.answers.get(question_id, [])
            
            for option in question.get('options', []):
                var = tk.BooleanVar()
                if option in saved_answer:
                    var.set(True)
                
                self.answer_vars[option] = var
                
                check = ttk.Checkbutton(
                    self.answer_frame,
                    text=option,
                    variable=var,
                    command=self._on_answer_changed
                )
                check.pack(anchor='w', pady=2)
                
        else:
            # 文本题（填空、简答、论述）
            self.answer_text = tk.Text(
                self.answer_frame,
                height=8,
                wrap='word',
                font=('Microsoft YaHei', 11)
            )
            self.answer_text.pack(fill='both', expand=True)
            
            # 恢复保存的答案
            saved_answer = self.answers.get(question_id, '')
            if saved_answer:
                self.answer_text.insert(1.0, saved_answer)
            
            # 绑定变化事件
            self.answer_text.bind('<KeyRelease>', lambda e: self._on_answer_changed())
    
    def _on_answer_changed(self):
        """答案变化回调"""
        try:
            question = self.questions[self.current_question_index]
            question_id = question.get('id')
            question_type = question.get('type')
            
            # 获取当前答案
            if question_type in ['single_choice', 'true_false']:
                answer = self.answer_var.get()
            elif question_type == 'multiple_choice':
                answer = [option for option, var in self.answer_vars.items() if var.get()]
            else:
                answer = self.answer_text.get(1.0, tk.END).strip()
            
            # 保存答案
            self.answers[question_id] = answer
            
            # 标记为已答
            if hasattr(self, 'navigator') and answer:
                self.navigator.mark_answered(self.current_question_index)
            
            # 自动保存到本地
            local_storage.save_exam_answer(self.exam_id, question_id, answer)
            
        except Exception as e:
            logger.error(f"处理答案变化失败: {e}")
    
    def _load_saved_answers(self):
        """加载保存的答案"""
        try:
            self.answers = local_storage.get_all_exam_answers(self.exam_id)
            logger.debug(f"加载了 {len(self.answers)} 个保存的答案")
        except Exception as e:
            logger.error(f"加载保存的答案失败: {e}")
    
    def _save_current_answer(self):
        """保存当前答案"""
        try:
            self._on_answer_changed()
            messagebox.showinfo("提示", "答案已保存")
        except Exception as e:
            logger.error(f"保存答案失败: {e}")
            messagebox.showerror("错误", f"保存答案失败: {e}")
    
    def _prev_question(self):
        """上一题"""
        if self.current_question_index > 0:
            self._show_question(self.current_question_index - 1)
    
    def _next_question(self):
        """下一题"""
        if self.current_question_index < len(self.questions) - 1:
            self._show_question(self.current_question_index + 1)
    
    def _on_question_navigate(self, question_index: int):
        """题目导航回调"""
        self._show_question(question_index)
    
    def _start_timer(self):
        """启动计时器"""
        def update_timer():
            if not self.is_exam_active:
                return
            
            try:
                duration_minutes = self.exam_data.get('duration', 60)
                elapsed_seconds = int(time.time() - self.start_time)
                remaining_seconds = duration_minutes * 60 - elapsed_seconds
                
                if remaining_seconds <= 0:
                    # 时间到，自动交卷
                    self._auto_submit_exam()
                    return
                
                # 更新时间显示
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                time_text = f"剩余时间: {minutes:02d}:{seconds:02d}"
                
                # 时间不足5分钟时变红
                if remaining_seconds <= 300:
                    self.time_label.config(text=time_text, foreground='red')
                else:
                    self.time_label.config(text=time_text, foreground='blue')
                
                # 1秒后再次更新
                self.timer_job = self.parent.after(1000, update_timer)
                
            except Exception as e:
                logger.error(f"更新计时器失败: {e}")
        
        update_timer()
    
    def _submit_exam(self):
        """交卷"""
        try:
            # 统计答题情况
            answered_count = len([a for a in self.answers.values() if a])
            total_count = len(self.questions)
            
            message = f"确定要交卷吗？\n\n"
            message += f"已答题目：{answered_count}/{total_count}\n"
            message += f"未答题目：{total_count - answered_count}\n\n"
            message += "交卷后无法修改答案。"
            
            result = messagebox.askyesno("确认交卷", message)
            if result:
                self._do_submit_exam()
                
        except Exception as e:
            logger.error(f"交卷确认失败: {e}")
            messagebox.showerror("错误", f"交卷确认失败: {e}")
    
    def _auto_submit_exam(self):
        """自动交卷（时间到）"""
        messagebox.showwarning("时间到", "考试时间已到，系统将自动交卷。")
        self._do_submit_exam()
    
    def _do_submit_exam(self):
        """执行交卷"""
        try:
            self.is_exam_active = False
            
            # 停止计时器
            if self.timer_job:
                self.parent.after_cancel(self.timer_job)
            
            # 提交答案到服务器（模拟）
            logger.info(f"考试已提交: {self.exam_id}")
            
            # 清除本地答案
            local_storage.clear_exam_data(self.exam_id)
            
            # 显示完成信息
            messagebox.showinfo("交卷成功", "考试已成功提交！\n\n感谢您的参与。")
            
            # 返回考试列表
            self.app.show_exam_list()
            
        except Exception as e:
            logger.error(f"交卷失败: {e}")
            messagebox.showerror("错误", f"交卷失败: {e}")
    
    def auto_submit_exam(self):
        """外部调用的自动交卷方法"""
        self._auto_submit_exam()
    
    def _enable_anti_cheat(self):
        """启用防作弊模式"""
        try:
            if client_config.get('security.enable_anti_cheat', True):
                # 检查是否为调试模式
                self.debug_mode = auth_manager.is_hidden_admin() and client_config.get('debug.enable_debug_mode', False)

                # 全屏模式
                if client_config.get('ui.fullscreen_exam', True):
                    self.parent.attributes('-fullscreen', True)

                # 置顶窗口
                self.parent.attributes('-topmost', True)

                # 禁用Alt+Tab等快捷键
                self.parent.bind('<Alt-Tab>', lambda e: 'break')
                self.parent.bind('<Control-Alt-Delete>', lambda e: 'break')
                self.parent.bind('<Alt-F4>', lambda e: 'break')

                # 绑定调试退出快捷键（仅调试模式）
                if self.debug_mode:
                    self.parent.bind('<Control-Shift-Q>', self._debug_exit)
                    logger.info("防作弊模式已启用（调试模式，Ctrl+Shift+Q退出）")
                else:
                    logger.info("防作弊模式已启用（生产模式）")

                # 启动防作弊监控
                from security.anti_cheat import anti_cheat_manager
                anti_cheat_manager.start_monitoring()

                # 监控窗口焦点
                self._start_focus_monitoring()

        except Exception as e:
            logger.error(f"启用防作弊模式失败: {e}")

    def _debug_exit(self, event=None):
        """调试模式退出功能"""
        if self.debug_mode:
            result = messagebox.askyesno(
                "调试退出",
                "确定要退出考试吗？\n（仅调试模式可用）",
                icon='warning'
            )
            if result:
                logger.info("调试模式退出考试")
                self.cleanup()
                self.app.show_exam_list()
        return 'break'

    def _start_focus_monitoring(self):
        """开始监控窗口焦点"""
        def check_focus():
            try:
                if self.is_exam_active:
                    # 检查窗口是否失去焦点
                    if self.parent.focus_get() is None:
                        logger.warning("检测到窗口失去焦点")
                        if not self.debug_mode:
                            # 生产模式下强制回到前台
                            self.parent.lift()
                            self.parent.focus_force()

                    # 继续监控
                    self.parent.after(1000, check_focus)
            except:
                pass

        # 开始监控
        self.parent.after(1000, check_focus)
    
    def _show_error(self, message: str):
        """显示错误信息"""
        messagebox.showerror("错误", message)
    
    def cleanup(self):
        """清理资源"""
        try:
            self.is_exam_active = False
            if self.timer_job:
                self.parent.after_cancel(self.timer_job)

            # 停止防作弊监控
            try:
                from security.anti_cheat import anti_cheat_manager
                anti_cheat_manager.stop_monitoring()
            except:
                pass

            # 退出全屏和置顶
            try:
                self.parent.attributes('-fullscreen', False)
                self.parent.attributes('-topmost', False)
            except:
                pass

            # 解绑快捷键
            try:
                self.parent.unbind('<Alt-Tab>')
                self.parent.unbind('<Control-Alt-Delete>')
                self.parent.unbind('<Alt-F4>')
                if self.debug_mode:
                    self.parent.unbind('<Control-Shift-Q>')
            except:
                pass

            logger.debug("考试答题界面已清理")

        except Exception as e:
            logger.error(f"考试答题界面清理失败: {e}")
    
    def destroy(self):
        """销毁界面"""
        try:
            self.cleanup()
            self.frame.destroy()
        except Exception as e:
            logger.error(f"销毁考试答题界面失败: {e}")
