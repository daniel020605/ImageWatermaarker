"""
主窗口模块 - 鲁棒性增强版本
应用程序的主界面，包含完整的输入验证和错误处理
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
from datetime import datetime
import threading

from core.image_processor import ImageProcessor
from core.watermark import WatermarkProcessor, WatermarkPosition
from core.config_manager import ConfigManager
from utils.file_utils import validate_output_directory
from utils.image_utils import pil_to_tkinter, resize_for_display
from utils.input_validation import InputValidator


class MainWindow:
    """主窗口类 - 鲁棒性增强版本"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ImageWatermarker - 图片水印工具 (增强版)")
        self.root.geometry("1400x900")
        
        # 核心组件
        self.image_processor = ImageProcessor()
        self.watermark_processor = WatermarkProcessor()
        self.config_manager = ConfigManager()
        
        # 数据存储
        self.current_images = []
        self.current_image_index = 0
        self.preview_image = None
        
        # 设置变量
        self.setup_variables()
        
        # 创建界面
        self.create_widgets()
        
        # 设置输入验证
        self.setup_input_validation()
        
        # 初始化水印类型显示
        self.on_watermark_type_change()
    
    def setup_variables(self):
        """设置GUI变量"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 水印类型和文本设置
        self.var_watermark_type = tk.StringVar(value="文本")
        self.var_watermark_text = tk.StringVar(value=current_date)
        self.var_font_size = tk.IntVar(value=48)
        self.var_font_color = tk.StringVar(value="#000000")
        self.var_opacity = tk.IntVar(value=128)
        
        # 图片水印设置
        self.var_watermark_image_path = tk.StringVar()
        self.var_image_scale = tk.IntVar(value=100)
        self.var_image_opacity = tk.IntVar(value=128)
        
        # 位置设置
        self.var_position = tk.StringVar(value="右下")
        
        # 导出设置
        self.var_output_dir = tk.StringVar()
        self.var_output_format = tk.StringVar(value="JPEG")
        self.var_quality = tk.IntVar(value=95)
    
    def setup_input_validation(self):
        """设置输入验证"""
        # 字体大小验证 (8-1000)
        def validate_font_size():
            try:
                current_value = self.font_size_entry.get()
                validated_value = InputValidator.validate_font_size(current_value, 48)
                if str(validated_value) != current_value:
                    self.var_font_size.set(validated_value)
                self.on_watermark_change()
            except Exception as e:
                print(f"字体大小验证错误: {e}")
        
        # 绑定字体大小输入框验证
        self.font_size_entry.bind('<KeyRelease>', lambda e: validate_font_size())
        self.font_size_entry.bind('<FocusOut>', lambda e: validate_font_size())
        
        # 透明度验证
        def validate_opacity(*args):
            try:
                opacity = InputValidator.validate_opacity(self.var_opacity.get(), 128)
                if opacity != self.var_opacity.get():
                    self.var_opacity.set(opacity)
            except Exception as e:
                print(f"透明度验证错误: {e}")
        
        self.var_opacity.trace('w', validate_opacity)
        
        # 图片透明度验证
        def validate_image_opacity(*args):
            try:
                opacity = InputValidator.validate_opacity(self.var_image_opacity.get(), 128)
                if opacity != self.var_image_opacity.get():
                    self.var_image_opacity.set(opacity)
            except Exception as e:
                print(f"图片透明度验证错误: {e}")
        
        self.var_image_opacity.trace('w', validate_image_opacity)
        
        # 图片缩放验证
        def validate_image_scale(*args):
            try:
                scale = InputValidator.validate_integer(self.var_image_scale.get(), 10, 200, 100)
                if scale != self.var_image_scale.get():
                    self.var_image_scale.set(scale)
            except Exception as e:
                print(f"图片缩放验证错误: {e}")
        
        self.var_image_scale.trace('w', validate_image_scale)
        
        # 质量验证
        def validate_quality(*args):
            try:
                quality = InputValidator.validate_quality(self.var_quality.get(), 95)
                if quality != self.var_quality.get():
                    self.var_quality.set(quality)
            except Exception as e:
                print(f"质量验证错误: {e}")
        
        self.var_quality.trace('w', validate_quality)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板 - 图片列表和控制
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 右侧面板 - 水印设置
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # 创建各个部分
        self.create_image_controls(left_frame)
        self.create_preview_area(left_frame)
        self.create_watermark_settings(right_frame)
        self.create_export_controls(right_frame)
    
    def create_image_controls(self, parent):
        """创建图片控制区域"""
        control_frame = ttk.LabelFrame(parent, text="图片管理", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮行
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="导入图片", 
                  command=self.import_images).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="导入文件夹", 
                  command=self.import_folder).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空列表", 
                  command=self.clear_images).pack(side=tk.LEFT)
        
        # 图片列表
        list_frame = ttk.Frame(control_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 创建Treeview
        columns = ("文件名", "尺寸", "格式")
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=6)
        
        # 设置列标题
        for col in columns:
            self.image_tree.heading(col, text=col)
            self.image_tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.image_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定选择事件
        self.image_tree.bind('<<TreeviewSelect>>', self.on_image_selected)
    
    def create_preview_area(self, parent):
        """创建预览区域"""
        preview_frame = ttk.LabelFrame(parent, text="预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(preview_frame, bg='white', relief=tk.SUNKEN, bd=1)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 预览信息
        self.preview_info = ttk.Label(preview_frame, text="请导入图片")
        self.preview_info.pack(pady=(10, 0))
    
    def create_watermark_settings(self, parent):
        """创建水印设置区域"""
        settings_frame = ttk.LabelFrame(parent, text="水印设置", padding="10")
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 水印类型选择
        type_frame = ttk.Frame(settings_frame)
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(type_frame, text="水印类型:").pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="文本", variable=self.var_watermark_type, 
                       value="文本", command=self.on_watermark_type_change).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(type_frame, text="图片", variable=self.var_watermark_type, 
                       value="图片", command=self.on_watermark_type_change).pack(side=tk.LEFT, padx=(10, 0))
        
        # 文本水印设置框架
        self.text_settings_frame = ttk.LabelFrame(settings_frame, text="文本水印设置", padding="10")
        
        # 水印文本输入
        ttk.Label(self.text_settings_frame, text="水印文本:").pack(anchor=tk.W)
        text_entry = ttk.Entry(self.text_settings_frame, textvariable=self.var_watermark_text, width=30)
        text_entry.pack(fill=tk.X, pady=(0, 10))
        text_entry.bind('<KeyRelease>', lambda e: self.on_watermark_change())
        
        # 字体大小输入框（增强版）
        font_size_frame = ttk.Frame(self.text_settings_frame)
        font_size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(font_size_frame, text="字体大小:").pack(side=tk.LEFT)
        
        # 字体大小控制按钮
        ttk.Button(font_size_frame, text="-", width=3, 
                  command=self.decrease_font_size).pack(side=tk.RIGHT, padx=(2, 0))
        ttk.Button(font_size_frame, text="+", width=3, 
                  command=self.increase_font_size).pack(side=tk.RIGHT, padx=(2, 0))
        
        self.font_size_entry = ttk.Entry(font_size_frame, textvariable=self.var_font_size, width=8)
        self.font_size_entry.pack(side=tk.RIGHT, padx=(0, 2))
        
        # 字体颜色选择
        color_frame = ttk.Frame(self.text_settings_frame)
        color_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(color_frame, text="字体颜色:").pack(side=tk.LEFT)
        ttk.Button(color_frame, text="选择颜色", 
                  command=self.choose_font_color).pack(side=tk.RIGHT)
        
        # 透明度滑块
        opacity_frame = ttk.Frame(self.text_settings_frame)
        opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(opacity_frame, text="透明度:").pack(side=tk.LEFT)
        self.opacity_label = ttk.Label(opacity_frame, text="50%")
        self.opacity_label.pack(side=tk.RIGHT)
        
        opacity_scale = ttk.Scale(opacity_frame, from_=0, to=255, variable=self.var_opacity,
                                 orient=tk.HORIZONTAL, command=self.on_watermark_change)
        opacity_scale.pack(fill=tk.X, padx=(10, 10))
        
        # 更新透明度标签
        def update_opacity_label(*args):
            opacity_percent = int((self.var_opacity.get() / 255) * 100)
            self.opacity_label.config(text=f"{opacity_percent}%")
        self.var_opacity.trace('w', update_opacity_label)
        update_opacity_label()
        
        # 图片水印设置框架
        self.image_settings_frame = ttk.LabelFrame(settings_frame, text="图片水印设置", padding="10")
        
        # 选择图片
        image_file_frame = ttk.Frame(self.image_settings_frame)
        image_file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(image_file_frame, text="水印图片:").pack(side=tk.LEFT)
        ttk.Button(image_file_frame, text="浏览", 
                  command=self.browse_watermark_image).pack(side=tk.RIGHT)
        
        self.watermark_image_entry = ttk.Entry(image_file_frame, textvariable=self.var_watermark_image_path,
                                              state="readonly")
        self.watermark_image_entry.pack(fill=tk.X, padx=(10, 10))
        
        # 图片大小调整
        image_size_frame = ttk.Frame(self.image_settings_frame)
        image_size_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(image_size_frame, text="水印大小:").pack(side=tk.LEFT)
        self.image_scale_label = ttk.Label(image_size_frame, text="100%")
        self.image_scale_label.pack(side=tk.RIGHT)
        
        image_scale = ttk.Scale(image_size_frame, from_=10, to=200, variable=self.var_image_scale,
                               orient=tk.HORIZONTAL, command=self.on_watermark_change)
        image_scale.pack(fill=tk.X, padx=(10, 10))
        
        # 更新图片大小标签
        def update_image_scale_label(*args):
            self.image_scale_label.config(text=f"{self.var_image_scale.get()}%")
        self.var_image_scale.trace('w', update_image_scale_label)
        
        # 图片透明度
        image_opacity_frame = ttk.Frame(self.image_settings_frame)
        image_opacity_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(image_opacity_frame, text="透明度:").pack(side=tk.LEFT)
        self.image_opacity_label = ttk.Label(image_opacity_frame, text="50%")
        self.image_opacity_label.pack(side=tk.RIGHT)
        
        image_opacity_scale = ttk.Scale(image_opacity_frame, from_=0, to=255, variable=self.var_image_opacity,
                                       orient=tk.HORIZONTAL, command=self.on_watermark_change)
        image_opacity_scale.pack(fill=tk.X, padx=(10, 10))
        
        # 更新图片透明度标签
        def update_image_opacity_label(*args):
            opacity_percent = int((self.var_image_opacity.get() / 255) * 100)
            self.image_opacity_label.config(text=f"{opacity_percent}%")
        self.var_image_opacity.trace('w', update_image_opacity_label)
        
        # 位置设置
        position_frame = ttk.LabelFrame(settings_frame, text="水印位置", padding="10")
        position_frame.pack(fill=tk.X, pady=(10, 0))
        
        positions = [
            ("左上", "左上"), ("上中", "上中"), ("右上", "右上"),
            ("左中", "左中"), ("中心", "中心"), ("右中", "右中"),
            ("左下", "左下"), ("下中", "下中"), ("右下", "右下")
        ]
        
        # 创建3x3网格
        for i, (text, value) in enumerate(positions):
            row = i // 3
            col = i % 3
            ttk.Radiobutton(position_frame, text=text, variable=self.var_position, 
                           value=value, command=self.on_watermark_change).grid(
                row=row, column=col, sticky="w", padx=5, pady=2)
    
    def create_export_controls(self, parent):
        """创建导出控制区域"""
        export_frame = ttk.LabelFrame(parent, text="导出设置", padding="10")
        export_frame.pack(fill=tk.X)
        
        # 输出目录选择
        dir_frame = ttk.Frame(export_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="输出目录:").pack(anchor=tk.W)
        
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Entry(dir_select_frame, textvariable=self.var_output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(dir_select_frame, text="浏览",
                  command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(10, 0))
        
        # 输出格式选择
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.var_output_format, 
                       value="JPEG").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(format_frame, text="PNG", variable=self.var_output_format, 
                       value="PNG").pack(side=tk.LEFT, padx=(10, 0))
        
        # JPEG质量设置
        quality_frame = ttk.Frame(export_frame)
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quality_frame, text="JPEG质量:").pack(anchor=tk.W)
        ttk.Scale(quality_frame, from_=1, to=100, variable=self.var_quality,
                 orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(5, 0))
        
        # 导出按钮
        ttk.Button(export_frame, text="批量导出", 
                  command=self.export_images).pack(fill=tk.X, pady=(10, 0))
    
    def on_watermark_type_change(self):
        """水印类型改变时的处理"""
        watermark_type = self.var_watermark_type.get()
        if watermark_type == "文本":
            self.text_settings_frame.pack(fill=tk.X, pady=(0, 10))
            self.image_settings_frame.pack_forget()
        else:
            self.image_settings_frame.pack(fill=tk.X, pady=(0, 10))
            self.text_settings_frame.pack_forget()
        
        self.on_watermark_change()
    
    def validate_font_size_input(self):
        """验证字体大小输入"""
        try:
            size = InputValidator.validate_font_size(self.var_font_size.get(), 48)
            if size != self.var_font_size.get():
                self.var_font_size.set(size)
            return size
        except Exception as e:
            print(f"字体大小验证错误: {e}")
            self.var_font_size.set(48)
            return 48
    
    def decrease_font_size(self):
        """减小字体大小"""
        current_size = self.validate_font_size_input()
        new_size = max(8, current_size - 2)
        self.var_font_size.set(new_size)
        self.on_watermark_change()
    
    def increase_font_size(self):
        """增大字体大小"""
        current_size = self.validate_font_size_input()
        new_size = min(1000, current_size + 2)
        self.var_font_size.set(new_size)
        self.on_watermark_change()
    
    def choose_font_color(self):
        """选择字体颜色"""
        try:
            current_color = InputValidator.validate_color_hex(self.var_font_color.get(), "#000000")
            color = colorchooser.askcolor(color=current_color)
            if color[1]:  # 用户选择了颜色
                self.var_font_color.set(color[1])
                self.on_watermark_change()
        except Exception as e:
            print(f"颜色选择错误: {e}")
    
    def browse_watermark_image(self):
        """浏览水印图片"""
        try:
            filetypes = [
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("所有文件", "*.*")
            ]
            
            filename = filedialog.askopenfilename(
                title="选择水印图片",
                filetypes=filetypes
            )
            
            if filename:
                self.var_watermark_image_path.set(filename)
                self.on_watermark_change()
        except Exception as e:
            print(f"浏览水印图片错误: {e}")
            messagebox.showerror("错误", f"选择水印图片时发生错误:\n{str(e)}")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        try:
            directory = filedialog.askdirectory(title="选择输出目录")
            if directory:
                self.var_output_dir.set(directory)
        except Exception as e:
            print(f"浏览输出目录错误: {e}")
            messagebox.showerror("错误", f"选择输出目录时发生错误:\n{str(e)}")
    
    def hex_to_rgba(self, hex_color, opacity):
        """将十六进制颜色转换为RGBA"""
        try:
            return InputValidator.hex_to_rgba(hex_color, opacity)
        except Exception as e:
            print(f"颜色转换错误: {e}")
            return (0, 0, 0, 128)  # 默认黑色，50%透明度
    
    def on_watermark_change(self, *args):
        """水印设置改变时更新预览"""
        try:
            self.update_preview()
        except Exception as e:
            print(f"预览更新错误: {e}")
    
    def update_preview(self):
        """更新预览"""
        try:
            if not self.current_images or self.current_image_index >= len(self.current_images):
                return
            
            image_info = self.current_images[self.current_image_index]
            base_image = image_info['image'].copy()
            
            watermark_type = self.var_watermark_type.get()
            
            if watermark_type == "文本":
                # 文本水印
                text = self.var_watermark_text.get()
                if text.strip():
                    config = {
                        'text': text,
                        'font_size': self.validate_font_size_input(),
                        'color': self.hex_to_rgba(self.var_font_color.get(), self.var_opacity.get()),
                        'position': self.var_position.get()
                    }
                    preview_image = self.watermark_processor.apply_text_watermark(base_image, config)
                else:
                    preview_image = base_image
            else:
                # 图片水印
                watermark_path = self.var_watermark_image_path.get()
                if watermark_path and os.path.exists(watermark_path):
                    config = {
                        'image_path': watermark_path,
                        'scale_percent': float(self.var_image_scale.get()),
                        'opacity': self.var_image_opacity.get(),
                        'position': self.var_position.get()
                    }
                    preview_image = self.watermark_processor.apply_image_watermark(base_image, config)
                else:
                    preview_image = base_image
            
            # 显示预览
            display_image = resize_for_display(preview_image, (600, 400))
            photo = pil_to_tkinter(display_image)
            
            self.preview_canvas.delete("all")
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                x = (canvas_width - display_image.width) // 2
                y = (canvas_height - display_image.height) // 2
                self.preview_canvas.create_image(x, y, anchor=tk.NW, image=photo)
                self.preview_canvas.image = photo  # 保持引用
            
            # 更新预览信息
            info_text = f"{image_info['name']} - {preview_image.width}x{preview_image.height}"
            self.preview_info.config(text=info_text)
            
        except Exception as e:
            print(f"更新预览错误: {e}")
    
    def import_images(self):
        """导入图片"""
        try:
            filetypes = [
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("PNG文件", "*.png"),
                ("JPEG文件", "*.jpg *.jpeg"),
                ("BMP文件", "*.bmp"),
                ("TIFF文件", "*.tiff"),
                ("所有文件", "*.*")
            ]
            
            filenames = filedialog.askopenfilenames(
                title="选择图片文件",
                filetypes=filetypes
            )
            
            if filenames:
                self.load_images(filenames)
        except Exception as e:
            print(f"导入图片错误: {e}")
            messagebox.showerror("错误", f"导入图片时发生错误:\n{str(e)}")
    
    def import_folder(self):
        """导入文件夹"""
        try:
            directory = filedialog.askdirectory(title="选择图片文件夹")
            if directory:
                # 查找所有图片文件
                image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
                image_files = []
                
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in image_extensions):
                            image_files.append(os.path.join(root, file))
                
                if image_files:
                    self.load_images(image_files)
                else:
                    messagebox.showinfo("提示", "所选文件夹中没有找到图片文件")
        except Exception as e:
            print(f"导入文件夹错误: {e}")
            messagebox.showerror("错误", f"导入文件夹时发生错误:\n{str(e)}")
    
    def load_images(self, file_paths):
        """加载图片文件"""
        try:
            loaded_count = 0
            for file_path in file_paths:
                try:
                    image = self.image_processor.load_image(file_path)
                    if image:
                        image_info = {
                            'path': file_path,
                            'name': os.path.basename(file_path),
                            'image': image,
                            'size': f"{image.width}x{image.height}",
                            'format': image.format or 'Unknown'
                        }
                        self.current_images.append(image_info)
                        loaded_count += 1
                except Exception as e:
                    print(f"加载图片失败 {file_path}: {e}")
                    continue
            
            if loaded_count > 0:
                self.update_image_list()
                self.current_image_index = 0
                self.update_preview()
                messagebox.showinfo("成功", f"成功加载 {loaded_count} 张图片")
            else:
                messagebox.showerror("错误", "没有成功加载任何图片")
                
        except Exception as e:
            print(f"加载图片错误: {e}")
            messagebox.showerror("错误", f"加载图片时发生错误:\n{str(e)}")
    
    def update_image_list(self):
        """更新图片列表显示"""
        try:
            # 清空现有项目
            for item in self.image_tree.get_children():
                self.image_tree.delete(item)
            
            # 添加新项目
            for i, image_info in enumerate(self.current_images):
                self.image_tree.insert("", "end", values=(
                    image_info['name'],
                    image_info['size'],
                    image_info['format']
                ))
        except Exception as e:
            print(f"更新图片列表错误: {e}")
    
    def on_image_selected(self, event):
        """图片选择事件"""
        try:
            selection = self.image_tree.selection()
            if selection:
                item = selection[0]
                index = self.image_tree.index(item)
                if 0 <= index < len(self.current_images):
                    self.current_image_index = index
                    self.update_preview()
        except Exception as e:
            print(f"图片选择错误: {e}")
    
    def clear_images(self):
        """清空图片列表"""
        try:
            if messagebox.askyesno("确认", "确定要清空所有图片吗？"):
                self.current_images.clear()
                self.current_image_index = 0
                self.update_image_list()
                self.preview_canvas.delete("all")
                self.preview_info.config(text="请导入图片")
        except Exception as e:
            print(f"清空图片列表错误: {e}")
    
    def export_images(self):
        """导出图片"""
        try:
            if not self.current_images:
                messagebox.showwarning("警告", "请先导入图片")
                return
            
            output_dir = self.var_output_dir.get()
            if not output_dir:
                messagebox.showwarning("警告", "请选择输出目录")
                return
            
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir)
                except Exception as e:
                    messagebox.showerror("错误", f"无法创建输出目录:\n{str(e)}")
                    return
            
            # 在后台线程中执行导出
            def export_thread():
                try:
                    total_count = len(self.current_images)
                    success_count = 0
                    
                    for i, image_info in enumerate(self.current_images):
                        try:
                            base_image = image_info['image'].copy()
                            watermark_type = self.var_watermark_type.get()
                            
                            if watermark_type == "文本":
                                # 文本水印
                                text = self.var_watermark_text.get()
                                if text.strip():
                                    config = {
                                        'text': text,
                                        'font_size': self.validate_font_size_input(),
                                        'color': self.hex_to_rgba(self.var_font_color.get(), self.var_opacity.get()),
                                        'position': self.var_position.get()
                                    }
                                    processed_image = self.watermark_processor.apply_text_watermark(base_image, config)
                                else:
                                    processed_image = base_image
                            else:
                                # 图片水印
                                watermark_path = self.var_watermark_image_path.get()
                                if watermark_path and os.path.exists(watermark_path):
                                    config = {
                                        'image_path': watermark_path,
                                        'scale_percent': float(self.var_image_scale.get()),
                                        'opacity': self.var_image_opacity.get(),
                                        'position': self.var_position.get()
                                    }
                                    processed_image = self.watermark_processor.apply_image_watermark(base_image, config)
                                else:
                                    processed_image = base_image
                            
                            # 生成输出文件名
                            base_name = os.path.splitext(image_info['name'])[0]
                            ext = '.jpg' if self.var_output_format.get() == 'JPEG' else '.png'
                            output_filename = f"{base_name}_watermarked{ext}"
                            output_path = os.path.join(output_dir, output_filename)
                            
                            # 保存图片
                            if self.var_output_format.get() == 'JPEG':
                                if processed_image.mode == 'RGBA':
                                    processed_image = processed_image.convert('RGB')
                                processed_image.save(output_path, 'JPEG', quality=InputValidator.validate_quality(self.var_quality.get(), 95))
                            else:
                                processed_image.save(output_path, 'PNG')
                            
                            success_count += 1
                            print(f"导出成功: {output_filename}")
                            
                        except Exception as e:
                            print(f"导出图片失败 {image_info['name']}: {e}")
                    
                    messagebox.showinfo("完成", f"成功导出 {success_count}/{total_count} 张图片到:\n{output_dir}")
                    
                except Exception as e:
                    messagebox.showerror("错误", f"导出过程中发生错误:\n{str(e)}")
            
            # 启动导出线程
            threading.Thread(target=export_thread, daemon=True).start()
            
        except Exception as e:
            print(f"导出图片错误: {e}")
            messagebox.showerror("错误", f"导出图片时发生错误:\n{str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()