"""
MCP-Mermaid包安装配置

智能Mermaid图表生成MCP服务器
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "MCP-Mermaid: 智能Mermaid图表生成工具"

# 读取requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return ["requests>=2.25.0"]

setup(
    name="mcp-mermaid",
    version="1.0.0",
    author="MCP-Mermaid Team",
    author_email="dev@mcp-mermaid.com",
    description="智能Mermaid图表生成工具，支持布局优化、主题系统和高质量输出",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/mcp-mermaid/mcp-mermaid",
    
    # 包配置
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # 依赖项
    install_requires=read_requirements(),
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 分类信息
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Text Processing :: Markup",
    ],
    
    # 关键词
    keywords="mcp, mermaid, diagram, visualization, charts, model-context-protocol",
    
    # 控制台脚本
    entry_points={
        "console_scripts": [
            "mcp-mermaid=mcp_mermaid.server:main_sync",
        ],
    },
    
    # 项目URL
    project_urls={
        "Bug Reports": "https://github.com/mcp-mermaid/mcp-mermaid/issues",
        "Source": "https://github.com/mcp-mermaid/mcp-mermaid",
        "Documentation": "https://github.com/mcp-mermaid/mcp-mermaid/blob/main/README.md",
    },
    
    # 额外数据文件
    package_data={
        "mcp_mermaid": ["*.json", "*.md"],
    },
    
    # 可选依赖
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.0",
        ],
    },
) 