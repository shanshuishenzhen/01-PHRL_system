# -*- coding: utf-8 -*-
"""
对话上下文管理模块

提供对话上下文的记录、查询和管理功能，记录问题的提出、解决方案以及尝试过的方案。

更新日志：
- 2024-07-10：初始版本，提供基本对话上下文记录功能
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# 导入项目模块
import sys
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.file_manager import ensure_dir, read_json_file, write_json_file

# 创建日志记录器
logger = get_logger("conversation_manager", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "conversation_manager.log"))

# 默认配置
DEFAULT_CONFIG = {
    "conversation_file": "data/conversations.json",
    "max_conversations": 100,
    "auto_save": True,
    "record_timestamp": True
}


class ConversationManager:
    """
    对话上下文管理器类
    
    提供对话上下文的记录、查询和管理功能。
    """
    def __init__(self, config=None):
        """
        初始化对话上下文管理器
        
        Args:
            config (dict, optional): 配置字典，如果为None则使用默认配置
        """
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        # 确保对话记录文件目录存在
        self.conversation_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), self.config["conversation_file"])
        ensure_dir(os.path.dirname(self.conversation_file))
        
        # 加载对话记录
        self.conversations = self._load_conversations()
    
    def _load_conversations(self):
        """
        加载对话记录
        
        Returns:
            list: 对话记录列表
        """
        data = read_json_file(self.conversation_file)
        if data is None:
            return []
        # 确保返回的是列表，如果数据是 {"conversations": []} 格式，则获取 conversations 键对应的值
        if isinstance(data, dict) and "conversations" in data:
            return data["conversations"]
        return data
    
    def _save_conversations(self):
        """
        保存对话记录
        
        Returns:
            bool: 是否成功保存
        """
        # 将对话记录列表包装在字典中，与读取格式保持一致
        data = {"conversations": self.conversations}
        return write_json_file(self.conversation_file, data)
    
    def add_conversation(self, topic, question, solution=None, attempts=None, status="未解决"):
        """
        添加对话记录
        
        Args:
            topic (str): 对话主题
            question (str): 问题描述
            solution (str, optional): 解决方案
            attempts (list, optional): 尝试过的方案列表
            status (str, optional): 问题状态，可选值："未解决"、"已解决"、"部分解决"
            
        Returns:
            str: 对话记录ID
        """
        # 生成唯一ID
        conversation_id = str(uuid.uuid4())
        
        # 创建对话记录
        conversation = {
            "id": conversation_id,
            "topic": topic,
            "question": question,
            "solution": solution,
            "attempts": attempts if attempts else [],
            "status": status,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 添加到对话记录列表
        self.conversations.append(conversation)
        
        # 如果超过最大记录数，删除最早的记录
        if len(self.conversations) > self.config["max_conversations"]:
            self.conversations.pop(0)
        
        # 如果配置了自动保存，则保存对话记录
        if self.config["auto_save"]:
            self._save_conversations()
        
        logger.info(f"添加对话记录: {conversation_id}, 主题: {topic}")
        return conversation_id
    
    def update_conversation(self, conversation_id, **kwargs):
        """
        更新对话记录
        
        Args:
            conversation_id (str): 对话记录ID
            **kwargs: 要更新的字段和值
            
        Returns:
            bool: 是否成功更新
        """
        # 查找对话记录
        for i, conversation in enumerate(self.conversations):
            if conversation["id"] == conversation_id:
                # 更新字段
                for key, value in kwargs.items():
                    if key in conversation:
                        conversation[key] = value
                
                # 更新更新时间
                conversation["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 如果配置了自动保存，则保存对话记录
                if self.config["auto_save"]:
                    self._save_conversations()
                
                logger.info(f"更新对话记录: {conversation_id}")
                return True
        
        logger.warning(f"未找到对话记录: {conversation_id}")
        return False
    
    def get_conversation(self, conversation_id):
        """
        获取对话记录
        
        Args:
            conversation_id (str): 对话记录ID
            
        Returns:
            dict: 对话记录，如果未找到则返回None
        """
        for conversation in self.conversations:
            if conversation["id"] == conversation_id:
                return conversation
        
        logger.warning(f"未找到对话记录: {conversation_id}")
        return None
    
    def get_all_conversations(self):
        """
        获取所有对话记录
        
        Returns:
            list: 对话记录列表
        """
        return self.conversations
    
    def delete_conversation(self, conversation_id):
        """
        删除对话记录
        
        Args:
            conversation_id (str): 对话记录ID
            
        Returns:
            bool: 是否成功删除
        """
        for i, conversation in enumerate(self.conversations):
            if conversation["id"] == conversation_id:
                self.conversations.pop(i)
                
                # 如果配置了自动保存，则保存对话记录
                if self.config["auto_save"]:
                    self._save_conversations()
                
                logger.info(f"删除对话记录: {conversation_id}")
                return True
        
        logger.warning(f"未找到对话记录: {conversation_id}")
        return False
    
    def add_attempt(self, conversation_id, attempt):
        """
        添加尝试过的方案
        
        Args:
            conversation_id (str): 对话记录ID
            attempt (str): 尝试过的方案
            
        Returns:
            bool: 是否成功添加
        """
        for conversation in self.conversations:
            if conversation["id"] == conversation_id:
                if "attempts" not in conversation:
                    conversation["attempts"] = []
                
                # 添加尝试过的方案
                conversation["attempts"].append({
                    "description": attempt,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if self.config["record_timestamp"] else None
                })
                
                # 更新更新时间
                conversation["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 如果配置了自动保存，则保存对话记录
                if self.config["auto_save"]:
                    self._save_conversations()
                
                logger.info(f"添加尝试方案: {conversation_id}")
                return True
        
        logger.warning(f"未找到对话记录: {conversation_id}")
        return False
    
    def search_conversations(self, keyword):
        """
        搜索对话记录
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            list: 匹配的对话记录列表
        """
        results = []
        for conversation in self.conversations:
            # 在主题、问题和解决方案中搜索关键词
            if (keyword.lower() in conversation["topic"].lower() or
                keyword.lower() in conversation["question"].lower() or
                (conversation["solution"] and keyword.lower() in conversation["solution"].lower())):
                results.append(conversation)
        
        return results
    
    def get_unsolved_conversations(self):
        """
        获取未解决的对话记录
        
        Returns:
            list: 未解决的对话记录列表
        """
        return [c for c in self.conversations if c["status"] == "未解决"]
    
    def get_solved_conversations(self):
        """
        获取已解决的对话记录
        
        Returns:
            list: 已解决的对话记录列表
        """
        return [c for c in self.conversations if c["status"] == "已解决"]
    
    def mark_as_solved(self, conversation_id, solution):
        """
        标记对话记录为已解决
        
        Args:
            conversation_id (str): 对话记录ID
            solution (str): 解决方案
            
        Returns:
            bool: 是否成功标记
        """
        return self.update_conversation(conversation_id, status="已解决", solution=solution)
    
    def mark_as_unsolved(self, conversation_id):
        """
        标记对话记录为未解决
        
        Args:
            conversation_id (str): 对话记录ID
            
        Returns:
            bool: 是否成功标记
        """
        return self.update_conversation(conversation_id, status="未解决")
    
    def mark_as_partially_solved(self, conversation_id, solution):
        """
        标记对话记录为部分解决
        
        Args:
            conversation_id (str): 对话记录ID
            solution (str): 部分解决方案
            
        Returns:
            bool: 是否成功标记
        """
        return self.update_conversation(conversation_id, status="部分解决", solution=solution)


# 单例模式，提供全局访问点
_instance = None

def get_conversation_manager(config=None):
    """
    获取对话上下文管理器实例
    
    Args:
        config (dict, optional): 配置字典
        
    Returns:
        ConversationManager: 对话上下文管理器实例
    """
    global _instance
    if _instance is None:
        _instance = ConversationManager(config)
    return _instance


# 测试代码
if __name__ == "__main__":
    # 创建对话上下文管理器
    manager = get_conversation_manager()
    
    # 添加对话记录
    conversation_id = manager.add_conversation(
        "系统启动问题",
        "系统启动时报错：无法连接到数据库",
        status="未解决"
    )
    
    # 添加尝试过的方案
    manager.add_attempt(conversation_id, "检查数据库服务是否启动")
    manager.add_attempt(conversation_id, "检查数据库连接字符串是否正确")
    
    # 标记为已解决
    manager.mark_as_solved(conversation_id, "数据库服务未启动，启动服务后问题解决")
    
    # 打印所有对话记录
    print("所有对话记录:")
    for conversation in manager.get_all_conversations():
        print(f"ID: {conversation['id']}")
        print(f"主题: {conversation['topic']}")
        print(f"问题: {conversation['question']}")
        print(f"状态: {conversation['status']}")
        print(f"解决方案: {conversation['solution']}")
        print(f"尝试过的方案: {conversation['attempts']}")
        print(f"创建时间: {conversation['created_at']}")
        print(f"更新时间: {conversation['updated_at']}")
        print("---")
    
    print("测试完成")