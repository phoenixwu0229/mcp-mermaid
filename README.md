# 🎨 MCP-Mermaid

智能Mermaid图表生成工具，支持布局优化、主题系统和高质量输出的MCP服务器。

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mcp-mermaid.svg)](https://pypi.org/project/mcp-mermaid/)

## ✨ 核心特性

- 🎯 **智能布局优化** - 自动分析图表结构，选择最优布局方案
- 🎨 **多主题系统** - 5种专业主题，适配不同使用场景
- 📸 **高质量输出** - 支持多种分辨率，确保图表清晰度
- ☁️ **自动上传** - 集成ImageBB，生成永久访问链接
- 🔧 **MCP协议** - 完整的Model Context Protocol支持
- 🌐 **跨平台** - 支持Linux、macOS、Windows

## 🚀 快速开始

### 安装

```bash
pip install mcp-mermaid
```

### 基本使用

```bash
# 查看版本
mcp-mermaid --version

# 查看可用工具
mcp-mermaid --help-tools

# 启动MCP服务器
mcp-mermaid
```

### MCP客户端集成

MCP-Mermaid可以作为工具被AI助手调用，生成高质量的Mermaid图表：

```python
# 示例：通过MCP协议生成流程图
{
    "content": "graph TD; A-->B; B-->C; C-->D",
    "optimize_layout": True,
    "theme": "professional", 
    "quality": "high",
    "upload_image": True
}
```

## 🎨 主题展示

支持5种专业主题：

- **professional** - 商务专业风格
- **compact** - 紧凑信息密集型
- **minimal** - 极简清爽风格  
- **dark-pro** - 深色专业主题
- **default** - 经典默认样式

## 📋 系统要求

- Python 3.8+
- Node.js 16+ (用于图表渲染)
- 系统emoji字体支持

## 🔧 高级配置

### 质量设置

- **low** - 快速生成，适合预览
- **medium** - 平衡质量与速度
- **high** - 最高质量，适合正式文档

### 布局优化

智能识别图表类型并自动优化：

- 高密度图表 → TB方向 + 紧凑布局
- 层次结构 → 分层显示优化
- 流程图表 → LR方向 + 流程对齐
- 网络图表 → 力导向布局

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [Mermaid.js官方文档](https://mermaid.js.org/)
- [Model Context Protocol](https://spec.modelcontextprotocol.io/)
- [问题反馈](https://github.com/mcp-mermaid/mcp-mermaid/issues)

## 📈 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新详情。
