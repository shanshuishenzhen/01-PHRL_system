# -*- coding: utf-8 -*-
"""
国际化和本地化工具模块

提供多语言支持、文本翻译和本地化功能。

更新日志：
- 2024-06-25：初始版本，提供基本国际化和本地化功能
"""

import os
import sys
import json
import locale
import gettext
from pathlib import Path
from functools import lru_cache

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.file_manager import ensure_dir, read_json_file, write_json_file

# 创建日志记录器
logger = get_logger("i18n_manager", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "i18n_manager.log"))

# 默认语言
DEFAULT_LANGUAGE = "zh_CN"

# 支持的语言列表
SUPPORTED_LANGUAGES = {
    "zh_CN": {
        "name": "简体中文",
        "code": "zh_CN",
        "locale": "zh_CN.UTF-8"
    },
    "en_US": {
        "name": "English (US)",
        "code": "en_US",
        "locale": "en_US.UTF-8"
    }
}


class I18nManager:
    """
    国际化管理器，用于处理多语言支持和文本翻译
    """
    def __init__(self, language=None, translations_dir=None):
        """
        初始化国际化管理器
        
        Args:
            language (str, optional): 语言代码，如果为None则使用系统语言或默认语言
            translations_dir (str, optional): 翻译文件目录
        """
        # 设置翻译文件目录
        if translations_dir is None:
            project_root = Path(__file__).parent.parent
            translations_dir = os.path.join(project_root, "translations")
        
        self.translations_dir = translations_dir
        self.translations = {}
        
        # 确保翻译文件目录存在
        ensure_dir(self.translations_dir)
        
        # 设置语言
        if language is None:
            language = self.get_system_language()
        
        self.language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        
        # 加载翻译文件
        self.load_translations()
    
    def get_system_language(self):
        """
        获取系统语言
        
        Returns:
            str: 系统语言代码
        """
        try:
            # 获取系统语言设置
            system_locale, _ = locale.getdefaultlocale()
            
            # 如果系统语言在支持的语言列表中，返回系统语言
            if system_locale in SUPPORTED_LANGUAGES:
                return system_locale
            
            # 如果系统语言的前两个字符在支持的语言列表中，返回对应的语言
            if system_locale and len(system_locale) >= 2:
                lang_prefix = system_locale[:2].lower()
                for lang_code in SUPPORTED_LANGUAGES:
                    if lang_code.startswith(lang_prefix):
                        return lang_code
        except Exception as e:
            logger.error(f"获取系统语言失败: {str(e)}")
        
        # 如果无法获取系统语言或系统语言不受支持，返回默认语言
        return DEFAULT_LANGUAGE
    
    def load_translations(self):
        """
        加载翻译文件
        
        Returns:
            bool: 是否成功加载
        """
        try:
            # 加载所有支持的语言的翻译文件
            for lang_code in SUPPORTED_LANGUAGES:
                lang_file = os.path.join(self.translations_dir, f"{lang_code}.json")
                
                # 如果翻译文件不存在，创建空翻译文件
                if not os.path.exists(lang_file):
                    if lang_code == DEFAULT_LANGUAGE:
                        # 为默认语言创建基本翻译
                        self.translations[lang_code] = self.get_default_translations()
                        write_json_file(lang_file, self.translations[lang_code])
                    else:
                        # 为其他语言创建空翻译
                        self.translations[lang_code] = {}
                        write_json_file(lang_file, self.translations[lang_code])
                else:
                    # 加载翻译文件
                    translations = read_json_file(lang_file)
                    if translations is None:
                        self.translations[lang_code] = {}
                    else:
                        self.translations[lang_code] = translations
            
            return True
        except Exception as e:
            logger.error(f"加载翻译文件失败: {str(e)}")
            return False
    
    def get_default_translations(self):
        """
        获取默认翻译
        
        Returns:
            dict: 默认翻译
        """
        return {
            "common": {
                "ok": "确定",
                "cancel": "取消",
                "save": "保存",
                "delete": "删除",
                "edit": "编辑",
                "add": "添加",
                "search": "搜索",
                "refresh": "刷新",
                "close": "关闭",
                "back": "返回",
                "next": "下一步",
                "previous": "上一步",
                "yes": "是",
                "no": "否",
                "loading": "加载中...",
                "error": "错误",
                "warning": "警告",
                "info": "信息",
                "success": "成功",
                "failed": "失败",
                "unknown": "未知"
            },
            "login": {
                "title": "登录",
                "username": "用户名",
                "password": "密码",
                "login": "登录",
                "remember_me": "记住我",
                "forgot_password": "忘记密码？",
                "login_success": "登录成功",
                "login_failed": "登录失败",
                "username_required": "请输入用户名",
                "password_required": "请输入密码"
            },
            "main_console": {
                "title": "主控台",
                "status": "状态",
                "modules": "模块",
                "question_bank": "题库管理",
                "grading_center": "阅卷中心",
                "exam_management": "考试管理",
                "client": "客户端",
                "start": "启动",
                "stop": "停止",
                "restart": "重启",
                "running": "运行中",
                "stopped": "已停止",
                "starting": "启动中",
                "system_info": "系统信息",
                "version": "版本",
                "platform": "平台",
                "cpu_usage": "CPU使用率",
                "memory_usage": "内存使用率",
                "disk_usage": "磁盘使用率"
            },
            "question_bank": {
                "title": "题库管理",
                "add_question": "添加题目",
                "edit_question": "编辑题目",
                "delete_question": "删除题目",
                "import_questions": "导入题目",
                "export_questions": "导出题目",
                "question_type": "题目类型",
                "single_choice": "单选题",
                "multiple_choice": "多选题",
                "true_false": "判断题",
                "fill_blank": "填空题",
                "short_answer": "简答题",
                "question_content": "题目内容",
                "question_options": "选项",
                "question_answer": "答案",
                "question_analysis": "解析",
                "question_difficulty": "难度",
                "question_category": "分类",
                "question_tags": "标签"
            },
            "grading_center": {
                "title": "阅卷中心",
                "exam_list": "考试列表",
                "student_list": "学生列表",
                "answer_sheet": "答题卡",
                "auto_grading": "自动评分",
                "manual_grading": "人工评分",
                "grading_progress": "评分进度",
                "grading_statistics": "评分统计",
                "export_results": "导出结果"
            },
            "exam_management": {
                "title": "考试管理",
                "add_exam": "添加考试",
                "edit_exam": "编辑考试",
                "delete_exam": "删除考试",
                "exam_name": "考试名称",
                "exam_time": "考试时间",
                "exam_duration": "考试时长",
                "exam_status": "考试状态",
                "exam_questions": "考试题目",
                "exam_students": "考试学生",
                "exam_settings": "考试设置",
                "random_order": "随机顺序",
                "prevent_cheating": "防作弊",
                "auto_submit": "自动提交"
            },
            "client": {
                "title": "客户端",
                "exam_list": "考试列表",
                "start_exam": "开始考试",
                "submit_exam": "提交考试",
                "remaining_time": "剩余时间",
                "question_navigation": "题目导航",
                "previous_question": "上一题",
                "next_question": "下一题",
                "mark_question": "标记题目",
                "unmark_question": "取消标记",
                "marked_questions": "已标记题目",
                "answered_questions": "已回答题目",
                "unanswered_questions": "未回答题目"
            },
            "system": {
                "title": "系统",
                "settings": "设置",
                "language": "语言",
                "theme": "主题",
                "light": "浅色",
                "dark": "深色",
                "auto": "自动",
                "about": "关于",
                "help": "帮助",
                "logout": "退出登录",
                "exit": "退出系统",
                "restart": "重启系统",
                "update": "检查更新",
                "backup": "备份数据",
                "restore": "恢复数据"
            }
        }
    
    def save_translations(self, lang_code=None):
        """
        保存翻译文件
        
        Args:
            lang_code (str, optional): 语言代码，如果为None则保存所有语言
            
        Returns:
            bool: 是否成功保存
        """
        try:
            # 确保翻译文件目录存在
            ensure_dir(self.translations_dir)
            
            # 如果指定了语言代码，只保存该语言的翻译文件
            if lang_code is not None:
                if lang_code not in SUPPORTED_LANGUAGES:
                    logger.error(f"不支持的语言: {lang_code}")
                    return False
                
                lang_file = os.path.join(self.translations_dir, f"{lang_code}.json")
                return write_json_file(lang_file, self.translations[lang_code])
            
            # 保存所有语言的翻译文件
            success = True
            for lang_code in SUPPORTED_LANGUAGES:
                lang_file = os.path.join(self.translations_dir, f"{lang_code}.json")
                if not write_json_file(lang_file, self.translations[lang_code]):
                    success = False
            
            return success
        except Exception as e:
            logger.error(f"保存翻译文件失败: {str(e)}")
            return False
    
    def set_language(self, language):
        """
        设置语言
        
        Args:
            language (str): 语言代码
            
        Returns:
            bool: 是否成功设置
        """
        # 检查语言是否受支持
        if language not in SUPPORTED_LANGUAGES:
            logger.error(f"不支持的语言: {language}")
            return False
        
        # 设置语言
        self.language = language
        
        # 设置系统语言环境
        try:
            locale_code = SUPPORTED_LANGUAGES[language]["locale"]
            locale.setlocale(locale.LC_ALL, locale_code)
        except Exception as e:
            logger.warning(f"设置系统语言环境失败: {str(e)}")
        
        return True
    
    def get_language(self):
        """
        获取当前语言
        
        Returns:
            str: 语言代码
        """
        return self.language
    
    def get_language_name(self, language=None):
        """
        获取语言名称
        
        Args:
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            str: 语言名称
        """
        if language is None:
            language = self.language
        
        if language not in SUPPORTED_LANGUAGES:
            return "Unknown"
        
        return SUPPORTED_LANGUAGES[language]["name"]
    
    def get_supported_languages(self):
        """
        获取支持的语言列表
        
        Returns:
            dict: 支持的语言列表
        """
        return SUPPORTED_LANGUAGES
    
    def translate(self, key, default=None, language=None):
        """
        翻译文本
        
        Args:
            key (str): 翻译键，格式为"section.key"，例如"common.ok"
            default (str, optional): 默认文本，如果翻译不存在则返回该文本
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            str: 翻译后的文本
        """
        if language is None:
            language = self.language
        
        # 检查语言是否受支持
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE
        
        # 解析翻译键
        parts = key.split(".")
        if len(parts) != 2:
            logger.warning(f"无效的翻译键: {key}")
            return default if default is not None else key
        
        section, subkey = parts
        
        # 获取翻译
        try:
            # 检查指定语言的翻译是否存在
            if section in self.translations[language] and subkey in self.translations[language][section]:
                return self.translations[language][section][subkey]
            
            # 如果指定语言的翻译不存在，尝试使用默认语言的翻译
            if language != DEFAULT_LANGUAGE:
                if section in self.translations[DEFAULT_LANGUAGE] and subkey in self.translations[DEFAULT_LANGUAGE][section]:
                    return self.translations[DEFAULT_LANGUAGE][section][subkey]
        except Exception as e:
            logger.error(f"获取翻译失败: {key}, 错误: {str(e)}")
        
        # 如果翻译不存在，返回默认文本或翻译键
        return default if default is not None else key
    
    def add_translation(self, section, key, value, language=None):
        """
        添加翻译
        
        Args:
            section (str): 翻译部分
            key (str): 翻译键
            value (str): 翻译值
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            bool: 是否成功添加
        """
        if language is None:
            language = self.language
        
        # 检查语言是否受支持
        if language not in SUPPORTED_LANGUAGES:
            logger.error(f"不支持的语言: {language}")
            return False
        
        try:
            # 如果翻译部分不存在，创建新部分
            if section not in self.translations[language]:
                self.translations[language][section] = {}
            
            # 添加翻译
            self.translations[language][section][key] = value
            
            # 保存翻译文件
            return self.save_translations(language)
        except Exception as e:
            logger.error(f"添加翻译失败: {section}.{key}, 错误: {str(e)}")
            return False
    
    def update_translation(self, section, key, value, language=None):
        """
        更新翻译
        
        Args:
            section (str): 翻译部分
            key (str): 翻译键
            value (str): 翻译值
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            bool: 是否成功更新
        """
        return self.add_translation(section, key, value, language)
    
    def delete_translation(self, section, key, language=None):
        """
        删除翻译
        
        Args:
            section (str): 翻译部分
            key (str): 翻译键
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            bool: 是否成功删除
        """
        if language is None:
            language = self.language
        
        # 检查语言是否受支持
        if language not in SUPPORTED_LANGUAGES:
            logger.error(f"不支持的语言: {language}")
            return False
        
        try:
            # 检查翻译是否存在
            if section not in self.translations[language] or key not in self.translations[language][section]:
                logger.warning(f"翻译不存在: {section}.{key}")
                return False
            
            # 删除翻译
            del self.translations[language][section][key]
            
            # 如果翻译部分为空，删除该部分
            if not self.translations[language][section]:
                del self.translations[language][section]
            
            # 保存翻译文件
            return self.save_translations(language)
        except Exception as e:
            logger.error(f"删除翻译失败: {section}.{key}, 错误: {str(e)}")
            return False
    
    def import_translations(self, file_path, language=None):
        """
        导入翻译
        
        Args:
            file_path (str): 翻译文件路径
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            bool: 是否成功导入
        """
        if language is None:
            language = self.language
        
        # 检查语言是否受支持
        if language not in SUPPORTED_LANGUAGES:
            logger.error(f"不支持的语言: {language}")
            return False
        
        try:
            # 加载翻译文件
            translations = read_json_file(file_path)
            if translations is None:
                logger.error(f"加载翻译文件失败: {file_path}")
                return False
            
            # 更新翻译
            self.translations[language] = translations
            
            # 保存翻译文件
            return self.save_translations(language)
        except Exception as e:
            logger.error(f"导入翻译失败: {file_path}, 错误: {str(e)}")
            return False
    
    def export_translations(self, file_path, language=None):
        """
        导出翻译
        
        Args:
            file_path (str): 翻译文件路径
            language (str, optional): 语言代码，如果为None则使用当前语言
            
        Returns:
            bool: 是否成功导出
        """
        if language is None:
            language = self.language
        
        # 检查语言是否受支持
        if language not in SUPPORTED_LANGUAGES:
            logger.error(f"不支持的语言: {language}")
            return False
        
        try:
            # 确保输出目录存在
            ensure_dir(os.path.dirname(file_path))
            
            # 导出翻译
            return write_json_file(file_path, self.translations[language])
        except Exception as e:
            logger.error(f"导出翻译失败: {file_path}, 错误: {str(e)}")
            return False


# 创建全局国际化管理器实例
_i18n_manager = None


def get_i18n_manager(language=None):
    """
    获取国际化管理器实例
    
    Args:
        language (str, optional): 语言代码
        
    Returns:
        I18nManager: 国际化管理器实例
    """
    global _i18n_manager
    
    if _i18n_manager is None:
        _i18n_manager = I18nManager(language)
    elif language is not None and language != _i18n_manager.get_language():
        _i18n_manager.set_language(language)
    
    return _i18n_manager


@lru_cache(maxsize=1024)
def _(key, default=None, language=None):
    """
    翻译文本的快捷函数
    
    Args:
        key (str): 翻译键，格式为"section.key"，例如"common.ok"
        default (str, optional): 默认文本，如果翻译不存在则返回该文本
        language (str, optional): 语言代码
        
    Returns:
        str: 翻译后的文本
    """
    i18n_manager = get_i18n_manager()
    return i18n_manager.translate(key, default, language)


if __name__ == "__main__":
    # 测试国际化管理器
    i18n_manager = get_i18n_manager()
    
    # 获取当前语言
    current_language = i18n_manager.get_language()
    print(f"当前语言: {current_language} ({i18n_manager.get_language_name()})")
    
    # 获取支持的语言列表
    supported_languages = i18n_manager.get_supported_languages()
    print("支持的语言:")
    for lang_code, lang_info in supported_languages.items():
        print(f"  {lang_code}: {lang_info['name']}")
    
    # 测试翻译
    print("\n翻译测试:")
    key1 = "common.ok"
    key2 = "login.title"
    key3 = "main_console.title"
    print(f"common.ok: {_(key1)}")
    print(f"login.title: {_(key2)}")
    print(f"main_console.title: {_(key3)}")
    
    # 测试不存在的翻译
    key4 = "test.not_exist"
    default_text = "默认文本"
    print(f"不存在的翻译: {_(key4, default_text)}")
    
    # 测试切换语言
    if "en_US" in supported_languages:
        i18n_manager.set_language("en_US")
        print(f"\n切换语言到: {i18n_manager.get_language()} ({i18n_manager.get_language_name()})")
        
        # 添加英文翻译
        i18n_manager.add_translation("common", "ok", "OK")
        i18n_manager.add_translation("login", "title", "Login")
        i18n_manager.add_translation("main_console", "title", "Main Console")
        
        # 测试翻译
        print("翻译测试:")
        print(f"common.ok: {_(key1)}")
        print(f"login.title: {_(key2)}")
        print(f"main_console.title: {_(key3)}")
        
        # 切换回原语言
        i18n_manager.set_language(current_language)
        print(f"\n切换回语言: {i18n_manager.get_language()} ({i18n_manager.get_language_name()})")
        print(f"common.ok: {_(key1)}")