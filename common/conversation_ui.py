# -*- coding: utf-8 -*-
"""
对话上下文管理UI模块

提供对话上下文的图形界面管理功能，包括查看、添加、编辑和删除对话记录。

更新日志：
- 2024-07-10：初始版本，提供基本对话上下文管理UI功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from pathlib import Path

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.conversation_manager import get_conversation_manager
from common.logger import get_logger

# 创建日志记录器
logger = get_logger("conversation_ui", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "conversation_ui.log"))


class ConversationUI:
    """
    对话上下文管理UI类
    
    提供对话上下文的图形界面管理功能。
    """
    def __init__(self, parent=None):
        """
        初始化对话上下文管理UI
        
        Args:
            parent (tk.Tk or tk.Toplevel, optional): 父窗口
        """
        # 如果没有提供父窗口，创建一个新窗口
        if parent is None:
            self.root = tk.Tk()
            self.root.title("对话上下文管理")
            self.root.geometry("800x600")
            self.is_toplevel = False
        else:
            self.root = tk.Toplevel(parent)
            self.root.title("对话上下文管理")
            self.root.geometry("800x600")
            self.is_toplevel = True
        
        # 获取对话上下文管理器
        self.manager = get_conversation_manager()
        
        # 创建UI组件
        self._create_widgets()
        
        # 加载对话记录
        self._load_conversations()
    
    def _create_widgets(self):
        """
        创建UI组件
        """
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建工具栏
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 添加按钮
        self.add_btn = ttk.Button(self.toolbar, text="添加对话", command=self._add_conversation)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_btn = ttk.Button(self.toolbar, text="编辑对话", command=self._edit_conversation)
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_btn = ttk.Button(self.toolbar, text="删除对话", command=self._delete_conversation)
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(self.toolbar, text="刷新", command=self._load_conversations)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 添加搜索框
        self.search_frame = ttk.Frame(self.toolbar)
        self.search_frame.pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(self.search_frame, text="搜索:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_btn = ttk.Button(self.search_frame, text="搜索", command=self._search_conversations)
        self.search_btn.pack(side=tk.LEFT)
        
        # 创建过滤器
        self.filter_frame = ttk.Frame(self.main_frame)
        self.filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.filter_frame, text="状态过滤:").pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value="全部")
        self.filter_combo = ttk.Combobox(self.filter_frame, textvariable=self.filter_var, 
                                        values=["全部", "未解决", "已解决", "部分解决"], 
                                        state="readonly", width=10)
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_conversations())
        
        # 创建表格
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(self.tree_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 创建表格
        self.tree = ttk.Treeview(self.tree_frame, columns=("id", "topic", "status", "created_at", "updated_at"), 
                                show="headings", yscrollcommand=self.scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 配置滚动条
        self.scrollbar.config(command=self.tree.yview)
        
        # 设置列宽和标题
        self.tree.column("id", width=0, stretch=tk.NO)  # 隐藏ID列
        self.tree.column("topic", width=300)
        self.tree.column("status", width=100)
        self.tree.column("created_at", width=150)
        self.tree.column("updated_at", width=150)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("topic", text="主题")
        self.tree.heading("status", text="状态")
        self.tree.heading("created_at", text="创建时间")
        self.tree.heading("updated_at", text="更新时间")
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", lambda e: self._view_conversation())
        
        # 创建详情框架
        self.detail_frame = ttk.LabelFrame(self.main_frame, text="对话详情", padding="10")
        self.detail_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 创建详情文本框
        self.detail_text = tk.Text(self.detail_frame, wrap=tk.WORD, height=10)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        self.detail_text.config(state=tk.DISABLED)
    
    def _load_conversations(self):
        """
        加载对话记录
        """
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取所有对话记录
        conversations = self.manager.get_all_conversations()
        
        # 应用过滤器
        filter_value = self.filter_var.get()
        if filter_value != "全部":
            conversations = [c for c in conversations if c["status"] == filter_value]
        
        # 添加到表格
        for conversation in conversations:
            self.tree.insert("", tk.END, values=(
                conversation["id"],
                conversation["topic"],
                conversation["status"],
                conversation["created_at"],
                conversation["updated_at"]
            ))
    
    def _filter_conversations(self):
        """
        过滤对话记录
        """
        self._load_conversations()
    
    def _search_conversations(self):
        """
        搜索对话记录
        """
        keyword = self.search_var.get().strip()
        if not keyword:
            self._load_conversations()
            return
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 搜索对话记录
        conversations = self.manager.search_conversations(keyword)
        
        # 应用过滤器
        filter_value = self.filter_var.get()
        if filter_value != "全部":
            conversations = [c for c in conversations if c["status"] == filter_value]
        
        # 添加到表格
        for conversation in conversations:
            self.tree.insert("", tk.END, values=(
                conversation["id"],
                conversation["topic"],
                conversation["status"],
                conversation["created_at"],
                conversation["updated_at"]
            ))
    
    def _view_conversation(self):
        """
        查看对话详情
        """
        # 获取选中的项
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个对话记录")
            return
        
        # 获取对话ID
        conversation_id = self.tree.item(selected[0], "values")[0]
        
        # 获取对话记录
        conversation = self.manager.get_conversation(conversation_id)
        if not conversation:
            messagebox.showerror("错误", "未找到对话记录")
            return
        
        # 显示对话详情
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        self.detail_text.insert(tk.END, f"主题: {conversation['topic']}\n")
        self.detail_text.insert(tk.END, f"状态: {conversation['status']}\n")
        self.detail_text.insert(tk.END, f"创建时间: {conversation['created_at']}\n")
        self.detail_text.insert(tk.END, f"更新时间: {conversation['updated_at']}\n\n")
        
        self.detail_text.insert(tk.END, f"问题描述:\n{conversation['question']}\n\n")
        
        if conversation["solution"]:
            self.detail_text.insert(tk.END, f"解决方案:\n{conversation['solution']}\n\n")
        
        if conversation["attempts"]:
            self.detail_text.insert(tk.END, "尝试过的方案:\n")
            for i, attempt in enumerate(conversation["attempts"], 1):
                if isinstance(attempt, dict):
                    self.detail_text.insert(tk.END, f"{i}. {attempt['description']}")
                    if attempt.get("timestamp"):
                        self.detail_text.insert(tk.END, f" ({attempt['timestamp']})")
                    self.detail_text.insert(tk.END, "\n")
                else:
                    self.detail_text.insert(tk.END, f"{i}. {attempt}\n")
        
        self.detail_text.config(state=tk.DISABLED)
    
    def _add_conversation(self):
        """
        添加对话记录
        """
        # 创建对话框
        dialog = ConversationDialog(self.root, title="添加对话记录")
        
        # 如果用户取消，直接返回
        if not dialog.result:
            return
        
        # 添加对话记录
        conversation_id = self.manager.add_conversation(
            dialog.result["topic"],
            dialog.result["question"],
            dialog.result["solution"],
            dialog.result["attempts"],
            dialog.result["status"]
        )
        
        # 刷新对话记录
        self._load_conversations()
        
        # 显示成功消息
        messagebox.showinfo("成功", "对话记录已添加")
    
    def _edit_conversation(self):
        """
        编辑对话记录
        """
        # 获取选中的项
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个对话记录")
            return
        
        # 获取对话ID
        conversation_id = self.tree.item(selected[0], "values")[0]
        
        # 获取对话记录
        conversation = self.manager.get_conversation(conversation_id)
        if not conversation:
            messagebox.showerror("错误", "未找到对话记录")
            return
        
        # 创建对话框
        dialog = ConversationDialog(self.root, title="编辑对话记录", conversation=conversation)
        
        # 如果用户取消，直接返回
        if not dialog.result:
            return
        
        # 更新对话记录
        self.manager.update_conversation(
            conversation_id,
            topic=dialog.result["topic"],
            question=dialog.result["question"],
            solution=dialog.result["solution"],
            attempts=dialog.result["attempts"],
            status=dialog.result["status"]
        )
        
        # 刷新对话记录
        self._load_conversations()
        
        # 显示成功消息
        messagebox.showinfo("成功", "对话记录已更新")
    
    def _delete_conversation(self):
        """
        删除对话记录
        """
        # 获取选中的项
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个对话记录")
            return
        
        # 获取对话ID
        conversation_id = self.tree.item(selected[0], "values")[0]
        
        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除选中的对话记录吗？"):
            return
        
        # 删除对话记录
        if self.manager.delete_conversation(conversation_id):
            # 刷新对话记录
            self._load_conversations()
            
            # 显示成功消息
            messagebox.showinfo("成功", "对话记录已删除")
        else:
            messagebox.showerror("错误", "删除对话记录失败")
    
    def run(self):
        """
        运行对话上下文管理UI
        """
        if not self.is_toplevel:
            self.root.mainloop()


class ConversationDialog:
    """
    对话记录编辑对话框
    """
    def __init__(self, parent, title="对话记录", conversation=None):
        """
        初始化对话记录编辑对话框
        
        Args:
            parent: 父窗口
            title (str, optional): 对话框标题
            conversation (dict, optional): 对话记录，如果为None则为新建模式
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.conversation = conversation
        self.result = None
        
        self._create_widgets()
        
        # 如果是编辑模式，填充数据
        if conversation:
            self._fill_data(conversation)
        
        # 等待对话框关闭
        parent.wait_window(self.dialog)
    
    def _create_widgets(self):
        """
        创建UI组件
        """
        # 创建主框架
        self.main_frame = ttk.Frame(self.dialog, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表单
        # 主题
        ttk.Label(self.main_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.topic_var = tk.StringVar()
        self.topic_entry = ttk.Entry(self.main_frame, textvariable=self.topic_var, width=50)
        self.topic_entry.grid(row=0, column=1, sticky=tk.W+tk.E, pady=5)
        
        # 状态
        ttk.Label(self.main_frame, text="状态:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.status_var = tk.StringVar(value="未解决")
        self.status_combo = ttk.Combobox(self.main_frame, textvariable=self.status_var, 
                                        values=["未解决", "已解决", "部分解决"], 
                                        state="readonly", width=10)
        self.status_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 问题描述
        ttk.Label(self.main_frame, text="问题描述:").grid(row=2, column=0, sticky=tk.W+tk.N, pady=5)
        self.question_text = tk.Text(self.main_frame, wrap=tk.WORD, height=5, width=50)
        self.question_text.grid(row=2, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        
        # 解决方案
        ttk.Label(self.main_frame, text="解决方案:").grid(row=3, column=0, sticky=tk.W+tk.N, pady=5)
        self.solution_text = tk.Text(self.main_frame, wrap=tk.WORD, height=5, width=50)
        self.solution_text.grid(row=3, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        
        # 尝试过的方案
        ttk.Label(self.main_frame, text="尝试过的方案:").grid(row=4, column=0, sticky=tk.W+tk.N, pady=5)
        
        # 尝试过的方案框架
        self.attempts_frame = ttk.Frame(self.main_frame)
        self.attempts_frame.grid(row=4, column=1, sticky=tk.W+tk.E+tk.N+tk.S, pady=5)
        
        # 尝试过的方案列表
        self.attempts_listbox = tk.Listbox(self.attempts_frame, height=5, width=50)
        self.attempts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 尝试过的方案滚动条
        self.attempts_scrollbar = ttk.Scrollbar(self.attempts_frame, command=self.attempts_listbox.yview)
        self.attempts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.attempts_listbox.config(yscrollcommand=self.attempts_scrollbar.set)
        
        # 尝试过的方案按钮框架
        self.attempts_btn_frame = ttk.Frame(self.main_frame)
        self.attempts_btn_frame.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # 添加尝试过的方案按钮
        self.add_attempt_btn = ttk.Button(self.attempts_btn_frame, text="添加", command=self._add_attempt)
        self.add_attempt_btn.pack(side=tk.LEFT, padx=5)
        
        # 删除尝试过的方案按钮
        self.delete_attempt_btn = ttk.Button(self.attempts_btn_frame, text="删除", command=self._delete_attempt)
        self.delete_attempt_btn.pack(side=tk.LEFT, padx=5)
        
        # 按钮框架
        self.btn_frame = ttk.Frame(self.dialog)
        self.btn_frame.pack(fill=tk.X, pady=10)
        
        # 确定按钮
        self.ok_btn = ttk.Button(self.btn_frame, text="确定", command=self._on_ok)
        self.ok_btn.pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        self.cancel_btn = ttk.Button(self.btn_frame, text="取消", command=self._on_cancel)
        self.cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # 设置列权重
        self.main_frame.columnconfigure(1, weight=1)
        
        # 设置行权重
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.rowconfigure(3, weight=1)
        self.main_frame.rowconfigure(4, weight=1)
    
    def _fill_data(self, conversation):
        """
        填充数据
        
        Args:
            conversation (dict): 对话记录
        """
        self.topic_var.set(conversation["topic"])
        self.status_var.set(conversation["status"])
        
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(tk.END, conversation["question"])
        
        if conversation["solution"]:
            self.solution_text.delete(1.0, tk.END)
            self.solution_text.insert(tk.END, conversation["solution"])
        
        if conversation["attempts"]:
            for attempt in conversation["attempts"]:
                if isinstance(attempt, dict):
                    self.attempts_listbox.insert(tk.END, attempt["description"])
                else:
                    self.attempts_listbox.insert(tk.END, attempt)
    
    def _add_attempt(self):
        """
        添加尝试过的方案
        """
        attempt = simpledialog.askstring("添加尝试过的方案", "请输入尝试过的方案:")
        if attempt:
            self.attempts_listbox.insert(tk.END, attempt)
    
    def _delete_attempt(self):
        """
        删除尝试过的方案
        """
        selected = self.attempts_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个尝试过的方案")
            return
        
        self.attempts_listbox.delete(selected[0])
    
    def _on_ok(self):
        """
        确定按钮事件处理
        """
        # 获取表单数据
        topic = self.topic_var.get().strip()
        status = self.status_var.get()
        question = self.question_text.get(1.0, tk.END).strip()
        solution = self.solution_text.get(1.0, tk.END).strip()
        
        # 获取尝试过的方案
        attempts = []
        for i in range(self.attempts_listbox.size()):
            attempts.append({"description": self.attempts_listbox.get(i), "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        
        # 验证数据
        if not topic:
            messagebox.showerror("错误", "主题不能为空")
            return
        
        if not question:
            messagebox.showerror("错误", "问题描述不能为空")
            return
        
        # 设置结果
        self.result = {
            "topic": topic,
            "status": status,
            "question": question,
            "solution": solution if solution else None,
            "attempts": attempts
        }
        
        # 关闭对话框
        self.dialog.destroy()
    
    def _on_cancel(self):
        """
        取消按钮事件处理
        """
        self.dialog.destroy()


def show_conversation_ui(parent=None):
    """
    显示对话上下文管理UI
    
    Args:
        parent (tk.Tk or tk.Toplevel, optional): 父窗口
    """
    ui = ConversationUI(parent)
    if parent:
        return ui
    else:
        ui.run()


# 主函数
def main():
    """主函数，用于直接运行对话上下文管理UI"""
    try:
        logger.info("启动对话上下文管理UI")
        show_conversation_ui()
        logger.info("对话上下文管理UI已关闭")
    except Exception as e:
        logger.error(f"运行对话上下文管理UI时出错: {e}")
        messagebox.showerror("错误", f"运行对话上下文管理UI时出错: {e}")

# 当作为脚本直接运行时执行主函数
if __name__ == "__main__":
    main()