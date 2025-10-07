# Hello-Scan-Code - 高效代码搜索工具 (新架构版本)

Hello-Scan-Code 是一个专为大型代码仓库设计的高效搜索工具。经过全面重构，现采用模块化架构，支持JSON配置文件和PyInstaller打包，提供更好的扩展性和易用性。

## ✨ 新架构特性

### PyInstaller 打包支持
- **跨平台打包**：支持 Windows 和 Linux 平台的二进制文件生成
- **无依赖运行**：生成的可执行文件包含所有必要依赖，可在目标系统直接运行
- **自动化构建**：提供构建脚本实现一键打包

### JSON 配置系统
- **配置外置化**：支持通过 `config.json` 文件管理所有配置
- **Schema 验证**：提供 JSON Schema 验证确保配置正确性
- **向后兼容**：保持与现有配置系统的兼容性

> 📝 **详细打包和配置指南请参考**: [PYINSTALLER_GUIDE.md](PYINSTALLER_GUIDE.md)

### 🏗️ 模块化架构重构
- **统一配置管理器**：`ConfigManager` 集中管理所有配置模块
- **分层配置系统**：应用配置、日志配置、数据库配置独立管理
- **智能配置加载**：支持JSON配置文件、环境变量的多层级配置
- **自动配置验证**：内置配置验证和错误处理机制
- **完全向后兼容**：保持与原有API的完全兼容性

### 📄 JSON配置系统
- **外置配置文件**：支持 `config.json` 配置文件，实现配置与代码分离
- **配置优先级**：JSON配置 > 环境变量 > 默认配置
- **实时配置验证**：自动验证配置文件格式和数据有效性
- **配置模板管理**：自动生成配置模板文件
- **错误恢复机制**：配置错误时自动回退到默认配置

### 🚀 增强的PyInstaller打包支持
- **智能资源收集**：自动识别和打包所有必要资源文件
- **跨平台构建**：支持Windows单文件和Linux目录模式打包
- **模块化钩子系统**：为新架构优化的PyInstaller钩子
- **自动化构建工具**：完整的构建脚本和Makefile支持
- **零依赖部署**：打包后程序包含所有必要依赖

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
pip install pyinstaller loguru pandas openpyxl sqlalchemy alembic

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
hello-scan-code.exe
```

#### Linux
```bash
# 解压下载的文件
tar -xzf hello-scan-code-v1.0.0-linux.tar.gz
cd hello-scan-code-v1.0.0-linux

# 使用启动脚本（推荐）
./run-hello-scan-code.sh

# 或直接运行
./hello-scan-code/hello-scan-code
```

### 从源码运行

```bash
# 创建配置文件
cp config/config.template.json config.json

# 编辑配置文件
vim config.json

# 运行程序
python main.py

# 或使用Makefile
make run
```

## 📋 新架构JSON配置系统

### 配置文件示例

```json
{
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

### 测试新架构

```bash
# 测试新架构集成
make test-new-arch

# 测试配置系统
make test-config

# 测试打包功能
make test-packaging

# 或直接运行
python test_new_architecture.py
```

## 📊 新架构优势

| 特性 | 原架构 | 新架构 | 改进 |
|------|--------|--------|------|
| 配置管理 | 单一配置文件 | 模块化 + JSON | ✓ 更灵活 |
| 错误处理 | 基础验证 | 多层验证 | ✓ 更健壮 |
| 扩展性 | 有限 | 高度模块化 | ✓ 易扩展 |
| 打包效率 | 手动配置 | 智能收集 | ✓ 更自动化 |
| 配置验证 | 缺少 | 完整验证 | ✓ 更安全 |
| 向后兼容 | N/A | 完全兼容 | ✓ 无缝升级 |

## 📝 更新日志

### v1.0.0 (新架构版本)
- 🏗️ 全新模块化架构重构
- 📄 统一配置管理系统
- 📋 JSON配置文件支持
- 🚀 增强的PyInstaller打包支持
- 🔧 自动化构建和测试工具
- 📚 完整的文档和使用指南
- 🔄 完全向后兼容

## 🔗 相关文档

- [PyInstaller打包使用指南](PYINSTALLER_GUIDE.md) - 详细的打包和部署指南
- [DATABASE_OPTIMIZATION_SUMMARY.md](DATABASE_OPTIMIZATION_SUMMARY.md) - 数据库优化总结
- [docs/](docs/) - 完整的技术文档

## 项目结构

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
│   ├── code_searcher.py    # 核心搜索器类
│   ├── searcher.py         # 搜索引擎实现
│   ├── strategies.py       # 搜索策略接口和实现（策略模式）
│   ├── search_factory.py   # 搜索策略工厂（工厂模式）
│   ├── search_template.py  # 搜索模板方法（模板方法模式）
│   ├── validators.py       # 结果验证器（装饰器模式）
│   ├── database.py         # 数据库操作接口
│   ├── exporter.py         # Excel 导出逻辑
│   ├── config/             # 配置管理模块
│   │   ├── __init__.py     # 配置模块入口
│   │   ├── base_config.py  # 配置基类
│   │   ├── app_config.py   # 应用配置类
│   │   ├── logger_config.py # 日志配置类
│   │   ├── database_config.py # 数据库配置类
│   │   ├── config_manager.py # 配置管理器
│   │   ├── json_config_loader.py # JSON配置加载器
│   │   └── json_config_adapter.py # JSON配置适配器
│   ├── database/           # 数据库模块
│   │   ├── __init__.py     # 数据库模块入口
│   │   ├── session_manager.py # 数据库会话管理器
│   │   ├── compatibility.py # 兼容性适配器
│   │   ├── config/         # 数据库配置
│   │   ├── migrations/     # 数据库迁移脚本
│   │   ├── models/         # 数据库模型
│   │   └── repositories/   # 数据库仓储
│   └── packaging/          # 打包模块
│       ├── __init__.py     # 打包模块入口
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

## 核心模块功能说明

### 配置管理模块 (src/config/)
- **[base_config.py](file:///e:/GitHub/Hello-Scan-Code/src/config/base_config.py)**: 配置基类，定义所有配置类的通用接口
- **[app_config.py](file:///e:/GitHub/Hello-Scan-Code/src/config/app_config.py)**: 应用配置类，管理搜索相关的配置参数
- **[logger_config.py](file:///e:/GitHub/Hello-Scan-Code/src/config/logger_config.py)**: 日志配置类，管理日志相关的配置参数
- **[database_config.py](file:///e:/GitHub/Hello-Scan-Code/src/config/database_config.py)**: 数据库配置类，管理数据库相关的配置参数
- **[config_manager.py](file:///e:/GitHub/Hello-Scan-Code/src/config/config_manager.py)**: 配置管理器，统一管理所有配置实例
- **[json_config_loader.py](file:///e:/GitHub/Hello-Scan-Code/src/config/json_config_loader.py)**: JSON配置加载器，负责加载和解析JSON配置文件
- **[json_config_adapter.py](file:///e:/GitHub/Hello-Scan-Code/src/config/json_config_adapter.py)**: JSON配置适配器，提供JSON配置与旧配置系统的兼容性

### 数据库模块 (src/database/)
- **[session_manager.py](file:///e:/GitHub/Hello-Scan-Code/src/database/session_manager.py)**: 数据库会话管理器，管理数据库连接和会话
- **[compatibility.py](file:///e:/GitHub/Hello-Scan-Code/src/database/compatibility.py)**: 兼容性适配器，提供新旧数据库接口的兼容性
- **[models/](file:///e:/GitHub/Hello-Scan-Code/src/database/models/)**: 数据库模型，定义数据表结构
- **[repositories/](file:///e:/GitHub/Hello-Scan-Code/src/database/repositories/)**: 数据库仓储，提供数据访问接口
- **[migrations/](file:///e:/GitHub/Hello-Scan-Code/src/database/migrations/)**: 数据库迁移脚本，管理数据库版本升级

### 打包模块 (src/packaging/)
- **[pyinstaller_hooks.py](file:///e:/GitHub/Hello-Scan-Code/src/packaging/pyinstaller_hooks.py)**: PyInstaller钩子，提供打包时的依赖和资源配置
- **[resource_bundler.py](file:///e:/GitHub/Hello-Scan-Code/src/packaging/resource_bundler.py)**: 资源打包器，负责收集和管理打包所需的资源文件
- **[hooks/](file:///e:/GitHub/Hello-Scan-Code/src/packaging/hooks/)**: 自定义PyInstaller钩子，处理特殊模块的打包需求

### 搜索核心模块
- **[code_searcher.py](file:///e:/GitHub/Hello-Scan-Code/src/code_searcher.py)**: 核心搜索器类，协调整个搜索流程
- **[searcher.py](file:///e:/GitHub/Hello-Scan-Code/src/searcher.py)**: 搜索引擎实现，提供基础的文件搜索功能
- **[strategies.py](file:///e:/GitHub/Hello-Scan-Code/src/strategies.py)**: 搜索策略接口和实现，支持多种搜索算法（grep、python等）
- **[search_factory.py](file:///e:/GitHub/Hello-Scan-Code/src/search_factory.py)**: 搜索策略工厂，根据配置创建相应的搜索策略
- **[search_template.py](file:///e:/GitHub/Hello-Scan-Code/src/search_template.py)**: 搜索模板方法，定义搜索流程的通用模板
- **[validators.py](file:///e:/GitHub/Hello-Scan-Code/src/validators.py)**: 结果验证器，提供搜索结果的验证功能

### 其他核心文件
- **[database.py](file:///e:/GitHub/Hello-Scan-Code/src/database.py)**: 数据库操作接口，提供简化的数据库操作方法
- **[exporter.py](file:///e:/GitHub/Hello-Scan-Code/src/exporter.py)**: Excel导出逻辑，负责将搜索结果导出到Excel文件
- **[main.py](file:///e:/GitHub/Hello-Scan-Code/src/main.py)**: 主程序入口，程序启动和执行的起点

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
pip install loguru pandas openpyxl sqlalchemy alembic pyinstaller
```

3. **创建输出目录**

```bash
mkdir -p db report logs
```

## 本地运行

1. **配置搜索参数**

创建并编辑配置文件：
```bash
cp config/config.template.json config.json
vim config.json
```

或在代码中直接修改配置：
```python
# 在 main.py 中修改配置
config = AppConfig()
config.repo_path = "/path/to/your/code/repository"  # 代码仓库路径
config.search_term = "keyword1,keyword2,keyword3"   # 搜索关键字
config.ignore_dirs = [".git", "node_modules"]       # 忽略目录
config.file_extensions = [".py", ".js", ".go"]      # 文件类型
```

2. **运行搜索**

   ```bash
   python main.py
   ```

3. **查看结果**
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
| `validate` | 是否启用结果验证 | `False` |
| `validate_workers` | 验证工作线程数 | `4` |
| `ignore_dirs` | 忽略的目录列表 | `[".git", "__pycache__", "node_modules"]` |
| `file_extensions` | 文件后缀过滤 | `None`（不限制） |
| `db_path` | SQLite 输出路径 | `db/results.db` |
| `excel_path` | Excel 输出路径 | `report/results.xlsx` |

## 技术特点

- **面向对象设计**：采用策略模式、工厂模式、模板方法模式等设计模式
- **高效搜索**：优先使用 `grep`，自动降级到 Python 实现
- **智能编码**：自动处理多种文件编码格式
- **结果导出**：支持 SQLite 和 Excel 双重输出
- **模块化架构**：高度模块化设计，易于扩展和维护
- **配置灵活**：支持JSON配置文件和环境变量配置
- **完整测试**：包含单元测试和集成测试