"""
数据库仓储 - 负责数据访问
"""
from typing import List, Optional
from .session_manager import DatabaseSessionManager
from .models import ScanResultModel, ScanSummaryModel
import logging

logger = logging.getLogger(__name__)

class ScanResultRepository:
    """扫描结果仓储"""
    
    def __init__(self, session_manager: DatabaseSessionManager):
        self.session_manager = session_manager
        self._create_table()
    
    def _create_table(self):
        """创建表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS scan_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plugin_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            line_number INTEGER NOT NULL,
            column INTEGER DEFAULT 0,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            rule_id TEXT NOT NULL,
            category TEXT NOT NULL,
            suggestion TEXT,
            code_snippet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.session_manager.execute_non_query(create_table_sql)
            logger.info("扫描结果表创建成功")
        except Exception as e:
            logger.error(f"创建扫描结果表失败: {e}")
    
    def save(self, result: ScanResultModel) -> int:
        """保存扫描结果"""
        insert_sql = """
        INSERT INTO scan_results 
        (plugin_id, file_path, line_number, column, message, severity, rule_id, category, suggestion, code_snippet)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            result.plugin_id,
            result.file_path,
            result.line_number,
            result.column,
            result.message,
            result.severity,
            result.rule_id,
            result.category,
            result.suggestion,
            result.code_snippet
        )
        
        try:
            rowcount = self.session_manager.execute_non_query(insert_sql, params)
            logger.debug(f"保存扫描结果成功: {result.plugin_id} - {result.file_path}:{result.line_number}")
            return rowcount
        except Exception as e:
            logger.error(f"保存扫描结果失败: {e}")
            return 0
    
    def save_batch(self, results: List[ScanResultModel]) -> int:
        """批量保存扫描结果"""
        saved_count = 0
        for result in results:
            if self.save(result) > 0:
                saved_count += 1
        return saved_count
    
    def get_all(self) -> List[ScanResultModel]:
        """获取所有扫描结果"""
        select_sql = "SELECT * FROM scan_results ORDER BY created_at DESC"
        
        try:
            rows = self.session_manager.execute_query(select_sql)
            results = []
            for row in rows:
                result = ScanResultModel(
                    id=row["id"],
                    plugin_id=row["plugin_id"],
                    file_path=row["file_path"],
                    line_number=row["line_number"],
                    column=row["column"],
                    message=row["message"],
                    severity=row["severity"],
                    rule_id=row["rule_id"],
                    category=row["category"],
                    suggestion=row["suggestion"],
                    code_snippet=row["code_snippet"]
                )
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"获取扫描结果失败: {e}")
            return []
    
    def get_by_plugin(self, plugin_id: str) -> List[ScanResultModel]:
        """根据插件ID获取扫描结果"""
        select_sql = "SELECT * FROM scan_results WHERE plugin_id = ? ORDER BY created_at DESC"
        
        try:
            rows = self.session_manager.execute_query(select_sql, (plugin_id,))
            results = []
            for row in rows:
                result = ScanResultModel(
                    id=row["id"],
                    plugin_id=row["plugin_id"],
                    file_path=row["file_path"],
                    line_number=row["line_number"],
                    column=row["column"],
                    message=row["message"],
                    severity=row["severity"],
                    rule_id=row["rule_id"],
                    category=row["category"],
                    suggestion=row["suggestion"],
                    code_snippet=row["code_snippet"]
                )
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"根据插件ID获取扫描结果失败: {e}")
            return []
    
    def delete_all(self) -> int:
        """删除所有扫描结果"""
        delete_sql = "DELETE FROM scan_results"
        
        try:
            rowcount = self.session_manager.execute_non_query(delete_sql)
            logger.info(f"删除了 {rowcount} 条扫描结果")
            return rowcount
        except Exception as e:
            logger.error(f"删除扫描结果失败: {e}")
            return 0


class ScanSummaryRepository:
    """扫描摘要仓储"""
    
    def __init__(self, session_manager: DatabaseSessionManager):
        self.session_manager = session_manager
        self._create_table()
    
    def _create_table(self):
        """创建表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS scan_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_files INTEGER NOT NULL,
            total_results INTEGER NOT NULL,
            scan_duration REAL NOT NULL,
            started_at TIMESTAMP,
            ended_at TIMESTAMP
        )
        """
        try:
            self.session_manager.execute_non_query(create_table_sql)
            logger.info("扫描摘要表创建成功")
        except Exception as e:
            logger.error(f"创建扫描摘要表失败: {e}")
    
    def save(self, summary: ScanSummaryModel) -> int:
        """保存扫描摘要"""
        insert_sql = """
        INSERT INTO scan_summaries 
        (total_files, total_results, scan_duration, started_at, ended_at)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            summary.total_files,
            summary.total_results,
            summary.scan_duration,
            summary.started_at,
            summary.ended_at
        )
        
        try:
            rowcount = self.session_manager.execute_non_query(insert_sql, params)
            logger.debug(f"保存扫描摘要成功")
            return rowcount
        except Exception as e:
            logger.error(f"保存扫描摘要失败: {e}")
            return 0
    
    def get_latest(self) -> Optional[ScanSummaryModel]:
        """获取最新的扫描摘要"""
        select_sql = "SELECT * FROM scan_summaries ORDER BY id DESC LIMIT 1"
        
        try:
            rows = self.session_manager.execute_query(select_sql)
            if rows:
                row = rows[0]
                summary = ScanSummaryModel(
                    id=row["id"],
                    total_files=row["total_files"],
                    total_results=row["total_results"],
                    scan_duration=row["scan_duration"],
                    started_at=row["started_at"],
                    ended_at=row["ended_at"]
                )
                return summary
            return None
        except Exception as e:
            logger.error(f"获取最新扫描摘要失败: {e}")
            return None