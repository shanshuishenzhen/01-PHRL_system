#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
考试发布管理器

负责从题库选择试卷，创建考试，分配学生，发布考试到客户端。

更新日志：
- 2025-01-07：创建考试发布管理器
"""

import os
import sys
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.error_handler import handle_error
from common.sql_security import ParameterizedQuery


class ExamPublisher:
    """考试发布管理器"""
    
    def __init__(self):
        self.logger = get_logger("exam_publisher")
        self.exams_file = Path(__file__).parent / "published_exams.json"
        self.enrollments_file = Path(__file__).parent / "enrollments.json"
        
        # 确保文件存在
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """确保必要的文件存在"""
        if not self.exams_file.exists():
            self.save_published_exams([])
        
        if not self.enrollments_file.exists():
            self.save_enrollments([])
    
    def get_available_papers(self) -> List[Dict]:
        """从题库获取可用的试卷"""
        try:
            db_path = Path(__file__).parent.parent / "question_bank_web" / "local_dev.db"
            if not db_path.exists():
                self.logger.warning("题库数据库不存在")
                return []
            
            db = ParameterizedQuery(str(db_path))
            papers_raw = db.execute_query("""
                SELECT p.id, p.name, p.description, p.duration, p.total_score,
                       p.created_at, COUNT(pq.question_id) as question_count
                FROM papers p
                LEFT JOIN paper_questions pq ON p.id = pq.paper_id
                GROUP BY p.id, p.name, p.description, p.duration, p.total_score, p.created_at
                ORDER BY p.created_at DESC
            """)

            # 转换为字典格式
            papers = []
            for row in papers_raw or []:
                paper = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'duration': row[3],
                    'total_score': row[4],
                    'created_at': row[5],
                    'question_count': row[6]
                }
                papers.append(paper)

            return papers
            
        except Exception as e:
            self.logger.error(f"获取试卷列表失败: {e}")
            return []
    
    def get_available_students(self) -> List[Dict]:
        """获取可用的学生列表"""
        try:
            db_path = Path(__file__).parent.parent / "user_management" / "users.db"
            if not db_path.exists():
                self.logger.warning("用户数据库不存在")
                return []
            
            db = ParameterizedQuery(str(db_path))
            students_raw = db.execute_query("""
                SELECT id, username, real_name, department, email
                FROM users
                WHERE role = 'student' AND status = 'active'
                ORDER BY department, real_name
            """)

            # 转换为字典格式
            students = []
            for row in students_raw or []:
                student = {
                    'id': row[0],
                    'username': row[1],
                    'real_name': row[2],
                    'department': row[3],
                    'email': row[4]
                }
                students.append(student)

            return students
            
        except Exception as e:
            self.logger.error(f"获取学生列表失败: {e}")
            return []
    
    def create_exam(self, exam_data: Dict) -> str:
        """创建新考试"""
        try:
            exam_id = str(uuid.uuid4())
            
            exam = {
                "id": exam_id,
                "paper_id": exam_data["paper_id"],
                "title": exam_data["title"],
                "description": exam_data.get("description", ""),
                "duration": exam_data["duration"],
                "total_score": exam_data["total_score"],
                "start_time": exam_data["start_time"],
                "end_time": exam_data["end_time"],
                "status": "draft",  # draft, published, active, completed, cancelled
                "created_by": exam_data.get("created_by", "admin"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "settings": {
                    "allow_review": exam_data.get("allow_review", True),
                    "show_score": exam_data.get("show_score", True),
                    "random_questions": exam_data.get("random_questions", False),
                    "max_attempts": exam_data.get("max_attempts", 1)
                }
            }
            
            # 保存考试
            published_exams = self.load_published_exams()
            published_exams.append(exam)
            self.save_published_exams(published_exams)
            
            self.logger.info(f"创建考试成功: {exam['title']} (ID: {exam_id})")
            return exam_id
            
        except Exception as e:
            self.logger.error(f"创建考试失败: {e}")
            raise
    
    def assign_students(self, exam_id: str, student_ids: List[str]) -> bool:
        """为考试分配学生"""
        try:
            # 加载现有的enrollments（可能是新格式或旧格式）
            existing_enrollments = self.load_enrollments()

            # 将现有数据转换为我们的内部格式（每个学生一个记录）
            internal_enrollments = []

            for enrollment in existing_enrollments:
                if isinstance(enrollment, dict):
                    # 检查是否是新格式（每个学生一个记录）
                    if "student_id" in enrollment:
                        internal_enrollments.append(enrollment)
                    # 检查是否是旧格式（每个考试一个记录，包含user_ids数组）
                    elif "user_ids" in enrollment:
                        for user_id in enrollment.get("user_ids", []):
                            internal_enrollment = {
                                "id": str(uuid.uuid4()),
                                "exam_id": enrollment.get("exam_id"),
                                "student_id": str(user_id),
                                "status": "assigned",
                                "assigned_at": enrollment.get("created_at", datetime.now().isoformat()),
                                "attempts": 0,
                                "max_attempts": 1
                            }
                            internal_enrollments.append(internal_enrollment)

            # 移除该考试的现有分配
            internal_enrollments = [e for e in internal_enrollments if e.get("exam_id") != exam_id]

            # 添加新的分配
            for student_id in student_ids:
                enrollment = {
                    "id": str(uuid.uuid4()),
                    "exam_id": exam_id,
                    "student_id": str(student_id),  # 确保是字符串
                    "status": "assigned",  # assigned, started, completed, cancelled
                    "assigned_at": datetime.now().isoformat(),
                    "attempts": 0,
                    "max_attempts": 1
                }
                internal_enrollments.append(enrollment)

            self.save_enrollments(internal_enrollments)
            self.logger.info(f"为考试 {exam_id} 分配了 {len(student_ids)} 个学生")
            return True

        except Exception as e:
            self.logger.error(f"分配学生失败: {e}")
            return False
    
    def publish_exam(self, exam_id: str) -> bool:
        """发布考试"""
        try:
            published_exams = self.load_published_exams()
            
            # 找到考试并更新状态
            for exam in published_exams:
                if exam["id"] == exam_id:
                    exam["status"] = "published"
                    exam["updated_at"] = datetime.now().isoformat()
                    break
            else:
                raise ValueError(f"考试 {exam_id} 不存在")
            
            self.save_published_exams(published_exams)
            
            # 触发数据同步
            self.trigger_data_sync()
            
            self.logger.info(f"考试 {exam_id} 发布成功")
            return True
            
        except Exception as e:
            self.logger.error(f"发布考试失败: {e}")
            return False
    
    def trigger_data_sync(self):
        """触发数据同步"""
        try:
            from common.data_sync_manager import DataSyncManager
            sync_manager = DataSyncManager()
            sync_manager.sync_published_exams_to_client()
            self.logger.info("数据同步触发成功")
        except Exception as e:
            self.logger.warning(f"触发数据同步失败: {e}")
    
    def get_published_exams(self) -> List[Dict]:
        """获取已发布的考试列表"""
        return self.load_published_exams()
    
    def get_exam_enrollments(self, exam_id: str) -> List[Dict]:
        """获取考试的学生分配情况"""
        enrollments = self.load_enrollments()
        return [e for e in enrollments if e.get("exam_id") == exam_id]
    
    def load_published_exams(self) -> List[Dict]:
        """加载已发布的考试"""
        try:
            if self.exams_file.exists():
                with open(self.exams_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"加载考试数据失败: {e}")
            return []
    
    def save_published_exams(self, exams: List[Dict]):
        """保存已发布的考试"""
        try:
            with open(self.exams_file, 'w', encoding='utf-8') as f:
                json.dump(exams, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存考试数据失败: {e}")
            raise
    
    def load_enrollments(self) -> List[Dict]:
        """加载学生分配数据"""
        try:
            if self.enrollments_file.exists():
                with open(self.enrollments_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容两种格式：新格式（列表）和旧格式（字典包含enrollments键）
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "enrollments" in data:
                        return data["enrollments"]
                    else:
                        return []
            return []
        except Exception as e:
            self.logger.error(f"加载分配数据失败: {e}")
            return []

    def save_enrollments(self, enrollments: List[Dict]):
        """保存学生分配数据"""
        try:
            # 转换为考试管理模块期望的格式
            # 将每个学生的单独记录转换为按考试分组的格式
            exam_enrollments = {}

            for enrollment in enrollments:
                exam_id = enrollment.get("exam_id")
                student_id = enrollment.get("student_id")

                if exam_id not in exam_enrollments:
                    exam_enrollments[exam_id] = {
                        "exam_id": exam_id,
                        "user_ids": [],
                        "status": "active",
                        "created_at": enrollment.get("assigned_at", "")
                    }

                if student_id not in exam_enrollments[exam_id]["user_ids"]:
                    exam_enrollments[exam_id]["user_ids"].append(student_id)

            # 保存为考试管理模块期望的格式
            data = {
                "enrollments": list(exam_enrollments.values())
            }

            with open(self.enrollments_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"保存了 {len(exam_enrollments)} 个考试的分配数据")

        except Exception as e:
            self.logger.error(f"保存分配数据失败: {e}")
            raise


class ExamPublisherGUI:
    """考试发布GUI界面"""

    def __init__(self):
        import tkinter as tk
        from tkinter import ttk, messagebox

        self.publisher = ExamPublisher()

        self.root = tk.Tk()
        self.root.title("考试发布管理 - PH&RL系统")
        self.root.geometry("1000x700")

        self.create_widgets()
        self.refresh_data()

    def create_widgets(self):
        """创建界面组件"""
        import tkinter as tk
        from tkinter import ttk

        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 标题
        title_label = ttk.Label(main_frame, text="考试发布管理", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 创建笔记本控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建考试标签页
        self.create_exam_tab()

        # 已发布考试标签页
        self.published_exams_tab()

    def create_exam_tab(self):
        """创建考试标签页"""
        import tkinter as tk
        from tkinter import ttk

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="创建考试")

        # 试卷选择
        ttk.Label(frame, text="选择试卷:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.paper_var = tk.StringVar()
        self.paper_combo = ttk.Combobox(frame, textvariable=self.paper_var, width=50)
        self.paper_combo.grid(row=0, column=1, padx=5, pady=5)

        # 考试标题
        ttk.Label(frame, text="考试标题:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.title_entry = ttk.Entry(frame, width=50)
        self.title_entry.grid(row=1, column=1, padx=5, pady=5)

        # 考试描述
        ttk.Label(frame, text="考试描述:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.desc_text = tk.Text(frame, width=50, height=3)
        self.desc_text.grid(row=2, column=1, padx=5, pady=5)

        # 考试时长
        ttk.Label(frame, text="考试时长(分钟):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.duration_entry = ttk.Entry(frame, width=20)
        self.duration_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # 开始时间
        ttk.Label(frame, text="开始时间:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.start_time_entry = ttk.Entry(frame, width=30)
        self.start_time_entry.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.start_time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # 结束时间
        ttk.Label(frame, text="结束时间:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.end_time_entry = ttk.Entry(frame, width=30)
        self.end_time_entry.grid(row=5, column=1, sticky="w", padx=5, pady=5)
        end_time = datetime.now() + timedelta(hours=2)
        self.end_time_entry.insert(0, end_time.strftime("%Y-%m-%d %H:%M:%S"))

        # 学生选择
        ttk.Label(frame, text="选择学生:").grid(row=6, column=0, sticky="nw", padx=5, pady=5)

        # 学生列表框架
        students_frame = ttk.Frame(frame)
        students_frame.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

        # 学生列表
        self.students_listbox = tk.Listbox(students_frame, selectmode=tk.MULTIPLE, height=8)
        self.students_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        scrollbar = ttk.Scrollbar(students_frame, orient=tk.VERTICAL, command=self.students_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.students_listbox.config(yscrollcommand=scrollbar.set)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="创建考试", command=self.create_exam).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新数据", command=self.refresh_data).pack(side=tk.LEFT, padx=5)

    def published_exams_tab(self):
        """已发布考试标签页"""
        import tkinter as tk
        from tkinter import ttk

        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="已发布考试")

        # 考试列表
        columns = ("ID", "标题", "状态", "开始时间", "结束时间", "分配学生")
        self.exams_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.exams_tree.heading(col, text=col)
            self.exams_tree.column(col, width=150)

        self.exams_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="发布考试", command=self.publish_selected_exam).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查看详情", command=self.view_exam_details).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新列表", command=self.refresh_published_exams).pack(side=tk.LEFT, padx=5)

    def refresh_data(self):
        """刷新数据"""
        # 刷新试卷列表
        papers = self.publisher.get_available_papers()
        paper_values = [f"{p['name']} (ID: {p['id']}, {p['question_count']}题)" for p in papers]
        self.paper_combo['values'] = paper_values
        self.papers_data = papers

        # 刷新学生列表
        students = self.publisher.get_available_students()
        self.students_listbox.delete(0, tk.END)
        for student in students:
            display_text = f"{student['real_name']} ({student['username']}) - {student['department']}"
            self.students_listbox.insert(tk.END, display_text)
        self.students_data = students

        # 刷新已发布考试
        self.refresh_published_exams()

    def refresh_published_exams(self):
        """刷新已发布考试列表"""
        # 清空现有数据
        for item in self.exams_tree.get_children():
            self.exams_tree.delete(item)

        # 加载考试数据
        exams = self.publisher.get_published_exams()
        for exam in exams:
            enrollments = self.publisher.get_exam_enrollments(exam['id'])
            student_count = len(enrollments)

            self.exams_tree.insert("", tk.END, values=(
                exam['id'][:8] + "...",
                exam['title'],
                exam['status'],
                exam['start_time'],
                exam['end_time'],
                f"{student_count}人"
            ))

    def create_exam(self):
        """创建考试"""
        try:
            # 验证输入
            if not self.paper_var.get():
                messagebox.showerror("错误", "请选择试卷")
                return

            if not self.title_entry.get():
                messagebox.showerror("错误", "请输入考试标题")
                return

            # 获取选中的试卷
            paper_index = self.paper_combo.current()
            if paper_index < 0:
                messagebox.showerror("错误", "请选择有效的试卷")
                return

            selected_paper = self.papers_data[paper_index]

            # 获取选中的学生
            selected_indices = self.students_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("错误", "请选择至少一个学生")
                return

            selected_students = [self.students_data[i]['id'] for i in selected_indices]

            # 创建考试数据
            exam_data = {
                "paper_id": selected_paper['id'],
                "title": self.title_entry.get(),
                "description": self.desc_text.get("1.0", tk.END).strip(),
                "duration": int(self.duration_entry.get() or selected_paper['duration'] or 60),
                "total_score": selected_paper['total_score'] or 100,
                "start_time": self.start_time_entry.get(),
                "end_time": self.end_time_entry.get()
            }

            # 创建考试
            exam_id = self.publisher.create_exam(exam_data)

            # 分配学生
            self.publisher.assign_students(exam_id, selected_students)

            messagebox.showinfo("成功", f"考试创建成功！\n考试ID: {exam_id}")

            # 刷新界面
            self.refresh_published_exams()

        except Exception as e:
            messagebox.showerror("错误", f"创建考试失败: {str(e)}")

    def publish_selected_exam(self):
        """发布选中的考试"""
        selection = self.exams_tree.selection()
        if not selection:
            messagebox.showerror("错误", "请选择要发布的考试")
            return

        # 获取考试ID（需要从完整数据中获取）
        item = self.exams_tree.item(selection[0])
        exam_title = item['values'][1]

        # 找到完整的考试ID
        exams = self.publisher.get_published_exams()
        exam_id = None
        for exam in exams:
            if exam['title'] == exam_title:
                exam_id = exam['id']
                break

        if not exam_id:
            messagebox.showerror("错误", "无法找到考试ID")
            return

        try:
            success = self.publisher.publish_exam(exam_id)
            if success:
                messagebox.showinfo("成功", "考试发布成功！")
                self.refresh_published_exams()
            else:
                messagebox.showerror("错误", "考试发布失败")
        except Exception as e:
            messagebox.showerror("错误", f"发布考试时出错: {str(e)}")

    def view_exam_details(self):
        """查看考试详情"""
        selection = self.exams_tree.selection()
        if not selection:
            messagebox.showinfo("提示", "请选择要查看的考试")
            return

        # 这里可以实现考试详情查看功能
        messagebox.showinfo("提示", "考试详情查看功能待实现")

    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    try:
        # 启动GUI
        app = ExamPublisherGUI()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        # 如果GUI启动失败，运行命令行版本
        publisher = ExamPublisher()

        print("📋 可用试卷:")
        papers = publisher.get_available_papers()
        for paper in papers[:5]:
            print(f"  - {paper['name']} ({paper['question_count']}题)")

        print("\n👥 可用学生:")
        students = publisher.get_available_students()
        for student in students[:5]:
            print(f"  - {student['real_name']} ({student['username']})")

        print(f"\n📝 已发布考试: {len(publisher.get_published_exams())}个")


if __name__ == "__main__":
    main()
