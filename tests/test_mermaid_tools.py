"""
测试MermaidTools MCP工具接口

包含工具列表获取、工具调用、参数验证、错误处理等功能测试
"""

import pytest
from unittest.mock import patch

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
        assert len(tool_list) == 3  # 应该有3个工具

        # 验证工具名称
        tool_names = [tool["name"] for tool in tool_list]
        assert "generate_diagram" in tool_names
        assert "optimize_layout" in tool_names
        assert "get_theme_info" in tool_names

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

    def test_optimize_layout_tool_schema(self, tools):
        """测试optimize_layout工具的schema"""
        tool_list = tools.get_tools()
        optimize_tool = next(
            tool for tool in tool_list if tool["name"] == "optimize_layout"
        )

        assert "description" in optimize_tool
        assert "inputSchema" in optimize_tool

        schema = optimize_tool["inputSchema"]
        assert schema["type"] == "object"
        assert "content" in schema["required"]
        assert "content" in schema["properties"]

    def test_get_theme_info_tool_schema(self, tools):
        """测试get_theme_info工具的schema"""
        tool_list = tools.get_tools()
        theme_tool = next(
            tool for tool in tool_list if tool["name"] == "get_theme_info"
        )

        assert "description" in theme_tool
        assert "inputSchema" in theme_tool

        schema = theme_tool["inputSchema"]
        assert schema["type"] == "object"
        assert schema["required"] == []  # 不需要参数

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
                "generate_diagram", {"content": sample_content, "theme": "default"}
            )

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
                upload_image=False,  # 默认值
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

            result = tools.call_tool("generate_diagram", {"content": sample_content})

            assert result["success"] is False
            assert result["error"] == "图片生成失败"
            assert "details" in result

    def test_call_optimize_layout_success(self, tools, sample_content):
        """测试成功调用optimize_layout"""
        optimized_content = sample_content.replace("TD", "LR")

        with patch.object(
            tools.generator.optimizer, "optimize_layout"
        ) as mock_optimize:
            mock_optimize.return_value = (optimized_content, "优化为横向布局")

            result = tools.call_tool("optimize_layout", {"content": sample_content})

            assert result["success"] is True
            assert result["message"] == "布局优化完成"
            assert result["data"]["original_content"] == sample_content
            assert result["data"]["optimized_content"] == optimized_content
            assert result["data"]["optimization_reason"] == "优化为横向布局"
            assert result["data"]["was_optimized"] is True

    def test_call_optimize_layout_no_change(self, tools, sample_content):
        """测试optimize_layout无变化"""
        with patch.object(
            tools.generator.optimizer, "optimize_layout"
        ) as mock_optimize:
            mock_optimize.return_value = (sample_content, "保持默认布局")

            result = tools.call_tool("optimize_layout", {"content": sample_content})

            assert result["success"] is True
            assert result["data"]["was_optimized"] is False

    def test_call_optimize_layout_exception(self, tools, sample_content):
        """测试optimize_layout异常处理"""
        with patch.object(
            tools.generator.optimizer, "optimize_layout"
        ) as mock_optimize:
            mock_optimize.side_effect = Exception("优化异常")

            result = tools.call_tool("optimize_layout", {"content": sample_content})

            assert result["success"] is False
            assert "优化异常" in result["error"]

    def test_call_get_theme_info_success(self, tools):
        """测试成功调用get_theme_info"""
        mock_themes = {"default": "默认主题", "professional": "专业主题"}

        with patch(
            "mcp_mermaid.themes.configs.ThemeManager.get_theme_info"
        ) as mock_get_themes:
            mock_get_themes.return_value = mock_themes

            result = tools.call_tool("get_theme_info", {})

            assert result["success"] is True
            assert result["message"] == "主题信息获取成功"
            assert result["data"]["available_themes"] == mock_themes
            assert result["data"]["total_count"] == 2
            assert result["data"]["default_theme"] == "default"

    def test_call_get_theme_info_exception(self, tools):
        """测试get_theme_info异常处理"""
        with patch(
            "mcp_mermaid.themes.configs.ThemeManager.get_theme_info"
        ) as mock_get_themes:
            mock_get_themes.side_effect = Exception("主题获取异常")

            result = tools.call_tool("get_theme_info", {})

            assert result["success"] is False
            assert "主题获取异常" in result["error"]

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

            result = tools.call_tool("generate_diagram", {"content": sample_content})

            assert result["success"] is False
            assert "生成过程异常" in result["error"]
            assert "生成异常" in result["error"]

    def test_get_stats(self, tools):
        """测试获取统计信息"""
        with patch.object(tools.generator, "get_optimizer_stats") as mock_stats, patch(
            "mcp_mermaid.themes.configs.ThemeManager.get_available_themes"
        ) as mock_themes:

            mock_stats.return_value = {"optimizations": 5}
            mock_themes.return_value = ["default", "professional"]

            stats = tools.get_stats()

            assert "optimizer_stats" in stats
            assert "available_themes" in stats
            assert "tools_count" in stats
            assert stats["tools_count"] == 3

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
 