"""
字体检测器模块

检测系统是否安装了必要的emoji字体，并提供安装指导
"""

import os
import platform
import subprocess
from typing import Tuple, List
from .logger import logger


class FontChecker:
    """系统字体检测器"""
    
    # 需要检测的emoji字体列表
    EMOJI_FONTS = [
        "Noto Color Emoji",
        "Apple Color Emoji", 
        "Segoe UI Emoji",
        "Twitter Color Emoji",
        "EmojiOne Color"
    ]
    
    @classmethod
    def check_emoji_fonts(cls) -> Tuple[bool, List[str]]:
        """
        检测系统是否安装了emoji字体
        
        Returns:
            Tuple[bool, List[str]]: (是否有emoji字体, 找到的字体列表)
        """
        system = platform.system().lower()
        
        if system == "linux":
            return cls._check_linux_fonts()
        elif system == "darwin":  # macOS
            return cls._check_macos_fonts()
        elif system == "windows":
            return cls._check_windows_fonts()
        else:
            logger.warning("⚠️ 未知操作系统，无法检测字体")
            return True, []  # 默认认为有字体，避免误报
    
    @classmethod
    def _check_linux_fonts(cls) -> Tuple[bool, List[str]]:
        """Linux系统字体检测"""
        try:
            # 首先尝试搜索emoji关键词
            result = subprocess.run(
                ["fc-list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                fonts = []
                for line in result.stdout.strip().split('\n'):
                    if 'emoji' in line.lower():
                        if ':' in line:
                            # 提取字体名称
                            parts = line.split(':')
                            if len(parts) >= 2:
                                font_name = parts[1].strip()
                                fonts.append(font_name)
                
                if fonts:
                    return True, fonts
                
            # 如果没找到，尝试检查已知的emoji字体文件
            known_emoji_fonts = [
                "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
                "/usr/share/fonts/truetype/twemoji/TwitterColorEmoji.ttf",
                "/usr/local/share/fonts/NotoColorEmoji.ttf"
            ]
            
            for font_path in known_emoji_fonts:
                if os.path.exists(font_path):
                    fonts.append(os.path.basename(font_path))
                    
            return len(fonts) > 0, fonts
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # fc-list命令不存在或超时
            logger.debug("fc-list命令不可用，跳过字体检测")
            return True, []  # 避免误报
    
    @classmethod
    def _check_macos_fonts(cls) -> Tuple[bool, List[str]]:
        """macOS系统字体检测"""
        # macOS通常自带Apple Color Emoji
        # 检查字体目录
        font_dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ]
        
        found_fonts = []
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for font_file in os.listdir(font_dir):
                    if "emoji" in font_file.lower():
                        found_fonts.append(font_file)
        
        return len(found_fonts) > 0, found_fonts
    
    @classmethod
    def _check_windows_fonts(cls) -> Tuple[bool, List[str]]:
        """Windows系统字体检测"""
        # Windows 10/11通常自带Segoe UI Emoji
        # 简单检查，大部分现代Windows都有emoji支持
        return True, ["Segoe UI Emoji"]
    
    @classmethod
    def get_install_instructions(cls) -> str:
        """获取字体安装指导"""
        system = platform.system().lower()
        
        if system == "linux":
            distro = cls._get_linux_distro()
            if "ubuntu" in distro or "debian" in distro:
                return """
🔧 请安装emoji字体以正确显示图表中的表情符号：

    sudo apt update
    sudo apt install fonts-noto-color-emoji

安装后可能需要刷新字体缓存：
    fc-cache -fv
"""
            elif "fedora" in distro or "centos" in distro or "rhel" in distro:
                return """
🔧 请安装emoji字体以正确显示图表中的表情符号：

    sudo dnf install google-noto-emoji-color-fonts
"""
            elif "arch" in distro:
                return """
🔧 请安装emoji字体以正确显示图表中的表情符号：

    sudo pacman -S noto-fonts-emoji
"""
            else:
                return """
🔧 请安装emoji字体以正确显示图表中的表情符号。

通用方法：
1. 下载Noto Color Emoji字体：
   https://github.com/googlefonts/noto-emoji/releases

2. 将字体文件复制到系统字体目录：
   sudo cp NotoColorEmoji.ttf /usr/share/fonts/

3. 刷新字体缓存：
   fc-cache -fv
"""
        
        elif system == "darwin":
            return """
🔧 macOS通常自带emoji字体支持。如果仍有问题，可以：

1. 从Google Fonts下载Noto Color Emoji：
   https://github.com/googlefonts/noto-emoji/releases

2. 双击字体文件安装
"""
        
        else:
            return """
🔧 请确保系统已安装emoji字体支持。
"""
    
    @classmethod
    def _get_linux_distro(cls) -> str:
        """获取Linux发行版信息"""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    return content
        except:
            pass
        return "unknown"
    
    @classmethod
    def check_and_warn(cls) -> None:
        """检测并警告用户关于字体问题"""
        has_fonts, found_fonts = cls.check_emoji_fonts()
        
        if not has_fonts:
            logger.warning("⚠️ 未检测到emoji字体，图表中的表情符号可能显示为方块")
            logger.info(cls.get_install_instructions())
        else:
            logger.debug(f"✅ 检测到emoji字体: {', '.join(found_fonts[:3])}") 