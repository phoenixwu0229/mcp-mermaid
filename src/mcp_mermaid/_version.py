"""版本管理模块"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# 版本历史
VERSION_HISTORY = {
    "1.0.0": {
        "date": "2024-12-19",
        "changes": [
            "🎉 初始版本发布",
            "✨ 智能布局优化系统",
            "🎨 5种专业主题支持",
            "📸 高质量图片输出",
            "☁️ ImageBB自动上传",
            "🔧 MCP协议完整集成",
            "📦 标准Python包结构",
        ],
        "compatibility": "Python 3.8+",
        "breaking_changes": [],
    }
}


def get_version():
    """获取当前版本"""
    return __version__


def get_version_info():
    """获取版本信息元组"""
    return __version_info__


def get_changelog(version: str = None):
    """获取版本更新日志"""
    if version:
        return VERSION_HISTORY.get(version, {})
    return VERSION_HISTORY
