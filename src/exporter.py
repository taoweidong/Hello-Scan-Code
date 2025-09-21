import os
from typing import List, Dict, Any
from .logger_config import get_logger

# 注意：在实际运行前需要安装依赖
# pandas 和 openpyxl 需要通过 pip 或 uv 安装
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False

logger = get_logger()

class ExcelExporter:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
    
    def export_to_excel(self, file_results: List[Dict[str, Any]]):
        """
        将结果导出到Excel文件
        """
        if not PANDAS_AVAILABLE:
            logger.warning("pandas 未安装，无法导出到Excel")
            return
            
        try:
            # 确保输出目录存在
            excel_dir = os.path.dirname(self.excel_path)
            if excel_dir:
                os.makedirs(excel_dir, exist_ok=True)
            
            # 准备导出数据
            export_data = []
            total_matches = 0
            for file_info in file_results:
                file_path = file_info['file_path']
                for match in file_info['matches']:
                    export_data.append({
                        'File Path': file_path,
                        'Line Number': match['line_number'],
                        'Matched Content': match['content'],
                        'Search Term': match['search_term']
                    })
                    total_matches += 1
            
            # 创建DataFrame
            df = pd.DataFrame(export_data)
            
            # 导出到Excel
            df.to_excel(self.excel_path, index=False, engine='openpyxl')
            logger.info(f"成功导出 {len(file_results)} 个文件，共 {total_matches} 条匹配结果到Excel文件: {self.excel_path}")
        except Exception as e:
            logger.error(f"导出到Excel时出错: {e}")
            raise