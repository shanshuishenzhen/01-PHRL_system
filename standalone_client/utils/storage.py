#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地存储管理

提供本地数据存储和缓存功能。
"""

import json
import sqlite3
import pickle
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)

class LocalStorage:
    """本地存储管理器"""
    
    def __init__(self):
        self.storage_dir = Path(__file__).parent.parent / "cache"
        self.storage_dir.mkdir(exist_ok=True)
        
        # 数据库文件
        self.db_file = self.storage_dir / "client.db"
        self._init_database()
        
        # JSON存储目录
        self.json_dir = self.storage_dir / "json"
        self.json_dir.mkdir(exist_ok=True)
        
        # 临时文件目录
        self.temp_dir = self.storage_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    def _init_database(self):
        """初始化数据库"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 创建缓存表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        access_count INTEGER DEFAULT 0,
                        last_access TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建考试数据表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS exam_data (
                        exam_id TEXT NOT NULL,
                        question_id TEXT NOT NULL,
                        answer TEXT,
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (exam_id, question_id)
                    )
                ''')
                
                # 创建用户设置表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id TEXT NOT NULL,
                        setting_key TEXT NOT NULL,
                        setting_value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (user_id, setting_key)
                    )
                ''')
                
                conn.commit()
                logger.debug("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
    
    def set_cache(self, key: str, value: Any, expires_in: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            # 计算过期时间
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO cache 
                    (key, value, expires_at, access_count, last_access)
                    VALUES (?, ?, ?, 0, CURRENT_TIMESTAMP)
                ''', (key, serialized_value, expires_at))
                conn.commit()
            
            logger.debug(f"缓存已设置: {key}")
            return True
            
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def get_cache(self, key: str, default: Any = None) -> Any:
        """获取缓存"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT value, expires_at FROM cache 
                    WHERE key = ?
                ''', (key,))
                
                result = cursor.fetchone()
                if not result:
                    return default
                
                value, expires_at = result
                
                # 检查是否过期
                if expires_at:
                    expires_time = datetime.fromisoformat(expires_at)
                    if datetime.now() > expires_time:
                        self.delete_cache(key)
                        return default
                
                # 更新访问统计
                cursor.execute('''
                    UPDATE cache 
                    SET access_count = access_count + 1, 
                        last_access = CURRENT_TIMESTAMP
                    WHERE key = ?
                ''', (key,))
                conn.commit()
                
                # 尝试反序列化
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
                    
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return default
    
    def delete_cache(self, key: str) -> bool:
        """删除缓存"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
                conn.commit()
            
            logger.debug(f"缓存已删除: {key}")
            return True
            
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def clear_expired_cache(self) -> int:
        """清理过期缓存"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM cache 
                    WHERE expires_at IS NOT NULL 
                    AND expires_at < CURRENT_TIMESTAMP
                ''')
                deleted_count = cursor.rowcount
                conn.commit()
            
            logger.info(f"清理了 {deleted_count} 个过期缓存")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return 0
    
    def save_exam_answer(self, exam_id: str, question_id: str, answer: Any) -> bool:
        """保存考试答案"""
        try:
            # 序列化答案
            if isinstance(answer, (dict, list)):
                serialized_answer = json.dumps(answer, ensure_ascii=False)
            else:
                serialized_answer = str(answer) if answer is not None else ""
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO exam_data 
                    (exam_id, question_id, answer, saved_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (exam_id, question_id, serialized_answer))
                conn.commit()
            
            logger.debug(f"答案已保存: {exam_id}/{question_id}")
            return True
            
        except Exception as e:
            logger.error(f"保存答案失败: {e}")
            return False
    
    def get_exam_answer(self, exam_id: str, question_id: str) -> Any:
        """获取考试答案"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT answer FROM exam_data 
                    WHERE exam_id = ? AND question_id = ?
                ''', (exam_id, question_id))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                answer = result[0]
                if not answer:
                    return None
                
                # 尝试反序列化
                try:
                    return json.loads(answer)
                except json.JSONDecodeError:
                    return answer
                    
        except Exception as e:
            logger.error(f"获取答案失败: {e}")
            return None
    
    def get_all_exam_answers(self, exam_id: str) -> Dict[str, Any]:
        """获取考试的所有答案"""
        try:
            answers = {}
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT question_id, answer FROM exam_data 
                    WHERE exam_id = ?
                ''', (exam_id,))
                
                for question_id, answer in cursor.fetchall():
                    if answer:
                        try:
                            answers[question_id] = json.loads(answer)
                        except json.JSONDecodeError:
                            answers[question_id] = answer
            
            return answers
            
        except Exception as e:
            logger.error(f"获取所有答案失败: {e}")
            return {}
    
    def clear_exam_data(self, exam_id: str) -> bool:
        """清除考试数据"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM exam_data WHERE exam_id = ?', (exam_id,))
                conn.commit()
            
            logger.info(f"考试数据已清除: {exam_id}")
            return True
            
        except Exception as e:
            logger.error(f"清除考试数据失败: {e}")
            return False
    
    def save_json(self, filename: str, data: Any) -> bool:
        """保存JSON文件"""
        try:
            file_path = self.json_dir / f"{filename}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"JSON文件已保存: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"保存JSON文件失败: {e}")
            return False
    
    def load_json(self, filename: str, default: Any = None) -> Any:
        """加载JSON文件"""
        try:
            file_path = self.json_dir / f"{filename}.json"
            if not file_path.exists():
                return default
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"加载JSON文件失败: {e}")
            return default
    
    def get_storage_size(self) -> Dict[str, int]:
        """获取存储大小信息"""
        try:
            sizes = {}
            
            # 数据库大小
            if self.db_file.exists():
                sizes['database'] = self.db_file.stat().st_size
            
            # JSON文件大小
            json_size = 0
            for file_path in self.json_dir.rglob('*.json'):
                json_size += file_path.stat().st_size
            sizes['json'] = json_size
            
            # 临时文件大小
            temp_size = 0
            for file_path in self.temp_dir.rglob('*'):
                if file_path.is_file():
                    temp_size += file_path.stat().st_size
            sizes['temp'] = temp_size
            
            sizes['total'] = sum(sizes.values())
            return sizes
            
        except Exception as e:
            logger.error(f"获取存储大小失败: {e}")
            return {}
    
    def cleanup_storage(self, max_age_days: int = 30) -> bool:
        """清理存储空间"""
        try:
            # 清理过期缓存
            self.clear_expired_cache()
            
            # 清理旧的临时文件
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0
            
            for file_path in self.temp_dir.rglob('*'):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
            
            logger.info(f"存储清理完成，删除了 {cleaned_count} 个文件")
            return True
            
        except Exception as e:
            logger.error(f"存储清理失败: {e}")
            return False

# 全局存储实例
local_storage = LocalStorage()
