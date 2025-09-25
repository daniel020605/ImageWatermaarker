"""
颜色选择器模块
"""

import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Callable, Optional, Tuple
import colorsys


class ColorPicker:
    """颜色选择器"""
    
    def __init__(self, parent, initial_color: str = "#000000"):
        """
        初始化颜色选择器
        
        Args:
            parent: 父控件
            initial_color: 初始颜色
        """
        self.parent = parent
        self.current_color = initial_color
        
        # 回调函数
        self.color_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)
        
        # 颜色显示框架
        self.color_frame = ttk.Frame(self.frame)
        self.color_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 颜色标签
        ttk.Label(self.color_frame, text="颜色:").pack(side=tk.LEFT)
        
        # 颜色显示框
        self.color_display = tk.Frame(
            self.color_frame, width=40, height=25,
            bg=self.current_color, relief=tk.RAISED, bd=2
        )
        self.color_display.pack(side=tk.LEFT, padx=(5, 10))
        self.color_display.pack_propagate(False)
        
        # 颜色选择按钮
        self.color_button = ttk.Button(
            self.color_frame, text="选择颜色",
            command=self.choose_color
        )
        self.color_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 颜色值输入框
        self.color_var = tk.StringVar(value=self.current_color)
        self.color_entry = ttk.Entry(
            self.color_frame, textvariable=self.color_var, width=10
        )
        self.color_entry.pack(side=tk.LEFT)
        self.color_entry.bind('<Return>', self.on_color_entry_change)
        self.color_entry.bind('<FocusOut>', self.on_color_entry_change)
        
        # 预设颜色框架
        self.preset_frame = ttk.LabelFrame(self.frame, text="预设颜色", padding="5")
        self.preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建预设颜色按钮
        self.create_preset_colors()
        
        # RGB调节框架
        self.rgb_frame = ttk.LabelFrame(self.frame, text="RGB调节", padding="5")
        self.rgb_frame.pack(fill=tk.X)
        
        # RGB滑块
        self.create_rgb_sliders()
    
    def create_preset_colors(self):
        """创建预设颜色按钮"""
        preset_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#FF00FF", "#00FFFF", "#FFA500", "#800080",
            "#FFC0CB", "#A52A2A", "#808080", "#008000", "#000080"
        ]
        
        # 创建颜色按钮网格
        for i, color in enumerate(preset_colors):
            row = i // 5
            col = i % 5
            
            color_btn = tk.Button(
                self.preset_frame, width=3, height=1,
                bg=color, relief=tk.RAISED, bd=1,
                command=lambda c=color: self.set_color(c)
            )
            color_btn.grid(row=row, column=col, padx=1, pady=1)
            
            # 添加工具提示
            self.create_tooltip(color_btn, color)
    
    def create_rgb_sliders(self):
        """创建RGB滑块"""
        # 解析当前颜色
        r, g, b = self.hex_to_rgb(self.current_color)
        
        # RGB变量
        self.var_r = tk.IntVar(value=r)
        self.var_g = tk.IntVar(value=g)
        self.var_b = tk.IntVar(value=b)
        
        # R滑块
        ttk.Label(self.rgb_frame, text="R:").grid(row=0, column=0, sticky=tk.W)
        self.r_scale = ttk.Scale(
            self.rgb_frame, from_=0, to=255, variable=self.var_r,
            orient=tk.HORIZONTAL, length=150,
            command=self.on_rgb_change
        )
        self.r_scale.grid(row=0, column=1, padx=(5, 10), sticky=tk.W+tk.E)
        self.r_label = ttk.Label(self.rgb_frame, text=str(r), width=3)
        self.r_label.grid(row=0, column=2, sticky=tk.W)
        
        # G滑块
        ttk.Label(self.rgb_frame, text="G:").grid(row=1, column=0, sticky=tk.W)
        self.g_scale = ttk.Scale(
            self.rgb_frame, from_=0, to=255, variable=self.var_g,
            orient=tk.HORIZONTAL, length=150,
            command=self.on_rgb_change
        )
        self.g_scale.grid(row=1, column=1, padx=(5, 10), sticky=tk.W+tk.E)
        self.g_label = ttk.Label(self.rgb_frame, text=str(g), width=3)
        self.g_label.grid(row=1, column=2, sticky=tk.W)
        
        # B滑块
        ttk.Label(self.rgb_frame, text="B:").grid(row=2, column=0, sticky=tk.W)
        self.b_scale = ttk.Scale(
            self.rgb_frame, from_=0, to=255, variable=self.var_b,
            orient=tk.HORIZONTAL, length=150,
            command=self.on_rgb_change
        )
        self.b_scale.grid(row=2, column=1, padx=(5, 10), sticky=tk.W+tk.E)
        self.b_label = ttk.Label(self.rgb_frame, text=str(b), width=3)
        self.b_label.grid(row=2, column=2, sticky=tk.W)
        
        # 配置列权重
        self.rgb_frame.columnconfigure(1, weight=1)
    
    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief=tk.SOLID, borderwidth=1, font=("Arial", 8))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def choose_color(self):
        """打开颜色选择对话框"""
        color = colorchooser.askcolor(
            color=self.current_color,
            title="选择颜色"
        )
        
        if color[1]:  # 用户选择了颜色
            self.set_color(color[1])
    
    def set_color(self, color: str):
        """设置颜色"""
        if self.is_valid_color(color):
            self.current_color = color.upper()
            self.update_display()
            
            # 触发回调
            if self.color_change_callback:
                self.color_change_callback(self.current_color)
    
    def update_display(self):
        """更新显示"""
        # 更新颜色显示框
        self.color_display.configure(bg=self.current_color)
        
        # 更新颜色值输入框
        self.color_var.set(self.current_color)
        
        # 更新RGB滑块
        r, g, b = self.hex_to_rgb(self.current_color)
        self.var_r.set(r)
        self.var_g.set(g)
        self.var_b.set(b)
        
        # 更新RGB标签
        self.r_label.configure(text=str(r))
        self.g_label.configure(text=str(g))
        self.b_label.configure(text=str(b))
    
    def on_color_entry_change(self, event=None):
        """颜色输入框改变"""
        color = self.color_var.get().strip()
        if self.is_valid_color(color):
            self.set_color(color)
        else:
            # 恢复原值
            self.color_var.set(self.current_color)
    
    def on_rgb_change(self, value=None):
        """RGB滑块改变"""
        r = int(self.var_r.get())
        g = int(self.var_g.get())
        b = int(self.var_b.get())
        
        # 更新RGB标签
        self.r_label.configure(text=str(r))
        self.g_label.configure(text=str(g))
        self.b_label.configure(text=str(b))
        
        # 转换为十六进制
        hex_color = self.rgb_to_hex(r, g, b)
        
        # 更新颜色
        self.current_color = hex_color
        self.color_display.configure(bg=hex_color)
        self.color_var.set(hex_color)
        
        # 触发回调
        if self.color_change_callback:
            self.color_change_callback(hex_color)
    
    def get_color(self) -> str:
        """获取当前颜色"""
        return self.current_color
    
    def get_rgb(self) -> Tuple[int, int, int]:
        """获取RGB值"""
        return self.hex_to_rgb(self.current_color)
    
    def set_color_change_callback(self, callback: Callable):
        """设置颜色改变回调"""
        self.color_change_callback = callback
    
    @staticmethod
    def is_valid_color(color: str) -> bool:
        """验证颜色格式"""
        if not color:
            return False
        
        # 移除空格
        color = color.strip()
        
        # 检查十六进制格式
        if color.startswith('#') and len(color) == 7:
            try:
                int(color[1:], 16)
                return True
            except ValueError:
                return False
        
        # 检查RGB格式
        if color.startswith('rgb(') and color.endswith(')'):
            try:
                rgb_str = color[4:-1]
                r, g, b = map(int, rgb_str.split(','))
                return 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255
            except (ValueError, TypeError):
                return False
        
        return False
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """十六进制转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        """RGB转十六进制"""
        return f"#{r:02X}{g:02X}{b:02X}"
    
    @staticmethod
    def rgb_to_hsv(r: int, g: int, b: int) -> Tuple[float, float, float]:
        """RGB转HSV"""
        return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    
    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> Tuple[int, int, int]:
        """HSV转RGB"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r*255), int(g*255), int(b*255)
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)


class SimpleColorPicker:
    """简单颜色选择器"""
    
    def __init__(self, parent, initial_color: str = "#000000"):
        """
        初始化简单颜色选择器
        
        Args:
            parent: 父控件
            initial_color: 初始颜色
        """
        self.parent = parent
        self.current_color = initial_color
        
        # 回调函数
        self.color_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)
        
        # 颜色标签
        ttk.Label(self.frame, text="颜色:").pack(side=tk.LEFT)
        
        # 颜色显示框
        self.color_display = tk.Frame(
            self.frame, width=30, height=20,
            bg=self.current_color, relief=tk.RAISED, bd=1
        )
        self.color_display.pack(side=tk.LEFT, padx=(5, 10))
        self.color_display.pack_propagate(False)
        
        # 颜色选择按钮
        self.color_button = ttk.Button(
            self.frame, text="选择",
            command=self.choose_color
        )
        self.color_button.pack(side=tk.LEFT)
    
    def choose_color(self):
        """打开颜色选择对话框"""
        color = colorchooser.askcolor(
            color=self.current_color,
            title="选择颜色"
        )
        
        if color[1]:  # 用户选择了颜色
            self.set_color(color[1])
    
    def set_color(self, color: str):
        """设置颜色"""
        self.current_color = color.upper()
        self.color_display.configure(bg=color)
        
        # 触发回调
        if self.color_change_callback:
            self.color_change_callback(color)
    
    def get_color(self) -> str:
        """获取当前颜色"""
        return self.current_color
    
    def get_rgb(self) -> Tuple[int, int, int]:
        """获取RGB值"""
        return ColorPicker.hex_to_rgb(self.current_color)
    
    def set_color_change_callback(self, callback: Callable):
        """设置颜色改变回调"""
        self.color_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)


class ColorPresets:
    """颜色预设管理器"""
    
    # 常用颜色预设
    COMMON_COLORS = {
        "黑色": "#000000",
        "白色": "#FFFFFF",
        "红色": "#FF0000",
        "绿色": "#00FF00",
        "蓝色": "#0000FF",
        "黄色": "#FFFF00",
        "青色": "#00FFFF",
        "洋红": "#FF00FF",
        "橙色": "#FFA500",
        "紫色": "#800080",
        "粉色": "#FFC0CB",
        "棕色": "#A52A2A",
        "灰色": "#808080",
        "深绿": "#008000",
        "深蓝": "#000080"
    }
    
    # 文本水印推荐颜色
    TEXT_WATERMARK_COLORS = {
        "经典黑": "#000000",
        "纯白": "#FFFFFF",
        "深灰": "#333333",
        "浅灰": "#CCCCCC",
        "半透明黑": "#00000080",
        "半透明白": "#FFFFFF80",
        "金色": "#FFD700",
        "银色": "#C0C0C0",
        "深红": "#8B0000",
        "深蓝": "#000080"
    }
    
    @classmethod
    def get_color_by_name(cls, name: str) -> str:
        """根据名称获取颜色"""
        return cls.COMMON_COLORS.get(name, "#000000")
    
    @classmethod
    def get_text_watermark_color(cls, name: str) -> str:
        """获取文本水印推荐颜色"""
        return cls.TEXT_WATERMARK_COLORS.get(name, "#000000")
    
    @classmethod
    def get_contrasting_color(cls, bg_color: str) -> str:
        """获取对比色"""
        # 计算亮度
        r, g, b = ColorPicker.hex_to_rgb(bg_color)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        # 根据亮度返回对比色
        return "#FFFFFF" if brightness < 128 else "#000000"