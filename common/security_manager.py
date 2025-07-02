# -*- coding: utf-8 -*-
"""
安全管理工具模块

提供用户认证、权限管理、数据加密等安全功能。

更新日志：
- 2024-06-25：初始版本，提供基本安全管理功能
"""

import os
import sys
import json
import time
import base64
import hashlib
import secrets
import threading
from pathlib import Path
from datetime import datetime, timedelta

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.file_manager import ensure_dir, read_json_file, write_json_file

# 创建日志记录器
logger = get_logger("security_manager", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "security_manager.log"))

# 尝试导入可选模块
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    logger.warning("cryptography模块未安装，高级加密功能将不可用")


class PasswordManager:
    """
    密码管理器，用于密码哈希和验证
    """
    def __init__(self, salt_length=16, iterations=100000, algorithm="sha256"):
        """
        初始化密码管理器
        
        Args:
            salt_length (int, optional): 盐长度
            iterations (int, optional): 哈希迭代次数
            algorithm (str, optional): 哈希算法
        """
        self.salt_length = salt_length
        self.iterations = iterations
        self.algorithm = algorithm
    
    def generate_salt(self):
        """
        生成随机盐
        
        Returns:
            bytes: 随机盐
        """
        return secrets.token_bytes(self.salt_length)
    
    def hash_password(self, password, salt=None):
        """
        哈希密码
        
        Args:
            password (str): 密码
            salt (bytes, optional): 盐，如果为None则生成新盐
            
        Returns:
            tuple: (哈希密码, 盐)
        """
        if salt is None:
            salt = self.generate_salt()
        
        # 将密码转换为字节
        if isinstance(password, str):
            password = password.encode("utf-8")
        
        # 哈希密码
        hash_obj = hashlib.pbkdf2_hmac(
            self.algorithm,
            password,
            salt,
            self.iterations
        )
        
        return hash_obj, salt
    
    def verify_password(self, password, hash_password, salt):
        """
        验证密码
        
        Args:
            password (str): 密码
            hash_password (bytes): 哈希密码
            salt (bytes): 盐
            
        Returns:
            bool: 密码是否正确
        """
        # 哈希密码
        new_hash, _ = self.hash_password(password, salt)
        
        # 比较哈希值
        return new_hash == hash_password
    
    def encode_hash_salt(self, hash_password, salt):
        """
        编码哈希密码和盐为字符串
        
        Args:
            hash_password (bytes): 哈希密码
            salt (bytes): 盐
            
        Returns:
            str: 编码后的字符串
        """
        hash_b64 = base64.b64encode(hash_password).decode("utf-8")
        salt_b64 = base64.b64encode(salt).decode("utf-8")
        return f"{hash_b64}:{salt_b64}"
    
    def decode_hash_salt(self, encoded_str):
        """
        解码字符串为哈希密码和盐
        
        Args:
            encoded_str (str): 编码后的字符串
            
        Returns:
            tuple: (哈希密码, 盐)
        """
        hash_b64, salt_b64 = encoded_str.split(":")
        hash_password = base64.b64decode(hash_b64)
        salt = base64.b64decode(salt_b64)
        return hash_password, salt


class EncryptionManager:
    """
    加密管理器，用于数据加密和解密
    """
    def __init__(self, key=None):
        """
        初始化加密管理器
        
        Args:
            key (bytes, optional): 加密密钥，如果为None则生成新密钥
        """
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("cryptography模块未安装，无法使用加密管理器")
        
        if key is None:
            key = Fernet.generate_key()
        
        self.key = key
        self.cipher = Fernet(key)
    
    @classmethod
    def generate_key(cls):
        """
        生成加密密钥
        
        Returns:
            bytes: 加密密钥
        """
        return Fernet.generate_key()
    
    @classmethod
    def derive_key_from_password(cls, password, salt=None):
        """
        从密码派生加密密钥
        
        Args:
            password (str): 密码
            salt (bytes, optional): 盐，如果为None则生成新盐
            
        Returns:
            tuple: (加密密钥, 盐)
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        # 将密码转换为字节
        if isinstance(password, str):
            password = password.encode("utf-8")
        
        # 派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        return key, salt
    
    def encrypt(self, data):
        """
        加密数据
        
        Args:
            data (str or bytes): 待加密数据
            
        Returns:
            bytes: 加密后的数据
        """
        # 将数据转换为字节
        if isinstance(data, str):
            data = data.encode("utf-8")
        
        # 加密数据
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """
        解密数据
        
        Args:
            encrypted_data (bytes): 加密后的数据
            
        Returns:
            bytes: 解密后的数据
        """
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_to_string(self, data):
        """
        加密数据并转换为字符串
        
        Args:
            data (str or bytes): 待加密数据
            
        Returns:
            str: 加密后的字符串
        """
        encrypted_data = self.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")
    
    def decrypt_from_string(self, encrypted_str):
        """
        从字符串解密数据
        
        Args:
            encrypted_str (str): 加密后的字符串
            
        Returns:
            bytes: 解密后的数据
        """
        encrypted_data = base64.b64decode(encrypted_str)
        return self.decrypt(encrypted_data)
    
    def encrypt_file(self, input_file, output_file=None):
        """
        加密文件
        
        Args:
            input_file (str): 输入文件路径
            output_file (str, optional): 输出文件路径，如果为None则覆盖输入文件
            
        Returns:
            bool: 是否成功加密
        """
        try:
            # 如果输出文件为None，则覆盖输入文件
            if output_file is None:
                output_file = input_file + ".enc"
            
            # 确保输出目录存在
            ensure_dir(os.path.dirname(output_file))
            
            # 读取文件内容
            with open(input_file, "rb") as f:
                data = f.read()
            
            # 加密数据
            encrypted_data = self.encrypt(data)
            
            # 写入加密后的数据
            with open(output_file, "wb") as f:
                f.write(encrypted_data)
            
            logger.info(f"文件已加密: {input_file} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"加密文件失败: {input_file}, 错误: {str(e)}")
            return False
    
    def decrypt_file(self, input_file, output_file=None):
        """
        解密文件
        
        Args:
            input_file (str): 输入文件路径
            output_file (str, optional): 输出文件路径，如果为None则自动生成
            
        Returns:
            bool: 是否成功解密
        """
        try:
            # 如果输出文件为None，则自动生成
            if output_file is None:
                if input_file.endswith(".enc"):
                    output_file = input_file[:-4]
                else:
                    output_file = input_file + ".dec"
            
            # 确保输出目录存在
            ensure_dir(os.path.dirname(output_file))
            
            # 读取加密后的数据
            with open(input_file, "rb") as f:
                encrypted_data = f.read()
            
            # 解密数据
            data = self.decrypt(encrypted_data)
            
            # 写入解密后的数据
            with open(output_file, "wb") as f:
                f.write(data)
            
            logger.info(f"文件已解密: {input_file} -> {output_file}")
            return True
        except Exception as e:
            logger.error(f"解密文件失败: {input_file}, 错误: {str(e)}")
            return False


class TokenManager:
    """
    令牌管理器，用于生成和验证访问令牌
    """
    def __init__(self, secret_key=None, token_expiry=3600):
        """
        初始化令牌管理器
        
        Args:
            secret_key (str, optional): 密钥，如果为None则生成新密钥
            token_expiry (int, optional): 令牌过期时间（秒）
        """
        if secret_key is None:
            secret_key = secrets.token_hex(32)
        
        self.secret_key = secret_key
        self.token_expiry = token_expiry
        self.tokens = {}
        self.lock = threading.Lock()
    
    def generate_token(self, user_id, data=None):
        """
        生成访问令牌
        
        Args:
            user_id (str): 用户ID
            data (dict, optional): 令牌数据
            
        Returns:
            str: 访问令牌
        """
        # 生成令牌
        token = secrets.token_hex(16)
        expires_at = datetime.now() + timedelta(seconds=self.token_expiry)
        
        # 创建令牌数据
        token_data = {
            "user_id": user_id,
            "expires_at": expires_at.timestamp(),
            "data": data or {}
        }
        
        # 存储令牌
        with self.lock:
            self.tokens[token] = token_data
        
        return token
    
    def verify_token(self, token):
        """
        验证访问令牌
        
        Args:
            token (str): 访问令牌
            
        Returns:
            dict: 令牌数据，如果令牌无效则返回None
        """
        with self.lock:
            # 检查令牌是否存在
            if token not in self.tokens:
                return None
            
            # 获取令牌数据
            token_data = self.tokens[token]
            
            # 检查令牌是否过期
            if token_data["expires_at"] < datetime.now().timestamp():
                # 删除过期令牌
                del self.tokens[token]
                return None
            
            return token_data
    
    def refresh_token(self, token):
        """
        刷新访问令牌
        
        Args:
            token (str): 访问令牌
            
        Returns:
            bool: 是否成功刷新
        """
        with self.lock:
            # 检查令牌是否存在
            if token not in self.tokens:
                return False
            
            # 获取令牌数据
            token_data = self.tokens[token]
            
            # 检查令牌是否过期
            if token_data["expires_at"] < datetime.now().timestamp():
                # 删除过期令牌
                del self.tokens[token]
                return False
            
            # 更新过期时间
            token_data["expires_at"] = (datetime.now() + timedelta(seconds=self.token_expiry)).timestamp()
            
            return True
    
    def revoke_token(self, token):
        """
        撤销访问令牌
        
        Args:
            token (str): 访问令牌
            
        Returns:
            bool: 是否成功撤销
        """
        with self.lock:
            # 检查令牌是否存在
            if token not in self.tokens:
                return False
            
            # 删除令牌
            del self.tokens[token]
            
            return True
    
    def cleanup_expired_tokens(self):
        """
        清理过期令牌
        
        Returns:
            int: 清理的令牌数量
        """
        count = 0
        current_time = datetime.now().timestamp()
        
        with self.lock:
            # 查找过期令牌
            expired_tokens = []
            for token, token_data in self.tokens.items():
                if token_data["expires_at"] < current_time:
                    expired_tokens.append(token)
            
            # 删除过期令牌
            for token in expired_tokens:
                del self.tokens[token]
                count += 1
        
        return count


class UserManager:
    """
    用户管理器，用于用户管理和认证
    """
    def __init__(self, users_file=None):
        """
        初始化用户管理器
        
        Args:
            users_file (str, optional): 用户文件路径
        """
        if users_file is None:
            project_root = Path(__file__).parent.parent
            users_file = os.path.join(project_root, "data", "users.json")
        
        self.users_file = users_file
        self.users = {}
        self.password_manager = PasswordManager()
        self.token_manager = TokenManager()
        self.lock = threading.Lock()
        
        # 加载用户数据
        self.load_users()
    
    def load_users(self):
        """
        加载用户数据
        
        Returns:
            bool: 是否成功加载
        """
        try:
            # 确保用户文件目录存在
            ensure_dir(os.path.dirname(self.users_file))
            
            # 如果用户文件不存在，创建空文件
            if not os.path.exists(self.users_file):
                self.users = {}
                self.save_users()
                return True
            
            # 加载用户数据
            users_data = read_json_file(self.users_file)
            if users_data is None:
                self.users = {}
                return False
            
            self.users = users_data
            return True
        except Exception as e:
            logger.error(f"加载用户数据失败: {str(e)}")
            self.users = {}
            return False
    
    def save_users(self):
        """
        保存用户数据
        
        Returns:
            bool: 是否成功保存
        """
        try:
            # 确保用户文件目录存在
            ensure_dir(os.path.dirname(self.users_file))
            
            # 保存用户数据
            return write_json_file(self.users_file, self.users)
        except Exception as e:
            logger.error(f"保存用户数据失败: {str(e)}")
            return False
    
    def create_user(self, username, password, role="user", data=None):
        """
        创建用户
        
        Args:
            username (str): 用户名
            password (str): 密码
            role (str, optional): 角色
            data (dict, optional): 用户数据
            
        Returns:
            bool: 是否成功创建
        """
        with self.lock:
            # 检查用户是否已存在
            if username in self.users:
                logger.error(f"用户已存在: {username}")
                return False
            
            # 哈希密码
            hash_password, salt = self.password_manager.hash_password(password)
            encoded_password = self.password_manager.encode_hash_salt(hash_password, salt)
            
            # 创建用户
            self.users[username] = {
                "username": username,
                "password": encoded_password,
                "role": role,
                "created_at": datetime.now().timestamp(),
                "last_login": None,
                "data": data or {}
            }
            
            # 保存用户数据
            success = self.save_users()
            if success:
                logger.info(f"用户已创建: {username}")
            
            return success
    
    def update_user(self, username, data):
        """
        更新用户数据
        
        Args:
            username (str): 用户名
            data (dict): 用户数据
            
        Returns:
            bool: 是否成功更新
        """
        with self.lock:
            # 检查用户是否存在
            if username not in self.users:
                logger.error(f"用户不存在: {username}")
                return False
            
            # 更新用户数据
            user = self.users[username]
            if "password" in data:
                # 哈希密码
                hash_password, salt = self.password_manager.hash_password(data["password"])
                encoded_password = self.password_manager.encode_hash_salt(hash_password, salt)
                user["password"] = encoded_password
                del data["password"]
            
            # 更新其他数据
            for key, value in data.items():
                if key in ["username", "created_at"]:
                    continue
                user[key] = value
            
            # 保存用户数据
            success = self.save_users()
            if success:
                logger.info(f"用户已更新: {username}")
            
            return success
    
    def delete_user(self, username):
        """
        删除用户
        
        Args:
            username (str): 用户名
            
        Returns:
            bool: 是否成功删除
        """
        with self.lock:
            # 检查用户是否存在
            if username not in self.users:
                logger.error(f"用户不存在: {username}")
                return False
            
            # 删除用户
            del self.users[username]
            
            # 保存用户数据
            success = self.save_users()
            if success:
                logger.info(f"用户已删除: {username}")
            
            return success
    
    def get_user(self, username):
        """
        获取用户信息
        
        Args:
            username (str): 用户名
            
        Returns:
            dict: 用户信息，如果用户不存在则返回None
        """
        # 检查用户是否存在
        if username not in self.users:
            return None
        
        # 返回用户信息（不包含密码）
        user = self.users[username].copy()
        if "password" in user:
            del user["password"]
        
        return user
    
    def authenticate(self, username, password):
        """
        认证用户
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 是否认证成功
        """
        # 检查用户是否存在
        if username not in self.users:
            return False
        
        # 获取用户信息
        user = self.users[username]
        
        # 解码密码
        hash_password, salt = self.password_manager.decode_hash_salt(user["password"])
        
        # 验证密码
        if not self.password_manager.verify_password(password, hash_password, salt):
            return False
        
        # 更新最后登录时间
        with self.lock:
            user["last_login"] = datetime.now().timestamp()
            self.save_users()
        
        return True
    
    def login(self, username, password):
        """
        用户登录
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            str: 访问令牌，如果登录失败则返回None
        """
        # 认证用户
        if not self.authenticate(username, password):
            return None
        
        # 获取用户信息
        user = self.get_user(username)
        
        # 生成访问令牌
        token = self.token_manager.generate_token(username, user)
        
        return token
    
    def verify_token(self, token):
        """
        验证访问令牌
        
        Args:
            token (str): 访问令牌
            
        Returns:
            dict: 用户信息，如果令牌无效则返回None
        """
        # 验证令牌
        token_data = self.token_manager.verify_token(token)
        if token_data is None:
            return None
        
        # 获取用户信息
        username = token_data["user_id"]
        return self.get_user(username)
    
    def refresh_token(self, token):
        """
        刷新访问令牌
        
        Args:
            token (str): 访问令牌
            
        Returns:
            bool: 是否成功刷新
        """
        return self.token_manager.refresh_token(token)
    
    def logout(self, token):
        """
        用户登出
        
        Args:
            token (str): 访问令牌
            
        Returns:
            bool: 是否成功登出
        """
        return self.token_manager.revoke_token(token)


class PermissionManager:
    """
    权限管理器，用于权限管理和访问控制
    """
    def __init__(self, permissions_file=None):
        """
        初始化权限管理器
        
        Args:
            permissions_file (str, optional): 权限文件路径
        """
        if permissions_file is None:
            project_root = Path(__file__).parent.parent
            permissions_file = os.path.join(project_root, "data", "permissions.json")
        
        self.permissions_file = permissions_file
        self.permissions = {}
        self.lock = threading.Lock()
        
        # 加载权限数据
        self.load_permissions()
    
    def load_permissions(self):
        """
        加载权限数据
        
        Returns:
            bool: 是否成功加载
        """
        try:
            # 确保权限文件目录存在
            ensure_dir(os.path.dirname(self.permissions_file))
            
            # 如果权限文件不存在，创建默认权限
            if not os.path.exists(self.permissions_file):
                self.permissions = self.get_default_permissions()
                self.save_permissions()
                return True
            
            # 加载权限数据
            permissions_data = read_json_file(self.permissions_file)
            if permissions_data is None:
                self.permissions = self.get_default_permissions()
                return False
            
            self.permissions = permissions_data
            return True
        except Exception as e:
            logger.error(f"加载权限数据失败: {str(e)}")
            self.permissions = self.get_default_permissions()
            return False
    
    def save_permissions(self):
        """
        保存权限数据
        
        Returns:
            bool: 是否成功保存
        """
        try:
            # 确保权限文件目录存在
            ensure_dir(os.path.dirname(self.permissions_file))
            
            # 保存权限数据
            return write_json_file(self.permissions_file, self.permissions)
        except Exception as e:
            logger.error(f"保存权限数据失败: {str(e)}")
            return False
    
    def get_default_permissions(self):
        """
        获取默认权限
        
        Returns:
            dict: 默认权限
        """
        return {
            "roles": {
                "admin": {
                    "description": "管理员",
                    "permissions": ["*"]
                },
                "teacher": {
                    "description": "教师",
                    "permissions": [
                        "question_bank:read",
                        "question_bank:write",
                        "exam:read",
                        "exam:write",
                        "grading:read",
                        "grading:write",
                        "student:read"
                    ]
                },
                "student": {
                    "description": "学生",
                    "permissions": [
                        "exam:read",
                        "grading:read"
                    ]
                },
                "guest": {
                    "description": "访客",
                    "permissions": []
                }
            },
            "resources": {
                "question_bank": {
                    "description": "题库",
                    "actions": ["read", "write", "delete"]
                },
                "exam": {
                    "description": "考试",
                    "actions": ["read", "write", "delete"]
                },
                "grading": {
                    "description": "阅卷",
                    "actions": ["read", "write", "delete"]
                },
                "student": {
                    "description": "学生",
                    "actions": ["read", "write", "delete"]
                },
                "system": {
                    "description": "系统",
                    "actions": ["read", "write", "delete"]
                }
            }
        }
    
    def has_permission(self, role, resource, action):
        """
        检查角色是否有权限
        
        Args:
            role (str): 角色
            resource (str): 资源
            action (str): 操作
            
        Returns:
            bool: 是否有权限
        """
        # 检查角色是否存在
        if role not in self.permissions["roles"]:
            return False
        
        # 获取角色权限
        role_permissions = self.permissions["roles"][role]["permissions"]
        
        # 检查是否有通配符权限
        if "*" in role_permissions:
            return True
        
        # 检查是否有资源通配符权限
        if f"{resource}:*" in role_permissions:
            return True
        
        # 检查是否有具体权限
        return f"{resource}:{action}" in role_permissions
    
    def add_role(self, role, description, permissions):
        """
        添加角色
        
        Args:
            role (str): 角色
            description (str): 描述
            permissions (list): 权限列表
            
        Returns:
            bool: 是否成功添加
        """
        with self.lock:
            # 检查角色是否已存在
            if role in self.permissions["roles"]:
                logger.error(f"角色已存在: {role}")
                return False
            
            # 添加角色
            self.permissions["roles"][role] = {
                "description": description,
                "permissions": permissions
            }
            
            # 保存权限数据
            success = self.save_permissions()
            if success:
                logger.info(f"角色已添加: {role}")
            
            return success
    
    def update_role(self, role, data):
        """
        更新角色
        
        Args:
            role (str): 角色
            data (dict): 角色数据
            
        Returns:
            bool: 是否成功更新
        """
        with self.lock:
            # 检查角色是否存在
            if role not in self.permissions["roles"]:
                logger.error(f"角色不存在: {role}")
                return False
            
            # 更新角色数据
            role_data = self.permissions["roles"][role]
            for key, value in data.items():
                role_data[key] = value
            
            # 保存权限数据
            success = self.save_permissions()
            if success:
                logger.info(f"角色已更新: {role}")
            
            return success
    
    def delete_role(self, role):
        """
        删除角色
        
        Args:
            role (str): 角色
            
        Returns:
            bool: 是否成功删除
        """
        with self.lock:
            # 检查角色是否存在
            if role not in self.permissions["roles"]:
                logger.error(f"角色不存在: {role}")
                return False
            
            # 删除角色
            del self.permissions["roles"][role]
            
            # 保存权限数据
            success = self.save_permissions()
            if success:
                logger.info(f"角色已删除: {role}")
            
            return success
    
    def add_resource(self, resource, description, actions):
        """
        添加资源
        
        Args:
            resource (str): 资源
            description (str): 描述
            actions (list): 操作列表
            
        Returns:
            bool: 是否成功添加
        """
        with self.lock:
            # 检查资源是否已存在
            if resource in self.permissions["resources"]:
                logger.error(f"资源已存在: {resource}")
                return False
            
            # 添加资源
            self.permissions["resources"][resource] = {
                "description": description,
                "actions": actions
            }
            
            # 保存权限数据
            success = self.save_permissions()
            if success:
                logger.info(f"资源已添加: {resource}")
            
            return success
    
    def update_resource(self, resource, data):
        """
        更新资源
        
        Args:
            resource (str): 资源
            data (dict): 资源数据
            
        Returns:
            bool: 是否成功更新
        """
        with self.lock:
            # 检查资源是否存在
            if resource not in self.permissions["resources"]:
                logger.error(f"资源不存在: {resource}")
                return False
            
            # 更新资源数据
            resource_data = self.permissions["resources"][resource]
            for key, value in data.items():
                resource_data[key] = value
            
            # 保存权限数据
            success = self.save_permissions()
            if success:
                logger.info(f"资源已更新: {resource}")
            
            return success
    
    def delete_resource(self, resource):
        """
        删除资源
        
        Args:
            resource (str): 资源
            
        Returns:
            bool: 是否成功删除
        """
        with self.lock:
            # 检查资源是否存在
            if resource not in self.permissions["resources"]:
                logger.error(f"资源不存在: {resource}")
                return False
            
            # 删除资源
            del self.permissions["resources"][resource]
            
            # 保存权限数据
            success = self.save_permissions()
            if success:
                logger.info(f"资源已删除: {resource}")
            
            return success


def generate_random_password(length=12):
    """
    生成随机密码
    
    Args:
        length (int, optional): 密码长度
        
    Returns:
        str: 随机密码
    """
    # 定义字符集
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+"
    
    # 生成随机密码
    password = ""
    for _ in range(length):
        password += secrets.choice(chars)
    
    return password


def hash_data(data, algorithm="sha256"):
    """
    哈希数据
    
    Args:
        data (str or bytes): 待哈希数据
        algorithm (str, optional): 哈希算法
        
    Returns:
        str: 哈希值
    """
    # 将数据转换为字节
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    # 哈希数据
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    
    return hash_obj.hexdigest()


if __name__ == "__main__":
    # 测试密码管理器
    password_manager = PasswordManager()
    password = "test_password"
    hash_password, salt = password_manager.hash_password(password)
    encoded = password_manager.encode_hash_salt(hash_password, salt)
    print(f"密码: {password}")
    print(f"编码后的密码: {encoded}")
    
    # 验证密码
    hash_password, salt = password_manager.decode_hash_salt(encoded)
    is_valid = password_manager.verify_password(password, hash_password, salt)
    print(f"密码验证: {is_valid}")
    
    # 测试加密管理器（如果有cryptography模块）
    if HAS_CRYPTOGRAPHY:
        encryption_manager = EncryptionManager()
        data = "测试数据"
        encrypted = encryption_manager.encrypt_to_string(data)
        print(f"加密后的数据: {encrypted}")
        
        # 解密数据
        decrypted = encryption_manager.decrypt_from_string(encrypted)
        print(f"解密后的数据: {decrypted.decode('utf-8')}")
    
    # 测试令牌管理器
    token_manager = TokenManager()
    token = token_manager.generate_token("test_user")
    print(f"访问令牌: {token}")
    
    # 验证令牌
    token_data = token_manager.verify_token(token)
    print(f"令牌数据: {token_data}")
    
    # 测试用户管理器
    user_manager = UserManager()
    username = "test_user"
    password = "test_password"
    
    # 创建用户
    user_manager.create_user(username, password, "admin")
    
    # 认证用户
    is_authenticated = user_manager.authenticate(username, password)
    print(f"用户认证: {is_authenticated}")
    
    # 用户登录
    token = user_manager.login(username, password)
    print(f"登录令牌: {token}")
    
    # 验证令牌
    user = user_manager.verify_token(token)
    print(f"用户信息: {user}")
    
    # 用户登出
    is_logout = user_manager.logout(token)
    print(f"用户登出: {is_logout}")
    
    # 删除测试用户
    user_manager.delete_user(username)