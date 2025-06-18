"""
MCP-Mermaid: 智能Mermaid图表生成MCP服务器

支持布局优化、主题系统和高质量输出的Model Context Protocol服务
"""

__version__ = "1.0.0"
__author__ = "MCP-Mermaid Team"
__description__ = "智能Mermaid图表生成工具，支持布局优化、主题系统和高质量输出"

from .core.generator import MermaidGenerator
from .tools.mermaid_tools import MermaidTools

__all__ = [
    "MermaidGenerator",
    "MermaidTools",
    "__version__",
]
