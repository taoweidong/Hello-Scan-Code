# PyInstaller 打包支持使用指南

## 概述

Hello-Scan-Code 现已支持 PyInstaller 打包，可以生成独立的可执行文件，无需 Python 环境即可运行。同时引入了全新的 JSON 配置系统，提供更灵活的配置管理。

## 新特性

### 1. JSON 配置系统

- **外置配置文件**：支持通过 `config.json` 文件管理所有配置
- **自动发现**：程序会自动查找配置文件
- **Schema 验证**：提供 JSON Schema 验证确保配置正确性
- **向后兼容**：保持与现有配置系统的兼容性

### 2. PyInstaller 打包支持

- **跨平台构建**：支持 Windows 和 Linux 平台
- **单文件模式**：Windows 生成单一 .exe 文件
- **目录模式**：Linux 生成包含依赖的目录结构
- **自动化构建**：提供构建脚本自动化打包流程

## 快速开始

### 使用 JSON 配置

1. **生成配置模板**：
```bash
python config_migration.py --template --output config.json
```

2. **编辑配置文件**：
```json
{
  "repo_path": "./your-project",
  "search_term": "function,class,TODO",
  "is_regex": false,
  "validate": true,
  "validate_workers": 8,
  "output": {
    "db_path": "results/search.db",
    "excel_path": "results/report.xlsx"
  },
  "logging": {
    "level": "INFO"
  },
  "filters": {
    "ignore_dirs": [".git", "__pycache__", "node_modules"],
    "file_extensions": [".py", ".js", ".java", ".cpp"]
  }
}
```

3. **运行搜索**：
```bash
python main.py
```

### 打包为可执行文件

#### Windows 平台

1. **安装依赖**：
```bash
pip install pyinstaller jsonschema
```

2. **执行打包**：
```bash
python scripts/build_windows.py
```

3. **查看结果**：
```
dist/hello-scan-code-v1.0.0-windows/
├── hello-scan-code.exe
├── config.template.json
├── USAGE.md
└── README.md
```

#### Linux 平台

1. **安装依赖**：
```bash
pip install pyinstaller jsonschema
```

2. **执行打包**：
```bash
python scripts/build_linux.py
```

3. **查看结果**：
```
dist/hello-scan-code-v1.0.0-linux/
├── hello-scan-code/          # 应用目录
├── run.sh                    # 启动脚本
├── config.template.json
├── USAGE.md
└── README.md
```

## 配置说明

### JSON 配置文件结构

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `repo_path` | string | `"."` | 搜索目标路径 |
| `search_term` | string | `"test,def,void"` | 搜索关键词（逗号分隔） |
| `is_regex` | boolean | `false` | 是否使用正则表达式 |
| `validate` | boolean | `false` | 是否启用结果验证 |
| `validate_workers` | integer | `4` | 验证工作线程数量 |
| `output.db_path` | string | `"db/results.db"` | SQLite 数据库路径 |
| `output.excel_path` | string | `"report/results.xlsx"` | Excel 报告路径 |
| `logging.level` | string | `"INFO"` | 日志级别 |
| `filters.ignore_dirs` | array | `[".git", "__pycache__"]` | 忽略目录列表 |
| `filters.file_extensions` | array/null | `null` | 文件扩展名过滤 |

### 配置文件查找顺序

1. 当前工作目录下的 `config.json`
2. 可执行文件目录下的 `config.json`
3. `config` 目录下的 `config.json`
4. 内置默认配置

## 高级功能

### 配置验证

验证现有配置文件：
```bash
python config_migration.py --validate config.json
```

### 配置迁移

将旧的 Python 配置转换为 JSON 格式：
```bash
python config_migration.py --migrate --output config.json
```

### 自定义构建

修改 `src/packaging/__init__.py` 中的 `PackagingHelper` 类来自定义打包行为：

- 添加新的隐式导入模块
- 包含额外的数据文件
- 自定义 spec 文件模板

## 部署指南

### 开发环境

1. 克隆项目并安装依赖
2. 复制 `config.template.json` 为 `config.json`
3. 修改配置参数
4. 运行 `python main.py`

### 生产环境

1. 下载对应平台的预编译包
2. 解压到目标目录
3. 复制 `config.template.json` 为 `config.json`
4. 修改配置参数
5. 运行可执行文件

#### Windows 部署

```cmd
# 下载并解压
unzip hello-scan-code-v1.0.0-windows.zip

# 配置
copy config.template.json config.json
notepad config.json

# 运行
hello-scan-code.exe
```

#### Linux 部署

```bash
# 下载并解压
tar -xzf hello-scan-code-v1.0.0-linux.tar.gz

# 配置
cp config.template.json config.json
nano config.json

# 运行
./run.sh
# 或者
./hello-scan-code/hello-scan-code
```

## 故障排查

### 常见问题

1. **配置文件格式错误**
   - 检查 JSON 语法是否正确
   - 使用 `config_migration.py --validate` 验证

2. **路径不存在**
   - 确保 `repo_path` 指向有效目录
   - 使用绝对路径避免路径问题

3. **权限问题**
   - Linux 下确保可执行文件有执行权限
   - 检查输出目录的写入权限

4. **依赖缺失**
   - 预编译包应包含所有必要依赖
   - 如遇问题，尝试在有 Python 环境的机器上运行

### 日志调试

设置更详细的日志级别：
```json
{
  "logging": {
    "level": "DEBUG"
  }
}
```

## 版本兼容性

- **配置兼容性**：JSON 配置与原有 Python 配置并存
- **API 兼容性**：保持所有原有 API 接口不变
- **数据兼容性**：数据库和 Excel 输出格式保持一致

## 技术架构

### 配置系统架构

```
JSON 配置文件 → JSONConfigLoader → JSONConfigAdapter → AppConfig → 应用组件
              ↓
        Schema 验证 → 配置合并 → 默认值填充 → 环境变量覆盖
```

### 打包系统架构

```
源代码 → PyInstaller → 依赖收集 → 资源打包 → 钩子处理 → 可执行文件
       ↓
    Spec 文件 → 隐式导入 → 数据文件 → 平台适配 → 分发包
```

更多详细信息请参考项目主 README.md 文件。