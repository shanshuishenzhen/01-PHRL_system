"""
公共模块单元测试

测试common目录下的各个模块功能。
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# 导入被测试的模块
try:
    from common.config_manager import ConfigManager, load_config, save_config
    from common.data_manager import load_json_data, save_json_data, ensure_dir
    from common.logger import setup_logger, get_logger
    from common.system_checker import check_python_version, check_disk_space
except ImportError as e:
    pytest.skip(f"无法导入common模块: {e}", allow_module_level=True)


class TestConfigManager:
    """配置管理器测试"""
    
    @pytest.fixture
    def sample_config(self):
        """示例配置数据"""
        return {
            "version": "1.0.0",
            "module_ports": {
                "question_bank": 5000,
                "grading_center": 3000
            },
            "logging": {
                "level": "INFO"
            }
        }
    
    @pytest.fixture
    def config_file(self, temp_dir, sample_config):
        """临时配置文件"""
        config_path = temp_dir / "config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f)
        return config_path
    
    def test_load_config_success(self, config_file, sample_config):
        """测试成功加载配置"""
        with patch('common.config_manager.CONFIG_FILE', str(config_file)):
            config = load_config()
            assert config == sample_config
    
    def test_load_config_file_not_found(self, temp_dir):
        """测试配置文件不存在"""
        non_existent_file = temp_dir / "non_existent.json"
        with patch('common.config_manager.CONFIG_FILE', str(non_existent_file)):
            config = load_config()
            assert isinstance(config, dict)
            assert "version" in config
    
    def test_save_config_success(self, temp_dir, sample_config):
        """测试成功保存配置"""
        config_path = temp_dir / "test_config.json"
        with patch('common.config_manager.CONFIG_FILE', str(config_path)):
            result = save_config(sample_config)
            assert result is True
            assert config_path.exists()
            
            # 验证保存的内容
            with open(config_path, 'r', encoding='utf-8') as f:
                saved_config = json.load(f)
            assert saved_config == sample_config
    
    def test_config_manager_get(self, config_file, sample_config):
        """测试ConfigManager的get方法"""
        with patch('common.config_manager.CONFIG_FILE', str(config_file)):
            manager = ConfigManager()
            
            # 测试获取整个配置
            assert manager.get() == sample_config
            
            # 测试获取特定键
            assert manager.get("version") == "1.0.0"
            assert manager.get("module_ports") == sample_config["module_ports"]
            
            # 测试获取不存在的键
            assert manager.get("non_existent") is None
            assert manager.get("non_existent", "default") == "default"
    
    def test_config_manager_set(self, config_file):
        """测试ConfigManager的set方法"""
        with patch('common.config_manager.CONFIG_FILE', str(config_file)):
            manager = ConfigManager()
            
            # 设置新值
            manager.set("new_key", "new_value")
            assert manager.get("new_key") == "new_value"
            
            # 修改现有值
            manager.set("version", "2.0.0")
            assert manager.get("version") == "2.0.0"


class TestDataManager:
    """数据管理器测试"""
    
    def test_load_json_data_success(self, temp_dir):
        """测试成功加载JSON数据"""
        test_data = {"key": "value", "number": 123}
        json_file = temp_dir / "test.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        loaded_data = load_json_data(str(json_file))
        assert loaded_data == test_data
    
    def test_load_json_data_file_not_found(self, temp_dir):
        """测试加载不存在的JSON文件"""
        non_existent_file = temp_dir / "non_existent.json"
        result = load_json_data(str(non_existent_file))
        assert result is None
    
    def test_load_json_data_invalid_json(self, temp_dir):
        """测试加载无效的JSON文件"""
        invalid_json_file = temp_dir / "invalid.json"
        invalid_json_file.write_text("invalid json content", encoding='utf-8')
        
        result = load_json_data(str(invalid_json_file))
        assert result is None
    
    def test_save_json_data_success(self, temp_dir):
        """测试成功保存JSON数据"""
        test_data = {"key": "value", "list": [1, 2, 3]}
        json_file = temp_dir / "output.json"
        
        result = save_json_data(str(json_file), test_data)
        assert result is True
        assert json_file.exists()
        
        # 验证保存的内容
        with open(json_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        assert saved_data == test_data
    
    def test_save_json_data_create_directory(self, temp_dir):
        """测试保存JSON数据时创建目录"""
        test_data = {"test": True}
        json_file = temp_dir / "subdir" / "test.json"
        
        result = save_json_data(str(json_file), test_data)
        assert result is True
        assert json_file.exists()
        assert json_file.parent.exists()
    
    def test_ensure_dir_success(self, temp_dir):
        """测试确保目录存在"""
        new_dir = temp_dir / "new_directory"
        assert not new_dir.exists()
        
        result = ensure_dir(str(new_dir))
        assert result is True
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_ensure_dir_already_exists(self, temp_dir):
        """测试确保已存在的目录"""
        result = ensure_dir(str(temp_dir))
        assert result is True
        assert temp_dir.exists()


class TestLogger:
    """日志器测试"""
    
    def test_setup_logger(self, temp_dir):
        """测试设置日志器"""
        log_file = temp_dir / "test.log"
        logger = setup_logger("test_logger", str(log_file))
        
        assert logger.name == "test_logger"
        
        # 测试日志记录
        logger.info("Test message")
        assert log_file.exists()
    
    def test_get_logger(self):
        """测试获取日志器"""
        logger1 = get_logger("test_logger")
        logger2 = get_logger("test_logger")
        
        # 应该返回同一个logger实例
        assert logger1 is logger2
    
    @patch('common.logger.logging.getLogger')
    def test_get_logger_with_mock(self, mock_get_logger):
        """测试使用mock的日志器获取"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        logger = get_logger("test")
        assert logger is mock_logger
        mock_get_logger.assert_called_once_with("test")


class TestSystemChecker:
    """系统检查器测试"""
    
    def test_check_python_version_success(self):
        """测试Python版本检查成功"""
        # 当前Python版本应该满足最低要求
        result = check_python_version([3, 6])
        assert result is True
    
    def test_check_python_version_failure(self):
        """测试Python版本检查失败"""
        # 设置一个不可能满足的版本要求
        result = check_python_version([99, 0])
        assert result is False
    
    @patch('common.system_checker.shutil.disk_usage')
    def test_check_disk_space_success(self, mock_disk_usage):
        """测试磁盘空间检查成功"""
        # 模拟有足够的磁盘空间
        mock_disk_usage.return_value = (1000000000, 500000000, 500000000)  # total, used, free
        
        result = check_disk_space(100)  # 需要100MB
        assert result is True
    
    @patch('common.system_checker.shutil.disk_usage')
    def test_check_disk_space_failure(self, mock_disk_usage):
        """测试磁盘空间检查失败"""
        # 模拟磁盘空间不足
        mock_disk_usage.return_value = (1000000, 900000, 100000)  # total, used, free
        
        result = check_disk_space(1000)  # 需要1000MB，但只有约0.1MB可用
        assert result is False
    
    @patch('common.system_checker.shutil.disk_usage')
    def test_check_disk_space_exception(self, mock_disk_usage):
        """测试磁盘空间检查异常"""
        mock_disk_usage.side_effect = OSError("Disk error")
        
        result = check_disk_space(100)
        assert result is False


@pytest.mark.unit
@pytest.mark.fast
class TestCommonIntegration:
    """公共模块集成测试"""
    
    def test_config_and_logger_integration(self, temp_dir):
        """测试配置管理器和日志器的集成"""
        # 创建配置文件
        config_data = {
            "logging": {
                "level": "DEBUG",
                "max_file_size_mb": 10
            }
        }
        config_file = temp_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)
        
        # 使用配置设置日志器
        with patch('common.config_manager.CONFIG_FILE', str(config_file)):
            config = load_config()
            log_file = temp_dir / "app.log"
            logger = setup_logger("app", str(log_file))
            
            logger.info("Test integration message")
            assert log_file.exists()
    
    def test_data_manager_and_config_integration(self, temp_dir):
        """测试数据管理器和配置管理器的集成"""
        # 使用数据管理器保存配置
        config_data = {"test": "integration"}
        config_file = temp_dir / "integration_config.json"
        
        save_result = save_json_data(str(config_file), config_data)
        assert save_result is True
        
        # 使用配置管理器加载
        with patch('common.config_manager.CONFIG_FILE', str(config_file)):
            loaded_config = load_config()
            assert loaded_config == config_data
