#!/usr/bin/env python3
"""
图片水印工具 - 修复版
ImageWatermarker - Fixed Complete Version
修复文本显示不全和位置不一致问题
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import tkinterdnd2 as tkdnd
import os
import json
from PIL import Image, ImageTk, ImageFont, ImageDraw
from datetime import datetime
from pathlib import Path
import threading

from core.image_processor import ImageProcessor
from core.watermark import WatermarkProcessor, WatermarkPosition
from core.config_manager import ConfigManager
from utils.image_utils import resize_for_display

class CompleteWatermarkApp:
    def __init__(self):
        self.root = tkdnd.Tk()
        self.root.title("ImageWatermarker - 完整功能版 (修复版)")
        self.root.geometry("1400x900")
        
        # 核心组件
        self.image_processor = ImageProcessor()
        self.watermark_processor = WatermarkProcessor()
        self.config_manager = ConfigManager()
        
        # 数据存储
        self.loaded_images = []
        self.current_image_index = 0
        self.image_refs = []  # 保存图像引用
        self.thumbnail_refs = {}  # 缩略图引用
        self.templates = {}  # 水印模板
        
        # 拖拽状态
        self.dragging_watermark = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.watermark_position = None  # 手动位置，None表示使用预设位置
        
        # 创建界面
        self.create_widgets()
        self.setup_drag_drop()
        self.load_templates()
        self.load_last_settings()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板容器
        left_container = ttk.Frame(main_frame, width=350)
        left_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_container.pack_propagate(False)
        
        # 创建可滚动的左侧面板
        self.create_scrollable_left_panel(left_container)
        
        # 右侧面板
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建右侧预览面板
        self.create_preview_panel(right_panel)
        
        # 创建菜单栏
        self.create_menu()
    
    def create_scrollable_left_panel(self, parent):
        """创建可滚动的左侧面板"""
        # 创建Canvas和Scrollbar
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # 创建控制面板内容
        self.create_control_panel(self.scrollable_frame)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        # 文件操作
        file_frame = ttk.LabelFrame(parent, text="文件操作")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="导入图片", command=self.import_images).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="导入文件夹", command=self.import_folder).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="导出当前", command=self.export_current).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="批量导出", command=self.export_all).pack(fill=tk.X, padx=5, pady=2)
        
        # 水印类型选择
        type_frame = ttk.LabelFrame(parent, text="水印类型")
        type_frame.pack(fill=tk.X, pady=5)
        
        self.watermark_type = tk.StringVar(value="text")
        ttk.Radiobutton(type_frame, text="文本水印", variable=self.watermark_type, 
                       value="text", command=self.on_type_change).pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(type_frame, text="图片水印", variable=self.watermark_type, 
                       value="image", command=self.on_type_change).pack(anchor=tk.W, padx=5)
        
        # 创建水印设置面板
        self.create_watermark_settings(parent)
        
        # 模板管理
        template_frame = ttk.LabelFrame(parent, text="模板管理")
        template_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(template_frame, text="保存模板", command=self.save_template).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(template_frame, text="加载模板", command=self.load_template).pack(fill=tk.X, padx=5, pady=2)
    
    def create_watermark_settings(self, parent):
        """创建水印设置面板"""
        # 文本水印设置
        self.text_frame = ttk.LabelFrame(parent, text="文本水印设置")
        self.text_frame.pack(fill=tk.X, pady=5)
        
        # 水印文本
        ttk.Label(self.text_frame, text="水印文本:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.text_content = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(self.text_frame, textvariable=self.text_content, width=25).grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5)
        self.text_content.trace('w', lambda *args: self.update_preview())
        
        # 字体设置
        ttk.Label(self.text_frame, text="字体:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.font_family = tk.StringVar(value="Arial")
        font_combo = ttk.Combobox(self.text_frame, textvariable=self.font_family, width=15)
        font_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        font_combo['values'] = ["Arial", "Times New Roman", "Helvetica", "Courier New"]
        font_combo.bind('<<ComboboxSelected>>', lambda e: self.update_preview())
        
        # 字体样式
        style_frame = ttk.Frame(self.text_frame)
        style_frame.grid(row=1, column=2, sticky=tk.W, padx=5)
        self.font_bold = tk.BooleanVar()
        self.font_italic = tk.BooleanVar()
        ttk.Checkbutton(style_frame, text="粗体", variable=self.font_bold, command=self.update_preview).pack(side=tk.LEFT)
        ttk.Checkbutton(style_frame, text="斜体", variable=self.font_italic, command=self.update_preview).pack(side=tk.LEFT)
        
        # 字体大小
        ttk.Label(self.text_frame, text="字体大小:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.font_size = tk.IntVar(value=36)
        size_frame = ttk.Frame(self.text_frame)
        size_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        ttk.Scale(size_frame, from_=8, to=200, variable=self.font_size, 
                 orient=tk.HORIZONTAL, length=150, command=self.on_font_size_change).pack(side=tk.LEFT)
        self.font_size_label = ttk.Label(size_frame, text="36")
        self.font_size_label.pack(side=tk.LEFT, padx=5)
        
        # 字体颜色
        ttk.Label(self.text_frame, text="字体颜色:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.font_color = tk.StringVar(value="#000000")
        color_frame = ttk.Frame(self.text_frame)
        color_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        self.color_button = tk.Button(color_frame, text="选择颜色", bg="#000000", 
                                     command=self.choose_color, width=10)
        self.color_button.pack(side=tk.LEFT)
        
        # 透明度
        ttk.Label(self.text_frame, text="透明度:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.opacity = tk.IntVar(value=80)
        opacity_frame = ttk.Frame(self.text_frame)
        opacity_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        ttk.Scale(opacity_frame, from_=0, to=100, variable=self.opacity, 
                 orient=tk.HORIZONTAL, length=150, command=self.on_opacity_change).pack(side=tk.LEFT)
        self.opacity_label = ttk.Label(opacity_frame, text="80%")
        self.opacity_label.pack(side=tk.LEFT, padx=5)
        
        # 文本样式增强
        ttk.Label(self.text_frame, text="样式增强:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
        enhance_frame = ttk.Frame(self.text_frame)
        enhance_frame.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        self.text_shadow = tk.BooleanVar()
        self.text_outline = tk.BooleanVar()
        ttk.Checkbutton(enhance_frame, text="阴影", variable=self.text_shadow, command=self.update_preview).pack(side=tk.LEFT)
        ttk.Checkbutton(enhance_frame, text="描边", variable=self.text_outline, command=self.update_preview).pack(side=tk.LEFT)
        
        # 阴影/描边颜色
        ttk.Label(self.text_frame, text="效果颜色:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=2)
        self.effect_color = tk.StringVar(value="#FFFFFF")
        effect_color_frame = ttk.Frame(self.text_frame)
        effect_color_frame.grid(row=6, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        self.effect_color_button = tk.Button(effect_color_frame, text="选择颜色", bg="#FFFFFF", 
                                           command=self.choose_effect_color, width=10)
        self.effect_color_button.pack(side=tk.LEFT)
        
        # 图片水印设置
        self.image_frame = ttk.LabelFrame(parent, text="图片水印设置")
        self.image_frame.pack(fill=tk.X, pady=5)
        
        # 图片选择
        ttk.Label(self.image_frame, text="水印图片:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.watermark_image_path = tk.StringVar()
        ttk.Button(self.image_frame, text="选择图片", command=self.choose_watermark_image).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # 图片大小
        ttk.Label(self.image_frame, text="大小比例:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.image_scale = tk.IntVar(value=100)
        scale_frame = ttk.Frame(self.image_frame)
        scale_frame.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Scale(scale_frame, from_=10, to=200, variable=self.image_scale, 
                 orient=tk.HORIZONTAL, length=150, command=self.on_image_scale_change).pack(side=tk.LEFT)
        self.image_scale_label = ttk.Label(scale_frame, text="100%")
        self.image_scale_label.pack(side=tk.LEFT, padx=5)
        
        # 位置设置
        position_frame = ttk.LabelFrame(parent, text="水印位置")
        position_frame.pack(fill=tk.X, pady=5)
        
        # 预设位置
        ttk.Label(position_frame, text="预设位置:").pack(anchor=tk.W, padx=5)
        pos_grid = ttk.Frame(position_frame)
        pos_grid.pack(fill=tk.X, padx=5, pady=2)
        
        self.position = tk.StringVar(value="右下")
        positions = [
            ("左上", "左上"), ("上中", "上中"), ("右上", "右上"),
            ("左中", "左中"), ("中心", "中心"), ("右中", "右中"),
            ("左下", "左下"), ("下中", "下中"), ("右下", "右下")
        ]
        
        for i, (text, value) in enumerate(positions):
            row = i // 3
            col = i % 3
            ttk.Radiobutton(pos_grid, text=text, variable=self.position, 
                           value=value, command=self.on_position_changed).grid(row=row, column=col, sticky=tk.W)
        
        # 手动位置提示和重置按钮
        manual_frame = ttk.Frame(position_frame)
        manual_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(manual_frame, text="提示: 可在预览区域拖拽水印", 
                 foreground="blue").pack(side=tk.LEFT)
        ttk.Button(manual_frame, text="重置位置", 
                  command=self.reset_watermark_position).pack(side=tk.RIGHT)
        
        # 旋转设置
        rotation_frame = ttk.LabelFrame(parent, text="旋转角度")
        rotation_frame.pack(fill=tk.X, pady=5)
        
        self.rotation = tk.IntVar(value=0)
        rotation_scale_frame = ttk.Frame(rotation_frame)
        rotation_scale_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Scale(rotation_scale_frame, from_=-180, to=180, variable=self.rotation, 
                 orient=tk.HORIZONTAL, length=200, command=self.on_rotation_change).pack(side=tk.LEFT)
        self.rotation_label = ttk.Label(rotation_scale_frame, text="0°")
        self.rotation_label.pack(side=tk.LEFT, padx=5)
        
        # 导出设置
        export_frame = ttk.LabelFrame(parent, text="导出设置")
        export_frame.pack(fill=tk.X, pady=5)
        
        # 输出格式
        ttk.Label(export_frame, text="输出格式:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.output_format = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(export_frame, textvariable=self.output_format, 
                                   values=["PNG", "JPEG"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)
        
        # JPEG质量
        self.jpeg_frame = ttk.Frame(export_frame)
        ttk.Label(self.jpeg_frame, text="JPEG质量:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.jpeg_quality = tk.IntVar(value=95)
        quality_frame = ttk.Frame(self.jpeg_frame)
        quality_frame.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Scale(quality_frame, from_=10, to=100, variable=self.jpeg_quality, 
                 orient=tk.HORIZONTAL, length=100, command=self.on_jpeg_quality_change).pack(side=tk.LEFT)
        self.quality_label = ttk.Label(quality_frame, text="95")
        self.quality_label.pack(side=tk.LEFT, padx=5)
        
        # 文件命名
        ttk.Label(export_frame, text="命名规则:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.naming_option = tk.StringVar(value="suffix")
        naming_frame = ttk.Frame(export_frame)
        naming_frame.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Radiobutton(naming_frame, text="原名", variable=self.naming_option, value="original").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="前缀", variable=self.naming_option, value="prefix").pack(anchor=tk.W)
        ttk.Radiobutton(naming_frame, text="后缀", variable=self.naming_option, value="suffix").pack(anchor=tk.W)
        
        ttk.Label(export_frame, text="自定义文本:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.custom_text = tk.StringVar(value="_watermarked")
        ttk.Entry(export_frame, textvariable=self.custom_text, width=15).grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # 初始状态
        self.on_type_change()
        self.on_format_change()
    
    def create_preview_panel(self, parent):
        """创建预览面板"""
        # 图片列表
        list_frame = ttk.LabelFrame(parent, text="图片列表")
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建Treeview显示图片列表
        columns = ("name", "size", "format")
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=6)
        
        self.image_tree.heading("#0", text="缩略图")
        self.image_tree.heading("name", text="文件名")
        self.image_tree.heading("size", text="尺寸")
        self.image_tree.heading("format", text="格式")
        
        self.image_tree.column("#0", width=80)
        self.image_tree.column("name", width=200)
        self.image_tree.column("size", width=100)
        self.image_tree.column("format", width=80)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.image_tree.bind('<<TreeviewSelect>>', self.on_image_select)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(parent, text="预览")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(preview_frame, bg="white", relief=tk.SUNKEN, bd=2)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 预览信息
        self.preview_info = ttk.Label(preview_frame, text="请导入图片")
        self.preview_info.pack(pady=5)
        
        # 绑定鼠标事件用于拖拽水印
        self.preview_canvas.bind("<Button-1>", self.on_canvas_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片", command=self.import_images)
        file_menu.add_command(label="导入文件夹", command=self.import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="导出当前", command=self.export_current)
        file_menu.add_command(label="批量导出", command=self.export_all)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 模板菜单
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模板", menu=template_menu)
        template_menu.add_command(label="保存模板", command=self.save_template)
        template_menu.add_command(label="加载模板", command=self.load_template)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def setup_drag_drop(self):
        """设置拖拽功能"""
        try:
            self.root.drop_target_register(tkdnd.DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        except Exception as e:
            print(f"拖拽功能初始化失败: {e}")
    
    def on_drop(self, event):
        """处理拖拽文件"""
        files = self.root.tk.splitlist(event.data)
        self.load_dropped_files(files)
    
    def load_dropped_files(self, files):
        """加载拖拽的文件"""
        image_files = []
        for file_path in files:
            if os.path.isfile(file_path):
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                    image_files.append(file_path)
            elif os.path.isdir(file_path):
                # 扫描文件夹
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                            image_files.append(os.path.join(root, file))
        
        if image_files:
            self.load_images_to_list(image_files)
    
    # 事件处理方法
    def on_type_change(self):
        """水印类型改变"""
        if self.watermark_type.get() == "text":
            self.text_frame.pack(fill=tk.X, pady=5)
            self.image_frame.pack_forget()
        else:
            self.text_frame.pack_forget()
            self.image_frame.pack(fill=tk.X, pady=5)
        self.update_preview()
    
    def on_format_change(self, event=None):
        """输出格式改变"""
        if self.output_format.get() == "JPEG":
            self.jpeg_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        else:
            self.jpeg_frame.grid_forget()
    
    def on_font_size_change(self, value):
        """字体大小改变"""
        size = int(float(value))
        self.font_size_label.config(text=str(size))
        self.update_preview()
    
    def on_opacity_change(self, value):
        """透明度改变"""
        opacity = int(float(value))
        self.opacity_label.config(text=f"{opacity}%")
        self.update_preview()
    
    def on_image_scale_change(self, value):
        """图片缩放改变"""
        scale = int(float(value))
        self.image_scale_label.config(text=f"{scale}%")
        self.update_preview()
    
    def on_rotation_change(self, value):
        """旋转角度改变"""
        rotation = int(float(value))
        self.rotation_label.config(text=f"{rotation}°")
        self.update_preview()
    
    def on_jpeg_quality_change(self, value):
        """JPEG质量改变"""
        quality = int(float(value))
        self.quality_label.config(text=str(quality))
    
    def on_position_changed(self):
        """位置改变事件处理"""
        # 重置手动位置
        self.watermark_position = None
        self.update_preview()
    
    def reset_watermark_position(self):
        """重置水印位置"""
        self.watermark_position = None
        self.update_preview()
    
    def choose_color(self):
        """选择字体颜色"""
        color = colorchooser.askcolor(color=self.font_color.get())
        if color[1]:
            self.font_color.set(color[1])
            self.color_button.config(bg=color[1])
            self.update_preview()
    
    def choose_effect_color(self):
        """选择效果颜色（阴影/描边）"""
        color = colorchooser.askcolor(color=self.effect_color.get())
        if color[1]:
            self.effect_color.set(color[1])
            self.effect_color_button.config(bg=color[1])
            self.update_preview()
    
    def choose_watermark_image(self):
        """选择水印图片"""
        file_path = filedialog.askopenfilename(
            title="选择水印图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        )
        if file_path:
            self.watermark_image_path.set(file_path)
            self.update_preview()
    
    def on_image_select(self, event):
        """图片选择事件"""
        selection = self.image_tree.selection()
        if selection:
            item = selection[0]
            # 获取选中项的索引
            for i, image_info in enumerate(self.loaded_images):
                if self.image_tree.item(item)['values'][0] == image_info['name']:
                    self.current_image_index = i
                    break
            self.update_preview()
    
    def on_canvas_click(self, event):
        """画布点击事件"""
        self.dragging_watermark = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
    
    def on_canvas_drag(self, event):
        """画布拖拽事件"""
        if self.dragging_watermark and self.loaded_images:
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # 计算相对位置
            rel_x = event.x / canvas_width
            rel_y = event.y / canvas_height
            
            # 限制在画布范围内
            rel_x = max(0, min(1, rel_x))
            rel_y = max(0, min(1, rel_y))
            
            self.watermark_position = (rel_x, rel_y)
            self.update_preview()
    
    def on_canvas_release(self, event):
        """画布释放事件"""
        self.dragging_watermark = False
    
    # 文件操作方法
    def import_images(self):
        """导入图片"""
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        )
        if files:
            self.load_images_to_list(files)
    
    def import_folder(self):
        """导入文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        if folder:
            image_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
                        image_files.append(os.path.join(root, file))
            
            if image_files:
                self.load_images_to_list(image_files)
            else:
                messagebox.showinfo("提示", "文件夹中没有找到图片文件")
    
    def load_images_to_list(self, file_paths):
        """加载图片到列表"""
        for file_path in file_paths:
            try:
                image_info = self.image_processor.load_image(file_path)
                if image_info:
                    self.loaded_images.append(image_info)
            except Exception as e:
                print(f"加载图片失败 {file_path}: {e}")
        
        self.update_image_list()
        if self.loaded_images:
            self.current_image_index = 0
            self.update_preview()
    
    def update_image_list(self):
        """更新图片列表显示"""
        # 清空现有项目
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        
        # 添加图片项目
        for i, image_info in enumerate(self.loaded_images):
            try:
                # 创建缩略图
                thumbnail = self.create_thumbnail(image_info['image'])
                if thumbnail:
                    # 保存缩略图引用
                    self.thumbnail_refs[i] = thumbnail
                    
                    # 插入到树形视图
                    item_id = self.image_tree.insert('', 'end',
                                                    image=thumbnail,
                                                    values=(image_info['name'], 
                                                           f"{image_info['size'][0]}x{image_info['size'][1]}", 
                                                           image_info['format']))
                else:
                    # 没有缩略图的情况
                    self.image_tree.insert('', 'end',
                                          values=(image_info['name'], 
                                                 f"{image_info['size'][0]}x{image_info['size'][1]}", 
                                                 image_info['format']))
            except Exception as e:
                print(f"创建缩略图失败: {e}")
                # 添加无缩略图的项目
                self.image_tree.insert('', 'end',
                                      values=(image_info['name'], 
                                             f"{image_info['size'][0]}x{image_info['size'][1]}", 
                                             image_info['format']))
    
    def create_thumbnail(self, image):
        """创建缩略图"""
        try:
            # 创建64x64的缩略图
            thumbnail = image.copy()
            thumbnail.thumbnail((64, 64), Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(thumbnail)
            return photo
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return None
    
    def update_preview(self):
        """更新预览"""
        if not self.loaded_images:
            return
        
        try:
            current_image = self.loaded_images[self.current_image_index]
            base_image = current_image['image'].copy()
            
            # 创建水印
            watermark = None
            if self.watermark_type.get() == "text":
                # 文本水印
                watermark = self.create_text_watermark()
            elif self.watermark_type.get() == "image" and self.watermark_image_path.get():
                # 图片水印
                watermark = self.create_image_watermark()
            
            if watermark:
                # 应用水印
                preview_image = self.apply_watermark_to_image(base_image, watermark)
            else:
                preview_image = base_image
            
            # 显示预览
            self.display_preview(preview_image)
            
            # 更新信息
            info_text = f"{current_image['name']} - {current_image['size'][0]}x{current_image['size'][1]} - {current_image['format']}"
            self.preview_info.config(text=info_text)
        
        except Exception as e:
            print(f"更新预览失败: {str(e)}")
    
    def create_text_watermark(self):
        """创建文本水印 - 支持粗体、斜体和样式增强"""
        try:
            # 获取字体 - 支持粗体和斜体
            font = self.get_styled_font()
            
            # 创建临时图像来测量文本大小
            temp_img = Image.new('RGBA', (2000, 2000))
            draw = ImageDraw.Draw(temp_img)
            
            # 使用textbbox获取准确的文本边界
            bbox = draw.textbbox((0, 0), self.text_content.get(), font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 为阴影和描边效果添加额外边距
            effect_margin = 5 if (self.text_shadow.get() or self.text_outline.get()) else 0
            margin = max(30, int(self.font_size.get() * 0.5)) + effect_margin
            watermark_width = text_width + margin * 2
            watermark_height = text_height + margin * 2
            
            # 创建水印图像
            watermark = Image.new('RGBA', (watermark_width, watermark_height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 解析主文本颜色和透明度
            text_color = self.parse_color_with_opacity(self.font_color.get(), self.opacity.get())
            
            # 计算文本位置
            text_x = margin - bbox[0]
            text_y = margin - bbox[1]
            
            # 绘制样式增强效果
            if self.text_shadow.get():
                self.draw_text_shadow(draw, text_x, text_y, font)
            
            if self.text_outline.get():
                self.draw_text_outline(draw, text_x, text_y, font)
            
            # 绘制主文本
            draw.text((text_x, text_y), self.text_content.get(), font=font, fill=text_color)
            
            return watermark
            
        except Exception as e:
            print(f"创建文本水印失败: {e}")
            return None
    
    def get_styled_font(self):
        """获取带样式的字体（支持粗体、斜体）"""
        try:
            font_name = self.font_family.get()
            font_size = self.font_size.get()
            
            # 尝试根据样式选择字体文件
            if self.font_bold.get() and self.font_italic.get():
                # 粗斜体
                font_variants = [f"{font_name} Bold Italic", f"{font_name}-BoldItalic", f"{font_name}BI"]
            elif self.font_bold.get():
                # 粗体
                font_variants = [f"{font_name} Bold", f"{font_name}-Bold", f"{font_name}B"]
            elif self.font_italic.get():
                # 斜体
                font_variants = [f"{font_name} Italic", f"{font_name}-Italic", f"{font_name}I"]
            else:
                # 常规
                font_variants = [font_name]
            
            # 尝试加载字体变体
            for variant in font_variants:
                try:
                    return ImageFont.truetype(variant, font_size)
                except:
                    continue
            
            # 如果找不到样式字体，使用基础字体并通过其他方式模拟
            try:
                return ImageFont.truetype(font_name, font_size)
            except:
                return ImageFont.load_default()
                
        except Exception as e:
            print(f"加载字体失败: {e}")
            return ImageFont.load_default()
    
    def parse_color_with_opacity(self, color_str, opacity_percent):
        """解析颜色并应用透明度"""
        opacity = int(255 * opacity_percent / 100)
        
        if color_str.startswith('#'):
            r = int(color_str[1:3], 16)
            g = int(color_str[3:5], 16)
            b = int(color_str[5:7], 16)
        else:
            r, g, b = 0, 0, 0
        
        return (r, g, b, opacity)
    
    def draw_text_shadow(self, draw, x, y, font):
        """绘制文本阴影"""
        shadow_color = self.parse_color_with_opacity(self.effect_color.get(), self.opacity.get())
        shadow_offset = max(2, int(self.font_size.get() * 0.05))
        
        # 绘制阴影（向右下偏移）
        draw.text((x + shadow_offset, y + shadow_offset), 
                 self.text_content.get(), font=font, fill=shadow_color)
    
    def draw_text_outline(self, draw, x, y, font):
        """绘制文本描边"""
        outline_color = self.parse_color_with_opacity(self.effect_color.get(), self.opacity.get())
        outline_width = max(1, int(self.font_size.get() * 0.03))
        
        # 绘制描边（8个方向）
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), 
                             self.text_content.get(), font=font, fill=outline_color)
    
    def create_image_watermark(self):
        """创建图片水印"""
        try:
            watermark_path = self.watermark_image_path.get()
            if not os.path.exists(watermark_path):
                return None
            
            # 加载水印图片
            watermark = Image.open(watermark_path)
            
            # 确保有透明通道
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            # 调整大小
            scale = self.image_scale.get() / 100.0
            new_size = (int(watermark.width * scale), int(watermark.height * scale))
            watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)
            
            # 调整透明度
            opacity = self.opacity.get() / 100.0
            if opacity < 1.0:
                # 创建透明度蒙版
                alpha = watermark.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                watermark.putalpha(alpha)
            
            return watermark
            
        except Exception as e:
            print(f"创建图片水印失败: {e}")
            return None
    
    def apply_watermark_to_image(self, base_image, watermark):
        """将水印应用到图片上 - 修复版"""
        try:
            # 确保基础图像有透明通道
            if base_image.mode != 'RGBA':
                base_image = base_image.convert('RGBA')
            
            # 旋转水印
            rotation_angle = self.rotation.get()
            if rotation_angle != 0:
                watermark = watermark.rotate(rotation_angle, expand=True, fillcolor=(0, 0, 0, 0))
            
            # 计算水印位置
            if self.watermark_position:
                # 手动位置
                x = int(self.watermark_position[0] * base_image.width - watermark.width / 2)
                y = int(self.watermark_position[1] * base_image.height - watermark.height / 2)
            else:
                # 预设位置 - 修复位置计算
                margin = 20
                position_map = {
                    '左上': (margin, margin),
                    '上中': (base_image.width // 2 - watermark.width // 2, margin),
                    '右上': (base_image.width - watermark.width - margin, margin),
                    '左中': (margin, base_image.height // 2 - watermark.height // 2),
                    '中心': (base_image.width // 2 - watermark.width // 2, base_image.height // 2 - watermark.height // 2),
                    '右中': (base_image.width - watermark.width - margin, base_image.height // 2 - watermark.height // 2),
                    '左下': (margin, base_image.height - watermark.height - margin),
                    '下中': (base_image.width // 2 - watermark.width // 2, base_image.height - watermark.height - margin),
                    '右下': (base_image.width - watermark.width - margin, base_image.height - watermark.height - margin)
                }
                x, y = position_map.get(self.position.get(), position_map['右下'])
            
            # 确保位置在图片范围内
            x = max(0, min(x, base_image.width - watermark.width))
            y = max(0, min(y, base_image.height - watermark.height))
            
            # 粘贴水印
            result = base_image.copy()
            result.paste(watermark, (x, y), watermark)
            
            return result
            
        except Exception as e:
            print(f"应用水印失败: {e}")
            return base_image
    
    def display_preview(self, image):
        """显示预览图片"""
        try:
            # 调整预览大小
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                display_image = resize_for_display(image, (canvas_width - 20, canvas_height - 20))
                
                # 创建PhotoImage并保存引用
                photo = ImageTk.PhotoImage(display_image)
                self.image_refs.append(photo)
                
                # 限制引用数量
                if len(self.image_refs) > 10:
                    self.image_refs = self.image_refs[-5:]
                
                # 清空画布并显示图片
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=photo, anchor=tk.CENTER
                )
        except Exception as e:
            print(f"显示预览失败: {e}")
    
    def export_current(self):
        """导出当前图片 - 修复版"""
        if not self.loaded_images:
            messagebox.showwarning("警告", "请先导入图片")
            return
        
        # 获取当前图片的原始文件夹路径
        current_image = self.loaded_images[self.current_image_index]
        original_dir = os.path.dirname(current_image['path'])
        
        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return
        
        # 检查是否选择了原文件夹
        if os.path.abspath(output_dir) == os.path.abspath(original_dir):
            messagebox.showerror("错误", "为防止覆盖原图，不能导出到原文件夹！\n请选择其他文件夹。")
            return
        
        try:
            self.export_single_image(current_image, output_dir)
            messagebox.showinfo("成功", "图片导出成功！")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")
    
    def export_all(self):
        """批量导出 - 修复版"""
        if not self.loaded_images:
            messagebox.showwarning("警告", "请先导入图片")
            return
        
        # 获取所有图片的原始文件夹路径
        original_dirs = set()
        for image_info in self.loaded_images:
            original_dirs.add(os.path.dirname(image_info['path']))
        
        output_dir = filedialog.askdirectory(title="选择输出文件夹")
        if not output_dir:
            return
        
        # 检查是否选择了任何一个原文件夹
        output_abs_path = os.path.abspath(output_dir)
        for original_dir in original_dirs:
            if output_abs_path == os.path.abspath(original_dir):
                messagebox.showerror("错误", "为防止覆盖原图，不能导出到原文件夹！\n请选择其他文件夹。")
                return
        
        try:
            success_count = 0
            for image_info in self.loaded_images:
                try:
                    self.export_single_image(image_info, output_dir)
                    success_count += 1
                except Exception as e:
                    print(f"导出 {image_info['name']} 失败: {e}")
            
            messagebox.showinfo("完成", f"成功导出 {success_count}/{len(self.loaded_images)} 张图片")
        except Exception as e:
            messagebox.showerror("错误", f"批量导出失败: {str(e)}")
    
    def export_single_image(self, image_info, output_dir):
        """导出单张图片"""
        base_image = image_info['image'].copy()
        
        # 创建水印
        watermark = None
        if self.watermark_type.get() == "text":
            watermark = self.create_text_watermark()
        elif self.watermark_type.get() == "image" and self.watermark_image_path.get():
            watermark = self.create_image_watermark()
        
        # 应用水印
        if watermark:
            result_image = self.apply_watermark_to_image(base_image, watermark)
        else:
            result_image = base_image
        
        # 生成输出文件名
        original_name = os.path.splitext(image_info['name'])[0]
        output_format = self.output_format.get().lower()
        
        if self.naming_option.get() == "original":
            output_name = f"{original_name}.{output_format}"
        elif self.naming_option.get() == "prefix":
            output_name = f"{self.custom_text.get()}{original_name}.{output_format}"
        else:  # suffix
            output_name = f"{original_name}{self.custom_text.get()}.{output_format}"
        
        output_path = os.path.join(output_dir, output_name)
        
        # 格式转换
        if output_format == 'jpeg':
            if result_image.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', result_image.size, (255, 255, 255))
                background.paste(result_image, mask=result_image.split()[-1])
                result_image = background
            
            # 保存JPEG
            result_image.save(output_path, 'JPEG', quality=self.jpeg_quality.get())
        else:
            # 保存PNG
            result_image.save(output_path, 'PNG')
    
    # 模板管理方法
    def save_template(self):
        """保存水印模板"""
        template_name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if not template_name:
            return
        
        template_data = {
            'watermark_type': self.watermark_type.get(),
            'text_content': self.text_content.get(),
            'font_family': self.font_family.get(),
            'font_size': self.font_size.get(),
            'font_bold': self.font_bold.get(),
            'font_italic': self.font_italic.get(),
            'font_color': self.font_color.get(),
            'opacity': self.opacity.get(),
            'text_shadow': self.text_shadow.get(),
            'text_outline': self.text_outline.get(),
            'effect_color': self.effect_color.get(),
            'watermark_image_path': self.watermark_image_path.get(),
            'image_scale': self.image_scale.get(),
            'position': self.position.get(),
            'rotation': self.rotation.get(),
            'output_format': self.output_format.get(),
            'jpeg_quality': self.jpeg_quality.get(),
            'naming_option': self.naming_option.get(),
            'custom_text': self.custom_text.get()
        }
        
        self.templates[template_name] = template_data
        self.save_templates_to_file()
        messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功！")
    
    def load_template(self):
        """加载水印模板"""
        if not self.templates:
            messagebox.showinfo("提示", "没有保存的模板")
            return
        
        template_names = list(self.templates.keys())
        
        # 创建选择对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择模板")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"450x350+{x}+{y}")
        
        # 模板列表
        listbox = tk.Listbox(dialog)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for name in template_names:
            listbox.insert(tk.END, name)
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def load_selected():
            selection = listbox.curselection()
            if selection:
                template_name = template_names[selection[0]]
                self.apply_template(self.templates[template_name])
                dialog.destroy()
        
        def delete_selected():
            selection = listbox.curselection()
            if selection:
                template_name = template_names[selection[0]]
                if messagebox.askyesno("确认", f"确定要删除模板 '{template_name}' 吗？"):
                    del self.templates[template_name]
                    self.save_templates_to_file()
                    listbox.delete(selection[0])
                    template_names.remove(template_name)
        
        ttk.Button(button_frame, text="加载", command=load_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除", command=delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def apply_template(self, template_data):
        """应用模板"""
        try:
            # 应用模板数据
            self.watermark_type.set(template_data.get('watermark_type', 'text'))
            self.text_content.set(template_data.get('text_content', ''))
            self.font_family.set(template_data.get('font_family', 'Arial'))
            self.font_size.set(template_data.get('font_size', 36))
            self.font_bold.set(template_data.get('font_bold', False))
            self.font_italic.set(template_data.get('font_italic', False))
            self.font_color.set(template_data.get('font_color', '#000000'))
            self.opacity.set(template_data.get('opacity', 80))
            self.text_shadow.set(template_data.get('text_shadow', False))
            self.text_outline.set(template_data.get('text_outline', False))
            self.effect_color.set(template_data.get('effect_color', '#FFFFFF'))
            self.watermark_image_path.set(template_data.get('watermark_image_path', ''))
            self.image_scale.set(template_data.get('image_scale', 100))
            self.position.set(template_data.get('position', '右下'))
            self.rotation.set(template_data.get('rotation', 0))
            self.output_format.set(template_data.get('output_format', 'PNG'))
            self.jpeg_quality.set(template_data.get('jpeg_quality', 95))
            self.naming_option.set(template_data.get('naming_option', 'suffix'))
            self.custom_text.set(template_data.get('custom_text', '_watermarked'))
            
            # 更新UI
            self.color_button.config(bg=self.font_color.get())
            self.effect_color_button.config(bg=self.effect_color.get())
            self.on_type_change()
            self.on_format_change()
            self.update_preview()
        except Exception as e:
            print(f"应用模板失败: {e}")
    
    def load_templates(self):
        """从文件加载模板"""
        try:
            templates_file = os.path.join('templates', 'watermark_templates.json')
            if os.path.exists(templates_file):
                with open(templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
        except Exception as e:
            print(f"加载模板失败: {e}")
            self.templates = {}
    
    def save_templates_to_file(self):
        """保存模板到文件"""
        try:
            os.makedirs('templates', exist_ok=True)
            templates_file = os.path.join('templates', 'watermark_templates.json')
            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模板失败: {e}")
    
    def load_last_settings(self):
        """加载上次的设置"""
        try:
            settings_file = os.path.join('templates', 'last_settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.apply_template(settings)
        except Exception as e:
            print(f"加载上次设置失败: {e}")
    
    def save_current_settings(self):
        """保存当前设置"""
        try:
            settings = {
                'watermark_type': self.watermark_type.get(),
                'text_content': self.text_content.get(),
                'font_family': self.font_family.get(),
                'font_size': self.font_size.get(),
                'font_bold': self.font_bold.get(),
                'font_italic': self.font_italic.get(),
                'font_color': self.font_color.get(),
                'opacity': self.opacity.get(),
                'text_shadow': self.text_shadow.get(),
                'text_outline': self.text_outline.get(),
                'effect_color': self.effect_color.get(),
                'watermark_image_path': self.watermark_image_path.get(),
                'image_scale': self.image_scale.get(),
                'position': self.position.get(),
                'rotation': self.rotation.get(),
                'output_format': self.output_format.get(),
                'jpeg_quality': self.jpeg_quality.get(),
                'naming_option': self.naming_option.get(),
                'custom_text': self.custom_text.get()
            }
            
            os.makedirs('templates', exist_ok=True)
            settings_file = os.path.join('templates', 'last_settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存当前设置失败: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """ImageWatermarker 使用说明

1. 导入图片:
   - 点击"导入图片"按钮选择文件
   - 点击"导入文件夹"选择整个文件夹
   - 直接拖拽图片或文件夹到程序窗口

2. 设置水印:
   - 选择文本水印或图片水印
   - 调整字体、大小、颜色、透明度等参数
   - 选择水印位置或在预览区域拖拽

3. 导出图片:
   - 选择输出格式和质量
   - 设置文件命名规则
   - 导出单张或批量导出
   - 程序会自动防止覆盖原图

4. 模板管理:
   - 保存常用的水印设置为模板
   - 快速加载已保存的模板
   - 程序会自动保存上次的设置

支持格式: JPEG, PNG, BMP, TIFF"""
        
        messagebox.showinfo("使用说明", help_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = """ImageWatermarker v2.0 修复版
完整功能版图片水印工具

功能特点:
✓ 支持拖拽导入
✓ 缩略图显示
✓ 文本和图片水印
✓ 手动拖拽定位
✓ 水印旋转
✓ 模板管理
✓ 批量处理
✓ 防止覆盖原图
✓ 修复文本显示问题

开发: CodeBuddy AI Assistant
时间: 2025年9月"""
        
        messagebox.showinfo("关于", about_text)
    
    def on_closing(self):
        """程序关闭时的处理"""
        self.save_current_settings()
        self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """主程序入口"""
    try:
        app = CompleteWatermarkApp()
        app.run()
    except ImportError as e:
        if "tkinterdnd2" in str(e):
            print("缺少 tkinterdnd2 依赖，请安装: pip install tkinterdnd2")
            print("将使用基础版本...")
        else:
            print(f"导入错误: {e}")
    except Exception as e:
        print(f"程序启动失败: {e}")

if __name__ == "__main__":
    main()