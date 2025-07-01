"""
测试MermaidTools MCP工具接口

包含工具列表获取、工具调用、参数验证、错误处理等功能测试
"""

from unittest.mock import patch

import pytest

from mcp_mermaid.tools.mermaid_tools import MermaidTools


class TestMermaidTools:
    """测试MermaidTools类"""

    @pytest.fixture
    def tools(self):
        """创建工具实例"""
        return MermaidTools()

    @pytest.fixture
    def sample_content(self):
        """示例Mermaid内容"""
        return """graph TD
    A[开始] --> B[处理]
    B --> C[结束]"""

    def test_tools_initialization(self, tools):
        """测试工具初始化"""
        assert tools is not None
        assert hasattr(tools, "generator")
        assert tools.generator is not None

    def test_get_tools_structure(self, tools):
        """测试工具列表结构"""
        tool_list = tools.get_tools()

        assert isinstance(tool_list, list)
        assert len(tool_list) == 1  # 简化为1个综合工具

        # 验证工具名称
        tool_names = [tool["name"] for tool in tool_list]
        assert "generate_diagram" in tool_names
        # 注意：optimize_layout和get_theme_info功能已内置到generate_diagram中

    def test_generate_diagram_tool_schema(self, tools):
        """测试generate_diagram工具的schema"""
        tool_list = tools.get_tools()
        generate_tool = next(
            tool for tool in tool_list if tool["name"] == "generate_diagram"
        )

        assert "description" in generate_tool
        assert "inputSchema" in generate_tool

        schema = generate_tool["inputSchema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "content" in schema["required"]

        # 验证必要属性
        properties = schema["properties"]
        assert "content" in properties
        assert "theme" in properties
        assert "optimize_layout" in properties
        assert "quality" in properties
        assert "upload_image" in properties
        assert "title" in properties

    def test_generate_diagram_has_optimization_features(self, tools):
        """测试generate_diagram工具包含优化功能"""
        tool_list = tools.get_tools()
        generate_tool = next(
            tool for tool in tool_list if tool["name"] == "generate_diagram"
        )

        # 验证包含布局优化功能
        properties = generate_tool["inputSchema"]["properties"]
        assert "optimize_layout" in properties
        assert properties["optimize_layout"]["type"] == "boolean"
        assert properties["optimize_layout"]["default"] is True

    def test_generate_diagram_has_theme_features(self, tools):
        """测试generate_diagram工具包含主题功能"""
        tool_list = tools.get_tools()
        generate_tool = next(
            tool for tool in tool_list if tool["name"] == "generate_diagram"
        )

        # 验证包含主题选择功能
        properties = generate_tool["inputSchema"]["properties"]
        assert "theme" in properties
        assert properties["theme"]["type"] == "string"
        assert "enum" in properties["theme"]
        assert properties["theme"]["default"] == "default"

    def test_call_generate_diagram_success(self, tools, sample_content):
        """测试成功调用generate_diagram"""
        mock_result = {
            "success": True,
            "theme": "default",
            "layout_optimization": "保持默认布局",
            "optimized_content": sample_content,
            "image_path": "/tmp/test.png",
        }

        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.return_value = mock_result

            result = tools.call_tool(
                "generate_diagram", {
                    "content": sample_content, "theme": "default"})

            assert result["success"] is True
            assert result["message"] == "图表生成成功"
            assert "data" in result
            assert result["data"]["theme"] == "default"
            assert result["data"]["image_path"] == "/tmp/test.png"

            mock_generate.assert_called_once_with(
                content=sample_content,
                theme="default",
                optimize_layout=True,  # 默认值
                quality="high",  # 默认值
                upload_image=True,  # 默认值已改为True
                title="",  # 默认值
            )

    def test_call_generate_diagram_with_upload(self, tools, sample_content):
        """测试带上传的generate_diagram调用"""
        mock_result = {
            "success": True,
            "theme": "professional",
            "layout_optimization": "优化为横向布局",
            "optimized_content": sample_content,
            "image_path": "/tmp/test.png",
            "image_url": "https://example.com/image.png",
            "markdown_link": "![测试](https://example.com/image.png)",
        }

        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.return_value = mock_result

            result = tools.call_tool(
                "generate_diagram",
                {
                    "content": sample_content,
                    "theme": "professional",
                    "upload_image": True,
                    "title": "测试图表",
                },
            )

            assert result["success"] is True
            assert result["data"]["image_url"] == "https://example.com/image.png"
            assert (
                result["data"]["markdown_link"]
                == "![测试](https://example.com/image.png)"
            )

    def test_call_generate_diagram_failure(self, tools, sample_content):
        """测试generate_diagram调用失败"""
        mock_result = {"success": False, "error": "图片生成失败"}

        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.return_value = mock_result

            result = tools.call_tool(
                "generate_diagram", {
                    "content": sample_content})

            assert result["success"] is False
            assert result["error"] == "图片生成失败"
            assert "details" in result

    def test_generate_diagram_includes_optimization_info(
            self, tools, sample_content):
        """测试generate_diagram包含优化信息"""
        mock_result = {
            "success": True,
            "theme": "default",
            "layout_optimization": "优化为横向布局",
            "optimized_content": sample_content.replace("TD", "LR"),
            "image_path": "/tmp/test.png",
        }

        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.return_value = mock_result

            result = tools.call_tool(
                "generate_diagram", {
                    "content": sample_content, "optimize_layout": True})

            assert result["success"] is True
            assert "optimization_details" in result["data"]
            assert result["data"]["layout_optimization"] == "优化为横向布局"

    def test_generate_diagram_includes_theme_info(self, tools, sample_content):
        """测试generate_diagram包含主题信息"""
        mock_result = {
            "success": True,
            "theme": "professional",
            "layout_optimization": "保持默认布局",
            "optimized_content": sample_content,
            "image_path": "/tmp/test.png",
        }

        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.return_value = mock_result

            result = tools.call_tool(
                "generate_diagram", {
                    "content": sample_content, "theme": "professional"})

            assert result["success"] is True
            assert "available_themes" in result["data"]
            assert result["data"]["theme"] == "professional"

    def test_call_unknown_tool(self, tools):
        """测试调用未知工具"""
        result = tools.call_tool("unknown_tool", {})

        assert result["success"] is False
        assert "未知工具" in result["error"]
        assert "unknown_tool" in result["error"]

    def test_call_generate_diagram_exception(self, tools, sample_content):
        """测试generate_diagram调用异常"""
        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.side_effect = Exception("生成异常")

            result = tools.call_tool(
                "generate_diagram", {
                    "content": sample_content})

            assert result["success"] is False
            assert "生成过程异常" in result["error"]
            assert "生成异常" in result["error"]

    def test_get_stats(self, tools):
        """测试获取统计信息"""
        with (
            patch.object(tools.generator, "get_optimizer_stats") as mock_stats,
            patch(
                "mcp_mermaid.themes.configs.ThemeManager.get_available_themes"
            ) as mock_themes,
        ):

            mock_stats.return_value = {"optimizations": 5}
            mock_themes.return_value = ["default", "professional"]

            stats = tools.get_stats()

            assert "optimizer_stats" in stats
            assert "available_themes" in stats
            assert "tools_count" in stats
            assert stats["tools_count"] == 1

    def test_cleanup(self, tools):
        """测试资源清理"""
        with patch.object(tools.generator, "cleanup") as mock_cleanup:
            tools.cleanup()
            mock_cleanup.assert_called_once()

    def test_generate_diagram_all_parameters(self, tools, sample_content):
        """测试generate_diagram所有参数"""
        mock_result = {
            "success": True,
            "theme": "minimal",
            "layout_optimization": "测试优化",
            "optimized_content": sample_content,
            "image_path": "/tmp/test.png",
        }

        with patch.object(tools.generator, "generate_diagram") as mock_generate:
            mock_generate.return_value = mock_result

            result = tools.call_tool(
                "generate_diagram",
                {
                    "content": sample_content,
                    "theme": "minimal",
                    "optimize_layout": False,
                    "quality": "low",
                    "upload_image": True,
                    "title": "完整测试",
                },
            )

            assert result["success"] is True

            mock_generate.assert_called_once_with(
                content=sample_content,
                theme="minimal",
                optimize_layout=False,
                quality="low",
                upload_image=True,
                title="完整测试",
            )
