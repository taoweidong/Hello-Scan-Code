"""
搜索结果仓库实现

提供搜索结果的专门数据访问功能
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, desc, and_, or_
from .base_repository import BaseRepository
from ..models.search_result import SearchResultModel
from src.config import get_logger

logger = get_logger()


class SearchResultRepository(BaseRepository[SearchResultModel]):
    """
    搜索结果仓库
    
    提供搜索结果相关的数据访问功能，包括高性能的批量操作和复杂查询
    """
    
    def __init__(self):
        """
        初始化搜索结果仓库
        """
        super().__init__(SearchResultModel)
    
    def save_results(self, session: Session, file_results: List[Dict[str, Any]]) -> int:
        """
        保存搜索结果（兼容原有接口）
        
        Args:
            session: 数据库会话
            file_results: 文件搜索结果列表
            
        Returns:
            保存的记录数量
        """
        try:
            # 准备插入数据
            data = []
            total_matches = 0
            
            for file_info in file_results:
                file_path = file_info['file_path']
                file_size = file_info.get('file_size')
                encoding = file_info.get('encoding')
                
                for match in file_info['matches']:
                    data.append({
                        'file_path': file_path,
                        'line_number': match.get('line_number'),
                        'matched_content': match.get('content'),
                        'search_term': match.get('search_term'),
                        'file_size': file_size,
                        'encoding': encoding,
                        'match_position': match.get('position')
                    })
                    total_matches += 1
            
            # 批量插入
            if data:
                self.bulk_create(session, data)
            
            logger.info(f"成功保存 {len(file_results)} 个文件，共 {total_matches} 条匹配结果")
            return total_matches
            
        except Exception as e:
            logger.error(f"保存搜索结果失败: {e}")
            raise
    
    def get_results(self, session: Session) -> List[str]:
        """
        获取所有文件路径（兼容原有接口）
        
        Args:
            session: 数据库会话
            
        Returns:
            文件路径列表
        """
        try:
            # 查询所有唯一的文件路径
            results = session.query(distinct(SearchResultModel.file_path)).all()
            return [row[0] for row in results]
        except Exception as e:
            logger.error(f"获取搜索结果失败: {e}")
            raise
    
    def get_by_criteria(self, session: Session, **criteria) -> List[SearchResultModel]:
        """
        根据条件查询搜索结果
        
        Args:
            session: 数据库会话
            **criteria: 查询条件
            
        Returns:
            匹配的搜索结果列表
        """
        query = session.query(SearchResultModel)
        
        # 按文件路径过滤
        if 'file_path' in criteria:
            query = query.filter(SearchResultModel.file_path == criteria['file_path'])
        
        # 按搜索词过滤
        if 'search_term' in criteria:
            query = query.filter(SearchResultModel.search_term == criteria['search_term'])
        
        # 按行号过滤
        if 'line_number' in criteria:
            query = query.filter(SearchResultModel.line_number == criteria['line_number'])
        
        # 文件路径模糊匹配
        if 'file_path_like' in criteria:
            query = query.filter(SearchResultModel.file_path.contains(criteria['file_path_like']))
        
        # 内容模糊匹配
        if 'content_like' in criteria:
            query = query.filter(SearchResultModel.matched_content.contains(criteria['content_like']))
        
        # 时间范围过滤
        if 'created_after' in criteria:
            query = query.filter(SearchResultModel.created_at >= criteria['created_after'])
        
        if 'created_before' in criteria:
            query = query.filter(SearchResultModel.created_at <= criteria['created_before'])
        
        # 排序（必须在offset和limit之前）
        order_by = criteria.get('order_by', 'created_at')
        if hasattr(SearchResultModel, order_by):
            if criteria.get('desc', False):
                query = query.order_by(desc(getattr(SearchResultModel, order_by)))
            else:
                query = query.order_by(getattr(SearchResultModel, order_by))
        
        # 分页参数
        if 'offset' in criteria:
            query = query.offset(criteria['offset'])
        
        if 'limit' in criteria:
            query = query.limit(criteria['limit'])
        
        return query.all()
    
    def get_by_file_path(self, session: Session, file_path: str) -> List[SearchResultModel]:
        """
        根据文件路径获取搜索结果
        
        Args:
            session: 数据库会话
            file_path: 文件路径
            
        Returns:
            匹配的搜索结果列表
        """
        return session.query(SearchResultModel).filter(
            SearchResultModel.file_path == file_path
        ).all()
    
    def get_by_search_term(self, session: Session, search_term: str) -> List[SearchResultModel]:
        """
        根据搜索词获取搜索结果
        
        Args:
            session: 数据库会话
            search_term: 搜索词
            
        Returns:
            匹配的搜索结果列表
        """
        return session.query(SearchResultModel).filter(
            SearchResultModel.search_term == search_term
        ).all()
    
    def search_in_content(self, session: Session, keyword: str) -> List[SearchResultModel]:
        """
        在匹配内容中搜索关键词
        
        Args:
            session: 数据库会话
            keyword: 搜索关键词
            
        Returns:
            包含关键词的搜索结果列表
        """
        return session.query(SearchResultModel).filter(
            SearchResultModel.matched_content.contains(keyword)
        ).all()
    
    def get_statistics(self, session: Session) -> Dict[str, Any]:
        """
        获取搜索结果统计信息
        
        Args:
            session: 数据库会话
            
        Returns:
            统计信息字典
        """
        try:
            # 基本统计
            stats = session.query(
                func.count(SearchResultModel.id).label('total_matches'),
                func.count(distinct(SearchResultModel.file_path)).label('unique_files'),
                func.count(distinct(SearchResultModel.search_term)).label('unique_terms')
            ).first()
            
            # 文件大小统计
            size_stats = session.query(
                func.sum(SearchResultModel.file_size).label('total_size'),
                func.avg(SearchResultModel.file_size).label('avg_size'),
                func.max(SearchResultModel.file_size).label('max_size')
            ).first()
            
            # 最近活动统计
            recent_activity = session.query(
                func.max(SearchResultModel.created_at).label('last_search'),
                func.min(SearchResultModel.created_at).label('first_search')
            ).first()
            
            return {
                'total_matches': stats.total_matches or 0,
                'unique_files': stats.unique_files or 0,
                'unique_search_terms': stats.unique_terms or 0,
                'total_file_size': size_stats.total_size or 0,
                'average_file_size': size_stats.avg_size or 0,
                'max_file_size': size_stats.max_size or 0,
                'last_search_time': recent_activity.last_search,
                'first_search_time': recent_activity.first_search
            }
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def count_total_matches(self, session: Session) -> int:
        """
        获取匹配总数
        
        Args:
            session: 数据库会话
            
        Returns:
            匹配总数
        """
        return self.count(session)
    
    def delete_by_file_path(self, session: Session, file_path: str) -> int:
        """
        删除指定文件的所有搜索结果
        
        Args:
            session: 数据库会话
            file_path: 文件路径
            
        Returns:
            删除的记录数量
        """
        deleted_count = session.query(SearchResultModel).filter(
            SearchResultModel.file_path == file_path
        ).delete(synchronize_session=False)
        
        logger.info(f"删除文件 {file_path} 的 {deleted_count} 条搜索结果")
        return deleted_count
    
    def cleanup_old_results(self, session: Session, days: int = 30) -> int:
        """
        清理旧的搜索结果
        
        Args:
            session: 数据库会话
            days: 保留天数
            
        Returns:
            清理的记录数量
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = session.query(SearchResultModel).filter(
            SearchResultModel.created_at < cutoff_date
        ).delete(synchronize_session=False)
        
        logger.info(f"清理了 {deleted_count} 条超过 {days} 天的搜索结果")
        return deleted_count
    
    def get_top_files_by_matches(self, session: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取匹配数最多的文件
        
        Args:
            session: 数据库会话
            limit: 返回数量限制
            
        Returns:
            文件统计信息列表
        """
        results = session.query(
            SearchResultModel.file_path,
            func.count(SearchResultModel.id).label('match_count'),
            func.max(SearchResultModel.file_size).label('file_size')
        ).group_by(
            SearchResultModel.file_path
        ).order_by(
            desc('match_count')
        ).limit(limit).all()
        
        return [
            {
                'file_path': result.file_path,
                'match_count': result.match_count,
                'file_size': result.file_size
            }
            for result in results
        ]
    
    def get_search_term_statistics(self, session: Session) -> List[Dict[str, Any]]:
        """
        获取搜索词统计信息
        
        Args:
            session: 数据库会话
            
        Returns:
            搜索词统计列表
        """
        results = session.query(
            SearchResultModel.search_term,
            func.count(SearchResultModel.id).label('usage_count'),
            func.count(distinct(SearchResultModel.file_path)).label('file_count')
        ).filter(
            SearchResultModel.search_term.isnot(None)
        ).group_by(
            SearchResultModel.search_term
        ).order_by(
            desc('usage_count')
        ).all()
        
        return [
            {
                'search_term': result.search_term,
                'usage_count': result.usage_count,
                'file_count': result.file_count
            }
            for result in results
        ]