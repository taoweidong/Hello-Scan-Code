"""
文件工具函数
"""
import os
import hashlib
from pathlib import Path
from typing import List, Generator, Optional
import logging

logger = logging.getLogger(__name__)

def get_file_hash(file_path: str, algorithm: str = "md5") -> str:
    """
    计算文件的哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (默认md5)
        
    Returns:
        文件的哈希值
    """
    try:
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"计算文件哈希值失败: {e}")
        return ""

def is_binary_file(file_path: str) -> bool:
    """
    判断文件是否为二进制文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        如果是二进制文件返回True，否则返回False
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:
                return True
            return False
    except Exception as e:
        logger.debug(f"判断文件是否为二进制文件时出错: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """
    获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except Exception as e:
        logger.debug(f"获取文件大小失败: {e}")
        return 0

def walk_files(directory: str, extensions: Optional[List[str]] = None, 
               ignore_dirs: Optional[List[str]] = None) -> Generator[str, None, None]:
    """
    遍历目录中的文件
    
    Args:
        directory: 目录路径
        extensions: 文件扩展名列表（可选）
        ignore_dirs: 忽略的目录列表（可选）
        
    Yields:
        文件路径
    """
    ignore_dirs = ignore_dirs or []
    directory_path = Path(directory)
    
    for item in directory_path.rglob('*'):
        if item.is_file():
            # 检查是否在忽略目录中
            if any(ignore_dir in str(item) for ignore_dir in ignore_dirs):
                continue
            
            # 检查文件扩展名
            if extensions and item.suffix not in extensions:
                continue
            
            yield str(item)

def ensure_directory_exists(directory: str):
    """
    确保目录存在
    
    Args:
        directory: 目录路径
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"创建目录失败: {e}")
        raise

def read_file_content(file_path: str, encoding: str = 'utf-8') -> str:
    """
    读取文件内容
    
    Args:
        file_path: 文件路径
        encoding: 文件编码
        
    Returns:
        文件内容
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            return f.read()
    except Exception as e:
        logger.debug(f"读取文件内容失败: {e}")
        return ""