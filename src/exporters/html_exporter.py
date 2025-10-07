"""
HTML导出器
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class HTMLExporter:
    """HTML导出器"""
    
    def __init__(self, output_dir: str = "report/"):
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        """确保输出目录存在"""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def export(self, results: List[Dict[str, Any]], filename: str = "scan_results.html") -> str:
        """导出扫描结果到HTML文件"""
        try:
            # 生成HTML内容
            html_content = self._generate_html_content(results)
            
            # 生成完整的文件路径
            filepath = os.path.join(self.output_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML报告已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"导出HTML报告失败: {e}")
            raise
    
    def _generate_html_content(self, results: List[Dict[str, Any]]) -> str:
        """生成HTML内容"""
        # 按插件分组结果
        grouped_results = {}
        for result in results:
            plugin_id = result.get("plugin_id", "unknown")
            if plugin_id not in grouped_results:
                grouped_results[plugin_id] = []
            grouped_results[plugin_id].append(result)
        
        # 生成HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码扫描报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .plugin-section {{
            background-color: white;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .plugin-header {{
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }}
        .result-item {{
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .result-item:last-child {{
            border-bottom: none;
        }}
        .severity-high {{
            border-left: 5px solid #f44336;
        }}
        .severity-medium {{
            border-left: 5px solid #ff9800;
        }}
        .severity-low {{
            border-left: 5px solid #4CAF50;
        }}
        .severity-critical {{
            border-left: 5px solid #d32f2f;
        }}
        .file-path {{
            font-weight: bold;
            color: #1976d2;
        }}
        .message {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 3px;
        }}
        .code-snippet {{
            font-family: 'Courier New', monospace;
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .stat-item {{
            text-align: center;
            padding: 10px;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>代码扫描报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>扫描摘要</h2>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{len(results)}</div>
                <div class="stat-label">发现问题</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(grouped_results)}</div>
                <div class="stat-label">插件</div>
            </div>
        </div>
    </div>
    
    <div class="results">
"""
        
        # 添加每个插件的结果
        for plugin_id, plugin_results in grouped_results.items():
            html += f"""
        <div class="plugin-section">
            <div class="plugin-header">
                <h2>{plugin_id} <span style="font-size: 16px;">({len(plugin_results)} 个问题)</span></h2>
            </div>
"""
            
            # 添加每个结果
            for result in plugin_results:
                severity_class = f"severity-{result.get('severity', 'medium')}"
                html += f"""
            <div class="result-item {severity_class}">
                <div class="file-path">{result.get('file_path', '')}:{result.get('line_number', 0)}</div>
                <div class="message">{result.get('message', '')}</div>
                <div class="code-snippet">{result.get('code_snippet', '')}</div>
                <div><strong>规则:</strong> {result.get('rule_id', '')}</div>
                <div><strong>类别:</strong> {result.get('category', '')}</div>
                <div><strong>建议:</strong> {result.get('suggestion', '')}</div>
            </div>
"""
            
            html += "        </div>\n"
        
        html += """
    </div>
</body>
</html>
"""
        
        return html
    
    def export_summary(self, summary: Dict[str, Any], filename: str = "scan_summary.html") -> str:
        """导出扫描摘要到HTML文件"""
        try:
            # 生成HTML内容
            html_content = self._generate_summary_html_content(summary)
            
            # 生成完整的文件路径
            filepath = os.path.join(self.output_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML摘要报告已导出到: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"导出HTML摘要报告失败: {e}")
            raise
    
    def _generate_summary_html_content(self, summary: Dict[str, Any]) -> str:
        """生成摘要HTML内容"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>代码扫描摘要报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #333;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .summary {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stats {{
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
        }}
        .stat-item {{
            text-align: center;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #333;
        }}
        .stat-label {{
            font-size: 16px;
            color: #666;
        }}
        .details {{
            margin-top: 30px;
        }}
        .detail-item {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>代码扫描摘要报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>扫描统计</h2>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{summary.get('total_files', 0)}</div>
                <div class="stat-label">扫描文件数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{summary.get('total_results', 0)}</div>
                <div class="stat-label">发现问题数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{summary.get('scan_duration', 0):.2f}</div>
                <div class="stat-label">扫描耗时(秒)</div>
            </div>
        </div>
        
        <div class="details">
            <div class="detail-item">
                <strong>开始时间:</strong> {summary.get('started_at', 'N/A')}
            </div>
            <div class="detail-item">
                <strong>结束时间:</strong> {summary.get('ended_at', 'N/A')}
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html