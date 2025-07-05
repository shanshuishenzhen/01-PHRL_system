#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密工具

提供数据加密和解密功能，保护考试数据安全。
"""

import base64
import hashlib
import json
import secrets
import time
from typing import Any, Optional, Union
from utils.logger import get_logger

logger = get_logger(__name__)

class EncryptionUtils:
    """加密工具类"""
    
    @staticmethod
    def generate_key(length: int = 32) -> str:
        """生成随机密钥"""
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple:
        """哈希密码"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 使用PBKDF2进行密码哈希
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )
        
        return base64.b64encode(password_hash).decode('utf-8'), salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """验证密码"""
        try:
            new_hash, _ = EncryptionUtils.hash_password(password, salt)
            return new_hash == hashed_password
        except Exception:
            return False
    
    @staticmethod
    def simple_encrypt(data: str, key: str) -> str:
        """简单加密（用于本地数据保护）"""
        try:
            # 使用XOR加密（简单但有效的本地保护）
            key_bytes = key.encode('utf-8')
            data_bytes = data.encode('utf-8')
            
            encrypted = bytearray()
            for i, byte in enumerate(data_bytes):
                encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return base64.b64encode(encrypted).decode('utf-8')
            
        except Exception as e:
            logger.error(f"简单加密失败: {e}")
            return data  # 加密失败时返回原数据
    
    @staticmethod
    def simple_decrypt(encrypted_data: str, key: str) -> str:
        """简单解密"""
        try:
            # 解码base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            key_bytes = key.encode('utf-8')
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            logger.error(f"简单解密失败: {e}")
            return encrypted_data  # 解密失败时返回原数据
    
    @staticmethod
    def encrypt_json(data: Any, key: str) -> str:
        """加密JSON数据"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            return EncryptionUtils.simple_encrypt(json_str, key)
        except Exception as e:
            logger.error(f"JSON加密失败: {e}")
            return json.dumps(data, ensure_ascii=False)
    
    @staticmethod
    def decrypt_json(encrypted_data: str, key: str) -> Any:
        """解密JSON数据"""
        try:
            json_str = EncryptionUtils.simple_decrypt(encrypted_data, key)
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"JSON解密失败: {e}")
            try:
                return json.loads(encrypted_data)
            except:
                return None
    
    @staticmethod
    def generate_checksum(data: Union[str, bytes]) -> str:
        """生成数据校验和"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def verify_checksum(data: Union[str, bytes], checksum: str) -> bool:
        """验证数据校验和"""
        return EncryptionUtils.generate_checksum(data) == checksum
    
    @staticmethod
    def obfuscate_string(text: str) -> str:
        """混淆字符串（用于日志等场景）"""
        if len(text) <= 4:
            return '*' * len(text)
        
        return text[:2] + '*' * (len(text) - 4) + text[-2:]

class SecureStorage:
    """安全存储类"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.encryption_key = encryption_key or self._generate_default_key()
    
    def _generate_default_key(self) -> str:
        """生成默认密钥"""
        # 基于机器特征生成密钥
        import platform
        import getpass
        
        machine_info = f"{platform.node()}{getpass.getuser()}{platform.machine()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:32]
    
    def encrypt_data(self, data: Any) -> str:
        """加密数据"""
        return EncryptionUtils.encrypt_json(data, self.encryption_key)
    
    def decrypt_data(self, encrypted_data: str) -> Any:
        """解密数据"""
        return EncryptionUtils.decrypt_json(encrypted_data, self.encryption_key)
    
    def secure_store(self, key: str, data: Any) -> dict:
        """安全存储数据"""
        encrypted_data = self.encrypt_data(data)
        checksum = EncryptionUtils.generate_checksum(encrypted_data)
        
        return {
            'data': encrypted_data,
            'checksum': checksum,
            'timestamp': time.time()
        }
    
    def secure_retrieve(self, stored_data: dict) -> Any:
        """安全检索数据"""
        try:
            encrypted_data = stored_data['data']
            checksum = stored_data['checksum']
            
            # 验证校验和
            if not EncryptionUtils.verify_checksum(encrypted_data, checksum):
                logger.warning("数据校验和验证失败")
                return None
            
            return self.decrypt_data(encrypted_data)
            
        except Exception as e:
            logger.error(f"安全检索数据失败: {e}")
            return None

# 全局安全存储实例
secure_storage = SecureStorage()
