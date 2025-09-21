# Hello-Scan-Code - 高效代码搜索工具

Hello-Scan-Code 是一个专为大型代码仓库设计的高效搜索工具。它结合了 `grep` 的速度和 Python 的灵活性，能够在千万级文件中快速定位包含特定字符串或正则表达式的文件。

## 功能特性

1. **高速搜索**：利用 `grep` 进行初步扫描，快速定位可能匹配的文件
2. **二次校验**：可选的 Python 二次校验，提供更精确的匹配和编码处理
3. **并发处理**：使用多进程并行处理文件，提高搜索效率
4. **编码兼容**：自动处理多种文件编码（UTF-8, Latin-1, GBK, GB2312等）
5. **多格式输出**：支持 SQLite 数据库和 Excel 文件输出
6. **详细日志**：集成 `loguru` 日志库，记录详细的运行信息
7. **多关键字搜索**：支持同时搜索多个关键字，用逗号分隔
8. **面向对象设计**：采用模块化、面向对象的架构，易于扩展和维护
9. **灵活配置**：支持通过直接修改配置参数来自定义搜索行为

## 项目结构

```
hello-scan-code/
├── src/
│   ├── __init__.py
│   ├── config.py        # 配置文件解析
│   ├── code_searcher.py # 核心搜索器类
│   ├── searcher.py      # 搜索引擎实现
│   ├── database.py      # 数据库操作
│   ├── exporter.py      # Excel 导出逻辑
│   ├── logger_config.py # loguru 配置
│   └── main.py          # 主程序入口
├── pyproject.toml       # 项目配置和依赖
├── README.md            # 使用说明
└── main.py              # 根目录入口文件
```

## 项目初始化

### 克隆项目

```bash
git clone <repository-url>
cd hello-scan-code
```

### 安装依赖

使用 `uv` 来管理项目依赖（推荐）：

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

或者使用 pip：

```bash
pip install loguru pandas openpyxl
```

### 目录结构准备

确保项目目录结构完整：

```bash
mkdir -p db report logs
```

这些目录将用于存储：
- `db/`：SQLite 数据库文件
- `report/`：Excel 报告文件
- `logs/`：日志文件

## 本地运行

### 1. 配置搜索参数

在运行之前，需要配置搜索参数。有两种方式：

#### 方式一：修改配置文件

编辑 [src/config.py](file:///e:/GitHub/Hello-Scan-Code/src/config.py) 文件，修改 [SearchConfig](file:///e:/GitHub/Hello-Scan-Code/src/config.py#L8-L17) 类中的默认值：

```python
@dataclass
class SearchConfig:
    repo_path: str = "/path/to/your/code/repository"  # 修改为你的代码仓库路径
    search_term: str = "your,search,keywords"        # 修改为你要搜索的关键字
    is_regex: bool = False
    validate: bool = False
    validate_workers: int = 4
    db_path: str = "db/results.db"
    excel_path: str = "report/results.xlsx"
    log_level: str = "INFO"
```

#### 方式二：在主程序中直接修改

编辑 [src/main.py](file:///e:/GitHub/Hello-Scan-Code/src/main.py) 文件，在 [main()](file:///e:/GitHub/Hello-Scan-Code/src/main.py#L12-L38) 函数中直接修改配置参数：

```python
def main():
    try:
        # 解析配置，使用config文件中的默认值
        config = parse_args()
        
        # 直接修改配置参数
        config.repo_path = "/path/to/your/code/repository"
        config.search_term = "your,search,keywords"
        config.is_regex = False
        config.validate = True
        config.validate_workers = 8
        config.db_path = "db/results.db"
        config.excel_path = "report/results.xlsx"
        config.log_level = "INFO"
        
        # ... 其余代码保持不变
```

### 2. 运行搜索

配置完成后，执行以下命令运行搜索：

```bash
python main.py
```

### 3. 查看结果

搜索完成后，可以在以下位置查看结果：

1. **SQLite数据库**：`db/results.db`
2. **Excel文件**：`report/results.xlsx`
3. **日志文件**：`logs/` 目录下的日志文件

## 使用方法

### 基本用法

```bash
# 使用默认配置进行搜索
python main.py
```

### 自定义配置

可以通过直接修改 [src/config.py](file:///e:/GitHub/Hello-Scan-Code/src/config.py) 文件中的默认值来自定义配置，或者在 [src/main.py](file:///e:/GitHub/Hello-Scan-Code/src/main.py) 中直接修改配置参数：

```python
# 在 main.py 中修改配置参数
config.repo_path = "/path/to/your/repo"
config.search_term = "keyword1,keyword2,keyword3"
config.is_regex = False
config.validate = True
config.validate_workers = 8
config.db_path = "custom/path/results.db"
config.excel_path = "custom/path/results.xlsx"
config.log_level = "DEBUG"
```

### 配置参数说明

- `repo_path`：代码仓库路径，默认为 "/root/openstack"
- `search_term`：要搜索的字符串或正则表达式，多个关键字用逗号分隔，默认为 "test,helo,pwd"
- `is_regex`：是否使用正则表达式搜索，默认为 False
- `validate`：是否启用二次校验，默认为 False
- `validate_workers`：二次校验的并发工作进程数，默认为 4
- `db_path`：SQLite数据库输出路径，默认为 "db/results.db"
- `excel_path`：Excel文件输出路径，默认为 "report/results.xlsx"
- `log_level`：日志级别（DEBUG, INFO, WARNING, ERROR），默认为 "INFO"

## 输出结果

工具会生成以下输出：

1. **SQLite数据库**：包含所有匹配文件的路径
2. **Excel文件**：包含所有匹配文件的路径
3. **日志文件**：记录在 `logs/` 目录下

## 技术实现

1. **面向对象架构**：采用模块化、面向对象的设计，功能聚合，提高可读性和可维护性
2. **初步搜索**：使用系统 `grep` 命令快速扫描整个代码仓库
3. **二次校验**：使用 Python 对初步筛选出的文件进行精确匹配
4. **并发处理**：使用 `concurrent.futures.ProcessPoolExecutor` 实现多进程并行处理
5. **编码处理**：尝试多种常见编码以确保兼容性
6. **数据存储**：使用 `sqlite3` 和 `pandas` 分别存储和导出结果

## 性能优化

- 利用 `grep` 的原生性能进行初步筛选
- 多进程并发处理提高二次校验效率
- 智能编码检测避免因单个文件编码问题导致程序崩溃
- 合理的日志记录级别控制，避免影响性能

## 依赖说明

- `loguru`：现代化的日志记录库
- `pandas`：数据分析和Excel导出
- `openpyxl`：Excel文件处理支持