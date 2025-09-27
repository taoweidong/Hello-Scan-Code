# 设计模式应用规范

## 概述

Hello-Scan-Code系统应用了四种核心设计模式，通过合理的模式组合实现了高内聚、低耦合的架构设计。

## 1. 模板方法模式 (Template Method Pattern)

### 应用场景
SearchTemplate类族中统一搜索流程控制。

### 核心实现

```python
from abc import ABC, abstractmethod

class SearchTemplate(ABC):
    """搜索模板抽象类"""
    
    def search(self) -> List[Dict[str, Any]]:
        """模板方法 - 定义算法骨架"""
        # 1. 统计文件
        file_count = self._count_files()
        
        # 2. 解析搜索词
        search_terms = self._parse_search_terms()
        
        # 3. 创建策略 (抽象方法)
        self.strategy = self._create_search_strategy()
        
        # 4. 执行搜索
        results = self._perform_initial_search(search_terms)
        
        # 5. 验证结果 (抽象方法)
        if self.config.enable_second_check:
            results = self._perform_validation(results, search_terms)
            
        return results
    
    # 具体方法
    def _count_files(self) -> int:
        """统计文件数量"""
        pass
    
    def _parse_search_terms(self):
        """解析搜索词"""
        pass
    
    def _perform_initial_search(self, terms):
        """执行初始搜索"""
        return self.strategy.search(self.config.repo_path, terms, self.config.is_regex)
    
    # 抽象方法
    @abstractmethod
    def _create_search_strategy(self) -> SearchStrategy:
        pass
    
    @abstractmethod
    def _perform_validation(self, results, terms) -> List[Dict[str, Any]]:
        pass

class DefaultSearchTemplate(SearchTemplate):
    """默认搜索模板实现"""
    
    def _create_search_strategy(self) -> SearchStrategy:
        from .search_factory import SearchStrategyFactory
        return SearchStrategyFactory.create_default_strategy(self.config)
    
    def _perform_validation(self, results, terms):
        from .validators import ResultValidator
        validator = ResultValidator(self.config)
        return validator.parallel_validate(results, terms)
```

### 设计优势
- 稳定的算法结构
- 易于扩展新的搜索流程
- 代码复用性高
- 符合开闭原则

## 2. 策略模式 (Strategy Pattern)

### 应用场景
SearchStrategy类族中实现不同搜索算法。

### 核心实现

```python
from abc import ABC, abstractmethod

class SearchStrategy(ABC):
    """搜索策略抽象接口"""
    
    @abstractmethod
    def search(self, repo_path: str, search_terms, is_regex: bool) -> List[Dict[str, Any]]:
        pass

class GrepSearchStrategy(SearchStrategy):
    """基于Grep的高性能搜索策略"""
    
    def search(self, repo_path: str, search_terms, is_regex: bool):
        # 构建grep命令
        cmd = self._build_grep_command(search_terms, is_regex)
        # 执行系统命令
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        # 解析输出
        return self._parse_grep_output(result.stdout)

class PythonSearchStrategy(SearchStrategy):
    """基于Python的跨平台搜索策略"""
    
    def search(self, repo_path: str, search_terms, is_regex: bool):
        results = []
        # 遍历文件
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_results = self._search_in_file(file_path, search_terms, is_regex)
                results.extend(file_results)
        return results
```

### 设计优势
- 算法独立可切换
- 运行时动态选择
- 易于扩展新算法
- 性能针对性优化

## 3. 工厂模式 (Factory Pattern)

### 应用场景
SearchStrategyFactory负责策略对象的创建和管理。

### 核心实现

```python
class SearchStrategyFactory:
    """搜索策略工厂类"""
    
    _strategies = {
        'grep': GrepSearchStrategy,
        'python': PythonSearchStrategy,
    }
    
    @staticmethod
    def create_strategy(strategy_type: str, config: SearchConfig) -> SearchStrategy:
        """根据类型创建策略"""
        if strategy_type == 'auto':
            return SearchStrategyFactory.create_default_strategy(config)
        
        if strategy_type not in SearchStrategyFactory._strategies:
            raise ValueError(f"不支持的策略类型: {strategy_type}")
        
        strategy_class = SearchStrategyFactory._strategies[strategy_type]
        return strategy_class(config)
    
    @staticmethod
    def create_default_strategy(config: SearchConfig) -> SearchStrategy:
        """自动选择最优策略"""
        if SearchStrategyFactory._is_grep_available():
            return GrepSearchStrategy(config)
        else:
            return PythonSearchStrategy(config)
    
    @staticmethod
    def _is_grep_available() -> bool:
        """检查grep可用性"""
        try:
            if os.name == 'nt':  # Windows系统
                return False
            result = subprocess.run(['grep', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    @staticmethod
    def register_strategy(name: str, strategy_class):
        """注册新策略"""
        SearchStrategyFactory._strategies[name] = strategy_class
```

### 设计优势
- 解耦对象创建与使用
- 集中管理策略类型
- 支持动态策略注册
- 智能环境检测

## 4. 外观模式 (Facade Pattern)

### 应用场景
CodeSearcher作为系统统一入口，简化复杂子系统使用。

### 核心实现

```python
class CodeSearcher:
    """代码搜索器外观类"""
    
    def __init__(self, config: SearchConfig):
        self.config = config
        self._initialize_components()
    
    def _initialize_components(self):
        """初始化所有组件"""
        self.search_template = DefaultSearchTemplate(self.config)
        self.db_manager = DatabaseManager(self.config.db_path)
        self.excel_exporter = ExcelExporter(self.config.excel_path)
    
    def search(self) -> List[Dict[str, Any]]:
        """执行搜索 - 简化接口"""
        return self.search_template.search()
    
    def save_results(self, results: List[Dict[str, Any]]):
        """保存结果 - 简化接口"""
        # 保存到数据库
        self.db_manager.save_results(results)
        # 导出到Excel
        self.excel_exporter.export_to_excel(results)
    
    def search_and_save(self) -> Dict[str, Any]:
        """一键搜索并保存 - 最简接口"""
        results = self.search()
        if results:
            self.save_results(results)
        return {'success': True, 'result_count': len(results)}
```

### 设计优势
- 简化复杂子系统接口
- 提供统一访问入口
- 降低客户端耦合度
- 减少学习成本

## 模式协作关系

```mermaid
graph TB
    subgraph "外观模式"
        CodeSearcher[CodeSearcher]
    end
    
    subgraph "模板方法模式"
        SearchTemplate[SearchTemplate]
        DefaultTemplate[DefaultSearchTemplate]
    end
    
    subgraph "工厂模式"
        Factory[SearchStrategyFactory]
    end
    
    subgraph "策略模式"
        Strategy[SearchStrategy]
        GrepStrategy[GrepSearchStrategy]
        PythonStrategy[PythonSearchStrategy]
    end
    
    CodeSearcher --> DefaultTemplate
    DefaultTemplate --> Factory
    Factory --> GrepStrategy
    Factory --> PythonStrategy
    SearchTemplate <|-- DefaultTemplate
    Strategy <|.. GrepStrategy
    Strategy <|.. PythonStrategy
```

## 扩展指导

### 添加新搜索策略

```python
# 1. 实现策略接口
class ElasticsearchStrategy(SearchStrategy):
    def search(self, repo_path: str, search_terms, is_regex: bool):
        # 实现Elasticsearch搜索逻辑
        pass

# 2. 注册到工厂
SearchStrategyFactory.register_strategy('elasticsearch', ElasticsearchStrategy)

# 3. 使用新策略
config = SearchConfig(search_strategy="elasticsearch", ...)
```

### 扩展搜索模板

```python
class CustomSearchTemplate(SearchTemplate):
    def _create_search_strategy(self):
        return CustomSearchStrategy(self.config)
    
    def _perform_validation(self, results, terms):
        return custom_validate(results, terms)
```

## 总结

通过合理应用四种设计模式，Hello-Scan-Code实现了：
- **灵活的架构**: 支持多种搜索策略和扩展
- **稳定的流程**: 统一的搜索算法框架
- **简单的接口**: 易用的外观接口
- **解耦的设计**: 低耦合高内聚的模块结构

这些模式的协同工作为系统提供了良好的可维护性、可扩展性和可重用性。