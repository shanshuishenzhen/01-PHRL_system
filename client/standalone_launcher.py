#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客户端独立启动器
允许客户端模块独立运行，无需通过主启动器
"""

import os
import sys
import json
import logging
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

def setup_environment():
    """设置运行环境"""
    
    # 确保必要的目录存在
    dirs_to_create = [
        project_root / "logs",
        project_root / "data", 
        project_root / "temp",
        project_root / "exam_management" / "results",
        project_root / "grading_center" / "queue",
        project_root / "grading_center" / "graded"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    log_file = project_root / "logs" / "client_standalone.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger('client_standalone')
    logger.info("客户端独立启动器初始化完成")
    
    return logger

def check_dependencies():
    """检查必要的依赖"""
    logger = logging.getLogger('client_standalone')
    
    # 检查关键依赖
    dependencies = {
        "tkinter": "tkinter",
        "json": "json", 
        "os": "os",
        "sys": "sys"
    }
    
    missing_deps = []
    
    for dep_name, import_name in dependencies.items():
        try:
            __import__(import_name)
            logger.debug(f"依赖检查通过: {dep_name}")
        except ImportError:
            logger.error(f"依赖检查失败: {dep_name}")
            missing_deps.append(dep_name)
    
    if missing_deps:
        logger.error(f"缺少必要依赖: {', '.join(missing_deps)}")
        return False
    
    logger.info("所有必要依赖检查通过")
    return True

def check_data_files():
    """检查必要的数据文件"""
    logger = logging.getLogger('client_standalone')
    
    # 检查必要的数据文件
    required_files = [
        project_root / "client" / "config" / "client_config.json",
        project_root / "client" / "available_exams.json"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
            logger.warning(f"数据文件不存在: {file_path}")
        else:
            logger.debug(f"数据文件检查通过: {file_path}")
    
    # 如果缺少考试列表文件，创建一个空的
    exam_list_file = project_root / "client" / "available_exams.json"
    if not exam_list_file.exists():
        logger.info("创建空的考试列表文件")
        try:
            with open(exam_list_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            logger.info(f"已创建空的考试列表文件: {exam_list_file}")
        except Exception as e:
            logger.error(f"创建考试列表文件失败: {e}")
    
    # 检查配置文件
    config_file = project_root / "client" / "config" / "client_config.json"
    if not config_file.exists():
        logger.info("创建默认客户端配置文件")
        try:
            config_dir = config_file.parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            default_config = {
                "app_name": "PH&RL考试客户端",
                "version": "1.0.0",
                "api_base_url": "http://localhost:5000",
                "auto_save_interval": 30,
                "theme": "default",
                "language": "zh_CN",
                "debug": False
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logger.info(f"已创建默认配置文件: {config_file}")
        except Exception as e:
            logger.error(f"创建配置文件失败: {e}")
    
    return len(missing_files) == 0

def main():
    """主函数"""
    print("PH&RL 客户端独立启动器")
    print("=" * 50)

    # 设置独立运行模式环境变量
    os.environ['PHRL_STANDALONE_MODE'] = 'true'

    # 设置环境
    logger = setup_environment()
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，无法启动客户端")
        sys.exit(1)
    
    # 检查数据文件
    if not check_data_files():
        logger.warning("部分数据文件缺失，但将尝试继续启动")
    
    # 启动客户端应用
    try:
        logger.info("正在启动客户端应用...")
        print("正在启动客户端应用...")
        
        # 导入并启动客户端应用
        import client_app
        
        # 如果client_app有main函数，调用它
        if hasattr(client_app, 'main'):
            client_app.main()
        else:
            # 否则直接运行模块
            logger.info("客户端应用已启动")
            print("✅ 客户端应用已启动")
            
    except ImportError as e:
        logger.error(f"无法导入客户端应用: {e}")
        print(f"❌ 无法导入客户端应用: {e}")
        print("请确保客户端应用文件存在且可访问")
        sys.exit(1)
    except Exception as e:
        logger.error(f"启动客户端应用时发生错误: {e}")
        print(f"❌ 启动客户端应用时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
