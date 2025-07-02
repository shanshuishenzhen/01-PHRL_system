# -*- coding: utf-8 -*-
"""
文件管理工具模块

提供统一的文件和目录操作功能，包括文件读写、目录创建、文件备份等。

更新日志：
- 2024-06-25：初始版本，提供基本文件管理功能
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger

# 创建日志记录器
logger = get_logger("file_manager", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "file_manager.log"))


def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory (str): 目录路径
        
    Returns:
        bool: 是否成功创建或已存在
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败: {directory}, 错误: {str(e)}")
        return False


def get_project_root():
    """
    获取项目根目录
    
    Returns:
        Path: 项目根目录路径
    """
    return Path(__file__).parent.parent


def read_text_file(file_path, encoding="utf-8"):
    """
    读取文本文件
    
    Args:
        file_path (str): 文件路径
        encoding (str, optional): 文件编码
        
    Returns:
        str: 文件内容，如果读取失败则返回None
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件失败: {file_path}, 错误: {str(e)}")
        return None


def write_text_file(file_path, content, encoding="utf-8", backup=False):
    """
    写入文本文件
    
    Args:
        file_path (str): 文件路径
        content (str): 文件内容
        encoding (str, optional): 文件编码
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功写入
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(file_path):
            backup_file(file_path)
        
        # 写入文件
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        
        return True
    except Exception as e:
        logger.error(f"写入文件失败: {file_path}, 错误: {str(e)}")
        return False


def read_json_file(file_path, encoding="utf-8"):
    """
    读取JSON文件
    
    Args:
        file_path (str): 文件路径
        encoding (str, optional): 文件编码
        
    Returns:
        dict: JSON数据，如果读取失败则返回None
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取JSON文件失败: {file_path}, 错误: {str(e)}")
        return None


def write_json_file(file_path, data, encoding="utf-8", indent=4, backup=False):
    """
    写入JSON文件
    
    Args:
        file_path (str): 文件路径
        data (dict): JSON数据
        encoding (str, optional): 文件编码
        indent (int, optional): 缩进空格数
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功写入
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(file_path):
            backup_file(file_path)
        
        # 写入文件
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        return True
    except Exception as e:
        logger.error(f"写入JSON文件失败: {file_path}, 错误: {str(e)}")
        return False


def backup_file(file_path, backup_dir=None):
    """
    备份文件
    
    Args:
        file_path (str): 文件路径
        backup_dir (str, optional): 备份目录，如果为None则使用原目录下的backups子目录
        
    Returns:
        str: 备份文件路径，如果备份失败则返回None
    """
    try:
        # 如果文件不存在，无需备份
        if not os.path.exists(file_path):
            return None
        
        # 确定备份目录
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        
        # 确保备份目录存在
        ensure_dir(backup_dir)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(file_path)
        backup_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # 复制文件
        shutil.copy2(file_path, backup_path)
        
        logger.info(f"文件已备份: {file_path} -> {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"备份文件失败: {file_path}, 错误: {str(e)}")
        return None


def copy_file(src_path, dst_path, overwrite=False):
    """
    复制文件
    
    Args:
        src_path (str): 源文件路径
        dst_path (str): 目标文件路径
        overwrite (bool, optional): 是否覆盖已存在的文件
        
    Returns:
        bool: 是否成功复制
    """
    try:
        # 如果源文件不存在，复制失败
        if not os.path.exists(src_path):
            logger.error(f"源文件不存在: {src_path}")
            return False
        
        # 如果目标文件已存在且不允许覆盖，复制失败
        if os.path.exists(dst_path) and not overwrite:
            logger.error(f"目标文件已存在且不允许覆盖: {dst_path}")
            return False
        
        # 确保目标目录存在
        ensure_dir(os.path.dirname(dst_path))
        
        # 复制文件
        shutil.copy2(src_path, dst_path)
        
        logger.info(f"文件已复制: {src_path} -> {dst_path}")
        return True
    except Exception as e:
        logger.error(f"复制文件失败: {src_path} -> {dst_path}, 错误: {str(e)}")
        return False


def move_file(src_path, dst_path, overwrite=False):
    """
    移动文件
    
    Args:
        src_path (str): 源文件路径
        dst_path (str): 目标文件路径
        overwrite (bool, optional): 是否覆盖已存在的文件
        
    Returns:
        bool: 是否成功移动
    """
    try:
        # 如果源文件不存在，移动失败
        if not os.path.exists(src_path):
            logger.error(f"源文件不存在: {src_path}")
            return False
        
        # 如果目标文件已存在且不允许覆盖，移动失败
        if os.path.exists(dst_path) and not overwrite:
            logger.error(f"目标文件已存在且不允许覆盖: {dst_path}")
            return False
        
        # 确保目标目录存在
        ensure_dir(os.path.dirname(dst_path))
        
        # 移动文件
        shutil.move(src_path, dst_path)
        
        logger.info(f"文件已移动: {src_path} -> {dst_path}")
        return True
    except Exception as e:
        logger.error(f"移动文件失败: {src_path} -> {dst_path}, 错误: {str(e)}")
        return False


def delete_file(file_path, backup=False):
    """
    删除文件
    
    Args:
        file_path (str): 文件路径
        backup (bool, optional): 是否在删除前备份
        
    Returns:
        bool: 是否成功删除
    """
    try:
        # 如果文件不存在，删除成功
        if not os.path.exists(file_path):
            return True
        
        # 如果需要备份，创建备份
        if backup:
            backup_file(file_path)
        
        # 删除文件
        os.remove(file_path)
        
        logger.info(f"文件已删除: {file_path}")
        return True
    except Exception as e:
        logger.error(f"删除文件失败: {file_path}, 错误: {str(e)}")
        return False


def list_files(directory, pattern=None, recursive=False):
    """
    列出目录中的文件
    
    Args:
        directory (str): 目录路径
        pattern (str, optional): 文件名模式，支持通配符
        recursive (bool, optional): 是否递归查找子目录
        
    Returns:
        list: 文件路径列表
    """
    try:
        # 如果目录不存在，返回空列表
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return []
        
        # 列出文件
        if recursive:
            files = []
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            files = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        # 如果指定了模式，过滤文件
        if pattern:
            import fnmatch
            files = [f for f in files if fnmatch.fnmatch(os.path.basename(f), pattern)]
        
        return files
    except Exception as e:
        logger.error(f"列出文件失败: {directory}, 错误: {str(e)}")
        return []


def create_temp_file(prefix=None, suffix=None, content=None, encoding="utf-8"):
    """
    创建临时文件
    
    Args:
        prefix (str, optional): 文件名前缀
        suffix (str, optional): 文件名后缀
        content (str, optional): 文件内容
        encoding (str, optional): 文件编码
        
    Returns:
        str: 临时文件路径，如果创建失败则返回None
    """
    try:
        # 创建临时文件
        fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix)
        os.close(fd)
        
        # 如果指定了内容，写入文件
        if content is not None:
            with open(temp_path, "w", encoding=encoding) as f:
                f.write(content)
        
        logger.info(f"临时文件已创建: {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"创建临时文件失败, 错误: {str(e)}")
        return None


def create_temp_dir(prefix=None, suffix=None):
    """
    创建临时目录
    
    Args:
        prefix (str, optional): 目录名前缀
        suffix (str, optional): 目录名后缀
        
    Returns:
        str: 临时目录路径，如果创建失败则返回None
    """
    try:
        # 创建临时目录
        temp_dir = tempfile.mkdtemp(prefix=prefix, suffix=suffix)
        
        logger.info(f"临时目录已创建: {temp_dir}")
        return temp_dir
    except Exception as e:
        logger.error(f"创建临时目录失败, 错误: {str(e)}")
        return None


def get_file_size(file_path, unit="bytes"):
    """
    获取文件大小
    
    Args:
        file_path (str): 文件路径
        unit (str, optional): 大小单位，可选值有'bytes', 'kb', 'mb', 'gb'
        
    Returns:
        float: 文件大小，如果获取失败则返回None
    """
    try:
        # 如果文件不存在，返回None
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None
        
        # 获取文件大小（字节）
        size_bytes = os.path.getsize(file_path)
        
        # 根据单位转换
        if unit.lower() == "bytes":
            return size_bytes
        elif unit.lower() == "kb":
            return size_bytes / 1024
        elif unit.lower() == "mb":
            return size_bytes / (1024 * 1024)
        elif unit.lower() == "gb":
            return size_bytes / (1024 * 1024 * 1024)
        else:
            return size_bytes
    except Exception as e:
        logger.error(f"获取文件大小失败: {file_path}, 错误: {str(e)}")
        return None


def get_file_info(file_path):
    """
    获取文件信息
    
    Args:
        file_path (str): 文件路径
        
    Returns:
        dict: 文件信息，包括大小、修改时间等，如果获取失败则返回None
    """
    try:
        # 如果文件不存在，返回None
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None
        
        # 获取文件信息
        stat = os.stat(file_path)
        
        # 返回文件信息字典
        return {
            "path": file_path,
            "name": os.path.basename(file_path),
            "size_bytes": stat.st_size,
            "size_kb": stat.st_size / 1024,
            "size_mb": stat.st_size / (1024 * 1024),
            "created_time": datetime.fromtimestamp(stat.st_ctime),
            "modified_time": datetime.fromtimestamp(stat.st_mtime),
            "accessed_time": datetime.fromtimestamp(stat.st_atime),
            "extension": os.path.splitext(file_path)[1]
        }
    except Exception as e:
        logger.error(f"获取文件信息失败: {file_path}, 错误: {str(e)}")
        return None


if __name__ == "__main__":
    # 测试文件管理功能
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    
    # 测试目录创建
    test_dir = os.path.join(project_root, "test_dir")
    if ensure_dir(test_dir):
        print(f"目录已创建: {test_dir}")
    
    # 测试文件写入和读取
    test_file = os.path.join(test_dir, "test.txt")
    if write_text_file(test_file, "测试内容\n这是第二行"):
        print(f"文件已写入: {test_file}")
    
    content = read_text_file(test_file)
    if content:
        print(f"文件内容:\n{content}")
    
    # 测试JSON文件写入和读取
    test_json = os.path.join(test_dir, "test.json")
    test_data = {"name": "测试", "value": 123, "items": [1, 2, 3]}
    if write_json_file(test_json, test_data):
        print(f"JSON文件已写入: {test_json}")
    
    json_data = read_json_file(test_json)
    if json_data:
        print(f"JSON数据: {json_data}")
    
    # 测试文件备份
    backup_path = backup_file(test_file)
    if backup_path:
        print(f"文件已备份: {backup_path}")
    
    # 测试文件复制
    copy_path = os.path.join(test_dir, "test_copy.txt")
    if copy_file(test_file, copy_path):
        print(f"文件已复制: {copy_path}")
    
    # 测试文件信息获取
    file_info = get_file_info(test_file)
    if file_info:
        print(f"文件信息: {file_info['name']}, 大小: {file_info['size_kb']:.2f} KB, 修改时间: {file_info['modified_time']}")
    
    # 测试临时文件创建
    temp_file = create_temp_file(prefix="test_", suffix=".txt", content="临时文件内容")
    if temp_file:
        print(f"临时文件已创建: {temp_file}")
        delete_file(temp_file)
    
    # 清理测试文件和目录
    delete_file(test_file)
    delete_file(test_json)
    delete_file(copy_path)
    try:
        os.rmdir(os.path.join(test_dir, "backups"))
        os.rmdir(test_dir)
        print(f"测试目录已清理: {test_dir}")
    except:
        pass