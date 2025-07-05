#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试列表界面

显示可参加的考试列表，支持考试选择和开始考试。
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import TYPE_CHECKING, List, Dict, Any

from core.config import client_config
from core.auth import auth_manager
from core.api import api_client
from utils.logger import get_logger
from .components import LoadingDialog, ExamCard

if TYPE_CHECKING:
    from core.app import ExamClientApp

logger = get_logger(__name__)

class ExamListView:
    """考试列表视图"""
    
    def __init__(self, parent: tk.Widget, app: 'ExamClientApp'):
        self.parent = parent
        self.app = app
        self.exams = []
        
        # 创建主框架
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True)
        
        # 创建界面
        self._create_widgets()
        
        # 加载考试列表
        self._load_exam_list()
        
        logger.debug("考试列表界面已创建")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ttk.Frame(self.frame, padding="10")
        toolbar.pack(fill='x')
        
        # 标题
        title_label = ttk.Label(
            toolbar,
            text="可参加的考试",
            font=('Microsoft YaHei', 16, 'bold')
        )
        title_label.pack(side='left')
        
        # 用户信息
        user = auth_manager.get_current_user()
        if user:
            username = user.get('username', '未知用户')
            user_label = ttk.Label(
                toolbar,
                text=f"欢迎，{username}",
                font=('Microsoft YaHei', 10)
            )
            user_label.pack(side='right', padx=(0, 10))
        
        # 登出按钮
        logout_button = ttk.Button(
            toolbar,
            text="登出",
            command=self._logout
        )
        logout_button.pack(side='right')
        
        # 刷新按钮
        refresh_button = ttk.Button(
            toolbar,
            text="刷新",
            command=self._refresh_exam_list
        )
        refresh_button.pack(side='right', padx=(0, 10))
        
        # 分隔线
        separator = ttk.Separator(self.frame, orient='horizontal')
        separator.pack(fill='x', pady=5)
        
        # 考试列表容器
        self.exam_container = ttk.Frame(self.frame)
        self.exam_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 滚动框架
        self.canvas = tk.Canvas(self.exam_container, bg='white')
        self.scrollbar = ttk.Scrollbar(self.exam_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 状态标签
        self.status_label = ttk.Label(
            self.frame,
            text="正在加载考试列表...",
            font=('Microsoft YaHei', 10)
        )
        self.status_label.pack(pady=10)
    
    def _load_exam_list(self):
        """加载考试列表"""
        def load_thread():
            try:
                # 模拟考试数据（实际应该从API获取）
                mock_exams = [
                    {
                        'id': 'exam_001',
                        'title': 'Python基础知识测试',
                        'description': '测试Python基础语法、数据类型、控制结构等知识点',
                        'duration': 60,
                        'question_count': 20,
                        'status': 'available'
                    },
                    {
                        'id': 'exam_002', 
                        'title': '数据结构与算法',
                        'description': '考查常用数据结构和基本算法的理解与应用',
                        'duration': 90,
                        'question_count': 25,
                        'status': 'available'
                    },
                    {
                        'id': 'exam_003',
                        'title': '软件工程概论',
                        'description': '软件开发生命周期、项目管理、质量保证等内容',
                        'duration': 120,
                        'question_count': 30,
                        'status': 'completed'
                    }
                ]
                
                # 在主线程中更新UI
                self.parent.after(0, lambda: self._update_exam_list(mock_exams))
                
            except Exception as e:
                logger.error(f"加载考试列表失败: {e}")
                self.parent.after(0, lambda: self._show_error(f"加载考试列表失败: {e}"))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _update_exam_list(self, exams: List[Dict[str, Any]]):
        """更新考试列表显示"""
        try:
            # 清除现有内容
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            self.exams = exams
            
            if not exams:
                # 没有考试
                no_exam_label = ttk.Label(
                    self.scrollable_frame,
                    text="暂无可参加的考试",
                    font=('Microsoft YaHei', 12)
                )
                no_exam_label.pack(pady=50)
            else:
                # 显示考试卡片
                for exam in exams:
                    exam_card = ExamCard(
                        self.scrollable_frame,
                        exam,
                        self._on_exam_selected
                    )
            
            # 更新状态
            self.status_label.config(
                text=f"共找到 {len(exams)} 个考试",
                foreground='green'
            )
            
            # 5秒后隐藏状态
            self.parent.after(5000, lambda: self.status_label.config(text=""))
            
        except Exception as e:
            logger.error(f"更新考试列表失败: {e}")
            self._show_error(f"更新考试列表失败: {e}")
    
    def _on_exam_selected(self, exam_data: Dict[str, Any]):
        """考试选择回调"""
        try:
            exam_id = exam_data.get('id')
            exam_title = exam_data.get('title')
            status = exam_data.get('status')
            
            if status == 'completed':
                messagebox.showinfo("提示", "该考试已完成，无法重复参加")
                return
            
            if status != 'available' and status != 'in_progress':
                messagebox.showwarning("提示", "该考试当前不可参加")
                return
            
            # 确认开始考试
            message = f"确定要开始考试《{exam_title}》吗？\n\n"
            message += f"考试时长：{exam_data.get('duration', 0)}分钟\n"
            message += f"题目数量：{exam_data.get('question_count', 0)}题\n\n"
            message += "开始后将进入全屏模式，请确保环境安静。"
            
            result = messagebox.askyesno("确认开始考试", message)
            if result:
                logger.info(f"用户选择开始考试: {exam_id}")
                self.app.show_exam_window(exam_id)
                
        except Exception as e:
            logger.error(f"处理考试选择失败: {e}")
            self._show_error(f"处理考试选择失败: {e}")
    
    def _refresh_exam_list(self):
        """刷新考试列表"""
        self.status_label.config(text="正在刷新...", foreground='blue')
        self._load_exam_list()
    
    def _logout(self):
        """用户登出"""
        try:
            result = messagebox.askyesno("确认登出", "确定要登出吗？")
            if result:
                auth_manager.logout()
                logger.info("用户已登出")
                self.app.show_login()
                
        except Exception as e:
            logger.error(f"登出失败: {e}")
            self._show_error(f"登出失败: {e}")
    
    def _show_error(self, message: str):
        """显示错误信息"""
        self.status_label.config(text=message, foreground='red')
        messagebox.showerror("错误", message)
    
    def cleanup(self):
        """清理资源"""
        try:
            logger.debug("考试列表界面已清理")
        except Exception as e:
            logger.error(f"考试列表界面清理失败: {e}")
    
    def destroy(self):
        """销毁界面"""
        try:
            self.cleanup()
            self.frame.destroy()
        except Exception as e:
            logger.error(f"销毁考试列表界面失败: {e}")
