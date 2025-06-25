"""
图片上传模块

负责将生成的图片上传到ImageBB并返回URL
"""

import base64
from pathlib import Path
from typing import Any, Dict, Optional

import requests

from .logger import logger


class ImageUploader:
    """ImageBB图片上传器"""

    def __init__(self, api_key: str = "06fe30dccc3e9ecb4113cc05714f1fb3"):
        self.api_key = api_key
        self.upload_url = "https://api.imgbb.com/1/upload"

    def upload_image(self, image_path: str, title: str = "") -> Optional[str]:
        """
        上传图片到ImageBB

        Args:
            image_path: 图片文件路径
            title: 图片标题

        Returns:
            str: 图片URL，失败返回None
        """
        try:
            # 检查文件是否存在
            if not Path(image_path).exists():
                logger.error("图片文件不存在: %s", image_path)
                return None

            # 读取并编码图片
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(
                    image_file.read()).decode("utf-8")

            # 准备上传参数
            upload_data = {
                "key": self.api_key,
                "image": image_data,
                "name": title or "mermaid_diagram",
            }

            logger.info("上传图片到ImageBB: %s", title)

            # 发送上传请求
            logger.info("正在上传到ImageBB...")
            response = requests.post(
                self.upload_url, data=upload_data, timeout=30)

            if response.status_code == 200:
                result: Dict[str, Any] = response.json()
                if result.get("success"):
                    image_url: str = result["data"]["url"]
                    logger.info("✅ 上传成功: %s", image_url)
                    return image_url
                else:
                    error_msg = result.get("error", {}).get("message", "未知错误")
                    logger.error("❌ 上传失败: %s", error_msg)
                    return None
            else:
                logger.error(
                    "❌ 上传请求失败: HTTP %d - %s",
                    response.status_code,
                    response.text[:200],
                )
                return None

        except requests.RequestException as e:
            logger.error("网络请求异常: %s", e)
            return None
        except Exception as e:
            logger.error("上传过程异常: %s", e)
            return None

    def generate_markdown_link(self, image_url: str, title: str = "") -> str:
        """
        生成Markdown图片链接

        Args:
            image_url: 图片URL
            title: 图片标题

        Returns:
            str: Markdown格式的图片链接
        """
        alt_text = title or "Mermaid Diagram"
        return f"![{alt_text}]({image_url})"

    def upload_and_get_markdown(
        self, image_path: str, title: str = ""
    ) -> Optional[str]:
        """
        上传图片并返回Markdown链接

        Args:
            image_path: 图片文件路径
            title: 图片标题

        Returns:
            str: Markdown格式的图片链接，失败返回None
        """
        image_url = self.upload_image(image_path, title)
        if image_url:
            return self.generate_markdown_link(image_url, title)
        return None

    def validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        try:
            # 创建一个小的测试图片
            test_data = base64.b64encode(b"test").decode("utf-8")
            test_payload = {"key": self.api_key, "image": test_data}

            response = requests.post(
                self.upload_url, data=test_payload, timeout=10)
            result = response.json()

            # 即使上传失败，只要不是API密钥错误就说明密钥有效
            if result.get("error", {}).get("code") == 130:  # Invalid API key
                return False
            return True

        except Exception:
            return False
