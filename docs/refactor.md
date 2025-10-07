```markdown
# Hello-Scan-Code 插件化架构完整实现方案

> **项目名称**：Hello-Scan-Code  
> **版本**：v2.1.0  
> **更新时间**：2025年10月7日  
> **目标**：专为大型代码仓库设计的高效搜索工具，支持自定义插件、自定义扫描规则，支持海量文件扫描，高性能、易扩展。

---

## 📌 项目概述

`Hello-Scan-Code` 是一个面向大型代码仓库的静态分析工具，采用 **插件化架构 + `grep` 预筛选 + 插件精准分析** 的双阶段扫描机制，显著提升扫描性能，同时保持高度可扩展性。

本方案支持：
- ✅ 使用 `grep` 进行初筛（Linux/macOS）或 `findstr`（Windows）
- ✅ 插件定义 `grep` 模式和精准分析逻辑
- ✅ 流式处理，内存友好
- ✅ 支持自定义插件开发
- ✅ 结果聚合与多格式导出（Excel、数据库、HTML）

---

## 🗂️ 项目目录结构

```bash
hello-scan-code/
├── README.md                          # 项目说明文档
├── requirements.txt                   # Python依赖
├── pyproject.toml                    # 项目配置
├── main.py                           # 程序主入口
├── config.json                       # 主配置文件
├── Makefile                          # 构建脚本
├── scripts/                          # 构建和工具脚本
│   ├── build_linux.py
│   ├── build_windows.py
│   └── install_plugins.py
├── src/                              # 源代码目录
│   ├── __init__.py
│   ├── main.py                       # 主程序入口
│   ├── engine/                       # 扫描引擎核心
│   │   ├── __init__.py
│   │   ├── scan_engine.py            # 优化扫描引擎
│   │   ├── grep_scanner.py           # Grep预扫描器
│   │   ├── plugin_processor.py       # 插件处理器
│   │   └── result_aggregator.py      # 结果聚合器
│   ├── plugin/                       # 插件系统
│   │   ├── __init__.py
│   │   ├── base.py                   # 插件基础接口
│   │   ├── manager.py                # 插件管理器
│   │   ├── registry.py               # 插件注册表
│   │   ├── discovery.py              # 插件发现服务
│   │   └── events.py                 # 插件事件系统
│   ├── config/                       # 配置管理
│   │   ├── __init__.py
│   │   ├── config_manager.py
│   │   ├── plugin_config.py          # 插件专用配置
│   │   └── models.py                 # 配置数据模型
│   ├── database/                     # 数据库模块
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── models.py
│   │   └── repositories.py
│   ├── exporters/                    # 结果导出器
│   │   ├── __init__.py
│   │   ├── excel_exporter.py
│   │   ├── database_exporter.py
│   │   └── html_exporter.py
│   ├── utils/                        # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── text_utils.py
│   │   └── platform_utils.py
│   └── plugins/                      # 内置插件目录
│       ├── __init__.py
│       ├── builtin/                  # 内置插件
│       │   ├── __init__.py
│       │   ├── keyword_plugin.py     # 关键字扫描插件
│       │   ├── regex_plugin.py       # 正则表达式插件
│       │   ├── todo_plugin.py        # TODO检测插件
│       │   └── security_plugin.py    # 安全检测插件
│       └── custom/                   # 自定义插件目录
│           ├── __init__.py
│           └── README.md
├── tests/                            # 测试目录
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_scan_engine.py
│   │   ├── test_grep_scanner.py
│   │   ├── test_plugin_manager.py
│   │   └── test_plugins.py
│   ├── integration/
│   │   ├── test_workflow.py
│   │   └── test_performance.py
│   └── fixtures/                     # 测试数据
│       ├── test_repo/
│       └── test_plugins/
├── docs/                             # 文档目录
│   ├── plugin_development_guide.md
│   ├── api_reference.md
│   └── performance_guide.md
├── logs/                             # 日志目录
├── db/                               # 数据库目录
├── report/                           # 报告输出目录
└── plugins/                          # 用户插件目录（外部）
    ├── __init__.py
    └── README.md
```

---

## ⚙️ 核心模块实现

### 1. 插件基础接口 (`src/plugin/base.py`)

```python
"""
插件系统基础接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import os

class SeverityLevel(Enum):
    """问题严重级别"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ScanResult:
    """扫描结果数据模型"""
    plugin_id: str
    file_path: str
    line_number: int
    column: int = 0
    message: str = ""
    severity: SeverityLevel = SeverityLevel.MEDIUM
    rule_id: str = ""
    category: str = ""
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

@dataclass
class ScanContext:
    """扫描上下文信息"""
    repo_path: str
    file_encoding: str = "utf-8"
    config: Dict[str, Any] = None
    extra_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.extra_context is None:
            self.extra_context = {}

class IScanPlugin(ABC):
    """扫描插件基础接口"""
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """插件唯一标识"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """插件显示名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """插件描述"""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """插件作者"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """返回支持的文件扩展名列表"""
        pass
    
    @abstractmethod
    def get_grep_pattern(self) -> Optional[str]:
        """
        返回用于grep预扫描的正则表达式
        返回None表示跳过grep阶段（全量扫描）
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        pass
    
    @abstractmethod
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: ScanContext) -> List[ScanResult]:
        """
        扫描单行内容（grep匹配后调用）
        """
        pass
    
    def scan_file(self, file_path: str, file_content: str, 
                 context: ScanContext) -> List[ScanResult]:
        """
        扫描整个文件（可选实现，用于不支持grep的插件）
        """
        return []
    
    def cleanup(self):
        """清理插件资源"""
        pass
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回插件配置schema"""
        return {}

class IAdvancedScanPlugin(IScanPlugin):
    """高级扫描插件接口（支持项目级分析）"""
    
    @abstractmethod
    def scan_project(self, project_path: str, context: ScanContext) -> List[ScanResult]:
        """扫描整个项目"""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """返回依赖的插件列表"""
        pass
```

---

### 2. Grep预扫描器 (`src/engine/grep_scanner.py`)

```python
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
```

---

### 3. 插件管理器 (`src/plugin/manager.py`)

```python
"""
插件管理器 - 负责插件的加载、注册和生命周期管理
"""
import importlib
import inspect
import pkgutil
from typing import Dict, List, Type, Optional, Any
from pathlib import Path
import logging
from .base import IScanPlugin, IAdvancedScanPlugin
from .registry import PluginRegistry
from .discovery import PluginDiscovery

logger = logging.getLogger(__name__)

class PluginManager:
    """插件管理器"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.registry = PluginRegistry()
        self.discovery = PluginDiscovery()
        self.plugins: Dict[str, IScanPlugin] = {}
        self._initialized = False
        
    def initialize(self) -> bool:
        """初始化插件管理器"""
        if self._initialized:
            return True
            
        try:
            # 加载内置插件
            self._load_builtin_plugins()
            
            # 加载外部插件
            plugin_dirs = self.config_manager.get_plugin_dirs()
            for plugin_dir in plugin_dirs:
                if Path(plugin_dir).exists():
                    self._load_external_plugins(plugin_dir)
            
            # 初始化所有插件
            self._initialize_plugins()
            
            self._initialized = True
            logger.info(f"插件管理器初始化完成，加载了 {len(self.plugins)} 个插件")
            return True
            
        except Exception as e:
            logger.error(f"插件管理器初始化失败: {e}")
            return False
    
    def _load_builtin_plugins(self):
        """加载内置插件"""
        try:
            # 动态导入内置插件包
            from ..plugins import builtin
            builtin_path = Path(builtin.__file__).parent
            
            for module_info in pkgutil.iter_modules([str(builtin_path)]):
                if module_info.ispkg:
                    continue
                    
                module_name = f"src.plugins.builtin.{module_info.name}"
                self._load_plugin_module(module_name)
                
        except Exception as e:
            logger.error(f"加载内置插件失败: {e}")
    
    def _load_external_plugins(self, plugin_dir: str):
        """加载外部插件"""
        plugin_path = Path(plugin_dir)
        
        for item in plugin_path.iterdir():
            if item.is_file() and item.suffix == '.py' and item.name != '__init__.py':
                # 直接导入Python文件
                try:
                    spec = importlib.util.spec_from_file_location(item.stem, item)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._register_plugins_from_module(module)
                    
                except Exception as e:
                    logger.error(f"加载插件文件 {item} 失败: {e}")
                    
            elif item.is_dir() and (item / '__init__.py').exists():
                # 导入插件包
                package_name = item.name
                try:
                    module = importlib.import_module(f"plugins.{package_name}")
                    self._register_plugins_from_module(module)
                    
                except Exception as e:
                    logger.error(f"加载插件包 {package_name} 失败: {e}")
    
    def _load_plugin_module(self, module_name: str):
        """加载插件模块"""
        try:
            module = importlib.import_module(module_name)
            self._register_plugins_from_module(module)
        except Exception as e:
            logger.error(f"加载插件模块 {module_name} 失败: {e}")
    
    def _register_plugins_from_module(self, module):
        """从模块中注册所有插件类"""
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, IScanPlugin) and 
                obj != IScanPlugin and 
                obj != IAdvancedScanPlugin):
                
                try:
                    plugin_instance = obj()
                    self.registry.register_plugin(plugin_instance)
                    logger.debug(f"注册插件: {plugin_instance.plugin_id}")
                except Exception as e:
                    logger.error(f"注册插件 {name} 失败: {e}")
    
    def _initialize_plugins(self):
        """初始化所有插件"""
        plugin_configs = self.config_manager.get_plugin_configs()
        
        for plugin in self.registry.get_all_plugins():
            plugin_id = plugin.plugin_id
            config = plugin_configs.get(plugin_id, {})
            
            try:
                if plugin.initialize(config):
                    self.plugins[plugin_id] = plugin
                    logger.info(f"插件 {plugin_id} 初始化成功")
                else:
                    logger.warning(f"插件 {plugin_id} 初始化失败")
            except Exception as e:
                logger.error(f"初始化插件 {plugin_id} 时出错: {e}")
    
    def get_enabled_plugins(self) -> List[IScanPlugin]:
        """获取所有启用的插件"""
        return list(self.plugins.values())
    
    def get_plugin(self, plugin_id: str) -> Optional[IScanPlugin]:
        """根据ID获取插件"""
        return self.plugins.get(plugin_id)
    
    def get_plugins_by_extension(self, extension: str) -> List[IScanPlugin]:
        """获取支持指定文件扩展名的插件"""
        return [
            plugin for plugin in self.plugins.values()
            if extension in plugin.get_supported_extensions()
        ]
    
    def reload_plugin(self, plugin_id: str) -> bool:
        """重新加载插件"""
        # 实现插件热重载逻辑
        pass
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            del self.plugins[plugin_id]
            return True
        return False
```

---

### 4. 优化扫描引擎 (`src/engine/scan_engine.py`)

```python
"""
优化扫描引擎 - 双阶段扫描架构
"""
import time
from typing import List, Dict, Any
from collections import defaultdict
import logging
from pathlib import Path

from .grep_scanner import GrepScanner
from .plugin_processor import PluginProcessor
from .result_aggregator import ResultAggregator
from ..plugin.base import IScanPlugin, ScanContext, ScanResult
from ..config.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class OptimizedScanEngine:
    """优化扫描引擎 - 采用grep预筛选 + 插件精准分析"""
    
    def __init__(self, config_manager: ConfigManager, plugin_manager):
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        self.grep_scanner = None
        self.plugin_processor = None
        self.result_aggregator = ResultAggregator()
        self.stats = {
            'total_files': 0,
            'scanned_files': 0,
            'total_plugins': 0,
            'scan_time': 0,
            'results_count': 0
        }
    
    def scan(self, repo_path: str = None) -> List[ScanResult]:
        """
        执行代码扫描
        
        Args:
            repo_path: 代码仓库路径，为None时使用配置中的路径
            
        Returns:
            扫描结果列表
        """
        start_time = time.time()
        
        # 获取配置
        if repo_path is None:
            repo_path = self.config_manager.get_repo_path()
        
        ignore_dirs = self.config_manager.get_ignore_dirs()
        file_extensions = self.config_manager.get_file_extensions()
        
        # 初始化扫描器
        self.grep_scanner = GrepScanner(repo_path, ignore_dirs)
        self.plugin_processor = PluginProcessor(self.plugin_manager)
        
        # 获取启用的插件
        enabled_plugins = self.plugin_manager.get_enabled_plugins()
        self.stats['total_plugins'] = len(enabled_plugins)
        
        logger.info(f"开始扫描仓库: {repo_path}")
        logger.info(f"启用插件数量: {len(enabled_plugins)}")
        
        # 按grep模式分组插件
        pattern_groups = self._group_plugins_by_pattern(enabled_plugins)
        
        all_results = []
        
        # 第一阶段：grep预扫描 + 插件精准分析
        for pattern, plugins in pattern_groups.items():
            if pattern:  # 使用grep优化的插件
                logger.info(f"使用grep模式扫描: {pattern}")
                results = self._scan_with_grep(pattern, plugins, repo_path, file_extensions)
                all_results.extend(results)
        
        # 第二阶段：全量扫描插件（不支持grep的插件）
        fallback_plugins = [p for p in enabled_plugins if not p.get_grep_pattern()]
        if fallback_plugins:
            logger.info(f"执行全量扫描插件: {len(fallback_plugins)} 个")
            results = self._scan_fallback(fallback_plugins, repo_path, file_extensions)
            all_results.extend(results)
        
        # 聚合结果
        aggregated_results = self.result_aggregator.aggregate(all_results)
        
        # 更新统计信息
        self.stats['scan_time'] = time.time() - start_time
        self.stats['results_count'] = len(aggregated_results)
        
        logger.info(f"扫描完成，耗时: {self.stats['scan_time']:.2f}s")
        logger.info(f"发现问题: {self.stats['results_count']} 个")
        
        return aggregated_results
    
    def _group_plugins_by_pattern(self, plugins: List[IScanPlugin]) -> Dict[str, List[IScanPlugin]]:
        """按grep模式分组插件"""
        groups = defaultdict(list)
        
        for plugin in plugins:
            pattern = plugin.get_grep_pattern()
            if pattern:
                # 合并相同的模式
                groups[pattern].append(plugin)
            else:
                # 无grep模式的插件单独分组
                groups[None].append(plugin)
        
        return dict(groups)
    
    def _scan_with_grep(self, pattern: str, plugins: List[IScanPlugin], 
                       repo_path: str, file_extensions: List[str]) -> List[ScanResult]:
        """使用grep预扫描进行优化扫描"""
        results = []
        
        try:
            # 执行grep扫描
            grep_stream = self.grep_scanner.scan(pattern, file_extensions)
            
            # 创建扫描上下文
            context = ScanContext(repo_path=repo_path)
            
            # 处理grep结果
            for file_path, line_no, line_content in grep_stream:
                # 对每个匹配的行执行插件分析
                for plugin in plugins:
                    # 检查文件类型支持
                    file_ext = Path(file_path).suffix
                    if file_ext not in plugin.get_supported_extensions():
                        continue
                    
                    # 执行插件扫描
                    plugin_results = plugin.scan_line(
                        file_path, line_no, line_content, context
                    )
                    results.extend(plugin_results)
                    
        except Exception as e:
            logger.error(f"Grep扫描失败: {e}")
        
        return results
    
    def _scan_fallback(self, plugins: List[IScanPlugin], repo_path: str, 
                      file_extensions: List[str]) -> List[ScanResult]:
        """全量扫描回退方案"""
        results = []
        context = ScanContext(repo_path=repo_path)
        
        # 遍历所有文件
        for file_path in self._walk_files(repo_path, file_extensions):
            try:
                file_ext = Path(file_path).suffix
                full_path = Path(repo_path) / file_path
                
                # 读取文件内容
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 对每个插件执行文件扫描
                for plugin in plugins:
                    if file_ext in plugin.get_supported_extensions():
                        plugin_results = plugin.scan_file(
                            file_path, content, context
                        )
                        results.extend(plugin_results)
                        
            except Exception as e:
                logger.debug(f"扫描文件 {file_path} 失败: {e}")
        
        return results
    
    def _walk_files(self, repo_path: str, file_extensions: List[str]):
        """遍历代码文件"""
        repo_path = Path(repo_path)
        ignore_dirs = self.config_manager.get_ignore_dirs()
        
        for item in repo_path.rglob('*'):
            if item.is_file():
                # 检查忽略目录
                if any(ignore in str(item) for ignore in ignore_dirs):
                    continue
                
                # 文件扩展名过滤
                if file_extensions and item.suffix not in file_extensions:
                    continue
                
                yield str(item.relative_to(repo_path))
    
    def get_stats(self) -> Dict[str, Any]:
        """获取扫描统计信息"""
        return self.stats.copy()
```

---

### 5. 内置插件示例

#### 关键字扫描插件 (`src/plugins/builtin/keyword_plugin.py`)

```python
"""
内置关键字扫描插件
"""
from typing import List, Dict, Any
import re
from ..plugin.base import IScanPlugin, ScanResult, ScanContext, SeverityLevel

class KeywordScanPlugin(IScanPlugin):
    """关键字扫描插件"""
    
    @property
    def plugin_id(self) -> str:
        return "builtin.keyword"
    
    @property
    def name(self) -> str:
        return "Keyword Scanner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "基于关键字的代码扫描插件"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"
    
    def __init__(self):
        self.keywords = []
        self.case_sensitive = False
        self.initialized = False
    
    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".php"]
    
    def get_grep_pattern(self) -> str:
        """构建grep搜索模式"""
        if not self.keywords:
            return ""
        
        # 将关键字转换为grep兼容的正则
        pattern = "|".join(re.escape(keyword) for keyword in self.keywords)
        return pattern
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            self.keywords = config.get("keywords", ["TODO", "FIXME", "BUG", "HACK"])
            self.case_sensitive = config.get("case_sensitive", False)
            self.initialized = True
            return True
        except Exception:
            return False
    
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: ScanContext) -> List[ScanResult]:
        """扫描单行内容"""
        if not self.initialized:
            return []
        
        results = []
        
        for keyword in self.keywords:
            if self.case_sensitive:
                found = keyword in line_content
            else:
                found = keyword.lower() in line_content.lower()
            
            if found:
                # 确定严重级别
                severity = self._get_severity_for_keyword(keyword)
                
                result = ScanResult(
                    plugin_id=self.plugin_id,
                    file_path=file_path,
                    line_number=line_number,
                    message=f"发现关键字: {keyword}",
                    severity=severity,
                    rule_id=f"KEYWORD_{keyword}",
                    category="code_style",
                    suggestion="考虑处理或移除该标记",
                    code_snippet=line_content.strip()
                )
                results.append(result)
        
        return results
    
    def _get_severity_for_keyword(self, keyword: str) -> SeverityLevel:
        """根据关键字确定严重级别"""
        severity_map = {
            "TODO": SeverityLevel.LOW,
            "FIXME": SeverityLevel.MEDIUM, 
            "HACK": SeverityLevel.MEDIUM,
            "BUG": SeverityLevel.HIGH,
            "XXX": SeverityLevel.MEDIUM,
        }
        return severity_map.get(keyword.upper(), SeverityLevel.LOW)
    
    def get_config_schema(self) -> Dict[str, Any]:
        """返回配置schema"""
        return {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "要搜索的关键字列表",
                    "default": ["TODO", "FIXME", "BUG", "HACK"]
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "是否区分大小写",
                    "default": False
                }
            }
        }
```

#### 安全检测插件 (`src/plugins/builtin/security_plugin.py`)

```python
"""
安全检测插件
"""
from typing import List, Dict, Any
import re
from ..plugin.base import IScanPlugin, ScanResult, ScanContext, SeverityLevel

class SecurityScanPlugin(IScanPlugin):
    """安全敏感信息检测插件"""
    
    @property
    def plugin_id(self) -> str:
        return "builtin.security"
    
    @property
    def name(self) -> str:
        return "Security Scanner"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "检测代码中的安全敏感信息"
    
    @property
    def author(self) -> str:
        return "Hello-Scan-Code Team"
    
    def get_supported_extensions(self) -> List[str]:
        return [".py", ".js", ".java", ".go", ".yaml", ".yml", ".json"]
    
    def get_grep_pattern(self) -> str:
        return r"password|passwd|secret|token|key|pwd"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        return True
    
    def scan_line(self, file_path: str, line_number: int, line_content: str, 
                 context: ScanContext) -> List[ScanResult]:
        patterns = {
            r'password\s*=\s*["\'][^"\']*["\']': ("PASSWORD_LITERAL", "硬编码密码"),
            r'api[_-]?key\s*=\s*["\'][^"\']*["\']': ("API_KEY_LITERAL", "硬编码API密钥"),
            r'secret[_-]?token\s*=\s*["\'][^"\']*["\']': ("SECRET_TOKEN", "硬编码密钥")
        }
        
        results = []
        for pattern, (rule_id, desc) in patterns.items():
            if re.search(pattern, line_content, re.I):
                results.append(ScanResult(
                    plugin_id=self.plugin_id,
                    file_path=file_path,
                    line_number=line_number,
                    message=desc,
                    severity=SeverityLevel.CRITICAL,
                    rule_id=rule_id,
                    category="security",
                    suggestion="请使用环境变量或密钥管理服务",
                    code_snippet=line_content.strip()
                ))
        
        return results
```

---

## ✅ 使用说明

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 `config.json`

```json
{
  "repo_path": "/path/to/your/code",
  "ignore_dirs": ["node_modules", "venv", ".git", "dist"],
  "file_extensions": [".py", ".js", ".java", ".go"],
  "plugins": {
    "enabled": ["builtin.keyword", "builtin.security"],
    "dirs": ["plugins/"]
  },
  "output": {
    "report_dir": "report/",
    "export_formats": ["excel", "html"]
  }
}
```

### 3. 运行扫描

```bash
python main.py
```

---

## 📦 下载与使用

此设计文档可直接作为项目骨架使用。完整代码结构已提供，开发者只需：

1. 创建目录结构
2. 复制各模块代码
3. 实现缺失模块（如 `result_aggregator.py`、`exporters/`）
4. 编写 `main.py` 入口

即可构建一个高性能、可扩展的代码扫描工具。

> **文档结束**  
> 本方案已通过模块化、接口抽象、双阶段扫描等设计，确保高性能与高扩展性，适用于企业级代码治理。
```