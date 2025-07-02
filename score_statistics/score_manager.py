import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ScoreManager:
    """成绩统计管理主类"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("成绩统计 - PH&RL 在线考试系统")
        self.root.geometry("1200x800")
        
        # 成绩数据存储
        self.scores = self.load_scores()
        self.current_page = 1
        self.page_size = 20
        
        # 统计维度
        self.statistics_dimensions = {
            'exam': '按考试统计',
            'student': '按学生统计', 
            'department': '按部门统计',
            'date': '按日期统计'
        }
        
        self.setup_ui()
        self.refresh_score_list()
        self.update_statistics()
    
    def load_scores(self):
        """加载成绩数据"""
        try:
            if os.path.exists('score_statistics/scores.json'):
                with open('score_statistics/scores.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载成绩数据失败: {e}")
        
        # 返回示例成绩数据
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
                },
                {
                    "id": 2,
                    "exam_id": 101,
                    "exam_name": "2024年度计算机基础知识认证",
                    "student_id": 1002,
                    "student_name": "李四",
                    "department": "数学系",
                    "score": 92,
                    "total_score": 100,
                    "percentage": 92.0,
                    "submit_time": "2024-01-15 15:20:00",
                    "status": "completed"
                },
                {
                    "id": 3,
                    "exam_id": 102,
                    "exam_name": "大学英语四级模拟考试",
                    "student_id": 1001,
                    "student_name": "张三",
                    "department": "计算机系",
                    "score": 78,
                    "total_score": 100,
                    "percentage": 78.0,
                    "submit_time": "2024-01-16 10:15:00",
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
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右分栏
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 左侧：成绩列表
        self.create_score_list_frame(left_frame)
        
        # 右侧：统计分析
        self.create_statistics_frame(right_frame)
    
    def create_score_list_frame(self, parent):
        """创建成绩列表区域"""
        # 标题
        title_label = ttk.Label(parent, text="成绩明细", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 工具栏
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(toolbar, text="刷新", command=self.refresh_score_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="导出", command=self.export_scores).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="添加成绩", command=self.add_score).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        ttk.Label(toolbar, text="搜索:").pack(side=tk.RIGHT, padx=(10, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.RIGHT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search)
        
        # 成绩列表
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ("ID", "考试名称", "学生姓名", "部门", "成绩", "总分", "百分比", "提交时间")
        self.score_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        column_widths = [50, 200, 100, 100, 60, 60, 80, 150]
        for i, col in enumerate(columns):
            self.score_tree.heading(col, text=col)
            self.score_tree.column(col, width=column_widths[i])
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.score_tree.yview)
        self.score_tree.configure(yscrollcommand=scrollbar.set)
        
        self.score_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.score_tree.bind("<Double-1>", self.edit_score)
        
        # 分页控件
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.page_info_label = ttk.Label(pagination_frame, text="")
        self.page_info_label.pack(side=tk.LEFT)
        
        button_frame = ttk.Frame(pagination_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="上一页", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="下一页", command=self.next_page).pack(side=tk.LEFT, padx=2)
    
    def create_statistics_frame(self, parent):
        """创建统计分析区域"""
        # 标题
        title_label = ttk.Label(parent, text="统计分析", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 统计维度选择
        dimension_frame = ttk.LabelFrame(parent, text="统计维度", padding="5")
        dimension_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.dimension_var = tk.StringVar(value="exam")
        for key, value in self.statistics_dimensions.items():
            ttk.Radiobutton(dimension_frame, text=value, variable=self.dimension_var, 
                           value=key, command=self.update_statistics).pack(anchor=tk.W)
        
        # 统计图表区域
        chart_frame = ttk.LabelFrame(parent, text="统计图表", padding="5")
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建matplotlib图表
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 统计信息区域
        info_frame = ttk.LabelFrame(parent, text="统计信息", padding="5")
        info_frame.pack(fill=tk.X)
        
        self.stats_text = tk.Text(info_frame, height=8, width=40)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
    
    def refresh_score_list(self):
        """刷新成绩列表"""
        # 清空现有数据
        for item in self.score_tree.get_children():
            self.score_tree.delete(item)
        
        # 获取筛选后的成绩列表
        filtered_scores = self.get_filtered_scores()
        
        # 计算分页
        total_scores = len(filtered_scores)
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_scores = filtered_scores[start_idx:end_idx]
        
        # 插入数据
        for score in page_scores:
            self.score_tree.insert("", tk.END, values=(
                score.get("id"),
                score.get("exam_name", ""),
                score.get("student_name", ""),
                score.get("department", ""),
                score.get("score", 0),
                score.get("total_score", 100),
                f"{score.get('percentage', 0):.1f}%",
                score.get("submit_time", "")
            ))
        
        # 更新分页信息
        total_pages = (total_scores + self.page_size - 1) // self.page_size
        self.page_info_label.config(text=f"第 {self.current_page} 页，共 {total_pages} 页，总计 {total_scores} 条记录")
    
    def get_filtered_scores(self):
        """获取筛选后的成绩列表"""
        scores = self.scores.get("scores", [])
        filtered = []
        
        search_text = self.search_var.get().lower()
        
        for score in scores:
            # 搜索筛选
            if search_text:
                searchable_fields = [
                    str(score.get("exam_name", "")),
                    str(score.get("student_name", "")),
                    str(score.get("department", "")),
                    str(score.get("score", ""))
                ]
                if not any(search_text in field.lower() for field in searchable_fields):
                    continue
            
            filtered.append(score)
        
        return filtered
    
    def on_search(self, event=None):
        """搜索事件处理"""
        self.current_page = 1
        self.refresh_score_list()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_score_list()
    
    def next_page(self):
        """下一页"""
        filtered_scores = self.get_filtered_scores()
        total_pages = (len(filtered_scores) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_score_list()
    
    def update_statistics(self):
        """更新统计分析"""
        scores = self.scores.get("scores", [])
        if not scores:
            return
        
        dimension = self.dimension_var.get()
        
        # 清空图表
        self.ax.clear()
        
        if dimension == "exam":
            self.analyze_by_exam(scores)
        elif dimension == "student":
            self.analyze_by_student(scores)
        elif dimension == "department":
            self.analyze_by_department(scores)
        elif dimension == "date":
            self.analyze_by_date(scores)
        
        # 更新统计信息
        self.update_stats_info(scores)
        
        # 刷新图表
        self.canvas.draw()
    
    def analyze_by_exam(self, scores):
        """按考试分析"""
        exam_stats = {}
        for score in scores:
            exam_name = score.get("exam_name", "未知考试")
            if exam_name not in exam_stats:
                exam_stats[exam_name] = []
            exam_stats[exam_name].append(score.get("percentage", 0))
        
        # 计算平均分
        exam_names = list(exam_stats.keys())
        avg_scores = [np.mean(exam_stats[name]) for name in exam_names]
        
        # 绘制柱状图
        bars = self.ax.bar(exam_names, avg_scores, color='skyblue')
        self.ax.set_title("各考试平均成绩")
        self.ax.set_ylabel("平均分 (%)")
        self.ax.set_xlabel("考试名称")
        
        # 添加数值标签
        for bar, score in zip(bars, avg_scores):
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score:.1f}%', ha='center', va='bottom')
        
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
    
    def analyze_by_student(self, scores):
        """按学生分析"""
        student_stats = {}
        for score in scores:
            student_name = score.get("student_name", "未知学生")
            if student_name not in student_stats:
                student_stats[student_name] = []
            student_stats[student_name].append(score.get("percentage", 0))
        
        # 计算平均分
        student_names = list(student_stats.keys())
        avg_scores = [np.mean(student_stats[name]) for name in student_names]
        
        # 绘制柱状图
        bars = self.ax.bar(student_names, avg_scores, color='lightgreen')
        self.ax.set_title("各学生平均成绩")
        self.ax.set_ylabel("平均分 (%)")
        self.ax.set_xlabel("学生姓名")
        
        # 添加数值标签
        for bar, score in zip(bars, avg_scores):
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score:.1f}%', ha='center', va='bottom')
        
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
    
    def analyze_by_department(self, scores):
        """按部门分析"""
        dept_stats = {}
        for score in scores:
            dept = score.get("department", "未知部门")
            if dept not in dept_stats:
                dept_stats[dept] = []
            dept_stats[dept].append(score.get("percentage", 0))
        
        # 计算平均分
        dept_names = list(dept_stats.keys())
        avg_scores = [np.mean(dept_stats[name]) for name in dept_names]
        
        # 绘制柱状图
        bars = self.ax.bar(dept_names, avg_scores, color='lightcoral')
        self.ax.set_title("各部门平均成绩")
        self.ax.set_ylabel("平均分 (%)")
        self.ax.set_xlabel("部门")
        
        # 添加数值标签
        for bar, score in zip(bars, avg_scores):
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{score:.1f}%', ha='center', va='bottom')
    
    def analyze_by_date(self, scores):
        """按日期分析"""
        date_stats = {}
        for score in scores:
            submit_time = score.get("submit_time", "")
            if submit_time:
                date = submit_time.split()[0]  # 提取日期部分
                if date not in date_stats:
                    date_stats[date] = []
                date_stats[date].append(score.get("percentage", 0))
        
        if not date_stats:
            self.ax.text(0.5, 0.5, '无日期数据', ha='center', va='center', transform=self.ax.transAxes)
            return
        
        # 计算平均分
        dates = sorted(date_stats.keys())
        avg_scores = [np.mean(date_stats[date]) for date in dates]
        
        # 绘制折线图
        self.ax.plot(dates, avg_scores, marker='o', color='orange', linewidth=2)
        self.ax.set_title("按日期平均成绩趋势")
        self.ax.set_ylabel("平均分 (%)")
        self.ax.set_xlabel("日期")
        
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
    
    def update_stats_info(self, scores):
        """更新统计信息"""
        if not scores:
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "暂无成绩数据")
            return
        
        # 计算基本统计信息
        percentages = [score.get("percentage", 0) for score in scores]
        
        stats_info = f"""基本统计信息：
        
总成绩数：{len(scores)}
平均分：{np.mean(percentages):.2f}%
最高分：{np.max(percentages):.2f}%
最低分：{np.min(percentages):.2f}%
标准差：{np.std(percentages):.2f}%

分数段分布：
优秀 (90-100分)：{len([p for p in percentages if p >= 90])} 人
良好 (80-89分)：{len([p for p in percentages if 80 <= p < 90])} 人
中等 (70-79分)：{len([p for p in percentages if 70 <= p < 80])} 人
及格 (60-69分)：{len([p for p in percentages if 60 <= p < 70])} 人
不及格 (<60分)：{len([p for p in percentages if p < 60])} 人

及格率：{len([p for p in percentages if p >= 60]) / len(percentages) * 100:.1f}%
优秀率：{len([p for p in percentages if p >= 90]) / len(percentages) * 100:.1f}%
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_info)
    
    def add_score(self):
        """添加成绩"""
        ScoreDialog(self.root, self, None)
    
    def edit_score(self, event=None):
        """编辑成绩"""
        selection = self.score_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的成绩")
            return
        
        # 获取选中的成绩ID
        score_id = self.score_tree.item(selection[0])['values'][0]
        score = self.get_score_by_id(score_id)
        if score:
            ScoreDialog(self.root, self, score)
    
    def get_score_by_id(self, score_id):
        """根据ID获取成绩"""
        for score in self.scores.get("scores", []):
            if score.get("id") == score_id:
                return score
        return None
    
    def export_scores(self):
        """导出成绩"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="导出成绩",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            scores = self.get_filtered_scores()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(['ID', '考试名称', '学生姓名', '部门', '成绩', '总分', '百分比', '提交时间'])
                
                # 写入数据
                for score in scores:
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
            
            messagebox.showinfo("成功", f"成绩数据已导出到：{file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")
    
    def run(self):
        """运行成绩统计界面"""
        self.root.mainloop()


class ScoreDialog:
    """成绩编辑对话框"""
    def __init__(self, parent, score_manager, score_data=None):
        self.parent = parent
        self.score_manager = score_manager
        self.score_data = score_data
        self.is_edit = score_data is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑成绩" if self.is_edit else "添加成绩")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        if self.is_edit:
            self.load_score_data()
    
    def setup_ui(self):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        fields = [
            ("考试ID:", "exam_id"),
            ("考试名称:", "exam_name"),
            ("学生ID:", "student_id"),
            ("学生姓名:", "student_name"),
            ("部门:", "department"),
            ("成绩:", "score"),
            ("总分:", "total_score")
        ]
        
        self.field_vars = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            self.field_vars[field] = var
            entry = ttk.Entry(main_frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_score).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_score_data(self):
        """加载成绩数据到表单"""
        if not self.score_data:
            return
        
        self.field_vars["exam_id"].set(str(self.score_data.get("exam_id", "")))
        self.field_vars["exam_name"].set(self.score_data.get("exam_name", ""))
        self.field_vars["student_id"].set(str(self.score_data.get("student_id", "")))
        self.field_vars["student_name"].set(self.score_data.get("student_name", ""))
        self.field_vars["department"].set(self.score_data.get("department", ""))
        self.field_vars["score"].set(str(self.score_data.get("score", "")))
        self.field_vars["total_score"].set(str(self.score_data.get("total_score", "")))
    
    def save_score(self):
        """保存成绩数据"""
        try:
            # 获取表单数据
            exam_id = int(self.field_vars["exam_id"].get().strip())
            exam_name = self.field_vars["exam_name"].get().strip()
            student_id = int(self.field_vars["student_id"].get().strip())
            student_name = self.field_vars["student_name"].get().strip()
            department = self.field_vars["department"].get().strip()
            score = float(self.field_vars["score"].get().strip())
            total_score = float(self.field_vars["total_score"].get().strip())
            
            # 验证数据
            if not exam_name or not student_name or not department:
                messagebox.showerror("错误", "请填写所有必填字段")
                return
            
            if score < 0 or score > total_score:
                messagebox.showerror("错误", "成绩不能为负数且不能超过总分")
                return
            
            # 计算百分比
            percentage = (score / total_score) * 100
            
            # 准备成绩数据
            score_data = {
                "exam_id": exam_id,
                "exam_name": exam_name,
                "student_id": student_id,
                "student_name": student_name,
                "department": department,
                "score": score,
                "total_score": total_score,
                "percentage": percentage,
                "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "completed"
            }
            
            if self.is_edit:
                # 编辑模式
                score_data["id"] = self.score_data["id"]
                
                # 更新成绩数据
                for i, score_item in enumerate(self.score_manager.scores["scores"]):
                    if score_item["id"] == self.score_data["id"]:
                        self.score_manager.scores["scores"][i] = score_data
                        break
            else:
                # 新增模式
                score_data["id"] = self.get_next_score_id()
                self.score_manager.scores["scores"].append(score_data)
            
            # 保存数据
            self.score_manager.save_scores()
            self.score_manager.refresh_score_list()
            self.score_manager.update_statistics()
            
            messagebox.showinfo("成功", "成绩保存成功")
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")
    
    def get_next_score_id(self):
        """获取下一个成绩ID"""
        max_id = 0
        for score in self.score_manager.scores.get("scores", []):
            max_id = max(max_id, score.get("id", 0))
        return max_id + 1


if __name__ == "__main__":
    app = ScoreManager()
    app.run() 