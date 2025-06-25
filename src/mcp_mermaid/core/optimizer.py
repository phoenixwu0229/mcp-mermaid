"""
布局优化器模块

智能分析Mermaid图表内容，自动选择最优布局方向
"""

import re
from typing import Any, Dict, Tuple

from .logger import logger


class LayoutOptimizer:
    """智能布局优化器"""

    def __init__(self) -> None:
        self.analysis_cache: Dict[int, Dict[str, Any]] = {}

    def analyze_content(self, mermaid_content: str) -> Dict[str, Any]:
        """分析Mermaid内容结构"""
        # 使用内容哈希做缓存
        content_hash = hash(mermaid_content)
        if content_hash in self.analysis_cache:
            cached_result: Dict[str, Any] = self.analysis_cache[content_hash]
            return cached_result

        # 检测子图数量
        subgraph_count = len(
            re.findall(
                r"subgraph\s+",
                mermaid_content,
                re.IGNORECASE))

        # 统计节点数量（改进算法）
        node_patterns = [
            r"\b[A-Z]\d*\[",  # A[text], B1[text] 等
            r"\b[A-Z]\d*\(",  # A(text), B1(text) 等
            r"\b[A-Z]\d*\{",  # A{text}, B1{text} 等
            r"\b[A-Z]\d*\>",  # A>text], B1>text] 等
        ]
        nodes = set()
        for pattern in node_patterns:
            matches = re.findall(pattern, mermaid_content)
            for match in matches:
                node_id = match.rstrip("[({>")
                nodes.add(node_id)

        node_count = len(nodes)

        # 统计连接数量
        connection_count = len(re.findall(r"-->", mermaid_content))

        # 计算连接密度
        connection_density = connection_count / node_count if node_count > 0 else 0

        analysis = {
            "nodes": node_count,
            "connections": connection_count,
            "subgraphs": subgraph_count,
            "density": connection_density,
        }

        # 缓存结果
        self.analysis_cache[content_hash] = analysis
        return analysis

    def optimize_layout(self, mermaid_content: str) -> Tuple[str, str]:
        """
        智能布局优化

        Args:
            mermaid_content: 原始Mermaid内容

        Returns:
            Tuple[str, str]: (优化后的内容, 优化说明)
        """
        analysis = self.analyze_content(mermaid_content)

        logger.info(
            "布局分析: 节点数=%d, 连接数=%d, 子图数=%d, 密度=%.2f",
            analysis["nodes"],
            analysis["connections"],
            analysis["subgraphs"],
            analysis["density"],
        )

        # 布局优化规则
        if analysis["subgraphs"] >= 2:
            # 分层架构保护：保持纵向布局
            reason = f"检测到{analysis['subgraphs']}个子图，适合分层显示"
            logger.info("保持纵向布局: %s", reason)
            return mermaid_content, reason

        elif analysis["nodes"] >= 4 and analysis["density"] <= 1.3:
            # 线性流程优化：转为横向布局
            optimized = self._convert_to_horizontal(mermaid_content)
            reason = (
                f"线性流程结构 (节点:{analysis['nodes']}, "
                f"边/节点比:{analysis['density']:.2f})"
            )
            logger.info("优化为横向布局: %s", reason)
            return optimized, reason

        elif analysis["nodes"] > 6 and analysis["density"] < 2.0:
            # 复杂网络适配：横向布局提升信息密度
            optimized = self._convert_to_horizontal(mermaid_content)
            reason = f"复杂网络横向优化 (节点:{analysis['nodes']})"
            logger.info("优化为横向布局: %s", reason)
            return optimized, reason

        reason = "保持默认纵向布局"
        logger.info("布局决策: %s", reason)
        return mermaid_content, reason

    def _convert_to_horizontal(self, content: str) -> str:
        """将纵向布局转换为横向布局"""
        # 替换图表方向
        content = content.replace("graph TB", "graph LR")
        content = content.replace("graph TD", "graph LR")
        return content

    def get_layout_stats(self) -> Dict[str, int]:
        """获取布局优化统计信息"""
        return {
            "cache_size": len(self.analysis_cache),
            "total_analyzed": len(self.analysis_cache),
        }

    def clear_cache(self) -> None:
        """清空缓存"""
        self.analysis_cache.clear()
