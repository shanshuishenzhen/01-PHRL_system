import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import csv
from datetime import datetime

class BatchImportDialog:
    """批量导入对话框"""
    def __init__(self, parent, user_manager):
        self.parent = parent
        self.user_manager = user_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("批量导入用户")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 说明文字
        info_text = """
批量导入说明：
1. 支持CSV格式文件导入
2. 文件应包含以下列：用户名,密码,真实姓名,邮箱,电话,部门,角色,状态
3. 角色可选值：super_admin, admin, examiner, student
4. 状态可选值：active, inactive, pending
5. 第一行应为列标题
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="选择文件", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=50).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_file).pack(side=tk.LEFT)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="数据预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建预览表格
        columns = ("用户名", "真实姓名", "邮箱", "电话", "部门", "角色", "状态")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="预览", command=self.preview_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="导入", command=self.import_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=(10, 0))
    
    def browse_file(self):
        """浏览文件"""
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def preview_data(self):
        """预览数据"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择文件")
            return
        
        try:
            # 清空预览表格
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # 读取CSV文件
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= 10:  # 只显示前10行
                        break
                    self.preview_tree.insert("", tk.END, values=(
                        row.get('用户名', ''),
                        row.get('真实姓名', ''),
                        row.get('邮箱', ''),
                        row.get('电话', ''),
                        row.get('部门', ''),
                        row.get('角色', ''),
                        row.get('状态', '')
                    ))
            
            self.status_label.config(text=f"预览完成，显示前10行数据")
            
        except Exception as e:
            messagebox.showerror("错误", f"预览文件失败: {e}")
    
    def import_data(self):
        """导入数据"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择文件")
            return
        
        try:
            imported_count = 0
            skipped_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 验证必填字段
                    username = row.get('用户名', '').strip()
                    if not username:
                        skipped_count += 1
                        continue
                    
                    # 检查用户名是否已存在
                    existing_user = None
                    for user in self.user_manager.users.get("users", []):
                        if user.get("username") == username:
                            existing_user = user
                            break
                    
                    if existing_user:
                        skipped_count += 1
                        continue
                    
                    # 创建新用户
                    new_user = {
                        "id": self.get_next_user_id(),
                        "username": username,
                        "password": row.get('密码', '123456'),
                        "real_name": row.get('真实姓名', ''),
                        "email": row.get('邮箱', ''),
                        "phone": row.get('电话', ''),
                        "department": row.get('部门', ''),
                        "role": row.get('角色', 'student'),
                        "status": row.get('状态', 'active'),
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.user_manager.users["users"].append(new_user)
                    imported_count += 1
            
            # 保存数据
            self.user_manager.save_users()
            self.user_manager.refresh_user_list()
            
            messagebox.showinfo("导入完成", 
                              f"成功导入 {imported_count} 个用户\n"
                              f"跳过 {skipped_count} 个用户（用户名重复或数据无效）")
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"导入数据失败: {e}")
    
    def get_next_user_id(self):
        """获取下一个用户ID"""
        max_id = 0
        for user in self.user_manager.users.get("users", []):
            max_id = max(max_id, user.get("id", 0))
        return max_id + 1


class BatchApproveDialog:
    """批量审批对话框"""
    def __init__(self, parent, user_manager):
        self.parent = parent
        self.user_manager = user_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("批量审批")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        self.load_pending_users()
    
    def setup_ui(self):
        """设置界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="待审批用户列表", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 用户列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建表格
        columns = ("选择", "ID", "用户名", "真实姓名", "邮箱", "电话", "部门", "申请时间")
        self.approve_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.approve_tree.heading(col, text=col)
            self.approve_tree.column(col, width=100)
        
        # 隐藏选择列（使用复选框）
        self.approve_tree.column("选择", width=50)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.approve_tree.yview)
        self.approve_tree.configure(yscrollcommand=scrollbar.set)
        
        self.approve_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定点击事件
        self.approve_tree.bind("<Button-1>", self.on_click)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="批量通过", command=self.batch_approve).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="批量拒绝", command=self.batch_reject).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="")
        self.status_label.pack(pady=(10, 0))
    
    def load_pending_users(self):
        """加载待审批用户"""
        # 清空表格
        for item in self.approve_tree.get_children():
            self.approve_tree.delete(item)
        
        # 获取待审批用户
        pending_users = []
        for user in self.user_manager.users.get("users", []):
            if user.get("status") == "pending":
                pending_users.append(user)
        
        # 插入数据
        for user in pending_users:
            item = self.approve_tree.insert("", tk.END, values=(
                "□",  # 复选框占位符
                user.get("id"),
                user.get("username"),
                user.get("real_name", ""),
                user.get("email", ""),
                user.get("phone", ""),
                user.get("department", ""),
                user.get("created_at", "")
            ))
            # 存储用户ID到item
            self.approve_tree.set(item, "选择", "□")
    
    def on_click(self, event):
        """处理点击事件"""
        region = self.approve_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.approve_tree.identify_column(event.x)
            if column == "#1":  # 第一列（选择列）
                item = self.approve_tree.identify_row(event.y)
                if item:
                    current_value = self.approve_tree.set(item, "选择")
                    new_value = "☑" if current_value == "□" else "□"
                    self.approve_tree.set(item, "选择", new_value)
    
    def select_all(self):
        """全选"""
        for item in self.approve_tree.get_children():
            self.approve_tree.set(item, "选择", "☑")
    
    def deselect_all(self):
        """取消全选"""
        for item in self.approve_tree.get_children():
            self.approve_tree.set(item, "选择", "□")
    
    def get_selected_users(self):
        """获取选中的用户"""
        selected_users = []
        for item in self.approve_tree.get_children():
            if self.approve_tree.set(item, "选择") == "☑":
                user_id = self.approve_tree.set(item, "ID")
                selected_users.append(int(user_id))
        return selected_users
    
    def batch_approve(self):
        """批量通过"""
        selected_ids = self.get_selected_users()
        if not selected_ids:
            messagebox.showwarning("警告", "请先选择要审批的用户")
            return
        
        if messagebox.askyesno("确认", f"确定要通过 {len(selected_ids)} 个用户的申请吗？"):
            approved_count = 0
            for user_id in selected_ids:
                for user in self.user_manager.users["users"]:
                    if user["id"] == user_id:
                        user["status"] = "active"
                        user["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        approved_count += 1
                        break
            
            self.user_manager.save_users()
            self.user_manager.refresh_user_list()
            self.load_pending_users()
            
            messagebox.showinfo("成功", f"成功通过 {approved_count} 个用户的申请")
    
    def batch_reject(self):
        """批量拒绝"""
        selected_ids = self.get_selected_users()
        if not selected_ids:
            messagebox.showwarning("警告", "请先选择要拒绝的用户")
            return
        
        if messagebox.askyesno("确认", f"确定要拒绝 {len(selected_ids)} 个用户的申请吗？"):
            rejected_count = 0
            for user_id in selected_ids:
                for user in self.user_manager.users["users"]:
                    if user["id"] == user_id:
                        user["status"] = "inactive"
                        user["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        rejected_count += 1
                        break
            
            self.user_manager.save_users()
            self.user_manager.refresh_user_list()
            self.load_pending_users()
            
            messagebox.showinfo("成功", f"成功拒绝 {rejected_count} 个用户的申请")


# 示例CSV文件生成函数
def create_sample_csv():
    """创建示例CSV文件"""
    sample_data = [
        ['用户名', '密码', '真实姓名', '邮箱', '电话', '部门', '角色', '状态'],
        ['student001', '123456', '张三', 'zhangsan@example.com', '13800138001', '计算机系', 'student', 'pending'],
        ['student002', '123456', '李四', 'lisi@example.com', '13800138002', '数学系', 'student', 'pending'],
        ['examiner001', '123456', '王老师', 'wang@example.com', '13800138003', '教务处', 'examiner', 'active'],
        ['admin001', '123456', '管理员', 'admin@example.com', '13800138004', '信息技术部', 'admin', 'active']
    ]
    
    try:
        with open('user_management/sample_users.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(sample_data)
        print("示例CSV文件已创建: user_management/sample_users.csv")
    except Exception as e:
        print(f"创建示例文件失败: {e}")


if __name__ == "__main__":
    # 创建示例CSV文件
    create_sample_csv() 