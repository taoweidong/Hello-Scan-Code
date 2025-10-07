"""
平台工具函数
"""
import platform
import subprocess
import os
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

def is_windows() -> bool:
    """
    检查是否为Windows系统
    
    Returns:
        如果是Windows系统返回True，否则返回False
    """
    return platform.system() == "Windows"

def is_unix() -> bool:
    """
    检查是否为Unix系统（Linux/macOS）
    
    Returns:
        如果是Unix系统返回True，否则返回False
    """
    return platform.system() in ["Linux", "Darwin"]

def is_macos() -> bool:
    """
    检查是否为macOS系统
    
    Returns:
        如果是macOS系统返回True，否则返回False
    """
    return platform.system() == "Darwin"

def get_platform() -> str:
    """
    获取平台信息
    
    Returns:
        平台名称
    """
    return platform.system()

def check_command_exists(command: str) -> bool:
    """
    检查命令是否存在
    
    Args:
        command: 命令名称
        
    Returns:
        如果命令存在返回True，否则返回False
    """
    try:
        if is_windows():
            # Windows系统
            result = subprocess.run(["where", command], 
                                  capture_output=True, text=True, timeout=5)
        else:
            # Unix系统
            result = subprocess.run(["which", command], 
                                  capture_output=True, text=True, timeout=5)
        
        return result.returncode == 0 and len(result.stdout.strip()) > 0
    except Exception as e:
        logger.debug(f"检查命令是否存在时出错: {e}")
        return False

def run_command(command: List[str], timeout: int = 30) -> Optional[subprocess.CompletedProcess]:
    """
    运行命令
    
    Args:
        command: 命令列表
        timeout: 超时时间（秒）
        
    Returns:
        命令执行结果
    """
    try:
        # Windows系统需要shell=True
        shell = is_windows()
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=shell
        )
        return result
    except subprocess.TimeoutExpired:
        logger.warning(f"命令执行超时: {' '.join(command)}")
        return None
    except Exception as e:
        logger.error(f"运行命令时出错: {e}")
        return None

def get_cpu_count() -> int:
    """
    获取CPU核心数
    
    Returns:
        CPU核心数
    """
    return os.cpu_count() or 1

def get_memory_info() -> Dict[str, int]:
    """
    获取内存信息
    
    Returns:
        内存信息字典
    """
    try:
        if is_unix():
            # Unix系统
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            # 解析内存信息
            mem_total = 0
            mem_available = 0
            
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) * 1024  # 转换为字节
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1]) * 1024  # 转换为字节
            
            return {
                "total": mem_total,
                "available": mem_available,
                "used": mem_total - mem_available
            }
        else:
            # Windows系统或其他系统
            return {
                "total": 0,
                "available": 0,
                "used": 0
            }
    except Exception as e:
        logger.debug(f"获取内存信息时出错: {e}")
        return {
            "total": 0,
            "available": 0,
            "used": 0
        }