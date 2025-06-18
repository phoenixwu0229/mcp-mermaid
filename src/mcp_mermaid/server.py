"""
MCP Mermaid服务器主模块

实现JSON-RPC 2.0协议的MCP服务器
"""

import asyncio
import sys
import argparse
import json
from typing import Any, Dict

from .tools.mermaid_tools import MermaidTools


class MCPMermaidServer:
    """MCP Mermaid服务器"""

    def __init__(self):
        self.tools = MermaidTools()
        # 服务器信息
        self.server_info = {
            "name": "mcp-mermaid",
            "version": "1.0.0",
            "description": "智能Mermaid图表生成工具，支持布局优化、主题系统和高质量输出",
            "author": "MCP-Mermaid Team",
            "homepage": "https://github.com/mcp-mermaid/mcp-mermaid"
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")

        try:
            if method == "initialize":
                # 初始化响应 - 按照MCP最新规范
                client_info = params.get("clientInfo", {})
                print(f"📞 客户端连接: {client_info.get('name', 'Unknown')} v{client_info.get('version', 'Unknown')}", file=sys.stderr)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": self.server_info,
                        "capabilities": {
                            "tools": {
                                "listChanged": False
                            },
                            "resources": {},
                            "prompts": {},
                            "logging": {}
                        },
                    },
                }

            elif method == "notifications/initialized":
                # 初始化完成通知
                print("✅ MCP协议初始化完成", file=sys.stderr)
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

                print(f"🔧 调用工具: {tool_name}", file=sys.stderr)

                result = self.tools.call_tool(tool_name, arguments)

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(result)}]},
                }

            elif method == "ping":
                # 心跳检测
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}
                }

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
            print(f"❌ 请求处理错误: {e}", file=sys.stderr)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
        }

    async def run(self):
        """运行MCP服务器"""
        print("🚀 MCP-Mermaid服务器已启动，等待连接...", file=sys.stderr)
        
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
                    print(f"📨 收到请求: {request.get('method')}", file=sys.stderr)

                    # 处理请求
                    response = await self.handle_request(request)

                # 发送响应（如果有）
                if response is not None:
                    response_str = json.dumps(response) + "\n"
                    sys.stdout.write(response_str)
                    sys.stdout.flush()

            except KeyboardInterrupt:
                print("🛑 收到中断信号，正在关闭服务器...", file=sys.stderr)
                break
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}", file=sys.stderr)
                # 发送错误响应
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": "Parse error"}
                }
                response_str = json.dumps(error_response) + "\n"
                sys.stdout.write(response_str)
                sys.stdout.flush()
            except Exception as e:
                print(f"❌ 服务器错误: {e}", file=sys.stderr)
                break

                # 清理资源
                print("🧹 清理资源...", file=sys.stderr)
                self.tools.cleanup()


async def main():
    """异步主函数"""
    server = MCPMermaidServer()
    await server.run()


def main_sync():
    """同步入口点，用于console script"""
    parser = argparse.ArgumentParser(
        prog="mcp-mermaid",
        description="MCP Mermaid图表生成服务器"
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 1.0.0"
    )
    parser.add_argument(
        "--help-tools",
        action="store_true",
        help="显示可用工具列表"
    )
    
    # 如果没有参数，或者参数只是帮助相关，则解析参数
    if len(sys.argv) > 1:
        args = parser.parse_args()
        
        if args.help_tools:
            tools = MermaidTools()
            print("🛠️ 可用工具:")
            for tool in tools.get_tools():
                print(f"  - {tool['name']}: {tool['description']}")
            tools.cleanup()
            return
    else:
        # 没有参数时启动MCP服务器
        print("🚀 启动MCP Mermaid服务器...", file=sys.stderr)
        print("💡 使用 --help 查看可用选项", file=sys.stderr)
        asyncio.run(main())


if __name__ == "__main__":
    main_sync() 