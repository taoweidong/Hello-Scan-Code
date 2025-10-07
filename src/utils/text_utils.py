"""
文本工具函数
"""
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def extract_code_snippets(text: str, line_numbers: List[int], 
                         context_lines: int = 2) -> List[Dict[str, str]]:
    """
    从文本中提取代码片段
    
    Args:
        text: 文本内容
        line_numbers: 行号列表
        context_lines: 上下文行数
        
    Returns:
        代码片段列表
    """
    lines = text.split('\n')
    snippets = []
    
    for line_num in line_numbers:
        start_line = max(0, line_num - context_lines - 1)
        end_line = min(len(lines), line_num + context_lines)
        
        snippet_lines = []
        for i in range(start_line, end_line):
            line_prefix = f"{i+1:4d} | " if i == line_num - 1 else f"     | "
            snippet_lines.append(f"{line_prefix}{lines[i]}")
        
        snippets.append({
            "line_number": line_num,
            "snippet": '\n'.join(snippet_lines)
        })
    
    return snippets

def highlight_text(text: str, pattern: str, highlight_start: str = "**", 
                  highlight_end: str = "**") -> str:
    """
    高亮文本中的匹配模式
    
    Args:
        text: 文本内容
        pattern: 正则表达式模式
        highlight_start: 高亮开始标记
        highlight_end: 高亮结束标记
        
    Returns:
        高亮后的文本
    """
    try:
        return re.sub(pattern, f"{highlight_start}\\g<0>{highlight_end}", text)
    except Exception as e:
        logger.debug(f"高亮文本时出错: {e}")
        return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 文本内容
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def normalize_whitespace(text: str) -> str:
    """
    标准化空白字符
    
    Args:
        text: 文本内容
        
    Returns:
        标准化后的文本
    """
    # 将多个空白字符替换为单个空格
    return re.sub(r'\s+', ' ', text).strip()

def count_lines(text: str) -> int:
    """
    计算文本行数
    
    Args:
        text: 文本内容
        
    Returns:
        行数
    """
    return len(text.split('\n'))

def find_pattern_positions(text: str, pattern: str) -> List[Dict[str, int]]:
    """
    查找模式在文本中的位置
    
    Args:
        text: 文本内容
        pattern: 正则表达式模式
        
    Returns:
        位置信息列表
    """
    positions = []
    try:
        for match in re.finditer(pattern, text):
            positions.append({
                "start": match.start(),
                "end": match.end(),
                "line_number": text[:match.start()].count('\n') + 1
            })
    except Exception as e:
        logger.debug(f"查找模式位置时出错: {e}")
    
    return positions