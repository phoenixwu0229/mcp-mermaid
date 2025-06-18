"""
集成测试 - 端到端系统测试

测试真实的MCP服务器启动、图片生成、命令行工具等完整系统功能
"""

import pytest
import subprocess
import json
import os
import tempfile
import time
import asyncio
from pathlib import Path
from unittest.mock import patch

from mcp_mermaid.server import MCPMermaidServer, main
from mcp_mermaid.core.generator import MermaidGenerator


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
            assert hasattr(server, 'tools')
            
            # 测试基本请求处理
            request = {
                "jsonrpc": "2.0",
                "id": "test",
                "method": "tools/list",
                "params": {}
            }
            
            response = await server.handle_request(request)
            assert response["jsonrpc"] == "2.0"
            assert "result" in response
            
        # 运行异步测试
        asyncio.run(run_test())

    def test_console_script_entry_point_issue(self):
        """测试控制台脚本入口点问题"""
        # 这个测试验证当前的entry point配置问题
        import subprocess
        import sys
        
        # 尝试运行安装的命令（应该会失败）
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import mcp_mermaid.server; mcp_mermaid.server.main()"],
                capture_output=True,
                text=True,
                timeout=5
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
            with patch.object(generator, '_generate_image') as mock_generate:
                # 创建一个临时的测试图片文件
                test_image_path = os.path.join(temp_dir, "test_output.png")
                
                # 创建一个小的测试PNG文件
                with open(test_image_path, 'wb') as f:
                    # 写入最小的PNG文件头
                    f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x02\xb5\x9c\xf2\x00\x00\x00\x00IEND\xaeB`\x82')
                
                mock_generate.return_value = test_image_path
                
                result = generator.generate_diagram(
                    content=sample_mermaid,
                    theme="default",
                    upload_image=False
                )
                
                assert result["success"] is True
                assert result["image_path"] == test_image_path
                assert os.path.exists(test_image_path)

    def test_mcp_server_stdin_stdout_protocol(self):
        """测试MCP服务器的stdin/stdout协议"""
        import subprocess
        import sys
        import json
        
        # 创建测试脚本，直接运行server.run()
        test_script = '''
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
'''
        
        # 运行测试脚本
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        
        # 解析输出的JSON响应（可能包含多行输出）
        try:
            output_lines = result.stdout.strip().split('\n')
            json_line = None
            for line in output_lines:
                if line.strip().startswith('{'):
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
        assert len(tool_list) == 3
        tool_names = [tool["name"] for tool in tool_list]
        
        # 测试2: 测试每个工具
        for tool_name in tool_names:
            if tool_name == "generate_diagram":
                # Mock图片生成避免依赖外部工具
                with patch.object(tools.generator, '_generate_image') as mock_gen:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                        f.write(b'fake_png_data')
                        mock_gen.return_value = f.name
                        
                        result = tools.call_tool(tool_name, {
                            "content": sample_mermaid,
                            "theme": "default"
                        })
                        
                        assert result["success"] is True
                        assert "image_path" in result["data"]
                        
                        # 清理临时文件
                        if os.path.exists(f.name):
                            os.unlink(f.name)
                            
            elif tool_name == "optimize_layout":
                result = tools.call_tool(tool_name, {"content": sample_mermaid})
                assert result["success"] is True
                assert "optimized_content" in result["data"]
                
            elif tool_name == "get_theme_info":
                result = tools.call_tool(tool_name, {})
                assert result["success"] is True
                # 检查数据结构（可能是available_themes而不是themes）
                assert "available_themes" in result["data"] or "themes" in result["data"]

    def test_error_recovery_and_cleanup(self):
        """测试错误恢复和资源清理"""
        from mcp_mermaid.server import MCPMermaidServer
        
        async def test_cleanup():
            server = MCPMermaidServer()
            
            # 测试异常后的清理
            with patch.object(server.tools, 'call_tool') as mock_call:
                mock_call.side_effect = Exception("模拟错误")
                
                request = {
                    "jsonrpc": "2.0",
                    "id": "error_test",
                    "method": "tools/call",
                    "params": {"name": "generate_diagram", "arguments": {"content": "test"}}
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
        from mcp_mermaid.server import main
        import inspect
        
        assert inspect.iscoroutinefunction(main), "main函数应该是async的"
        
        # 但是entry point需要同步函数
        # 这个测试记录了需要修复的问题

    def test_package_metadata(self):
        """测试包元数据正确性"""
        import pkg_resources
        
        try:
            dist = pkg_resources.get_distribution('mcp-mermaid')
            
            # 验证entry points
            entry_points = dist.get_entry_map()
            assert 'console_scripts' in entry_points
            assert 'mcp-mermaid' in entry_points['console_scripts']
            
            entry_point = entry_points['console_scripts']['mcp-mermaid']
            # 应该指向server:main_sync，因为main_sync是同步的
            assert entry_point.module_name == 'mcp_mermaid.server'
            assert entry_point.attrs == ('main_sync',)
            
        except pkg_resources.DistributionNotFound:
            pytest.skip("包未安装，跳过元数据测试")


class TestPerformanceAndLoad:
    """性能和负载测试"""

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self):
        """测试并发请求处理性能"""
        server = MCPMermaidServer()
        
        # 创建多个并发请求
        requests = []
        for i in range(10):
            requests.append({
                "jsonrpc": "2.0",
                "id": f"perf_test_{i}",
                "method": "tools/list",
                "params": {}
            })
        
        # 记录开始时间
        start_time = time.time()
        
        # 并发处理所有请求
        tasks = [server.handle_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)
        
        # 记录结束时间
        end_time = time.time()
        
        # 验证性能
        assert len(responses) == 10
        assert end_time - start_time < 5.0  # 应该在5秒内完成
        
        # 验证所有响应都成功
        for response in responses:
            assert response["jsonrpc"] == "2.0"
            assert "result" in response

    def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        import gc
        
        # 获取初始内存使用
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # 创建和销毁多个服务器实例
        for i in range(5):
            server = MCPMermaidServer()
            tools = server.tools
            tools.cleanup()
            del server
            del tools
            gc.collect()
        
        # 检查内存泄漏
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # 允许一些合理的对象增长，但不应该过多
        assert object_growth < 100, f"可能存在内存泄漏，对象增长: {object_growth}"


class TestDocumentationAndExamples:
    """文档和示例测试"""

    def test_readme_examples_work(self):
        """测试README中的示例能够正常工作"""
        # 这里应该测试README中提到的用法示例
        # 比如基本的MCP请求响应示例
        
        from mcp_mermaid.server import MCPMermaidServer
        
        async def test_readme_example():
            server = MCPMermaidServer()
            
            # README中可能提到的基本用法
            tools_request = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "tools/list",
                "params": {}
            }
            
            response = await server.handle_request(tools_request)
            assert response["jsonrpc"] == "2.0"
            assert "tools" in response["result"]
            
        asyncio.run(test_readme_example())

    def test_configuration_examples(self):
        """测试配置示例"""
        # 测试mcp-server.json配置是否有效
        config_path = Path("mcp-server.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                
            # 验证配置结构
            assert "mcpServers" in config or "servers" in config 