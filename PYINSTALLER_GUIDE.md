# PyInstaller 打包使用指南

## 概述

Hello-Scan-Code 现已支持 PyInstaller 打包，可以生成独立的可执行文件，无需在目标系统安装 Python 环境即可运行。

## 新功能特性

### JSON 配置系统
- **外置配置文件**：支持 `config.json` 配置文件，实现配置与代码分离
- **配置验证**：自动验证配置文件格式和数据有效性
- **向后兼容**：保持与现有 Python 配置方式的兼容性
- **默认回退**：配置文件缺失或无效时自动使用默认配置

### 跨平台打包
- **Windows 支持**：生成单文件可执行程序 (.exe)
- **Linux 支持**：生成目录式应用包
- **自动化构建**：提供构建脚本简化打包流程
- **资源管理**：自动打包配置文件、数据库迁移等资源

## 目录结构

```
项目根目录/
├── src/
│   ├── config/                    # JSON配置系统
│   │   ├── config_loader.py       # 配置加载器
│   │   ├── config_validator.py    # 配置验证器
│   │   └── default_config.py      # 默认配置定义
│   ├── packaging/                 # 打包支持模块
│   │   ├── pyinstaller_hooks.py   # PyInstaller钩子
│   │   └── resource_bundler.py    # 资源打包器
│   └── ... (现有模块)
├── config/                        # 配置文件目录
│   ├── config.template.json       # 配置模板
│   └── default.json               # 默认配置
├── build/                         # 构建配置
│   ├── windows/
│   │   └── hello-scan-code.spec   # Windows打包配置
│   └── linux/
│       └── hello-scan-code.spec   # Linux打包配置
├── scripts/                       # 构建脚本
│   ├── build_windows.py           # Windows构建脚本
│   └── build_linux.py             # Linux构建脚本
└── dist/                          # 打包输出目录
```

## 快速开始

### 1. 安装依赖

```bash
# 安装项目依赖（包括PyInstaller）
pip install -r requirements.txt

# 或者手动安装
pip install pyinstaller>=6.0.0 loguru pandas openpyxl sqlalchemy alembic
```

### 2. 配置文件设置

#### 创建配置文件
```bash
# 复制配置模板
cp config/config.template.json config.json

# 编辑配置文件
vim config.json
```

#### 配置文件示例
```json
{
  "repo_path": ".",
  "search_term": "test,def,void",
  "is_regex": false,
  "validate": false,
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
      ".git", "__pycache__", ".svn", ".hg", 
      ".idea", ".vscode", "node_modules", ".tox"
    ],
    "file_extensions": null
  }
}
```

### 3. 构建可执行文件

#### Windows 平台
```bash
# 运行Windows构建脚本
python scripts/build_windows.py

# 带依赖安装的构建
python scripts/build_windows.py --install-deps

# 不清理构建目录
python scripts/build_windows.py --no-clean
```

#### Linux 平台
```bash
# 运行Linux构建脚本
python scripts/build_linux.py

# 带依赖安装的构建
python scripts/build_linux.py --install-deps

# 不清理构建目录
python scripts/build_linux.py --no-clean
```

### 4. 测试打包功能

```bash
# 测试配置系统
python test_config_system.py

# 测试打包功能
python test_packaging.py
```

## 配置系统详解

### 配置加载优先级

1. **JSON配置文件**：优先加载可执行文件同目录下的 `config.json`
2. **默认配置**：如果JSON配置不存在或无效，使用内置默认配置
3. **配置合并**：用户配置与默认配置进行智能合并

### 配置文件位置

- **开发环境**：项目根目录下的 `config.json`
- **打包后**：可执行文件同目录下的 `config.json`
- **模板文件**：始终包含 `config.template.json` 作为参考

### 配置验证

系统会自动验证配置文件的：
- **JSON格式正确性**
- **字段类型有效性**
- **数值范围合理性**
- **路径存在性**

### 错误处理

- **格式错误**：显示详细的JSON解析错误信息
- **验证失败**：列出所有验证错误项
- **自动回退**：错误时自动使用默认配置并记录警告
- **路径创建**：自动创建输出文件的父目录

## 构建脚本使用

### Windows 构建脚本 (`scripts/build_windows.py`)

```bash
# 基本构建
python scripts/build_windows.py

# 显示帮助
python scripts/build_windows.py --help

# 可选参数
--no-clean      # 不清理构建目录
--install-deps  # 安装构建依赖
--project-root  # 指定项目根目录
```

**输出文件**：`dist/windows/hello-scan-code.exe`

### Linux 构建脚本 (`scripts/build_linux.py`)

```bash
# 基本构建
python scripts/build_linux.py

# 显示帮助
python scripts/build_linux.py --help

# 可选参数
--no-clean      # 不清理构建目录
--install-deps  # 安装构建依赖
--project-root  # 指定项目根目录
```

**输出文件**：`dist/linux/hello-scan-code/` 目录

## 手动打包

如果需要手动执行PyInstaller打包：

### Windows 单文件模式
```bash
cd 项目根目录
python -m PyInstaller --clean --noconfirm build/windows/hello-scan-code.spec
```

### Linux 目录模式
```bash
cd 项目根目录
python -m PyInstaller --clean --noconfirm build/linux/hello-scan-code.spec
```

## 部署指南

### Windows 部署

1. **下载分发包**：`hello-scan-code-v1.0.0-windows.zip`
2. **解压到目标目录**
3. **配置文件**：
   ```bash
   # 复制配置模板
   copy config.template.json config.json
   
   # 编辑配置文件
   notepad config.json
   ```
4. **运行程序**：
   ```bash
   hello-scan-code.exe
   ```

### Linux 部署

1. **下载分发包**：`hello-scan-code-v1.0.0-linux.tar.gz`
2. **解压到目标目录**：
   ```bash
   tar -xzf hello-scan-code-v1.0.0-linux.tar.gz
   cd hello-scan-code-v1.0.0-linux
   ```
3. **配置文件**：
   ```bash
   # 复制配置模板
   cp hello-scan-code/config.template.json config.json
   
   # 编辑配置文件
   vim config.json
   ```
4. **运行程序**：
   ```bash
   # 使用启动脚本（推荐）
   ./run-hello-scan-code.sh
   
   # 或直接运行
   ./hello-scan-code/hello-scan-code
   ```

## 配置示例

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

### 正则表达式搜索
```json
{
  "repo_path": ".",
  "search_term": "def\\s+\\w+\\s*\\(",
  "is_regex": true,
  "validate": true,
  "validate_workers": 8,
  "filters": {
    "file_extensions": [".py", ".js", ".java"]
  }
}
```

### 性能优化配置
```json
{
  "repo_path": ".",
  "search_term": "TODO,FIXME,BUG",
  "validate": true,
  "validate_workers": 16,
  "filters": {
    "ignore_dirs": [
      ".git", "node_modules", "dist", "build",
      "__pycache__", ".vscode", ".idea"
    ]
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

## 故障排除

### 常见问题

1. **PyInstaller 安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 清理缓存后重新安装
   pip cache purge
   pip install pyinstaller
   ```

2. **打包时缺少模块**
   - 检查 `src/packaging/pyinstaller_hooks.py` 中的隐藏导入列表
   - 添加缺失的模块到 `hiddenimports` 列表

3. **配置文件加载失败**
   - 验证JSON格式正确性
   - 检查文件编码为UTF-8
   - 确认路径使用正斜杠或转义反斜杠

4. **可执行文件过大**
   - 检查 `excludes` 列表，排除不需要的模块
   - 考虑使用目录模式而非单文件模式

5. **运行时找不到资源文件**
   - 检查 `src/packaging/resource_bundler.py` 中的资源文件收集
   - 确认资源文件已正确添加到 `datas` 列表

### 调试技巧

1. **启用详细日志**
   ```json
   {
     "logging": {
       "level": "DEBUG"
     }
   }
   ```

2. **使用控制台模式**
   - Windows: 确保 `.spec` 文件中 `console=True`
   - 查看详细的错误信息和日志输出

3. **验证打包结果**
   ```bash
   # 运行测试脚本
   python test_packaging.py
   
   # 检查资源文件
   python -c "from src.packaging.resource_bundler import ResourceBundler; ResourceBundler().validate_resources()"
   ```

## 开发者指南

### 添加新的配置项

1. **更新默认配置**：修改 `src/config/default_config.py`
2. **更新验证器**：在 `src/config/config_validator.py` 中添加验证规则
3. **更新模板**：修改 `config/config.template.json`

### 添加新的依赖

1. **更新打包钩子**：在 `src/packaging/pyinstaller_hooks.py` 中添加隐藏导入
2. **测试打包**：确保新依赖正确打包
3. **更新文档**：在本文档中说明新依赖的作用

### 自定义构建流程

1. **修改 .spec 文件**：调整打包参数
2. **扩展构建脚本**：添加自定义构建步骤
3. **更新资源收集**：修改 `resource_bundler.py` 收集新资源

## 版本更新

当更新版本时：

1. **更新版本号**：在构建脚本中修改版本号
2. **更新配置**：如有配置格式变更，提供迁移指南
3. **测试兼容性**：确保向后兼容性
4. **更新文档**：同步更新使用文档

## 技术支持

如遇到问题，请检查：

1. **Python版本**：确保使用 Python 3.10+
2. **依赖版本**：确保所有依赖包版本符合要求
3. **系统环境**：确认目标系统的兼容性
4. **配置文件**：验证配置文件格式和内容正确性

更多技术支持请参考项目 README 或提交 Issue。