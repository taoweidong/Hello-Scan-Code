import subprocess
import re
import os
from typing import List, Tuple, Dict, Any
from .logger_config import get_logger
from concurrent.futures import ProcessPoolExecutor, as_completed
import chardet

logger = get_logger()

def run_grep_search(repo_path: str, search_term: str, is_regex: bool = False) -> List[Dict[str, Any]]:
    """
    使用grep进行初步搜索（如果可用），否则使用纯Python实现，返回文件路径和匹配的行信息
    """
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
                            'search_term': search_term
                        })
            
            # 转换为列表格式
            result_list = []
            for file_path, matches in file_matches.items():
                result_list.append({
                    'file_path': file_path,
                    'matches': matches
                })
            
            logger.info(f"grep找到 {len(result_list)} 个匹配文件，共 {sum(len(item['matches']) for item in result_list)} 个匹配行")
            return result_list
        elif result.returncode == 1:
            # 没有找到匹配项
            logger.info("grep未找到匹配项")
            return []
        else:
            logger.warning(f"grep命令执行失败: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.warning("grep命令执行超时")
    except FileNotFoundError:
        logger.warning("未找到grep命令，将使用纯Python实现搜索")
    except Exception as e:
        logger.warning(f"执行grep搜索时出错: {e}")
    
    # 如果grep不可用，使用纯Python实现
    return run_python_search(repo_path, search_term, is_regex)

def validate_file_content(file_info: Dict[str, Any], search_term: str, is_regex: bool = False) -> Dict[str, Any] | None:
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

def run_python_search(repo_path: str, search_term: str, is_regex: bool = False) -> List[Dict[str, Any]]:
    """
    使用纯Python实现搜索功能
    """
    import glob
    
    file_matches = {}
    
    # 递归搜索所有文件
    for file_path in glob.glob(os.path.join(repo_path, '**/*'), recursive=True):
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 搜索匹配的行
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

def parallel_validate(file_results: List[Dict[str, Any]], search_term: str, is_regex: bool, max_workers: int = 4) -> List[Dict[str, Any]]:
    """
    并行二次校验
    """
    validated_results = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_file = {
            executor.submit(validate_file_content, file_info, search_term, is_regex): file_info['file_path'] 
            for file_info in file_results
        }
        
        # 收集结果
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    validated_results.append(result)
            except Exception as e:
                logger.error(f"校验文件 {file_path} 时出错: {e}")
    
    logger.info(f"二次校验完成，找到 {len(validated_results)} 个有效匹配文件")
    return validated_results