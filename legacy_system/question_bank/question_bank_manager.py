#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库管理模块
负责题目的录入、分类、审核和维护
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime

class QuestionBankManager:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("题库管理模块")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 题库数据
        self.questions = []
        self.categories = ["选择题", "填空题", "简答题", "编程题"]
        self.difficulty_levels = ["简单", "中等", "困难"]
        
        # 数据文件路径
        self.data_file = "question_bank_data.json"
        self.load_data()
        
        # 设置界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 标题
        title_label = ttk.Label(main_frame, text="题库管理系统", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 创建左侧题目列表
        self.create_question_list(main_frame)
        
        # 创建右侧题目编辑区域
        self.create_question_editor(main_frame)
        
        # 创建底部按钮区域
        self.create_buttons(main_frame)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def create_question_list(self, parent):
        """创建题目列表"""
        # 左侧框架
        left_frame = ttk.LabelFrame(parent, text="题目列表", padding="5")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        
        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill="x", pady=(0, 5))
        
        ttk.Label(search_frame, text="搜索:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_questions)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # 题目列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        # 创建Treeview
        columns = ("序号", "题目", "类型", "难度")
        self.question_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # 设置列标题
        for col in columns:
            self.question_tree.heading(col, text=col)
            self.question_tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.question_tree.yview)
        self.question_tree.configure(yscrollcommand=scrollbar.set)
        
        self.question_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定选择事件
        self.question_tree.bind("<<TreeviewSelect>>", self.on_question_select)
        
        # 更新题目列表
        self.update_question_list()
        
    def create_question_editor(self, parent):
        """创建题目编辑区域"""
        # 右侧框架
        right_frame = ttk.LabelFrame(parent, text="题目编辑", padding="5")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        
        # 题目类型
        type_frame = ttk.Frame(right_frame)
        type_frame.pack(fill="x", pady=5)
        ttk.Label(type_frame, text="题目类型:").pack(side="left")
        self.type_var = tk.StringVar(value=self.categories[0])
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, 
                                 values=self.categories, state="readonly")
        type_combo.pack(side="left", padx=(5, 0))
        
        # 难度等级
        difficulty_frame = ttk.Frame(right_frame)
        difficulty_frame.pack(fill="x", pady=5)
        ttk.Label(difficulty_frame, text="难度等级:").pack(side="left")
        self.difficulty_var = tk.StringVar(value=self.difficulty_levels[0])
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var,
                                      values=self.difficulty_levels, state="readonly")
        difficulty_combo.pack(side="left", padx=(5, 0))
        
        # 题目标题
        title_frame = ttk.Frame(right_frame)
        title_frame.pack(fill="x", pady=5)
        ttk.Label(title_frame, text="题目标题:").pack(anchor="w")
        self.title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=self.title_var)
        title_entry.pack(fill="x", pady=(5, 0))
        
        # 题目内容
        content_frame = ttk.Frame(right_frame)
        content_frame.pack(fill="both", expand=True, pady=5)
        ttk.Label(content_frame, text="题目内容:").pack(anchor="w")
        self.content_text = tk.Text(content_frame, height=10, wrap="word")
        content_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                        command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=content_scrollbar.set)
        self.content_text.pack(side="left", fill="both", expand=True, pady=(5, 0))
        content_scrollbar.pack(side="right", fill="y", pady=(5, 0))
        
        # 答案
        answer_frame = ttk.Frame(right_frame)
        answer_frame.pack(fill="both", expand=True, pady=5)
        ttk.Label(answer_frame, text="答案:").pack(anchor="w")
        self.answer_text = tk.Text(answer_frame, height=5, wrap="word")
        answer_scrollbar = ttk.Scrollbar(answer_frame, orient="vertical", 
                                       command=self.answer_text.yview)
        self.answer_text.configure(yscrollcommand=answer_scrollbar.set)
        self.answer_text.pack(side="left", fill="both", expand=True, pady=(5, 0))
        answer_scrollbar.pack(side="right", fill="y", pady=(5, 0))
        
        # 标签
        tags_frame = ttk.Frame(right_frame)
        tags_frame.pack(fill="x", pady=5)
        ttk.Label(tags_frame, text="标签:").pack(side="left")
        self.tags_var = tk.StringVar()
        tags_entry = ttk.Entry(tags_frame, textvariable=self.tags_var)
        tags_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
    def create_buttons(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 按钮
        ttk.Button(button_frame, text="新增题目", command=self.add_question).pack(side="left", padx=5)
        ttk.Button(button_frame, text="保存题目", command=self.save_question).pack(side="left", padx=5)
        ttk.Button(button_frame, text="删除题目", command=self.delete_question).pack(side="left", padx=5)
        ttk.Button(button_frame, text="清空表单", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(button_frame, text="导入题库", command=self.import_questions).pack(side="left", padx=5)
        ttk.Button(button_frame, text="导出题库", command=self.export_questions).pack(side="left", padx=5)
        ttk.Button(button_frame, text="关闭", command=self.root.destroy).pack(side="right", padx=5)
        
    def load_data(self):
        """加载题库数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.questions = json.load(f)
            else:
                self.questions = []
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {str(e)}")
            self.questions = []
            
    def save_data(self):
        """保存题库数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {str(e)}")
            
    def update_question_list(self):
        """更新题目列表"""
        # 清空列表
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
            
        # 添加题目
        for i, question in enumerate(self.questions, 1):
            self.question_tree.insert("", "end", values=(
                i,
                question.get("title", "")[:30] + "..." if len(question.get("title", "")) > 30 else question.get("title", ""),
                question.get("type", ""),
                question.get("difficulty", "")
            ))
            
    def filter_questions(self, *args):
        """过滤题目"""
        search_term = self.search_var.get().lower()
        
        # 清空列表
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
            
        # 添加过滤后的题目
        for i, question in enumerate(self.questions, 1):
            title = question.get("title", "").lower()
            content = question.get("content", "").lower()
            tags = question.get("tags", "").lower()
            
            if (search_term in title or search_term in content or 
                search_term in tags or search_term == ""):
                self.question_tree.insert("", "end", values=(
                    i,
                    question.get("title", "")[:30] + "..." if len(question.get("title", "")) > 30 else question.get("title", ""),
                    question.get("type", ""),
                    question.get("difficulty", "")
                ))
                
    def on_question_select(self, event):
        """题目选择事件"""
        selection = self.question_tree.selection()
        if selection:
            item = self.question_tree.item(selection[0])
            index = int(item['values'][0]) - 1
            if 0 <= index < len(self.questions):
                self.load_question_to_form(self.questions[index])
                
    def load_question_to_form(self, question):
        """将题目加载到表单"""
        self.title_var.set(question.get("title", ""))
        self.type_var.set(question.get("type", self.categories[0]))
        self.difficulty_var.set(question.get("difficulty", self.difficulty_levels[0]))
        
        # 清空文本区域
        self.content_text.delete(1.0, tk.END)
        self.answer_text.delete(1.0, tk.END)
        
        # 设置内容
        self.content_text.insert(1.0, question.get("content", ""))
        self.answer_text.insert(1.0, question.get("answer", ""))
        self.tags_var.set(question.get("tags", ""))
        
    def add_question(self):
        """新增题目"""
        self.clear_form()
        
    def save_question(self):
        """保存题目"""
        # 获取表单数据
        title = self.title_var.get().strip()
        question_type = self.type_var.get()
        difficulty = self.difficulty_var.get()
        content = self.content_text.get(1.0, tk.END).strip()
        answer = self.answer_text.get(1.0, tk.END).strip()
        tags = self.tags_var.get().strip()
        
        # 验证数据
        if not title:
            messagebox.showwarning("警告", "请输入题目标题")
            return
        if not content:
            messagebox.showwarning("警告", "请输入题目内容")
            return
            
        # 创建题目对象
        question = {
            "id": len(self.questions) + 1,
            "title": title,
            "type": question_type,
            "difficulty": difficulty,
            "content": content,
            "answer": answer,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 添加到题库
        self.questions.append(question)
        self.save_data()
        self.update_question_list()
        
        messagebox.showinfo("成功", "题目保存成功！")
        
    def delete_question(self):
        """删除题目"""
        selection = self.question_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的题目")
            return
            
        if messagebox.askyesno("确认", "确定要删除选中的题目吗？"):
            item = self.question_tree.item(selection[0])
            index = int(item['values'][0]) - 1
            if 0 <= index < len(self.questions):
                del self.questions[index]
                self.save_data()
                self.update_question_list()
                self.clear_form()
                messagebox.showinfo("成功", "题目删除成功！")
                
    def clear_form(self):
        """清空表单"""
        self.title_var.set("")
        self.type_var.set(self.categories[0])
        self.difficulty_var.set(self.difficulty_levels[0])
        self.content_text.delete(1.0, tk.END)
        self.answer_text.delete(1.0, tk.END)
        self.tags_var.set("")
        
    def import_questions(self):
        """导入题库"""
        filename = filedialog.askopenfilename(
            title="选择题库文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_questions = json.load(f)
                    
                if isinstance(imported_questions, list):
                    self.questions.extend(imported_questions)
                    self.save_data()
                    self.update_question_list()
                    messagebox.showinfo("成功", f"成功导入 {len(imported_questions)} 道题目")
                else:
                    messagebox.showerror("错误", "文件格式不正确")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")
                
    def export_questions(self):
        """导出题库"""
        if not self.questions:
            messagebox.showwarning("警告", "题库为空，无法导出")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存题库文件",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.questions, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", f"成功导出 {len(self.questions)} 道题目")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
                
    def run(self):
        """运行题库管理模块"""
        self.root.grab_set()  # 模态窗口
        self.root.wait_window()

if __name__ == "__main__":
    app = QuestionBankManager()
    app.run() 