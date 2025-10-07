"""
兼容性适配器

保持与原有DatabaseManager接口的完全兼容，内部使用新的ORM实现
"""

import os
from typing import List, Dict, Any
from .session_manager import DatabaseSessionManager
from .repositories import SearchResultRepository
from .migrations.migration_service import MigrationService
from .config import DatabaseConfig, EngineFactory
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    数据库管理器兼容性适配器
    
    保持与原有DatabaseManager完全相同的接口，内部使用新的ORM架构实现
    这确保了现有代码无需修改就能使用新的数据库层
    """
    
    def __init__(self, db_path: str):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 创建数据库配置
        self.config = DatabaseConfig(db_path=db_path)
        
        # 初始化会话管理器
        self.session_manager = DatabaseSessionManager(self.config)
        
        # 初始化仓库
        self.search_result_repo = SearchResultRepository()
        
        # 执行数据库迁移（在测试时可以跳过）
        if not os.getenv('SKIP_MIGRATION'):
            self._run_migrations()
        
        logger.info(f"DatabaseManager初始化完成: {db_path}")
    
    def _run_migrations(self):
        """
        运行数据库迁移
        """
        try:
            migration_service = MigrationService(self.session_manager.engine)
            migration_info = migration_service.get_migration_info()
            
            if migration_info['migration_needed']:
                logger.info(f"检测到数据库需要迁移从 {migration_info['current_version']} 到 {migration_info['target_version']}")
                if migration_service.migrate():
                    logger.info("数据库迁移成功完成")
                else:
                    logger.error("数据库迁移失败")
                    raise Exception("数据库迁移失败")
            else:
                logger.info(f"数据库已是最新版本: {migration_info['current_version']}")
                
        except Exception as e:
            logger.error(f"数据库迁移过程出错: {e}")
            raise
    
    def init_database(self):
        """
        初始化数据库（兼容原有接口）
        
        注意：在新架构中，数据库初始化在SessionManager中自动完成，
        这个方法保留只是为了兼容性，实际上是空操作
        """
        # 检查数据库健康状态
        if self.session_manager.health_check():
            logger.info(f"数据库连接正常: {self.db_path}")
        else:
            logger.error(f"数据库连接异常: {self.db_path}")
            raise Exception("数据库连接失败")
    
    def save_results(self, file_results: List[Dict[str, Any]]):
        """
        保存搜索结果到数据库（兼容原有接口）
        
        Args:
            file_results: 文件搜索结果列表
                格式: [{'file_path': str, 'matches': [{'line_number': str, 'content': str, 'search_term': str}]}]
        """
        try:
            def _save_operation(session):
                return self.search_result_repo.save_results(session, file_results)
            
            total_matches = self.session_manager.execute_in_transaction(_save_operation)
            logger.info(f"通过兼容性适配器成功保存 {total_matches} 条搜索结果")
            
        except Exception as e:
            logger.error(f"通过兼容性适配器保存结果失败: {e}")
            raise
    
    def get_results(self) -> List[str]:
        """
        从数据库获取结果（兼容原有接口）
        
        Returns:
            文件路径列表
        """
        try:
            def _get_operation(session):
                return self.search_result_repo.get_results(session)
            
            results = self.session_manager.execute_in_transaction(_get_operation)
            logger.debug(f"通过兼容性适配器获取到 {len(results)} 个文件路径")
            return results
            
        except Exception as e:
            logger.error(f"通过兼容性适配器获取结果失败: {e}")
            raise
    
    # 以下是新增的扩展功能，提供更丰富的数据访问能力
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        获取搜索统计信息（新增功能）
        
        Returns:
            统计信息字典
        """
        try:
            def _stats_operation(session):
                return self.search_result_repo.get_statistics(session)
            
            return self.session_manager.execute_in_transaction(_stats_operation)
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def search_by_file_path(self, file_path: str) -> List[Dict[str, Any]]:
        """
        根据文件路径搜索结果（新增功能）
        
        Args:
            file_path: 文件路径
            
        Returns:
            搜索结果列表
        """
        try:
            def _search_operation(session):
                models = self.search_result_repo.get_by_file_path(session, file_path)
                return [model.to_dict() for model in models]
            
            return self.session_manager.execute_in_transaction(_search_operation)
        except Exception as e:
            logger.error(f"按文件路径搜索失败: {e}")
            return []
    
    def search_by_term(self, search_term: str) -> List[Dict[str, Any]]:
        """
        根据搜索词搜索结果（新增功能）
        
        Args:
            search_term: 搜索词
            
        Returns:
            搜索结果列表
        """
        try:
            def _search_operation(session):
                models = self.search_result_repo.get_by_search_term(session, search_term)
                return [model.to_dict() for model in models]
            
            return self.session_manager.execute_in_transaction(_search_operation)
        except Exception as e:
            logger.error(f"按搜索词搜索失败: {e}")
            return []
    
    def search_in_content(self, keyword: str) -> List[Dict[str, Any]]:
        """
        在内容中搜索关键词（新增功能）
        
        Args:
            keyword: 关键词
            
        Returns:
            包含关键词的搜索结果列表
        """
        try:
            def _search_operation(session):
                models = self.search_result_repo.search_in_content(session, keyword)
                return [model.to_dict() for model in models]
            
            return self.session_manager.execute_in_transaction(_search_operation)
        except Exception as e:
            logger.error(f"内容搜索失败: {e}")
            return []
    
    def delete_by_file_path(self, file_path: str) -> int:
        """
        删除指定文件的搜索结果（新增功能）
        
        Args:
            file_path: 文件路径
            
        Returns:
            删除的记录数量
        """
        try:
            def _delete_operation(session):
                return self.search_result_repo.delete_by_file_path(session, file_path)
            
            return self.session_manager.execute_in_transaction(_delete_operation)
        except Exception as e:
            logger.error(f"删除文件搜索结果失败: {e}")
            return 0
    
    def cleanup_old_results(self, days: int = 30) -> int:
        """
        清理旧的搜索结果（新增功能）
        
        Args:
            days: 保留天数
            
        Returns:
            清理的记录数量
        """
        try:
            def _cleanup_operation(session):
                return self.search_result_repo.cleanup_old_results(session, days)
            
            return self.session_manager.execute_in_transaction(_cleanup_operation)
        except Exception as e:
            logger.error(f"清理旧结果失败: {e}")
            return 0
    
    def get_top_files(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取匹配数最多的文件（新增功能）
        
        Args:
            limit: 返回数量限制
            
        Returns:
            文件统计信息列表
        """
        try:
            def _top_files_operation(session):
                return self.search_result_repo.get_top_files_by_matches(session, limit)
            
            return self.session_manager.execute_in_transaction(_top_files_operation)
        except Exception as e:
            logger.error(f"获取热门文件失败: {e}")
            return []
    
    def close(self):
        """
        关闭数据库连接（新增功能）
        """
        try:
            self.session_manager.close()
            logger.info("DatabaseManager已关闭")
        except Exception as e:
            logger.error(f"关闭DatabaseManager失败: {e}")
    
    def __enter__(self):
        """
        支持with语句
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出时自动关闭
        """
        self.close()
    
    def __del__(self):
        """
        析构函数
        """
        try:
            self.close()
        except:
            pass