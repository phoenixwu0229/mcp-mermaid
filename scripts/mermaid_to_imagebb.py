#!/usr/bin/env python3
"""
MCP-Mermaid 图表生成工具

使用 mermaid-cli 生成高质量图表，支持智能布局优化、主题系统和自动上传 ImageBB
"""

import os
import sys
import subprocess
import requests
import base64
import json
import tempfile
import re
from pathlib import Path

# ImageBB API 配置
IMAGEBB_API_KEY = "06fe30dccc3e9ecb4113cc05714f1fb3"
IMAGEBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"

def setup_puppeteer_config():
    """设置 Puppeteer 配置文件"""
    # 指向js目录中的puppeteer-config.json
    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent
    config_path = project_root / "js" / "puppeteer-config.json"
    if not config_path.exists():
        config = {
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-first-run",
                "--disable-extensions",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ 创建 Puppeteer 配置文件: {config_path}")
    return str(config_path)

def create_theme_config(theme="default"):
    """创建主题配置文件"""
    themes = {
        "compact": {
            "theme": "base", 
            "themeVariables": {
                "primaryColor": "#4A90E2",
                "primaryTextColor": "#000000",
                "primaryBorderColor": "#2E5E99",
                "lineColor": "#333333",
                "secondaryColor": "#F0F8FF",
                "tertiaryColor": "#E8F4FD",
                "background": "#FFFFFF",
                "mainBkg": "#4A90E2",
                "secondBkg": "#E8F4FD",
                "tertiaryBkg": "#F0F8FF"
            },
            "flowchart": {
                "nodeSpacing": 30,
                "rankSpacing": 40,
                "padding": 10
            }
        },
        "professional": {
            "theme": "base",
            "themeVariables": {
                "primaryColor": "#2E5E99", 
                "primaryTextColor": "#000000",
                "primaryBorderColor": "#1A4D7A",
                "lineColor": "#2E5E99",
                "secondaryColor": "#E8F4FD",
                "tertiaryColor": "#F0F8FF",
                "background": "#FFFFFF"
            }
        },
        "minimal": {
            "theme": "base",
            "themeVariables": {
                "primaryColor": "#000000",
                "primaryTextColor": "#000000", 
                "primaryBorderColor": "#000000",
                "lineColor": "#000000",
                "secondaryColor": "#FFFFFF",
                "tertiaryColor": "#F5F5F5",
                "background": "#FFFFFF"
            }
        },
        "dark-pro": {
            "theme": "dark",
            "themeVariables": {
                "primaryColor": "#64B5F6",
                "primaryTextColor": "#FFFFFF",
                "primaryBorderColor": "#42A5F5", 
                "lineColor": "#64B5F6",
                "secondaryColor": "#263238",
                "tertiaryColor": "#37474F",
                "background": "#1E1E1E"
            }
        },
        "default": {
            "theme": "default",
            "themeVariables": {
                "primaryTextColor": "#000000",
                "lineColor": "#333333"
            }
        }
    }
    
    return themes.get(theme, themes["default"])

def optimize_layout(mermaid_content):
    """智能布局优化"""
    # 检测子图数量
    subgraph_count = len(re.findall(r'subgraph\s+', mermaid_content, re.IGNORECASE))
    
    # 统计节点数量（改进算法）
    node_patterns = [
        r'\b[A-Z]\d*\[',  # A[text], B1[text] 等
        r'\b[A-Z]\d*\(',  # A(text), B1(text) 等  
        r'\b[A-Z]\d*\{',  # A{text}, B1{text} 等
        r'\b[A-Z]\d*\>',  # A>text], B1>text] 等
    ]
    nodes = set()
    for pattern in node_patterns:
        matches = re.findall(pattern, mermaid_content)
        for match in matches:
            node_id = match.rstrip('[({>')
            nodes.add(node_id)
    
    node_count = len(nodes)
    
    # 统计连接数量
    connection_count = len(re.findall(r'-->', mermaid_content))
    
    # 计算连接密度
    connection_density = connection_count / node_count if node_count > 0 else 0
    
    print(f"📊 布局分析: 节点数={node_count}, 连接数={connection_count}, 子图数={subgraph_count}, 密度={connection_density:.2f}")
    
    # 布局优化规则
    if subgraph_count >= 2:
        # 分层架构保护：保持纵向布局
        return mermaid_content
    elif node_count >= 4 and connection_density <= 1.3:
        # 线性流程优化：转为横向布局
        return mermaid_content.replace('graph TB', 'graph LR').replace('graph TD', 'graph LR')
    elif node_count > 6 and connection_density < 2.0:
        # 复杂网络适配：横向布局提升信息密度
        return mermaid_content.replace('graph TB', 'graph LR').replace('graph TD', 'graph LR')
    
    return mermaid_content

def generate_mermaid_image(mermaid_content, output_path, title="", theme="default", format="png", quality="high"):
    """使用 mermaid-cli 生成图表"""
    
    # 智能布局优化
    optimized_content = optimize_layout(mermaid_content)
    
    # 设置质量参数
    quality_params = {
        "low": {"scale": 2, "width": 1200},
        "medium": {"scale": 3, "width": 1600}, 
        "high": {"scale": 3, "width": 1600},
        "ultra": {"scale": 4, "width": 2000}
    }
    
    params = quality_params.get(quality, quality_params["high"])
    
    # 创建主题配置
    theme_config = create_theme_config(theme)
    config_path = Path(__file__).parent / "mermaid-config.json"
    with open(config_path, 'w') as f:
        json.dump(theme_config, f, indent=2)
    
    # 创建临时 mermaid 文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(optimized_content)
        mermaid_file = f.name
    
    try:
        # 设置 Puppeteer 配置
        puppeteer_config = setup_puppeteer_config()
        
        # 构建 mermaid 命令
        cmd = [
            'mmdc',
            '-i', mermaid_file,
            '-o', output_path,
            '--configFile', str(config_path),
            '--puppeteerConfigFile', puppeteer_config,
            '--scale', str(params["scale"]),
            '--width', str(params["width"]),
            '--backgroundColor', 'white'
        ]
        
        if format == 'svg':
            cmd.extend(['-f', 'svg'])
        
        print(f"🎨 生成图表: {title}")
        print(f"📋 参数: 主题={theme}, 格式={format}, 质量={quality}")
        print(f"🔧 命令: {' '.join(cmd)}")
        
        # 执行命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 图表生成成功: {output_path}")
            return True
        else:
            print(f"❌ 图表生成失败:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 图表生成超时 (30秒)")
        return False
    except Exception as e:
        print(f"❌ 图表生成异常: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(mermaid_file):
            os.unlink(mermaid_file)
        if config_path.exists():
            os.unlink(config_path)

def upload_to_imagebb(image_path, title=""):
    """上传图片到 ImageBB"""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            'key': IMAGEBB_API_KEY,
            'image': image_data,
            'name': title or os.path.basename(image_path)
        }
        
        print(f"📤 上传到 ImageBB: {title}")
        response = requests.post(IMAGEBB_UPLOAD_URL, payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                url = data['data']['url']
                print(f"✅ 上传成功: {url}")
                return url
            else:
                print(f"❌ 上传失败: {data.get('error', {}).get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 上传失败: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 上传异常: {e}")
        return None

def mermaid_to_imagebb(mermaid_input, title="", theme="default", format="png", quality="high"):
    """主函数：Mermaid 转 ImageBB 链接"""
    
    # 处理输入：文件路径或直接内容
    if os.path.isfile(mermaid_input):
        with open(mermaid_input, 'r', encoding='utf-8') as f:
            mermaid_content = f.read()
        if not title:
            title = os.path.splitext(os.path.basename(mermaid_input))[0]
    else:
        mermaid_content = mermaid_input
    
    # 创建临时输出文件
    with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as f:
        output_path = f.name
    
    try:
        # 生成图表
        if generate_mermaid_image(mermaid_content, output_path, title, theme, format, quality):
            # 上传到 ImageBB
            image_url = upload_to_imagebb(output_path, title)
            if image_url:
                markdown_link = f"![{title}]({image_url})"
                print(f"📋 Markdown 链接: {markdown_link}")
                return markdown_link
        
        return None
        
    finally:
        # 清理临时文件
        if os.path.exists(output_path):
            os.unlink(output_path)

def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python mermaid_to_imagebb.py <mermaid文件或内容> <标题> [主题] [格式] [质量]")
        print("主题: compact(紧凑), professional(专业), minimal(极简), dark-pro(深色), default(默认)")
        print("格式: png, svg")  
        print("质量: low, medium, high, ultra")
        sys.exit(1)
    
    mermaid_input = sys.argv[1]
    title = sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) > 3 else "default"
    format = sys.argv[4] if len(sys.argv) > 4 else "png"
    quality = sys.argv[5] if len(sys.argv) > 5 else "high"
    
    result = mermaid_to_imagebb(mermaid_input, title, theme, format, quality)
    if result:
        print(f"\n🎉 最终结果: {result}")
    else:
        print("\n❌ 生成失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 