"""
布局优化器测试

测试智能布局优化功能
"""

from src.mcp_mermaid.core.optimizer import LayoutOptimizer


class TestLayoutOptimizer:
    """布局优化器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.optimizer = LayoutOptimizer()

    def test_analyze_content_basic(self):
        """测试基本内容分析"""
        content = """
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
"""
        analysis = self.optimizer.analyze_content(content)

        assert analysis["nodes"] >= 3
        assert analysis["connections"] >= 2
        assert analysis["subgraphs"] == 0
        assert analysis["density"] > 0

    def test_optimize_layout_linear(self):
        """测试线性流程优化"""
        content = """
graph TD
    A[步骤1] --> B[步骤2]
    B --> C[步骤3]
    C --> D[步骤4]
"""
        optimized, reason = self.optimizer.optimize_layout(content)

        # 线性流程应该转为横向布局
        assert "graph LR" in optimized
        assert "线性流程" in reason

    def test_optimize_layout_subgraph(self):
        """测试子图保护"""
        content = """
graph TD
    subgraph S1[模块1]
        A[功能A]
        B[功能B]
    end
    subgraph S2[模块2]
        C[功能C]
        D[功能D]
    end
"""
        optimized, reason = self.optimizer.optimize_layout(content)

        # 有子图的应该保持纵向布局
        assert optimized == content
        assert "子图" in reason

    def test_cache_functionality(self):
        """测试缓存功能"""
        content = "graph TD\n    A --> B"

        # 第一次分析
        analysis1 = self.optimizer.analyze_content(content)

        # 第二次分析应该使用缓存
        analysis2 = self.optimizer.analyze_content(content)

        assert analysis1 == analysis2
        assert len(self.optimizer.analysis_cache) == 1

    def test_get_stats(self):
        """测试统计信息"""
        content = "graph TD\n    A --> B"
        self.optimizer.analyze_content(content)

        stats = self.optimizer.get_layout_stats()

        assert stats["cache_size"] == 1
        assert stats["total_analyzed"] == 1

    def test_clear_cache(self):
        """测试清空缓存"""
        content = "graph TD\n    A --> B"
        self.optimizer.analyze_content(content)

        assert len(self.optimizer.analysis_cache) == 1

        self.optimizer.clear_cache()

        assert len(self.optimizer.analysis_cache) == 0
