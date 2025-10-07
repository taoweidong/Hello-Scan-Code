# Hello-Scan-Code - 高效代码扫描工具 (插件化架构版本)

Hello-Scan-Code 是一个专为大型代码仓库设计的高性能代码扫描工具。经过全面重构，采用了现代化的插件化架构，支持JSON配置文件、PyInstaller打包和Click命令行界面，提供更好的扩展性和易用性。

## 🚀 核心特性

### 🔌 插件化架构
- **模块化设计**：采用插件化架构，易于扩展和维护
- **双阶段扫描**：Grep预筛选 + 插件精准分析，大幅提升扫描性能
- **内置插件**：提供关键字扫描、安全检测、TODO检测、正则表达式等多种内置插件
- **自定义插件**：支持开发自定义插件以满足特定需求

### 📄 JSON配置系统
- **配置外置化**：支持通过 `config.json` 文件管理所有配置
- **灵活配置**：支持应用配置、日志配置、数据库配置等多维度配置
- **插件配置**：支持为每个插件单独配置参数

### 📦 PyInstaller打包支持
- **跨平台打包**：支持 Windows 和 Linux 平台的二进制文件生成
- **无依赖运行**：生成的可执行文件包含所有必要依赖，可在目标系统直接运行
- **自动化构建**：提供构建脚本实现一键打包

### 🖥️ Click命令行界面
- **友好的CLI**：使用Click库提供直观的命令行界面
- **丰富的选项**：支持路径指定、配置文件、详细日志、多种导出格式等选项

## 📦 安装方式

### 方式一：下载可执行文件（推荐）

从 [Releases](https://github.com/taoweidong/Hello-Scan-Code/releases) 页面下载对应平台的预编译版本：

- `hello-scan-code-v1.0.0-windows.zip` - Windows 平台
- `hello-scan-code-v1.0.0-linux.tar.gz` - Linux 平台

### 方式二：从源码安装（开发者）

```bash
# 克隆项目
git clone https://github.com/taoweidong/Hello-Scan-Code.git
cd Hello-Scan-Code

# 安装依赖
pip install -r requirements.txt

# 或使用Makefile
make install
```

## 🚀 快速开始

### 使用可执行文件

#### Windows
```bash
# 解压下载的文件
unzip hello-scan-code-v1.0.0-windows.zip
cd hello-scan-code-v1.0.0-windows

# 创建配置文件
copy config.template.json config.json

# 编辑配置文件
notepad config.json

# 运行程序
hello-scan-code.exe --path /path/to/code
```

#### Linux
```bash
# 解压下载的文件
tar -xzf hello-scan-code-v1.0.0-linux.tar.gz
cd hello-scan-code-v1.0.0-linux

# 使用启动脚本（推荐）
./run-hello-scan-code.sh

# 或直接运行
./hello-scan-code/hello-scan-code --path /path/to/code
```

### 从源码运行

```bash
# 创建配置文件
cp config/config.template.json config.json

# 编辑配置文件
vim config.json

# 运行程序
python main.py --path /path/to/code

# 或使用Makefile
make run
```

## 📋 命令行选项

```bash
Usage: main.py [OPTIONS]

Options:
  -p, --path PATH                 要扫描的代码仓库路径
  -c, --config PATH               配置文件路径  [default: config.json]
  -v, --verbose                   启用详细日志输出
  --export-excel PATH             导出Excel报告文件路径
  --export-html PATH              导出HTML报告文件路径
  --export-db                     导出结果到数据库
  --help                          Show this message and exit.
```

## 📋 插件化架构JSON配置系统

### 配置文件示例

```json
{
  "_comment": "Hello-Scan-Code 配置文件模板 (插件化架构版本)",
  "_description": "复制此文件为 config.json 并修改相应配置项",
  "repo_path": ".",
  "search_term": "TODO,FIXME,BUG",
  "is_regex": false,
  "validate": true,
  "validate_workers": 4,
  
  "output": {
    "db_path": "db/results.db",
    "excel_path": "report/results.xlsx"
  },
  
  "logging": {
    "level": "INFO",
    "file_path": "logs/app.log",
    "rotation": "10 MB",
    "retention": "7 days"
  },
  
  "database": {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30
  },
  
  "filters": {
    "ignore_dirs": [
      ".git", "__pycache__", "node_modules",
      "dist", "build", ".vscode", ".idea"
    ],
    "file_extensions": [".py", ".js", ".java"]
  },
  
  "plugins": {
    "enabled": ["keyword", "todo", "security", "regex"],
    "configs": {
      "keyword": {
        "keywords": ["TODO", "FIXME", "BUG", "HACK"]
      },
      "regex": {
        "patterns": {
          "email": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
          "phone": "\\b\\d{3}-\\d{3}-\\d{4}\\b"
        }
      }
    }
  }
}
```

## 🔧 开发者指南

### 构建可执行文件

```bash
# 使用Makefile构建
make build-linux    # Linux平台
make build-windows  # Windows平台
make all           # 完整构建流程

# 或手动执行构建脚本
python scripts/build_linux.py
python scripts/build_windows.py
```

### 测试

```bash
# 运行所有测试
make test

# 运行单元测试
make test-unit

# 运行集成测试
make test-integration

# 检查代码覆盖率
make coverage
```

## 📊 插件化架构优势

| 特性 | 传统架构 | 插件化架构 | 改进 |
|------|----------|------------|------|
| 扫描性能 | 低效全量扫描 | Grep预筛选+精准分析 | ✓ 性能提升 |
| 扩展性 | 困难 | 插件化扩展 | ✓ 易扩展 |
| 可维护性 | 耦合度高 | 模块化设计 | ✓ 易维护 |
| 配置管理 | 简单配置 | 多维度配置 | ✓ 更灵活 |
| 插件生态 | 不支持 | 完整插件系统 | ✓ 可定制 |

## 📝 更新日志

### v1.0.0 (插件化架构版本)
- 🔌 全新插件化架构重构
- ⚡ 双阶段扫描引擎（Grep预筛选 + 插件精准分析）
- 📦 统一配置管理系统
- 📋 JSON配置文件支持
- 🚀 增强的PyInstaller打包支持
- 🖥️ Click命令行界面
- 🔧 自动化构建和测试工具
- 📚 完整的文档和使用指南

## 📁 项目结构

```bash
hello-scan-code/
├── config/                 # 配置文件目录
│   ├── config.template.json # 配置模板文件
│   └── ...                  # 其他配置文件
├── scripts/                # 构建脚本
│   ├── build_linux.py      # Linux平台构建脚本
│   └── build_windows.py    # Windows平台构建脚本
├── src/
│   ├── __init__.py         # Python包初始化文件
│   ├── main.py             # 主程序入口
│   ├── engine/             # 扫描引擎模块
│   │   ├── __init__.py     
│   │   ├── scan_engine.py  # 优化扫描引擎
│   │   └── grep_scanner.py # Grep预扫描器
│   ├── plugin/             # 插件系统核心
│   │   ├── __init__.py     
│   │   ├── base.py         # 插件基础接口
│   │   ├── manager.py      # 插件管理器
│   │   ├── registry.py     # 插件注册表
│   │   └── discovery.py    # 插件发现服务
│   ├── plugins/            # 插件实现
│   │   ├── __init__.py     
│   │   ├── builtin/        # 内置插件
│   │   │   ├── keyword_plugin.py  # 关键字扫描插件
│   │   │   ├── todo_plugin.py     # TODO检测插件
│   │   │   ├── security_plugin.py # 安全检测插件
│   │   │   └── regex_plugin.py    # 正则表达式插件
│   │   └── custom/         # 自定义插件目录
│   ├── config/             # 配置管理模块
│   │   ├── __init__.py     
│   │   └── config_manager.py # 配置管理器
│   ├── database/           # 数据库模块
│   │   ├── __init__.py     
│   │   ├── session_manager.py # 数据库会话管理器
│   │   ├── models.py       # 数据库模型
│   │   ├── repositories.py # 数据库仓储
│   │   └── compatibility.py # 兼容性适配器
│   ├── exporters/          # 导出器模块
│   │   ├── __init__.py     
│   │   ├── excel_exporter.py # Excel导出器
│   │   ├── html_exporter.py  # HTML导出器
│   │   └── database_exporter.py # 数据库导出器
│   ├── utils/              # 工具函数模块
│   │   ├── __init__.py     
│   │   ├── file_utils.py   # 文件工具函数
│   │   ├── text_utils.py   # 文本工具函数
│   │   └── platform_utils.py # 平台工具函数
│   └── packaging/          # 打包模块
│       ├── __init__.py     
│       ├── pyinstaller_hooks.py # PyInstaller钩子
│       ├── resource_bundler.py # 资源打包器
│       └── hooks/          # PyInstaller自定义钩子
├── tests/                  # 测试目录
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── ...                 # 其他测试文件
├── pyproject.toml          # 项目配置和依赖
├── README.md               # 使用说明
├── Makefile                # 构建脚本
└── main.py                 # 根目录入口文件
```

## 🧩 插件系统详解

### 内置插件

1. **关键字扫描插件 (keyword)**
   - 功能：扫描代码中的指定关键字
   - 配置：支持自定义关键字列表

2. **TODO检测插件 (todo)**
   - 功能：检测代码中的TODO、FIXME等注释
   - 配置：支持自定义注释标记

3. **安全检测插件 (security)**
   - 功能：检测潜在的安全问题
   - 配置：支持自定义安全规则

4. **正则表达式插件 (regex)**
   - 功能：使用正则表达式扫描代码
   - 配置：支持自定义正则表达式模式

### 开发自定义插件

创建自定义插件需要继承 [IScanPlugin](file:///E:/GitHub/Hello-Scan-Code/src/plugin/base.py#L56-L115) 接口并实现相关方法：

```python
from src.plugin.base import IScanPlugin, ScanResult, ScanContext

class MyCustomPlugin(IScanPlugin):
    @property
    def plugin_id(self) -> str:
        return "my_custom_plugin"
    
    @property
    def name(self) -> str:
        return "My Custom Plugin"
    
    # 实现其他必需的方法...
```

## 项目初始化

1. **克隆项目**

```bash
git clone https://github.com/taoweidong/Hello-Scan-Code.git
cd Hello-Scan-Code
```

2. **安装依赖**

```bash
# 使用 pip
pip install -r requirements.txt

# 或安装特定依赖
pip install loguru pandas openpyxl sqlalchemy alembic pyinstaller click
```

3. **创建输出目录**

```bash
mkdir -p db report logs
```

## 本地运行

1. **配置扫描参数**

创建并编辑配置文件：
```bash
cp config/config.template.json config.json
vim config.json
```

2. **运行扫描**

```bash
# 基本扫描
python main.py --path /path/to/code

# 详细日志输出
python main.py --path /path/to/code --verbose

# 导出多种格式报告
python main.py --path /path/to/code --export-excel report.xlsx --export-html report.html --export-db
```

3. **查看结果**
   - SQLite 数据库：`db/results.db`
   - Excel 文件：`report/results.xlsx`
   - HTML 报告：`report/report.html`
   - 日志文件：`logs/` 目录

## 配置参数

主要配置参数说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `repo_path` | 代码仓库路径 | `.` |
| `search_term` | 搜索关键字（逗号分隔） | `TODO,FIXME,BUG` |
| `is_regex` | 是否使用正则表达式 | `false` |
| `validate` | 是否启用结果验证 | `true` |
| `validate_workers` | 验证工作线程数 | `4` |
| `ignore_dirs` | 忽略的目录列表 | `[".git", "__pycache__", "node_modules"]` |
| `file_extensions` | 文件后缀过滤 | `[".py", ".js", ".java"]` |
| `db_path` | SQLite 输出路径 | `db/results.db` |
| `excel_path` | Excel 输出路径 | `report/results.xlsx` |

## 技术特点

- **插件化架构**：采用现代化插件化设计，易于扩展和维护
- **高性能扫描**：双阶段扫描引擎，Grep预筛选 + 插件精准分析
- **多格式导出**：支持Excel、HTML、数据库等多种导出格式
- **跨平台支持**：支持Windows和Linux平台
- **完整测试**：包含单元测试和集成测试，代码覆盖率超过80%
- **现代化工具链**：使用Click、PyInstaller、Loguru等现代化Python库