"""
主题配置管理器

管理5种专业主题的配置和应用
"""

from typing import Any, Dict, List


class ThemeManager:
    """主题配置管理器"""

    # 主题配置定义
    THEMES = {
        "compact": {
            "theme": "base",
            "themeVariables": {
                "primaryColor": "#4A90E2",
                "primaryTextColor": "#000000",
                "primaryBorderColor": "#2E5E99",
                "lineColor": "#333333",
                "secondaryColor": "#F0F8FF",
                "tertiaryColor": "#E8F4FD",
                "background": "#FFFFFF",
                "mainBkg": "#4A90E2",
                "secondBkg": "#E8F4FD",
                "tertiaryBkg": "#F0F8FF",
            },
            "flowchart": {"nodeSpacing": 30, "rankSpacing": 40, "padding": 10},
        },
        "professional": {
            "theme": "base",
            "themeVariables": {
                "primaryColor": "#2E5E99",
                "primaryTextColor": "#000000",
                "primaryBorderColor": "#1A4D7A",
                "lineColor": "#2E5E99",
                "secondaryColor": "#E8F4FD",
                "tertiaryColor": "#F0F8FF",
                "background": "#FFFFFF",
            },
        },
        "minimal": {
            "theme": "base",
            "themeVariables": {
                "primaryColor": "#000000",
                "primaryTextColor": "#000000",
                "primaryBorderColor": "#000000",
                "lineColor": "#000000",
                "secondaryColor": "#FFFFFF",
                "tertiaryColor": "#F5F5F5",
                "background": "#FFFFFF",
            },
        },
        "dark-pro": {
            "theme": "dark",
            "themeVariables": {
                "primaryColor": "#64B5F6",
                "primaryTextColor": "#FFFFFF",
                "primaryBorderColor": "#42A5F5",
                "lineColor": "#64B5F6",
                "secondaryColor": "#263238",
                "tertiaryColor": "#37474F",
                "background": "#1E1E1E",
            },
        },
        "default": {
            "theme": "default",
            "themeVariables": {"primaryTextColor": "#000000", "lineColor": "#333333"},
        },
    }

    @classmethod
    def get_theme_config(cls, theme_name: str) -> Dict[str, Any]:
        """
        获取主题配置

        Args:
            theme_name: 主题名称

        Returns:
            Dict[str, Any]: 主题配置字典
        """
        return cls.THEMES.get(theme_name, cls.THEMES["default"])

    @classmethod
    def get_available_themes(cls) -> List[str]:
        """获取所有可用主题列表"""
        return list(cls.THEMES.keys())

    @classmethod
    def is_valid_theme(cls, theme_name: str) -> bool:
        """检查主题名称是否有效"""
        return theme_name in cls.THEMES

    @classmethod
    def get_theme_description(cls, theme_name: str) -> str:
        """获取主题描述"""
        descriptions = {
            "compact": "紧凑主题，最大化信息密度，节点间距最小",
            "professional": "专业蓝色主题，商务风格，文字清晰",
            "minimal": "极简黑白主题，最高对比度，适合文档",
            "dark-pro": "深色专业主题，适合演示场景",
            "default": "默认优化主题，平衡美观与可读性",
        }
        return descriptions.get(theme_name, "未知主题")

    @classmethod
    def get_theme_info(cls) -> Dict[str, str]:
        """获取所有主题的信息"""
        return {
            theme: cls.get_theme_description(theme)
            for theme in cls.get_available_themes()
        }
