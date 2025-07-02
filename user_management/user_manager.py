import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import sqlite3

# 动态导入批量操作模块
def get_batch_dialogs():
    """动态获取批量操作对话框类"""
    try:
        from batch_operations import BatchImportDialog, BatchApproveDialog
        return BatchImportDialog, BatchApproveDialog
    except ImportError:
        # 创建占位符类
        class BatchImportDialog:
            def __init__(self, parent, user_manager):
                messagebox.showinfo("提示", "批量导入功能需要安装额外依赖")
        
        class BatchApproveDialog:
            def __init__(self, parent, user_manager):
                messagebox.showinfo("提示", "批量审批功能需要安装额外依赖")
        
        return BatchImportDialog, BatchApproveDialog

class UserManager:
    """用户管理主类"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("用户管理 - PH&RL 在线考试系统")
        self.root.geometry("1000x700")
        
        # 用户数据存储
        self.users = self.load_users()
        self.current_user = None  # 当前登录的管理员
        self.current_page = 1
        self.page_size = 20
        
        # 用户角色定义
        self.roles = {
            'super_admin': '超级用户',
            'admin': '管理员', 
            'examiner': '考评员',
            'student': '考生'
        }
        
        # 用户状态定义
        self.statuses = {
            'active': '正常',
            'inactive': '禁用',
            'pending': '待审批'
        }
        
        self.setup_ui()
        self.refresh_user_list()
    
    def load_users(self):
        """加载用户数据"""
        try:
            if os.path.exists('user_management/users.json'):
                with open('user_management/users.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载用户数据失败: {e}")
        
        # 返回默认用户数据
        return {
            "users": [
                {
                    "id": 1,
                    "username": "admin",
                    "password": "123456",
                    "role": "super_admin",
                    "status": "active",
                    "real_name": "系统管理员",
                    "email": "admin@example.com",
                    "phone": "13800138000",
                    "department": "信息技术部",
                    "created_at": "2024-01-01 00:00:00",
                    "updated_at": "2024-01-01 00:00:00"
                }
            ]
        }
    
    def save_users(self):
        """保存用户数据"""
        try:
            os.makedirs('user_management', exist_ok=True)
            with open('user_management/users.json', 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存用户数据失败: {e}")
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        self.create_toolbar(main_frame)
        
        # 搜索和筛选区域
        self.create_search_frame(main_frame)
        
        # 用户列表区域
        self.create_user_list_frame(main_frame)
        
        # 分页控件
        self.create_pagination_frame(main_frame)
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        title_label = ttk.Label(toolbar, text="用户管理", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(toolbar)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="新增用户", command=self.add_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编辑用户", command=self.edit_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除用户", command=self.delete_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="批量导入", command=self.batch_import).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="批量审批", command=self.batch_approve).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="刷新", command=self.refresh_user_list).pack(side=tk.LEFT, padx=5)
    
    def create_search_frame(self, parent):
        """创建搜索和筛选区域"""
        search_frame = ttk.LabelFrame(parent, text="搜索和筛选", padding="5")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索框
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 角色筛选
        ttk.Label(search_frame, text="角色:").pack(side=tk.LEFT, padx=(0, 5))
        self.role_filter_var = tk.StringVar(value="all")
        role_combo = ttk.Combobox(search_frame, textvariable=self.role_filter_var, 
                                 values=["all"] + list(self.roles.keys()), width=10)
        role_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 状态筛选
        ttk.Label(search_frame, text="状态:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_filter_var,
                                   values=["all"] + list(self.statuses.keys()), width=10)
        status_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # 搜索按钮
        ttk.Button(search_frame, text="搜索", command=self.search_users).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="重置", command=self.reset_search).pack(side=tk.LEFT, padx=5)
    
    def create_user_list_frame(self, parent):
        """创建用户列表区域"""
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ("ID", "用户名", "真实姓名", "角色", "状态", "邮箱", "电话", "部门", "创建时间")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", self.edit_user)
    
    def create_pagination_frame(self, parent):
        """创建分页控件"""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 分页信息
        self.page_info_label = ttk.Label(pagination_frame, text="")
        self.page_info_label.pack(side=tk.LEFT)
        
        # 分页按钮
        button_frame = ttk.Frame(pagination_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="上一页", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="下一页", command=self.next_page).pack(side=tk.LEFT, padx=2)
    
    def refresh_user_list(self):
        """刷新用户列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取筛选后的用户列表
        filtered_users = self.get_filtered_users()
        
        # 计算分页
        total_users = len(filtered_users)
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_users = filtered_users[start_idx:end_idx]
        
        # 插入数据
        for user in page_users:
            self.tree.insert("", tk.END, values=(
                user.get("id"),
                user.get("username"),
                user.get("real_name", ""),
                self.roles.get(user.get("role"), user.get("role")),
                self.statuses.get(user.get("status"), user.get("status")),
                user.get("email", ""),
                user.get("phone", ""),
                user.get("department", ""),
                user.get("created_at", "")
            ))
        
        # 更新分页信息
        total_pages = (total_users + self.page_size - 1) // self.page_size
        self.page_info_label.config(text=f"第 {self.current_page} 页，共 {total_pages} 页，总计 {total_users} 条记录")
    
    def get_filtered_users(self):
        """从数据库获取筛选后的用户列表"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # 这允许我们通过列名访问数据
        cursor = conn.cursor()

        query = "SELECT * FROM users WHERE 1=1"
        params = []

        search_text = self.search_var.get()
        if search_text:
            query += " AND (username LIKE ? OR real_name LIKE ? OR email LIKE ? OR phone LIKE ?)"
            search_param = f"%{search_text}%"
            params.extend([search_param, search_param, search_param, search_param])

        # 从显示名称反向查找角色和状态的键
        role_filter_display = self.role_filter_var.get()
        if role_filter_display != "全部":
            # 找到角色显示名称对应的键 (e.g., "管理员" -> "admin")
            role_key = [k for k, v in self.roles.items() if v == role_filter_display]
            if role_key:
                query += " AND role = ?"
                params.append(role_key[0])

        status_filter_display = self.status_filter_var.get()
        if status_filter_display != "全部":
            # 找到状态显示名称对应的键 (e.g., "正常" -> "active")
            status_key = [k for k, v in self.statuses.items() if v == status_filter_display]
            if status_key:
                query += " AND status = ?"
                params.append(status_key[0])
        
        query += " ORDER BY id DESC"

        try:
            cursor.execute(query, params)
            users_rows = cursor.fetchall()
            # 将数据库行转换为字典，以保持与代码其余部分的兼容性
            users = [dict(row) for row in users_rows]
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"查询用户失败: {e}")
            users = []
        finally:
            conn.close()

        return users
    
    def search_users(self):
        """搜索用户"""
        self.current_page = 1
        self.refresh_user_list()
    
    def reset_search(self):
        """重置搜索条件"""
        self.search_var.set("")
        self.role_filter_var.set("all")
        self.status_filter_var.set("all")
        self.current_page = 1
        self.refresh_user_list()
    
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_user_list()
    
    def next_page(self):
        """下一页"""
        filtered_users = self.get_filtered_users()
        total_pages = (len(filtered_users) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_user_list()
    
    def add_user(self):
        """新增用户"""
        UserDialog(self.root, self, None)
    
    def edit_user(self, event=None):
        """编辑用户"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的用户")
            return
        
        # 获取选中的用户ID
        user_id = self.tree.item(selection[0])['values'][0]
        user = self.get_user_by_id(user_id)
        if user:
            UserDialog(self.root, self, user)
    
    def get_user_by_id(self, user_id):
        """根据ID从数据库获取用户"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            return dict(user_row) if user_row else None
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"获取用户信息失败: {e}")
            return None
        finally:
            conn.close()
    
    def delete_user(self):
        """删除用户"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的用户")
            return
        
        # 获取选中的用户ID
        user_id = self.tree.item(selection[0])['values'][0]
        user = self.get_user_by_id(user_id)
        
        if not user:
            messagebox.showerror("错误", "用户不存在")
            return
        
        # 防止删除超级用户
        if user.get("role") == "super_admin":
            messagebox.showerror("错误", "不能删除超级用户")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除用户 '{user.get('username')}' 吗？\n此操作不可恢复！"):
            # 从用户列表中删除
            self.users["users"] = [u for u in self.users["users"] if u.get("id") != user_id]
            
            # 保存数据
            self.save_users()
            self.refresh_user_list()
            
            messagebox.showinfo("成功", "用户删除成功")
    
    def batch_import(self):
        """批量导入用户"""
        try:
            BatchImportDialog, BatchApproveDialog = get_batch_dialogs()
            BatchImportDialog(self.root, self)
        except Exception as e:
            messagebox.showerror("错误", f"启动批量导入失败: {e}")
    
    def batch_approve(self):
        """批量审批"""
        try:
            BatchImportDialog, BatchApproveDialog = get_batch_dialogs()
            BatchApproveDialog(self.root, self)
        except Exception as e:
            messagebox.showerror("错误", f"启动批量审批失败: {e}")
    
    def run(self):
        """运行用户管理界面"""
        self.root.mainloop()


class UserDialog:
    """用户编辑对话框"""
    def __init__(self, parent, user_manager, user_data=None):
        self.parent = parent
        self.user_manager = user_manager
        self.user_data = user_data
        self.is_edit = user_data is not None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑用户" if self.is_edit else "新增用户")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        if self.is_edit:
            self.load_user_data()
    
    def setup_ui(self):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        fields = [
            ("用户名:", "username"),
            ("密码:", "password"),
            ("真实姓名:", "real_name"),
            ("邮箱:", "email"),
            ("电话:", "phone"),
            ("部门:", "department")
        ]
        
        self.field_vars = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            self.field_vars[field] = var
            entry = ttk.Entry(main_frame, textvariable=var, width=30)
            entry.grid(row=i, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 角色选择
        ttk.Label(main_frame, text="角色:").grid(row=len(fields), column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(value="student")
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var, 
                                 values=list(self.user_manager.roles.keys()), width=27)
        role_combo.grid(row=len(fields), column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 状态选择
        ttk.Label(main_frame, text="状态:").grid(row=len(fields)+1, column=0, sticky="w", pady=5)
        self.status_var = tk.StringVar(value="active")
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var,
                                   values=list(self.user_manager.statuses.keys()), width=27)
        status_combo.grid(row=len(fields)+1, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="保存", command=self.save_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # 如果是编辑模式，密码字段设为只读
        if self.is_edit:
            self.field_vars["password"].set("******")
            for widget in main_frame.winfo_children():
                if isinstance(widget, ttk.Entry) and widget.grid_info()["row"] == 1:
                    widget.config(state="readonly")
    
    def load_user_data(self):
        """加载用户数据到表单"""
        if not self.user_data:
            return
        
        username = self.user_data.get("username", "")
        real_name = self.user_data.get("real_name", "")
        email = self.user_data.get("email", "")
        phone = self.user_data.get("phone", "")
        department = self.user_data.get("department", "")
        role = self.user_data.get("role", "student")
        status = self.user_data.get("status", "active")
        
        self.field_vars["username"].set(username)
        self.field_vars["real_name"].set(real_name)
        self.field_vars["email"].set(email)
        self.field_vars["phone"].set(phone)
        self.field_vars["department"].set(department)
        self.role_var.set(role)
        self.status_var.set(status)
    
    def save_user(self):
        """保存用户数据"""
        # 验证必填字段
        username = self.field_vars["username"].get().strip()
        if not username:
            messagebox.showerror("错误", "用户名不能为空")
            return
        
        # 检查用户名是否重复（新增时）
        if not self.is_edit:
            for user in self.user_manager.users.get("users", []):
                if user.get("username") == username:
                    messagebox.showerror("错误", "用户名已存在")
                    return
        
        # 准备用户数据
        user_data = {
            "username": username,
            "real_name": self.field_vars["real_name"].get().strip(),
            "email": self.field_vars["email"].get().strip(),
            "phone": self.field_vars["phone"].get().strip(),
            "department": self.field_vars["department"].get().strip(),
            "role": self.role_var.get(),
            "status": self.status_var.get(),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.is_edit:
            # 编辑模式
            user_data["id"] = self.user_data["id"]
            user_data["password"] = self.user_data["password"]
            user_data["created_at"] = self.user_data["created_at"]
            
            # 更新用户数据
            for i, user in enumerate(self.user_manager.users["users"]):
                if user["id"] == self.user_data["id"]:
                    self.user_manager.users["users"][i] = user_data
                    break
        else:
            # 新增模式
            user_data["id"] = self.get_next_user_id()
            user_data["password"] = self.field_vars["password"].get()
            user_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            self.user_manager.users["users"].append(user_data)
        
        # 保存数据
        self.user_manager.save_users()
        self.user_manager.refresh_user_list()
        
        messagebox.showinfo("成功", "用户保存成功")
        self.dialog.destroy()
    
    def get_next_user_id(self):
        """获取下一个用户ID"""
        max_id = 0
        for user in self.user_manager.users.get("users", []):
            max_id = max(max_id, user.get("id", 0))
        return max_id + 1


if __name__ == "__main__":
    app = UserManager()
    app.run() 