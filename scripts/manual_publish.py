#!/usr/bin/env python3
"""
手动发布脚本 - 用于首次发布到PyPI
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False


def main():
    """主函数"""
    print("🚀 开始手动发布到PyPI...")
    
    # 检查必要文件
    required_files = ["pyproject.toml", "README.md"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少必要文件: {file}")
            sys.exit(1)
    
    # 清理之前的构建
    print("🧹 清理之前的构建...")
    for dir_name in ["build", "dist", "*.egg-info"]:
        if Path(dir_name).exists():
            subprocess.run(["rm", "-rf", dir_name], check=False)
    
    # 构建包
    if not run_command(["python", "-m", "build"], "构建包"):
        sys.exit(1)
    
    # 检查构建结果
    if not run_command(["python", "-m", "twine", "check", "dist/*"], "检查构建结果"):
        sys.exit(1)
    
    # 发布到TestPyPI（可选）
    print("\n📤 准备发布...")
    choice = input("选择发布目标:\n1) TestPyPI (测试)\n2) PyPI (正式)\n请选择 (1/2): ").strip()
    
    if choice == "1":
        # 发布到TestPyPI
        print("📤 发布到TestPyPI...")
        cmd = ["python", "-m", "twine", "upload", "--repository", "testpypi", "dist/*"]
    elif choice == "2":
        # 发布到PyPI
        print("📤 发布到PyPI...")
        cmd = ["python", "-m", "twine", "upload", "dist/*"]
    else:
        print("❌ 无效选择")
        sys.exit(1)
    
    # 提示用户准备认证
    print("\n⚠️  注意：您需要输入PyPI的用户名和密码")
    print("   或者确保已配置好 .pypirc 文件")
    input("按回车键继续...")
    
    if run_command(cmd, f"发布到{'TestPyPI' if choice == '1' else 'PyPI'}"):
        print("\n🎉 发布成功！")
        if choice == "1":
            print("📋 TestPyPI页面: https://test.pypi.org/project/mcp-mermaid/")
        else:
            print("📋 PyPI页面: https://pypi.org/project/mcp-mermaid/")
        print("\n🔧 下一步：配置 Trusted Publisher")
        print("   请参考 PYPI_SETUP.md 文件中的说明")
    else:
        print("❌ 发布失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 