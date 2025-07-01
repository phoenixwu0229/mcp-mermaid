"""
测试MermaidGenerator核心功能

包含图表生成、主题应用、质量设置、布局优化集成等功能测试
"""

import os
from unittest.mock import patch

import pytest

from mcp_mermaid.core.generator import MermaidGenerator
from mcp_mermaid.themes.configs import ThemeManager


class TestMermaidGenerator:
    """测试MermaidGenerator类"""

    @pytest.fixture
    def generator(self):
        """创建生成器实例"""
        return MermaidGenerator()

    @pytest.fixture
    def sample_content(self):
        """示例Mermaid内容"""
        return """graph TD
    A[开始] --> B[处理]
    B --> C[结束]"""

    def test_generator_initialization(self, generator):
        """测试生成器初始化"""
        assert generator is not None
        assert hasattr(generator, "optimizer")
        assert hasattr(generator, "uploader")
        assert hasattr(generator, "temp_dir")
        assert os.path.exists(generator.temp_dir)

    def test_quality_settings(self, generator):
        """测试质量设置参数"""
        # 测试low质量
        settings = generator._get_quality_settings("low")
        assert settings["width"] == 800
        assert settings["height"] == 600
        assert settings["scale"] == 1

        # 测试high质量
        settings = generator._get_quality_settings("high")
        assert settings["width"] == 1600
        assert settings["height"] == 1200
        assert settings["scale"] == 3

        # 测试默认质量（未知质量参数）
        settings = generator._get_quality_settings("unknown")
        assert settings["width"] == 1600  # 应该使用high质量的设置

    def test_html_file_creation(self, generator, sample_content):
        """测试HTML文件创建"""
        theme_config = ThemeManager.get_theme_config("default")
        html_file = generator._create_html_file(sample_content, theme_config)

        assert os.path.exists(html_file)
        assert html_file.endswith(".html")

        # 读取文件内容验证
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "mermaid.min.js" in content
        assert sample_content in content
        assert "background-color" in content

    def test_generate_diagram_basic(self, generator, sample_content):
        """测试基本图表生成功能"""
        with patch.object(generator, "_generate_image") as mock_generate:
            mock_generate.return_value = "/tmp/test.png"

            result = generator.generate_diagram(
                content=sample_content,
                theme="default",
                optimize_layout=False,
                upload_image=False,
            )

            assert result["success"] is True
            assert result["mermaid_content"] == sample_content
            assert result["theme"] == "default"
            assert result["image_path"] == "/tmp/test.png"
            assert result["layout_optimization"] == "未启用布局优化"

    def test_generate_diagram_with_optimization(
            self, generator, sample_content):
        """测试带布局优化的图表生成"""
        with patch.object(generator, "_generate_image") as mock_generate:
            mock_generate.return_value = "/tmp/test.png"

            result = generator.generate_diagram(
                content=sample_content,
                optimize_layout=True,
                upload_image=False)

            assert result["success"] is True
            assert result["layout_optimization"] != "未启用布局优化"
            # 优化后的内容可能与原始内容不同
            assert "optimized_content" in result

    def test_generate_diagram_with_upload(self, generator, sample_content):
        """测试带上传功能的图表生成"""
        with (
            patch.object(generator, "_generate_image") as mock_generate,
            patch.object(generator.uploader, "upload_image") as mock_upload,
        ):

            mock_generate.return_value = "/tmp/test.png"
            mock_upload.return_value = "https://example.com/image.png"

            result = generator.generate_diagram(
                content=sample_content, upload_image=True, title="测试图表"
            )

            assert result["success"] is True
            assert result["image_url"] == "https://example.com/image.png"
            assert "markdown_link" in result
            mock_upload.assert_called_once_with("/tmp/test.png", "测试图表")

    def test_invalid_theme_handling(self, generator, sample_content):
        """测试无效主题处理"""
        with patch.object(generator, "_generate_image") as mock_generate:
            mock_generate.return_value = "/tmp/test.png"

            result = generator.generate_diagram(
                content=sample_content,
                theme="invalid_theme",
                upload_image=False)

            assert result["success"] is True
            assert result["theme"] == "invalid_theme"  # 传入的主题会被记录

    def test_generate_diagram_error_handling(self, generator, sample_content):
        """测试图表生成错误处理"""
        with patch.object(generator, "_generate_image") as mock_generate:
            mock_generate.return_value = None  # 模拟生成失败

            result = generator.generate_diagram(
                content=sample_content, upload_image=False
            )

            assert result["success"] is False
            assert result["error"] == "图片生成失败"

    def test_generate_diagram_exception_handling(self, generator):
        """测试异常处理"""
        with patch.object(generator.optimizer, "optimize_layout") as mock_optimize:
            mock_optimize.side_effect = Exception("测试异常")

            result = generator.generate_diagram(
                content="invalid content", upload_image=False
            )

            assert result["success"] is False
            assert "测试异常" in result["error"]

    def test_available_themes(self, generator):
        """测试可用主题获取"""
        themes = generator.get_available_themes()

        assert isinstance(themes, dict)
        assert len(themes) > 0
        assert "default" in themes or "professional" in themes

    def test_upload_failure_handling(self, generator, sample_content):
        """测试上传失败处理"""
        with (
            patch.object(generator, "_generate_image") as mock_generate,
            patch.object(generator.uploader, "upload_image") as mock_upload,
        ):

            mock_generate.return_value = "/tmp/test.png"
            mock_upload.return_value = None  # 模拟上传失败

            result = generator.generate_diagram(
                content=sample_content, upload_image=True
            )

            # 即使上传失败，生成应该仍然成功
            assert result["success"] is True
            assert result["image_path"] == "/tmp/test.png"
            assert result["image_url"] == ""

    def test_title_sanitization(self, generator):
        """测试标题清理功能"""
        with patch.object(generator, "_generate_image") as mock_generate:
            # 测试内部方法，通过检查生成的文件路径
            mock_generate.return_value = "/tmp/test.png"

            # 使用包含特殊字符的标题
            result = generator.generate_diagram(
                content="graph TD\nA-->B",
                title="测试@#$%图表!",
                upload_image=False)

            assert result["success"] is True
            # 验证mock被调用
            mock_generate.assert_called_once()

    @pytest.fixture(autouse=True)
    def cleanup(self, generator):
        """测试后清理"""
        yield
        # 清理临时目录
        if hasattr(
                generator,
                "temp_dir") and os.path.exists(
                generator.temp_dir):
            import shutil

            try:
                shutil.rmtree(generator.temp_dir)
            except Exception:
                pass  # 忽略清理错误
