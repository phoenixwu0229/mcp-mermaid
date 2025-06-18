#!/usr/bin/env python3
"""
测试MCP-Mermaid架构图生成
"""

from src.mcp_mermaid.tools.mermaid_tools import MermaidTools

def main():
    tools = MermaidTools()
    
    # 简化的架构图
    content = '''graph TB
    subgraph "MCP-Mermaid架构"
        A[MCP Server] --> B[Tools Interface]
        B --> C[MermaidGenerator]
        C --> D[LayoutOptimizer]
        C --> E[ThemeManager]
        C --> F[ImageUploader]
        C --> G[HTML Template]
        G --> H[Mermaid.js]
        H --> I[Puppeteer]
        I --> J[PNG Output]
        F --> K[ImageBB API]
        K --> L[Cloud URL]
    end
    
    style A fill:#ff9999
    style C fill:#99ccff
    style H fill:#99ff99
    style K fill:#ffcc99'''
    
    result = tools.call_tool('generate_diagram', {
        'content': content,
        'theme': 'professional',
        'title': 'MCP-Mermaid-Architecture'
    })
    
    print('=== MCP-Mermaid 架构图生成测试 ===')
    print('成功:', result['success'])
    
    if result['success']:
        data = result['data']
        print('主题:', data.get('theme'))
        print('布局优化:', data.get('layout_optimization'))
        print('云端URL:', data.get('image_url', 'None'))
        
        if data.get('image_url'):
            print('\n✅ 架构图已生成并上传到云端！')
            print('可直接访问:', data['image_url'])
            print('Markdown链接:', data.get('markdown_link', ''))
        else:
            print('本地图片:', data.get('image_path', 'None'))
    else:
        print('❌ 生成失败:', result.get('error'))

if __name__ == '__main__':
    main() 