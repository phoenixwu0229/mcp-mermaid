"""版本管理模块 - Git环境版本获取"""

import subprocess
from typing import Optional


def get_version() -> str:
    """
    获取版本号，优先从Git tag获取，没有tag时使用commit hash

    Returns:
        版本字符串
    """
    # 尝试从Git tag获取版本
    git_version = _get_git_version()
    if git_version:
        return _normalize_version(git_version)

    # 没有tag时，直接使用commit hash
    commit_hash = _get_commit_hash()
    if commit_hash:
        return commit_hash

    # 异常情况（Git不可用等）
    return "unknown"


def _get_git_version() -> Optional[str]:
    """从Git tag获取版本信息"""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--dirty"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            if version:
                return version

    except Exception:
        pass

    return None


def _get_commit_hash() -> Optional[str]:
    """获取当前commit hash"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            commit_hash = result.stdout.strip()
            if commit_hash:
                return commit_hash

    except Exception:
        pass

    return None


def _normalize_version(git_version: str) -> str:
    """将Git版本转换为标准格式"""
    # 移除 'v' 前缀
    if git_version.startswith("v"):
        git_version = git_version[1:]

    # 处理dirty状态
    if git_version.endswith("-dirty"):
        git_version = git_version[:-6] + ".dev0"

    # 解析版本组件
    parts = git_version.split("-")

    if len(parts) == 1:
        # 精确标签
        return parts[0]
    elif len(parts) >= 3:
        # 包含提交信息：base.postN+hash
        base_version = parts[0]
        commits_ahead = parts[1]
        commit_hash = parts[2]
        return f"{base_version}.post{commits_ahead}+{commit_hash}"
    else:
        return parts[0] if parts else "unknown"


# 全局版本变量
__version__ = get_version()
