# 🚀 MCP-Mermaid 部署指南

## 环境要求

### 系统依赖

- **Python**: 3.8+
- **Node.js**: 14+
- **系统字体**: emoji字体包（必需）

### 字体依赖安装

**⚠️ 重要**：emoji正常显示需要系统安装emoji字体包

#### Ubuntu/Debian 系统

```bash
# 安装emoji字体
sudo apt update
sudo apt install fonts-noto-color-emoji

# 刷新字体缓存
sudo fc-cache -fv

# 验证安装
fc-list | grep emoji
# 应该看到: /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf
```

#### CentOS/RHEL 系统

```bash
# 安装emoji字体
sudo yum install google-noto-emoji-fonts

# 刷新字体缓存
sudo fc-cache -fv

# 验证安装
fc-list | grep emoji
```

#### macOS 系统

```bash
# macOS通常已内置emoji字体，如需安装：
brew install --cask font-noto-color-emoji
```

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd mcp-mermaid
```

### 2. 安装Python依赖

```bash
pip install -e .
# 或
pip install -r requirements.txt
```

### 3. 安装Node.js依赖

```bash
cd js
npm install
cd ..
```

### 4. 验证安装

```bash
# 检查命令行工具
mcp-mermaid --version
mcp-mermaid --help-tools

# 检查字体安装
fc-list | grep emoji
```

## 常见问题解决

### Emoji显示乱码

**现象**：图表中emoji显示为方块□或问号？

**诊断**：

```bash
fc-list | grep -i emoji
```

如果返回空，说明系统缺少emoji字体。

**解决**：按照上述字体依赖安装步骤操作。

### 图片生成失败

**现象**：Puppeteer截图失败

**可能原因**：

1. Node.js依赖未安装
2. 系统缺少图形库依赖

**解决**：

```bash
# 安装图形库依赖（Ubuntu）
sudo apt install libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 libcairo-gobject2 libgtk-3-0 libgdk-pixbuf2.0-0

# 重新安装Node.js依赖
cd js && npm install
```

### MCP协议通信问题

**现象**：客户端连接失败或响应格式错误

**检查**：

```bash
# 测试MCP服务器
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | mcp-mermaid
```

应该返回标准的JSON-RPC 2.0响应。

## 部署检查清单

### 必需检查项

- [ ] Python 3.8+ 已安装
- [ ] Node.js 14+ 已安装  
- [ ] emoji字体包已安装并验证
- [ ] Python依赖已安装
- [ ] Node.js依赖已安装
- [ ] 命令行工具正常工作
- [ ] 图片生成功能正常
- [ ] MCP协议通信正常

### 生产环境建议

- [ ] 配置日志输出目录
- [ ] 设置合适的临时文件清理策略
- [ ] 配置ImageBB API密钥（可选）
- [ ] 设置进程监控和自动重启
- [ ] 配置资源限制（内存、CPU）

## 性能优化

### 内存管理

- 图片生成后自动清理临时文件
- 控制并发请求数量
- 定期重启服务释放内存

### 响应时间

- 简单图表：2-5秒
- 复杂图表：5-15秒
- 包含上传：+2-5秒

### 资源使用

- CPU：主要消耗在Puppeteer渲染
- 内存：峰值约200-500MB
- 磁盘：临时文件约1-10MB/图表

## 技术支持

如遇到问题，请提供以下信息：

1. 操作系统版本：`cat /etc/os-release`
2. Python版本：`python --version`
3. Node.js版本：`node --version`
4. 字体安装状态：`fc-list | grep emoji`
5. 错误日志和详细错误信息

---

**最佳实践**：生产环境部署前，请确保在测试环境完整验证所有功能，特别是emoji显示和图片生成功能。
