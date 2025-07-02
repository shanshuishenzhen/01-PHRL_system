#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试管理模块 - 核心功能模块
负责考试创建、配置、状态管理、时间控制等核心功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
from datetime import datetime, timedelta
import threading
import time
# 修复导入路径
import sys
import os
# 将当前目录添加到模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from paper_generator import PaperGenerator, PaperGenerationError

class SimpleExamManager:
    """简化版考试管理主类"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("考试管理 - PH&RL 在线考试系统")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        
        # 设置主题颜色
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40',
            'white': '#ffffff',
            'purple': '#9b59b6',
            'orange': '#e67e22'
        }
        
        # 考试数据存储
        self.exams = self.load_exams()
        self.current_page = 1
        self.page_size = 20
        
        # 考试状态定义
        self.exam_statuses = {
            'draft': '草稿',
            'published': '已发布',
            'ongoing': '进行中',
            'completed': '已完成',
            'archived': '已归档'
        }
        
        # 考试类型定义
        self.exam_types = {
            'practice': '练习考试',
            'formal': '正式考试',
            'mock': '模拟考试',
            'quiz': '小测验'
        }
        
        self.enrollments = self.load_enrollments()
        self.users = self.load_users()
        
        self.setup_ui()
        self.refresh_exam_list()
        
        # 启动状态更新线程
        self.start_status_update()
    
    def load_exams(self):
        """加载考试数据"""
        try:
            if os.path.exists('exam_management/exams.json'):
                with open('exam_management/exams.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载考试数据失败: {e}")
        
        # 返回默认考试数据
        return {
            "exams": [
                {
                    "id": 1,
                    "name": "2024年度计算机基础知识认证考试",
                    "type": "formal",
                    "status": "draft",
                    "description": "测试考生的计算机基础知识掌握程度",
                    "duration_minutes": 120,
                    "total_score": 100,
                    "pass_score": 60,
                    "start_time": "2024-02-01 09:00:00",
                    "end_time": "2024-02-01 11:00:00",
                    "question_bank_id": 1,
                    "allowed_departments": ["计算机系", "信息工程系"],
                    "max_participants": 100,
                    "current_participants": 0,
                    "created_by": "admin",
                    "created_at": "2024-01-15 10:00:00",
                    "updated_at": "2024-01-15 10:00:00"
                }
            ]
        }
    
    def save_exams(self):
        """保存考试数据"""
        try:
            os.makedirs('exam_management', exist_ok=True)
            with open('exam_management/exams.json', 'w', encoding='utf-8') as f:
                json.dump(self.exams, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存考试数据失败: {e}")
    
    def load_enrollments(self):
        """新增：加载报考数据"""
        try:
            path = os.path.join('exam_management', 'enrollments.json')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载报考数据失败: {e}")
        return {"enrollments": []}

    def save_enrollments(self):
        """新增：保存报考数据"""
        try:
            os.makedirs('exam_management', exist_ok=True)
            with open('exam_management/enrollments.json', 'w', encoding='utf-8') as f:
                json.dump(self.enrollments, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存报考数据失败: {e}")
    
    def create_new_exam(self):
        """创建一个新的考试对象"""
        # 生成新的考试ID
        max_id = 0
        for exam in self.exams.get("exams", []):
            if exam.get("id", 0) > max_id:
                max_id = exam.get("id")
        
        # 创建新考试对象
        new_exam = {
            "id": max_id + 1,
            "name": "",
            "type": "formal",
            "status": "draft",
            "description": "",
            "duration": 60,  # 与import_selected_paper方法中使用的字段名保持一致
            "duration_minutes": 60,  # 保留原有字段
            "total_score": 100,
            "pass_score": 60,
            "total_questions": 0,  # 添加total_questions字段
            "paper_id": None,  # 添加paper_id字段
            "question_ids": [],  # 添加question_ids字段
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "question_bank_id": None,
            "allowed_departments": [],
            "max_participants": 100,
            "current_participants": 0,
            "created_by": "admin",  # 这里可以替换为实际的用户名
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到考试列表
        self.exams.setdefault("exams", []).append(new_exam)
        
        return new_exam
    
    def load_users(self):
        """新增：加载用户数据（仅用于考生分配）"""
        try:
            path = os.path.join('user_management', 'users.json')
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("users", [])
        except Exception as e:
            print(f"加载用户数据失败: {e}")
        return []
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        self.create_toolbar(main_frame)
        
        # 搜索和筛选区域
        self.create_search_frame(main_frame)
        
        # 主要内容区域（左右分栏）
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # 左侧：考试列表
        self.create_exam_list_frame(content_frame)
        
        # 右侧：考试详情和操作
        self.create_exam_detail_frame(content_frame)
        
        # 分页控件
        self.create_pagination_frame(main_frame)
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 15))
        
        # 左侧标题区域
        title_frame = ttk.Frame(toolbar)
        title_frame.pack(side=tk.LEFT)
        
        # 标题图标和文字
        title_label = ttk.Label(
            title_frame, 
            text="📝 考试管理", 
            font=("Microsoft YaHei", 20, "bold"),
            foreground=self.colors['primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # 考试统计信息
        total_exams = len(self.exams.get("exams", []))
        ongoing_exams = len([exam for exam in self.exams.get("exams", []) 
                           if exam.get("status") == "ongoing"])
        
        stats_label = ttk.Label(
            title_frame,
            text=f"共 {total_exams} 场考试 | 进行中: {ongoing_exams}",
            font=("Microsoft YaHei", 10),
            foreground=self.colors['dark']
        )
        stats_label.pack(side=tk.LEFT, padx=(15, 0), pady=(5, 0))
        
        # 右侧按钮区域
        button_frame = ttk.Frame(toolbar)
        button_frame.pack(side=tk.RIGHT)
        
        # 按钮样式配置
        button_style = {
            "font": ("Microsoft YaHei", 10),
            "relief": "flat",
            "borderwidth": 0,
            "padx": 15,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # 新增考试按钮
        add_btn = tk.Button(
            button_frame, 
            text="➕ 新增考试", 
            command=self.add_exam,
            bg=self.colors['success'],
            fg="white",
            activebackground=self.colors['success'],
            activeforeground="white",
            **button_style
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 编辑考试按钮
        edit_btn = tk.Button(
            button_frame, 
            text="✏️ 编辑考试", 
            command=self.edit_exam,
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            **button_style
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # 发布考试按钮
        publish_btn = tk.Button(
            button_frame, 
            text="📢 发布考试", 
            command=self.publish_exam,
            bg=self.colors['purple'],
            fg="white",
            activebackground=self.colors['purple'],
            activeforeground="white",
            **button_style
        )
        publish_btn.pack(side=tk.LEFT, padx=5)
        
        # 删除考试按钮
        delete_btn = tk.Button(
            button_frame, 
            text="🗑️ 删除考试", 
            command=self.delete_exam,
            bg=self.colors['danger'],
            fg="white",
            activebackground=self.colors['danger'],
            activeforeground="white",
            **button_style
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 从题库导入试卷创建考试按钮
        import_paper_btn = tk.Button(
            button_frame, 
            text="📋 从题库导入试卷", 
            command=self.create_exam_from_question_bank,
            bg=self.colors['warning'],
            fg="white",
            activebackground=self.colors['warning'],
            activeforeground="white",
            **button_style
        )
        import_paper_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            button_frame, 
            text="🔄 刷新", 
            command=self.refresh_exam_list,
            bg=self.colors['info'],
            fg="white",
            activebackground=self.colors['info'],
            activeforeground="white",
            **button_style
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
    
    def create_search_frame(self, parent):
        """创建搜索和筛选区域"""
        search_frame = ttk.LabelFrame(
            parent, 
            text="🔍 搜索和筛选", 
            padding="10"
        )
        search_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 搜索框
        search_label = ttk.Label(
            search_frame, 
            text="搜索:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var, 
            width=25,
            font=("Microsoft YaHei", 10)
        )
        self.search_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # 状态筛选
        status_label = ttk.Label(
            search_frame, 
            text="状态:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        status_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_filter_var = tk.StringVar(value="全部")
        status_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.status_filter_var,
            values=["全部"] + list(self.exam_statuses.values()), 
            width=12,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        status_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 类型筛选
        type_label = ttk.Label(
            search_frame, 
            text="类型:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        type_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.type_filter_var = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.type_filter_var,
            values=["全部"] + list(self.exam_types.values()), 
            width=12,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        type_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 搜索按钮
        search_btn = tk.Button(
            search_frame, 
            text="🔍 搜索", 
            command=self.search_exams,
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            font=("Microsoft YaHei", 10),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # 重置按钮
        reset_btn = tk.Button(
            search_frame, 
            text="🔄 重置", 
            command=self.reset_search,
            bg=self.colors['warning'],
            fg="white",
            activebackground=self.colors['warning'],
            activeforeground="white",
            font=("Microsoft YaHei", 10),
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=5,
            cursor="hand2"
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def create_exam_list_frame(self, parent):
        """创建考试列表区域"""
        list_frame = ttk.LabelFrame(
            parent, 
            text="📋 考试列表", 
            padding="10"
        )
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 创建Treeview
        columns = ("ID", "考试名称", "类型", "状态", "开始时间", "结束时间", "参与人数", "创建时间")
        self.tree = ttk.Treeview(
            list_frame, 
            columns=columns, 
            show="headings", 
            height=20,
            style="Custom.Treeview"
        )
        
        # 设置列标题和宽度
        column_widths = {
            "ID": 60,
            "考试名称": 200,
            "类型": 80,
            "状态": 80,
            "开始时间": 120,
            "结束时间": 120,
            "参与人数": 80,
            "创建时间": 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self.edit_exam)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_exam_select)
    
    def create_exam_detail_frame(self, parent):
        """创建考试详情区域"""
        detail_frame = ttk.LabelFrame(
            parent, 
            text="📊 考试详情", 
            padding="10"
        )
        detail_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 详情内容区域
        self.detail_content = ttk.Frame(detail_frame)
        self.detail_content.pack(fill=tk.BOTH, expand=True)
        
        # 默认显示提示信息
        self.show_default_detail()
    
    def create_pagination_frame(self, parent):
        """创建分页控件"""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 分页信息
        self.page_info_label = ttk.Label(
            pagination_frame, 
            text="",
            font=("Microsoft YaHei", 10),
            foreground=self.colors['dark']
        )
        self.page_info_label.pack(side=tk.LEFT)
        
        # 分页按钮
        button_frame = ttk.Frame(pagination_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # 按钮样式
        page_button_style = {
            "font": ("Microsoft YaHei", 10),
            "relief": "flat",
            "borderwidth": 1,
            "padx": 12,
            "pady": 5,
            "cursor": "hand2"
        }
        
        prev_btn = tk.Button(
            button_frame, 
            text="◀ 上一页", 
            command=self.prev_page,
            bg=self.colors['light'],
            fg=self.colors['dark'],
            activebackground=self.colors['primary'],
            activeforeground="white",
            **page_button_style
        )
        prev_btn.pack(side=tk.LEFT, padx=2)
        
        next_btn = tk.Button(
            button_frame, 
            text="下一页 ▶", 
            command=self.next_page,
            bg=self.colors['light'],
            fg=self.colors['dark'],
            activebackground=self.colors['primary'],
            activeforeground="white",
            **page_button_style
        )
        next_btn.pack(side=tk.LEFT, padx=2)
    
    def show_default_detail(self):
        """显示默认详情信息"""
        # 清空现有内容
        for widget in self.detail_content.winfo_children():
            widget.destroy()
        
        # 显示提示信息
        info_label = ttk.Label(
            self.detail_content, 
            text="👆 请选择一个考试查看详细信息", 
            font=("Microsoft YaHei", 14),
            foreground=self.colors['dark']
        )
        info_label.pack(expand=True)
    
    def show_exam_detail(self, exam):
        """显示考试详细信息"""
        # 清空现有内容
        for widget in self.detail_content.winfo_children():
            widget.destroy()
        
        # 创建详情内容
        detail_info = [
            ("考试名称", exam.get("name", "")),
            ("考试类型", self.exam_types.get(exam.get("type"), exam.get("type"))),
            ("考试状态", self.exam_statuses.get(exam.get("status"), exam.get("status"))),
            ("考试描述", exam.get("description", "")),
            ("考试时长", f"{exam.get('duration_minutes', 0)} 分钟"),
            ("总分", f"{exam.get('total_score', 0)} 分"),
            ("及格分", f"{exam.get('pass_score', 0)} 分"),
            ("开始时间", exam.get("start_time", "")),
            ("结束时间", exam.get("end_time", "")),
            ("最大参与人数", f"{exam.get('max_participants', 0)} 人"),
            ("当前参与人数", f"{exam.get('current_participants', 0)} 人"),
            ("允许部门", ", ".join(exam.get("allowed_departments", []))),
            ("创建人", exam.get("created_by", "")),
            ("创建时间", exam.get("created_at", "")),
            ("更新时间", exam.get("updated_at", ""))
        ]
        
        # 创建详情表格
        for i, (label, value) in enumerate(detail_info):
            row_frame = ttk.Frame(self.detail_content)
            row_frame.pack(fill=tk.X, pady=2)
            
            label_widget = ttk.Label(
                row_frame, 
                text=f"{label}:", 
                font=("Microsoft YaHei", 10, "bold"),
                width=15
            )
            label_widget.pack(side=tk.LEFT)
            
            value_widget = ttk.Label(
                row_frame, 
                text=value, 
                font=("Microsoft YaHei", 10),
                wraplength=300
            )
            value_widget.pack(side=tk.LEFT, padx=(10, 0))
        
        # 添加操作按钮
        action_frame = ttk.Frame(self.detail_content, padding=(0, 10))
        action_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Label(action_frame, text="操作中心", font=("Microsoft YaHei", 12, "bold")).pack(anchor=tk.W)

        button_container = ttk.Frame(action_frame)
        button_container.pack(fill=tk.X, pady=10)

        # 新增：分配考生按钮
        assign_btn = tk.Button(button_container, text="👥 分配考生", command=lambda exam_id=exam.get("id"): self.assign_candidates(exam_id), bg=self.colors['purple'], fg="white", font=("Microsoft YaHei", 10), relief="flat", padx=15, pady=5)
        assign_btn.pack(side=tk.LEFT, padx=5)
        
        # 根据考试状态显示不同按钮
        status = exam.get("status")
        
        if status == "draft":
            # 草稿状态：可以编辑、发布
            tk.Button(
                button_container, 
                text="✏️ 编辑考试", 
                command=lambda exam_id=exam.get("id"): self.edit_exam_by_id(exam_id),
                bg=self.colors['primary'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_container, 
                text="📢 发布考试", 
                command=lambda exam_id=exam.get("id"): self.publish_exam_by_id(exam_id),
                bg=self.colors['success'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
        
        elif status == "published":
            # 已发布状态：可以开始、编辑
            tk.Button(
                button_container, 
                text="▶️ 开始考试", 
                command=lambda exam_id=exam.get("id"): self.start_exam_by_id(exam_id),
                bg=self.colors['success'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_container, 
                text="✏️ 编辑考试", 
                command=lambda exam_id=exam.get("id"): self.edit_exam_by_id(exam_id),
                bg=self.colors['primary'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
        
        elif status == "ongoing":
            # 进行中状态：可以结束、查看
            tk.Button(
                button_container, 
                text="⏹️ 结束考试", 
                command=lambda exam_id=exam.get("id"): self.end_exam_by_id(exam_id),
                bg=self.colors['danger'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_container, 
                text="📊 查看统计", 
                command=lambda exam_id=exam.get("id"): self.view_exam_stats(exam_id),
                bg=self.colors['info'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
        
        elif status == "completed":
            # 已完成状态：可以查看、归档
            tk.Button(
                button_container, 
                text="📊 查看成绩", 
                command=lambda exam_id=exam.get("id"): self.view_exam_results(exam_id),
                bg=self.colors['info'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
            
            tk.Button(
                button_container, 
                text="📁 归档考试", 
                command=lambda exam_id=exam.get("id"): self.archive_exam_by_id(exam_id),
                bg=self.colors['warning'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=5,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)
    
    def start_status_update(self):
        """启动状态更新线程"""
        def update_status():
            while True:
                try:
                    # 更新考试状态
                    self.update_exam_statuses()
                    time.sleep(30)  # 每30秒更新一次
                except:
                    break
        
        status_thread = threading.Thread(target=update_status, daemon=True)
        status_thread.start()
    
    def update_exam_statuses(self):
        """更新考试状态"""
        current_time = datetime.now()
        updated = False
        
        for exam in self.exams.get("exams", []):
            start_time = datetime.strptime(exam.get("start_time"), "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(exam.get("end_time"), "%Y-%m-%d %H:%M:%S")
            
            if exam.get("status") == "published" and current_time >= start_time:
                exam["status"] = "ongoing"
                exam["updated_at"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                updated = True
            # 彻底禁止自动完成，必须手动结束考试或所有考生交卷后才变为已完成
            # elif exam.get("status") == "ongoing" and current_time >= end_time:
            #     exam["status"] = "completed"
            #     exam["updated_at"] = current_time.strftime("%Y-%m-%d %H:%M:%S")
            #     updated = True
        
        if updated:
            self.save_exams()
            self.refresh_exam_list()
    
    def refresh_exam_list(self):
        """刷新考试列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取筛选后的考试列表
        filtered_exams = self.get_filtered_exams()
        
        # 计算分页
        total_exams = len(filtered_exams)
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_exams = filtered_exams[start_idx:end_idx]
        
        # 插入数据
        for i, exam in enumerate(page_exams):
            # 新增：获取已报名人数
            enrolled_count = 0
            enrollment_record = next((e for e in self.enrollments.get("enrollments", []) if e.get("exam_id") == exam.get("id")), None)
            if enrollment_record:
                enrolled_count = len(enrollment_record.get("user_ids", []))

            self.tree.insert("", tk.END, values=(
                exam.get("id"),
                exam.get("name"),
                self.exam_types.get(exam.get("type"), exam.get("type")),
                self.exam_statuses.get(exam.get("status"), exam.get("status")),
                exam.get("start_time"),
                exam.get("end_time"),
                f"{enrolled_count}/{exam.get('max_participants', 'N/A')}",
                exam.get("created_at")
            ))
        
        # 更新分页信息
        total_pages = (total_exams + self.page_size - 1) // self.page_size
        self.page_info_label.config(
            text=f"第 {self.current_page} 页，共 {total_pages} 页，总计 {total_exams} 场考试"
        )
    
    def get_filtered_exams(self):
        """获取筛选后的考试列表"""
        exams = self.exams.get("exams", [])
        filtered_exams = []
        
        for exam in exams:
            # 搜索筛选
            search_text = self.search_var.get().lower()
            if search_text:
                if (search_text not in exam.get("name", "").lower() and
                    search_text not in exam.get("description", "").lower()):
                    continue
            
            # 状态筛选
            status_filter = self.status_filter_var.get()
            if status_filter != "全部":
                exam_status = self.exam_statuses.get(exam.get("status"), exam.get("status"))
                if status_filter != exam_status:
                    continue
            
            # 类型筛选
            type_filter = self.type_filter_var.get()
            if type_filter != "全部":
                exam_type = self.exam_types.get(exam.get("type"), exam.get("type"))
                if type_filter != exam_type:
                    continue
            
            filtered_exams.append(exam)
        
        return filtered_exams
    
    def search_exams(self):
        """搜索考试"""
        self.current_page = 1
        self.refresh_exam_list()
    
    def reset_search(self):
        """重置搜索"""
        self.search_var.set("")
        self.status_filter_var.set("全部")
        self.type_filter_var.set("全部")
        self.current_page = 1
        self.refresh_exam_list()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_exam_list()
    
    def next_page(self):
        """下一页"""
        filtered_exams = self.get_filtered_exams()
        total_pages = (len(filtered_exams) + self.page_size - 1) // self.page_size
        
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_exam_list()
    
    def on_exam_select(self, event):
        """考试选择事件"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            exam_id = item['values'][0]
            exam = self.get_exam_by_id(exam_id)
            if exam:
                self.show_exam_detail(exam)
    
    def get_exam_by_id(self, exam_id):
        """根据ID获取考试对象"""
        for exam in self.exams.get("exams", []):
            if str(exam.get("id")) == str(exam_id): # 强制转换为字符串比较
                return exam
        return None
    
    def add_exam(self):
        """新增考试"""
        # 创建新增考试对话框
        dialog = ExamDialog(self.root, self, None)
        self.exam_dialog = dialog  # 保存对话框引用，以便在从题库导入试卷时使用
        self.root.wait_window(dialog.dialog)
        self.exam_dialog = None  # 清除引用
        self.refresh_exam_list()
        
    def create_exam_from_question_bank(self):
        """从题库导入试卷创建考试"""
        try:
            # 首先检查SQLite数据库文件是否存在
            db_path = os.path.join('question_bank_web', 'local_dev.db')
            if not os.path.exists(db_path):
                messagebox.showinfo("提示", f"题库数据库文件不存在: {db_path}")
                return
                
            # 创建ExamDialog对象并调用其load_papers_from_question_bank方法
            exam_dialog = ExamDialog(self.root, self, None)
            papers = exam_dialog.load_papers_from_question_bank()
            
            if not papers:
                messagebox.showinfo("提示", "未找到可导入的试卷。\n请确认题库管理模块已启动并已生成试卷。")
                return
                
            # 显示试卷选择对话框
            exam_dialog.show_paper_selection_dialog(papers)
        except Exception as e:
            messagebox.showerror("错误", f"从题库管理模块加载试卷失败: {e}")
            return
        if not papers:
            messagebox.showinfo("提示", "没有可用的试卷")
            return
        
        # 创建试卷选择对话框
        paper_dialog = tk.Toplevel(self.root)
        paper_dialog.title("选择试卷")
        paper_dialog.geometry("900x600")
        paper_dialog.transient(self.root)
        paper_dialog.grab_set()
        
        # 创建分割窗口
        paned = ttk.PanedWindow(paper_dialog, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧试卷列表框架
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # 右侧试卷详情框架
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        # 试卷列表标题
        ttk.Label(left_frame, text="可用试卷列表", font=("Microsoft YaHei", 12, "bold")).pack(pady=(0, 10))
        
        # 创建试卷列表
        columns = ("id", "name", "description", "total_score", "question_count", "created_at")
        tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        tree.heading("id", text="ID")
        tree.heading("name", text="试卷名称")
        tree.heading("description", text="描述")
        tree.heading("total_score", text="总分")
        tree.heading("question_count", text="题目数量")
        tree.heading("created_at", text="创建时间")
        
        # 设置列宽
        tree.column("id", width=50)
        tree.column("name", width=150)
        tree.column("description", width=200)
        tree.column("total_score", width=80)
        tree.column("question_count", width=80)
        tree.column("created_at", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 填充试卷数据
        for paper in papers:
            created_at = paper.get('created_at', '')
            if created_at and len(created_at) > 19:
                created_at = created_at[:19]  # 截取前19个字符，去除可能的毫秒部分
                
            tree.insert("", tk.END, values=(
                paper.get('id', ''),
                paper.get('name', ''),
                paper.get('description', '')[:30] + '...' if paper.get('description', '') and len(paper.get('description', '')) > 30 else paper.get('description', ''),
                paper.get('total_score', ''),
                paper.get('question_count', len(paper.get('questions', []))),
                created_at
            ))
        
        # 试卷详情标题
        ttk.Label(right_frame, text="试卷详情", font=("Microsoft YaHei", 12, "bold")).pack(pady=(0, 10))
        
        # 试卷详情文本区域
        detail_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=40, height=20)
        detail_text.pack(fill=tk.BOTH, expand=True)
        detail_text.config(state=tk.DISABLED)
        
        # 选择事件处理
        def on_select(event):
            selected_items = tree.selection()
            if not selected_items:
                return
            
            item = tree.item(selected_items[0])
            paper_id = item['values'][0]
            
            # 查找选中的试卷
            selected_paper = None
            for paper in papers:
                if paper.get('id') == paper_id:
                    selected_paper = paper
                    break
            
            if not selected_paper:
                return
            
            # 更新详情显示
            detail_text.config(state=tk.NORMAL)
            detail_text.delete(1.0, tk.END)
            
            # 统计题型分布
            question_types = {}
            for question in selected_paper.get('questions', []):
                q_type = question.get('type', '未知')
                question_types[q_type] = question_types.get(q_type, 0) + 1
            
            # 计算平均难度
            difficulties = [q.get('difficulty', 0) for q in selected_paper.get('questions', []) if q.get('difficulty') is not None]
            avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 0
            
            # 格式化详情信息
            detail_info = f"""试卷名称: {selected_paper.get('name', '')}

描述: {selected_paper.get('description', '')}

总分: {selected_paper.get('total_score', '')}

及格分: {selected_paper.get('pass_score', '')}

题目数量: {len(selected_paper.get('questions', []))}

平均难度: {avg_difficulty:.1f}

题型分布:
"""
            
            for q_type, count in question_types.items():
                detail_info += f"  - {q_type}: {count}题\n"
            
            detail_text.insert(tk.END, detail_info)
            detail_text.config(state=tk.DISABLED)
        
        tree.bind("<<TreeviewSelect>>", on_select)
        
        # 底部按钮框架
        button_frame = ttk.Frame(paper_dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 导入选中试卷按钮
        def import_selected_paper():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("警告", "请先选择一个试卷")
                return
            
            item = tree.item(selected_items[0])
            paper_id = item['values'][0]
            
            # 查找选中的试卷
            selected_paper = None
            for paper in papers:
                if paper.get('id') == paper_id:
                    selected_paper = paper
                    break
            
            if not selected_paper:
                messagebox.showerror("错误", "未找到选中的试卷")
                return
            
            # 确认导入
            if messagebox.askyesno("确认导入", f"确定要导入试卷 '{selected_paper.get('name', '')}' 创建新考试吗？"):
                # 提取题目ID
                question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                
                # 创建新考试对话框
                paper_dialog.destroy()
                exam_dialog = ExamDialog(self.root, self, None)
                
                # 设置试卷相关信息
                exam_dialog.paper_id_var.set(str(selected_paper.get('id', '')))
                exam_dialog.question_ids = question_ids
                exam_dialog.total_questions_var.set(str(len(question_ids)))
                exam_dialog.total_score_var.set(str(selected_paper.get('total_score', 100)))
                exam_dialog.pass_score_var.set(str(selected_paper.get('pass_score', 60)))
                
                # 设置考试名称和描述
                exam_dialog.name_var.set(f"{selected_paper.get('name', '')} - 考试")
                exam_dialog.description_var.set(selected_paper.get('description', ''))
        
        import_btn = tk.Button(
            button_frame,
            text="导入选中试卷",
            command=import_selected_paper,
            bg=self.colors['success'],
            fg="white",
            font=("Microsoft YaHei", 10),
            padx=15,
            pady=5
        )
        import_btn.pack(side=tk.RIGHT, padx=10)
        
        # 取消按钮
        cancel_btn = tk.Button(
            button_frame,
            text="取消",
            command=paper_dialog.destroy,
            bg=self.colors['light'],
            fg=self.colors['dark'],
            font=("Microsoft YaHei", 10),
            padx=15,
            pady=5
        )
        cancel_btn.pack(side=tk.RIGHT, padx=10)

    def edit_exam(self, event=None, exam_id=None):
        """编辑考试 - 核心实现"""
        if exam_id is None:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个考试")
                return
            item = self.tree.item(selection[0])
            exam_id = item['values'][0]
        
        exam = self.get_exam_by_id(exam_id)
        if exam:
            # 创建编辑考试对话框
            dialog = ExamDialog(self.root, self, exam)
            self.root.wait_window(dialog.dialog)
            self.refresh_exam_list()
        else:
            messagebox.showerror("错误", "未找到指定的考试")

    def publish_exam(self, event=None, exam_id=None):
        """发布考试 - 核心实现"""
        if exam_id is None:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个考试")
                return
            item = self.tree.item(selection[0])
            exam_id = item['values'][0]

        exam = self.get_exam_by_id(exam_id)
        if exam:
            if exam['status'] != 'draft':
                messagebox.showinfo("提示", f"考试 '{exam['name']}' 当前状态为 '{self.exam_statuses.get(exam['status'])}'，无法发布。")
                return

            # 自动校验并修正考试时间，防止刚发布就结束
            now = datetime.now()
            # 容错处理：如果时间字段缺失或格式错误，直接用当前时间
            try:
                start_time = datetime.strptime(exam.get("start_time") or now.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            except Exception:
                start_time = now
            try:
                end_time = datetime.strptime(exam.get("end_time") or (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            except Exception:
                end_time = start_time + timedelta(days=1)
            if start_time < now:
                # 如果开始时间早于当前，自动设置为当前时间+1分钟
                start_time = now + timedelta(minutes=1)
                exam["start_time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
            if end_time <= start_time:
                # 如果结束时间早于或等于开始时间，自动设置为开始时间+1天
                end_time = start_time + timedelta(days=1)
                exam["end_time"] = end_time.strftime("%Y-%m-%d %H:%M:%S")

            if messagebox.askyesno("确认发布", f"确定要发布考试 '{exam['name']}' 吗？\n\n实际考试时间：\n开始：{exam['start_time']}\n结束：{exam['end_time']}"):
                exam["status"] = "published"
                exam["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_exams()
                self.refresh_exam_list()
                self.show_exam_detail(exam)
                messagebox.showinfo("成功", "考试已发布")
        else:
            messagebox.showerror("错误", "未找到指定的考试")
    
    def delete_exam(self):
        """删除考试"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择至少一个考试")
            return
        
        # 获取所有选中的考试ID
        exam_ids = []
        for selected_item in selection:
            item = self.tree.item(selected_item)
            exam_ids.append(item['values'][0])
        
        # 确认删除信息
        confirm_message = "确定要删除选中的考试吗？" if len(exam_ids) == 1 else f"确定要删除选中的 {len(exam_ids)} 个考试吗？"
        confirm_message += "此操作不可恢复。"
        
        if messagebox.askyesno("确认删除", confirm_message):
            # 删除所有选中的考试
            self.exams["exams"] = [exam for exam in self.exams["exams"] if exam.get("id") not in exam_ids]
            self.save_exams()
            self.refresh_exam_list()
            self.show_default_detail() # 删除后显示默认信息
            
            # 显示成功信息
            success_message = "考试已删除" if len(exam_ids) == 1 else f"{len(exam_ids)} 个考试已删除"
            messagebox.showinfo("成功", success_message)
    
    def edit_exam_by_id(self, exam_id):
        """根据ID编辑考试"""
        print(f"--- DEBUG: edit_exam_by_id an ID: {exam_id} ---")
        self.edit_exam(exam_id=exam_id)
    
    def publish_exam_by_id(self, exam_id):
        """根据ID发布考试"""
        print(f"--- DEBUG: publish_exam_by_id an ID: {exam_id} ---")
        self.publish_exam(exam_id=exam_id)
    
    def start_exam_by_id(self, exam_id):
        """根据ID开始考试"""
        exam = self.get_exam_by_id(exam_id)
        if exam:
            if messagebox.askyesno("确认开始", f"确定要开始考试 '{exam['name']}' 吗？"):
                exam["status"] = "ongoing"
                exam["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_exams()
                self.refresh_exam_list()
                messagebox.showinfo("成功", "考试已开始")
        else:
            messagebox.showerror("错误", "未找到指定的考试")
    
    def end_exam_by_id(self, exam_id):
        """根据ID结束考试"""
        exam = self.get_exam_by_id(exam_id)
        if exam:
            if messagebox.askyesno("确认结束", f"确定要结束考试 '{exam['name']}' 吗？"):
                exam["status"] = "completed"
                exam["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_exams()
                self.refresh_exam_list()
                messagebox.showinfo("成功", "考试已结束")
        else:
            messagebox.showerror("错误", "未找到指定的考试")
    
    def view_exam_stats(self, exam_id):
        """查看考试统计"""
        exam = self.get_exam_by_id(exam_id)
        if exam:
            stats_text = f"""
考试统计信息

考试名称: {exam['name']}
考试状态: {self.exam_statuses.get(exam['status'], exam['status'])}
开始时间: {exam['start_time']}
结束时间: {exam['end_time']}
参与人数: {exam.get('current_participants', 0)}/{exam.get('max_participants', 0)}
完成人数: {exam.get('completed_participants', 0)}
平均分: {exam.get('average_score', 0)}
最高分: {exam.get('highest_score', 0)}
最低分: {exam.get('lowest_score', 0)}
            """
            messagebox.showinfo("考试统计", stats_text)
        else:
            messagebox.showerror("错误", "未找到指定的考试")
    
    def view_exam_results(self, exam_id):
        """查看考试结果"""
        exam = self.get_exam_by_id(exam_id)
        if exam:
            results_text = f"""
考试结果

考试名称: {exam['name']}
考试状态: {self.exam_statuses.get(exam['status'], exam['status'])}
参与人数: {exam.get('current_participants', 0)}
完成人数: {exam.get('completed_participants', 0)}
平均分: {exam.get('average_score', 0)}
最高分: {exam.get('highest_score', 0)}
最低分: {exam.get('lowest_score', 0)}

详细成绩请查看成绩统计模块。
            """
            messagebox.showinfo("考试结果", results_text)
        else:
            messagebox.showerror("错误", "未找到指定的考试")
    
    def archive_exam_by_id(self, exam_id):
        """根据ID归档考试"""
        exam = self.get_exam_by_id(exam_id)
        if exam:
            if messagebox.askyesno("确认归档", f"确定要归档考试 '{exam['name']}' 吗？\n归档后将无法修改。"):
                exam["status"] = "archived"
                exam["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_exams()
                self.refresh_exam_list()
                messagebox.showinfo("成功", "考试已归档")
        else:
            messagebox.showerror("错误", "未找到指定的考试")
    
    def assign_candidates(self, exam_id):
        """新增：打开分配考生对话框"""
        if not exam_id:
            messagebox.showerror("错误", "请先选择一场考试")
            return
        
        exam = self.get_exam_by_id(exam_id)
        if not exam:
            messagebox.showerror("错误", "找不到该考试的信息")
            return
            
        dialog = EnrollmentDialog(self.root, self, exam_id)
        self.root.wait_window(dialog.dialog)
        self.refresh_exam_list() # 分配完成后刷新列表
    
    def open_paper_generator_dialog(self, exam_id):
        """打开智能组卷对话框。"""
        PaperGeneratorDialog(self.root, self, exam_id)
    
    def run(self):
        """运行主应用循环"""
        self.root.mainloop()

# === 升级 EnrollmentDialog 类 ===
class EnrollmentDialog:
    def __init__(self, parent, manager, exam_id):
        self.manager = manager
        self.exam_id = exam_id
        self.exam = self.manager.get_exam_by_id(exam_id)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"批量报考处理 - '{self.exam.get('name')}'")
        self.dialog.geometry("1000x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 获取所有考生和已报名的考生ID
        all_candidates = [u for u in self.manager.users if u.get("role") == "student"]
        self.candidate_map = {u.get("id"): u for u in all_candidates} # ID到用户对象的映射

        enrollment_record = next((e for e in self.manager.enrollments.get("enrollments", []) if e.get("exam_id") == self.exam_id), {})
        enrolled_user_ids = set(enrollment_record.get("user_ids", []))
        
        # 确保admin用户被添加到已报名列表中
        admin_user = next((u for u in self.manager.users if u.get("username") == "admin"), None)
        if admin_user:
            admin_id = admin_user.get("id")
            if admin_id:
                enrolled_user_ids.add(admin_id)
                print(f"已自动将admin用户(ID:{admin_id})添加到考试{self.exam_id}的报名列表中")
        
        self.available_ids = set(self.candidate_map.keys()) - enrolled_user_ids
        self.enrolled_ids = enrolled_user_ids

        self.setup_ui()
        self.populate_lists()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 可选考生区域
        available_frame = ttk.LabelFrame(main_frame, text="可选考生", padding=10)
        available_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # --- 筛选和导入控件 ---
        filter_controls_frame = ttk.Frame(available_frame)
        filter_controls_frame.pack(fill="x", pady=(0, 10))
        
        self.search_var = tk.StringVar()
        ttk.Entry(filter_controls_frame, textvariable=self.search_var, width=20).pack(side="left", padx=(0,5))
        
        all_departments = sorted(list(set(u.get("department", "未分配") for u in self.candidate_map.values())))
        self.department_var = tk.StringVar()
        ttk.Combobox(filter_controls_frame, textvariable=self.department_var, values=["所有部门"] + all_departments, state="readonly").pack(side="left", padx=5)
        self.department_var.set("所有部门")
        
        tk.Button(filter_controls_frame, text="🔍 筛选", command=self.filter_candidates).pack(side="left", padx=5)
        tk.Button(filter_controls_frame, text="📥 从文件导入", command=self.import_from_file).pack(side="right")

        self.available_listbox = tk.Listbox(available_frame, selectmode="extended", height=20)
        self.available_listbox.pack(fill="both", expand=True)

        # 中间控制按钮区域
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(side="left", fill="y", padx=10)
        tk.Button(controls_frame, text=">", command=self.move_selected_to_enrolled).pack(pady=5)
        tk.Button(controls_frame, text=">>", command=self.move_all_to_enrolled).pack(pady=5)
        tk.Button(controls_frame, text="<", command=self.move_selected_to_available).pack(pady=5)
        tk.Button(controls_frame, text="<<", command=self.move_all_to_available).pack(pady=5)

        # 已选考生区域
        enrolled_frame = ttk.LabelFrame(main_frame, text="已选考生", padding=10)
        enrolled_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        self.enrolled_count_label = ttk.Label(enrolled_frame, text="已选：0 人")
        self.enrolled_count_label.pack(anchor="w")
        self.enrolled_listbox = tk.Listbox(enrolled_frame, selectmode="extended", height=20)
        self.enrolled_listbox.pack(fill="both", expand=True)
        
        # 底部保存按钮
        bottom_frame = ttk.Frame(self.dialog, padding=10)
        bottom_frame.pack(fill="x")
        tk.Button(bottom_frame, text="保存", command=self.save_enrollments).pack(side="right", padx=5)
        tk.Button(bottom_frame, text="取消", command=self.dialog.destroy).pack(side="right")

    def populate_lists(self, search_term="", department="所有部门"):
        self.available_listbox.delete(0, "end")
        self.enrolled_listbox.delete(0, "end")

        # 填充可选列表
        display_ids = sorted(list(self.available_ids))
        for user_id in display_ids:
            user = self.candidate_map.get(user_id)
            if user:
                # 筛选逻辑
                dep_match = (department == "所有部门" or user.get("department") == department)
                search_match = (search_term.lower() in user.get("real_name", "").lower() or 
                                search_term in user.get("username", "") or
                                search_term in user.get("ID", ""))
                if dep_match and search_match:
                    self.available_listbox.insert("end", f"{user.get('real_name')} ({user.get('username')})")
        
        # 填充已选列表
        # 确保所有ID都是字符串类型再排序，避免字符串和整数比较错误
        enrolled_display_ids = sorted([str(user_id) for user_id in self.enrolled_ids])
        for user_id in enrolled_display_ids:
            # 由于candidate_map可能使用整数或字符串作为键，尝试两种类型
            user = self.candidate_map.get(user_id) or self.candidate_map.get(int(user_id) if user_id.isdigit() else user_id)
            if user:
                self.enrolled_listbox.insert("end", f"{user.get('real_name')} ({user.get('username')})")
        
        self.update_enrolled_count()

    def filter_candidates(self):
        self.populate_lists(self.search_var.get(), self.department_var.get())

    def update_enrolled_count(self):
        self.enrolled_count_label.config(text=f"已选：{len(self.enrolled_ids)} 人")

    def _get_user_id_from_listbox_string(self, s):
        username = s.split('(')[1][:-1]
        for user_id, user in self.candidate_map.items():
            if user.get("username") == username:
                return user_id
        return None

    def move_selected_to_enrolled(self):
        selected_strings = [self.available_listbox.get(i) for i in self.available_listbox.curselection()]
        for s in selected_strings:
            user_id = self._get_user_id_from_listbox_string(s)
            if user_id:
                self.available_ids.remove(user_id)
                self.enrolled_ids.add(user_id)
        self.filter_candidates() # 刷新列表

    def move_all_to_enrolled(self):
        # 移动当前所有可见的
        visible_user_strings = self.available_listbox.get(0, "end")
        for s in visible_user_strings:
            user_id = self._get_user_id_from_listbox_string(s)
            if user_id:
                self.available_ids.remove(user_id)
                self.enrolled_ids.add(user_id)
        self.filter_candidates()

    def move_selected_to_available(self):
        selected_strings = [self.enrolled_listbox.get(i) for i in self.enrolled_listbox.curselection()]
        for s in selected_strings:
            user_id = self._get_user_id_from_listbox_string(s)
            if user_id:
                self.enrolled_ids.remove(user_id)
                self.available_ids.add(user_id)
        self.filter_candidates()

    def move_all_to_available(self):
        # 移动所有已报名的
        for user_id in list(self.enrolled_ids):
            self.enrolled_ids.remove(user_id)
            self.available_ids.add(user_id)
        self.filter_candidates()

    def import_from_file(self):
        file_path = filedialog.askopenfilename(title="选择考生名单文件", filetypes=[("文本文件", "*.txt"), ("CSV文件", "*.csv"), ("所有文件", "*.*")])
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                identifiers = [line.strip() for line in f if line.strip()]
            
            moved_count = 0
            not_found = []
            
            # 创建反向查找映射
            username_map = {u.get("username"): u_id for u_id, u in self.candidate_map.items()}
            id_card_map = {u.get("ID"): u_id for u_id, u in self.candidate_map.items() if u.get("ID")}
            
            for identifier in identifiers:
                user_id = username_map.get(identifier) or id_card_map.get(identifier)
                if user_id and user_id in self.available_ids:
                    self.available_ids.remove(user_id)
                    self.enrolled_ids.add(user_id)
                    moved_count += 1
                elif not user_id:
                    not_found.append(identifier)
            
            self.filter_candidates()
            msg = f"成功导入并移动了 {moved_count} 名考生。"
            if not_found:
                msg += f"\n\n以下 {len(not_found)} 个标识符未找到或无法匹配考生：\n{', '.join(not_found[:10])}"
                if len(not_found) > 10: msg += "..."
            messagebox.showinfo("导入完成", msg)

        except Exception as e:
            messagebox.showerror("导入失败", str(e))

    def save_enrollments(self):
        # 找到或创建当前考试的报名记录
        enrollment_record = next((e for e in self.manager.enrollments.get("enrollments", []) if e.get("exam_id") == self.exam_id), None)
        
        # 确保admin用户被添加到已报名列表中
        admin_user = next((u for u in self.manager.users if u.get("username") == "admin"), None)
        if admin_user:
            admin_id = admin_user.get("id")
            if admin_id and admin_id not in self.enrolled_ids:
                self.enrolled_ids.add(admin_id)
                print(f"在保存时确保admin用户(ID:{admin_id})添加到考试{self.exam_id}的报名列表中")
        
        if enrollment_record:
            enrollment_record["user_ids"] = list(self.enrolled_ids)
        else:
            # 如果是新考试，确保 enrollments["enrollments"] 存在
            if "enrollments" not in self.manager.enrollments:
                self.manager.enrollments["enrollments"] = []
                
            self.manager.enrollments["enrollments"].append({
                "exam_id": self.exam_id,
                "user_ids": list(self.enrolled_ids)
            })
            
        self.manager.save_enrollments()
        messagebox.showinfo("成功", "报考关系已成功保存！", parent=self.dialog)
        self.dialog.destroy()

# === 新增 PaperGeneratorDialog 类 ===
class PaperGeneratorDialog:
    def __init__(self, parent, manager, exam_id):
        self.manager = manager
        self.exam_id = exam_id
        self.exam = self.manager.get_exam_by_id(exam_id)

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"为 '{self.exam.get('name')}' 智能组卷")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.all_questions = self.load_full_question_bank()
        if not self.all_questions:
            messagebox.showerror("错误", "无法加载题库文件 questions.json！", parent=self.dialog)
            self.dialog.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_button_frame = ttk.Frame(main_frame)
        top_button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(top_button_frame, text="载入官方蓝图", command=self.load_blueprint).pack(side="left")
        ttk.Label(top_button_frame, text="<-- 可载入官方题库模板作为编辑起点").pack(side="left", padx=10)
        
        # 添加从题库管理模块导入试卷的按钮
        ttk.Button(top_button_frame, text="从题库导入试卷", command=self.import_paper_from_question_bank).pack(side="left", padx=(20, 0))
        ttk.Label(top_button_frame, text="<-- 从题库管理模块导入已生成的试卷").pack(side="left", padx=10)
        
        # 分数设置区域
        score_frame = ttk.LabelFrame(main_frame, text="分数设置")
        score_frame.pack(fill="x", pady=(0, 10))
        
        # 总分设置
        total_score_frame = ttk.Frame(score_frame)
        total_score_frame.pack(fill="x", pady=5, padx=5)
        
        ttk.Label(total_score_frame, text="试卷总分:", width=15).pack(side=tk.LEFT)
        self.total_score_var = tk.IntVar(value=self.exam.get("total_score", 100))
        total_score_spinbox = ttk.Spinbox(total_score_frame, from_=10, to=1000, textvariable=self.total_score_var, width=10)
        total_score_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 及格分设置
        pass_score_frame = ttk.Frame(score_frame)
        pass_score_frame.pack(fill="x", pady=5, padx=5)
        
        ttk.Label(pass_score_frame, text="及格分:", width=15).pack(side=tk.LEFT)
        self.pass_score_var = tk.IntVar(value=self.exam.get("pass_score", 60))
        self.pass_score_spinbox = ttk.Spinbox(pass_score_frame, from_=0, to=1000, textvariable=self.pass_score_var, width=10)
        self.pass_score_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 及格百分比设置
        pass_percentage_frame = ttk.Frame(score_frame)
        pass_percentage_frame.pack(fill="x", pady=5, padx=5)
        
        ttk.Label(pass_percentage_frame, text="及格百分比(%):", width=15).pack(side=tk.LEFT)
        self.pass_percentage_var = tk.IntVar(value=int((self.exam.get("pass_score", 60) / self.exam.get("total_score", 100)) * 100))
        pass_percentage_spinbox = ttk.Spinbox(pass_percentage_frame, from_=0, to=100, textvariable=self.pass_percentage_var, width=10)
        pass_percentage_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 计算按钮
        calculate_btn = ttk.Button(pass_percentage_frame, text="计算及格分", command=self.calculate_pass_score)
        calculate_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 绑定事件，当总分或及格百分比变化时自动计算及格分
        self.total_score_var.trace_add("write", lambda *args: self.calculate_pass_score())
        self.pass_percentage_var.trace_add("write", lambda *args: self.calculate_pass_score())
        
        template_frame = ttk.LabelFrame(main_frame, text="组卷模板 (JSON格式)")
        template_frame.pack(fill="both", expand=True)
        self.template_text = scrolledtext.ScrolledText(template_frame, wrap=tk.WORD, height=20, font=("Courier New", 10))
        self.template_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.load_existing_template()

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(10, 0))
        self.status_label = ttk.Label(bottom_frame, text="状态：准备就绪")
        self.status_label.pack(side="left")
        ttk.Button(bottom_frame, text="关闭", command=self.dialog.destroy).pack(side="right")
        ttk.Button(bottom_frame, text="开始组卷", command=self.run_generation).pack(side="right", padx=10)

    def load_full_question_bank(self):
        try:
            q_bank_path = os.path.join('question_bank_web', 'questions.json')
            if not os.path.exists(q_bank_path):
                self.status_label.config(text="题库文件不存在")
                return None
            with open(q_bank_path, 'r', encoding='utf-8') as f:
                return json.load(f).get('questions', [])
        except Exception as e:
            self.status_label.config(text=f"题库加载失败: {str(e)}")
            return None
    
    def load_papers_from_question_bank(self):
        """从题库管理模块加载试卷列表"""
        try:
            # 尝试从题库管理模块的数据库中读取试卷信息
            # 首先检查SQLite数据库文件是否存在
            db_path = os.path.join('question_bank_web', 'local_dev.db')
            if not os.path.exists(db_path):
                print(f"题库数据库文件不存在: {db_path}")
                return []
                
            # 使用SQLite直接读取数据库
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询试卷表
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.total_score, 
                       COALESCE(p.pass_score, p.total_score * 0.6) as pass_score, 
                       p.duration, p.difficulty_level, p.created_at,
                       COUNT(pq.question_id) as question_count
                FROM papers p
                LEFT JOIN paper_questions pq ON p.id = pq.paper_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
            """)
            
            papers = []
            for row in cursor.fetchall():
                paper = dict(row)
                # 查询该试卷的所有题目
                cursor.execute("""
                    SELECT q.id, q.question_type_code as type, q.stem, 
                           json_object('A', q.option_a, 'B', q.option_b, 'C', q.option_c, 'D', q.option_d, 'E', q.option_e) as options, 
                           q.correct_answer as answer, q.analysis, q.difficulty_code as difficulty, 
                           pq.score, pq.question_order
                    FROM questions q
                    JOIN paper_questions pq ON q.id = pq.question_id
                    WHERE pq.paper_id = ?
                    ORDER BY pq.question_order
                """, (paper['id'],))
                
                questions = []
                for q_row in cursor.fetchall():
                    q = dict(q_row)
                    # 将stem字段的值赋给content字段，以保持与papers.json的兼容性
                    if 'stem' in q:
                        q['content'] = q.pop('stem')
                    # 处理选项字段，从JSON字符串转换为Python对象
                    if q['options'] and q['options'].strip():
                        try:
                            q['options'] = json.loads(q['options'])
                        except json.JSONDecodeError:
                            q['options'] = []
                    else:
                        q['options'] = []
                    questions.append(q)
                
                paper['questions'] = questions
                papers.append(paper)
            
            conn.close()
            print(f"从题库管理模块成功加载了 {len(papers)} 份试卷")
            return papers
        except Exception as e:
            print(f"从题库管理模块加载试卷失败: {e}")
            return []
            
    def load_blueprint(self):
        try:
            blueprint_path = os.path.join('developer_tools', 'question_bank_blueprint.json')
            with open(blueprint_path, 'r', encoding='utf-8') as f:
                blueprint_content = json.dumps(json.load(f), ensure_ascii=False, indent=4)
                self.template_text.delete('1.0', tk.END)
                self.template_text.insert('1.0', blueprint_content)
                self.status_label.config(text="状态：已载入官方蓝图，请按需修改题目数量。")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("错误", f"加载蓝图失败: {e}", parent=self.dialog)

    def load_existing_template(self):
        paper_template = self.exam.get("paper_template")
        if paper_template:
            self.template_text.insert('1.0', json.dumps(paper_template, ensure_ascii=False, indent=4))
            self.status_label.config(text="状态：已加载当前考试的组卷模板。")

    def calculate_pass_score(self):
        """根据总分和及格百分比计算及格分"""
        try:
            total_score = self.total_score_var.get()
            pass_percentage = self.pass_percentage_var.get()
            pass_score = int(total_score * pass_percentage / 100)
            self.pass_score_var.set(pass_score)
        except Exception as e:
            # 计算出错时不做处理，保持原值
            pass
    
    def run_generation(self):
        template_str = self.template_text.get('1.0', tk.END)
        try:
            template = json.loads(template_str)
        except json.JSONDecodeError as e:
            messagebox.showerror("模板错误", f"JSON格式错误: {e}", parent=self.dialog)
            return

        # 增加一个确认步骤
        if not messagebox.askyesno("确认操作", "即将根据当前模板生成全新的试卷。\n这会覆盖本次考试已有的试题列表，是否继续？", parent=self.dialog):
            return

        self.status_label.config(text="状态：组卷中，请稍候...")
        generator = PaperGenerator(self.all_questions)
        try:
            question_ids = generator.generate_paper(template)
            
            # 保存试卷信息和分数设置
            self.exam['question_ids'] = question_ids
            self.exam['paper_template'] = template
            self.exam['total_questions'] = len(question_ids)
            
            # 保存总分和及格分设置
            self.exam['total_score'] = self.total_score_var.get()
            self.exam['pass_score'] = self.pass_score_var.get()
            
            self.manager.save_exams()
            self.status_label.config(text=f"状态：组卷成功！共 {len(question_ids)} 题。")
            messagebox.showinfo("成功", f"组卷成功！共生成 {len(question_ids)} 道题目。\n总分：{self.exam['total_score']}\n及格分：{self.exam['pass_score']}", parent=self.dialog)
            self.manager.refresh_exam_list()
            self.dialog.destroy()
        except PaperGenerationError as e:
            self.status_label.config(text="状态：组卷失败！"); messagebox.showerror("组卷失败", str(e), parent=self.dialog)
        except Exception as e:
            self.status_label.config(text="状态：未知错误！"); messagebox.showerror("未知错误", f"发生意外错误: {e}", parent=self.dialog)
            
    def import_paper_from_question_bank(self):
        """从题库管理模块导入试卷"""
        if not self.question_bank:
            messagebox.showerror("错误", "请先加载题库数据")
            return
        self.status_label.config(text="状态：正在从题库管理模块加载试卷列表...")
        papers = self.load_papers_from_question_bank()
        
        if not papers:
            self.status_label.config(text="状态：未找到可导入的试卷")
            messagebox.showinfo("提示", "未找到可导入的试卷。\n请确认题库管理模块已启动并已生成试卷。", parent=self.dialog)
            return
            
        # 创建试卷选择对话框
        paper_dialog = tk.Toplevel(self.dialog)
        paper_dialog.title("选择要导入的试卷")
        paper_dialog.geometry("800x500")
        paper_dialog.transient(self.dialog)
        paper_dialog.grab_set()
        
        # 创建试卷列表框架
        frame = ttk.Frame(paper_dialog, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="请选择要导入的试卷：", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        # 创建表格显示试卷列表，设置为多选模式
        columns = ("id", "name", "description", "total_score", "question_count", "created_at")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="extended")
        
        # 设置列标题
        tree.heading("id", text="ID")
        tree.heading("name", text="试卷名称")
        tree.heading("description", text="描述")
        tree.heading("total_score", text="总分")
        tree.heading("question_count", text="题目数量")
        tree.heading("created_at", text="创建时间")
        
        # 设置列宽
        tree.column("id", width=50)
        tree.column("name", width=200)
        tree.column("description", width=200)
        tree.column("total_score", width=80)
        tree.column("question_count", width=80)
        tree.column("created_at", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 填充数据
        for paper in papers:
            created_at = paper.get('created_at', '')
            if isinstance(created_at, str):
                # 如果是字符串，尝试格式化
                try:
                    created_at = created_at[:19]  # 取前19个字符，去掉可能的毫秒部分
                except:
                    pass
            
            tree.insert("", tk.END, values=(
                paper.get('id', ''),
                paper.get('name', '无标题'),
                paper.get('description', '')[:30] + ('...' if len(paper.get('description', '')) > 30 else ''),
                paper.get('total_score', 0),
                len(paper.get('questions', [])),
                created_at
            ))
        
        # 详情显示区域
        detail_frame = ttk.LabelFrame(frame, text="试卷详情")
        detail_frame.pack(fill=tk.X, pady=10)
        
        detail_text = scrolledtext.ScrolledText(detail_frame, height=8, wrap=tk.WORD)
        detail_text.pack(fill=tk.X, padx=5, pady=5)
        detail_text.insert(tk.END, "请选择一个试卷查看详情")
        detail_text.config(state=tk.DISABLED)
        
        # 选择事件处理
        def on_select(event):
            selected_items = tree.selection()
            if selected_items:
                item = selected_items[0]
                values = tree.item(item, "values")
                paper_id = values[0]
                
                # 查找选中的试卷
                selected_paper = next((p for p in papers if str(p.get('id', '')) == str(paper_id)), None)
                if selected_paper:
                    # 更新详情显示
                    detail_text.config(state=tk.NORMAL)
                    detail_text.delete(1.0, tk.END)
                    
                    detail_info = f"试卷名称: {selected_paper.get('name', '无标题')}\n"
                    detail_info += f"描述: {selected_paper.get('description', '无描述')}\n"
                    detail_info += f"总分: {selected_paper.get('total_score', 0)}\n"
                    detail_info += f"及格分: {selected_paper.get('pass_score', 0)}\n"
                    detail_info += f"题目数量: {len(selected_paper.get('questions', []))}\n"
                    detail_info += f"难度: {selected_paper.get('difficulty_level', '未设置')}\n"
                    
                    # 添加题型统计
                    question_types = {}
                    for q in selected_paper.get('questions', []):
                        q_type = q.get('type', '未知')
                        question_types[q_type] = question_types.get(q_type, 0) + 1
                    
                    detail_info += "\n题型分布:\n"
                    for q_type, count in question_types.items():
                        detail_info += f"  - {q_type}: {count}题\n"
                    
                    detail_text.insert(tk.END, detail_info)
                    detail_text.config(state=tk.DISABLED)
        
        tree.bind("<<TreeviewSelect>>", on_select)
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def import_selected_paper():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("警告", "请先选择至少一个试卷", parent=paper_dialog)
                return
            
            # 获取所有选中的试卷
            selected_papers = []
            for item in selected_items:
                values = tree.item(item, "values")
                paper_id = values[0]
                
                # 查找选中的试卷
                paper = next((p for p in papers if str(p.get('id', '')) == str(paper_id)), None)
                if paper:
                    selected_papers.append(paper)
            
            if not selected_papers:
                messagebox.showerror("错误", "无法找到选中的试卷数据", parent=paper_dialog)
                return
            
            # 确认导入
            paper_names = ", ".join([p.get('name', '无标题') for p in selected_papers])
            if not messagebox.askyesno("确认导入", 
                                      f"确定要导入 {len(selected_papers)} 套试卷？\n" +
                                      f"选中的试卷: {paper_names}\n" +
                                      "这将覆盖当前考试的试题设置。", parent=paper_dialog):
                return
            
            # 如果只选择了一套试卷，按原来的方式处理
            if len(selected_papers) == 1:
                selected_paper = selected_papers[0]
                # 提取题目ID列表
                question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                
                # 更新考试信息
                self.exam['paper_id'] = selected_paper.get('id')
                self.exam['question_ids'] = question_ids
                self.exam['total_questions'] = len(question_ids)
                self.exam['total_score'] = selected_paper.get('total_score', self.total_score_var.get())
                self.exam['pass_score'] = selected_paper.get('pass_score', self.pass_score_var.get())
                
                # 更新UI显示
                self.total_score_var.set(self.exam['total_score'])
                self.pass_score_var.set(self.exam['pass_score'])
                
                # 保存考试信息
                self.manager.save_exams()
                
                # 关闭对话框并显示成功消息
                paper_dialog.destroy()
                self.status_label.config(text=f"状态：成功导入试卷 '{selected_paper.get('name', '无标题')}'")
                messagebox.showinfo("导入成功", 
                                  f"成功导入试卷 '{selected_paper.get('name', '无标题')}'\n" +
                                  f"题目数量: {len(question_ids)}\n" +
                                  f"总分: {self.exam['total_score']}\n" +
                                  f"及格分: {self.exam['pass_score']}", 
                                  parent=self.dialog)
            else:
                # 如果选择了多套试卷，为每套试卷创建一个考试
                created_exams = []
                for i, selected_paper in enumerate(selected_papers):
                    if i == 0:  # 第一套试卷更新当前考试
                        question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                        self.exam['paper_id'] = selected_paper.get('id')
                        self.exam['question_ids'] = question_ids
                        self.exam['total_questions'] = len(question_ids)
                        self.exam['total_score'] = selected_paper.get('total_score', self.total_score_var.get())
                        self.exam['pass_score'] = selected_paper.get('pass_score', self.pass_score_var.get())
                        self.exam['name'] = selected_paper.get('name', '无标题')
                        
                        # 更新UI显示
                        self.name_var.set(self.exam['name'])
                        self.total_score_var.set(self.exam['total_score'])
                        self.pass_score_var.set(self.exam['pass_score'])
                        created_exams.append(self.exam)
                    else:  # 其他试卷创建新考试
                        new_exam = self.manager.create_new_exam()
                        question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                        new_exam['paper_id'] = selected_paper.get('id')
                        new_exam['question_ids'] = question_ids
                        new_exam['total_questions'] = len(question_ids)
                        new_exam['total_score'] = selected_paper.get('total_score', 100)
                        new_exam['pass_score'] = selected_paper.get('pass_score', 60)
                        new_exam['name'] = selected_paper.get('name', '无标题')
                        new_exam['type'] = self.exam.get('type', '普通考试')
                        new_exam['description'] = selected_paper.get('description', '')
                        new_exam['duration'] = self.exam.get('duration', 60)
                        created_exams.append(new_exam)
                
                # 保存考试信息
                self.manager.save_exams()
                
                # 关闭对话框并显示成功消息
                paper_dialog.destroy()
                self.status_label.config(text=f"状态：成功导入 {len(selected_papers)} 套试卷")
                messagebox.showinfo("导入成功", 
                                  f"成功导入 {len(selected_papers)} 套试卷\n" +
                                  f"已为每套试卷创建对应的考试", 
                                  parent=self.dialog)
            
            # 刷新考试列表
            self.manager.refresh_exam_list()
        
        ttk.Button(button_frame, text="导入选中试卷", command=import_selected_paper).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=paper_dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 更新状态
        self.status_label.config(text=f"状态：已加载 {len(papers)} 份试卷")
        
        # 等待对话框关闭
        self.dialog.wait_window(paper_dialog)

# === 新增 ExamDialog 类 ===
class ExamDialog:
    def __init__(self, parent, manager, exam=None):
        self.manager = manager
        self.is_edit_mode = exam is not None
        self.exam = exam or {}
        self.parent = parent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'编辑' if self.is_edit_mode else '新增'}考试")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 设置主题颜色
        self.colors = manager.colors
        
        self.setup_ui()
        self.load_exam_data()
    
    def show_paper_selection_dialog(self, papers):
        """显示试卷选择对话框"""
        if not papers:
            messagebox.showinfo("提示", "未找到可导入的试卷。\n请确认题库管理模块已启动并已生成试卷。", parent=self.dialog)
            return
            
        # 创建试卷选择对话框
        paper_dialog = tk.Toplevel(self.dialog)
        paper_dialog.title("从题库选择试卷")
        paper_dialog.geometry("800x600")
        paper_dialog.transient(self.dialog)
        paper_dialog.grab_set()
        
        # 创建主框架
        frame = ttk.Frame(paper_dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(frame, text="选择要导入的试卷", font=("Microsoft YaHei", 14, "bold")).pack(pady=(0, 10))
        
        # 创建表格，设置为多选模式
        columns = ("id", "name", "description", "total_score", "question_count", "created_at")
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="extended")
        
        # 设置列标题
        tree.heading("id", text="ID")
        tree.heading("name", text="试卷名称")
        tree.heading("description", text="描述")
        tree.heading("total_score", text="总分")
        tree.heading("question_count", text="题目数量")
        tree.heading("created_at", text="创建时间")
        
        # 设置列宽
        tree.column("id", width=80)
        tree.column("name", width=150)
        tree.column("description", width=200)
        tree.column("total_score", width=80)
        tree.column("question_count", width=80)
        tree.column("created_at", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加数据
        for paper in papers:
            tree.insert("", tk.END, values=(
                paper.get("id", ""),
                paper.get("name", "无标题"),
                paper.get("description", "无描述")[:30] + ("..." if len(paper.get("description", "")) > 30 else ""),
                paper.get("total_score", 0),
                len(paper.get("questions", [])),
                paper.get("created_at", "")
            ))
        
        # 详情区域
        detail_frame = ttk.LabelFrame(frame, text="试卷详情", padding=10)
        detail_frame.pack(fill=tk.X, pady=10)
        
        detail_text = tk.Text(detail_frame, height=8, wrap=tk.WORD)
        detail_text.pack(fill=tk.X)
        detail_text.config(state=tk.DISABLED)
        
        # 选择事件
        def on_select(event):
            selected_items = tree.selection()
            if not selected_items:
                return
                
            item = selected_items[0]
            values = tree.item(item, "values")
            paper_id = values[0]
            
            # 查找选中的试卷
            selected_paper = next((p for p in papers if str(p.get("id", "")) == str(paper_id)), None)
            if selected_paper:
                # 更新详情显示
                detail_text.config(state=tk.NORMAL)
                detail_text.delete(1.0, tk.END)
                
                detail_info = f"试卷名称: {selected_paper.get('name', '无标题')}\n"
                detail_info += f"描述: {selected_paper.get('description', '无描述')}\n"
                detail_info += f"总分: {selected_paper.get('total_score', 0)}\n"
                detail_info += f"及格分: {selected_paper.get('pass_score', 0)}\n"
                detail_info += f"题目数量: {len(selected_paper.get('questions', []))}\n"
                detail_info += f"难度: {selected_paper.get('difficulty_level', '未设置')}\n"
                
                # 添加题型统计
                question_types = {}
                for q in selected_paper.get('questions', []):
                    q_type = q.get('type', '未知')
                    question_types[q_type] = question_types.get(q_type, 0) + 1
                
                detail_info += "\n题型分布:\n"
                for q_type, count in question_types.items():
                    detail_info += f"  - {q_type}: {count}题\n"
                
                detail_text.insert(tk.END, detail_info)
                detail_text.config(state=tk.DISABLED)
        
        tree.bind("<<TreeviewSelect>>", on_select)
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def import_selected_paper():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("警告", "请先选择至少一个试卷", parent=paper_dialog)
                return
            
            # 获取所有选中的试卷
            selected_papers = []
            for item in selected_items:
                values = tree.item(item, "values")
                paper_id = values[0]
                
                # 查找选中的试卷
                paper = next((p for p in papers if str(p.get("id", "")) == str(paper_id)), None)
                if paper:
                    selected_papers.append(paper)
            
            if not selected_papers:
                messagebox.showerror("错误", "无法找到选中的试卷数据", parent=paper_dialog)
                return
            
            # 确认导入
            paper_names = ", ".join([p.get('name', '无标题') for p in selected_papers])
            if not messagebox.askyesno("确认导入", 
                                      f"确定要导入 {len(selected_papers)} 套试卷？\n" +
                                      f"选中的试卷: {paper_names}\n" +
                                      "这将覆盖当前考试的试题设置。", parent=paper_dialog):
                return
            
            # 如果只选择了一套试卷，按原来的方式处理
            if len(selected_papers) == 1:
                selected_paper = selected_papers[0]
                # 提取题目ID列表
                question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                
                # 更新考试信息
                self.exam['paper_id'] = selected_paper.get('id')
                self.exam['question_ids'] = question_ids
                self.exam['total_questions'] = len(question_ids)
                self.exam['total_score'] = selected_paper.get('total_score', self.total_score_var.get())
                self.exam['pass_score'] = selected_paper.get('pass_score', self.pass_score_var.get())
                
                # 更新UI显示
                self.total_score_var.set(self.exam['total_score'])
                self.pass_score_var.set(self.exam['pass_score'])
                
                # 保存考试信息
                self.manager.save_exams()
                
                # 关闭对话框并显示成功消息
                paper_dialog.destroy()
                messagebox.showinfo("导入成功", 
                                  f"成功导入试卷 '{selected_paper.get('name', '无标题')}'\n" +
                                  f"题目数量: {len(question_ids)}\n" +
                                  f"总分: {self.exam['total_score']}\n" +
                                  f"及格分: {self.exam['pass_score']}", 
                                  parent=self.dialog)
            else:
                # 如果选择了多套试卷，为每套试卷创建一个考试
                for i, selected_paper in enumerate(selected_papers):
                    if i == 0:  # 第一套试卷更新当前考试
                        question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                        self.exam['paper_id'] = selected_paper.get('id')
                        self.exam['question_ids'] = question_ids
                        self.exam['total_questions'] = len(question_ids)
                        self.exam['total_score'] = selected_paper.get('total_score', self.total_score_var.get())
                        self.exam['pass_score'] = selected_paper.get('pass_score', self.pass_score_var.get())
                        self.exam['name'] = selected_paper.get('name', '无标题')
                        
                        # 更新UI显示
                        self.name_var.set(self.exam['name'])
                        self.total_score_var.set(self.exam['total_score'])
                        self.pass_score_var.set(self.exam['pass_score'])
                    else:  # 其他试卷创建新考试
                        new_exam = self.manager.create_new_exam()
                        question_ids = [q.get('id') for q in selected_paper.get('questions', [])]
                        new_exam['paper_id'] = selected_paper.get('id')
                        new_exam['question_ids'] = question_ids
                        new_exam['total_questions'] = len(question_ids)
                        new_exam['total_score'] = selected_paper.get('total_score', 100)
                        new_exam['pass_score'] = selected_paper.get('pass_score', 60)
                        new_exam['name'] = selected_paper.get('name', '无标题')
                        new_exam['type'] = self.exam.get('type', '普通考试')
                        new_exam['description'] = selected_paper.get('description', '')
                        new_exam['duration'] = self.exam.get('duration', 60)
                
                # 保存考试信息
                self.manager.save_exams()
                
                # 关闭对话框并显示成功消息
                paper_dialog.destroy()
                messagebox.showinfo("导入成功", 
                                  f"成功导入 {len(selected_papers)} 套试卷\n" +
                                  f"已为每套试卷创建对应的考试", 
                                  parent=self.dialog)
            
            # 刷新考试列表
            self.manager.refresh_exam_list()
        
        ttk.Button(button_frame, text="导入选中试卷", command=import_selected_paper).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="取消", command=paper_dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 等待对话框关闭
        self.dialog.wait_window(paper_dialog)
    
    def setup_ui(self):
        """设置用户界面"""
        main_frame = ttk.Frame(self.dialog, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text=f"{'✏️ 编辑' if self.is_edit_mode else '➕ 新增'}考试", 
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # 创建滚动区域
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 表单区域
        form_frame = ttk.Frame(scrollable_frame, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 基本信息区域
        basic_info_frame = ttk.LabelFrame(form_frame, text="基本信息", padding=10)
        basic_info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 考试名称
        name_frame = ttk.Frame(basic_info_frame)
        name_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(name_frame, text="考试名称:", width=15).pack(side=tk.LEFT)
        self.name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self.name_var, width=50).pack(side=tk.LEFT, padx=(5, 0))
        
        # 考试类型
        type_frame = ttk.Frame(basic_info_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="考试类型:", width=15).pack(side=tk.LEFT)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            type_frame, 
            textvariable=self.type_var,
            values=list(self.manager.exam_types.values()), 
            width=20,
            state="readonly"
        )
        type_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 考试描述
        desc_frame = ttk.Frame(basic_info_frame)
        desc_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(desc_frame, text="考试描述:", width=15).pack(side=tk.LEFT, anchor="n")
        self.desc_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=self.desc_var, width=50)
        desc_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 时间设置区域
        time_frame = ttk.LabelFrame(form_frame, text="时间设置", padding=10)
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 考试时长
        duration_frame = ttk.Frame(time_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(duration_frame, text="考试时长(分钟):", width=15).pack(side=tk.LEFT)
        self.duration_var = tk.IntVar(value=60)
        ttk.Spinbox(duration_frame, from_=10, to=300, textvariable=self.duration_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # 开始时间
        start_time_frame = ttk.Frame(time_frame)
        start_time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(start_time_frame, text="开始时间:", width=15).pack(side=tk.LEFT)
        
        # 日期选择
        self.start_date_var = tk.StringVar()
        ttk.Entry(start_time_frame, textvariable=self.start_date_var, width=12).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(start_time_frame, text="格式: YYYY-MM-DD").pack(side=tk.LEFT, padx=(5, 0))
        
        # 时间选择
        self.start_time_var = tk.StringVar()
        ttk.Entry(start_time_frame, textvariable=self.start_time_var, width=8).pack(side=tk.LEFT, padx=(15, 0))
        ttk.Label(start_time_frame, text="格式: HH:MM").pack(side=tk.LEFT, padx=(5, 0))
        
        # 结束时间
        end_time_frame = ttk.Frame(time_frame)
        end_time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(end_time_frame, text="结束时间:", width=15).pack(side=tk.LEFT)
        
        # 日期选择
        self.end_date_var = tk.StringVar()
        ttk.Entry(end_time_frame, textvariable=self.end_date_var, width=12).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(end_time_frame, text="格式: YYYY-MM-DD").pack(side=tk.LEFT, padx=(5, 0))
        
        # 时间选择
        self.end_time_var = tk.StringVar()
        ttk.Entry(end_time_frame, textvariable=self.end_time_var, width=8).pack(side=tk.LEFT, padx=(15, 0))
        ttk.Label(end_time_frame, text="格式: HH:MM").pack(side=tk.LEFT, padx=(5, 0))
        
        # 分数设置区域
        score_frame = ttk.LabelFrame(form_frame, text="分数设置", padding=10)
        score_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 总分
        total_score_frame = ttk.Frame(score_frame)
        total_score_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(total_score_frame, text="总分:", width=15).pack(side=tk.LEFT)
        self.total_score_var = tk.IntVar(value=100)
        total_score_spinbox = ttk.Spinbox(total_score_frame, from_=10, to=1000, textvariable=self.total_score_var, width=10)
        total_score_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 及格分
        pass_score_frame = ttk.Frame(score_frame)
        pass_score_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pass_score_frame, text="及格分:", width=15).pack(side=tk.LEFT)
        self.pass_score_var = tk.IntVar(value=60)
        self.pass_score_spinbox = ttk.Spinbox(pass_score_frame, from_=0, to=1000, textvariable=self.pass_score_var, width=10)
        self.pass_score_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 及格百分比
        pass_percentage_frame = ttk.Frame(score_frame)
        pass_percentage_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pass_percentage_frame, text="及格百分比(%):", width=15).pack(side=tk.LEFT)
        self.pass_percentage_var = tk.IntVar(value=60)
        pass_percentage_spinbox = ttk.Spinbox(pass_percentage_frame, from_=0, to=100, textvariable=self.pass_percentage_var, width=10)
        pass_percentage_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 计算按钮
        calculate_btn = ttk.Button(pass_percentage_frame, text="计算及格分", command=self.calculate_pass_score)
        calculate_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # 绑定事件，当总分或及格百分比变化时自动计算及格分
        self.total_score_var.trace_add("write", lambda *args: self.calculate_pass_score())
        self.pass_percentage_var.trace_add("write", lambda *args: self.calculate_pass_score())
        
        # 参与者设置区域
        participants_frame = ttk.LabelFrame(form_frame, text="参与者设置", padding=10)
        participants_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 最大参与人数
        max_participants_frame = ttk.Frame(participants_frame)
        max_participants_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(max_participants_frame, text="最大参与人数:", width=15).pack(side=tk.LEFT)
        self.max_participants_var = tk.IntVar(value=100)
        ttk.Spinbox(max_participants_frame, from_=1, to=1000, textvariable=self.max_participants_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # 允许部门
        allowed_departments_frame = ttk.Frame(participants_frame)
        allowed_departments_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(allowed_departments_frame, text="允许部门:", width=15).pack(side=tk.LEFT)
        self.allowed_departments_var = tk.StringVar()
        ttk.Entry(allowed_departments_frame, textvariable=self.allowed_departments_var, width=50).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(allowed_departments_frame, text="多个部门用逗号分隔").pack(side=tk.LEFT, padx=(5, 0))
        
        # 底部按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="保存", command=self.save_exam, width=15).pack(side=tk.RIGHT, padx=5)
    
    def calculate_pass_score(self):
        """根据总分和及格百分比计算及格分"""
        try:
            total_score = self.total_score_var.get()
            pass_percentage = self.pass_percentage_var.get()
            pass_score = int(total_score * pass_percentage / 100)
            self.pass_score_var.set(pass_score)
        except Exception as e:
            # 计算出错时不做处理，保持原值
            pass
    
    def load_exam_data(self):
        """加载考试数据到表单"""
        if not self.is_edit_mode:
            # 设置默认值
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            self.start_date_var.set(now.strftime("%Y-%m-%d"))
            self.start_time_var.set("09:00")
            self.end_date_var.set(tomorrow.strftime("%Y-%m-%d"))
            self.end_time_var.set("09:00")
            self.type_var.set("formal")
            
            # 设置默认的及格百分比
            self.pass_percentage_var.set(60)
            self.calculate_pass_score()
            return
        
        # 编辑模式，加载现有数据
        self.name_var.set(self.exam.get("name", ""))
        # 将英文类型转换为中文显示
        exam_type = self.exam.get("type", "formal")
        self.type_var.set(self.manager.exam_types.get(exam_type, "正式考试"))
        self.desc_var.set(self.exam.get("description", ""))
        self.duration_var.set(self.exam.get("duration_minutes", 60))
        
        # 设置总分和及格分
        total_score = self.exam.get("total_score", 100)
        pass_score = self.exam.get("pass_score", 60)
        self.total_score_var.set(total_score)
        self.pass_score_var.set(pass_score)
        
        # 计算并设置及格百分比
        if total_score > 0:
            pass_percentage = int((pass_score / total_score) * 100)
            self.pass_percentage_var.set(pass_percentage)
        else:
            self.pass_percentage_var.set(60)  # 默认60%
        
        self.max_participants_var.set(self.exam.get("max_participants", 100))
        
        # 处理允许部门
        allowed_departments = self.exam.get("allowed_departments", [])
        self.allowed_departments_var.set(", ".join(allowed_departments))
        
        # 处理时间
        if "start_time" in self.exam:
            start_time = datetime.strptime(self.exam["start_time"], "%Y-%m-%d %H:%M:%S")
            self.start_date_var.set(start_time.strftime("%Y-%m-%d"))
            self.start_time_var.set(start_time.strftime("%H:%M"))
        
        if "end_time" in self.exam:
            end_time = datetime.strptime(self.exam["end_time"], "%Y-%m-%d %H:%M:%S")
            self.end_date_var.set(end_time.strftime("%Y-%m-%d"))
            self.end_time_var.set(end_time.strftime("%H:%M"))
    
    def save_exam(self):
        """保存考试数据"""
        # 验证必填字段
        if not self.name_var.get().strip():
            messagebox.showerror("错误", "考试名称不能为空！", parent=self.dialog)
            return
        
        try:
            # 验证时间格式
            start_datetime = datetime.strptime(
                f"{self.start_date_var.get()} {self.start_time_var.get()}:00", 
                "%Y-%m-%d %H:%M:%S"
            )
            end_datetime = datetime.strptime(
                f"{self.end_date_var.get()} {self.end_time_var.get()}:00", 
                "%Y-%m-%d %H:%M:%S"
            )
            
            if end_datetime <= start_datetime:
                messagebox.showerror("错误", "结束时间必须晚于开始时间！", parent=self.dialog)
                return
        except ValueError:
            messagebox.showerror("错误", "日期或时间格式不正确！", parent=self.dialog)
            return
        
        # 构建考试数据
        # 将中文考试类型转换回英文键值
        selected_type = self.type_var.get()
        exam_type = "formal"  # 默认值
        for key, value in self.manager.exam_types.items():
            if value == selected_type:
                exam_type = key
                break
                
        exam_data = {
            "name": self.name_var.get().strip(),
            "type": exam_type,
            "description": self.desc_var.get().strip(),
            "duration_minutes": self.duration_var.get(),
            "total_score": self.total_score_var.get(),
            "pass_score": self.pass_score_var.get(),
            "start_time": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "max_participants": self.max_participants_var.get(),
            "allowed_departments": [dept.strip() for dept in self.allowed_departments_var.get().split(",") if dept.strip()],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.is_edit_mode:
            # 更新现有考试
            for key, value in exam_data.items():
                self.exam[key] = value
        else:
            # 创建新考试
            # 生成新的考试ID
            max_id = 0
            for exam in self.manager.exams.get("exams", []):
                if exam.get("id", 0) > max_id:
                    max_id = exam.get("id")
            
            exam_data.update({
                "id": max_id + 1,
                "status": "draft",
                "current_participants": 0,
                "created_by": "admin",  # 这里可以替换为实际的用户名
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 添加到考试列表
            self.manager.exams.setdefault("exams", []).append(exam_data)
        
        # 保存到文件
        self.manager.save_exams()
        messagebox.showinfo("成功", f"考试已{'更新' if self.is_edit_mode else '创建'}！", parent=self.dialog)
        self.dialog.destroy()


    
    def load_papers_from_question_bank(self):
        """从题库管理模块的SQLite数据库中加载试卷数据"""
        import sqlite3
        import os
        
        papers = []
        db_path = os.path.join('question_bank_web', 'local_dev.db')
        
        if not os.path.exists(db_path):
            messagebox.showerror("错误", f"题库数据库文件不存在: {db_path}")
            return papers
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 查询所有试卷
            cursor.execute("""
                SELECT p.id, p.name, p.description, p.total_score, p.created_at, 
                       COUNT(pq.question_id) as question_count
                FROM papers p
                LEFT JOIN paper_questions pq ON p.id = pq.paper_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
            """)
            
            paper_rows = cursor.fetchall()
            
            for paper_row in paper_rows:
                paper = dict(paper_row)
                # 添加默认的pass_score值，因为数据库中没有这个字段
                paper['pass_score'] = int(paper.get('total_score', 100) * 0.6)  # 默认及格分为总分的60%
                
                # 查询试卷中的题目
                cursor.execute("""
                    SELECT q.id, q.stem, q.question_type_code as type, q.difficulty_code as difficulty, 
                           pq.score, q.correct_answer as answer, q.analysis,
                           pq.question_order
                    FROM questions q
                    JOIN paper_questions pq ON q.id = pq.question_id
                    WHERE pq.paper_id = ?
                    ORDER BY pq.question_order
                """, (paper['id'],))
                
                questions = []
                for q_row in cursor.fetchall():
                    q = dict(q_row)
                    # 将stem字段的值赋给content字段，以保持与papers.json的兼容性
                    if 'stem' in q:
                        q['content'] = q.pop('stem')
                    questions.append(q)
                paper['questions'] = questions
                papers.append(paper)
            
            conn.close()
            return papers
        except Exception as e:
            messagebox.showerror("错误", f"从题库加载试卷失败: {e}")
            return []

if __name__ == "__main__":
    app = SimpleExamManager()
    app.run()