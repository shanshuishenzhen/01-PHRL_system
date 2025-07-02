import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import csv
import requests
import threading
import time
from datetime import datetime

# 导入自定义模块
from import_scores import ScoreImporter

# 尝试导入matplotlib和numpy
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("警告：未安装matplotlib和numpy，图表功能将不可用")
    print("请运行：pip install matplotlib numpy")

class SimpleScoreManager:
    """简化版成绩统计主类"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("成绩统计 - PH&RL 在线考试系统")
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
        
        # 成绩数据存储
        self.scores = self.load_scores()
        self.current_page = 1
        self.page_size = 20
        
        # 统计维度定义
        self.dimensions = {
            'exam': '按考试统计',
            'student': '按考生统计',
            'department': '按部门统计',
            'date': '按日期统计'
        }
        
        self.setup_ui()
        self.refresh_score_list()
    
    def load_scores(self):
        """加载成绩数据"""
        try:
            if os.path.exists('score_statistics/scores.json'):
                with open('score_statistics/scores.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载成绩数据失败: {e}")
        
        # 返回默认成绩数据
        return {
            "scores": [
                {
                    "id": 1,
                    "exam_id": 101,
                    "exam_name": "2024年度计算机基础知识认证",
                    "student_id": 1001,
                    "student_name": "张三",
                    "department": "计算机系",
                    "score": 85,
                    "total_score": 100,
                    "percentage": 85.0,
                    "submit_time": "2024-01-15 14:30:00",
                    "status": "completed"
                }
            ]
        }
    
    def save_scores(self):
        """保存成绩数据"""
        try:
            os.makedirs('score_statistics', exist_ok=True)
            with open('score_statistics/scores.json', 'w', encoding='utf-8') as f:
                json.dump(self.scores, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存成绩数据失败: {e}")
    
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
        
        # 左侧：成绩列表
        self.create_score_list_frame(content_frame)
        
        # 右侧：统计图表
        self.create_statistics_frame(content_frame)
        
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
            text="📊 成绩统计", 
            font=("Microsoft YaHei", 20, "bold"),
            foreground=self.colors['primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # 成绩统计信息
        total_scores = len(self.scores.get("scores", []))
        avg_score = 0
        if total_scores > 0:
            scores_list = self.scores.get("scores", [])
            total_points = sum(score.get("score", 0) for score in scores_list)
            avg_score = round(total_points / total_scores, 1)
        
        stats_label = ttk.Label(
            title_frame,
            text=f"共 {total_scores} 条成绩记录 | 平均分: {avg_score}",
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
        
        # 从阅卷中心导入按钮
        import_btn = tk.Button(
            button_frame, 
            text="📥 从阅卷中心导入", 
            command=self.import_from_grading_center,
            bg=self.colors['info'],
            fg="white",
            activebackground=self.colors['info'],
            activeforeground="white",
            **button_style
        )
        import_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加成绩按钮
        add_btn = tk.Button(
            button_frame, 
            text="➕ 添加成绩", 
            command=self.add_score,
            bg=self.colors['success'],
            fg="white",
            activebackground=self.colors['success'],
            activeforeground="white",
            **button_style
        )
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # 编辑成绩按钮
        edit_btn = tk.Button(
            button_frame, 
            text="✏️ 编辑成绩", 
            command=self.edit_score,
            bg=self.colors['primary'],
            fg="white",
            activebackground=self.colors['primary'],
            activeforeground="white",
            **button_style
        )
        edit_btn.pack(side=tk.LEFT, padx=5)
        
        # 删除成绩按钮
        delete_btn = tk.Button(
            button_frame, 
            text="🗑️ 删除成绩", 
            command=self.delete_score,
            bg=self.colors['danger'],
            fg="white",
            activebackground=self.colors['danger'],
            activeforeground="white",
            **button_style
        )
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # 导出数据按钮
        export_btn = tk.Button(
            button_frame, 
            text="📤 导出数据", 
            command=self.export_data,
            bg=self.colors['purple'],
            fg="white",
            activebackground=self.colors['purple'],
            activeforeground="white",
            **button_style
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            button_frame, 
            text="🔄 刷新", 
            command=self.refresh_score_list,
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
        
        # 考试筛选
        exam_label = ttk.Label(
            search_frame, 
            text="考试:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        exam_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.exam_filter_var = tk.StringVar(value="all")
        self.exam_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.exam_filter_var, 
            width=20,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        self.exam_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 部门筛选
        dept_label = ttk.Label(
            search_frame, 
            text="部门:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        dept_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.dept_filter_var = tk.StringVar(value="all")
        self.dept_combo = ttk.Combobox(
            search_frame, 
            textvariable=self.dept_filter_var, 
            width=12,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        self.dept_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 搜索按钮
        search_btn = tk.Button(
            search_frame, 
            text="🔍 搜索", 
            command=self.search_scores,
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
        
        # 更新筛选选项
        self.update_filter_options()
    
    def create_score_list_frame(self, parent):
        """创建成绩列表区域"""
        list_frame = ttk.LabelFrame(
            parent, 
            text="📋 成绩明细", 
            padding="10"
        )
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 创建Treeview
        columns = ("ID", "考试名称", "考生姓名", "部门", "成绩", "总分", "通过率", "提交时间")
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
            "考生姓名": 100,
            "部门": 120,
            "成绩": 80,
            "总分": 80,
            "通过率": 80,
            "提交时间": 150
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
        self.tree.bind("<Double-1>", self.edit_score)
        
        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_score_select)
    
    def create_statistics_frame(self, parent):
        """创建统计图表区域"""
        stats_frame = ttk.LabelFrame(
            parent, 
            text="📈 统计分析", 
            padding="10"
        )
        stats_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 统计维度选择
        dimension_frame = ttk.Frame(stats_frame)
        dimension_frame.pack(fill=tk.X, pady=(0, 10))
        
        dimension_label = ttk.Label(
            dimension_frame, 
            text="统计维度:", 
            font=("Microsoft YaHei", 10, "bold")
        )
        dimension_label.pack(side=tk.LEFT)
        
        self.dimension_var = tk.StringVar(value="exam")
        dimension_combo = ttk.Combobox(
            dimension_frame, 
            textvariable=self.dimension_var,
            values=list(self.dimensions.keys()), 
            width=15,
            font=("Microsoft YaHei", 10),
            state="readonly"
        )
        dimension_combo.pack(side=tk.LEFT, padx=(5, 10))
        dimension_combo.bind("<<ComboboxSelected>>", self.update_statistics)
        
        # 图表区域
        self.chart_frame = ttk.Frame(stats_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # 统计信息区域
        self.stats_info_frame = ttk.Frame(stats_frame)
        self.stats_info_frame.pack(fill=tk.X, pady=(10, 0))
    
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
    
    def on_score_select(self, event):
        """成绩选择事件"""
        selection = self.tree.selection()
        if selection:
            # 可以在这里添加选中成绩后的操作
            pass
    
    def update_filter_options(self):
        """更新筛选选项"""
        try:
            # 更新考试选项
            exams = ["all"] + list(set(score.get("exam_name", "") for score in self.scores.get("scores", [])))
            if hasattr(self, 'exam_combo') and self.exam_combo:
                self.exam_combo['values'] = exams
            
            # 更新部门选项
            depts = ["all"] + list(set(score.get("department", "") for score in self.scores.get("scores", [])))
            if hasattr(self, 'dept_combo') and self.dept_combo:
                self.dept_combo['values'] = depts
        except Exception as e:
            print(f"更新筛选选项出错: {e}")
    
    def refresh_score_list(self):
        """刷新成绩列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取筛选后的成绩列表
        filtered_scores = self.get_filtered_scores()
        
        # 计算分页
        total_scores = len(filtered_scores)
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_scores = filtered_scores[start_idx:end_idx]
        
        # 插入数据
        for score in page_scores:
            self.tree.insert("", tk.END, values=(
                score.get("id"),
                score.get("exam_name", ""),
                score.get("student_name", ""),
                score.get("department", ""),
                score.get("score", 0),
                score.get("total_score", 100),
                f"{score.get('percentage', 0):.1f}%",  # 这里仍然显示百分比，因为它表示的是成绩/总分的比例
                score.get("submit_time", "")
            ))
        
        # 更新分页信息
        total_pages = (total_scores + self.page_size - 1) // self.page_size
        self.page_info_label.config(text=f"第 {self.current_page} 页，共 {total_pages} 页，总计 {total_scores} 条记录")
        
        # 更新统计图表
        self.update_statistics()
    
    def get_filtered_scores(self):
        """获取筛选后的成绩列表"""
        scores = self.scores.get("scores", [])
        filtered = []
        
        search_term = self.search_var.get().lower()
        exam_filter = self.exam_filter_var.get()
        dept_filter = self.dept_filter_var.get()
        
        for score in scores:
            # 搜索筛选
            if search_term:
                if not any(search_term in str(value).lower() for value in score.values()):
                    continue
            
            # 考试筛选
            if exam_filter != "all" and score.get("exam_name") != exam_filter:
                continue
            
            # 部门筛选
            if dept_filter != "all" and score.get("department") != dept_filter:
                continue
            
            filtered.append(score)
        
        return filtered
    
    def search_scores(self):
        """搜索成绩"""
        self.current_page = 1
        self.refresh_score_list()
    
    def reset_search(self):
        """重置搜索"""
        self.search_var.set("")
        self.exam_filter_var.set("all")
        self.dept_filter_var.set("all")
        self.current_page = 1
        self.refresh_score_list()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_score_list()
    
    def next_page(self):
        """下一页"""
        total_scores = len(self.get_filtered_scores())
        total_pages = (total_scores + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_score_list()
    
    def add_score(self):
        """添加成绩"""
        dialog = ScoreDialog(self.root, self, None)
        self.root.wait_window(dialog.dialog)
        self.refresh_score_list()
    
    def edit_score(self, event=None):
        """编辑成绩"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要编辑的成绩记录")
            return
        
        item = self.tree.item(selected[0])
        score_id = item['values'][0]
        score_data = self.get_score_by_id(score_id)
        
        if score_data:
            dialog = ScoreDialog(self.root, self, score_data)
            self.root.wait_window(dialog.dialog)
            self.refresh_score_list()
    
    def delete_score(self):
        """删除成绩"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要删除的成绩记录")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的成绩记录吗？"):
            for item in selected:
                score_id = self.tree.item(item)['values'][0]
                self.scores["scores"] = [s for s in self.scores["scores"] if s.get("id") != score_id]
            
            self.save_scores()
            self.refresh_score_list()
            messagebox.showinfo("成功", "成绩记录已删除")
    
    def get_score_by_id(self, score_id):
        """根据ID获取成绩数据"""
        for score in self.scores.get("scores", []):
            if score.get("id") == score_id:
                return score
        return None
    
    def update_statistics(self, event=None):
        """更新统计图表"""
        # 清空图表区域
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # 清空统计信息区域
        for widget in self.stats_info_frame.winfo_children():
            widget.destroy()
        
        if not HAS_MATPLOTLIB:
            ttk.Label(self.chart_frame, text="图表功能需要安装matplotlib和numpy\n请运行：pip install matplotlib numpy").pack(expand=True)
            return
        
        dimension = self.dimension_var.get()
        filtered_scores = self.get_filtered_scores()
        
        if not filtered_scores:
            ttk.Label(self.chart_frame, text="暂无数据").pack(expand=True)
            return
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        if dimension == 'exam':
            self.analyze_by_exam(filtered_scores, ax1, ax2)
        elif dimension == 'student':
            self.analyze_by_student(filtered_scores, ax1, ax2)
        elif dimension == 'department':
            self.analyze_by_department(filtered_scores, ax1, ax2)
        elif dimension == 'date':
            self.analyze_by_date(filtered_scores, ax1, ax2)
        
        # 嵌入图表
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 显示统计信息
        self.show_statistics_info(filtered_scores)
    
    def analyze_by_exam(self, scores, ax1, ax2):
        """按考试分析"""
        exam_stats = {}
        for score in scores:
            exam_name = score.get("exam_name", "未知考试")
            if exam_name not in exam_stats:
                exam_stats[exam_name] = []
            exam_stats[exam_name].append(score.get("score", 0))
        
        # 计算平均分
        exam_avgs = {exam: np.mean(scores) for exam, scores in exam_stats.items()}
        
        # 柱状图
        exams = list(exam_avgs.keys())
        avgs = list(exam_avgs.values())
        ax1.bar(exams, avgs)
        ax1.set_title("各考试平均分")
        ax1.set_ylabel("平均分")
        ax1.tick_params(axis='x', rotation=45)
        
        # 饼图
        total_scores = len(scores)
        exam_counts = {exam: len(scores) for exam, scores in exam_stats.items()}
        ax2.pie(exam_counts.values(), labels=exam_counts.keys(), autopct='%1.1f%%')
        ax2.set_title("考试分布")
    
    def analyze_by_student(self, scores, ax1, ax2):
        """按考生分析"""
        student_stats = {}
        for score in scores:
            student_name = score.get("student_name", "未知考生")
            if student_name not in student_stats:
                student_stats[student_name] = []
            student_stats[student_name].append(score.get("score", 0))
        
        # 计算平均分
        student_avgs = {student: np.mean(scores) for student, scores in student_stats.items()}
        
        # 取前10名
        top_students = sorted(student_avgs.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 柱状图
        students = [s[0] for s in top_students]
        avgs = [s[1] for s in top_students]
        ax1.bar(students, avgs)
        ax1.set_title("考生平均分排名（前10名）")
        ax1.set_ylabel("平均分")
        ax1.tick_params(axis='x', rotation=45)
        
        # 成绩分布
        all_scores = [score.get("score", 0) for score in scores]
        ax2.hist(all_scores, bins=10, alpha=0.7)
        ax2.set_title("成绩分布")
        ax2.set_xlabel("分数")
        ax2.set_ylabel("人数")
    
    def analyze_by_department(self, scores, ax1, ax2):
        """按部门分析"""
        dept_stats = {}
        for score in scores:
            dept = score.get("department", "未知部门")
            if dept not in dept_stats:
                dept_stats[dept] = []
            dept_stats[dept].append(score.get("score", 0))
        
        # 计算平均分
        dept_avgs = {dept: np.mean(scores) for dept, scores in dept_stats.items()}
        
        # 柱状图
        depts = list(dept_avgs.keys())
        avgs = list(dept_avgs.values())
        ax1.bar(depts, avgs)
        ax1.set_title("各部门平均分")
        ax1.set_ylabel("平均分")
        ax1.tick_params(axis='x', rotation=45)
        
        # 饼图
        dept_counts = {dept: len(scores) for dept, scores in dept_stats.items()}
        ax2.pie(dept_counts.values(), labels=dept_counts.keys(), autopct='%1.1f%%')
        ax2.set_title("部门分布")
    
    def analyze_by_date(self, scores, ax1, ax2):
        """按日期分析"""
        date_stats = {}
        for score in scores:
            submit_time = score.get("submit_time", "")
            if submit_time:
                date = submit_time.split()[0]  # 取日期部分
                if date not in date_stats:
                    date_stats[date] = []
                date_stats[date].append(score.get("score", 0))
        
        if not date_stats:
            ax1.text(0.5, 0.5, "无日期数据", ha='center', va='center', transform=ax1.transAxes)
            ax2.text(0.5, 0.5, "无日期数据", ha='center', va='center', transform=ax2.transAxes)
            return
        
        # 计算平均分
        date_avgs = {date: np.mean(scores) for date, scores in date_stats.items()}
        
        # 按日期排序
        sorted_dates = sorted(date_avgs.items())
        dates = [d[0] for d in sorted_dates]
        avgs = [d[1] for d in sorted_dates]
        
        # 折线图
        ax1.plot(dates, avgs, marker='o')
        ax1.set_title("成绩趋势")
        ax1.set_ylabel("平均分")
        ax1.tick_params(axis='x', rotation=45)
        
        # 柱状图
        ax2.bar(dates, avgs)
        ax2.set_title("各日期平均分")
        ax2.set_ylabel("平均分")
        ax2.tick_params(axis='x', rotation=45)
    
    def show_statistics_info(self, scores):
        """显示统计信息"""
        if not scores:
            return
        
        # 基本统计
        all_scores = [score.get("score", 0) for score in scores]
        if HAS_MATPLOTLIB:
            avg_score = np.mean(all_scores)
            max_score = np.max(all_scores)
            min_score = np.min(all_scores)
            std_score = np.std(all_scores)
        else:
            avg_score = sum(all_scores) / len(all_scores)
            max_score = max(all_scores)
            min_score = min(all_scores)
            std_score = 0  # 简化计算
        
        # 分数段统计
        excellent = len([s for s in all_scores if s >= 90])
        good = len([s for s in all_scores if 80 <= s < 90])
        fair = len([s for s in all_scores if 70 <= s < 80])
        pass_score = len([s for s in all_scores if 60 <= s < 70])
        fail = len([s for s in all_scores if s < 60])
        
        # 显示统计信息
        info_text = f"""
基本统计：
- 总记录数：{len(scores)}
- 平均分：{avg_score:.2f}
- 最高分：{max_score}
- 最低分：{min_score}
- 标准差：{std_score:.2f}

分数段分布：
- 优秀（90分以上）：{excellent}人 ({excellent/len(scores)*100:.1f}%)
- 良好（80-89分）：{good}人 ({good/len(scores)*100:.1f}%)
- 中等（70-79分）：{fair}人 ({fair/len(scores)*100:.1f}%)
- 及格（60-69分）：{pass_score}人 ({pass_score/len(scores)*100:.1f}%)
- 不及格（60分以下）：{fail}人 ({fail/len(scores)*100:.1f}%)
        """
        
        ttk.Label(self.stats_info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # 添加考试合格率统计表格
        self.create_exam_pass_rate_table(scores)
    
    def create_exam_pass_rate_table(self, scores):
        """创建考试合格率统计表格"""
        # 创建表格框架
        table_frame = ttk.LabelFrame(self.stats_info_frame, text="考试合格率统计表", padding="10")
        table_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 创建表格
        columns = ("考试名称", "考试人数", "总分", "合格分数", "合格人数", "通过率")
        table = ttk.Treeview(table_frame, columns=columns, show="headings", height=5)
        
        # 设置列标题和宽度
        column_widths = {
            "考试名称": 200,
            "考试人数": 80,
            "总分": 80,
            "合格分数": 80,
            "合格人数": 80,
            "通过率": 100
        }
        
        for col in columns:
            table.heading(col, text=col)
            table.column(col, width=column_widths.get(col, 100), anchor="center")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        
        table.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按考试分组统计数据
        exam_stats = {}
        for score in scores:
            exam_name = score.get("exam_name", "未知考试")
            if exam_name not in exam_stats:
                exam_stats[exam_name] = {
                    "total": 0,
                    "pass": 0,
                    "total_score": score.get("total_score", 100),
                    "pass_score": 60  # 默认60分为合格分数
                }
            
            exam_stats[exam_name]["total"] += 1
            if score.get("score", 0) >= exam_stats[exam_name]["pass_score"]:  # 使用设置的合格分数
                exam_stats[exam_name]["pass"] += 1
        
        # 填充表格数据
        for exam_name, stats in exam_stats.items():
            pass_rate = (stats["pass"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            table.insert("", tk.END, values=(
                exam_name,
                stats["total"],
                stats["total_score"],
                stats["pass_score"],
                stats["pass"],
                f"{pass_rate:.1f}% ({stats['pass']}/{stats['total']})"
            ))
    
    def export_data(self):
        """导出数据"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['ID', '考试名称', '考生姓名', '部门', '成绩', '总分', '通过率', '提交时间'])
                    
                    for score in self.scores.get("scores", []):
                        writer.writerow([
                            score.get("id"),
                            score.get("exam_name", ""),
                            score.get("student_name", ""),
                            score.get("department", ""),
                            score.get("score", 0),
                            score.get("total_score", 100),
                            f"{score.get('percentage', 0):.1f}%",
                            score.get("submit_time", "")
                        ])
                
                messagebox.showinfo("成功", f"数据已导出到 {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {e}")
    
    def import_from_grading_center(self):
        """从阅卷中心导入数据"""
        try:
            # 创建导入对话框
            import_dialog = tk.Toplevel(self.root)
            import_dialog.title("从阅卷中心导入")
            import_dialog.geometry("500x400")
            import_dialog.transient(self.root)
            import_dialog.grab_set()
            
            # 创建主框架
            main_frame = ttk.Frame(import_dialog, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = ttk.Label(
                main_frame, 
                text="从阅卷中心导入成绩数据", 
                font=("Microsoft YaHei", 16, "bold"),
                foreground=self.colors['primary']
            )
            title_label.pack(pady=(0, 20))
            
            # 选项框架
            options_frame = ttk.LabelFrame(main_frame, text="导入选项", padding="10")
            options_frame.pack(fill=tk.X, pady=(0, 20))
            
            # 导入方式选择
            method_frame = ttk.Frame(options_frame)
            method_frame.pack(fill=tk.X, pady=5)
            
            method_label = ttk.Label(method_frame, text="导入方式:", width=15)
            method_label.pack(side=tk.LEFT)
            
            method_var = tk.StringVar(value="auto")
            auto_radio = ttk.Radiobutton(method_frame, text="自动导入", variable=method_var, value="auto")
            auto_radio.pack(side=tk.LEFT, padx=(0, 10))
            
            manual_radio = ttk.Radiobutton(method_frame, text="手动导入", variable=method_var, value="manual")
            manual_radio.pack(side=tk.LEFT)
            
            # 考试选择（仅手动导入时使用）
            exam_frame = ttk.Frame(options_frame)
            exam_frame.pack(fill=tk.X, pady=5)
            
            exam_label = ttk.Label(exam_frame, text="选择考试:", width=15)
            exam_label.pack(side=tk.LEFT)
            
            exam_var = tk.StringVar()
            exam_combo = ttk.Combobox(exam_frame, textvariable=exam_var, state="readonly", width=30)
            exam_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 导入格式选择
            format_frame = ttk.Frame(options_frame)
            format_frame.pack(fill=tk.X, pady=5)
            
            format_label = ttk.Label(format_frame, text="导入格式:", width=15)
            format_label.pack(side=tk.LEFT)
            
            format_var = tk.StringVar(value="json")
            json_radio = ttk.Radiobutton(format_frame, text="JSON", variable=format_var, value="json")
            json_radio.pack(side=tk.LEFT, padx=(0, 10))
            
            csv_radio = ttk.Radiobutton(format_frame, text="CSV", variable=format_var, value="csv")
            csv_radio.pack(side=tk.LEFT)
            
            # 状态显示区域
            status_frame = ttk.LabelFrame(main_frame, text="导入状态", padding="10")
            status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
            
            status_text = tk.Text(status_frame, height=8, wrap=tk.WORD, font=("Microsoft YaHei", 10))
            status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=status_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            status_text.configure(yscrollcommand=scrollbar.set)
            
            # 禁用文本编辑
            status_text.config(state=tk.DISABLED)
            
            # 按钮区域
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            # 获取考试列表函数
            def fetch_exams():
                try:
                    status_text.config(state=tk.NORMAL)
                    status_text.insert(tk.END, "正在获取考试列表...\n")
                    status_text.config(state=tk.DISABLED)
                    status_text.see(tk.END)
                    
                    # 发送请求获取考试列表
                    response = requests.get("http://localhost:3000/api/exams")
                    if response.status_code == 200:
                        exams = response.json().get("data", [])
                        exam_combo['values'] = ["全部考试"] + [exam.get("examName", "") for exam in exams]
                        exam_combo.current(0)
                        
                        status_text.config(state=tk.NORMAL)
                        status_text.insert(tk.END, f"成功获取 {len(exams)} 个考试\n")
                        status_text.config(state=tk.DISABLED)
                        status_text.see(tk.END)
                    else:
                        status_text.config(state=tk.NORMAL)
                        status_text.insert(tk.END, f"获取考试列表失败: {response.status_code}\n")
                        status_text.config(state=tk.DISABLED)
                        status_text.see(tk.END)
                except Exception as e:
                    status_text.config(state=tk.NORMAL)
                    status_text.insert(tk.END, f"获取考试列表出错: {e}\n")
                    status_text.config(state=tk.DISABLED)
                    status_text.see(tk.END)
            
            # 导入函数
            def do_import():
                try:
                    import_method = method_var.get()
                    import_format = format_var.get()
                    selected_exam = exam_var.get() if import_method == "manual" else None
                    
                    status_text.config(state=tk.NORMAL)
                    status_text.insert(tk.END, f"开始{import_method=='auto' and '自动' or '手动'}导入成绩数据...\n")
                    status_text.config(state=tk.DISABLED)
                    status_text.see(tk.END)
                    
                    # 禁用按钮，防止重复点击
                    import_btn.config(state=tk.DISABLED)
                    refresh_btn.config(state=tk.DISABLED)
                    cancel_btn.config(state=tk.DISABLED)
                    
                    def import_thread():
                        try:
                            if import_method == "auto":
                                # 自动导入本地文件
                                importer = ScoreImporter()
                                result = importer.import_all_pending_files()
                                
                                status_text.config(state=tk.NORMAL)
                                if result:
                                    status_text.insert(tk.END, "自动导入成功\n")
                                else:
                                    status_text.insert(tk.END, "自动导入过程中出现错误\n")
                                status_text.config(state=tk.DISABLED)
                                status_text.see(tk.END)
                            else:
                                # 手动从API获取数据
                                exam_param = "" if selected_exam == "全部考试" else f"?examId={selected_exam}"
                                format_param = f"&format={import_format}"
                                
                                status_text.config(state=tk.NORMAL)
                                status_text.insert(tk.END, f"正在从阅卷中心获取成绩数据...\n")
                                status_text.config(state=tk.DISABLED)
                                status_text.see(tk.END)
                                
                                # 发送请求获取成绩数据
                                response = requests.get(f"http://localhost:3000/api/scores/export{exam_param}{format_param}")
                                if response.status_code == 200:
                                    result = response.json()
                                    if result.get("success"):
                                        filepath = result.get("data", {}).get("scoreStatsFilepath")
                                        count = result.get("data", {}).get("count", 0)
                                        
                                        status_text.config(state=tk.NORMAL)
                                        status_text.insert(tk.END, f"成功获取 {count} 条成绩数据\n")
                                        status_text.insert(tk.END, f"数据已保存到: {filepath}\n")
                                        status_text.config(state=tk.DISABLED)
                                        status_text.see(tk.END)
                                        
                                        # 导入获取的数据
                                        importer = ScoreImporter()
                                        import_result = importer.import_scores_from_file(filepath)
                                        
                                        status_text.config(state=tk.NORMAL)
                                        if import_result:
                                            status_text.insert(tk.END, "导入成功\n")
                                        else:
                                            status_text.insert(tk.END, "导入过程中出现错误\n")
                                        status_text.config(state=tk.DISABLED)
                                        status_text.see(tk.END)
                                    else:
                                        status_text.config(state=tk.NORMAL)
                                        status_text.insert(tk.END, f"获取成绩数据失败: {result.get('message')}\n")
                                        status_text.config(state=tk.DISABLED)
                                        status_text.see(tk.END)
                                else:
                                    status_text.config(state=tk.NORMAL)
                                    status_text.insert(tk.END, f"获取成绩数据失败: {response.status_code}\n")
                                    status_text.config(state=tk.DISABLED)
                                    status_text.see(tk.END)
                            
                            # 导入完成后刷新成绩列表
                            self.root.after(0, self.refresh_score_list)
                        except Exception as e:
                            status_text.config(state=tk.NORMAL)
                            status_text.insert(tk.END, f"导入过程中出现错误: {e}\n")
                            status_text.config(state=tk.DISABLED)
                            status_text.see(tk.END)
                        finally:
                            # 恢复按钮状态
                            import_btn.config(state=tk.NORMAL)
                            refresh_btn.config(state=tk.NORMAL)
                            cancel_btn.config(state=tk.NORMAL)
                    
                    # 创建线程执行导入操作
                    threading.Thread(target=import_thread).start()
                    
                except Exception as e:
                    status_text.config(state=tk.NORMAL)
                    status_text.insert(tk.END, f"导入过程中出现错误: {e}\n")
                    status_text.config(state=tk.DISABLED)
                    status_text.see(tk.END)
                    
                    # 恢复按钮状态
                    import_btn.config(state=tk.NORMAL)
                    refresh_btn.config(state=tk.NORMAL)
                    cancel_btn.config(state=tk.NORMAL)
            
            # 导入按钮
            import_btn = tk.Button(
                button_frame, 
                text="开始导入", 
                command=do_import,
                bg=self.colors['success'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=8,
                cursor="hand2"
            )
            import_btn.pack(side=tk.LEFT, padx=5)
            
            # 刷新按钮
            refresh_btn = tk.Button(
                button_frame, 
                text="刷新考试列表", 
                command=fetch_exams,
                bg=self.colors['info'],
                fg="white",
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=8,
                cursor="hand2"
            )
            refresh_btn.pack(side=tk.LEFT, padx=5)
            
            # 取消按钮
            cancel_btn = tk.Button(
                button_frame, 
                text="关闭", 
                command=import_dialog.destroy,
                bg=self.colors['light'],
                fg=self.colors['dark'],
                font=("Microsoft YaHei", 10),
                relief="flat",
                borderwidth=0,
                padx=15,
                pady=8,
                cursor="hand2"
            )
            cancel_btn.pack(side=tk.RIGHT, padx=5)
            
            # 初始获取考试列表
            fetch_exams()
            
        except Exception as e:
            messagebox.showerror("错误", f"打开导入对话框失败: {e}")
    
    def run(self):
        """运行应用"""
        self.root.mainloop()

class ScoreDialog:
    """成绩编辑对话框"""
    def __init__(self, parent, score_manager, score_data=None):
        self.score_manager = score_manager
        self.score_data = score_data
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑成绩" if score_data else "添加成绩")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        if score_data:
            self.load_score_data()
    
    def setup_ui(self):
        """设置界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        fields = [
            ("考试ID:", "exam_id"),
            ("考试名称:", "exam_name"),
            ("考生ID:", "student_id"),
            ("考生姓名:", "student_name"),
            ("部门:", "department"),
            ("成绩:", "score"),
            ("总分:", "total_score"),
            ("提交时间:", "submit_time")
        ]
        
        self.field_vars = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="w", pady=2)
            var = tk.StringVar()
            self.field_vars[field] = var
            ttk.Entry(main_frame, textvariable=var).grid(row=i, column=1, sticky="we", pady=2, padx=(5, 0))
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_score).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
    
    def load_score_data(self):
        """加载成绩数据"""
        if self.score_data:
            for field, var in self.field_vars.items():
                value = self.score_data.get(field, "")
                var.set(str(value))
    
    def save_score(self):
        """保存成绩"""
        try:
            # 获取表单数据
            score_data = {}
            for field, var in self.field_vars.items():
                value = var.get().strip()
                if field in ['exam_id', 'student_id', 'score', 'total_score']:
                    try:
                        value = int(value)
                    except ValueError:
                        messagebox.showerror("错误", f"{field} 必须是数字")
                        return
                score_data[field] = value
            
            # 计算百分比
            if score_data.get('score') and score_data.get('total_score'):
                score_data['percentage'] = (score_data['score'] / score_data['total_score']) * 100
            
            # 设置状态
            score_data['status'] = 'completed'
            
            if self.score_data:
                # 编辑模式
                score_data['id'] = self.score_data['id']
                score_data['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 更新数据
                for i, score in enumerate(self.score_manager.scores["scores"]):
                    if score['id'] == score_data['id']:
                        self.score_manager.scores["scores"][i] = score_data
                        break
            else:
                # 新增模式
                score_data['id'] = self.get_next_score_id()
                score_data['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                score_data['updated_at'] = score_data['created_at']
                
                self.score_manager.scores["scores"].append(score_data)
            
            self.score_manager.save_scores()
            self.dialog.destroy()
            messagebox.showinfo("成功", "成绩数据已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def get_next_score_id(self):
        """获取下一个成绩ID"""
        scores = self.score_manager.scores.get("scores", [])
        if not scores:
            return 1
        return max(score.get("id", 0) for score in scores) + 1

if __name__ == "__main__":
    app = SimpleScoreManager()
    app.run()