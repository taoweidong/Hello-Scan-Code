import subprocess
import re
import os
from typing import List, Tuple, Dict, Any
from .logger_config import get_logger
from concurrent.futures import ProcessPoolExecutor, as_completed
import chardet
import glob

logger = get_logger()


class SearchEngine:
    """搜索引擎类，包含所有搜索相关功能"""
    
    def __init__(self):
        """初始化搜索引擎"""
        pass
    
    def run_grep_search(self, repo_path: str, search_terms: list[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
        """
        使用grep进行初步搜索（如果可用），否则使用纯Python实现，返回文件路径和匹配的行信息
        支持传入多个关键字一起扫描
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
                return self.run_python_search(repo_path, search_terms, is_regex)
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
    
    def validate_file_content(self, file_info: Dict[str, Any], search_term: str, is_regex: bool = False) -> Dict[str, Any] | None:
        """
        二次校验文件内容，返回验证后的文件信息
        """
        file_path = file_info['file_path']
        encodings = ['utf-8', 'latin-1', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                
                # 验证匹配的行
                validated_matches = []
                for match in file_info['matches']:
                    line_number = int(match['line_number'])
                    if 1 <= line_number <= len(lines):
                        line_content = lines[line_number - 1]  # 行号从1开始，列表索引从0开始
                        
                        if is_regex:
                            if re.search(search_term, line_content):
                                validated_matches.append(match)
                        else:
                            if search_term in line_content:
                                validated_matches.append(match)
                
                # 如果有验证通过的匹配项，返回文件信息
                if validated_matches:
                    return {
                        'file_path': file_path,
                        'matches': validated_matches
                    }
                else:
                    return None
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.warning(f"读取文件 {file_path} 时出错 (编码: {encoding}): {e}")
                break
        
        return None
    
    def run_python_search(self, repo_path: str, search_terms: list[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
        """
        使用纯Python实现搜索功能，支持多个搜索词
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
    
    def _should_ignore_file(self, file_path: str) -> bool:
        """
        判断是否应该忽略该文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否应该忽略该文件
        """
        from .config import SearchConfig
        config = SearchConfig()  # 使用默认配置
        
        # 检查是否在忽略目录中
        if config.ignore_dirs:
            for ignore_dir in config.ignore_dirs:
                if ignore_dir in file_path:
                    return True
        
        # 检查文件后缀
        if config.file_extensions is not None:
            # 获取文件扩展名
            _, ext = os.path.splitext(file_path)
            if ext and ext not in config.file_extensions:
                # 如果有扩展名但不在允许列表中，则忽略
                if config.file_extensions:  # 只有当允许列表不为空时才应用限制
                    return True
        
        return False
    
    def parallel_validate(self, file_results: List[Dict[str, Any]], search_terms: list[str] | str, is_regex: bool, max_workers: int = 4) -> List[Dict[str, Any]]:
        """
        并行二次校验，支持多个搜索词
        """
        # 确保search_terms是列表格式
        if isinstance(search_terms, str):
            search_terms = [search_terms]
        
        validated_results = []
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 对每个搜索词提交任务
            all_futures = []
            for search_term in search_terms:
                futures = {
                    executor.submit(self.validate_file_content, file_info, search_term, is_regex): (file_info['file_path'], search_term) 
                    for file_info in file_results
                }
                all_futures.append(futures)
            
            # 收集所有搜索词的结果
            file_match_map = {}  # 用于存储每个文件的所有匹配项
            for futures in all_futures:
                for future in as_completed(futures):
                    file_path, search_term = futures[future]
                    try:
                        result = future.result()
                        if result:
                            # 将结果按文件路径组织
                            if file_path not in file_match_map:
                                file_match_map[file_path] = {
                                    'file_path': file_path,
                                    'matches': []
                                }
                            file_match_map[file_path]['matches'].extend(result['matches'])
                    except Exception as e:
                        logger.error(f"校验文件 {file_path} (搜索词: {search_term}) 时出错: {e}")
            
            # 转换为列表格式
            validated_results = list(file_match_map.values())
        
        logger.info(f"二次校验完成，找到 {len(validated_results)} 个有效匹配文件")
        return validated_results


# 为了保持向后兼容性，保留原有的函数接口
_search_engine = SearchEngine()

def run_grep_search(repo_path: str, search_terms: list[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
    return _search_engine.run_grep_search(repo_path, search_terms, is_regex)

def validate_file_content(file_info: Dict[str, Any], search_term: str, is_regex: bool = False) -> Dict[str, Any] | None:
    return _search_engine.validate_file_content(file_info, search_term, is_regex)

def run_python_search(repo_path: str, search_terms: list[str] | str, is_regex: bool = False) -> List[Dict[str, Any]]:
    return _search_engine.run_python_search(repo_path, search_terms, is_regex)

def parallel_validate(file_results: List[Dict[str, Any]], search_terms: list[str] | str, is_regex: bool, max_workers: int = 4) -> List[Dict[str, Any]]:
    return _search_engine.parallel_validate(file_results, search_terms, is_regex, max_workers)