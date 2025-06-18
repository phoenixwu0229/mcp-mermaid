#!/usr/bin/env python3
"""
MCP-Mermaid 便捷函数库

提供快捷函数用于生成不同类型的Mermaid图表
"""

from mermaid_to_imagebb import mermaid_to_imagebb

def flowchart(mermaid_content, title="流程图", theme="professional"):
    """生成流程图 - 使用专业主题"""
    return mermaid_to_imagebb(mermaid_content, title, theme, "png", "high")

def architecture(mermaid_content, title="架构图", theme="minimal"):
    """生成架构图 - 使用极简主题"""
    return mermaid_to_imagebb(mermaid_content, title, theme, "png", "high")

def presentation(mermaid_content, title="演示图", theme="dark-pro"):
    """生成演示图 - 使用深色专业主题"""
    return mermaid_to_imagebb(mermaid_content, title, theme, "png", "high")

def compact(mermaid_content, title="紧凑图表", theme="compact"):
    """生成紧凑图表 - 最大化信息密度"""
    return mermaid_to_imagebb(mermaid_content, title, theme, "png", "high")

def ultra_hd(mermaid_content, title="超高清图表", theme="default"):
    """生成超高清图表"""
    return mermaid_to_imagebb(mermaid_content, title, theme, "png", "ultra")

def vector_svg(mermaid_content, title="矢量图", theme="default"):
    """生成SVG矢量图"""
    return mermaid_to_imagebb(mermaid_content, title, theme, "svg", "high")

def mermaid_to_markdown(mermaid_content, title="", theme="default", format="png", quality="high"):
    """通用函数 - 生成Mermaid图表的markdown链接"""
    return mermaid_to_imagebb(mermaid_content, title, theme, format, quality)

# 快捷主题函数
def professional_chart(mermaid_content, title="专业图表"):
    """专业蓝色主题图表"""
    return flowchart(mermaid_content, title, "professional")

def minimal_chart(mermaid_content, title="极简图表"):
    """极简黑白主题图表"""
    return architecture(mermaid_content, title, "minimal")

def dark_chart(mermaid_content, title="深色图表"):
    """深色专业主题图表"""
    return presentation(mermaid_content, title, "dark-pro")

def compact_chart(mermaid_content, title="紧凑图表"):
    """紧凑信息密度主题图表"""
    return compact(mermaid_content, title, "compact")

# 使用示例
if __name__ == "__main__":
    print("MCP-Mermaid Helper Functions")
    print("===========================================")
    print()
    print("使用示例:")
    print()
    print("# 导入函数")
    print("from mermaid_helper import flowchart, architecture, compact")
    print()
    print("# 生成流程图")
    print("result = flowchart('graph LR\\n    A[开始] --> B[结束]', '简单流程')")
    print("print(result)")
    print()
    print("# 生成架构图")
    print("result = architecture('graph TB\\n    A[前端] --> B[后端]', '系统架构')")
    print("print(result)")
    print()
    print("# 生成紧凑图表")
    print("result = compact('graph LR\\n    A --> B --> C --> D', '信息密度测试')")
    print("print(result)")
    print()
    print("支持的主题:")
    print("- compact: 紧凑主题，最大化信息密度")
    print("- professional: 专业蓝色主题，商务风格")
    print("- minimal: 极简黑白主题，最高对比度")
    print("- dark-pro: 深色专业主题，适合演示")
    print("- default: 默认优化主题") 