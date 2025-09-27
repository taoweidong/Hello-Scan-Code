# PyInstaller 打包使用指南 (新架构版本)

## 概述

Hello-Scan-Code 现已基于全新的模块化架构完全重构，支持 PyInstaller 打包，可以生成独立的可执行文件，无需在目标系统安装 Python 环境即可运行。

## 🚀 新架构特性

### 模块化配置系统
- **统一配置管理器**：`ConfigManager` 统一管理所有配置模块
- **分层配置架构**：应用配置、日志配置、数据库配置独立管理
- **JSON配置优先**：支持外置JSON配置文件，优先级高于环境变量
- **自动配置验证**：内置配置验证和错误处理机制
- **向后兼容性**：完全兼容原有的配置方式

### 增强的打包支持
- **智能资源收集**：自动识别和打包所有必要资源文件
- **模块化钩子系统**：为新架构优化的PyInstaller钩子
- **跨平台构建脚本**：适配新架构的自动化构建工具
- **配置模板管理**：自动生成和管理配置模板文件

## 📁 新架构目录结构

```
项目根目录/
├── src/
│   ├── config/                        # 配置系统模块
│   │   ├── __init__.py                # 统一配置接口
│   │   ├── base_config.py             # 配置基类
│   │   ├── app_config.py              # 应用配置
│   │   ├── logger_config.py           # 日志配置
│   │   ├── database_config.py         # 数据库配置
│   │   ├── config_manager.py          # 配置管理器
│   │   └── json_config_loader.py      # JSON配置加载器
│   ├── packaging/                     # 打包支持模块
│   │   ├── __init__.py                # 打包接口
│   │   ├── pyinstaller_hooks.py       # PyInstaller钩子
│   │   └── resource_bundler.py        # 资源打包器
│   └── ... (其他业务模块)
├── config/                            # 配置文件目录
│   ├── config.template.json           # 配置模板
│   └── example.json                   # 示例配置
├── build/                             # 构建配置
│   ├── windows/hello-scan-code.spec   # Windows打包配置
│   └── linux/hello-scan-code.spec     # Linux打包配置
├── scripts/                           # 构建脚本
│   ├── build_windows.py               # Windows构建脚本
│   └── build_linux.py                 # Linux构建脚本
├── tests/                             # 测试目录
├── Makefile                           # 构建工具
├── test_new_architecture.py           # 新架构测试
└── dist/                              # 打包输出目录
```

## 🛠️ 快速开始

### 1. 环境准备

```bash
# 安装项目依赖
pip install pyinstaller>=6.0.0 loguru pandas openpyxl sqlalchemy alembic

# 或使用Makefile
make install
```

### 2. 配置文件设置

#### 创建配置文件
```bash
# 使用Makefile创建配置文件
make config

# 或手动复制
cp config/config.template.json config.json

# 编辑配置文件
vim config.json
```

#### 新架构配置文件示例
```json
{
  "_comment": "Hello-Scan-Code 配置文件 (新架构版本)",
  
  "repo_path": ".",
  "search_term": "test,def,void",
  "is_regex": false,
  "validate": false,
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
      ".git", "__pycache__", ".svn", ".hg", ".idea",
      ".vscode", "node_modules", ".tox", "dist", "build"
    ],
    "file_extensions": null
  }
}
```

### 3. 构建和测试

#### 测试新架构
```bash
# 测试新架构集成
make test-new-arch

# 或直接运行
python test_new_architecture.py
```

#### 构建可执行文件
```bash
# Linux平台构建
make build-linux

# Windows平台构建  
make build-windows

# 完整构建流程
make all
```

## 📋 配置系统详解

### 配置加载优先级

1. **JSON配置文件** (最高优先级)
   - 开发环境：项目根目录的 `config.json`
   - 打包环境：可执行文件同目录的 `config.json`

2. **环境变量** (中等优先级)
   - `REPO_PATH`、`SEARCH_TERM`、`LOG_LEVEL` 等

3. **默认配置** (最低优先级)
   - 内置在代码中的默认值

### 配置管理器使用

```python
from src.config import get_config_manager, get_app_config

# 获取配置管理器
manager = get_config_manager()

# 获取应用配置
app_config = get_app_config()

# 创建配置模板
manager.create_config_template()

# 获取配置信息
config_info = manager.get_config_info()
```

### JSON配置加载器

```python
from src.config import get_json_loader, load_config_from_json

# 获取JSON加载器
loader = get_json_loader()

# 加载JSON配置
config = AppConfig()
config = load_config_from_json(config)

# 创建配置模板
loader.save_config_template()
```

## 🔧 构建系统详解

### 新架构构建特性

1. **智能依赖检测**：自动检测新架构模块的依赖关系
2. **配置模板管理**：自动生成和复制配置模板文件
3. **资源文件收集**：智能收集配置文件、数据库迁移等资源
4. **多平台支持**：针对Windows和Linux平台的优化配置

### 使用构建脚本

#### Windows平台
```bash
# 基本构建
python scripts/build_windows.py

# 安装依赖并构建
python scripts/build_windows.py --install-deps

# 不清理构建目录
python scripts/build_windows.py --no-clean
```

#### Linux平台
```bash
# 基本构建
python scripts/build_linux.py

# 安装依赖并构建
python scripts/build_linux.py --install-deps

# 不清理构建目录
python scripts/build_linux.py --no-clean
```

### 手动PyInstaller打包

```bash
# Windows单文件模式
python -m PyInstaller --clean --noconfirm build/windows/hello-scan-code.spec

# Linux目录模式
python -m PyInstaller --clean --noconfirm build/linux/hello-scan-code.spec
```

## 📦 部署指南

### Windows部署

1. **下载分发包**：`hello-scan-code-v1.0.0-windows.zip`
2. **解压到目标目录**
3. **配置应用**：
   ```cmd
   copy config.template.json config.json
   notepad config.json
   ```
4. **运行程序**：
   ```cmd
   hello-scan-code.exe
   ```

### Linux部署

1. **下载分发包**：`hello-scan-code-v1.0.0-linux.tar.gz`
2. **解压并部署**：
   ```bash
   tar -xzf hello-scan-code-v1.0.0-linux.tar.gz
   cd hello-scan-code-v1.0.0-linux
   ```
3. **使用启动脚本**（推荐）：
   ```bash
   ./run-hello-scan-code.sh
   ```
4. **或直接运行**：
   ```bash
   ./hello-scan-code/hello-scan-code
   ```

## 🔍 配置示例

### 基本搜索配置
```json
{
  "repo_path": "/path/to/your/code",
  "search_term": "function,class,def",
  "is_regex": false,
  "validate": false,
  "output": {
    "db_path": "search_results.db",
    "excel_path": "search_report.xlsx"
  }
}
```

### 高级搜索配置
```json
{
  "repo_path": ".",
  "search_term": "TODO|FIXME|BUG",
  "is_regex": true,
  "validate": true,
  "validate_workers": 8,
  "logging": {
    "level": "DEBUG",
    "file_path": "logs/debug.log"
  },
  "filters": {
    "file_extensions": [".py", ".js", ".java", ".cpp"],
    "ignore_dirs": [
      ".git", "node_modules", "dist", "build",
      "__pycache__", ".vscode", ".idea"
    ]
  }
}
```

### 性能优化配置
```json
{
  "repo_path": ".",
  "search_term": "performance,optimization",
  "validate": true,
  "validate_workers": 16,
  "database": {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 60
  },
  "logging": {
    "level": "INFO",
    "rotation": "100 MB",
    "retention": "30 days"
  }
}
```

## 🛠️ 开发者指南

### 扩展配置系统

1. **添加新配置类**：
```python
from src.config.base_config import BaseConfig

class MyConfig(BaseConfig):
    def __init__(self):
        self.my_setting = "default_value"
    
    def load_from_env(self):
        self.my_setting = self.get_env_var('MY_SETTING', self.my_setting)
    
    def validate(self):
        return bool(self.my_setting)
```

2. **注册到配置管理器**：
```python
from src.config import get_config_manager

manager = get_config_manager()
my_config = manager.get_config(MyConfig)
```

### 添加新的打包资源

```python
from src.packaging import ResourceBundler

class CustomResourceBundler(ResourceBundler):
    def collect_custom_files(self):
        # 自定义资源收集逻辑
        return [(source, target), ...]
```

## 🔧 故障排除

### 常见问题

1. **配置文件加载失败**
   ```bash
   # 验证JSON格式
   python -c "import json; json.load(open('config.json'))"
   
   # 测试配置加载
   python -c "from src.config import get_app_config; print(get_app_config().repo_path)"
   ```

2. **模块导入错误**
   ```bash
   # 测试新架构模块
   python test_new_architecture.py
   
   # 检查Python路径
   python -c "import sys; print(sys.path)"
   ```

3. **打包资源缺失**
   ```bash
   # 验证资源收集
   python -c "from src.packaging import ResourceBundler; print(ResourceBundler().validate_resources())"
   ```

### 调试技巧

1. **启用详细日志**：
   ```json
   {
     "logging": {
       "level": "DEBUG"
     }
   }
   ```

2. **验证配置加载**：
   ```bash
   python -c "from src.config import get_config_manager; print(get_config_manager().get_all_configs())"
   ```

3. **测试打包模块**：
   ```bash
   python -c "from src.packaging import get_hidden_imports; print(len(get_hidden_imports()))"
   ```

## 📊 性能对比

| 特性 | 原架构 | 新架构 | 改进 |
|------|--------|--------|------|
| 配置加载 | 单一配置文件 | 模块化 + JSON | ✓ 更灵活 |
| 错误处理 | 基础验证 | 多层验证 | ✓ 更健壮 |
| 扩展性 | 有限 | 高度模块化 | ✓ 易扩展 |
| 打包效率 | 手动配置 | 智能收集 | ✓ 更自动化 |
| 维护性 | 中等 | 高 | ✓ 更易维护 |

## 📝 更新日志

### v1.0.0 (新架构版本)
- 🏗️ 全新模块化架构重构
- 🎯 统一配置管理系统
- 📄 JSON配置文件支持
- 🚀 增强的PyInstaller打包支持
- 🔧 自动化构建和测试工具
- 📚 完整的文档和使用指南
- 🔄 完全向后兼容

## 🤝 贡献指南

欢迎为新架构贡献代码！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd Hello-Scan-Code

# 安装依赖
make install

# 运行测试
make test

# 测试新架构
make test-new-arch
```

### 代码规范

- 遵循现有的模块化架构
- 所有配置类继承 `BaseConfig`
- 使用统一的日志接口
- 编写相应的测试用例
- 更新相关文档

## 📞 技术支持

如遇到问题，请检查：

1. **Python版本**：确保使用 Python 3.10+
2. **依赖安装**：运行 `make install` 确保所有依赖已安装
3. **配置格式**：验证JSON配置文件格式正确
4. **架构测试**：运行 `make test-new-arch` 验证新架构功能

更多技术支持请参考项目 README 或提交 Issue。