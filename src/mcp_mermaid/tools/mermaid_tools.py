"""
MCP Mermaid工具接口

提供符合Model Context Protocol规范的Mermaid图表生成工具
"""

from typing import Any, Dict, List

from ..core.generator import MermaidGenerator
from ..themes.configs import ThemeManager


class MermaidTools:
    """MCP Mermaid工具集"""

    def __init__(self) -> None:
        self.generator = MermaidGenerator()

    def get_tools(self) -> List[Dict[str, Any]]:
        """返回MCP工具列表"""
        return [
            {
                "name": "generate_diagram",
                "description": (
                    "生成Mermaid图表，支持智能布局优化、主题配置和高质量输出。"
                    "内置布局优化和主题选择功能，一个工具完成所有图表生成需求。"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Mermaid图表的DSL内容",
                        },
                        "theme": {
                            "type": "string",
                            "description": (
                                "主题名称。可选：compact(紧凑), professional(专业), "
                                "minimal(极简), dark-pro(深色), default(默认)"
                            ),
                            "enum": list(ThemeManager.get_available_themes()),
                            "default": "default",
                        },
                        "optimize_layout": {
                            "type": "boolean",
                            "description": "是否启用智能布局优化，自动优化图表布局和方向",
                            "default": True,
                        },
                        "quality": {
                            "type": "string",
                            "description": (
                                "输出图片质量：low(低质量,快速), "
                                "medium(中等质量), high(高质量,推荐)"
                            ),
                            "enum": ["low", "medium", "high"],
                            "default": "high",
                        },
                        "upload_image": {
                            "type": "boolean",
                            "description": "是否上传图片到云端并返回URL，便于分享和使用",
                            "default": True,
                        },
                        "title": {
                            "type": "string",
                            "description": "图表标题，用于文件命名和图片描述",
                            "default": "",
                        },
                    },
                    "required": ["content"],
                },
            },
        ]

    def call_tool(self,
                  name: str,
                  arguments: Dict[str,
                                  Any]) -> Dict[str,
                                                Any]:
        """调用指定的工具"""
        if name == "generate_diagram":
            return self._generate_diagram(**arguments)
        else:
            return {"success": False, "error": f"未知工具: {name}"}

    def _generate_diagram(
        self,
        content: str,
        theme: str = "default",
        optimize_layout: bool = True,
        quality: str = "high",
        upload_image: bool = True,
        title: str = "",
    ) -> Dict[str, Any]:
        """生成Mermaid图表"""
        try:
            result = self.generator.generate_diagram(
                content=content,
                theme=theme,
                optimize_layout=optimize_layout,
                quality=quality,
                upload_image=upload_image,
                title=title,
            )

            # 格式化返回结果
            if result["success"]:
                response: Dict[str, Any] = {
                    "success": True,
                    "message": "图表生成成功",
                    "data": {
                        "theme": result["theme"],
                        "layout_optimization": result["layout_optimization"],
                        "optimized_content": result["optimized_content"],
                        "image_path": result["image_path"],
                    },
                }

                # 添加云端信息（如果上传成功）
                data_dict = response["data"]
                if result.get("image_url"):
                    data_dict["image_url"] = result["image_url"]
                    data_dict["markdown_link"] = result["markdown_link"]

                # 总是包含主题信息和优化详情
                themes = ThemeManager.get_theme_info()
                data_dict["available_themes"] = themes
                data_dict["theme_count"] = len(themes)

                data_dict["optimization_details"] = {
                    "original_content": content,
                    "was_optimized": result["optimized_content"] != content,
                    "optimizer_stats": self.generator.get_optimizer_stats(),
                }

                return response
            else:
                return {
                    "success": False,
                    "error": result.get("error", "生成失败"),
                    "details": result,
                }

        except Exception as e:
            return {"success": False, "error": f"生成过程异常: {str(e)}"}

    def get_stats(self) -> Dict[str, Any]:
        """获取工具使用统计"""
        return {
            "optimizer_stats": self.generator.get_optimizer_stats(),
            "available_themes": len(ThemeManager.get_available_themes()),
            "tools_count": len(self.get_tools()),
        }

    def cleanup(self) -> None:
        """清理资源"""
        self.generator.cleanup()
