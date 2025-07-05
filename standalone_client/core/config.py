#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端配置管理

负责管理客户端的所有配置信息，包括服务器配置、UI配置、安全配置等。
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ClientConfig:
    """客户端配置管理器"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config_file = self.config_dir / "client_config.json"
        self.config_dir.mkdir(exist_ok=True)
        
        # 默认配置
        self.default_config = {
            "app": {
                "name": "PH&RL 考试客户端",
                "version": "1.0.0",
                "debug": False,
                "auto_save_interval": 30,  # 秒
                "theme": "default"
            },
            "server": {
                "host": "localhost",
                "port": 5000,
                "protocol": "http",
                "timeout": 30,
                "retry_count": 3,
                "retry_delay": 5
            },
            "ui": {
                "window_size": "1024x768",
                "fullscreen_exam": True,
                "font_family": "Microsoft YaHei",
                "font_size": 12,
                "theme_color": "#2196F3",
                "show_progress": True,
                "show_timer": True
            },
            "security": {
                "enable_anti_cheat": True,
                "disable_alt_tab": True,
                "disable_task_manager": True,
                "monitor_processes": True,
                "encrypt_answers": True,
                "screenshot_protection": True
            },
            "exam": {
                "auto_save_answers": True,
                "save_interval": 30,
                "confirm_submit": True,
                "show_question_numbers": True,
                "allow_review": True,
                "time_warning_minutes": 5
            },
            "network": {
                "connection_check_interval": 60,
                "offline_mode": False,
                "cache_questions": True,
                "max_cache_size": 100  # MB
            },
            "logging": {
                "level": "INFO",
                "max_file_size": 10,  # MB
                "backup_count": 5,
                "log_to_file": True,
                "log_to_console": False
            }
        }
        
        # 加载配置
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # 合并默认配置和加载的配置
                config = self.default_config.copy()
                self._deep_update(config, loaded_config)
                return config
            else:
                # 如果配置文件不存在，创建默认配置文件
                self.save_config(self.default_config)
                return self.default_config.copy()
                
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """保存配置文件"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        try:
            # 导航到最后一级的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
            # 保存配置
            return self.save_config()
            
        except Exception as e:
            print(f"设置配置值失败: {e}")
            return False
    
    def _deep_update(self, base_dict: Dict, update_dict: Dict) -> None:
        """深度更新字典"""
        for key, value in update_dict.items():
            if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def get_server_url(self) -> str:
        """获取服务器URL"""
        protocol = self.get('server.protocol', 'http')
        host = self.get('server.host', 'localhost')
        port = self.get('server.port', 5000)
        return f"{protocol}://{host}:{port}"
    
    def is_debug_mode(self) -> bool:
        """是否为调试模式"""
        return self.get('app.debug', False)
    
    def get_ui_config(self) -> Dict[str, Any]:
        """获取UI配置"""
        return self.get('ui', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.get('security', {})
    
    def get_exam_config(self) -> Dict[str, Any]:
        """获取考试配置"""
        return self.get('exam', {})
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        self.config = self.default_config.copy()
        return self.save_config()
    
    def validate_config(self) -> list:
        """验证配置有效性"""
        errors = []
        
        # 验证服务器配置
        if not self.get('server.host'):
            errors.append("服务器地址不能为空")
        
        port = self.get('server.port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("服务器端口必须是1-65535之间的整数")
        
        # 验证UI配置
        window_size = self.get('ui.window_size', '')
        if 'x' not in window_size:
            errors.append("窗口大小格式错误，应为 '宽度x高度'")
        
        # 验证字体大小
        font_size = self.get('ui.font_size')
        if not isinstance(font_size, int) or font_size < 8 or font_size > 72:
            errors.append("字体大小必须是8-72之间的整数")
        
        return errors

# 全局配置实例
client_config = ClientConfig()
