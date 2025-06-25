# PyPI Trusted Publisher 配置指南

## 🎯 问题描述

当前的CI/CD发布失败，错误信息：

```
invalid-publisher: valid token, but no corresponding publisher
```

这表示需要在PyPI上配置Trusted Publisher。

## 🔧 解决方案

### 方案1：配置Trusted Publisher（推荐）

#### 1. TestPyPI配置

1. **访问TestPyPI**：<https://test.pypi.org/>
2. **创建/管理项目**：
   - 如果项目不存在，先手动上传一个版本
   - 项目URL：<https://test.pypi.org/project/mcp-mermaid/>
3. **添加Trusted Publisher**：
   - 进入项目管理页面
   - 点击 "Publishing" 标签
   - 点击 "Add a new publisher"
   - 填写信息：

     ```
     Owner: phoenixwu0229
     Repository name: mcp-mermaid
     Workflow filename: publish.yml
     Environment name: testpypi
     ```

#### 2. 正式PyPI配置

1. **访问PyPI**：<https://pypi.org/>
2. **重复上述步骤**，但环境名称改为：`pypi`

### 方案2：使用API Token（临时方案）

如果Trusted Publisher配置有问题，可以暂时使用API Token：

#### 1. 获取API Token

**TestPyPI Token**：

1. 访问 <https://test.pypi.org/manage/account/token/>
2. 创建新的API Token
3. 范围选择：整个账户或特定项目

**PyPI Token**：

1. 访问 <https://pypi.org/manage/account/token/>
2. 创建新的API Token

#### 2. 添加GitHub Secrets

在GitHub仓库中添加以下secrets：

1. 进入仓库 → Settings → Secrets and variables → Actions
2. 添加：
   - `TEST_PYPI_API_TOKEN`: TestPyPI的API token
   - `PYPI_API_TOKEN`: PyPI的API token

## 🚀 推荐配置流程

1. **优先使用Trusted Publisher**：
   - 更安全，无需管理token
   - GitHub和PyPI官方推荐
   - 自动轮换，无过期问题

2. **API Token作为后备**：
   - 当前workflow已支持两种方式
   - 如果Trusted Publisher失败，会自动使用API token

## 📋 验证步骤

配置完成后，可以通过以下方式验证：

1. **推送新tag触发发布**：

   ```bash
   git tag v0.2.3
   git push origin v0.2.3
   ```

2. **检查GitHub Actions日志**
3. **验证包是否成功发布到PyPI/TestPyPI**

## 🔍 调试信息

当前错误的调试信息显示：

- Repository: `phoenixwu0229/mcp-mermaid`
- Environment: `testpypi`  
- Workflow: `publish.yml`
- Tag: `v0.2.2`

确保PyPI配置中的这些信息完全匹配。

## 📚 参考链接

- [PyPI Trusted Publishers文档](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions PyPI发布指南](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [故障排除指南](https://docs.pypi.org/trusted-publishers/troubleshooting/)
