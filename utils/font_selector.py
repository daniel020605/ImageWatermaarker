"""
字体选择器模块
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
from typing import List, Optional, Callable, Tuple
import os
import platform
from PIL import ImageFont


class FontSelector:
    """字体选择器"""
    
    def __init__(self, parent):
        """
        初始化字体选择器
        
        Args:
            parent: 父控件
        """
        self.parent = parent
        
        # 变量
        self.var_font_family = tk.StringVar(value="Arial")
        self.var_font_size = tk.IntVar(value=24)
        self.var_font_bold = tk.BooleanVar(value=False)
        self.var_font_italic = tk.BooleanVar(value=False)
        
        # 回调函数
        self.font_change_callback: Optional[Callable] = None
        
        # 字体列表
        self.system_fonts = self.get_system_fonts()
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.var_font_family.trace('w', self.on_font_change)
        self.var_font_size.trace('w', self.on_font_change)
        self.var_font_bold.trace('w', self.on_font_change)
        self.var_font_italic.trace('w', self.on_font_change)
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="字体设置", padding="10")
        
        # 字体族框架
        self.family_frame = ttk.Frame(self.frame)
        self.family_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.family_frame, text="字体:").pack(side=tk.LEFT)
        
        # 字体下拉框
        self.font_combo = ttk.Combobox(
            self.family_frame, textvariable=self.var_font_family,
            values=self.system_fonts, state="readonly", width=20
        )
        self.font_combo.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 字体大小框架
        self.size_frame = ttk.Frame(self.frame)
        self.size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.size_frame, text="大小:").pack(side=tk.LEFT)
        
        # 字体大小滑块
        self.size_scale = ttk.Scale(
            self.size_frame, from_=8, to=200,
            variable=self.var_font_size, orient=tk.HORIZONTAL,
            length=150
        )
        self.size_scale.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        # 字体大小输入框
        self.size_spinbox = ttk.Spinbox(
            self.size_frame, from_=8, to=200,
            textvariable=self.var_font_size, width=6
        )
        self.size_spinbox.pack(side=tk.LEFT)
        
        # 字体样式框架
        self.style_frame = ttk.Frame(self.frame)
        self.style_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 粗体复选框
        self.bold_check = ttk.Checkbutton(
            self.style_frame, text="粗体",
            variable=self.var_font_bold
        )
        self.bold_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # 斜体复选框
        self.italic_check = ttk.Checkbutton(
            self.style_frame, text="斜体",
            variable=self.var_font_italic
        )
        self.italic_check.pack(side=tk.LEFT)
        
        # 预览框架
        self.preview_frame = ttk.LabelFrame(self.frame, text="预览", padding="10")
        self.preview_frame.pack(fill=tk.X)
        
        # 预览文本
        self.preview_text = tk.Text(
            self.preview_frame, height=3, width=30,
            wrap=tk.WORD, state=tk.DISABLED
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 更新预览
        self.update_preview()
    
    def get_system_fonts(self) -> List[str]:
        """获取系统字体列表"""
        try:
            # 获取tkinter字体列表
            tk_fonts = list(tkfont.families())
            
            # 添加常用字体
            common_fonts = [
                "Arial", "Times New Roman", "Helvetica", "Courier New",
                "Verdana", "Georgia", "Comic Sans MS", "Impact",
                "Trebuchet MS", "Arial Black", "Palatino", "Garamond"
            ]
            
            # 中文字体
            chinese_fonts = [
                "SimSun", "SimHei", "Microsoft YaHei", "KaiTi",
                "FangSong", "LiSu", "YouYuan", "STXihei",
                "STKaiti", "STSong", "STFangsong"
            ]
            
            # 合并并去重
            all_fonts = list(set(tk_fonts + common_fonts + chinese_fonts))
            all_fonts.sort()
            
            return all_fonts
            
        except Exception:
            # 如果获取失败，返回基本字体列表
            return [
                "Arial", "Times New Roman", "Helvetica", "Courier New",
                "Verdana", "Georgia", "SimSun", "SimHei", "Microsoft YaHei"
            ]
    
    def on_font_change(self, *args):
        """字体改变事件"""
        self.update_preview()
        
        # 触发回调
        if self.font_change_callback:
            font_info = self.get_font_info()
            self.font_change_callback(font_info)
    
    def update_preview(self):
        """更新字体预览"""
        try:
            # 获取字体信息
            family = self.var_font_family.get()
            size = max(8, min(72, self.var_font_size.get()))  # 限制预览字体大小
            weight = "bold" if self.var_font_bold.get() else "normal"
            slant = "italic" if self.var_font_italic.get() else "roman"
            
            # 创建字体
            preview_font = tkfont.Font(
                family=family, size=size,
                weight=weight, slant=slant
            )
            
            # 更新预览文本
            self.preview_text.configure(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            preview_content = f"字体预览 Font Preview\n{family} {size}pt\nABCDEFG abcdefg 123456"
            self.preview_text.insert(1.0, preview_content)
            self.preview_text.configure(font=preview_font, state=tk.DISABLED)
            
        except Exception as e:
            # 如果字体设置失败，使用默认字体
            self.preview_text.configure(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, f"字体预览失败: {str(e)}")
            self.preview_text.configure(state=tk.DISABLED)
    
    def get_font_info(self) -> dict:
        """获取字体信息"""
        return {
            "family": self.var_font_family.get(),
            "size": self.var_font_size.get(),
            "bold": self.var_font_bold.get(),
            "italic": self.var_font_italic.get()
        }
    
    def set_font_info(self, font_info: dict):
        """设置字体信息"""
        if "family" in font_info:
            self.var_font_family.set(font_info["family"])
        if "size" in font_info:
            self.var_font_size.set(font_info["size"])
        if "bold" in font_info:
            self.var_font_bold.set(font_info["bold"])
        if "italic" in font_info:
            self.var_font_italic.set(font_info["italic"])
    
    def get_pil_font(self) -> ImageFont.FreeTypeFont:
        """获取PIL字体对象"""
        try:
            family = self.var_font_family.get()
            size = self.var_font_size.get()
            
            # 尝试加载系统字体
            font_path = self.find_font_file(family)
            if font_path:
                return ImageFont.truetype(font_path, size)
            else:
                # 使用默认字体
                return ImageFont.load_default()
                
        except Exception:
            # 如果加载失败，返回默认字体
            return ImageFont.load_default()
    
    def find_font_file(self, font_family: str) -> Optional[str]:
        """查找字体文件路径"""
        try:
            system = platform.system()
            
            if system == "Windows":
                font_dirs = [
                    "C:/Windows/Fonts/",
                    "C:/Windows/System32/Fonts/"
                ]
                font_extensions = [".ttf", ".otf", ".ttc"]
                
            elif system == "Darwin":  # macOS
                font_dirs = [
                    "/System/Library/Fonts/",
                    "/Library/Fonts/",
                    os.path.expanduser("~/Library/Fonts/")
                ]
                font_extensions = [".ttf", ".otf", ".ttc", ".dfont"]
                
            else:  # Linux
                font_dirs = [
                    "/usr/share/fonts/",
                    "/usr/local/share/fonts/",
                    os.path.expanduser("~/.fonts/"),
                    os.path.expanduser("~/.local/share/fonts/")
                ]
                font_extensions = [".ttf", ".otf", ".ttc"]
            
            # 字体名称映射
            font_mapping = {
                "Arial": ["arial", "Arial"],
                "Times New Roman": ["times", "Times", "TimesNewRoman"],
                "Helvetica": ["helvetica", "Helvetica"],
                "Courier New": ["courier", "Courier", "CourierNew"],
                "Verdana": ["verdana", "Verdana"],
                "Georgia": ["georgia", "Georgia"],
                "SimSun": ["simsun", "SimSun", "宋体"],
                "SimHei": ["simhei", "SimHei", "黑体"],
                "Microsoft YaHei": ["msyh", "MicrosoftYaHei", "微软雅黑"],
                "KaiTi": ["kaiti", "KaiTi", "楷体"],
                "FangSong": ["fangsong", "FangSong", "仿宋"]
            }
            
            # 获取可能的字体文件名
            possible_names = font_mapping.get(font_family, [font_family.lower(), font_family])
            
            # 搜索字体文件
            for font_dir in font_dirs:
                if not os.path.exists(font_dir):
                    continue
                    
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        file_lower = file.lower()
                        name_without_ext = os.path.splitext(file_lower)[0]
                        
                        # 检查文件扩展名
                        if not any(file_lower.endswith(ext) for ext in font_extensions):
                            continue
                        
                        # 检查文件名是否匹配
                        for possible_name in possible_names:
                            if possible_name.lower() in name_without_ext:
                                return os.path.join(root, file)
            
            return None
            
        except Exception:
            return None
    
    def set_font_change_callback(self, callback: Callable):
        """设置字体改变回调"""
        self.font_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)


class SimpleFontSelector:
    """简单字体选择器"""
    
    def __init__(self, parent):
        """
        初始化简单字体选择器
        
        Args:
            parent: 父控件
        """
        self.parent = parent
        
        # 变量
        self.var_font_size = tk.IntVar(value=24)
        
        # 回调函数
        self.font_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.var_font_size.trace('w', self.on_font_change)
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)
        
        # 字体大小
        ttk.Label(self.frame, text="字体大小:").pack(side=tk.LEFT)
        
        self.size_spinbox = ttk.Spinbox(
            self.frame, from_=8, to=200,
            textvariable=self.var_font_size, width=6
        )
        self.size_spinbox.pack(side=tk.LEFT, padx=(5, 0))
    
    def on_font_change(self, *args):
        """字体改变事件"""
        if self.font_change_callback:
            self.font_change_callback(self.var_font_size.get())
    
    def get_font_size(self) -> int:
        """获取字体大小"""
        return self.var_font_size.get()
    
    def set_font_size(self, size: int):
        """设置字体大小"""
        self.var_font_size.set(size)
    
    def set_font_change_callback(self, callback: Callable):
        """设置字体改变回调"""
        self.font_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)


class FontPresets:
    """字体预设管理器"""
    
    # 常用字体预设
    COMMON_FONTS = {
        "标准": {"family": "Arial", "size": 24, "bold": False, "italic": False},
        "标题": {"family": "Arial", "size": 36, "bold": True, "italic": False},
        "小标题": {"family": "Arial", "size": 28, "bold": True, "italic": False},
        "正文": {"family": "Arial", "size": 20, "bold": False, "italic": False},
        "注释": {"family": "Arial", "size": 16, "bold": False, "italic": True},
        "强调": {"family": "Arial", "size": 24, "bold": True, "italic": True}
    }
    
    # 中文字体预设
    CHINESE_FONTS = {
        "宋体标准": {"family": "SimSun", "size": 24, "bold": False, "italic": False},
        "黑体标题": {"family": "SimHei", "size": 36, "bold": True, "italic": False},
        "雅黑正文": {"family": "Microsoft YaHei", "size": 22, "bold": False, "italic": False},
        "楷体签名": {"family": "KaiTi", "size": 20, "bold": False, "italic": False},
        "仿宋古典": {"family": "FangSong", "size": 18, "bold": False, "italic": False}
    }
    
    # 水印专用字体预设
    WATERMARK_FONTS = {
        "版权标准": {"family": "Arial", "size": 16, "bold": False, "italic": False},
        "版权加粗": {"family": "Arial", "size": 18, "bold": True, "italic": False},
        "签名风格": {"family": "Times New Roman", "size": 20, "bold": False, "italic": True},
        "品牌标识": {"family": "Arial Black", "size": 24, "bold": True, "italic": False},
        "日期时间": {"family": "Courier New", "size": 14, "bold": False, "italic": False}
    }
    
    @classmethod
    def get_preset(cls, category: str, name: str) -> dict:
        """获取预设字体"""
        presets = {
            "common": cls.COMMON_FONTS,
            "chinese": cls.CHINESE_FONTS,
            "watermark": cls.WATERMARK_FONTS
        }
        
        return presets.get(category, {}).get(name, cls.COMMON_FONTS["标准"])
    
    @classmethod
    def get_all_presets(cls) -> dict:
        """获取所有预设"""
        return {
            "常用字体": cls.COMMON_FONTS,
            "中文字体": cls.CHINESE_FONTS,
            "水印专用": cls.WATERMARK_FONTS
        }


class FontManager:
    """字体管理器"""
    
    def __init__(self):
        """初始化字体管理器"""
        self.font_cache = {}
        self.system_fonts = None
    
    def get_system_fonts(self) -> List[str]:
        """获取系统字体列表（缓存）"""
        if self.system_fonts is None:
            self.system_fonts = self._scan_system_fonts()
        return self.system_fonts
    
    def _scan_system_fonts(self) -> List[str]:
        """扫描系统字体"""
        try:
            # 获取tkinter字体列表
            fonts = list(tkfont.families())
            fonts.sort()
            return fonts
        except Exception:
            return ["Arial", "Times New Roman", "Helvetica"]
    
    def get_font(self, family: str, size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
        """获取字体对象（带缓存）"""
        cache_key = f"{family}_{size}_{bold}_{italic}"
        
        if cache_key not in self.font_cache:
            try:
                # 尝试创建字体
                font_path = self._find_font_file(family)
                if font_path:
                    font = ImageFont.truetype(font_path, size)
                else:
                    font = ImageFont.load_default()
                
                self.font_cache[cache_key] = font
            except Exception:
                self.font_cache[cache_key] = ImageFont.load_default()
        
        return self.font_cache[cache_key]
    
    def _find_font_file(self, family: str) -> Optional[str]:
        """查找字体文件"""
        # 这里可以实现更复杂的字体查找逻辑
        # 暂时返回None，使用默认字体
        return None
    
    def clear_cache(self):
        """清除字体缓存"""
        self.font_cache.clear()
    
    def get_font_info(self, font_path: str) -> dict:
        """获取字体文件信息"""
        try:
            font = ImageFont.truetype(font_path, 12)
            return {
                "path": font_path,
                "family": getattr(font, 'font', {}).get('family', 'Unknown'),
                "style": getattr(font, 'font', {}).get('style', 'Regular')
            }
        except Exception:
            return {"path": font_path, "family": "Unknown", "style": "Regular"}


# 全局字体管理器实例
font_manager = FontManager()