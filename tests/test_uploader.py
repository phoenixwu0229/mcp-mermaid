"""
测试ImageUploader图片上传功能

包含图片上传、Markdown链接生成、错误处理等功能测试
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from mcp_mermaid.core.uploader import ImageUploader


class TestImageUploader:
    """测试ImageUploader类"""

    @pytest.fixture
    def uploader(self):
        """创建上传器实例"""
        return ImageUploader()

    @pytest.fixture
    def temp_image(self):
        """创建临时图片文件"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"fake_image_data")
            return f.name

    def test_uploader_initialization(self, uploader):
        """测试上传器初始化"""
        assert uploader is not None
        assert hasattr(uploader, "api_key")
        assert hasattr(uploader, "upload_url")
        assert uploader.upload_url == "https://api.imgbb.com/1/upload"

    def test_custom_api_key(self):
        """测试自定义API密钥"""
        custom_key = "custom_test_key"
        uploader = ImageUploader(api_key=custom_key)
        assert uploader.api_key == custom_key

    def test_generate_markdown_link(self, uploader):
        """测试Markdown链接生成"""
        image_url = "https://example.com/image.png"
        title = "测试图片"

        link = uploader.generate_markdown_link(image_url, title)
        assert link == "![测试图片](https://example.com/image.png)"

    def test_generate_markdown_link_no_title(self, uploader):
        """测试无标题Markdown链接生成"""
        image_url = "https://example.com/image.png"

        link = uploader.generate_markdown_link(image_url)
        assert link == "![Mermaid Diagram](https://example.com/image.png)"

    def test_upload_image_file_not_exists(self, uploader):
        """测试上传不存在的文件"""
        result = uploader.upload_image("/nonexistent/path.png")
        assert result is None

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_image_success(self, mock_post, uploader, temp_image):
        """测试成功上传图片"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"url": "https://example.com/uploaded.png"},
        }
        mock_post.return_value = mock_response

        result = uploader.upload_image(temp_image, "测试上传")

        assert result == "https://example.com/uploaded.png"
        mock_post.assert_called_once()

        # 验证请求参数
        call_args = mock_post.call_args
        assert call_args[0][0] == uploader.upload_url
        assert "data" in call_args[1]
        assert call_args[1]["data"]["key"] == uploader.api_key
        assert call_args[1]["data"]["name"] == "测试上传"

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_image_api_failure(self, mock_post, uploader, temp_image):
        """测试API返回失败"""
        # 模拟API失败响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": {"message": "API错误"},
        }
        mock_post.return_value = mock_response

        result = uploader.upload_image(temp_image)
        assert result is None

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_image_http_error(self, mock_post, uploader, temp_image):
        """测试HTTP错误"""
        # 模拟HTTP错误
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = uploader.upload_image(temp_image)
        assert result is None

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_image_network_error(self, mock_post, uploader, temp_image):
        """测试网络异常"""
        # 模拟网络异常
        mock_post.side_effect = Exception("网络连接失败")

        result = uploader.upload_image(temp_image)
        assert result is None

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_image_timeout(self, mock_post, uploader, temp_image):
        """测试请求超时"""
        import requests

        mock_post.side_effect = requests.RequestException("请求超时")

        result = uploader.upload_image(temp_image)
        assert result is None

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_image_default_title(self, mock_post, uploader, temp_image):
        """测试默认标题"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"url": "https://example.com/uploaded.png"},
        }
        mock_post.return_value = mock_response

        result = uploader.upload_image(temp_image)

        assert result == "https://example.com/uploaded.png"

        # 验证使用了默认名称
        call_args = mock_post.call_args
        assert call_args[1]["data"]["name"] == "mermaid_diagram"

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_and_get_markdown_success(
            self, mock_post, uploader, temp_image):
        """测试上传并获取Markdown链接成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"url": "https://example.com/uploaded.png"},
        }
        mock_post.return_value = mock_response

        result = uploader.upload_and_get_markdown(temp_image, "测试标题")

        assert result == "![测试标题](https://example.com/uploaded.png)"

    @patch("mcp_mermaid.core.uploader.requests.post")
    def test_upload_and_get_markdown_failure(
            self, mock_post, uploader, temp_image):
        """测试上传失败时获取Markdown链接"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = uploader.upload_and_get_markdown(temp_image, "测试标题")

        assert result is None

    def test_upload_image_binary_encoding(self, uploader, temp_image):
        """测试二进制文件编码"""
        # 创建包含特定内容的测试文件
        test_content = b"\x89PNG\r\n\x1a\n"  # PNG文件头
        with open(temp_image, "wb") as f:
            f.write(test_content)

        with patch("mcp_mermaid.core.uploader.requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {"url": "https://example.com/test.png"},
            }
            mock_post.return_value = mock_response

            result = uploader.upload_image(temp_image)

            assert result == "https://example.com/test.png"

            # 验证base64编码正确
            call_args = mock_post.call_args
            image_data = call_args[1]["data"]["image"]
            import base64

            decoded = base64.b64decode(image_data)
            assert decoded == test_content

    @pytest.fixture(autouse=True)
    def cleanup(self, temp_image):
        """测试后清理临时文件"""
        yield
        try:
            if os.path.exists(temp_image):
                os.unlink(temp_image)
        except Exception:
            pass
