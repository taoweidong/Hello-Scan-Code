"""
Grep预扫描器 - 使用系统grep进行高性能初筛
"""
import subprocess
import os
import platform
from typing import Generator, Tuple, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GrepScanner:
    """Grep预扫描器"""
    
    def __init__(self, repo_path: str, ignore_dirs: List[str] = None, 
                 timeout: int = 300):
        self.repo_path = Path(repo_path).resolve()
        self.ignore_dirs = ignore_dirs or []
        self.timeout = timeout
        self.is_windows = platform.system() == "Windows"
        
    def scan(self, pattern: str, file_extensions: List[str] = None) -> Generator[Tuple[str, int, str], None, None]:
        """
        执行grep扫描
        
        Args:
            pattern: 搜索模式
            file_extensions: 文件扩展名过滤
            
        Yields:
            (文件路径, 行号, 行内容)
        """
        if self.is_windows:
            yield from self._scan_windows(pattern, file_extensions)
        else:
            yield from self._scan_unix(pattern, file_extensions)
    
    def _scan_unix(self, pattern: str, file_extensions: List[str]) -> Generator[Tuple[str, int, str], None, None]:
        """Unix系统grep扫描"""
        try:
            cmd = [
                "grep", 
                "-rn",           # 递归，显示行号
                "--binary-files=without-match",  # 跳过二进制文件
                "-I",            # 忽略二进制文件
            ]
            
            # 文件类型过滤
            if file_extensions:
                for ext in file_extensions:
                    cmd.extend(["--include", f"*{ext}"])
            
            # 忽略目录
            for ignore_dir in self.ignore_dirs:
                cmd.extend(["--exclude-dir", ignore_dir])
            
            # 添加模式和路径
            cmd.extend(["-E", pattern, str(self.repo_path)])
            
            logger.debug(f"执行grep命令: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            try:
                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析grep输出格式: path:line:content
                    parts = line.split(':', 2)
                    if len(parts) == 3:
                        file_path, line_no, content = parts
                        # 转换为相对路径
                        rel_path = os.path.relpath(file_path, self.repo_path)
                        yield rel_path, int(line_no), content
                    
                # 等待进程完成
                process.wait(timeout=self.timeout)
                
            except subprocess.TimeoutExpired:
                logger.warning("Grep扫描超时")
                process.terminate()
                
        except FileNotFoundError:
            logger.error("系统中未找到grep命令")
            raise RuntimeError("grep command not found. Please install grep or use WSL on Windows.")
        except Exception as e:
            logger.error(f"Grep扫描失败: {e}")
            raise
    
    def _scan_windows(self, pattern: str, file_extensions: List[str]) -> Generator[Tuple[str, int, str], None, None]:
        """Windows系统扫描（使用findstr）"""
        try:
            # Windows使用findstr命令
            cmd = [
                "findstr",
                "/S",           # 递归搜索
                "/N",           # 显示行号
                "/R",           # 使用正则
                pattern
            ]
            
            # 构建搜索路径
            search_path = str(self.repo_path)
            if file_extensions:
                # Windows不支持像grep那样的include，这里简化处理
                pass
            
            cmd.append(search_path)
            
            logger.debug(f"执行findstr命令: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True  # Windows需要shell
            )
            
            try:
                for line in process.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 解析findstr输出格式: path(line): content
                    if '(' in line and ')' in line:
                        file_part, content = line.split(')', 1)
                        if '(' in file_part:
                            file_path, line_no = file_part.split('(')
                            file_path = file_path.strip()
                            line_no = line_no.strip()
                            
                            # 转换为相对路径
                            rel_path = os.path.relpath(file_path, self.repo_path)
                            yield rel_path, int(line_no), content.strip()
                
                process.wait(timeout=self.timeout)
                
            except subprocess.TimeoutExpired:
                logger.warning("Findstr扫描超时")
                process.terminate()
                
        except Exception as e:
            logger.error(f"Windows扫描失败: {e}")
            # 回退到Python实现
            yield from self._fallback_scan(pattern, file_extensions)
    
    def _fallback_scan(self, pattern: str, file_extensions: List[str]) -> Generator[Tuple[str, int, str], None, None]:
        """回退的Python实现扫描"""
        import re
        
        logger.info("使用Python回退扫描")
        pattern_re = re.compile(pattern)
        
        for root, dirs, files in os.walk(self.repo_path):
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                file_path = Path(root) / file
                
                # 文件扩展名过滤
                if file_extensions and file_path.suffix not in file_extensions:
                    continue
                
                # 转换为相对路径
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_no, line in enumerate(f, 1):
                            if pattern_re.search(line):
                                yield rel_path, line_no, line.strip()
                except Exception as e:
                    logger.debug(f"读取文件失败 {file_path}: {e}")