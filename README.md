# Hello-Scan-Code - 高效代码搜索工具

Hello-Scan-Code 是一个专为大型代码仓库设计的高效搜索工具。它结合了 `grep` 的速度和 Python 的灵活性，能够在千万级文件中快速定位包含特定字符串或正则表达式的文件。

## 功能特性

1. **高速搜索**：利用 `grep` 进行初步扫描，快速定位可能匹配的文件
2. **二次校验**：可选的 Python 二次校验，提供更精确的匹配和编码处理
3. **并发处理**：使用多进程并行处理文件，提高搜索效率
4. **编码兼容**：自动处理多种文件编码（UTF-8, Latin-1, GBK, GB2312等）
5. **多格式输出**：支持 SQLite 数据库和 Excel 文件输出
6. **详细日志**：集成 `loguru` 日志库，记录详细的运行信息

## 项目结构

```
hello-scan-code/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── config.py        # 配置文件解析
│       ├── searcher.py      # 核心搜索逻辑
│       ├── database.py      # 数据库操作
│       ├── exporter.py      # Excel 导出逻辑
│       ├── logger_config.py # loguru 配置
│       └── main.py          # 主程序入口
├── pyproject.toml           # 项目配置和依赖
├── README.md                # 使用说明
└── main.py                  # 根目录入口文件
```

## 安装依赖

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

## 使用方法

### 基本用法

```bash
# 搜索字符串
python main.py /path/to/your/repo "your_search_string"

# 搜索正则表达式
python main.py /path/to/your/repo "your_regex_pattern" --regex
```

### 高级选项

```bash
# 启用二次校验并增加并发数
python main.py /path/to/your/repo "your_search_string_or_regex" --validate --validate_workers 8

# 指定输出路径和日志级别
python main.py /path/to/your/repo "search_term" --db_path ./output/results.db --excel_path ./output/results.xlsx --log_level DEBUG
```

### 命令行参数

- `repo_path`：代码仓库路径（必需）
- `search_term`：要搜索的字符串或正则表达式（必需）
- `--regex`：是否使用正则表达式搜索
- `--validate`：是否启用二次校验
- `--validate_workers`：二次校验的并发工作进程数（默认4）
- `--db_path`：SQLite数据库输出路径（默认db/results.db）
- `--excel_path`：Excel文件输出路径（默认report/results.xlsx）
- `--log_level`：日志级别（DEBUG, INFO, WARNING, ERROR，默认INFO）

## 输出结果

工具会生成以下输出：

1. **SQLite数据库**：包含所有匹配文件的路径
2. **Excel文件**：包含所有匹配文件的路径
3. **日志文件**：记录在 `logs/` 目录下

## 技术实现

1. **初步搜索**：使用系统 `grep` 命令快速扫描整个代码仓库
2. **二次校验**：使用 Python 对初步筛选出的文件进行精确匹配
3. **并发处理**：使用 `concurrent.futures.ProcessPoolExecutor` 实现多进程并行处理
4. **编码处理**：尝试多种常见编码以确保兼容性
5. **数据存储**：使用 `sqlite3` 和 `pandas` 分别存储和导出结果

## 性能优化

- 利用 `grep` 的原生性能进行初步筛选
- 多进程并发处理提高二次校验效率
- 智能编码检测避免因单个文件编码问题导致程序崩溃
- 合理的日志记录级别控制，避免影响性能

## 依赖说明

- `loguru`：现代化的日志记录库
- `pandas`：数据分析和Excel导出
- `openpyxl`：Excel文件处理支持