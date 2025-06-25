"""
真实环境测试

测试在实际环境中的图片生成、文件操作、命令行工具等功能
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_mermaid.core.generator import MermaidGenerator
from mcp_mermaid.core.uploader import ImageUploader
from mcp_mermaid.server import MCPMermaidServer


class TestRealImageGeneration:
    """真实图片生成测试"""

    @pytest.fixture
    def sample_diagrams(self):
        """提供多种类型的测试图表"""
        return {
            "simple_flowchart": """graph TD
    A[开始] --> B[处理]
    B --> C[结束]""",
            "complex_flowchart": """graph TD
    A[用户登录] --> B{验证凭据}
    B -->|成功| C[显示仪表板]
    B -->|失败| D[显示错误消息]
    D --> A
    C --> E[用户操作]
    E --> F{保存更改?}
    F -->|是| G[保存到数据库]
    F -->|否| H[丢弃更改]
    G --> I[显示成功消息]
    H --> E
    I --> E""",
            "sequence_diagram": """sequenceDiagram
    participant U as 用户
    participant C as 客户端
    participant S as 服务器
    participant D as 数据库

    U->>C: 发起请求
    C->>S: 转发请求
    S->>D: 查询数据
    D-->>S: 返回结果
    S-->>C: 处理结果
    C-->>U: 显示数据""",
            "class_diagram": """classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }

    class Admin {
        +manage_users()
        +view_logs()
    }

    User <|-- Admin : 继承""",
        }

    def test_html_file_generation(self, sample_diagrams):
        """测试HTML文件生成"""
        generator = MermaidGenerator()

        for diagram_type, content in sample_diagrams.items():
            with tempfile.TemporaryDirectory():
                # 使用默认主题测试
                from mcp_mermaid.themes.configs import ThemeManager

                theme_config = ThemeManager.get_theme_config("default")

                html_file = generator._create_html_file(content, theme_config)

                # 验证文件存在
                assert os.path.exists(html_file)
                assert html_file.endswith(".html")

                # 验证文件内容
                with open(html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # 检查必要的HTML结构
                assert "<!DOCTYPE html>" in html_content
                assert '<html lang="en">' in html_content
                assert "mermaid" in html_content.lower()
                assert content in html_content

                # 检查主题样式
                assert "background-color" in html_content

                print(f"✅ {diagram_type} HTML生成成功: {len(html_content)} 字节")

    def test_theme_variations(self):
        """测试不同主题的应用"""
        generator = MermaidGenerator()
        content = """graph TD
    A[测试] --> B[主题]
    B --> C[变化]"""

        from mcp_mermaid.themes.configs import ThemeManager

        available_themes = ThemeManager.get_available_themes()

        for theme_name in available_themes:
            with tempfile.TemporaryDirectory():
                theme_config = ThemeManager.get_theme_config(theme_name)
                html_file = generator._create_html_file(content, theme_config)

                # 验证主题特定的样式被应用
                with open(html_file, "r", encoding="utf-8") as f:
                    html_content = f.read()

                # 每个主题都应该有不同的背景色
                assert "background-color" in html_content
                print(f"✅ 主题 '{theme_name}' 应用成功")

    def test_file_cleanup_after_generation(self):
        """测试生成后的文件清理"""
        generator = MermaidGenerator()
        initial_temp_files = len(list(Path(generator.temp_dir).glob("*")))

        # 模拟图片生成过程
        content = "graph TD\nA-->B"
        with patch.object(generator, "_generate_image") as mock_generate:
            mock_generate.return_value = None  # 模拟生成失败

            generator.generate_diagram(content=content, upload_image=False)

            # 即使生成失败，也不应该留下临时文件
            final_temp_files = len(list(Path(generator.temp_dir).glob("*")))

            # 临时文件数量不应该显著增加
            assert final_temp_files <= initial_temp_files + 1

    def test_quality_settings_impact(self):
        """测试质量设置对生成的影响"""
        generator = MermaidGenerator()

        qualities = ["low", "medium", "high"]
        for quality in qualities:
            settings = generator._get_quality_settings(quality)

            # 验证质量设置参数
            assert "width" in settings
            assert "height" in settings
            assert "scale" in settings

            # 验证质量递增
            if quality == "low":
                assert settings["scale"] == 1
            elif quality == "high":
                assert settings["scale"] >= 2

            print(f"✅ 质量设置 '{quality}': {settings}")


class TestRealFileOperations:
    """真实文件操作测试"""

    def test_temp_directory_management(self):
        """测试临时目录管理"""
        generator = MermaidGenerator()

        # 验证临时目录存在
        assert os.path.exists(generator.temp_dir)
        assert os.path.isdir(generator.temp_dir)

        # 验证可以创建文件
        test_file = os.path.join(generator.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        assert os.path.exists(test_file)

        # 清理测试
        os.remove(test_file)

    def test_file_permissions_and_access(self):
        """测试文件权限和访问"""
        generator = MermaidGenerator()

        # 创建测试文件
        test_file = os.path.join(generator.temp_dir, "permission_test.html")
        with open(test_file, "w") as f:
            f.write("<html>Test</html>")

        # 验证文件可读
        assert os.access(test_file, os.R_OK)

        # 验证文件内容
        with open(test_file, "r") as f:
            content = f.read()
        assert "Test" in content

        # 清理
        os.remove(test_file)

    def test_large_diagram_handling(self):
        """测试大型图表处理"""
        generator = MermaidGenerator()

        # 创建一个较大的图表
        large_diagram = """graph TD
    Start --> Node1
"""

        # 添加100个节点来创建复杂图表
        for i in range(2, 50):
            large_diagram += f"    Node{i - 1} --> Node{i}\n"

        large_diagram += "    Node49 --> End"

        # 测试处理大型图表时的HTML生成
        from mcp_mermaid.themes.configs import ThemeManager

        theme_config = ThemeManager.get_theme_config("default")

        html_file = generator._create_html_file(large_diagram, theme_config)

        # 验证文件大小合理
        file_size = os.path.getsize(html_file)
        assert file_size > 1000  # 应该至少有1KB
        assert file_size < 1024 * 1024  # 但不应该超过1MB

        print(f"✅ 大型图表HTML文件大小: {file_size} 字节")


class TestCommandLineIntegration:
    """命令行集成测试"""

    def test_entry_point_function_exists(self):
        """测试入口点函数存在"""
        from mcp_mermaid.server import main_sync

        # 验证函数存在且可调用
        assert callable(main_sync)

        # 验证函数不是协程
        import inspect

        assert not inspect.iscoroutinefunction(main_sync)

    def test_package_installation_simulation(self):
        """测试包安装模拟"""
        # 验证导入路径正确
        try:
            import mcp_mermaid.server

            assert hasattr(mcp_mermaid.server, "main_sync")
            assert hasattr(mcp_mermaid.server, "MCPMermaidServer")
            print("✅ 包导入结构正确")
        except ImportError as e:
            pytest.fail(f"包导入失败: {e}")

    def test_server_can_be_instantiated(self):
        """测试服务器可以被实例化"""
        server = MCPMermaidServer()
        assert server is not None
        assert hasattr(server, "tools")

        # 测试清理
        server.tools.cleanup()

    @pytest.mark.skipif(shutil.which("python") is None, reason="python命令不可用")
    def test_python_module_execution(self):
        """测试Python模块执行"""
        # 测试模块可以作为脚本运行
        test_script = """
import sys
import asyncio
from mcp_mermaid.server import MCPMermaidServer

async def quick_test():
    server = MCPMermaidServer()
    request = {
        "jsonrpc": "2.0",
        "id": "test",
        "method": "tools/list",
        "params": {}
    }
    response = await server.handle_request(request)
    print("SUCCESS" if response.get("jsonrpc") == "2.0" else "FAILED")

asyncio.run(quick_test())
"""

        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0
        assert "SUCCESS" in result.stdout


class TestUploadIntegration:
    """上传集成测试"""

    def test_uploader_initialization(self):
        """测试上传器初始化"""
        uploader = ImageUploader()
        assert uploader is not None

        # 验证API密钥存在（应该从环境变量或配置中读取）
        # 这里不验证具体值，只验证结构
        assert hasattr(uploader, "api_key")

    def test_image_file_validation(self):
        """测试图片文件验证"""
        ImageUploader()  # 仅验证可以创建实例

        # 创建一个小的测试PNG文件
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            # 写入最小的PNG文件头
            png_data = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                b"\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a"
                b"\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01"
                b"\x00\x01\x02\xb5\x9c\xf2\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            f.write(png_data)
            temp_path = f.name

        try:
            # 验证文件存在且可读
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0

            # 验证是PNG文件（通过文件头）
            with open(temp_path, "rb") as f:
                header = f.read(8)
            assert header.startswith(b"\x89PNG")

            print(f"✅ 测试PNG文件创建成功: {os.path.getsize(temp_path)} 字节")

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_markdown_link_generation(self):
        """测试Markdown链接生成"""
        uploader = ImageUploader()

        # 测试生成Markdown链接
        test_url = "https://example.com/image.png"
        test_title = "测试图片"

        markdown_link = uploader.generate_markdown_link(test_url, test_title)

        expected = f"![{test_title}]({test_url})"
        assert markdown_link == expected


class TestErrorHandlingAndRecovery:
    """错误处理和恢复测试"""

    def test_invalid_mermaid_syntax_handling(self):
        """测试无效Mermaid语法处理"""
        generator = MermaidGenerator()

        invalid_contents = [
            "invalid syntax here",
            "graph TD\n    A[unclosed",
            "sequenceDiagram\n    missing participant",
            "",  # 空内容
            "   ",  # 仅空白字符
        ]

        for invalid_content in invalid_contents:
            # 即使内容无效，也应该能处理不崩溃
            with patch.object(generator, "_generate_image") as mock_generate:
                mock_generate.return_value = None

                result = generator.generate_diagram(
                    content=invalid_content, upload_image=False
                )

                # 应该返回失败结果而不是抛出异常
                assert isinstance(result, dict)
                assert "success" in result

    def test_file_system_error_recovery(self):
        """测试文件系统错误恢复"""
        generator = MermaidGenerator()

        # 模拟文件系统错误 - mock tempfile.mkdtemp 而不是 NamedTemporaryFile
        with patch("tempfile.mkdtemp") as mock_temp:
            mock_temp.side_effect = OSError("文件系统错误")

            # 由于temp_dir已经在__init__中创建，我们需要重新创建generator
            with patch("mcp_mermaid.core.generator.tempfile.mkdtemp") as mock_mkdtemp:
                mock_mkdtemp.side_effect = OSError("文件系统错误")

                try:
                    # 这应该在初始化时就失败
                    MermaidGenerator()
                    assert False, "应该在初始化时抛出异常"
                except OSError:
                    # 这是预期的行为
                    pass

        # 测试在HTML文件创建时的错误处理
        with patch("builtins.open") as mock_open:
            mock_open.side_effect = OSError("无法创建HTML文件")

            result = generator.generate_diagram(
                content="graph TD\nA-->B", upload_image=False
            )

            # 应该能优雅地处理文件创建错误
            assert isinstance(result, dict)
            assert result.get("success") is False

    def test_memory_constraints_handling(self):
        """测试内存约束处理"""
        # 测试处理大量数据时的内存使用
        generator = MermaidGenerator()

        # 创建一个非常大的图表字符串
        large_content = "graph TD\n"
        for i in range(1000):
            large_content += f"    Node{i} --> Node{i + 1}\n"

        # 这应该不会导致内存溢出
        with patch.object(generator, "_generate_image") as mock_generate:
            mock_generate.return_value = None

            try:
                result = generator.generate_diagram(
                    content=large_content, upload_image=False
                )
                assert isinstance(result, dict)
                print(f"✅ 大型内容处理成功: {len(large_content)} 字符")
            except MemoryError:
                pytest.fail("处理大型内容时发生内存错误")
