"""
Excel导出器
"""
import pandas as pd
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ExcelExporter:
    """Excel导出器"""
    
    def __init__(self, output_dir: str = "report/"):
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """确保输出目录存在"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def export(self, results: List[Dict[str, Any]], filename: str = "scan_results.xlsx") -> str:
        """导出扫描结果到Excel文件"""
        try:
            # 转换结果为DataFrame
            df = pd.DataFrame(results)
            
            # 处理空结果
            if df.empty:
                # 创建一个空的DataFrame与列结构
                df = pd.DataFrame({
                    "plugin_id": pd.Series(dtype='str'),
                    "file_path": pd.Series(dtype='str'),
                    "line_number": pd.Series(dtype='int'),
                    "column": pd.Series(dtype='int'),
                    "message": pd.Series(dtype='str'),
                    "severity": pd.Series(dtype='str'),
                    "rule_id": pd.Series(dtype='str'),
                    "category": pd.Series(dtype='str'),
                    "suggestion": pd.Series(dtype='str'),
                    "code_snippet": pd.Series(dtype='str')
                })
            
            # 确保必要的列存在
            required_columns = [
                "plugin_id", "file_path", "line_number", "column", "message",
                "severity", "rule_id", "category", "suggestion", "code_snippet"
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # 重新排列列的顺序
            df = df[required_columns]
            
            # 生成完整的文件路径
            filepath = os.path.join(self.output_dir, filename)
            
            # 导出到Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Excel报告已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"导出Excel报告失败: {e}")
            raise
    
    def export_summary(self, summary: Dict[str, Any], filename: str = "scan_summary.xlsx") -> str:
        """导出扫描摘要到Excel文件"""
        try:
            # 创建摘要DataFrame
            summary_data = {
                "指标": ["扫描文件数", "发现问题数", "扫描耗时(秒)", "开始时间", "结束时间"],
                "值": [
                    summary.get("total_files", 0),
                    summary.get("total_results", 0),
                    summary.get("scan_duration", 0),
                    summary.get("started_at", ""),
                    summary.get("ended_at", "")
                ]
            }
            
            df = pd.DataFrame(summary_data)
            
            # 生成完整的文件路径
            filepath = os.path.join(self.output_dir, filename)
            
            # 导出到Excel
            df.to_excel(filepath, index=False, engine='openpyxl')
            
            logger.info(f"Excel摘要报告已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"导出Excel摘要报告失败: {e}")
            raise