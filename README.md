# Hello-Scan-Code - 高效代码搜索工具

Hello-Scan-Code 是一个专为大型代码仓库设计的高效搜索工具。它结合了 `grep` 的速度和 Python 的灵活性，能够快速定位包含特定字符串或正则表达式的文件。现已支持PyInstaller打包，可生成独立可执行文件。

## ✨ 新功能特性

### 🚀 PyInstaller 打包支持
- **独立部署**：生成无需Python环境的可执行文件
- **跨平台分发**：支持Windows和Linux平台
- **零依赖运行**：打包后程序包含所有必要依赖

### 📋 JSON 配置系统
- **外置配置**：支持 `config.json` 配置文件
- **配置验证**：自动验证配置文件格式和有效性
- **向后兼容**：保持与现有配置方式的兼容性
- **智能回退**：配置错误时自动使用默认配置

## 📦 安装方式

### 方式一：下载可执行文件（推荐）

从 [Releases](https://github.com/your-repo/releases) 页面下载对应平台的预编译版本：

- `hello-scan-code-v1.0.0-windows.zip` - Windows 平台
- `hello-scan-code-v1.0.0-linux.tar.gz` - Linux 平台

### 方式二：从源码安装（开发者）

```bash
# 克隆项目
git clone <repository-url>
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
```

## 📋 JSON 配置系统

### 配置文件示例

```json
{
  "repo_path": ".",
  "search_term": "TODO,FIXME,BUG",
  "is_regex": false,
  "validate": true,
  "validate_workers": 4,
  
  "output": {
    "db_path": "results.db",
    "excel_path": "results.xlsx"
  },
  
  "logging": {
    "level": "INFO"
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

### 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `repo_path` | string | `"."` | 搜索目标代码仓库路径 |
| `search_term` | string | `"test,def,void"` | 搜索关键词，逗号分隔 |
| `is_regex` | boolean | `false` | 是否启用正则表达式搜索 |
| `validate` | boolean | `false` | 是否启用结果二次验证 |
| `validate_workers` | integer | `4` | 验证工作线程数量 |
| `output.db_path` | string | `"results.db"` | SQLite数据库输出路径 |
| `output.excel_path` | string | `"results.xlsx"` | Excel报告输出路径 |
| `logging.level` | string | `"INFO"` | 日志级别 |
| `filters.ignore_dirs` | array | `[".git", "__pycache__"]` | 忽略目录列表 |
| `filters.file_extensions` | array\|null | `null` | 文件扩展名过滤器 |

## 🔧 开发者指南

### 构建可执行文件

```bash
# 使用Makefile构建
make build-windows  # Windows平台
make build-linux    # Linux平台
make all           # 完整构建流程

# 或手动执行构建脚本
python scripts/build_windows.py
python scripts/build_linux.py
```

### 测试功能

```bash
# 测试配置系统
python test_config_system.py

# 测试打包功能
python test_packaging.py

# 或使用Makefile
make test
```

### 手动PyInstaller打包

```bash
# Windows单文件模式
python -m PyInstaller --clean --noconfirm build/windows/hello-scan-code.spec

# Linux目录模式
python -m PyInstaller --clean --noconfirm build/linux/hello-scan-code.spec
```

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

## 🔗 相关文档

- [PyInstaller打包使用指南](PYINSTALLER_GUIDE.md) - 详细的打包和部署指南
- [API文档](docs/api.md) - 开发者API参考
- [FAQ](docs/faq.md) - 常见问题解答

## 📝 更新日志

### v1.0.0 (2025-01)
- ✨ 新增 PyInstaller 打包支持
- ✨ 新增 JSON 配置系统
- ✨ 新增 配置验证和错误处理
- ✨ 新增 跨平台构建脚本
- ✨ 新增 Makefile 构建工具
- 📝 完善文档和使用指南

## 🤝 贡献

欢迎提交 Pull Requests 和 Issues！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>
cd Hello-Scan-Code

# 安装开发依赖
make dev-install

# 运行测试
make test

# 代码格式化
make format

# 代码检查
make lint
```

## 📝 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。