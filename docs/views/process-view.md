# 进程视图 (Process View)

## 概述

进程视图描述了Hello-Scan-Code系统的动态行为，展示了系统在运行时的并发处理机制、性能特性和可靠性设计。该视图关注系统的运行时架构，包括进程间通信、同步机制和资源管理。

## 系统运行时架构

```mermaid
graph TB
    subgraph "主进程 (Main Process)"
        MainThread[主线程]
        ConfigLoader[配置加载器]
        FlowController[流程控制器]
    end
    
    subgraph "搜索执行进程"
        SearchCoordinator[搜索协调器]
        StrategySelector[策略选择器]
        
        subgraph "Grep搜索策略"
            GrepProcess[Grep子进程]
            GrepParser[结果解析器]
        end
        
        subgraph "Python搜索策略"
            FileScanner[文件扫描器]
            PatternMatcher[模式匹配器]
            ContentReader[内容读取器]
        end
    end
    
    subgraph "验证处理进程"
        ValidationCoordinator[验证协调器]
        ThreadPool[验证线程池]
        ResultFilter[结果过滤器]
    end
    
    subgraph "数据持久化进程"
        DatabaseWriter[数据库写入器]
        ExcelGenerator[Excel生成器]
        FileIOManager[文件IO管理器]
    end
    
    MainThread --> ConfigLoader
    ConfigLoader --> FlowController
    FlowController --> SearchCoordinator
    SearchCoordinator --> StrategySelector
    
    StrategySelector --> GrepProcess
    StrategySelector --> FileScanner
    
    GrepProcess --> GrepParser
    FileScanner --> PatternMatcher
    PatternMatcher --> ContentReader
    
    GrepParser --> ValidationCoordinator
    ContentReader --> ValidationCoordinator
    
    ValidationCoordinator --> ThreadPool
    ThreadPool --> ResultFilter
    
    ResultFilter --> DatabaseWriter
    ResultFilter --> ExcelGenerator
    
    DatabaseWriter --> FileIOManager
    ExcelGenerator --> FileIOManager
```

## 主要执行流程

### 1. 系统启动序列

```mermaid
sequenceDiagram
    participant User as 用户
    participant Main as 主程序
    participant Config as 配置管理器
    participant CodeSearcher as 代码搜索器
    participant Logger as 日志系统
    
    User->>Main: 启动程序
    Main->>Logger: 初始化日志系统
    Logger-->>Main: 日志系统就绪
    
    Main->>Config: 加载配置参数
    Config->>Config: 验证配置有效性
    Config-->>Main: 配置加载完成
    
    Main->>CodeSearcher: 创建搜索器实例
    CodeSearcher->>CodeSearcher: 初始化组件
    CodeSearcher-->>Main: 搜索器就绪
    
    Main->>CodeSearcher: 执行搜索
    CodeSearcher-->>Main: 返回搜索结果
    
    Main->>CodeSearcher: 保存结果
    CodeSearcher-->>Main: 保存完成
    
    Main->>User: 显示执行结果
```

### 2. 搜索执行流程

```mermaid
sequenceDiagram
    participant CodeSearcher as 代码搜索器
    participant SearchTemplate as 搜索模板
    participant StrategyFactory as 策略工厂
    participant SearchStrategy as 搜索策略
    participant ResultValidator as 结果验证器
    
    CodeSearcher->>SearchTemplate: search()
    SearchTemplate->>SearchTemplate: _count_files()
    SearchTemplate->>SearchTemplate: _parse_search_terms()
    
    SearchTemplate->>StrategyFactory: create_default_strategy()
    StrategyFactory->>StrategyFactory: 检测系统环境
    StrategyFactory-->>SearchTemplate: 返回策略实例
    
    SearchTemplate->>SearchStrategy: search(repo_path, terms, is_regex)
    
    alt Grep策略
        SearchStrategy->>SearchStrategy: _build_grep_command()
        SearchStrategy->>SearchStrategy: 执行系统命令
        SearchStrategy->>SearchStrategy: _parse_grep_output()
    else Python策略
        SearchStrategy->>SearchStrategy: 递归扫描文件
        SearchStrategy->>SearchStrategy: _search_in_file()
        SearchStrategy->>SearchStrategy: 模式匹配
    end
    
    SearchStrategy-->>SearchTemplate: 返回初步结果
    
    opt 启用二次验证
        SearchTemplate->>ResultValidator: validate_results()
        ResultValidator->>ResultValidator: parallel_validate()
        ResultValidator-->>SearchTemplate: 返回验证结果
    end
    
    SearchTemplate-->>CodeSearcher: 返回最终结果
```

### 3. 并行验证流程

```mermaid
sequenceDiagram
    participant ResultValidator as 结果验证器
    participant ThreadPoolExecutor as 线程池
    participant WorkerThread1 as 工作线程1
    participant WorkerThread2 as 工作线程2
    participant WorkerThreadN as 工作线程N
    participant FileSystem as 文件系统
    
    ResultValidator->>ThreadPoolExecutor: 提交验证任务
    ThreadPoolExecutor->>WorkerThread1: 分配任务批次1
    ThreadPoolExecutor->>WorkerThread2: 分配任务批次2
    ThreadPoolExecutor->>WorkerThreadN: 分配任务批次N
    
    par 并行验证
        WorkerThread1->>FileSystem: 读取文件内容
        FileSystem-->>WorkerThread1: 返回文件内容
        WorkerThread1->>WorkerThread1: 重新匹配验证
    and
        WorkerThread2->>FileSystem: 读取文件内容
        FileSystem-->>WorkerThread2: 返回文件内容
        WorkerThread2->>WorkerThread2: 重新匹配验证
    and
        WorkerThreadN->>FileSystem: 读取文件内容
        FileSystem-->>WorkerThreadN: 返回文件内容
        WorkerThreadN->>WorkerThreadN: 重新匹配验证
    end
    
    WorkerThread1-->>ThreadPoolExecutor: 返回验证结果1
    WorkerThread2-->>ThreadPoolExecutor: 返回验证结果2
    WorkerThreadN-->>ThreadPoolExecutor: 返回验证结果N
    
    ThreadPoolExecutor-->>ResultValidator: 汇总验证结果
```

## 并发处理机制

### 1. 线程池配置

```python
# 线程池配置策略
class ThreadPoolConfig:
    def __init__(self, config: SearchConfig):
        self.max_workers = min(
            config.max_workers or 4,  # 用户配置
            os.cpu_count() or 1,      # CPU核心数
            32                        # 最大限制
        )
        self.timeout = 300            # 5分钟超时
        self.chunk_size = 100         # 任务批次大小
```

**线程池使用场景**:
- 并行验证搜索结果
- 大文件并行处理
- 批量数据库操作
- Excel文件并行生成

### 2. 资源同步机制

```mermaid
graph TB
    subgraph "资源同步"
        FileLock[文件锁]
        DatabaseLock[数据库锁]
        MemoryBarrier[内存屏障]
        ThreadSafety[线程安全]
    end
    
    subgraph "同步原语"
        Mutex[互斥锁]
        Semaphore[信号量]
        Condition[条件变量]
        Queue[线程安全队列]
    end
    
    subgraph "应用场景"
        FileIO[文件IO操作]
        DatabaseOp[数据库操作]
        ResultAgg[结果聚合]
        LogWrite[日志写入]
    end
    
    FileLock --> FileIO
    DatabaseLock --> DatabaseOp
    ThreadSafety --> ResultAgg
    MemoryBarrier --> LogWrite
    
    Mutex --> FileLock
    Semaphore --> DatabaseLock
    Condition --> ThreadSafety
    Queue --> ResultAgg
```

### 3. 错误处理和恢复

```mermaid
stateDiagram-v2
    [*] --> 正常执行
    正常执行 --> 检测异常 : 异常发生
    检测异常 --> 分类异常 : 异常类型判断
    
    分类异常 --> 可恢复异常 : IO错误、网络超时
    分类异常 --> 不可恢复异常 : 配置错误、系统错误
    
    可恢复异常 --> 重试机制 : 重试策略
    重试机制 --> 正常执行 : 重试成功
    重试机制 --> 降级处理 : 重试失败
    
    降级处理 --> 备用策略 : 策略切换
    备用策略 --> 正常执行 : 降级成功
    备用策略 --> 优雅失败 : 降级失败
    
    不可恢复异常 --> 优雅失败 : 记录错误
    优雅失败 --> [*] : 程序终止
```

## 性能优化策略

### 1. 搜索性能优化

```mermaid
graph TB
    subgraph "搜索优化"
        IndexCache[索引缓存]
        FileFilter[文件预过滤]
        LazyLoad[延迟加载]
        Parallel[并行处理]
    end
    
    subgraph "IO优化"
        BufferIO[缓冲IO]
        MemoryMap[内存映射]
        AsyncIO[异步IO]
        BatchOp[批量操作]
    end
    
    subgraph "CPU优化"
        RegexCompile[正则预编译]
        StringIntern[字符串内部化]
        FastPath[快速路径]
        Vectorize[向量化计算]
    end
    
    IndexCache --> FileFilter
    FileFilter --> LazyLoad
    LazyLoad --> Parallel
    
    BufferIO --> AsyncIO
    MemoryMap --> BatchOp
    
    RegexCompile --> StringIntern
    StringIntern --> FastPath
    FastPath --> Vectorize
```

### 2. 内存管理策略

```python
# 内存使用监控和优化
class MemoryManager:
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory = max_memory_mb * 1024 * 1024
        self.current_usage = 0
        self.gc_threshold = 0.8  # 80%触发垃圾回收
    
    def check_memory_usage(self):
        """检查内存使用情况"""
        process = psutil.Process()
        self.current_usage = process.memory_info().rss
        
        if self.current_usage > self.max_memory * self.gc_threshold:
            self._trigger_gc()
    
    def _trigger_gc(self):
        """触发垃圾回收"""
        import gc
        gc.collect()
        logger.info(f"Memory cleanup triggered, usage: {self.current_usage / 1024 / 1024:.2f}MB")
```

### 3. 缓存机制

```mermaid
graph TB
    subgraph "多级缓存"
        L1Cache[L1: 内存缓存]
        L2Cache[L2: 磁盘缓存]
        L3Cache[L3: 数据库缓存]
    end
    
    subgraph "缓存策略"
        LRU[LRU淘汰]
        TTL[时间过期]
        Size[大小限制]
        Version[版本控制]
    end
    
    subgraph "缓存应用"
        FileMetadata[文件元数据]
        SearchResults[搜索结果]
        RegexPatterns[正则模式]
        ConfigData[配置数据]
    end
    
    L1Cache --> LRU
    L2Cache --> TTL
    L3Cache --> Size
    
    LRU --> FileMetadata
    TTL --> SearchResults
    Size --> RegexPatterns
    Version --> ConfigData
```

## 可靠性设计

### 1. 故障检测机制

```mermaid
graph TB
    subgraph "健康检查"
        ProcessHealth[进程健康]
        ResourceHealth[资源健康]
        ServiceHealth[服务健康]
    end
    
    subgraph "监控指标"
        CPUUsage[CPU使用率]
        MemoryUsage[内存使用率]
        DiskSpace[磁盘空间]
        NetworkIO[网络IO]
        FileDescriptors[文件描述符]
    end
    
    subgraph "告警机制"
        ThresholdAlert[阈值告警]
        TrendAlert[趋势告警]
        HealthAlert[健康告警]
    end
    
    ProcessHealth --> CPUUsage
    ResourceHealth --> MemoryUsage
    ServiceHealth --> DiskSpace
    
    CPUUsage --> ThresholdAlert
    MemoryUsage --> TrendAlert
    DiskSpace --> HealthAlert
```

### 2. 容错处理

```python
# 容错装饰器
def with_retry(max_attempts=3, backoff_factor=1.0, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = backoff_factor * (2 ** attempt)
                        time.sleep(sleep_time)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {sleep_time}s: {e}")
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
        return wrapper
    return decorator

# 应用示例
@with_retry(max_attempts=3, exceptions=(IOError, OSError))
def safe_file_operation(file_path: str):
    """安全的文件操作"""
    pass
```

### 3. 优雅降级

```mermaid
stateDiagram-v2
    [*] --> 正常模式
    正常模式 --> 检测压力 : 负载监控
    
    检测压力 --> 轻度降级 : 轻度压力
    检测压力 --> 中度降级 : 中度压力
    检测压力 --> 重度降级 : 重度压力
    
    轻度降级 --> 减少并发 : 降低线程数
    中度降级 --> 关闭验证 : 跳过二次验证
    重度降级 --> 基础功能 : 仅保留核心功能
    
    减少并发 --> 正常模式 : 压力缓解
    关闭验证 --> 轻度降级 : 压力缓解
    基础功能 --> 中度降级 : 压力缓解
    
    基础功能 --> [*] : 无法处理
```

## 性能监控与分析

### 1. 性能指标收集

```python
# 性能监控器
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'search_time': [],
            'file_count': [],
            'result_count': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        self.start_time = None
    
    def start_timing(self):
        self.start_time = time.time()
    
    def end_timing(self, operation: str):
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics[f'{operation}_time'].append(duration)
            return duration
    
    def collect_system_metrics(self):
        process = psutil.Process()
        self.metrics['memory_usage'].append(process.memory_info().rss)
        self.metrics['cpu_usage'].append(process.cpu_percent())
    
    def generate_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        report = {}
        for metric, values in self.metrics.items():
            if values:
                report[metric] = {
                    'avg': statistics.mean(values),
                    'max': max(values),
                    'min': min(values),
                    'count': len(values)
                }
        return report
```

### 2. 性能基准测试

```mermaid
graph TB
    subgraph "基准测试场景"
        SmallRepo[小型仓库测试<br/>< 1K文件]
        MediumRepo[中型仓库测试<br/>1K-10K文件]
        LargeRepo[大型仓库测试<br/>> 10K文件]
    end
    
    subgraph "测试维度"
        SearchTime[搜索时间]
        MemoryUsage[内存占用]
        CPUUsage[CPU使用率]
        Accuracy[准确性]
    end
    
    subgraph "性能目标"
        SmallTarget[< 5秒]
        MediumTarget[< 30秒]
        LargeTarget[< 300秒]
    end
    
    SmallRepo --> SearchTime
    MediumRepo --> MemoryUsage
    LargeRepo --> CPUUsage
    
    SearchTime --> SmallTarget
    MemoryUsage --> MediumTarget
    CPUUsage --> LargeTarget
```

## 扩展性设计

### 1. 水平扩展

```mermaid
graph TB
    subgraph "主节点"
        Coordinator[协调器]
        TaskDistributor[任务分发器]
        ResultAggregator[结果聚合器]
    end
    
    subgraph "工作节点1"
        Worker1[搜索工作器1]
        LocalCache1[本地缓存1]
    end
    
    subgraph "工作节点2"
        Worker2[搜索工作器2]
        LocalCache2[本地缓存2]
    end
    
    subgraph "工作节点N"
        WorkerN[搜索工作器N]
        LocalCacheN[本地缓存N]
    end
    
    subgraph "共享存储"
        SharedDB[(共享数据库)]
        SharedFS[共享文件系统]
    end
    
    Coordinator --> TaskDistributor
    TaskDistributor --> Worker1
    TaskDistributor --> Worker2
    TaskDistributor --> WorkerN
    
    Worker1 --> LocalCache1
    Worker2 --> LocalCache2
    WorkerN --> LocalCacheN
    
    Worker1 --> ResultAggregator
    Worker2 --> ResultAggregator
    WorkerN --> ResultAggregator
    
    ResultAggregator --> SharedDB
    Worker1 --> SharedFS
    Worker2 --> SharedFS
    WorkerN --> SharedFS
```

### 2. 插件化架构

```python
# 插件接口定义
class SearchPlugin:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def initialize(self) -> bool:
        """插件初始化"""
        pass
    
    def search(self, repo_path: str, search_terms: Any) -> List[Dict[str, Any]]:
        """执行搜索"""
        pass
    
    def cleanup(self):
        """清理资源"""
        pass

# 插件加载器
class PluginLoader:
    def __init__(self):
        self.plugins = {}
    
    def load_plugin(self, plugin_name: str, plugin_class: type):
        """动态加载插件"""
        if issubclass(plugin_class, SearchPlugin):
            self.plugins[plugin_name] = plugin_class
    
    def create_plugin(self, plugin_name: str, config: Dict[str, Any]) -> SearchPlugin:
        """创建插件实例"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name](config)
        raise ValueError(f"Plugin {plugin_name} not found")
```

## 总结

进程视图展现了Hello-Scan-Code系统完整的运行时架构和动态行为。通过合理的并发设计、性能优化和可靠性保障，系统能够在各种负载条件下稳定高效地运行。并发处理机制提高了系统的吞吐量，容错设计保证了系统的健壮性，性能监控机制确保了系统的可观测性。整体设计为系统的横向扩展和功能演进提供了良好的基础。