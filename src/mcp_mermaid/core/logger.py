"""
MCP-Mermaid日志系统

确保所有日志输出都通过stderr，不会干扰JSON-RPC协议通信
"""

import logging
import sys
from typing import Any


class MCPLogger:
    """MCP兼容的日志器"""

    def __init__(self, name: str = "mcp-mermaid"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            # 配置输出到stderr，避免干扰stdout的JSON-RPC通信
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def info(self, message: str, *args: Any) -> None:
        """记录信息日志"""
        self.logger.info(message, *args)

    def error(self, message: str, *args: Any) -> None:
        """记录错误日志"""
        self.logger.error(message, *args)

    def warning(self, message: str, *args: Any) -> None:
        """记录警告日志"""
        self.logger.warning(message, *args)

    def debug(self, message: str, *args: Any) -> None:
        """记录调试日志"""
        self.logger.debug(message, *args)


# 全局日志实例
logger = MCPLogger()
