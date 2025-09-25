"""
手动定位模块
支持在预览画布上拖拽水印位置
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple
from PIL import Image, ImageTk


class ManualPositioningCanvas:
    """手动定位画布"""
    
    def __init__(self, parent):
        """
        初始化手动定位画布
        
        Args:
            parent: 父控件
        """
        self.parent = parent
        
        # 画布变量
        self.canvas_width = 600
        self.canvas_height = 400
        
        # 图片相关
        self.original_image = None
        self.display_image = None
        self.image_item = None
        self.scale_factor = 1.0
        self.image_offset = (0, 0)
        
        # 水印相关
        self.watermark_item = None
        self.watermark_position = (0, 0)
        self.is_dragging = False
        self.drag_start = (0, 0)
        
        # 回调函数
        self.position_change_callback: Optional[Callable[[Tuple[int, int]], None]] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
    
    def create_widgets(self):
        """创建界面控件"""
        # 画布容器
        canvas_frame = ttk.Frame(self.parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建画布
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            relief=tk.SUNKEN,
            bd=1
        )
        
        # 滚动条
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # 布局
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        h_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        v_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # 控制按钮
        control_frame = ttk.Frame(self.parent)
        control_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(control_frame, text="适应窗口", command=self.fit_to_window).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="实际尺寸", command=self.actual_size).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="放大", command=self.zoom_in).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="缩小", command=self.zoom_out).pack(side=tk.LEFT)
        
        # 显示提示
        self.show_placeholder()
    
    def bind_events(self):
        """绑定事件"""
        # 鼠标事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        # 滚轮缩放
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Button-4>', self.on_mousewheel)  # Linux
        self.canvas.bind('<Button-5>', self.on_mousewheel)  # Linux
        
        # 窗口大小改变
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def show_placeholder(self):
        """显示占位符"""
        self.canvas.delete("all")
        
        # 绘制占位符
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2
        
        self.canvas.create_rectangle(
            center_x - 100, center_y - 50,
            center_x + 100, center_y + 50,
            outline='gray', fill='lightgray', dash=(5, 5)
        )
        
        self.canvas.create_text(
            center_x, center_y,
            text="请选择图片进行预览\n支持拖拽调整水印位置",
            fill='gray', justify=tk.CENTER
        )
    
    def set_image(self, image: Image.Image):
        """
        设置要显示的图片
        
        Args:
            image: PIL图片对象
        """
        self.original_image = image.copy()
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        if not self.original_image:
            self.show_placeholder()
            return
        
        # 清空画布
        self.canvas.delete("all")
        
        # 计算显示尺寸
        img_width, img_height = self.original_image.size
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        # 调整图片尺寸
        if self.scale_factor != 1.0:
            display_image = self.original_image.resize(
                (display_width, display_height),
                Image.Resampling.LANCZOS
            )
        else:
            display_image = self.original_image
        
        # 转换为tkinter格式
        self.display_image = ImageTk.PhotoImage(display_image)
        
        # 计算图片位置（居中）
        canvas_center_x = self.canvas_width // 2
        canvas_center_y = self.canvas_height // 2
        
        image_x = canvas_center_x - display_width // 2 + self.image_offset[0]
        image_y = canvas_center_y - display_height // 2 + self.image_offset[1]
        
        # 显示图片
        self.image_item = self.canvas.create_image(
            image_x, image_y,
            anchor=tk.NW,
            image=self.display_image
        )
        
        # 更新滚动区域
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # 绘制水印位置指示器（如果有的话）
        self.update_watermark_indicator()
    
    def update_watermark_indicator(self):
        """更新水印位置指示器"""
        if not self.original_image:
            return
        
        # 删除旧的指示器
        if self.watermark_item:
            self.canvas.delete(self.watermark_item)
        
        # 计算水印在画布上的位置
        img_width, img_height = self.original_image.size
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        canvas_center_x = self.canvas_width // 2
        canvas_center_y = self.canvas_height // 2
        
        image_x = canvas_center_x - display_width // 2 + self.image_offset[0]
        image_y = canvas_center_y - display_height // 2 + self.image_offset[1]
        
        # 水印在图片上的相对位置转换为画布坐标
        watermark_x = image_x + int(self.watermark_position[0] * self.scale_factor)
        watermark_y = image_y + int(self.watermark_position[1] * self.scale_factor)
        
        # 绘制水印指示器
        indicator_size = 10
        self.watermark_item = self.canvas.create_rectangle(
            watermark_x - indicator_size, watermark_y - indicator_size,
            watermark_x + indicator_size, watermark_y + indicator_size,
            outline='red', width=2, dash=(3, 3)
        )
        
        # 添加标签
        self.canvas.create_text(
            watermark_x, watermark_y - indicator_size - 10,
            text="水印位置", fill='red', font=('Arial', 8)
        )
    
    def on_click(self, event):
        """鼠标点击事件"""
        if not self.original_image:
            return
        
        # 检查是否点击在图片区域内
        if self.is_point_on_image(event.x, event.y):
            self.is_dragging = True
            self.drag_start = (event.x, event.y)
            
            # 计算点击位置在原图上的坐标
            image_pos = self.canvas_to_image_coords(event.x, event.y)
            if image_pos:
                self.watermark_position = image_pos
                self.update_watermark_indicator()
    
    def on_drag(self, event):
        """鼠标拖拽事件"""
        if not self.is_dragging or not self.original_image:
            return
        
        # 计算新的水印位置
        image_pos = self.canvas_to_image_coords(event.x, event.y)
        if image_pos:
            self.watermark_position = image_pos
            self.update_watermark_indicator()
    
    def on_release(self, event):
        """鼠标释放事件"""
        if self.is_dragging:
            self.is_dragging = False
            
            # 触发位置改变回调
            if self.position_change_callback:
                self.position_change_callback(self.watermark_position)
    
    def is_point_on_image(self, canvas_x: int, canvas_y: int) -> bool:
        """检查点是否在图片区域内"""
        if not self.original_image:
            return False
        
        # 计算图片在画布上的边界
        img_width, img_height = self.original_image.size
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        canvas_center_x = self.canvas_width // 2
        canvas_center_y = self.canvas_height // 2
        
        image_left = canvas_center_x - display_width // 2 + self.image_offset[0]
        image_top = canvas_center_y - display_height // 2 + self.image_offset[1]
        image_right = image_left + display_width
        image_bottom = image_top + display_height
        
        return (image_left <= canvas_x <= image_right and 
                image_top <= canvas_y <= image_bottom)
    
    def canvas_to_image_coords(self, canvas_x: int, canvas_y: int) -> Optional[Tuple[int, int]]:
        """将画布坐标转换为图片坐标"""
        if not self.original_image:
            return None
        
        # 计算图片在画布上的位置
        img_width, img_height = self.original_image.size
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        canvas_center_x = self.canvas_width // 2
        canvas_center_y = self.canvas_height // 2
        
        image_left = canvas_center_x - display_width // 2 + self.image_offset[0]
        image_top = canvas_center_y - display_height // 2 + self.image_offset[1]
        
        # 转换为图片坐标
        relative_x = canvas_x - image_left
        relative_y = canvas_y - image_top
        
        # 缩放到原图尺寸
        image_x = int(relative_x / self.scale_factor)
        image_y = int(relative_y / self.scale_factor)
        
        # 确保坐标在图片范围内
        image_x = max(0, min(image_x, img_width - 1))
        image_y = max(0, min(image_y, img_height - 1))
        
        return (image_x, image_y)
    
    def on_mousewheel(self, event):
        """鼠标滚轮事件（缩放）"""
        if not self.original_image:
            return
        
        # 确定缩放方向
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        else:
            self.zoom_out()
    
    def on_canvas_configure(self, event):
        """画布大小改变事件"""
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.update_display()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self.original_image:
            return
        
        img_width, img_height = self.original_image.size
        
        # 计算缩放比例
        width_ratio = (self.canvas_width - 20) / img_width
        height_ratio = (self.canvas_height - 20) / img_height
        
        self.scale_factor = min(width_ratio, height_ratio, 1.0)
        self.image_offset = (0, 0)
        
        self.update_display()
    
    def actual_size(self):
        """实际尺寸显示"""
        self.scale_factor = 1.0
        self.image_offset = (0, 0)
        self.update_display()
    
    def zoom_in(self):
        """放大"""
        self.scale_factor = min(self.scale_factor * 1.2, 5.0)
        self.update_display()
    
    def zoom_out(self):
        """缩小"""
        self.scale_factor = max(self.scale_factor / 1.2, 0.1)
        self.update_display()
    
    def set_watermark_position(self, position: Tuple[int, int]):
        """设置水印位置"""
        self.watermark_position = position
        self.update_watermark_indicator()
    
    def get_watermark_position(self) -> Tuple[int, int]:
        """获取水印位置"""
        return self.watermark_position
    
    def set_position_change_callback(self, callback: Callable[[Tuple[int, int]], None]):
        """设置位置改变回调"""
        self.position_change_callback = callback
    
    def clear_canvas(self):
        """清空画布"""
        self.original_image = None
        self.display_image = None
        self.image_item = None
        self.watermark_item = None
        self.watermark_position = (0, 0)
        self.show_placeholder()
    
    def pack(self, **kwargs):
        """打包控件"""
        # 这个方法由父类调用，实际上控件已经在__init__中布局了
        pass
    
    def grid(self, **kwargs):
        """网格布局控件"""
        # 这个方法由父类调用，实际上控件已经在__init__中布局了
        pass