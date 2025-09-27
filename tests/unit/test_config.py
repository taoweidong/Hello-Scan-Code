"""
配置系统测试

测试新的统一配置管理系统
"""

import pytest
import os
import tempfile
from unittest.mock import patch

from src.config import (
    AppConfig, LoggerConfig, DatabaseConfig, ConfigManager,
    get_config_manager, get_app_config, get_logger_config, get_database_config
)


class TestAppConfig:
    """应用配置测试"""
    
    def test_app_config_defaults(self):
        """测试默认配置值"""
        config = AppConfig()
        
        assert config.repo_path == "/root/CodeRootPath"
        assert config.search_term == "test,def,void"
        assert config.is_regex is False
        assert config.validate is False
        assert config.validate_workers == 4
        assert ".git" in config.ignore_dirs
        
    def test_app_config_env_loading(self):
        """测试环境变量加载"""
        with patch.dict(os.environ, {
            'REPO_PATH': '/custom/path',
            'SEARCH_TERM': 'custom_search',
            'IS_REGEX': 'true',
            'VALIDATE_WORKERS': '8'
        }):
            config = AppConfig()
            config.load_from_env()
            
            assert config.repo_path == '/custom/path'
            assert config.search_term == 'custom_search'
            assert config.is_regex is True
            assert config.validate_workers == 8
    
    def test_app_config_validation(self):
        """测试配置验证"""
        # 有效配置
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AppConfig(repo_path=temp_dir, search_term="test")
            assert config.validate() is True
        
        # 无效配置 - 路径不存在
        config = AppConfig(repo_path="/nonexistent/path")
        assert config.validate() is False
        
        # 无效配置 - 空搜索词
        config = AppConfig(search_term="")
        assert config.validate() is False


class TestLoggerConfig:
    """日志配置测试"""
    
    def test_logger_config_defaults(self):
        """测试默认配置值"""
        config = LoggerConfig()
        
        assert config.log_level == "INFO"
        assert config.console_output is True
        assert "logs/" in config.log_file_path
        
    def test_logger_config_env_loading(self):
        """测试环境变量加载"""
        with patch.dict(os.environ, {
            'LOG_LEVEL': 'DEBUG',
            'CONSOLE_OUTPUT': 'false'
        }):
            config = LoggerConfig()
            config.load_from_env()
            
            assert config.log_level == 'DEBUG'
            assert config.console_output is False
    
    def test_logger_config_validation(self):
        """测试配置验证"""
        # 有效日志级别
        config = LoggerConfig(log_level="DEBUG")
        assert config.validate() is True
        
        # 无效日志级别
        config = LoggerConfig(log_level="INVALID")
        assert config.validate() is False


class TestDatabaseConfig:
    """数据库配置测试"""
    
    def test_database_config_defaults(self):
        """测试默认配置值"""
        config = DatabaseConfig()
        
        assert config.db_path == "db/results.db"
        assert config.excel_path == "report/results.xlsx"
        assert config.connection_pool_size == 5
        assert config.connection_timeout == 30
        
    def test_database_config_url_property(self):
        """测试数据库URL属性"""
        config = DatabaseConfig(db_path="test.db")
        assert config.database_url == "sqlite:///test.db"
    
    def test_database_config_validation(self):
        """测试配置验证"""
        # 有效配置
        config = DatabaseConfig()
        assert config.validate() is True
        
        # 无效配置 - 空路径
        config = DatabaseConfig(db_path="")
        assert config.validate() is False
        
        # 无效配置 - 负数连接池大小
        config = DatabaseConfig(connection_pool_size=-1)
        assert config.validate() is False


class TestConfigManager:
    """配置管理器测试"""
    
    def test_config_manager_initialization(self):
        """测试配置管理器初始化"""
        manager = ConfigManager()
        assert not manager._initialized
        
        manager.initialize()
        assert manager._initialized
        assert hasattr(manager, 'app')
        assert hasattr(manager, 'logger')
        assert hasattr(manager, 'database')
    
    def test_get_config(self):
        """测试获取配置"""
        manager = ConfigManager()
        
        app_config = manager.get_config(AppConfig)
        assert isinstance(app_config, AppConfig)
        
        # 第二次获取应该返回同一实例
        app_config2 = manager.get_config(AppConfig)
        assert app_config is app_config2
    
    def test_reload_config(self):
        """测试重新加载配置"""
        manager = ConfigManager()
        
        app_config1 = manager.get_config(AppConfig)
        app_config2 = manager.reload_config(AppConfig)
        
        assert app_config1 is not app_config2
        assert isinstance(app_config2, AppConfig)
    
    def test_validate_all(self):
        """测试验证所有配置"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {'REPO_PATH': temp_dir}):
                manager = ConfigManager()
                assert manager.validate_all() is True


class TestGlobalConfigFunctions:
    """全局配置函数测试"""
    
    def test_get_app_config(self):
        """测试获取应用配置"""
        config = get_app_config()
        assert isinstance(config, AppConfig)
    
    def test_get_logger_config(self):
        """测试获取日志配置"""
        config = get_logger_config()
        assert isinstance(config, LoggerConfig)
    
    def test_get_database_config(self):
        """测试获取数据库配置"""
        config = get_database_config()
        assert isinstance(config, DatabaseConfig)
    
    def test_config_manager_singleton(self):
        """测试配置管理器单例模式"""
        manager1 = get_config_manager()
        manager2 = get_config_manager()
        assert manager1 is manager2