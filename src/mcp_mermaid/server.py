"""
MCP Mermaid服务器主模块

实现JSON-RPC 2.0协议的MCP服务器
"""

import argparse
import asyncio
import json
import sys
from typing import Any, Dict, Optional

from ._version import __version__
from .core.logger import logger
from .tools.mermaid_tools import MermaidTools


class MCPMermaidServer:
    """MCP Mermaid服务器"""

    def __init__(self) -> None:
        self.tools = MermaidTools()
        # 服务器信息
        self.server_info: Dict[str, str] = {
            "name": "mcp-mermaid",
            "version": __version__,
            "description": "智能Mermaid图表生成工具，支持布局优化、主题系统和高质量输出",
            "author": "MCP-Mermaid Team",
            "homepage": "https://github.com/mcp-mermaid/mcp-mermaid",
        }

    async def handle_request(
            self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                # 初始化响应 - 按照MCP最新规范
                client_info = params.get("clientInfo", {})
                logger.info(
                    "📞 客户端连接: %s v%s",
                    client_info.get("name", "Unknown"),
                    client_info.get("version", "Unknown"),
                )

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": self.server_info,
                        "capabilities": {
                            "tools": {"listChanged": False},
                            "resources": {},
                            "prompts": {},
                            "logging": {},
                        },
                    },
                }

            elif method == "notifications/initialized":
                # 初始化完成通知
                logger.info("✅ MCP协议初始化完成")
                return None  # 通知消息不需要响应

            elif method == "tools/list":
                # 返回工具列表
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tools.get_tools()},
                }

            elif method == "tools/call":
                # 调用工具
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                logger.info("🔧 调用工具: %s", tool_name)

                result = self.tools.call_tool(tool_name, arguments)

                return {"jsonrpc": "2.0", "id": request_id, "result": {
                    "content": [{"type": "text", "text": str(result)}]}, }

            elif method == "ping":
                # 心跳检测
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}

            else:
                # 未知方法
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    },
                }

        except Exception as e:
            logger.error("❌ 请求处理错误: %s", e)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}",
                },
            }

    async def run(self) -> None:
        """运行MCP服务器"""
        logger.info("🚀 MCP-Mermaid服务器已启动，等待连接...")

        while True:
            try:
                # 从stdin读取请求
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                    # 解析JSON请求
                request = json.loads(line.strip())

                # 记录请求（仅调试模式）
                if request.get("method") not in ["ping"]:
                    logger.info("📨 收到请求: %s", request.get("method"))

                    # 处理请求
                    response = await self.handle_request(request)

                # 发送响应（如果有）
                if response is not None:
                    response_str = json.dumps(response) + "\n"
                    sys.stdout.write(response_str)
                    sys.stdout.flush()

            except KeyboardInterrupt:
                logger.info("🛑 收到中断信号，正在关闭服务器...")
                break
            except json.JSONDecodeError as e:
                logger.error("❌ JSON解析错误: %s", e)
                # 发送错误响应
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"},
                }
                response_str = json.dumps(error_response) + "\n"
                sys.stdout.write(response_str)
                sys.stdout.flush()
            except Exception as e:
                logger.error("❌ 服务器错误: %s", e)
                break

                # 清理资源
                logger.info("🧹 清理资源...")
                self.tools.cleanup()


async def main() -> None:
    """异步主函数"""
    server = MCPMermaidServer()
    await server.run()


def main_sync() -> None:
    """同步入口点，用于console script"""
    parser = argparse.ArgumentParser(
        prog="mcp-mermaid", description="MCP Mermaid图表生成服务器"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--help-tools", action="store_true", help="显示可用工具列表")

    # 如果没有参数，直接启动MCP服务器
    if len(sys.argv) == 1:
        # 没有参数时启动MCP服务器
        logger.info("🚀 启动MCP Mermaid服务器...")
        logger.info("💡 使用 --help 查看可用选项")
        asyncio.run(main())
        return

    # 有参数时解析参数
    args = parser.parse_args()

    if args.help_tools:
        tools = MermaidTools()
        logger.info("🛠️ 可用工具:")
        for tool in tools.get_tools():
            logger.info("  - %s: %s", tool["name"], tool["description"])
        tools.cleanup()
        return


if __name__ == "__main__":
    main_sync()
