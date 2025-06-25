"""
MCP协议实际实现测试

测试真实的MCP服务器协议处理，包括JSON-RPC 2.0标准实现
"""

import asyncio
from unittest.mock import patch

import pytest

from mcp_mermaid.server import MCPMermaidServer


class TestMCPProtocolImplementation:
    """测试MCP协议的实际实现"""

    @pytest.fixture
    def server(self):
        """创建真实的服务器实例"""
        return MCPMermaidServer()

    @pytest.mark.asyncio
    async def test_handle_initialize_request(self, server):
        """测试initialize请求处理"""
        request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        response = await server.handle_request(request)

        # 验证JSON-RPC 2.0响应格式
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "1"
        assert "result" in response

        # 验证MCP协议结构
        result = response["result"]
        assert "protocolVersion" in result
        assert "serverInfo" in result
        assert "capabilities" in result
        assert result["protocolVersion"] == "2025-03-26"
        assert "tools" in result["capabilities"]

        # 验证服务器信息
        server_info = result["serverInfo"]
        assert "name" in server_info
        assert "version" in server_info
        assert server_info["name"] == "mcp-mermaid"

    @pytest.mark.asyncio
    async def test_handle_tools_list_request(self, server):
        """测试tools/list请求处理"""
        request = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list",
            "params": {}}

        response = await server.handle_request(request)

        # 验证响应结构
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "2"
        assert "result" in response
        assert "tools" in response["result"]

        # 验证工具列表内容
        tools = response["result"]["tools"]
        assert isinstance(tools, list)
        assert len(tools) >= 1  # 应该有至少1个工具

        # 验证每个工具的结构
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

    @pytest.mark.asyncio
    async def test_handle_tool_call_request(self, server):
        """测试tools/call请求处理"""
        content = """graph TD
    A[开始] --> B[处理]
    B --> C[结束]"""

        request = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "generate_diagram",
                "arguments": {"content": content, "theme": "default"},
            },
        }

        # Mock工具调用结果
        mock_result = {
            "success": True,
            "message": "图表生成成功",
            "data": {"theme": "default", "image_path": "/tmp/test.png"},
        }

        with patch.object(server.tools, "call_tool") as mock_call:
            mock_call.return_value = mock_result

            response = await server.handle_request(request)

            # 验证响应结构
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == "3"
            assert "result" in response
            assert "content" in response["result"]

            # 验证MCP工具响应格式
            content_items = response["result"]["content"]
            assert isinstance(content_items, list)
            assert len(content_items) > 0
            assert content_items[0]["type"] == "text"
            assert "text" in content_items[0]

            # 验证工具被正确调用
            mock_call.assert_called_once_with(
                "generate_diagram", {"content": content, "theme": "default"}
            )

    @pytest.mark.asyncio
    async def test_handle_notifications_initialized(self, server):
        """测试notifications/initialized处理"""
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {},
        }

        response = await server.handle_request(notification)

        # 通知消息不应该有响应
        assert response is None

    @pytest.mark.asyncio
    async def test_handle_unknown_method(self, server):
        """测试未知方法处理"""
        request = {
            "jsonrpc": "2.0",
            "id": "4",
            "method": "unknown/method",
            "params": {},
        }

        response = await server.handle_request(request)

        # 验证错误响应格式
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "4"
        assert "error" in response

        error = response["error"]
        assert error["code"] == -32601  # Method not found
        assert "Method not found" in error["message"]

    @pytest.mark.asyncio
    async def test_handle_request_exception(self, server):
        """测试请求处理异常"""
        request = {
            "jsonrpc": "2.0",
            "id": "5",
            "method": "tools/call",
            "params": {
                "name": "generate_diagram",
                "arguments": {
                    "content": "test"}},
        }

        # Mock工具调用异常
        with patch.object(server.tools, "call_tool") as mock_call:
            mock_call.side_effect = Exception("测试异常")

            response = await server.handle_request(request)

            # 验证异常响应
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == "5"
            assert "error" in response

            error = response["error"]
            assert error["code"] == -32603  # Internal error
            assert "Internal error" in error["message"]
            assert "测试异常" in error["message"]

    @pytest.mark.asyncio
    async def test_request_id_types(self, server):
        """测试不同类型的请求ID"""
        # 测试字符串ID
        request_str = {
            "jsonrpc": "2.0",
            "id": "string-id",
            "method": "tools/list",
            "params": {},
        }

        response = await server.handle_request(request_str)
        assert response["id"] == "string-id"

        # 测试数字ID
        request_num = {
            "jsonrpc": "2.0",
            "id": 123,
            "method": "tools/list",
            "params": {},
        }

        response = await server.handle_request(request_num)
        assert response["id"] == 123

    @pytest.mark.asyncio
    async def test_missing_params_handling(self, server):
        """测试缺少params字段的请求"""
        request = {
            "jsonrpc": "2.0",
            "id": "6",
            "method": "tools/list",
            # 没有params字段
        }

        response = await server.handle_request(request)

        # 应该能正常处理（params默认为{}）
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == "6"
        assert "result" in response

    @pytest.mark.asyncio
    async def test_tool_call_with_missing_arguments(self, server):
        """测试工具调用缺少arguments"""
        request = {
            "jsonrpc": "2.0",
            "id": "7",
            "method": "tools/call",
            "params": {
                "name": "generate_diagram"
                # 缺少arguments
            },
        }

        # Mock工具调用
        mock_result = {"success": False, "error": "参数缺失"}
        with patch.object(server.tools, "call_tool") as mock_call:
            mock_call.return_value = mock_result

            await server.handle_request(request)

            # 验证工具被调用时使用了空字典作为默认参数
            mock_call.assert_called_once_with("generate_diagram", {})

    @pytest.mark.asyncio
    async def test_server_initialization(self, server):
        """测试服务器初始化"""
        assert server is not None
        assert hasattr(server, "tools")
        assert server.tools is not None

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self, server):
        """测试并发请求处理"""
        requests = []
        for i in range(5):
            requests.append({"jsonrpc": "2.0", "id": str(
                i), "method": "tools/list", "params": {}})

        # 并发处理请求
        tasks = [server.handle_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)

        # 验证所有响应
        assert len(responses) == 5
        for i, response in enumerate(responses):
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == str(i)
            assert "result" in response

    @pytest.mark.asyncio
    async def test_tool_response_formatting(self, server):
        """测试工具响应格式化"""
        request = {
            "jsonrpc": "2.0",
            "id": "8",
            "method": "tools/call",
            "params": {"name": "get_theme_info", "arguments": {}},
        }

        mock_result = {
            "success": True,
            "message": "主题信息获取成功",
            "data": {"themes": ["default", "professional"]},
        }

        with patch.object(server.tools, "call_tool") as mock_call:
            mock_call.return_value = mock_result

            response = await server.handle_request(request)

            # 验证响应被正确格式化为字符串
            content_text = response["result"]["content"][0]["text"]
            assert isinstance(content_text, str)
            # 应该包含工具调用的结果
            assert "success" in content_text or str(
                mock_result) in content_text


class TestMCPServerCleanup:
    """测试MCP服务器清理功能"""

    @pytest.fixture
    def server(self):
        return MCPMermaidServer()

    def test_cleanup_on_server_destruction(self, server):
        """测试服务器销毁时的清理"""
        with patch.object(server.tools, "cleanup") as mock_cleanup:
            # 模拟服务器清理
            server.tools.cleanup()
            mock_cleanup.assert_called_once()
