"""
Mermaid生成器主模块

整合智能布局优化、主题应用和高质量图片生成功能
"""

import json
import os
import subprocess
import tempfile
from typing import Any, Dict, Optional

from ..themes.configs import ThemeManager
from .logger import logger
from .optimizer import LayoutOptimizer
from .uploader import ImageUploader
from .font_checker import FontChecker


class MermaidGenerator:
    """智能Mermaid图表生成器"""

    def __init__(self, puppeteer_config_path: str = "puppeteer-config.json"):
        self.optimizer = LayoutOptimizer()
        self.uploader = ImageUploader()
        self.puppeteer_config_path = puppeteer_config_path
        self.temp_dir = tempfile.mkdtemp()
        
        # 首次运行时检测系统字体
        self._check_system_fonts()

    def generate_diagram(
        self,
        content: str,
        theme: str = "default",
        optimize_layout: bool = True,
        quality: str = "high",
        upload_image: bool = True,
        title: str = "",
    ) -> Dict[str, Any]:
        """
        生成Mermaid图表

        Args:
            content: Mermaid图表内容
            theme: 主题名称
            optimize_layout: 是否启用布局优化
            quality: 输出质量 (low/medium/high)
            upload_image: 是否上传图片
            title: 图表标题

        Returns:
            Dict[str, Any]: 生成结果
        """
        result = {
            "success": False,
            "mermaid_content": content,
            "optimized_content": content,
            "theme": theme,
            "layout_optimization": "",
            "image_path": "",
            "image_url": "",
            "markdown_link": "",
            "error": "",
        }

        try:
            # 1. 布局优化
            if optimize_layout:
                optimized_content, optimization_reason = self.optimizer.optimize_layout(
                    content)
                result["optimized_content"] = optimized_content
                result["layout_optimization"] = optimization_reason
                logger.info("🎯 布局优化完成: %s", optimization_reason)
            else:
                optimized_content = content
                result["layout_optimization"] = "未启用布局优化"

            # 2. 应用主题
            if not ThemeManager.is_valid_theme(theme):
                theme = "default"
                logger.warning("⚠️ 主题无效，使用默认主题")

            theme_config = ThemeManager.get_theme_config(theme)
            theme_desc = ThemeManager.get_theme_description(theme)
            logger.info("🎨 应用主题: %s - %s", theme, theme_desc)

            # 3. 生成图片
            image_path = self._generate_image(
                optimized_content, theme_config, quality, title
            )
            if not image_path:
                result["error"] = "图片生成失败"
                return result

            result["image_path"] = image_path
            logger.info("🖼️ 图片生成成功: %s", image_path)

            # 4. 上传图片（可选）
            if upload_image:
                image_url = self.uploader.upload_image(image_path, title)
                if image_url:
                    result["image_url"] = image_url
                    # 上传成功时，image_path设置为云端URL
                    result["image_path"] = image_url
                    result["markdown_link"] = self.uploader.generate_markdown_link(
                        image_url, title)
                    logger.info("☁️ 图片上传成功: %s", image_url)
                else:
                    logger.warning("⚠️ 图片上传失败，但本地图片生成成功")

            result["success"] = True
            return result

        except Exception as e:
            result["error"] = str(e)
            logger.error("❌ 生成过程出错: %s", e)
            return result

    def _generate_image(
        self,
        mermaid_content: str,
        theme_config: Dict[str, Any],
        quality: str,
        title: str,
    ) -> Optional[str]:
        """生成图片文件"""
        try:
            # 创建临时HTML文件
            html_file = self._create_html_file(mermaid_content, theme_config)

            # 生成输出文件路径
            safe_title = "".join(
                c for c in title if c.isalnum() or c in (" ", "-", "_")
            ).strip()
            if not safe_title:
                safe_title = "mermaid_diagram"

            output_path = os.path.join(self.temp_dir, f"{safe_title}.png")

            # 根据质量设置参数
            quality_settings = self._get_quality_settings(quality)

            # 使用自定义Puppeteer脚本生成图片
            # 从包内资源定位JS文件
            try:
                from importlib import resources
                # Python 3.9+
                js_dir = resources.files('mcp_mermaid').joinpath('js')
                puppeteer_script = str(js_dir.joinpath('puppeteer-screenshot.js'))
            except (ImportError, AttributeError):
                # Python 3.8 fallback
                import pkg_resources
                puppeteer_script = pkg_resources.resource_filename(
                    'mcp_mermaid', 'js/puppeteer-screenshot.js'
                )

            cmd = [
                "node",
                puppeteer_script,
                html_file,
                output_path,
                "--width",
                str(quality_settings["width"]),
                "--height",
                str(quality_settings["height"]),
                "--device-scale-factor",
                str(quality_settings["scale"]),
            ]

            logger.info("🔧 生成命令: %s", " ".join(cmd))

            # 执行命令
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                logger.error("❌ Puppeteer执行失败:")
                logger.error("stdout: %s", result.stdout)
                logger.error("stderr: %s", result.stderr)
                return None

        except subprocess.TimeoutExpired:
            logger.error("❌ 图片生成超时")
            return None
        except Exception as e:
            logger.error("❌ 图片生成异常: %s", e)
            return None

    def _create_html_file(
        self, mermaid_content: str, theme_config: Dict[str, Any]
    ) -> str:
        """创建用于生成图片的HTML文件"""
        bg_color = theme_config.get(
            "themeVariables", {}).get(
            "background", "#FFFFFF")

        # 使用本地下载的Mermaid.js文件
        try:
            from importlib import resources
            # Python 3.9+
            js_dir = resources.files('mcp_mermaid').joinpath('js')
            mermaid_js_path = str(js_dir.joinpath('mermaid.min.js'))
        except (ImportError, AttributeError):
            # Python 3.8 fallback
            import pkg_resources
            mermaid_js_path = pkg_resources.resource_filename(
                'mcp_mermaid', 'js/mermaid.min.js'
            )
        mermaid_js_url = f"file://{os.path.abspath(mermaid_js_path)}"

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram</title>
    <script src="{mermaid_js_url}"></script>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background-color: {bg_color};
            font-family: system-ui, -apple-system, BlinkMacSystemFont,
                "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans",
                "Noto Color Emoji", sans-serif;
            font-variant-emoji: emoji;
            font-synthesis: none;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
            font-family: inherit;
        }}
        .mermaid svg {{
            font-family: inherit;
        }}
        .mermaid .nodeLabel {{
            font-family: inherit;
            font-variant-emoji: emoji;
        }}
        .mermaid text {{
            font-family: inherit;
            font-variant-emoji: emoji;
        }}
    </style>
</head>
<body>
    <div class="mermaid">
{mermaid_content}
    </div>
    <script>
        // 增强的Mermaid初始化，确保正确渲染
        window.addEventListener('load', function() {{
            mermaid.initialize({{
                startOnLoad: true,
                {json.dumps(theme_config)[1:-1]},
                fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, ' +
                    '"Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", ' +
                    '"Noto Color Emoji", sans-serif',
                fontSize: 14,
                wrap: true,
                useMaxWidth: true
            }});

            // 添加渲染完成检测
            const observer = new MutationObserver(function(mutations) {{
                mutations.forEach(function(mutation) {{
                    if (mutation.type === 'childList') {{
                        const svgElement = document.querySelector('.mermaid svg');
                        if (svgElement) {{
                            console.log('Mermaid SVG渲染完成');
                            // 设置一个全局标记，供Puppeteer检测
                            window.mermaidReady = true;
                        }}
                    }}
                }});
            }});

            const mermaidContainer = document.querySelector('.mermaid');
            if (mermaidContainer) {{
                observer.observe(mermaidContainer, {{
                    childList: true, subtree: true }});
            }}
        }});
    </script>
</body>
</html>
"""

        # 创建临时HTML文件
        html_file = os.path.join(self.temp_dir, "diagram.html")
        with open(html_file, "w", encoding="utf-8", errors="replace") as f:
            f.write(html_template)

        return html_file

    def _get_quality_settings(self, quality: str) -> Dict[str, int]:
        """获取质量设置参数"""
        settings = {
            "low": {"width": 800, "height": 600, "scale": 1},
            "medium": {"width": 1200, "height": 900, "scale": 2},
            "high": {"width": 1600, "height": 1200, "scale": 3},
        }
        return settings.get(quality, settings["high"])

    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题信息"""
        return ThemeManager.get_theme_info()

    def get_optimizer_stats(self) -> Dict[str, int]:
        """获取布局优化器统计信息"""
        return self.optimizer.get_layout_stats()

    def cleanup(self) -> None:
        """清理临时文件"""
        try:
            import shutil

            if hasattr(self, "temp_dir") and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 清理临时目录: %s", self.temp_dir)
        except Exception as e:
            logger.warning("⚠️ 清理临时文件失败: %s", e)

    def _check_system_fonts(self) -> None:
        """检测系统字体（仅在首次运行时）"""
        # 使用环境变量避免重复检测
        if os.environ.get("MCP_MERMAID_FONT_CHECKED") != "1":
            FontChecker.check_and_warn()
            # 设置环境变量，避免同一进程内重复检测
            os.environ["MCP_MERMAID_FONT_CHECKED"] = "1"

    def __del__(self) -> None:
        """析构函数，自动清理"""
        self.cleanup()
