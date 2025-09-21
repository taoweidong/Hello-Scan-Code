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
    def __init__(self, excel_path: str, max_rows_per_file: int = 100000):
        self.excel_path = excel_path
        self.max_rows_per_file = max_rows_per_file  # 每个Excel文件的最大行数
    
    def export_to_excel(self, file_results: List[Dict[str, Any]]):
        """
        将结果导出到Excel文件，支持大文件拆分
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
            
            # 如果数据量不大，直接导出到单个文件
            if len(export_data) <= self.max_rows_per_file:
                self._export_to_single_excel(export_data, len(file_results), total_matches)
            else:
                # 如果数据量大，拆分导出到多个文件
                self._export_to_multiple_excel(export_data, len(file_results), total_matches)
                
        except Exception as e:
            logger.error(f"导出到Excel时出错: {e}")
            raise
    
    def _export_to_single_excel(self, export_data: List[Dict], file_count: int, total_matches: int):
        """导出到单个Excel文件"""
        if not PANDAS_AVAILABLE:
            logger.warning("pandas 未安装，无法导出到Excel")
            return
            
        try:
            # 清理可能导致Excel错误的特殊字符
            for row in export_data:
                for key in row:
                    if isinstance(row[key], str):
                        row[key] = self._clean_excel_content(row[key])
            
            # 创建DataFrame并导出到Excel
            self._create_and_export_dataframe(export_data, self.excel_path)
            logger.info(f"成功导出 {file_count} 个文件，共 {total_matches} 条匹配结果到Excel文件: {self.excel_path}")
        except Exception as e:
            logger.error(f"导出到Excel时出错: {e}")
            raise
    
    def _export_to_multiple_excel(self, export_data: List[Dict], file_count: int, total_matches: int):
        """拆分导出到多个Excel文件"""
        if not PANDAS_AVAILABLE:
            logger.warning("pandas 未安装，无法导出到Excel")
            return
            
        try:
            # 计算需要拆分成多少个文件
            num_files = (len(export_data) + self.max_rows_per_file - 1) // self.max_rows_per_file
            logger.info(f"数据量大，将拆分为 {num_files} 个Excel文件")
            
            # 获取文件名和扩展名
            base_name, ext = os.path.splitext(self.excel_path)
            
            exported_count = 0
            for i in range(num_files):
                # 计算当前文件的数据范围
                start_idx = i * self.max_rows_per_file
                end_idx = min((i + 1) * self.max_rows_per_file, len(export_data))
                chunk_data = export_data[start_idx:end_idx]
                
                # 清理可能导致Excel错误的特殊字符
                for row in chunk_data:
                    for key in row:
                        if isinstance(row[key], str):
                            row[key] = self._clean_excel_content(row[key])
                
                # 创建文件名
                if num_files == 1:
                    chunk_file_path = self.excel_path
                else:
                    chunk_file_path = f"{base_name}_part_{i+1}{ext}"
                
                # 创建DataFrame并导出
                self._create_and_export_dataframe(chunk_data, chunk_file_path)
                exported_count += len(chunk_data)
                logger.info(f"已导出部分数据到: {chunk_file_path} ({len(chunk_data)} 条记录)")
            
            logger.info(f"成功导出 {file_count} 个文件，共 {total_matches} 条匹配结果到 {num_files} 个Excel文件")
        except Exception as e:
            logger.error(f"拆分导出到Excel时出错: {e}")
            raise
    
    def _create_and_export_dataframe(self, data: List[Dict], file_path: str):
        """创建DataFrame并导出到Excel文件"""
        if pd is not None:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, engine='openpyxl')
    
    def _clean_excel_content(self, content: str) -> str:
        """清理可能导致Excel错误的特殊字符"""
        if not isinstance(content, str):
            return content
        
        # 移除或替换可能导致Excel错误的特殊字符
        # Excel中不能使用的字符: \, /, ?, *, [, ], :
        invalid_chars = ['\\', '/', '?', '*', '[', ']', ':']
        for char in invalid_chars:
            content = content.replace(char, '')
        
        # 移除控制字符 (ASCII 0-31 except 9, 10, 13 which are tab, newline, carriage return)
        # 这些字符包括错误信息中的等控制字符
        control_chars = [chr(i) for i in range(32) if i not in [9, 10, 13]]
        for char in control_chars:
            content = content.replace(char, '')
        
        # 限制内容长度以避免Excel单元格限制
        if len(content) > 32767:  # Excel单元格最大字符数
            content = content[:32764] + "..."
        
        return content