#!/usr/bin/env python3
"""
MCP-Mermaid 包构建和发布脚本

支持本地构建、测试发布到TestPyPI和正式发布到PyPI
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd, check=True):
    """运行命令并处理输出"""
    print(f"🔧 执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result


def clean_build():
    """清理构建文件"""
    print("🧹 清理构建文件...")
    
    clean_dirs = ["build", "dist", "*.egg-info", "src/*.egg-info"]
    
    for pattern in clean_dirs:
        run_command(f"rm -rf {pattern}", check=False)
    
    print("✅ 清理完成")


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")
    
    os.chdir(PROJECT_ROOT)
    
    # 检查是否安装了pytest
    try:
        run_command("python -m pytest --version")
    except subprocess.CalledProcessError:
        print("⚠️ pytest未安装，跳过测试")
        return True
    
    # 运行测试
    result = run_command("python -m pytest tests/ -v", check=False)
    
    if result.returncode == 0:
        print("✅ 所有测试通过")
        return True
    else:
        print("❌ 测试失败")
        return False


def build_package():
    """构建包"""
    print("📦 构建包...")
    
    os.chdir(PROJECT_ROOT)
    
    # 检查是否安装了build
    try:
        run_command("python -m build --version")
    except subprocess.CalledProcessError:
        print("📥 安装build工具...")
        run_command("pip install build")
    
    # 构建包
    run_command("python -m build")
    
    print("✅ 包构建完成")


def check_package():
    """检查包的有效性"""
    print("🔍 检查包...")
    
    os.chdir(PROJECT_ROOT)
    
    # 检查是否安装了twine
    try:
        run_command("python -m twine --version")
    except subprocess.CalledProcessError:
        print("📥 安装twine...")
        run_command("pip install twine")
    
    # 检查包
    run_command("python -m twine check dist/*")
    
    print("✅ 包检查通过")


def publish_test():
    """发布到TestPyPI"""
    print("🚀 发布到TestPyPI...")
    
    os.chdir(PROJECT_ROOT)
    
    run_command("python -m twine upload --repository testpypi dist/*")
    
    print("✅ 发布到TestPyPI完成")
    print("📖 测试安装: pip install --index-url https://test.pypi.org/simple/ mcp-mermaid")


def publish_pypi():
    """发布到PyPI"""
    print("🚀 发布到PyPI...")
    
    # 确认发布
    confirm = input("⚠️ 确认发布到正式PyPI？(yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 发布已取消")
        return False
    
    os.chdir(PROJECT_ROOT)
    
    run_command("python -m twine upload dist/*")
    
    print("🎉 发布到PyPI完成")
    print("📖 安装命令: pip install mcp-mermaid")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="MCP-Mermaid 构建和发布工具")
    parser.add_argument("action", choices=["clean", "test", "build", "check", "test-publish", "publish", "full"], 
                       help="要执行的操作")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    
    args = parser.parse_args()
    
    print("🔨 MCP-Mermaid 构建和发布工具")
    print("=" * 40)
    
    try:
        if args.action == "clean":
            clean_build()
        
        elif args.action == "test":
            if not run_tests():
                sys.exit(1)
        
        elif args.action == "build":
            if not args.skip_tests:
                if not run_tests():
                    sys.exit(1)
            clean_build()
            build_package()
            check_package()
        
        elif args.action == "check":
            check_package()
        
        elif args.action == "test-publish":
            if not args.skip_tests:
                if not run_tests():
                    sys.exit(1)
            clean_build()
            build_package()
            check_package()
            publish_test()
        
        elif args.action == "publish":
            if not args.skip_tests:
                if not run_tests():
                    sys.exit(1)
            clean_build()
            build_package() 
            check_package()
            if not publish_pypi():
                sys.exit(1)
        
        elif args.action == "full":
            print("🎯 执行完整发布流程...")
            if not args.skip_tests:
                if not run_tests():
                    sys.exit(1)
            clean_build()
            build_package()
            check_package()
            publish_test()
            
            # 等待用户确认TestPyPI测试
            input("✋ 请先测试TestPyPI版本，确认无误后按Enter继续发布到正式PyPI...")
            
            if not publish_pypi():
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 