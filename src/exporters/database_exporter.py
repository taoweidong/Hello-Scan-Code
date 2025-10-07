"""
数据库导出器
"""
from typing import List, Dict, Any
from src.database.repositories import ScanResultRepository, ScanSummaryRepository
from src.database.models import ScanResultModel, ScanSummaryModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseExporter:
    """数据库导出器"""
    
    def __init__(self, result_repository: ScanResultRepository, summary_repository: ScanSummaryRepository):
        self.result_repository = result_repository
        self.summary_repository = summary_repository
    
    def export(self, results: List[Dict[str, Any]]) -> int:
        """导出扫描结果到数据库"""
        try:
            # 转换字典结果为模型对象
            model_results = []
            for result_dict in results:
                model_result = ScanResultModel(
                    plugin_id=result_dict.get("plugin_id", ""),
                    file_path=result_dict.get("file_path", ""),
                    line_number=result_dict.get("line_number", 0),
                    column=result_dict.get("column", 0),
                    message=result_dict.get("message", ""),
                    severity=result_dict.get("severity", "medium"),
                    rule_id=result_dict.get("rule_id", ""),
                    category=result_dict.get("category", ""),
                    suggestion=result_dict.get("suggestion"),
                    code_snippet=result_dict.get("code_snippet")
                )
                model_results.append(model_result)
            
            # 批量保存到数据库
            saved_count = self.result_repository.save_batch(model_results)
            
            logger.info(f"已将 {saved_count} 条扫描结果保存到数据库")
            return saved_count
            
        except Exception as e:
            logger.error(f"导出扫描结果到数据库失败: {e}")
            raise
    
    def export_summary(self, summary: Dict[str, Any]) -> int:
        """导出扫描摘要到数据库"""
        try:
            # 转换字典摘要为模型对象
            model_summary = ScanSummaryModel(
                total_files=summary.get("total_files", 0),
                total_results=summary.get("total_results", 0),
                scan_duration=summary.get("scan_duration", 0.0),
                started_at=summary.get("started_at"),
                ended_at=summary.get("ended_at")
            )
            
            # 保存到数据库
            saved_count = self.summary_repository.save(model_summary)
            
            if saved_count > 0:
                logger.info("扫描摘要已保存到数据库")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"导出扫描摘要到数据库失败: {e}")
            raise
    
    def clear_previous_results(self) -> int:
        """清除之前的扫描结果"""
        try:
            deleted_count = self.result_repository.delete_all()
            logger.info(f"已清除 {deleted_count} 条之前的扫描结果")
            return deleted_count
        except Exception as e:
            logger.error(f"清除之前扫描结果失败: {e}")
            raise