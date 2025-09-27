#!/usr/bin/env python3
"""
搜索策略接口和实现
使用策略模式定义不同的搜索算法
"""

import subprocess
import re
import os
import glob
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from .config import get_logger, AppConfig

logger = get_logger()


class SearchStrategy(ABC):
    """搜索策略抽象基类"""
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """
        初始化搜索策略
        
        Args:
            config: 搜索配置对象
        """
        self.config = config or SearchConfig()
    
    @abstractmethod
    def search(self, repo_path: str, search_terms: List[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
        """
        执行搜索的抽象方法
        
        Args:
            repo_path: 仓库路径
            search_terms: 搜索词列表或单个搜索词
            is_regex: 是否使用正则表达式
            
        Returns:
            搜索结果列表
        """
        pass
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """
        判断是否应该忽略该文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否应该忽略该文件
        """
        # 检查是否在忽略目录中
        if self.config.ignore_dirs:
            for ignore_dir in self.config.ignore_dirs:
                if ignore_dir in file_path:
                    return True
        
        # 检查文件后缀
        if self.config.file_extensions is not None:
            # 获取文件扩展名
            _, ext = os.path.splitext(file_path)
            if ext and ext not in self.config.file_extensions:
                # 如果有扩展名但不在允许列表中，则忽略
                if self.config.file_extensions:  # 只有当允许列表不为空时才应用限制
                    return True
        
        return False


class GrepSearchStrategy(SearchStrategy):
    """Grep搜索策略实现"""
    
    def search(self, repo_path: str, search_terms: List[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
        """
        使用grep进行搜索
        """
        # 确保search_terms是列表格式
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        
        all_results = []
        
        # 对每个搜索词执行一次grep搜索
        for search_term in search_terms:
            # 首先尝试使用grep
            try:
                # 构建grep命令获取匹配的行
                cmd = ["grep", "-r", "-n"]
                if is_regex:
                    cmd.append("-E")
                cmd.extend([search_term, repo_path])
                
                # 添加grep的排除目录选项
                if self.config.ignore_dirs:
                    for ignore_dir in self.config.ignore_dirs:
                        cmd.extend(["--exclude-dir", ignore_dir])
                
                # 如果指定了文件后缀，添加文件类型过滤
                if self.config.file_extensions is not None and self.config.file_extensions:
                    patterns = ["*" + ext if not ext.startswith(".") else "*" + ext for ext in self.config.file_extensions]
                    for pattern in patterns:
                        cmd.extend(["--include", pattern])
                
                logger.info(f"执行grep命令: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    # 过滤空行
                    lines = [line for line in lines if line]
                    
                    # 解析结果，组织成文件和匹配行的结构
                    file_matches = {}
                    for line in lines:
                        if ':' in line:
                            parts = line.split(':', 2)  # 最多分割成3部分
                            if len(parts) >= 3:
                                file_path, line_number, matched_content = parts[0], parts[1], parts[2]
                                # 检查是否应该忽略该文件
                                if not self._should_ignore_file(file_path):
                                    if file_path not in file_matches:
                                        file_matches[file_path] = []
                                    file_matches[file_path].append({
                                        'line_number': line_number,
                                        'content': matched_content,
                                        'search_term': search_term  # 记录是哪个搜索词匹配的
                                    })
                    
                    # 转换为列表格式
                    result_list = []
                    for file_path, matches in file_matches.items():
                        result_list.append({
                            'file_path': file_path,
                            'matches': matches
                        })
                    
                    all_results.extend(result_list)
                    logger.info(f"grep搜索 '{search_term}' 找到 {len(result_list)} 个匹配文件，共 {sum(len(item['matches']) for item in result_list)} 个匹配行")
                elif result.returncode == 1:
                    # 没有找到匹配项
                    logger.info(f"grep搜索 '{search_term}' 未找到匹配项")
                else:
                    logger.warning(f"grep命令执行失败: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.warning(f"grep命令执行超时: {search_term}")
            except FileNotFoundError:
                logger.warning("未找到grep命令，将使用纯Python实现搜索")
                # 如果grep不可用，使用纯Python实现，并跳出循环避免重复执行
                return PythonSearchStrategy(self.config).search(repo_path, search_terms, is_regex)
            except Exception as e:
                logger.warning(f"执行grep搜索 '{search_term}' 时出错: {e}")
        
        # 合并相同文件的匹配结果
        merged_results = {}
        for item in all_results:
            file_path = item['file_path']
            if file_path not in merged_results:
                merged_results[file_path] = {
                    'file_path': file_path,
                    'matches': []
                }
            merged_results[file_path]['matches'].extend(item['matches'])
        
        # 转换回列表格式
        final_results = list(merged_results.values())
        
        logger.info(f"grep总共找到 {len(final_results)} 个匹配文件，共 {sum(len(item['matches']) for item in final_results)} 个匹配行")
        return final_results


class PythonSearchStrategy(SearchStrategy):
    """Python搜索策略实现"""
    
    def search(self, repo_path: str, search_terms: List[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
        """
        使用纯Python实现搜索功能
        """
        # 确保search_terms是列表格式
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        
        file_matches = {}
        
        # 递归搜索所有文件
        for file_path in glob.glob(os.path.join(repo_path, '**/*'), recursive=True):
            if os.path.isfile(file_path):
                # 检查是否应该忽略该文件
                if self._should_ignore_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # 对每个搜索词检查每一行
                    for search_term in search_terms:
                        for i, line in enumerate(lines, 1):
                            match_found = False
                            if is_regex:
                                if re.search(search_term, line):
                                    match_found = True
                            else:
                                if search_term in line:
                                    match_found = True
                            
                            if match_found:
                                if file_path not in file_matches:
                                    file_matches[file_path] = []
                                file_matches[file_path].append({
                                    'line_number': str(i),
                                    'content': line.rstrip(),
                                    'search_term': search_term
                                })
                except (UnicodeDecodeError, PermissionError):
                    # 跳过无法读取的文件
                    continue
                except Exception as e:
                    logger.warning(f"读取文件 {file_path} 时出错: {e}")
        
        # 转换为列表格式
        result_list = []
        for file_path, matches in file_matches.items():
            result_list.append({
                'file_path': file_path,
                'matches': matches
            })
        
        logger.info(f"Python搜索找到 {len(result_list)} 个匹配文件，共 {sum(len(item['matches']) for item in result_list)} 个匹配行")
        return result_list