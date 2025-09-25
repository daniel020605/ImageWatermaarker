"""
图片尺寸调整模块
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple
from PIL import Image


class ImageResizeControl:
    """图片尺寸调整控制器"""
    
    def __init__(self, parent):
        """
        初始化图片尺寸调整控制器
        
        Args:
            parent: 父控件
        """
        self.parent = parent
        
        # 变量
        self.var_enable_resize = tk.BooleanVar(value=False)
        self.var_resize_mode = tk.StringVar(value="按百分比")
        self.var_scale_percent = tk.IntVar(value=100)
        self.var_target_width = tk.IntVar(value=800)
        self.var_target_height = tk.IntVar(value=600)
        self.var_keep_aspect_ratio = tk.BooleanVar(value=True)
        
        # 原始尺寸（用于计算）
        self.original_width = 0
        self.original_height = 0
        
        # 回调函数
        self.resize_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="图片尺寸调整", padding="10")
        
        # 启用调整
        self.enable_check = ttk.Checkbutton(
            self.frame, text="启用尺寸调整",
            variable=self.var_enable_resize
        )
        self.enable_check.pack(anchor=tk.W, pady=(0, 10))
        
        # 调整模式
        mode_frame = ttk.Frame(self.frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mode_frame, text="调整模式:").pack(side=tk.LEFT)
        
        self.mode_combo = ttk.Combobox(
            mode_frame, textvariable=self.var_resize_mode,
            values=["按百分比", "按宽度", "按高度", "自定义尺寸"],
            state="readonly", width=15
        )
        self.mode_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 百分比调整
        self.percent_frame = ttk.Frame(self.frame)
        self.percent_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.percent_frame, text="缩放百分比:").pack(side=tk.LEFT)
        
        self.percent_scale = ttk.Scale(
            self.percent_frame, from_=10, to=200, variable=self.var_scale_percent,
            orient=tk.HORIZONTAL, length=150
        )
        self.percent_scale.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        self.percent_spinbox = ttk.Spinbox(
            self.percent_frame, from_=10, to=500, textvariable=self.var_scale_percent, width=6
        )
        self.percent_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(self.percent_frame, text="%").pack(side=tk.LEFT, padx=(2, 0))
        
        # 尺寸调整
        self.size_frame = ttk.Frame(self.frame)
        
        # 宽度
        width_frame = ttk.Frame(self.size_frame)
        width_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(width_frame, text="宽度:").pack(side=tk.LEFT)
        
        self.width_spinbox = ttk.Spinbox(
            width_frame, from_=1, to=9999, textvariable=self.var_target_width, width=8
        )
        self.width_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(width_frame, text="像素").pack(side=tk.LEFT)
        
        # 高度
        height_frame = ttk.Frame(self.size_frame)
        height_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(height_frame, text="高度:").pack(side=tk.LEFT)
        
        self.height_spinbox = ttk.Spinbox(
            height_frame, from_=1, to=9999, textvariable=self.var_target_height, width=8
        )
        self.height_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(height_frame, text="像素").pack(side=tk.LEFT)
        
        # 保持宽高比
        self.aspect_check = ttk.Checkbutton(
            self.size_frame, text="保持宽高比",
            variable=self.var_keep_aspect_ratio
        )
        self.aspect_check.pack(anchor=tk.W)
        
        # 原始尺寸显示
        self.info_frame = ttk.Frame(self.frame)
        self.info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_label = ttk.Label(
            self.info_frame, text="原始尺寸: 未知",
            foreground="gray"
        )
        self.info_label.pack(anchor=tk.W)
        
        # 初始状态
        self.update_widget_states()
        self.update_mode_display()
    
    def bind_events(self):
        """绑定事件"""
        self.var_enable_resize.trace('w', self.on_enable_change)
        self.var_resize_mode.trace('w', self.on_mode_change)
        self.var_scale_percent.trace('w', self.on_resize_change)
        self.var_target_width.trace('w', self.on_width_change)
        self.var_target_height.trace('w', self.on_height_change)
        self.var_keep_aspect_ratio.trace('w', self.on_resize_change)
        
        self.mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
    
    def on_enable_change(self, *args):
        """启用状态改变"""
        self.update_widget_states()
        self.on_resize_change()
    
    def on_mode_change(self, *args):
        """模式改变"""
        self.update_mode_display()
        self.on_resize_change()
    
    def on_width_change(self, *args):
        """宽度改变"""
        if (self.var_keep_aspect_ratio.get() and 
            self.original_width > 0 and self.original_height > 0):
            # 根据宽度计算高度
            width = self.var_target_width.get()
            height = int(width * self.original_height / self.original_width)
            self.var_target_height.set(height)
        
        self.on_resize_change()
    
    def on_height_change(self, *args):
        """高度改变"""
        if (self.var_keep_aspect_ratio.get() and 
            self.original_width > 0 and self.original_height > 0):
            # 根据高度计算宽度
            height = self.var_target_height.get()
            width = int(height * self.original_width / self.original_height)
            self.var_target_width.set(width)
        
        self.on_resize_change()
    
    def on_resize_change(self, *args):
        """调整参数改变"""
        if self.resize_change_callback:
            self.resize_change_callback(self.get_resize_config())
    
    def update_widget_states(self):
        """更新控件状态"""
        enabled = self.var_enable_resize.get()
        state = "normal" if enabled else "disabled"
        
        self.mode_combo.configure(state="readonly" if enabled else "disabled")
        self.percent_scale.configure(state=state)
        self.percent_spinbox.configure(state=state)
        self.width_spinbox.configure(state=state)
        self.height_spinbox.configure(state=state)
        self.aspect_check.configure(state=state)
    
    def update_mode_display(self):
        """更新模式显示"""
        mode = self.var_resize_mode.get()
        
        if mode == "按百分比":
            self.percent_frame.pack(fill=tk.X, pady=(0, 10))
            self.size_frame.pack_forget()
        else:
            self.percent_frame.pack_forget()
            self.size_frame.pack(fill=tk.X, pady=(0, 10))
    
    def set_original_size(self, width: int, height: int):
        """设置原始尺寸"""
        self.original_width = width
        self.original_height = height
        
        # 更新显示
        self.info_label.configure(text=f"原始尺寸: {width} × {height}")
        
        # 更新默认目标尺寸
        self.var_target_width.set(width)
        self.var_target_height.set(height)
    
    def get_resize_config(self) -> dict:
        """获取调整配置"""
        if not self.var_enable_resize.get():
            return {'enabled': False}
        
        mode = self.var_resize_mode.get()
        
        config = {
            'enabled': True,
            'mode': mode,
            'keep_aspect_ratio': self.var_keep_aspect_ratio.get()
        }
        
        if mode == "按百分比":
            config['scale_percent'] = self.var_scale_percent.get()
        elif mode == "按宽度":
            config['target_width'] = self.var_target_width.get()
        elif mode == "按高度":
            config['target_height'] = self.var_target_height.get()
        else:  # 自定义尺寸
            config['target_width'] = self.var_target_width.get()
            config['target_height'] = self.var_target_height.get()
        
        return config
    
    def set_resize_config(self, config: dict):
        """设置调整配置"""
        self.var_enable_resize.set(config.get('enabled', False))
        self.var_resize_mode.set(config.get('mode', '按百分比'))
        self.var_keep_aspect_ratio.set(config.get('keep_aspect_ratio', True))
        
        if 'scale_percent' in config:
            self.var_scale_percent.set(config['scale_percent'])
        if 'target_width' in config:
            self.var_target_width.set(config['target_width'])
        if 'target_height' in config:
            self.var_target_height.set(config['target_height'])
        
        self.update_widget_states()
        self.update_mode_display()
    
    def set_resize_change_callback(self, callback: Callable):
        """设置调整改变回调"""
        self.resize_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)


class ImageResizer:
    """图片尺寸调整器"""
    
    @staticmethod
    def resize_image(image: Image.Image, resize_config: dict) -> Image.Image:
        """
        调整图片尺寸
        
        Args:
            image: 原图
            resize_config: 调整配置
            
        Returns:
            调整后的图片
        """
        if not resize_config.get('enabled', False):
            return image
        
        mode = resize_config.get('mode', '按百分比')
        keep_aspect = resize_config.get('keep_aspect_ratio', True)
        
        original_width, original_height = image.size
        
        if mode == "按百分比":
            scale = resize_config.get('scale_percent', 100) / 100.0
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
        elif mode == "按宽度":
            new_width = resize_config.get('target_width', original_width)
            if keep_aspect:
                new_height = int(new_width * original_height / original_width)
            else:
                new_height = original_height
                
        elif mode == "按高度":
            new_height = resize_config.get('target_height', original_height)
            if keep_aspect:
                new_width = int(new_height * original_width / original_height)
            else:
                new_width = original_width
                
        else:  # 自定义尺寸
            new_width = resize_config.get('target_width', original_width)
            new_height = resize_config.get('target_height', original_height)
        
        # 确保尺寸有效
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        # 调整图片尺寸
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    @staticmethod
    def calculate_size(original_size: Tuple[int, int], resize_config: dict) -> Tuple[int, int]:
        """
        计算调整后的尺寸（不实际调整图片）
        
        Args:
            original_size: 原始尺寸 (width, height)
            resize_config: 调整配置
            
        Returns:
            新尺寸 (width, height)
        """
        if not resize_config.get('enabled', False):
            return original_size
        
        original_width, original_height = original_size
        mode = resize_config.get('mode', '按百分比')
        keep_aspect = resize_config.get('keep_aspect_ratio', True)
        
        if mode == "按百分比":
            scale = resize_config.get('scale_percent', 100) / 100.0
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
        elif mode == "按宽度":
            new_width = resize_config.get('target_width', original_width)
            if keep_aspect:
                new_height = int(new_width * original_height / original_width)
            else:
                new_height = original_height
                
        elif mode == "按高度":
            new_height = resize_config.get('target_height', original_height)
            if keep_aspect:
                new_width = int(new_height * original_width / original_height)
            else:
                new_width = original_width
                
        else:  # 自定义尺寸
            new_width = resize_config.get('target_width', original_width)
            new_height = resize_config.get('target_height', original_height)
        
        # 确保尺寸有效
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        return new_width, new_height


class SimpleImageResize:
    """简化的图片尺寸调整"""
    
    def __init__(self, parent):
        """初始化简化图片尺寸调整"""
        self.parent = parent
        
        # 变量
        self.var_enable_resize = tk.BooleanVar(value=False)
        self.var_scale_percent = tk.IntVar(value=100)
        
        # 回调函数
        self.resize_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.var_enable_resize.trace('w', self.on_resize_change)
        self.var_scale_percent.trace('w', self.on_resize_change)
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)
        
        # 启用调整
        self.enable_check = ttk.Checkbutton(
            self.frame, text="调整尺寸",
            variable=self.var_enable_resize
        )
        self.enable_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # 百分比
        ttk.Label(self.frame, text="缩放:").pack(side=tk.LEFT)
        
        self.percent_spinbox = ttk.Spinbox(
            self.frame, from_=10, to=200, textvariable=self.var_scale_percent, width=6
        )
        self.percent_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(self.frame, text="%").pack(side=tk.LEFT, padx=(2, 0))
    
    def on_resize_change(self, *args):
        """调整改变"""
        if self.resize_change_callback:
            self.resize_change_callback(self.get_resize_config())
    
    def get_resize_config(self) -> dict:
        """获取调整配置"""
        return {
            'enabled': self.var_enable_resize.get(),
            'mode': '按百分比',
            'scale_percent': self.var_scale_percent.get(),
            'keep_aspect_ratio': True
        }
    
    def set_resize_change_callback(self, callback: Callable):
        """设置调整改变回调"""
        self.resize_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)