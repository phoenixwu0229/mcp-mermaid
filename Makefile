# MCP-Mermaid 自动构建脚本
# 提供开发、测试、构建、发布的完整自动化流程

.PHONY: help install dev-install test lint format build clean publish test-publish docker all

# 默认目标
help:
	@echo "🔨 MCP-Mermaid 自动构建系统"
	@echo "================================"
	@echo "📦 安装和环境"
	@echo "  install      - 安装项目依赖"
	@echo "  dev-install  - 安装开发依赖"
	@echo ""
	@echo "🧪 开发和测试"
	@echo "  test         - 运行所有测试"
	@echo "  test-coverage- 运行测试覆盖率检查(基础30%)"
	@echo "  test-coverage-report - 生成详细覆盖率报告"
	@echo "  test-coverage-strict - 严格覆盖率检查(目标70%)"
	@echo "  test-quick   - 快速测试(遇到失败即停止)"
	@echo "  lint         - 代码检查"
	@echo "  lint-strict  - 严格代码检查(含类型检查)"
	@echo "  format       - 代码格式化"
	@echo "  format-check - 检查代码格式"
	@echo ""
	@echo "📦 构建和发布"
	@echo "  build        - 构建包"
	@echo "  clean        - 清理构建文件"
	@echo "  publish      - 发布到PyPI"
	@echo "  test-publish - 发布到TestPyPI"
	@echo ""
	@echo "🐳 容器化"
	@echo "  docker       - 构建Docker镜像"
	@echo ""
	@echo "🎯 快捷命令"
	@echo "  all          - 完整构建流程(测试+构建+检查)"
	@echo "  qa           - 质量保证检查(格式+严格检查+覆盖率)"
	@echo "  qa-fix       - 质量问题修复(格式化+检查+测试)"

# 安装和环境配置
install:
	@echo "📥 安装项目依赖..."
	pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .

dev-install: install
	@echo "📥 安装开发依赖..."
	pip install -i https://mirrors.aliyun.com/pypi/simple/ -e ".[dev,test]"

# 开发和测试
test:
	@echo "🧪 运行测试..."
	@if command -v pytest >/dev/null 2>&1; then \
		python -m pytest tests/ -v; \
	else \
		echo "⚠️ pytest未安装，跳过测试"; \
	fi

test-coverage:
	@echo "📊 运行测试覆盖率检查..."
	@if command -v pytest >/dev/null 2>&1; then \
		python -m pytest tests/ --cov=mcp_mermaid --cov-report=term --cov-report=html --cov-fail-under=30; \
	else \
		echo "⚠️ pytest或pytest-cov未安装，跳过覆盖率检查"; \
	fi

test-coverage-report:
	@echo "📊 生成详细覆盖率报告..."
	@if command -v pytest >/dev/null 2>&1; then \
		python -m pytest tests/ --cov=mcp_mermaid --cov-report=term-missing --cov-report=html; \
		echo "📄 HTML报告: htmlcov/index.html"; \
	else \
		echo "⚠️ pytest或pytest-cov未安装，跳过覆盖率检查"; \
	fi

test-coverage-strict:
	@echo "📊 严格覆盖率检查(目标70%)..."
	@if command -v pytest >/dev/null 2>&1; then \
		python -m pytest tests/ --cov=mcp_mermaid --cov-report=term --cov-report=html --cov-fail-under=70; \
	else \
		echo "⚠️ pytest或pytest-cov未安装，跳过覆盖率检查"; \
	fi

test-quick:
	@echo "⚡ 快速测试..."
	@if command -v pytest >/dev/null 2>&1; then \
		python -m pytest tests/ -x -q; \
	else \
		echo "⚠️ pytest未安装，跳过测试"; \
	fi

lint:
	@echo "🔍 代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		python -m flake8 src/ tests/ --max-line-length=88 --exclude=__pycache__; \
	else \
		echo "⚠️ flake8未安装，跳过代码检查"; \
	fi

lint-strict:
	@echo "🔍 严格代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		python -m flake8 src/ tests/ --max-line-length=88 --exclude=__pycache__ --max-complexity=10; \
	else \
		echo "⚠️ flake8未安装，跳过代码检查"; \
	fi
	@if command -v mypy >/dev/null 2>&1; then \
		echo "🔍 类型检查..."; \
		python -m mypy src/ --ignore-missing-imports; \
	else \
		echo "⚠️ mypy未安装，跳过类型检查"; \
	fi

format:
	@echo "✨ 代码格式化..."
	@echo "🔧 使用 black 格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		python -m black src/ tests/; \
	else \
		echo "⚠️ black未安装，跳过代码格式化"; \
	fi
	@echo "🔧 使用 autopep8 修复 PEP8 问题..."
	@if command -v autopep8 >/dev/null 2>&1; then \
		python -m autopep8 --in-place --recursive --aggressive --aggressive src/ tests/; \
	else \
		echo "📥 安装 autopep8..."; \
		pip install -i https://mirrors.aliyun.com/pypi/simple/ autopep8; \
		python -m autopep8 --in-place --recursive --aggressive --aggressive src/ tests/; \
	fi
	@echo "🔧 使用 isort 整理导入..."
	@if command -v isort >/dev/null 2>&1; then \
		python -m isort src/ tests/ --profile black; \
	else \
		echo "📥 安装 isort..."; \
		pip install -i https://mirrors.aliyun.com/pypi/simple/ isort; \
		python -m isort src/ tests/ --profile black; \
	fi
	@echo "🗑️ 移除未使用的导入..."
	@if command -v unimport >/dev/null 2>&1; then \
		python -m unimport --remove src/ tests/; \
	else \
		echo "📥 安装 unimport..."; \
		pip install -i https://mirrors.aliyun.com/pypi/simple/ unimport; \
		python -m unimport --remove src/ tests/; \
	fi
	@echo "🧹 清理多余空白字符..."
	@find src/ tests/ -name "*.py" -exec sed -i 's/[[:space:]]*$$//' {} \;
	@echo "✅ 代码格式化完成"

format-check:
	@echo "🔍 检查代码格式..."
	@if command -v black >/dev/null 2>&1; then \
		python -m black --check src/ tests/; \
	else \
		echo "⚠️ black未安装，跳过格式检查"; \
	fi

# 构建和发布
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean
	@echo "📦 构建包..."
	@if command -v python -m build >/dev/null 2>&1; then \
		python -m build; \
	else \
		echo "📥 安装build工具..."; \
		pip install -i https://mirrors.aliyun.com/pypi/simple/ build; \
		python -m build; \
	fi

check-build: build
	@echo "🔍 检查包..."
	@if command -v twine >/dev/null 2>&1; then \
		python -m twine check dist/*; \
	else \
		echo "📥 安装twine..."; \
		pip install -i https://mirrors.aliyun.com/pypi/simple/ twine; \
		python -m twine check dist/*; \
	fi

test-publish: check-build
	@echo "🚀 发布到TestPyPI..."
	python -m twine upload --repository testpypi dist/*
	@echo "📖 测试安装: pip install --index-url https://test.pypi.org/simple/ mcp-mermaid"

publish: check-build
	@echo "⚠️ 准备发布到正式PyPI..."
	@read -p "确认发布到PyPI? [y/N] " confirm && [ "$$confirm" = "y" ]
	python -m twine upload dist/*
	@echo "🎉 发布完成! 安装命令: pip install mcp-mermaid"

# 容器化
docker:
	@echo "🐳 构建Docker镜像..."
	docker build -t mcp-mermaid:latest .
	@echo "✅ Docker镜像构建完成: mcp-mermaid:latest"

# 快捷命令
all: test lint build check-build
	@echo "🎉 完整构建流程完成!"

qa: format-check lint-strict test-coverage
	@echo "🎯 质量保证检查完成!"

qa-fix: format lint test
	@echo "🔧 质量问题修复完成!"

# 开发环境设置
setup-dev: dev-install
	@echo "⚙️ 设置开发环境..."
	@if [ ! -f .env ]; then \
		echo "创建.env文件..."; \
		echo "# MCP-Mermaid 开发环境配置" > .env; \
		echo "PYTHONPATH=./src" >> .env; \
	fi
	@echo "✅ 开发环境设置完成"

# 版本管理
version:
	@echo "📋 当前版本信息:"
	@python -m setuptools_scm

# 快速验证
verify: install
	@echo "✅ 验证安装..."
	python -c "from mcp_mermaid.core.generator import MermaidGenerator; print('✅ 包导入成功')"
	@if command -v mcp-mermaid >/dev/null 2>&1; then \
		echo "✅ 命令行工具可用"; \
	else \
		echo "❌ 命令行工具不可用"; \
	fi

# 性能测试
benchmark:
	@echo "⚡ 性能基准测试..."
	python -c "\
	from mcp_mermaid.core.optimizer import LayoutOptimizer; \
	import time; \
	optimizer = LayoutOptimizer(); \
	content = 'graph TD\\n    A[开始] --> B[处理]\\n    B --> C[结束]'; \
	start = time.time(); \
	for i in range(100): optimizer.optimize_layout(content); \
	end = time.time(); \
	print(f'💨 100次布局优化耗时: {(end-start)*1000:.2f}ms')" 