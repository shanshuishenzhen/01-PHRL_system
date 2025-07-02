# -*- coding: utf-8 -*-
"""
配置管理工具模块

提供系统配置的加载、保存和更新功能。

更新日志：
- 2024-06-25：初始版本，提供基本配置管理功能
- 2024-07-05：添加ConfigManager类，提供面向对象的配置管理接口
"""

import os
import json
from pathlib import Path

# 默认配置
DEFAULT_CONFIG = {
    # 系统基本信息
    'version': '1.0.0',
    'min_python_version': [3, 6],
    'required_disk_space_mb': 100,
    'check_dependencies': True,
    'auto_create_missing_files': True,
    'update_interval': 5,
    
    # 模块端口配置
    'module_ports': {
        'question_bank': 5000,
        'grading_center': 3000,
        'grading_center_frontend': 5173,
        'exam_management': 5001,
        'client': 8080
    },
    
    # 系统监控配置
    'enable_resource_monitoring': True,
    'auto_restart_crashed_modules': False,
    
    # 系统信息
    'system': {
        'name': 'PH&RL 在线考试系统',
        'organization': 'PH&RL 教育科技',
        'contact_email': 'support@phrl-exam.com',
        'website': 'https://www.phrl-exam.com',
        'copyright': '© 2024 PH&RL 教育科技. 保留所有权利。'
    },
    
    # 日志配置
    'logging': {
        'level': 'INFO',
        'max_file_size_mb': 10,
        'backup_count': 5,
        'console_output': True
    },
    
    # 用户界面配置
    'language': 'zh_CN',  # 默认语言
    'theme': 'default',   # 默认主题
    'log_level': 'INFO',  # 默认日志级别
    'auto_update': True,  # 是否自动更新
    'data_path': '',      # 数据存储路径
    'backup_path': '',    # 备份路径
    'max_log_size': 10,   # 最大日志大小(MB)
    'max_log_count': 5,   # 最大日志文件数
    'check_update_interval': 7,  # 检查更新间隔(天)
    'last_update_check': 0,      # 上次检查更新时间
    'modules': {},        # 模块配置
    'debug_mode': False,  # 调试模式
    'advanced_mode': False,  # 高级模式
    'show_console': False,   # 显示控制台
    'auto_backup': True,     # 自动备份
    'backup_interval': 7,    # 备份间隔(天)
    'last_backup': 0,        # 上次备份时间
    'max_backup_count': 5,   # 最大备份数量
    'startup_module': '',    # 启动时打开的模块
    'recent_files': [],      # 最近打开的文件
    'max_recent_files': 10,  # 最近文件最大数量
    'window_size': '1024x768',  # 窗口大小
    'window_position': '',      # 窗口位置
    'window_maximized': False,  # 窗口是否最大化
    'font_size': 12,            # 字体大小
    'font_family': '',          # 字体
    'ui_scale': 1.0,            # UI缩放
    'show_toolbar': True,       # 显示工具栏
    'show_statusbar': True,     # 显示状态栏
    'confirm_exit': True,       # 退出时确认
    'auto_save': True,          # 自动保存
    'auto_save_interval': 5,    # 自动保存间隔(分钟)
    'check_disk_space': True,   # 检查磁盘空间
    'min_disk_space': 500,      # 最小磁盘空间(MB)
    'enable_animations': True,  # 启用动画
    'enable_sounds': True,      # 启用声音
    'notification_level': 'all',  # 通知级别
    
    # 网络配置
    'proxy': '',                # 代理设置
    'timeout': 30,              # 网络超时(秒)
    'retry_count': 3,           # 重试次数
    'retry_interval': 5,        # 重试间隔(秒)
    
    # 自定义配置
    'custom_css': '',           # 自定义CSS
    'custom_js': '',            # 自定义JS
    'plugins': [],              # 启用的插件
    'experimental_features': False,  # 实验性功能
    'telemetry': False,         # 遥测
    'update_channel': 'stable',  # 更新通道
    
    # 依赖管理配置
    'auto_check_dependencies': True,  # 自动检查依赖
    'use_pip_mirror': True,     # 使用国内镜像源安装依赖
    'pip_mirror_url': 'https://pypi.tuna.tsinghua.edu.cn/simple',  # 默认镜像源URL
    
    # 其他配置
    'show_welcome': True,       # 显示欢迎页
    'first_run': True,          # 首次运行
    'last_run_version': '',     # 上次运行版本
    'custom_user_agent': '',    # 自定义User-Agent
    
    # 编辑器配置
    'editor_theme': 'default',  # 编辑器主题
    'editor_word_wrap': True,   # 编辑器自动换行
    'editor_show_line_numbers': True,  # 显示行号
    'editor_tab_size': 4,       # Tab大小
    'editor_use_spaces': True,  # 使用空格代替Tab
    'editor_auto_indent': True, # 自动缩进
    'editor_highlight_line': True,  # 高亮当前行
    'editor_auto_complete': True,   # 自动完成
    'editor_auto_pair': True,       # 自动配对括号
    'editor_spell_check': False,    # 拼写检查
    'editor_font_size': 12,         # 编辑器字体大小
    'editor_font_family': '',       # 编辑器字体
    
    # 终端配置
    'terminal_font_size': 12,       # 终端字体大小
    'terminal_font_family': '',     # 终端字体
    'terminal_cursor_style': 'block',  # 终端光标样式
    'terminal_transparency': 0,     # 终端透明度
    'terminal_scrollback': 1000,    # 终端回滚行数
}


def get_config_path():
    """
    获取配置文件路径
    
    Returns:
        Path: 配置文件路径
    """
    return Path(__file__).parent.parent / "config.json"


def load_config():
    """
    加载系统配置
    
    Returns:
        dict: 系统配置字典，如果加载失败则返回默认配置
    """
    config_path = get_config_path()
    
    # 如果配置文件不存在，创建默认配置文件
    if not config_path.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    # 尝试加载配置文件
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        # 如果加载失败，返回默认配置
        return DEFAULT_CONFIG


def save_config(config):
    """
    保存系统配置
    
    Args:
        config (dict): 系统配置字典
        
    Returns:
        bool: 保存是否成功
    """
    config_path = get_config_path()
    
    try:
        # 确保配置文件目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存配置文件
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False


def get_system_info():
    """获取系统信息
    
    Returns:
        dict: 系统信息字典
    """
    config = load_config()
    return config.get("system_info", {
        "name": "PH&RL在线考试系统",
        "version": "1.0.0",
        "copyright": "© 2024 PH&RL教育科技",
        "website": "https://www.phrl-edu.com",
        "support_email": "support@phrl-edu.com"
    })


class ConfigManager:
    """
    配置管理器类
    
    提供面向对象的配置管理接口，包括配置的加载、保存、获取和设置。
    """
    def __init__(self, config_path=None):
        """
        初始化配置管理器
        
        Args:
            config_path (str, optional): 配置文件路径，如果为None则使用默认路径
        """
        self.config_path = Path(config_path) if config_path else get_config_path()
        self.config = self.load()
    
    def load(self):
        """
        加载配置
        
        Returns:
            dict: 配置字典
        """
        # 如果配置文件不存在，创建默认配置文件
        if not self.config_path.exists():
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        
        # 尝试加载配置文件
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            # 如果加载失败，返回默认配置
            return DEFAULT_CONFIG.copy()
    
    def save(self, config=None):
        """
        保存配置
        
        Args:
            config (dict, optional): 要保存的配置字典，如果为None则保存当前配置
            
        Returns:
            bool: 保存是否成功
        """
        if config is None:
            config = self.config
        
        try:
            # 确保配置文件目录存在
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存配置文件
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """
        获取配置项
        
        Args:
            key (str): 配置项键名，支持点号分隔的多级键名，如"system.name"
            default: 默认值，如果配置项不存在则返回此值
            
        Returns:
            配置项的值
        """
        if "." in key:
            # 处理多级键名
            keys = key.split(".")
            value = self.config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        else:
            # 处理单级键名
            return self.config.get(key, default)
    
    def set(self, key, value):
        """
        设置配置项
        
        Args:
            key (str): 配置项键名，支持点号分隔的多级键名，如"system.name"
            value: 配置项的值
            
        Returns:
            bool: 设置是否成功
        """
        if "." in key:
            # 处理多级键名
            keys = key.split(".")
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
        else:
            # 处理单级键名
            self.config[key] = value
        return True
    
    def update(self, config_dict):
        """
        更新多个配置项
        
        Args:
            config_dict (dict): 包含要更新的配置项的字典
            
        Returns:
            bool: 更新是否成功
        """
        self.config.update(config_dict)
        return True
    
    def reset(self):
        """
        重置配置为默认值
        
        Returns:
            bool: 重置是否成功
        """
        self.config = DEFAULT_CONFIG.copy()
        return self.save()
    
    def get_all(self):
        """
        获取所有配置
        
        Returns:
            dict: 完整的配置字典
        """
        return self.config.copy()