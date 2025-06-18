"""
MCP Mermaid工具接口

提供符合Model Context Protocol规范的Mermaid图表生成工具
"""

from typing import Dict, Any, List
from ..core.generator import MermaidGenerator
from ..themes.configs import ThemeManager


class MermaidTools:
    """MCP Mermaid工具集"""

    def __init__(self):
        self.generator = MermaidGenerator()

    def get_tools(self) -> List[Dict[str, Any]]:
        """返回MCP工具列表"""
        return [
            {
                "name": "generate_diagram",
                "description": "生成Mermaid图表，支持智能布局优化、主题配置和高质量输出",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Mermaid图表的DSL内容",
                        },
                        "theme": {
                            "type": "string",
                            "description": "主题名称",
                            "enum": list(ThemeManager.get_available_themes()),
                            "default": "default",
                        },
                        "optimize_layout": {
                            "type": "boolean",
                            "description": "是否启用智能布局优化",
                            "default": True,
                        },
                        "quality": {
                            "type": "string",
                            "description": "输出图片质量",
                            "enum": ["low", "medium", "high"],
                            "default": "high",
                        },
                        "upload_image": {
                            "type": "boolean",
                            "description": "是否上传图片到云端并返回URL",
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
            {
                "name": "optimize_layout",
                "description": "仅对Mermaid图表进行布局优化，不生成图片",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "要优化的Mermaid图表DSL内容",
                        }
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "get_theme_info",
                "description": "获取所有可用主题的信息和描述",
                "inputSchema": {"type": "object", "properties": {}, "required": []},
            },
        ]

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用指定的工具"""
        if name == "generate_diagram":
            return self._generate_diagram(**arguments)
        elif name == "optimize_layout":
            return self._optimize_layout(**arguments)
        elif name == "get_theme_info":
            return self._get_theme_info()
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
                response = {
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
                if result.get("image_url"):
                    response["data"]["image_url"] = result["image_url"]
                    response["data"]["markdown_link"] = result["markdown_link"]

                return response
            else:
                return {
                    "success": False,
                    "error": result.get("error", "生成失败"),
                    "details": result,
                }

        except Exception as e:
            return {"success": False, "error": f"生成过程异常: {str(e)}"}

    def _optimize_layout(self, content: str) -> Dict[str, Any]:
        """优化Mermaid图表布局"""
        try:
            optimized_content, optimization_reason = (
                self.generator.optimizer.optimize_layout(content)
            )

            return {
                "success": True,
                "message": "布局优化完成",
                "data": {
                    "original_content": content,
                    "optimized_content": optimized_content,
                    "optimization_reason": optimization_reason,
                    "was_optimized": optimized_content != content,
                },
            }

        except Exception as e:
            return {"success": False, "error": f"布局优化异常: {str(e)}"}

    def _get_theme_info(self) -> Dict[str, Any]:
        """获取主题信息"""
        try:
            themes = ThemeManager.get_theme_info()

            return {
                "success": True,
                "message": "主题信息获取成功",
                "data": {
                    "available_themes": themes,
                    "total_count": len(themes),
                    "default_theme": "default",
                },
            }

        except Exception as e:
            return {"success": False, "error": f"获取主题信息异常: {str(e)}"}

    def get_stats(self) -> Dict[str, Any]:
        """获取工具使用统计"""
        return {
            "optimizer_stats": self.generator.get_optimizer_stats(),
            "available_themes": len(ThemeManager.get_available_themes()),
            "tools_count": len(self.get_tools()),
        }

    def cleanup(self):
        """清理资源"""
        self.generator.cleanup()
