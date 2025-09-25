"""
文本效果模块
支持阴影和描边效果
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont


class TextEffectsControl:
    """文本效果控制器"""
    
    def __init__(self, parent):
        """
        初始化文本效果控制器
        
        Args:
            parent: 父控件
        """
        self.parent = parent
        
        # 变量
        self.var_enable_shadow = tk.BooleanVar(value=False)
        self.var_shadow_offset_x = tk.IntVar(value=2)
        self.var_shadow_offset_y = tk.IntVar(value=2)
        self.var_shadow_color = tk.StringVar(value="#808080")
        self.var_shadow_opacity = tk.IntVar(value=128)
        
        self.var_enable_stroke = tk.BooleanVar(value=False)
        self.var_stroke_width = tk.IntVar(value=1)
        self.var_stroke_color = tk.StringVar(value="#FFFFFF")
        
        # 回调函数
        self.effects_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="文本效果", padding="10")
        
        # 阴影效果
        self.shadow_frame = ttk.LabelFrame(self.frame, text="阴影效果", padding="5")
        self.shadow_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 启用阴影
        self.shadow_check = ttk.Checkbutton(
            self.shadow_frame, text="启用阴影",
            variable=self.var_enable_shadow
        )
        self.shadow_check.pack(anchor=tk.W, pady=(0, 5))
        
        # 阴影偏移
        offset_frame = ttk.Frame(self.shadow_frame)
        offset_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(offset_frame, text="偏移X:").grid(row=0, column=0, sticky=tk.W)
        self.shadow_x_spinbox = ttk.Spinbox(
            offset_frame, from_=-10, to=10, textvariable=self.var_shadow_offset_x, width=6
        )
        self.shadow_x_spinbox.grid(row=0, column=1, padx=(5, 10), sticky=tk.W)
        
        ttk.Label(offset_frame, text="偏移Y:").grid(row=0, column=2, sticky=tk.W)
        self.shadow_y_spinbox = ttk.Spinbox(
            offset_frame, from_=-10, to=10, textvariable=self.var_shadow_offset_y, width=6
        )
        self.shadow_y_spinbox.grid(row=0, column=3, padx=(5, 0), sticky=tk.W)
        
        # 阴影颜色
        shadow_color_frame = ttk.Frame(self.shadow_frame)
        shadow_color_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(shadow_color_frame, text="颜色:").pack(side=tk.LEFT)
        
        self.shadow_color_display = tk.Frame(
            shadow_color_frame, width=25, height=20,
            bg=self.var_shadow_color.get(), relief=tk.RAISED, bd=1
        )
        self.shadow_color_display.pack(side=tk.LEFT, padx=(5, 10))
        self.shadow_color_display.pack_propagate(False)
        
        ttk.Button(
            shadow_color_frame, text="选择",
            command=self.choose_shadow_color
        ).pack(side=tk.LEFT)
        
        # 阴影透明度
        shadow_opacity_frame = ttk.Frame(self.shadow_frame)
        shadow_opacity_frame.pack(fill=tk.X)
        
        ttk.Label(shadow_opacity_frame, text="透明度:").pack(side=tk.LEFT)
        
        self.shadow_opacity_scale = ttk.Scale(
            shadow_opacity_frame, from_=0, to=255, variable=self.var_shadow_opacity,
            orient=tk.HORIZONTAL, length=100
        )
        self.shadow_opacity_scale.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        self.shadow_opacity_label = ttk.Label(shadow_opacity_frame, text="128")
        self.shadow_opacity_label.pack(side=tk.RIGHT)
        
        # 描边效果
        self.stroke_frame = ttk.LabelFrame(self.frame, text="描边效果", padding="5")
        self.stroke_frame.pack(fill=tk.X)
        
        # 启用描边
        self.stroke_check = ttk.Checkbutton(
            self.stroke_frame, text="启用描边",
            variable=self.var_enable_stroke
        )
        self.stroke_check.pack(anchor=tk.W, pady=(0, 5))
        
        # 描边宽度
        stroke_width_frame = ttk.Frame(self.stroke_frame)
        stroke_width_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(stroke_width_frame, text="宽度:").pack(side=tk.LEFT)
        
        self.stroke_width_spinbox = ttk.Spinbox(
            stroke_width_frame, from_=1, to=10, textvariable=self.var_stroke_width, width=6
        )
        self.stroke_width_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 描边颜色
        stroke_color_frame = ttk.Frame(self.stroke_frame)
        stroke_color_frame.pack(fill=tk.X)
        
        ttk.Label(stroke_color_frame, text="颜色:").pack(side=tk.LEFT)
        
        self.stroke_color_display = tk.Frame(
            stroke_color_frame, width=25, height=20,
            bg=self.var_stroke_color.get(), relief=tk.RAISED, bd=1
        )
        self.stroke_color_display.pack(side=tk.LEFT, padx=(5, 10))
        self.stroke_color_display.pack_propagate(False)
        
        ttk.Button(
            stroke_color_frame, text="选择",
            command=self.choose_stroke_color
        ).pack(side=tk.LEFT)
        
        # 初始状态
        self.update_widget_states()
    
    def bind_events(self):
        """绑定事件"""
        self.var_enable_shadow.trace('w', self.on_effects_change)
        self.var_shadow_offset_x.trace('w', self.on_effects_change)
        self.var_shadow_offset_y.trace('w', self.on_effects_change)
        self.var_shadow_opacity.trace('w', self.on_shadow_opacity_change)
        
        self.var_enable_stroke.trace('w', self.on_effects_change)
        self.var_stroke_width.trace('w', self.on_effects_change)
        
        # 启用状态改变
        self.var_enable_shadow.trace('w', self.on_enable_change)
        self.var_enable_stroke.trace('w', self.on_enable_change)
    
    def on_enable_change(self, *args):
        """启用状态改变"""
        self.update_widget_states()
        self.on_effects_change()
    
    def on_effects_change(self, *args):
        """效果改变"""
        if self.effects_change_callback:
            self.effects_change_callback(self.get_effects_config())
    
    def on_shadow_opacity_change(self, *args):
        """阴影透明度改变"""
        opacity = self.var_shadow_opacity.get()
        self.shadow_opacity_label.configure(text=str(opacity))
        self.on_effects_change()
    
    def update_widget_states(self):
        """更新控件状态"""
        # 阴影控件状态
        shadow_enabled = self.var_enable_shadow.get()
        shadow_state = "normal" if shadow_enabled else "disabled"
        
        self.shadow_x_spinbox.configure(state=shadow_state)
        self.shadow_y_spinbox.configure(state=shadow_state)
        self.shadow_opacity_scale.configure(state=shadow_state)
        
        # 描边控件状态
        stroke_enabled = self.var_enable_stroke.get()
        stroke_state = "normal" if stroke_enabled else "disabled"
        
        self.stroke_width_spinbox.configure(state=stroke_state)
    
    def choose_shadow_color(self):
        """选择阴影颜色"""
        from tkinter import colorchooser
        
        color = colorchooser.askcolor(
            color=self.var_shadow_color.get(),
            title="选择阴影颜色"
        )
        
        if color[1]:
            self.var_shadow_color.set(color[1])
            self.shadow_color_display.configure(bg=color[1])
            self.on_effects_change()
    
    def choose_stroke_color(self):
        """选择描边颜色"""
        from tkinter import colorchooser
        
        color = colorchooser.askcolor(
            color=self.var_stroke_color.get(),
            title="选择描边颜色"
        )
        
        if color[1]:
            self.var_stroke_color.set(color[1])
            self.stroke_color_display.configure(bg=color[1])
            self.on_effects_change()
    
    def get_effects_config(self) -> dict:
        """获取效果配置"""
        return {
            'shadow': {
                'enabled': self.var_enable_shadow.get(),
                'offset_x': self.var_shadow_offset_x.get(),
                'offset_y': self.var_shadow_offset_y.get(),
                'color': self.var_shadow_color.get(),
                'opacity': self.var_shadow_opacity.get()
            },
            'stroke': {
                'enabled': self.var_enable_stroke.get(),
                'width': self.var_stroke_width.get(),
                'color': self.var_stroke_color.get()
            }
        }
    
    def set_effects_config(self, config: dict):
        """设置效果配置"""
        if 'shadow' in config:
            shadow_config = config['shadow']
            self.var_enable_shadow.set(shadow_config.get('enabled', False))
            self.var_shadow_offset_x.set(shadow_config.get('offset_x', 2))
            self.var_shadow_offset_y.set(shadow_config.get('offset_y', 2))
            self.var_shadow_color.set(shadow_config.get('color', '#808080'))
            self.var_shadow_opacity.set(shadow_config.get('opacity', 128))
            
            # 更新颜色显示
            self.shadow_color_display.configure(bg=self.var_shadow_color.get())
        
        if 'stroke' in config:
            stroke_config = config['stroke']
            self.var_enable_stroke.set(stroke_config.get('enabled', False))
            self.var_stroke_width.set(stroke_config.get('width', 1))
            self.var_stroke_color.set(stroke_config.get('color', '#FFFFFF'))
            
            # 更新颜色显示
            self.stroke_color_display.configure(bg=self.var_stroke_color.get())
        
        self.update_widget_states()
    
    def set_effects_change_callback(self, callback: Callable):
        """设置效果改变回调"""
        self.effects_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)


class TextEffectsRenderer:
    """文本效果渲染器"""
    
    @staticmethod
    def render_text_with_effects(image: Image.Image, text: str, font: ImageFont.FreeTypeFont,
                                color: tuple, position: tuple, effects_config: dict) -> Image.Image:
        """
        渲染带效果的文本
        
        Args:
            image: 原图
            text: 文本内容
            font: 字体
            color: 文本颜色
            position: 位置
            effects_config: 效果配置
            
        Returns:
            处理后的图片
        """
        result = image.copy()
        
        # 获取文本尺寸
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算需要的画布大小（考虑效果扩展）
        shadow_config = effects_config.get('shadow', {})
        stroke_config = effects_config.get('stroke', {})
        
        extra_width = 0
        extra_height = 0
        
        if shadow_config.get('enabled', False):
            extra_width = max(extra_width, abs(shadow_config.get('offset_x', 0)))
            extra_height = max(extra_height, abs(shadow_config.get('offset_y', 0)))
        
        if stroke_config.get('enabled', False):
            stroke_width = stroke_config.get('width', 1)
            extra_width = max(extra_width, stroke_width)
            extra_height = max(extra_height, stroke_width)
        
        # 创建文本图像
        canvas_width = text_width + extra_width * 4
        canvas_height = text_height + extra_height * 4
        text_img = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)
        
        # 文本在画布中的位置
        text_x = extra_width * 2
        text_y = extra_height * 2
        
        # 绘制阴影
        if shadow_config.get('enabled', False):
            shadow_x = text_x + shadow_config.get('offset_x', 2)
            shadow_y = text_y + shadow_config.get('offset_y', 2)
            shadow_color_hex = shadow_config.get('color', '#808080')
            shadow_opacity = shadow_config.get('opacity', 128)
            
            # 转换阴影颜色
            shadow_rgb = TextEffectsRenderer.hex_to_rgb(shadow_color_hex)
            shadow_color_rgba = shadow_rgb + (shadow_opacity,)
            
            draw.text((shadow_x, shadow_y), text, font=font, fill=shadow_color_rgba)
        
        # 绘制描边
        if stroke_config.get('enabled', False):
            stroke_width = stroke_config.get('width', 1)
            stroke_color_hex = stroke_config.get('color', '#FFFFFF')
            stroke_rgb = TextEffectsRenderer.hex_to_rgb(stroke_color_hex)
            stroke_color_rgba = stroke_rgb + (255,)
            
            # 绘制描边（通过在周围绘制多次文本实现）
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), text, font=font, fill=stroke_color_rgba)
        
        # 绘制主文本
        draw.text((text_x, text_y), text, font=font, fill=color)
        
        # 计算粘贴位置
        paste_x = position[0] - extra_width * 2
        paste_y = position[1] - extra_height * 2
        
        # 粘贴到结果图像
        result.paste(text_img, (paste_x, paste_y), text_img)
        
        return result
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> tuple:
        """十六进制转RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


class SimpleTextEffects:
    """简化的文本效果控制"""
    
    def __init__(self, parent):
        """初始化简化文本效果控制"""
        self.parent = parent
        
        # 变量
        self.var_enable_shadow = tk.BooleanVar(value=False)
        self.var_enable_stroke = tk.BooleanVar(value=False)
        
        # 回调函数
        self.effects_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.var_enable_shadow.trace('w', self.on_effects_change)
        self.var_enable_stroke.trace('w', self.on_effects_change)
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)
        
        # 效果选项
        self.shadow_check = ttk.Checkbutton(
            self.frame, text="阴影效果",
            variable=self.var_enable_shadow
        )
        self.shadow_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stroke_check = ttk.Checkbutton(
            self.frame, text="描边效果",
            variable=self.var_enable_stroke
        )
        self.stroke_check.pack(side=tk.LEFT)
    
    def on_effects_change(self, *args):
        """效果改变"""
        if self.effects_change_callback:
            self.effects_change_callback(self.get_effects_config())
    
    def get_effects_config(self) -> dict:
        """获取效果配置"""
        return {
            'shadow': {
                'enabled': self.var_enable_shadow.get(),
                'offset_x': 2,
                'offset_y': 2,
                'color': '#808080',
                'opacity': 128
            },
            'stroke': {
                'enabled': self.var_enable_stroke.get(),
                'width': 1,
                'color': '#FFFFFF'
            }
        }
    
    def set_effects_change_callback(self, callback: Callable):
        """设置效果改变回调"""
        self.effects_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)