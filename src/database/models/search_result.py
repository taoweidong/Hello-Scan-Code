"""
搜索结果数据模型

定义搜索结果的数据结构和映射关系
"""

from typing import List, Optional
from sqlalchemy import String, Text, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class SearchResultModel(BaseModel):
    """
    搜索结果数据模型
    
    表示代码搜索的匹配结果，包含文件路径、行号、匹配内容等信息
    """
    
    __tablename__ = 'search_results'
    
    # 文件路径 - 建立索引以提升查询性能
    file_path: Mapped[str] = mapped_column(
        String(500), 
        nullable=False,
        index=True,
        comment="文件完整路径"
    )
    
    # 匹配行号
    line_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="匹配内容所在行号"
    )
    
    # 匹配的内容
    matched_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="匹配到的具体内容"
    )
    
    # 搜索关键词 - 建立索引以支持按搜索词查询
    search_term: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        index=True,
        comment="搜索使用的关键词"
    )
    
    # 文件大小（字节）
    file_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="文件大小，单位：字节"
    )
    
    # 文件编码格式
    encoding: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="文件编码格式，如utf-8、gbk等"
    )
    
    # 匹配位置偏移量
    match_position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="匹配内容在文件中的字符偏移位置"
    )
    
    # 创建复合索引以优化常见查询场景
    __table_args__ = (
        # 文件路径和搜索词的复合索引，优化按文件和搜索词的联合查询
        Index('idx_file_path_search_term', 'file_path', 'search_term'),
        # 创建时间索引，支持按时间范围查询
        Index('idx_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """
        返回搜索结果的字符串表示
        """
        return (f"<SearchResult(id={self.id}, "
                f"file_path='{self.file_path}', "
                f"line_number='{self.line_number}', "
                f"search_term='{self.search_term}')>")
    
    @classmethod
    def get_by_file_path(cls, session, file_path: str) -> List['SearchResultModel']:
        """
        根据文件路径查询搜索结果
        
        Args:
            session: 数据库会话
            file_path: 文件路径
            
        Returns:
            匹配的搜索结果列表
        """
        return session.query(cls).filter(cls.file_path == file_path).all()
    
    @classmethod
    def get_by_search_term(cls, session, search_term: str) -> List['SearchResultModel']:
        """
        根据搜索词查询搜索结果
        
        Args:
            session: 数据库会话
            search_term: 搜索关键词
            
        Returns:
            匹配的搜索结果列表
        """
        return session.query(cls).filter(cls.search_term == search_term).all()
    
    @classmethod
    def search_in_content(cls, session, keyword: str) -> List['SearchResultModel']:
        """
        在匹配内容中搜索关键词（模糊搜索）
        
        Args:
            session: 数据库会话
            keyword: 要搜索的关键词
            
        Returns:
            包含关键词的搜索结果列表
        """
        return session.query(cls).filter(
            cls.matched_content.contains(keyword)
        ).all()
    
    @classmethod
    def get_statistics(cls, session) -> dict:
        """
        获取搜索结果统计信息
        
        Args:
            session: 数据库会话
            
        Returns:
            包含统计信息的字典
        """
        from sqlalchemy import func, distinct
        
        stats = session.query(
            func.count(cls.id).label('total_matches'),
            func.count(distinct(cls.file_path)).label('unique_files'),
            func.count(distinct(cls.search_term)).label('unique_terms')
        ).first()
        
        return {
            'total_matches': stats.total_matches or 0,
            'unique_files': stats.unique_files or 0,
            'unique_search_terms': stats.unique_terms or 0
        }