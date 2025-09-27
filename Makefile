# Hello-Scan-Code PyInstaller 构建 Makefile (新架构版本)

.PHONY: help clean test install build-windows build-linux package all

# 默认目标
help:
	@echo "Hello-Scan-Code PyInstaller 构建工具 (新架构版本)"
	@echo ""
	@echo "可用目标:"
	@echo "  help           - 显示此帮助信息"
	@echo "  install        - 安装项目依赖"
	@echo "  test           - 运行所有测试"
	@echo "  test-config    - 测试配置系统"
	@echo "  test-new-arch  - 测试新架构集成"
	@echo "  test-packaging - 测试打包功能"
	@echo "  clean          - 清理构建目录"
	@echo "  build-windows  - 构建Windows可执行文件"
	@echo "  build-linux    - 构建Linux可执行文件"
	@echo "  package        - 创建分发包"
	@echo "  all            - 执行完整构建流程"
	@echo ""
	@echo "使用示例:"
	@echo "  make install       # 安装依赖"
	@echo "  make test          # 运行测试"
	@echo "  make build-linux   # 构建Linux版本"
	@echo "  make clean         # 清理构建目录"

# 安装项目依赖
install:
	@echo "安装项目依赖..."
	pip install --upgrade pip
	pip install pyinstaller>=6.0.0
	pip install loguru pandas openpyxl sqlalchemy alembic

# 运行所有测试
test: test-config test-new-arch test-packaging

# 测试配置系统
test-config:
	@echo "测试配置系统..."
	@if [ -f "tests/unit/test_config.py" ]; then \
		python -m pytest tests/unit/test_config.py -v; \
	else \
		echo "警告: tests/unit/test_config.py 不存在"; \
	fi

# 测试新架构集成
test-new-arch:
	@echo "测试新架构集成..."
	python test_new_architecture.py

# 测试打包功能
test-packaging:
	@echo "测试打包功能..."
	python -c "from src.packaging import ResourceBundler, get_hidden_imports; print('✓ 打包模块导入成功')"

# 清理构建目录
clean:
	@echo "清理构建目录..."
	rm -rf dist/
	rm -rf build/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 构建Windows可执行文件
build-windows:
	@echo "构建Windows可执行文件..."
	python scripts/build_windows.py

# 构建Linux可执行文件  
build-linux:
	@echo "构建Linux可执行文件..."
	python scripts/build_linux.py

# 创建分发包
package:
	@echo "创建分发包..."
	@if [ -d "dist/windows" ]; then \
		cd dist && zip -r hello-scan-code-windows.zip windows/; \
		echo "Windows分发包: dist/hello-scan-code-windows.zip"; \
	fi
	@if [ -d "dist/linux" ]; then \
		cd dist && tar -czf hello-scan-code-linux.tar.gz linux/; \
		echo "Linux分发包: dist/hello-scan-code-linux.tar.gz"; \
	fi

# 执行完整构建流程
all: clean install test
	@echo "执行完整构建流程..."
	@echo "当前平台: $$(uname -s)"
	@if [ "$$(uname -s)" = "Linux" ]; then \
		$(MAKE) build-linux; \
	elif [ "$$(uname -s)" = "Darwin" ]; then \
		$(MAKE) build-linux; \
	else \
		$(MAKE) build-windows; \
	fi
	$(MAKE) package
	@echo "构建完成！"

# 快速构建（跳过测试）
quick-build:
	@echo "快速构建..."
	@if [ "$$(uname -s)" = "Linux" ]; then \
		$(MAKE) build-linux; \
	else \
		$(MAKE) build-windows; \
	fi

# 创建配置文件
config:
	@echo "创建配置文件..."
	@if [ ! -f "config.json" ]; then \
		cp config/config.template.json config.json; \
		echo "已创建 config.json，请根据需要修改配置"; \
	else \
		echo "config.json 已存在"; \
	fi

# 显示构建信息
info:
	@echo "构建环境信息:"
	@echo "Python版本: $$(python --version 2>&1 || echo 'Python未安装')"
	@echo "操作系统: $$(uname -s)"
	@echo "项目目录: $$(pwd)"
	@echo "配置文件: $$([ -f config.json ] && echo '存在' || echo '不存在')"
	@echo "新架构支持: ✓"
	@echo "JSON配置支持: ✓"
	@echo "PyInstaller打包支持: ✓"

# 运行项目（开发模式）
run:
	@echo "运行项目..."
	python main.py

# 创建配置模板
create-template:
	@echo "创建配置模板..."
	python -c "from src.config import create_config_template; create_config_template(); print('配置模板已创建')"