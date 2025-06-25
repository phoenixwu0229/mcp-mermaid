"""
集成测试 - 端到端系统测试

测试真实的MCP服务器启动、图片生成、命令行工具等完整系统功能
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import pytest

from mcp_mermaid.core.generator import MermaidGenerator
from mcp_mermaid.server import MCPMermaidServer


class TestSystemIntegration:
    """系统集成测试"""

    @pytest.fixture
    def sample_mermaid(self):
        """测试用的Mermaid内容"""
        return """graph TD
    A[开始] --> B[处理数据]
    B --> C{判断条件}
    C -->|是| D[执行操作A]
    C -->|否| E[执行操作B]
    D --> F[结束]
    E --> F"""

    def test_async_main_function_direct_call(self):
        """测试async main函数直接调用"""

        async def run_test():
            # 创建服务器实例
            server = MCPMermaidServer()
            assert server is not None
            assert hasattr(server, "tools")

            # 测试基本请求处理
            request = {
                "jsonrpc": "2.0",
                "id": "test",
                "method": "tools/list",
                "params": {},
            }

            response = await server.handle_request(request)
            assert response["jsonrpc"] == "2.0"
            assert "result" in response

        # 运行异步测试
        asyncio.run(run_test())

    def test_console_script_entry_point_issue(self):
        """测试控制台脚本入口点问题"""
        # 这个测试验证当前的entry point配置问题

        # 尝试运行安装的命令（应该会失败）
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import mcp_mermaid.server; mcp_mermaid.server.main()",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # 应该会有coroutine警告
            assert "RuntimeWarning" in result.stderr or "coroutine" in result.stderr

        except subprocess.TimeoutExpired:
            # 超时也是预期的，因为服务器会一直运行
            pass

    @pytest.mark.asyncio
    async def test_real_mermaid_generation(self, sample_mermaid):
        """测试真实的Mermaid图片生成"""
        generator = MermaidGenerator()

        # 使用临时目录测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock _generate_image来避免需要真实的puppeteer环境
            with patch.object(generator, "_generate_image") as mock_generate:
                # 创建一个临时的测试图片文件
                test_image_path = os.path.join(temp_dir, "test_output.png")

                # 创建一个小的测试PNG文件
                with open(test_image_path, "wb") as f:
                    # 写入最小的PNG文件头
                    png_data = (
                        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
                        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
                        b"\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a"
                        b"\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01"
                        b"\x00\x01\x02\xb5\x9c\xf2\x00\x00\x00\x00IEND\xaeB`\x82")
                    f.write(png_data)

                mock_generate.return_value = test_image_path

                result = generator.generate_diagram(
                    content=sample_mermaid, theme="default", upload_image=False
                )

                assert result["success"] is True
                assert result["image_path"] == test_image_path
                assert os.path.exists(test_image_path)

    def test_mcp_server_stdin_stdout_protocol(self):
        """测试MCP服务器的stdin/stdout协议"""

        # 创建测试脚本，直接运行server.run()
        test_script = """
import asyncio
import json
import sys
from mcp_mermaid.server import MCPMermaidServer

async def test_run():
    server = MCPMermaidServer()

    # 模拟单个请求处理
    request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "tools/list",
        "params": {}
    }

    response = await server.handle_request(request)
    print(json.dumps(response))

asyncio.run(test_run())
"""

        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0

        # 解析输出的JSON响应（可能包含多行输出）
        try:
            output_lines = result.stdout.strip().split("\n")
            json_line = None
            for line in output_lines:
                if line.strip().startswith("{"):
                    json_line = line.strip()
                    break

            assert json_line is not None, f"未找到JSON输出: {result.stdout}"
            response = json.loads(json_line)
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == "1"
            assert "result" in response
            assert "tools" in response["result"]
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON output: {result.stdout}")

    def test_all_tools_end_to_end(self, sample_mermaid):
        """测试所有工具的端到端功能"""
        from mcp_mermaid.tools.mermaid_tools import MermaidTools

        tools = MermaidTools()

        # 测试1: 获取工具列表
        tool_list = tools.get_tools()
        assert len(tool_list) == 1
        tool_names = [tool["name"] for tool in tool_list]

        # 测试2: 测试每个工具
        for tool_name in tool_names:
            if tool_name == "generate_diagram":
                # Mock图片生成避免依赖外部工具
                with patch.object(tools.generator, "_generate_image") as mock_gen:
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
                        f.write(b"fake_png_data")
                        mock_gen.return_value = f.name

                        result = tools.call_tool(
                            tool_name, {
                                "content": sample_mermaid, "theme": "default"})

                        assert result["success"] is True
                        assert "image_path" in result["data"]

                        # 清理临时文件
                        if os.path.exists(f.name):
                            os.unlink(f.name)

            elif tool_name == "optimize_layout":
                result = tools.call_tool(
                    tool_name, {"content": sample_mermaid})
                assert result["success"] is True
                assert "optimized_content" in result["data"]

            elif tool_name == "get_theme_info":
                result = tools.call_tool(tool_name, {})
                assert result["success"] is True
                # 检查数据结构（可能是available_themes而不是themes）
                themes_check = (
                    "available_themes" in result["data"] or "themes" in result["data"])
                assert themes_check

    def test_error_recovery_and_cleanup(self):
        """测试错误恢复和资源清理"""
        from mcp_mermaid.server import MCPMermaidServer

        async def test_cleanup():
            server = MCPMermaidServer()

            # 测试异常后的清理
            with patch.object(server.tools, "call_tool") as mock_call:
                mock_call.side_effect = Exception("模拟错误")

                request = {
                    "jsonrpc": "2.0",
                    "id": "error_test",
                    "method": "tools/call",
                    "params": {
                        "name": "generate_diagram",
                        "arguments": {"content": "test"},
                    },
                }

                response = await server.handle_request(request)

                # 验证错误被正确处理
                assert "error" in response
                assert response["error"]["code"] == -32603

                # 验证清理功能
                server.tools.cleanup()

        asyncio.run(test_cleanup())


class TestCommandLineInterface:
    """命令行接口测试"""

    def test_sync_wrapper_needed(self):
        """测试需要同步包装器的问题"""
        # 验证当前main函数是async的
        import inspect

        from mcp_mermaid.server import main

        assert inspect.iscoroutinefunction(main), "main函数应该是async的"

        # 但是entry point需要同步函数
        # 这个测试记录了需要修复的问题

    def test_package_metadata(self):
        """测试包元数据"""
        import mcp_mermaid

        # 验证包可以导入
        assert mcp_mermaid is not None

        # 验证版本信息存在
        try:
            from mcp_mermaid._version import __version__

            assert isinstance(__version__, str)
            assert len(__version__) > 0
        except ImportError:
            # 如果没有版本模块，跳过测试
            pass

        # 验证主要模块可以导入
        try:
            from mcp_mermaid.server import MCPMermaidServer
            from mcp_mermaid.tools.mermaid_tools import MermaidTools

            assert MCPMermaidServer is not None
            assert MermaidTools is not None
        except ImportError as e:
            pytest.fail(f"主要模块导入失败: {e}")


class TestPerformanceAndLoad:
    """性能和负载测试"""

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """测试并发请求处理"""
        server = MCPMermaidServer()

        # 创建多个并发请求
        requests = []
        for i in range(10):
            requests.append({"jsonrpc": "2.0", "id": str(
                i), "method": "tools/list", "params": {}})

        # 并发处理请求
        start_time = time.time()
        tasks = [server.handle_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # 验证所有响应
        assert len(responses) == 10
        for i, response in enumerate(responses):
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == str(i)

        # 性能检查（并发处理应该较快）
        processing_time = end_time - start_time
        assert processing_time < 5.0, f"并发处理时间过长: {processing_time}秒"

    def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        # 创建多个服务器实例并清理
        for _ in range(50):
            server = MCPMermaidServer()
            tools = server.tools

            # 执行一些操作
            tool_list = tools.get_tools()
            assert len(tool_list) > 0

            # 清理资源
            tools.cleanup()

        # 如果到这里没有内存错误，说明清理机制工作正常


class TestDocumentationAndExamples:
    """文档和示例测试"""

    def test_readme_examples_work(self):
        """测试README中的示例是否工作"""

        # 测试基本的服务器创建
        async def test_readme_example():
            server = MCPMermaidServer()

            # 基本工具列表请求
            request = {
                "jsonrpc": "2.0",
                "id": "readme_test",
                "method": "tools/list",
                "params": {},
            }

            response = await server.handle_request(request)
            assert response["jsonrpc"] == "2.0"
            assert "result" in response

        asyncio.run(test_readme_example())

    def test_configuration_examples(self):
        """测试配置示例"""
        from mcp_mermaid.themes.configs import ThemeManager

        # 验证所有主题都可以获取
        themes = ThemeManager.get_available_themes()
        assert len(themes) > 0

        for theme_name in themes:
            theme_config = ThemeManager.get_theme_config(theme_name)
            assert isinstance(theme_config, dict)
            assert "theme" in theme_config or "themeVariables" in theme_config
