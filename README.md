# Hello-Scan-Code - 高效代码搜索工具

Hello-Scan-Code 是一个专为大型代码仓库设计的高效搜索工具。它结合了 `grep` 的速度和 Python 的灵活性，能够快速定位包含特定字符串或正则表达式的文件。

## 新特性 🎆

### PyInstaller 打包支持
- **跨平台打包**：支持 Windows 和 Linux 平台的二进制文件生成
- **无依赖运行**：生成的可执行文件包含所有必要依赖，可在目标系统直接运行
- **自动化构建**：提供构建脚本实现一键打包

### JSON 配置系统
- **配置外置化**：支持通过 `config.json` 文件管理所有配置
- **Schema 验证**：提供 JSON Schema 验证确保配置正确性
- **向后兼容**：保持与现有配置系统的兼容性

> 📝 **详细打包和配置指南请参考**: [PYINSTALLER_GUIDE.md](PYINSTALLER_GUIDE.md)

## 功能特性

- **高速搜索**：优先使用系统 `grep` 命令，自动降级到 Python 实现
- **多关键字搜索**：支持同时搜索多个关键字，用逗号分隔
- **灵活过滤**：支持配置忽略目录和指定文件后缀
- **多格式输出**：支持 SQLite 数据库和 Excel 文件输出
- **详细日志**：集成 `loguru` 日志库，记录详细的运行信息

## 项目结构

```bash
hello-scan-code/
├── src/
│   ├── __init__.py
│   ├── config.py           # 配置文件解析
│   ├── logger_config.py    # 日志配置
│   ├── strategies.py       # 搜索策略接口和实现（策略模式）
│   ├── search_factory.py   # 搜索策略工厂（工厂模式）
│   ├── search_template.py  # 搜索模板方法（模板方法模式）
│   ├── validators.py       # 结果验证器（装饰器模式）
│   ├── searcher.py         # 搜索引擎实现
│   ├── database.py         # 数据库操作
│   ├── exporter.py         # Excel 导出逻辑
│   ├── code_searcher.py    # 核心搜索器类
│   └── main.py             # 主程序入口
├── pyproject.toml          # 项目配置和依赖
├── README.md               # 使用说明
└── main.py                 # 根目录入口文件
```

## 项目初始化

1. **克隆项目**

```bash
git clone https://github.com/taoweidong/Hello-Scan-Code.git
cd Hello-Scan-Code
```

1. **安装依赖**

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install loguru pandas openpyxl
```

1. **创建输出目录**

```bash
mkdir -p db report logs
```

## 本地运行

1. **配置搜索参数**

在 `src/main.py` 中修改配置：

```python
config.repo_path = "/path/to/your/code/repository"  # 代码仓库路径
config.search_term = "keyword1,keyword2,keyword3"   # 搜索关键字
config.ignore_dirs = [".git", "node_modules"]       # 忽略目录
config.file_extensions = [".py", ".js", ".go"]      # 文件类型
```

1. **运行搜索**

   ```bash
   python main.py
   ```

1. **查看结果**
   - SQLite 数据库：`db/results.db`
   - Excel 文件：`report/results.xlsx`
   - 日志文件：`logs/` 目录

## 配置参数

主要配置参数说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `repo_path` | 代码仓库路径 | `/root/CodeRootPath` |
| `search_term` | 搜索关键字（逗号分隔） | `test,def,void` |
| `is_regex` | 是否使用正则表达式 | `False` |
| `ignore_dirs` | 忽略的目录列表 | `[".git", "__pycache__", "node_modules"]` |
| `file_extensions` | 文件后缀过滤 | `None`（不限制） |
| `db_path` | SQLite 输出路径 | `db/results.db` |
| `excel_path` | Excel 输出路径 | `report/results.xlsx` |

## 技术特点

- **面向对象设计**：采用策略模式、工厂模式等设计模式
- **高效搜索**：优先使用 `grep`，自动降级到 Python 实现
- **智能编码**：自动处理多种文件编码格式
- **结果导出**：支持 SQLite 和 Excel 双重输出