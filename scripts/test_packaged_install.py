#!/usr/bin/env python3
"""
测试打包后的mcp-mermaid安装和功能

用于验证PyPI发布后的包是否能正常工作
"""

import sys
import os
import tempfile

def test_packaged_installation():
    """测试打包后的安装"""
    print("🧪 测试mcp_mermaid包导入...")
    
    try:
        # 测试基本导入
        from mcp_mermaid.core.generator import MermaidGenerator
        print("✅ 导入MermaidGenerator成功")
        
        # 测试JS文件访问
        try:
            from importlib import resources
            js_dir = resources.files('mcp_mermaid').joinpath('js')
            puppeteer_script = js_dir.joinpath('puppeteer-screenshot.js')
            if puppeteer_script.exists():
                print(f"✅ 找到puppeteer-screenshot.js: {puppeteer_script}")
            else:
                print(f"❌ 找不到puppeteer-screenshot.js")
                return False
        except (ImportError, AttributeError):
            # Python 3.8 fallback
            import pkg_resources
            try:
                puppeteer_script = pkg_resources.resource_filename(
                    'mcp_mermaid', 'js/puppeteer-screenshot.js'
                )
                if os.path.exists(puppeteer_script):
                    print(f"✅ 找到puppeteer-screenshot.js (pkg_resources): {puppeteer_script}")
                else:
                    print(f"❌ 找不到puppeteer-screenshot.js")
                    return False
            except Exception as e:
                print(f"❌ 访问资源文件失败: {e}")
                return False
        
        # 测试生成器初始化
        print("\n🧪 测试MermaidGenerator初始化...")
        generator = MermaidGenerator()
        print("✅ MermaidGenerator初始化成功")
        
        # 测试简单图表生成（不执行puppeteer，只测试路径）
        print("\n🧪 测试图表生成准备...")
        sample_content = """graph TD
            A[开始] --> B[处理]
            B --> C[结束]"""
        
        # 创建HTML文件测试
        theme_config = {'theme': 'default'}
        html_file = generator._create_html_file(sample_content, theme_config)
        if os.path.exists(html_file):
            print(f"✅ HTML文件创建成功: {html_file}")
            os.remove(html_file)
        else:
            print("❌ HTML文件创建失败")
            return False
        
        # 清理
        generator.cleanup()
        
        print("\n🎉 所有测试通过！包安装和功能正常")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_packaged_installation()
    sys.exit(0 if success else 1) 