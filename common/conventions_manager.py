#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统约定管理器

负责管理和应用系统全局约定条件，确保所有模块遵循统一的约定。
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

class ConventionsManager:
    """系统约定管理器"""
    
    def __init__(self, conventions_file: str = "system_conventions.json"):
        """
        初始化约定管理器
        
        Args:
            conventions_file: 约定文件路径
        """
        self.conventions_file = PROJECT_ROOT / conventions_file
        self.conventions = {}
        self.logger = self._setup_logger()
        
        # 加载约定
        self.load_conventions()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("conventions_manager")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 创建日志目录
            log_dir = PROJECT_ROOT / "logs"
            log_dir.mkdir(exist_ok=True)
            
            # 文件处理器
            file_handler = logging.FileHandler(
                log_dir / "conventions.log", 
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def load_conventions(self) -> bool:
        """
        加载系统约定
        
        Returns:
            bool: 是否成功加载
        """
        try:
            if not self.conventions_file.exists():
                self.logger.warning(f"约定文件不存在: {self.conventions_file}")
                self._create_default_conventions()
                return False
            
            with open(self.conventions_file, 'r', encoding='utf-8') as f:
                self.conventions = json.load(f)
            
            self.logger.info(f"成功加载系统约定: {self.conventions_file}")
            self._log_conventions_summary()
            return True
            
        except Exception as e:
            self.logger.error(f"加载约定文件失败: {e}")
            return False
    
    def _create_default_conventions(self):
        """创建默认约定文件"""
        default_conventions = {
            "system_info": {
                "name": "PH&RL 考试系统全局约定",
                "version": "1.0.0",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "description": "系统全局约定条件和默认配置"
            },
            "authentication": {
                "super_admin": {
                    "username": "admin",
                    "password": "123456",
                    "description": "内置超级用户，拥有所有权限"
                }
            }
        }
        
        try:
            with open(self.conventions_file, 'w', encoding='utf-8') as f:
                json.dump(default_conventions, f, ensure_ascii=False, indent=2)
            self.logger.info(f"创建默认约定文件: {self.conventions_file}")
        except Exception as e:
            self.logger.error(f"创建默认约定文件失败: {e}")
    
    def _log_conventions_summary(self):
        """记录约定摘要"""
        if not self.conventions:
            return
        
        system_info = self.conventions.get("system_info", {})
        self.logger.info(f"约定文件信息:")
        self.logger.info(f"  名称: {system_info.get('name', '未知')}")
        self.logger.info(f"  版本: {system_info.get('version', '未知')}")
        self.logger.info(f"  更新时间: {system_info.get('last_updated', '未知')}")
        
        # 记录主要约定类别
        categories = [k for k in self.conventions.keys() if k != "system_info"]
        self.logger.info(f"  约定类别: {', '.join(categories)}")
    
    def get_convention(self, path: str, default: Any = None) -> Any:
        """
        获取约定值
        
        Args:
            path: 约定路径，使用点号分隔，如 "authentication.super_admin.username"
            default: 默认值
            
        Returns:
            约定值或默认值
        """
        try:
            keys = path.split('.')
            value = self.conventions
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"获取约定值失败: {path}, 错误: {e}")
            return default
    
    def get_super_admin(self) -> Dict[str, str]:
        """
        获取超级管理员信息
        
        Returns:
            超级管理员信息字典
        """
        return {
            "username": self.get_convention("authentication.super_admin.username", "admin"),
            "password": self.get_convention("authentication.super_admin.password", "123456"),
            "description": self.get_convention("authentication.super_admin.description", "内置超级用户")
        }
    
    def get_default_permissions(self, role: str) -> List[str]:
        """
        获取角色默认权限
        
        Args:
            role: 用户角色
            
        Returns:
            权限列表
        """
        permissions_map = self.get_convention("authentication.default_permissions", {})
        return permissions_map.get(role, [])
    
    def get_ui_theme(self) -> Dict[str, Any]:
        """
        获取UI主题配置
        
        Returns:
            UI主题配置字典
        """
        return self.get_convention("ui_conventions.theme", {})
    
    def get_question_type_config(self, question_type: str) -> Dict[str, Any]:
        """
        获取题型配置
        
        Args:
            question_type: 题型名称
            
        Returns:
            题型配置字典
        """
        return self.get_convention(f"exam_conventions.question_types.{question_type}", {})
    
    def get_default_ports(self) -> Dict[str, int]:
        """
        获取默认端口配置
        
        Returns:
            端口配置字典
        """
        return self.get_convention("network_conventions.default_ports", {})
    
    def get_file_conventions(self) -> Dict[str, Any]:
        """
        获取文件约定
        
        Returns:
            文件约定字典
        """
        return self.get_convention("file_conventions", {})
    
    def apply_conventions_to_module(self, module_name: str) -> Dict[str, Any]:
        """
        为特定模块应用约定
        
        Args:
            module_name: 模块名称
            
        Returns:
            应用的约定配置
        """
        applied_config = {}
        
        try:
            # 应用认证约定
            if module_name in ["user_management", "main_console", "client"]:
                applied_config["super_admin"] = self.get_super_admin()
                applied_config["default_permissions"] = self.get_convention("authentication.default_permissions", {})
            
            # 应用UI约定
            if module_name in ["client", "main_console", "question_bank"]:
                applied_config["ui_theme"] = self.get_ui_theme()
                applied_config["fonts"] = self.get_convention("ui_conventions.fonts", {})
                applied_config["layout"] = self.get_convention("ui_conventions.layout", {})
            
            # 应用考试约定
            if module_name in ["exam_management", "client", "grading_center"]:
                applied_config["question_types"] = self.get_convention("exam_conventions.question_types", {})
                applied_config["scoring"] = self.get_convention("exam_conventions.scoring", {})
                applied_config["time_limits"] = self.get_convention("exam_conventions.time_limits", {})
            
            # 应用网络约定
            if module_name in ["main_console", "question_bank", "grading_center"]:
                applied_config["default_ports"] = self.get_default_ports()
                applied_config["api_endpoints"] = self.get_convention("network_conventions.api_endpoints", {})
                applied_config["timeouts"] = self.get_convention("network_conventions.timeouts", {})
            
            # 应用文件约定
            applied_config["file_conventions"] = self.get_file_conventions()
            
            self.logger.info(f"为模块 {module_name} 应用了约定配置")
            return applied_config
            
        except Exception as e:
            self.logger.error(f"为模块 {module_name} 应用约定失败: {e}")
            return {}
    
    def validate_conventions(self) -> List[str]:
        """
        验证约定配置
        
        Returns:
            验证错误列表
        """
        errors = []
        
        try:
            # 验证必需的约定
            required_paths = [
                "authentication.super_admin.username",
                "authentication.super_admin.password",
                "ui_conventions.theme.primary_color",
                "exam_conventions.question_types.true_false.options"
            ]
            
            for path in required_paths:
                value = self.get_convention(path)
                if value is None:
                    errors.append(f"缺少必需约定: {path}")
            
            # 验证特定约定
            true_false_options = self.get_convention("exam_conventions.question_types.true_false.options", [])
            if len(true_false_options) != 2:
                errors.append("判断题选项必须包含2个选项")
            
            # 验证端口配置
            ports = self.get_default_ports()
            for module, port in ports.items():
                if not isinstance(port, int) or port < 1000 or port > 65535:
                    errors.append(f"模块 {module} 的端口配置无效: {port}")
            
            if not errors:
                self.logger.info("约定配置验证通过")
            else:
                self.logger.warning(f"约定配置验证发现 {len(errors)} 个问题")
                for error in errors:
                    self.logger.warning(f"  - {error}")
            
            return errors
            
        except Exception as e:
            self.logger.error(f"验证约定配置时出错: {e}")
            return [f"验证过程出错: {e}"]

    def save_config(self) -> bool:
        """
        保存约定配置到文件

        Returns:
            bool: 是否成功保存
        """
        try:
            # 更新时间戳
            if "system_info" in self.conventions:
                self.conventions["system_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")

            # 保存到文件
            with open(self.conventions_file, 'w', encoding='utf-8') as f:
                json.dump(self.conventions, f, ensure_ascii=False, indent=2)

            self.logger.info(f"成功保存约定配置: {self.conventions_file}")
            return True

        except Exception as e:
            self.logger.error(f"保存约定配置失败: {e}")
            return False

    def update_convention(self, path: str, value: Any) -> bool:
        """
        更新约定值
        
        Args:
            path: 约定路径
            value: 新值
            
        Returns:
            bool: 是否成功更新
        """
        try:
            keys = path.split('.')
            current = self.conventions
            
            # 导航到目标位置
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # 设置值
            current[keys[-1]] = value
            
            # 更新时间戳
            if "system_info" in self.conventions:
                self.conventions["system_info"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
            
            # 保存到文件
            with open(self.conventions_file, 'w', encoding='utf-8') as f:
                json.dump(self.conventions, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"成功更新约定: {path} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"更新约定失败: {path}, 错误: {e}")
            return False
    
    def print_conventions_summary(self):
        """打印约定摘要"""
        print("\n" + "="*60)
        print("📋 系统约定摘要")
        print("="*60)
        
        if not self.conventions:
            print("❌ 未加载约定配置")
            return
        
        # 系统信息
        system_info = self.conventions.get("system_info", {})
        print(f"📌 系统名称: {system_info.get('name', '未知')}")
        print(f"📌 版本: {system_info.get('version', '未知')}")
        print(f"📌 更新时间: {system_info.get('last_updated', '未知')}")
        
        # 超级管理员
        super_admin = self.get_super_admin()
        print(f"\n👤 超级管理员:")
        print(f"   用户名: {super_admin['username']}")
        print(f"   密码: {super_admin['password']}")
        
        # 判断题约定
        true_false_options = self.get_convention("exam_conventions.question_types.true_false.options", [])
        print(f"\n📝 判断题选项: {true_false_options}")
        
        # 默认端口
        ports = self.get_default_ports()
        print(f"\n🌐 默认端口:")
        for module, port in ports.items():
            print(f"   {module}: {port}")
        
        print("="*60)


# 创建全局实例
conventions_manager = ConventionsManager()

def get_conventions_manager() -> ConventionsManager:
    """获取约定管理器实例"""
    return conventions_manager

def get_convention(path: str, default: Any = None) -> Any:
    """快捷方式：获取约定值"""
    return conventions_manager.get_convention(path, default)

def apply_conventions(module_name: str) -> Dict[str, Any]:
    """快捷方式：为模块应用约定"""
    return conventions_manager.apply_conventions_to_module(module_name)
