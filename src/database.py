import sqlite3
import os
from typing import List, Dict, Any
from .logger_config import get_logger

logger = get_logger()

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """
        初始化数据库
        """
        try:
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    line_number TEXT,
                    matched_content TEXT,
                    search_term TEXT
                )
            ''')
            
            # 创建索引
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_path ON search_results (file_path)
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f"数据库初始化完成: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_results(self, file_results: List[Dict[str, Any]]):
        """
        保存搜索结果到数据库
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 准备插入数据
            data = []
            total_matches = 0
            for file_info in file_results:
                file_path = file_info['file_path']
                for match in file_info['matches']:
                    data.append((
                        file_path,
                        match['line_number'],
                        match['content'],
                        match['search_term']
                    ))
                    total_matches += 1
            
            # 批量插入数据
            cursor.executemany(
                "INSERT INTO search_results (file_path, line_number, matched_content, search_term) VALUES (?, ?, ?, ?)",
                data
            )
            
            conn.commit()
            conn.close()
            logger.info(f"成功保存 {len(file_results)} 个文件，共 {total_matches} 条匹配结果到数据库")
        except Exception as e:
            logger.error(f"保存结果到数据库时出错: {e}")
            raise
    
    def get_results(self) -> List[str]:
        """
        从数据库获取结果
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT file_path FROM search_results")
            results = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"从数据库获取结果时出错: {e}")
            raise