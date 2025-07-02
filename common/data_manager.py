# -*- coding: utf-8 -*-
"""
数据管理工具模块

提供数据导入、导出和转换功能，支持JSON、CSV、Excel等格式。

更新日志：
- 2024-06-25：初始版本，提供基本数据管理功能
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime

# 导入项目模块
sys.path.append(str(Path(__file__).parent.parent))
from common.logger import get_logger
from common.file_manager import ensure_dir, backup_file

# 创建日志记录器
logger = get_logger("data_manager", os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "data_manager.log"))

# 尝试导入可选模块，使用安全导入
try:
    # 使用安全导入避免numpy冲突
    from common.numpy_fix import NumpyImportFixer
    fixer = NumpyImportFixer()
    pd = fixer.safe_import_pandas()
    HAS_PANDAS = True
except ImportError:
    try:
        import pandas as pd
        HAS_PANDAS = True
    except ImportError:
        HAS_PANDAS = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# 导入安全工具
try:
    from common.sql_security import ParameterizedQuery, InputValidator
    HAS_SQL_SECURITY = True
except ImportError:
    HAS_SQL_SECURITY = False

# 导入错误处理
try:
    from common.error_handler import handle_error, retry, safe_call
    HAS_ERROR_HANDLER = True
except ImportError:
    HAS_ERROR_HANDLER = False


def load_json_data(file_path, encoding="utf-8"):
    """
    加载JSON数据
    
    Args:
        file_path (str): 文件路径
        encoding (str, optional): 文件编码
        
    Returns:
        dict: JSON数据，如果加载失败则返回None
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载JSON数据失败: {file_path}, 错误: {str(e)}")
        return None


def save_json_data(file_path, data, encoding="utf-8", indent=4, backup=False):
    """
    保存JSON数据
    
    Args:
        file_path (str): 文件路径
        data (dict): JSON数据
        encoding (str, optional): 文件编码
        indent (int, optional): 缩进空格数
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功保存
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(file_path):
            backup_file(file_path)
        
        # 保存数据
        with open(file_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        logger.info(f"JSON数据已保存: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存JSON数据失败: {file_path}, 错误: {str(e)}")
        return False


def load_csv_data(file_path, encoding="utf-8", delimiter=",", has_header=True):
    """
    加载CSV数据
    
    Args:
        file_path (str): 文件路径
        encoding (str, optional): 文件编码
        delimiter (str, optional): 分隔符
        has_header (bool, optional): 是否有表头
        
    Returns:
        list: CSV数据，如果加载失败则返回None
    """
    try:
        data = []
        with open(file_path, "r", encoding=encoding, newline="") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                data.append(row)
        
        # 如果有表头，将第一行作为表头
        if has_header and len(data) > 0:
            header = data[0]
            rows = data[1:]
            return {"header": header, "rows": rows}
        else:
            return {"header": None, "rows": data}
    except Exception as e:
        logger.error(f"加载CSV数据失败: {file_path}, 错误: {str(e)}")
        return None


def save_csv_data(file_path, data, encoding="utf-8", delimiter=",", backup=False):
    """
    保存CSV数据
    
    Args:
        file_path (str): 文件路径
        data (dict): CSV数据，包含header和rows
        encoding (str, optional): 文件编码
        delimiter (str, optional): 分隔符
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功保存
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(file_path):
            backup_file(file_path)
        
        # 保存数据
        with open(file_path, "w", encoding=encoding, newline="") as f:
            writer = csv.writer(f, delimiter=delimiter)
            
            # 如果有表头，先写入表头
            if "header" in data and data["header"]:
                writer.writerow(data["header"])
            
            # 写入数据行
            if "rows" in data and data["rows"]:
                writer.writerows(data["rows"])
        
        logger.info(f"CSV数据已保存: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存CSV数据失败: {file_path}, 错误: {str(e)}")
        return False


def load_excel_data(file_path, sheet_name=0):
    """
    加载Excel数据
    
    Args:
        file_path (str): 文件路径
        sheet_name (str or int, optional): 工作表名称或索引
        
    Returns:
        dict: Excel数据，如果加载失败则返回None
    """
    if not HAS_PANDAS or not HAS_OPENPYXL:
        logger.error("加载Excel数据失败: 缺少pandas或openpyxl模块")
        return None
    
    try:
        # 使用pandas读取Excel文件
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # 转换为字典格式
        header = df.columns.tolist()
        rows = df.values.tolist()
        
        return {"header": header, "rows": rows}
    except Exception as e:
        logger.error(f"加载Excel数据失败: {file_path}, 错误: {str(e)}")
        return None


def save_excel_data(file_path, data, sheet_name="Sheet1", backup=False):
    """
    保存Excel数据
    
    Args:
        file_path (str): 文件路径
        data (dict): Excel数据，包含header和rows
        sheet_name (str, optional): 工作表名称
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功保存
    """
    if not HAS_PANDAS or not HAS_OPENPYXL:
        logger.error("保存Excel数据失败: 缺少pandas或openpyxl模块")
        return False
    
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(file_path):
            backup_file(file_path)
        
        # 创建DataFrame
        if "header" in data and data["header"] and "rows" in data and data["rows"]:
            df = pd.DataFrame(data["rows"], columns=data["header"])
        elif "rows" in data and data["rows"]:
            df = pd.DataFrame(data["rows"])
        else:
            df = pd.DataFrame()
        
        # 保存到Excel文件
        df.to_excel(file_path, sheet_name=sheet_name, index=False)
        
        logger.info(f"Excel数据已保存: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存Excel数据失败: {file_path}, 错误: {str(e)}")
        return False


def convert_json_to_csv(json_data, csv_file_path, encoding="utf-8", delimiter=",", backup=False):
    """
    将JSON数据转换为CSV文件
    
    Args:
        json_data (dict or list): JSON数据
        csv_file_path (str): CSV文件路径
        encoding (str, optional): 文件编码
        delimiter (str, optional): 分隔符
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功转换
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(csv_file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(csv_file_path):
            backup_file(csv_file_path)
        
        # 如果JSON数据是列表
        if isinstance(json_data, list) and len(json_data) > 0:
            # 如果列表元素是字典，提取键作为表头
            if isinstance(json_data[0], dict):
                header = list(json_data[0].keys())
                rows = []
                for item in json_data:
                    row = [item.get(key, "") for key in header]
                    rows.append(row)
                
                # 保存CSV数据
                return save_csv_data(csv_file_path, {"header": header, "rows": rows}, encoding, delimiter)
            # 如果列表元素不是字典，直接保存为CSV
            else:
                return save_csv_data(csv_file_path, {"header": None, "rows": json_data}, encoding, delimiter)
        # 如果JSON数据是字典
        elif isinstance(json_data, dict):
            # 如果字典值是列表，提取键作为表头
            if any(isinstance(value, list) for value in json_data.values()):
                # 找到第一个列表值
                for key, value in json_data.items():
                    if isinstance(value, list):
                        # 保存CSV数据
                        return save_csv_data(csv_file_path, {"header": [key], "rows": [[item] for item in value]}, encoding, delimiter)
            # 如果字典值不是列表，将键值对保存为CSV
            else:
                header = ["key", "value"]
                rows = [[key, value] for key, value in json_data.items()]
                return save_csv_data(csv_file_path, {"header": header, "rows": rows}, encoding, delimiter)
        
        logger.error(f"转换JSON到CSV失败: 不支持的JSON数据格式")
        return False
    except Exception as e:
        logger.error(f"转换JSON到CSV失败: {csv_file_path}, 错误: {str(e)}")
        return False


def convert_csv_to_json(csv_data, json_file_path, encoding="utf-8", indent=4, backup=False):
    """
    将CSV数据转换为JSON文件
    
    Args:
        csv_data (dict): CSV数据，包含header和rows
        json_file_path (str): JSON文件路径
        encoding (str, optional): 文件编码
        indent (int, optional): 缩进空格数
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功转换
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(json_file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(json_file_path):
            backup_file(json_file_path)
        
        # 如果有表头，将每行数据转换为字典
        if "header" in csv_data and csv_data["header"] and "rows" in csv_data and csv_data["rows"]:
            header = csv_data["header"]
            rows = csv_data["rows"]
            
            json_data = []
            for row in rows:
                item = {}
                for i, key in enumerate(header):
                    if i < len(row):
                        item[key] = row[i]
                    else:
                        item[key] = ""
                json_data.append(item)
        # 如果没有表头，将每行数据作为列表元素
        elif "rows" in csv_data and csv_data["rows"]:
            json_data = csv_data["rows"]
        else:
            json_data = []
        
        # 保存JSON数据
        return save_json_data(json_file_path, json_data, encoding, indent)
    except Exception as e:
        logger.error(f"转换CSV到JSON失败: {json_file_path}, 错误: {str(e)}")
        return False


def convert_excel_to_json(excel_data, json_file_path, encoding="utf-8", indent=4, backup=False):
    """
    将Excel数据转换为JSON文件
    
    Args:
        excel_data (dict): Excel数据，包含header和rows
        json_file_path (str): JSON文件路径
        encoding (str, optional): 文件编码
        indent (int, optional): 缩进空格数
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功转换
    """
    # Excel数据格式与CSV数据格式相同，可以直接调用convert_csv_to_json
    return convert_csv_to_json(excel_data, json_file_path, encoding, indent, backup)


def convert_json_to_excel(json_data, excel_file_path, sheet_name="Sheet1", backup=False):
    """
    将JSON数据转换为Excel文件
    
    Args:
        json_data (dict or list): JSON数据
        excel_file_path (str): Excel文件路径
        sheet_name (str, optional): 工作表名称
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功转换
    """
    if not HAS_PANDAS or not HAS_OPENPYXL:
        logger.error("转换JSON到Excel失败: 缺少pandas或openpyxl模块")
        return False
    
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(excel_file_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(excel_file_path):
            backup_file(excel_file_path)
        
        # 如果JSON数据是列表
        if isinstance(json_data, list) and len(json_data) > 0:
            # 如果列表元素是字典，提取键作为表头
            if isinstance(json_data[0], dict):
                # 创建DataFrame
                df = pd.DataFrame(json_data)
            # 如果列表元素不是字典，直接创建DataFrame
            else:
                df = pd.DataFrame(json_data)
        # 如果JSON数据是字典
        elif isinstance(json_data, dict):
            # 创建DataFrame
            df = pd.DataFrame([json_data])
        else:
            logger.error(f"转换JSON到Excel失败: 不支持的JSON数据格式")
            return False
        
        # 保存到Excel文件
        df.to_excel(excel_file_path, sheet_name=sheet_name, index=False)
        
        logger.info(f"JSON数据已转换为Excel: {excel_file_path}")
        return True
    except Exception as e:
        logger.error(f"转换JSON到Excel失败: {excel_file_path}, 错误: {str(e)}")
        return False


def merge_json_files(file_paths, output_path, encoding="utf-8", indent=4, backup=False):
    """
    合并多个JSON文件
    
    Args:
        file_paths (list): JSON文件路径列表
        output_path (str): 输出文件路径
        encoding (str, optional): 文件编码
        indent (int, optional): 缩进空格数
        backup (bool, optional): 是否备份原文件
        
    Returns:
        bool: 是否成功合并
    """
    try:
        # 确保目录存在
        ensure_dir(os.path.dirname(output_path))
        
        # 如果需要备份且文件存在，创建备份
        if backup and os.path.exists(output_path):
            backup_file(output_path)
        
        # 加载所有JSON文件
        merged_data = []
        for file_path in file_paths:
            data = load_json_data(file_path, encoding)
            if data is None:
                continue
            
            # 如果数据是列表，扩展合并数据
            if isinstance(data, list):
                merged_data.extend(data)
            # 如果数据是字典，添加到合并数据
            elif isinstance(data, dict):
                merged_data.append(data)
        
        # 保存合并后的数据
        return save_json_data(output_path, merged_data, encoding, indent)
    except Exception as e:
        logger.error(f"合并JSON文件失败: {output_path}, 错误: {str(e)}")
        return False


def filter_json_data(data, filter_func):
    """
    过滤JSON数据
    
    Args:
        data (dict or list): JSON数据
        filter_func (callable): 过滤函数，接受一个参数（数据项），返回布尔值
        
    Returns:
        dict or list: 过滤后的数据
    """
    try:
        # 如果数据是列表
        if isinstance(data, list):
            return [item for item in data if filter_func(item)]
        # 如果数据是字典
        elif isinstance(data, dict):
            return {key: value for key, value in data.items() if filter_func((key, value))}
        else:
            return data
    except Exception as e:
        logger.error(f"过滤JSON数据失败: {str(e)}")
        return data


def sort_json_data(data, key_func, reverse=False):
    """
    排序JSON数据
    
    Args:
        data (list): JSON数据列表
        key_func (callable): 排序键函数，接受一个参数（数据项），返回排序键
        reverse (bool, optional): 是否降序排序
        
    Returns:
        list: 排序后的数据
    """
    try:
        # 如果数据是列表
        if isinstance(data, list):
            return sorted(data, key=key_func, reverse=reverse)
        else:
            return data
    except Exception as e:
        logger.error(f"排序JSON数据失败: {str(e)}")
        return data


if __name__ == "__main__":
    # 测试数据管理功能
    project_root = Path(__file__).parent.parent
    test_dir = os.path.join(project_root, "test_dir")
    ensure_dir(test_dir)
    
    # 测试JSON数据保存和加载
    test_json = os.path.join(test_dir, "test_data.json")
    test_data = [
        {"id": 1, "name": "张三", "age": 25, "score": 85},
        {"id": 2, "name": "李四", "age": 22, "score": 92},
        {"id": 3, "name": "王五", "age": 28, "score": 78}
    ]
    
    if save_json_data(test_json, test_data):
        print(f"JSON数据已保存: {test_json}")
    
    loaded_data = load_json_data(test_json)
    if loaded_data:
        print(f"加载的JSON数据: {loaded_data}")
    
    # 测试CSV数据转换
    test_csv = os.path.join(test_dir, "test_data.csv")
    if convert_json_to_csv(test_data, test_csv):
        print(f"JSON数据已转换为CSV: {test_csv}")
    
    csv_data = load_csv_data(test_csv)
    if csv_data:
        print(f"加载的CSV数据: {csv_data}")
    
    # 测试Excel数据转换（如果有pandas和openpyxl）
    if HAS_PANDAS and HAS_OPENPYXL:
        test_excel = os.path.join(test_dir, "test_data.xlsx")
        if convert_json_to_excel(test_data, test_excel):
            print(f"JSON数据已转换为Excel: {test_excel}")
        
        excel_data = load_excel_data(test_excel)
        if excel_data:
            print(f"加载的Excel数据: {excel_data}")
    
    # 测试数据过滤和排序
    filtered_data = filter_json_data(test_data, lambda item: item["age"] > 22)
    print(f"过滤后的数据（年龄 > 22）: {filtered_data}")
    
    sorted_data = sort_json_data(test_data, lambda item: item["score"], reverse=True)
    print(f"排序后的数据（按分数降序）: {sorted_data}")
    
    # 清理测试文件和目录
    try:
        os.remove(test_json)
        os.remove(test_csv)
        if HAS_PANDAS and HAS_OPENPYXL:
            os.remove(test_excel)
        os.rmdir(test_dir)
        print(f"测试目录已清理: {test_dir}")
    except:
        pass