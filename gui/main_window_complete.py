"""
完整的主窗口模块
包含所有事件处理方法
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import os
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any
from PIL import Image
from datetime import datetime

from core.image_processor import ImageProcessor
from core.watermark import WatermarkProcessor, WatermarkPosition
from core.config_manager import ConfigManager
from utils.file_utils import validate_output_directory, get_available_fonts, get_font_name_from_path
from utils.image_utils import pil_to_tkinter, resize_for_display, create_thumbnail_with_border


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ImageWatermarker - 图片水印工具")
        self.root.geometry("1200x800")
        
        # 核心组件
        self.image_processor = ImageProcessor()
        self.watermark_processor = WatermarkProcessor()
        self.config_manager = ConfigManager()
        
        # 数据存储
        self.loaded_images = []  # 加载的图片列表
        self.current_image_index = 0  # 当前预览的图片索引
        self.preview_image = None  # 当前预览图像
        self.watermark_config = self.config_manager.get_default_watermark_config()
        self.export_config = self.config_manager.get_default_export_config()
        
        # GUI变量
        self.setup_variables()
        
        # 创建界面
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
        # 加载设置
        self.load_settings()
        
        # 绑定事件
        self.bind_events()
        
        # 加载最后使用的模板
        self.load_last_template()
    
    def setup_variables(self):
        """设置GUI变量"""
        # 获取当前日期作为默认水印文本
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # 水印设置变量
        self.var_watermark_type = tk.StringVar(value="text")
        self.var_watermark_text = tk.StringVar(value=current_date)
        self.var_font_size = tk.IntVar(value=36)
        self.var_opacity = tk.IntVar(value=50)
        self.var_position = tk.StringVar(value="middle_center")
        self.var_rotation = tk.IntVar(value=0)
        self.var_margin = tk.IntVar(value=20)
        
        # 导出设置变量
        self.var_output_format = tk.StringVar(value="JPEG")
        self.var_quality = tk.IntVar(value=95)
        self.var_naming_rule = tk.StringVar(value="suffix")
        self.var_custom_text = tk.StringVar(value="_watermarked")
        
        # 其他变量
        self.var_output_dir = tk.StringVar()
        self.var_current_template = tk.StringVar(value="Default")
        
        # 颜色变量 - 设置默认为黑色，便于预览
        self.watermark_color = (0, 0, 0, 128)  # 默认黑色半透明
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="导入图片...", command=self.import_images, accelerator="Ctrl+O")
        file_menu.add_command(label="导入文件夹...", command=self.import_folder)
        file_menu.add_separator()
        file_menu.add_command(label="导出图片...", command=self.export_images, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit, accelerator="Ctrl+Q")
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清空图片列表", command=self.clear_images)
        edit_menu.add_separator()
        edit_menu.add_command(label="重置水印设置", command=self.reset_watermark_settings)
        
        # 模板菜单
        template_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="模板", menu=template_menu)
        template_menu.add_command(label="保存模板...", command=self.save_template)
        template_menu.add_command(label="加载模板...", command=self.load_template)
        template_menu.add_command(label="管理模板...", command=self.manage_templates)
        template_menu.add_separator()
        template_menu.add_command(label="导出模板...", command=self.export_template)
        template_menu.add_command(label="导入模板...", command=self.import_template)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # 导入按钮
        ttk.Button(toolbar, text="导入图片", command=self.import_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="导入文件夹", command=self.import_folder).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 导出按钮
        ttk.Button(toolbar, text="导出图片", command=self.export_images).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="清空列表", command=self.clear_images).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 模板按钮
        ttk.Button(toolbar, text="保存模板", command=self.save_template).pack(side=tk.LEFT, padx=2)
        
        # 模板选择
        ttk.Label(toolbar, text="模板:").pack(side=tk.LEFT, padx=(10, 2))
        self.template_combo = ttk.Combobox(toolbar, textvariable=self.var_current_template, 
                                          width=15, state="readonly")
        self.template_combo.pack(side=tk.LEFT, padx=2)
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        ttk.Button(toolbar, text="加载", command=self.load_template).pack(side=tk.LEFT, padx=2)
    
    def create_main_layout(self):
        """创建主布局"""
        # 主容器
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板 - 图片列表
        self.create_image_list_panel(main_container)
        
        # 右侧容器
        right_container = ttk.PanedWindow(main_container, orient=tk.VERTICAL)
        main_container.add(right_container, weight=3)
        
        # 预览面板
        self.create_preview_panel(right_container)
        
        # 设置面板
        self.create_settings_panel(right_container)
    
    def create_image_list_panel(self, parent):
        """创建图片列表面板"""
        # 左侧面板框架
        left_frame = ttk.LabelFrame(parent, text="图片列表", padding=5)
        parent.add(left_frame, weight=1)
        
        # 图片列表
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview来显示图片列表
        columns = ('name', 'size', 'format')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings', height=15)
        
        # 设置列标题
        self.image_tree.heading('#0', text='缩略图')
        self.image_tree.heading('name', text='文件名')
        self.image_tree.heading('size', text='尺寸')
        self.image_tree.heading('format', text='格式')
        
        # 设置列宽
        self.image_tree.column('#0', width=80, minwidth=80)
        self.image_tree.column('name', width=150, minwidth=100)
        self.image_tree.column('size', width=80, minwidth=80)
        self.image_tree.column('format', width=60, minwidth=60)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.image_tree.xview)
        self.image_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 布局
        self.image_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 绑定选择事件
        self.image_tree.bind('<<TreeviewSelect>>', self.on_image_selected)
        
        # 右键菜单
        self.create_image_context_menu()
    
    def create_preview_panel(self, parent):
        """创建预览面板"""
        preview_frame = ttk.LabelFrame(parent, text="预览", padding=5)
        parent.add(preview_frame, weight=2)
        
        # 预览画布
        self.preview_canvas = tk.Canvas(preview_frame, bg='white', relief=tk.SUNKEN, bd=1)
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 预览信息标签
        self.preview_info_label = ttk.Label(preview_frame, text="请导入图片")
        self.preview_info_label.pack(pady=5)
    
    def create_settings_panel(self, parent):
        """创建设置面板"""
        settings_frame = ttk.LabelFrame(parent, text="水印设置", padding=5)
        parent.add(settings_frame, weight=1)
        
        # 创建笔记本控件来组织设置
        notebook = ttk.Notebook(settings_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 水印设置标签页
        self.create_watermark_tab(notebook)
        
        # 导出设置标签页
        self.create_export_tab(notebook)
    
    def create_watermark_tab(self, parent):
        """创建水印设置标签页"""
        watermark_frame = ttk.Frame(parent)
        parent.add(watermark_frame, text="水印设置")
        
        # 使用滚动框架
        canvas = tk.Canvas(watermark_frame)
        scrollbar = ttk.Scrollbar(watermark_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 水印类型
        type_frame = ttk.LabelFrame(scrollable_frame, text="水印类型", padding=5)
        type_frame.pack(fill=tk.X, pady=2)
        
        ttk.Radiobutton(type_frame, text="文本水印", variable=self.var_watermark_type, 
                       value="text", command=self.on_watermark_type_changed).pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="图片水印", variable=self.var_watermark_type, 
                       value="image", command=self.on_watermark_type_changed).pack(side=tk.LEFT)
        
        # 文本水印设置
        self.text_settings_frame = ttk.LabelFrame(scrollable_frame, text="文本设置", padding=5)
        self.text_settings_frame.pack(fill=tk.X, pady=2)
        
        # 文本内容
        ttk.Label(self.text_settings_frame, text="文本内容:").grid(row=0, column=0, sticky=tk.W, pady=2)
        text_entry = ttk.Entry(self.text_settings_frame, textvariable=self.var_watermark_text, width=30)
        text_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        text_entry.bind('<KeyRelease>', self.on_text_changed)
        
        # 字体大小
        ttk.Label(self.text_settings_frame, text="字体大小:").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # 字体大小输入框和调整按钮
        font_size_frame = ttk.Frame(self.text_settings_frame)
        font_size_frame.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        # 减小按钮
        ttk.Button(font_size_frame, text="-", width=3, 
                  command=self.decrease_font_size).pack(side=tk.LEFT, padx=(0, 2))
        
        # 字体大小输入框
        font_size_entry = ttk.Entry(font_size_frame, textvariable=self.var_font_size, 
                                   width=8, justify=tk.CENTER)
        font_size_entry.pack(side=tk.LEFT, padx=2)
        font_size_entry.bind('<Return>', self.on_font_size_entry_changed)
        font_size_entry.bind('<FocusOut>', self.on_font_size_entry_changed)
        
        # 增大按钮
        ttk.Button(font_size_frame, text="+", width=3, 
                  command=self.increase_font_size).pack(side=tk.LEFT, padx=(2, 0))
        
        # 颜色选择
        ttk.Label(self.text_settings_frame, text="文字颜色:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.color_button = ttk.Button(self.text_settings_frame, text="选择颜色", 
                                      command=self.choose_color)
        self.color_button.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 透明度
        ttk.Label(self.text_settings_frame, text="透明度:").grid(row=3, column=0, sticky=tk.W, pady=2)
        opacity_scale = ttk.Scale(self.text_settings_frame, from_=0, to=100, 
                                 variable=self.var_opacity, orient=tk.HORIZONTAL,
                                 command=self.on_opacity_changed)
        opacity_scale.grid(row=3, column=1, sticky=tk.EW, pady=2)
        ttk.Label(self.text_settings_frame, textvariable=self.var_opacity).grid(row=3, column=2, pady=2)
        
        # 配置列权重
        self.text_settings_frame.grid_columnconfigure(1, weight=1)
        
        # 位置设置
        position_frame = ttk.LabelFrame(scrollable_frame, text="位置设置", padding=5)
        position_frame.pack(fill=tk.X, pady=2)
        
        # 九宫格位置按钮
        positions = [
            ("左上", "top_left"), ("上中", "top_center"), ("右上", "top_right"),
            ("左中", "middle_left"), ("正中", "middle_center"), ("右中", "middle_right"),
            ("左下", "bottom_left"), ("下中", "bottom_center"), ("右下", "bottom_right")
        ]
        
        for i, (text, value) in enumerate(positions):
            row, col = divmod(i, 3)
            ttk.Radiobutton(position_frame, text=text, variable=self.var_position, 
                           value=value, command=self.on_position_changed).grid(row=row, column=col, padx=5, pady=2)
        
        # 边距设置
        ttk.Label(position_frame, text="边距:").grid(row=3, column=0, sticky=tk.W, pady=2)
        margin_scale = ttk.Scale(position_frame, from_=0, to=100, 
                                variable=self.var_margin, orient=tk.HORIZONTAL,
                                command=self.on_margin_changed)
        margin_scale.grid(row=3, column=1, sticky=tk.EW, pady=2)
        ttk.Label(position_frame, textvariable=self.var_margin).grid(row=3, column=2, pady=2)
        
        # 旋转设置
        ttk.Label(position_frame, text="旋转角度:").grid(row=4, column=0, sticky=tk.W, pady=2)
        rotation_scale = ttk.Scale(position_frame, from_=0, to=360, 
                                  variable=self.var_rotation, orient=tk.HORIZONTAL,
                                  command=self.on_rotation_changed)
        rotation_scale.grid(row=4, column=1, sticky=tk.EW, pady=2)
        ttk.Label(position_frame, textvariable=self.var_rotation).grid(row=4, column=2, pady=2)
        
        position_frame.grid_columnconfigure(1, weight=1)
        
        # 布局滚动框架
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_export_tab(self, parent):
        """创建导出设置标签页"""
        export_frame = ttk.Frame(parent)
        parent.add(export_frame, text="导出设置")
        
        # 输出目录
        dir_frame = ttk.LabelFrame(export_frame, text="输出设置", padding=5)
        dir_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(dir_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.var_output_dir, width=40)
        dir_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        ttk.Button(dir_frame, text="浏览", command=self.choose_output_dir).grid(row=0, column=2, padx=5, pady=2)
        
        dir_frame.grid_columnconfigure(1, weight=1)
        
        # 文件格式
        format_frame = ttk.LabelFrame(export_frame, text="文件格式", padding=5)
        format_frame.pack(fill=tk.X, pady=2)
        
        ttk.Radiobutton(format_frame, text="JPEG", variable=self.var_output_format, 
                       value="JPEG", command=self.on_format_changed).pack(side=tk.LEFT)
        ttk.Radiobutton(format_frame, text="PNG", variable=self.var_output_format, 
                       value="PNG", command=self.on_format_changed).pack(side=tk.LEFT)
        
        # JPEG质量设置
        self.quality_frame = ttk.Frame(format_frame)
        self.quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.quality_frame, text="JPEG质量:").pack(side=tk.LEFT)
        quality_scale = ttk.Scale(self.quality_frame, from_=1, to=100, 
                                 variable=self.var_quality, orient=tk.HORIZONTAL, length=200)
        quality_scale.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.quality_frame, textvariable=self.var_quality).pack(side=tk.LEFT)
        
        # 文件命名
        naming_frame = ttk.LabelFrame(export_frame, text="文件命名", padding=5)
        naming_frame.pack(fill=tk.X, pady=2)
        
        ttk.Radiobutton(naming_frame, text="保留原名", variable=self.var_naming_rule, 
                       value="original").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(naming_frame, text="添加前缀", variable=self.var_naming_rule, 
                       value="prefix").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(naming_frame, text="添加后缀", variable=self.var_naming_rule, 
                       value="suffix").grid(row=2, column=0, sticky=tk.W)
        
        ttk.Label(naming_frame, text="自定义文本:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(naming_frame, textvariable=self.var_custom_text, width=20).grid(row=3, column=1, sticky=tk.W, pady=2)
    
    def create_image_context_menu(self):
        """创建图片列表右键菜单"""
        self.image_context_menu = tk.Menu(self.root, tearoff=0)
        self.image_context_menu.add_command(label="删除", command=self.remove_selected_image)
        self.image_context_menu.add_command(label="在文件管理器中显示", command=self.show_in_explorer)
        
        def show_context_menu(event):
            try:
                self.image_context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.image_context_menu.grab_release()
        
        self.image_tree.bind("<Button-3>", show_context_menu)  # 右键
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.status_bar, variable=self.progress_var, 
                                           length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def bind_events(self):
        """绑定事件"""
        # 键盘快捷键
        self.root.bind('<Control-o>', lambda e: self.import_images())
        self.root.bind('<Control-s>', lambda e: self.export_images())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # ==================== 事件处理方法 ====================
    
    def import_images(self):
        """导入图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("BMP文件", "*.bmp"),
            ("TIFF文件", "*.tiff *.tif"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=file_types,
            initialdir=self.config_manager.get_setting('last_input_dir', str(Path.home()))
        )
        
        if files:
            self.load_images_to_list(files)
            # 保存最后使用的目录
            self.config_manager.set_setting('last_input_dir', str(Path(files[0]).parent))
    
    def import_folder(self):
        """导入文件夹中的所有图片"""
        folder = filedialog.askdirectory(
            title="选择图片文件夹",
            initialdir=self.config_manager.get_setting('last_input_dir', str(Path.home()))
        )
        
        if folder:
            images = self.image_processor.load_images_from_folder(folder)
            if images:
                self.loaded_images.extend(images)
                self.update_image_list()
                self.update_status(f"从文件夹导入了 {len(images)} 张图片")
                # 保存最后使用的目录
                self.config_manager.set_setting('last_input_dir', folder)
            else:
                messagebox.showwarning("警告", "文件夹中没有找到支持的图片文件")
    
    def load_images_to_list(self, file_paths: List[str]):
        """加载图片到列表"""
        self.update_status("正在加载图片...")
        loaded_count = 0
        
        for i, file_path in enumerate(file_paths):
            self.update_progress((i + 1) / len(file_paths) * 100)
            
            image_info = self.image_processor.load_image(file_path)
            if image_info:
                self.loaded_images.append(image_info)
                loaded_count += 1
        
        self.update_image_list()
        self.update_status(f"成功加载 {loaded_count} 张图片")
        self.update_progress(0)
        
        # 如果有图片，选择第一张并自动设置字体大小
        if self.loaded_images:
            self.current_image_index = 0
            # 根据第一张图片自动设置字体大小
            auto_font_size = self.calculate_auto_font_size()
            self.var_font_size.set(auto_font_size)
            self.update_preview()
    
    def update_image_list(self):
        """更新图片列表显示"""
        # 清空现有项目
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        
        # 添加图片项目
        for i, image_info in enumerate(self.loaded_images):
            # 创建缩略图
            thumbnail = self.image_processor.create_thumbnail(image_info['image'], (60, 60))
            thumbnail_photo = pil_to_tkinter(thumbnail)
            
            # 添加到树形控件
            item_id = self.image_tree.insert('', 'end', 
                                           image=thumbnail_photo,
                                           values=(
                                               image_info['name'],
                                               f"{image_info['size'][0]}x{image_info['size'][1]}",
                                               image_info['format'] or 'Unknown'
                                           ))
            
            # 保存缩略图引用到字典中，防止被垃圾回收
            if not hasattr(self, 'thumbnail_refs'):
                self.thumbnail_refs = {}
            self.thumbnail_refs[item_id] = thumbnail_photo
    
    def clear_images(self):
        """清空图片列表"""
        if self.loaded_images:
            result = messagebox.askyesno("确认", "确定要清空所有图片吗？")
            if result:
                self.loaded_images.clear()
                self.current_image_index = 0
                self.update_image_list()
                self.clear_preview()
                self.update_status("已清空图片列表")
    
    def on_image_selected(self, event):
        """图片选择事件"""
        selection = self.image_tree.selection()
        if selection:
            item = selection[0]
            index = self.image_tree.index(item)
            self.current_image_index = index
            # 根据新选择的图片自动调整字体大小
            auto_font_size = self.calculate_auto_font_size()
            self.var_font_size.set(auto_font_size)
            self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        if not self.loaded_images or self.current_image_index >= len(self.loaded_images):
            self.clear_preview()
            return
        
        try:
            current_image = self.loaded_images[self.current_image_index]
            base_image = current_image['image']
            
            # 创建水印配置
            watermark_config = self.get_current_watermark_config()
            
            # 创建水印
            if watermark_config['type'] == 'text':
                watermark = self.watermark_processor.create_text_watermark(
                    text=watermark_config['text'],
                    font_size=watermark_config['font_size'],
                    color=watermark_config['color']
                )
            else:
                # 图片水印暂时跳过
                watermark = None
            
            if watermark:
                # 应用水印
                preview_image = self.watermark_processor.apply_watermark(
                    base_image=base_image,
                    watermark=watermark,
                    position=WatermarkPosition(watermark_config['position']),
                    margin=watermark_config['margin'],
                    rotation=watermark_config['rotation']
                )
            else:
                preview_image = base_image
            
            # 调整预览大小
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                display_image = resize_for_display(preview_image, (canvas_width - 20, canvas_height - 20))
                photo = pil_to_tkinter(display_image)
                
                # 清空画布并显示图片
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(
                    canvas_width // 2, canvas_height // 2,
                    image=photo, anchor=tk.CENTER
                )
                
                # 保存引用
                self.preview_image = photo
                
                # 更新信息标签
                info_text = f"{current_image['name']} - {current_image['size'][0]}x{current_image['size'][1]} - {current_image['format']}"
                self.preview_info_label.config(text=info_text)
        
        except Exception as e:
            print(f"更新预览失败: {str(e)}")
            self.clear_preview()
    
    def clear_preview(self):
        """清空预览"""
        self.preview_canvas.delete("all")
        self.preview_info_label.config(text="请导入图片")
        self.preview_image = None
    
    def get_current_watermark_config(self) -> Dict[str, Any]:
        """获取当前水印配置"""
        return {
            'type': self.var_watermark_type.get(),
            'text': self.var_watermark_text.get(),
            'font_size': self.var_font_size.get(),
            'color': (*self.watermark_color[:3], int(self.var_opacity.get() * 255 / 100)),
            'position': self.var_position.get(),
            'margin': self.var_margin.get(),
            'rotation': self.var_rotation.get()
        }
    
    # 水印设置变化事件
    def on_watermark_type_changed(self):
        """水印类型变化"""
        self.update_preview()
    
    def on_text_changed(self, event=None):
        """文本内容变化"""
        self.update_preview()
    
    def on_font_size_changed(self, value):
        """字体大小变化"""
        self.update_preview()
    
    def on_font_size_entry_changed(self, event=None):
        """字体大小输入框变化"""
        try:
            size = int(self.var_font_size.get())
            if size < 8:
                size = 8
                self.var_font_size.set(size)
            elif size > 1000:  # 放宽上限到1000
                size = 1000
                self.var_font_size.set(size)
            self.update_preview()
        except ValueError:
            # 如果输入无效，恢复到自动计算的默认值
            default_size = self.calculate_auto_font_size()
            self.var_font_size.set(default_size)
            self.update_preview()
    
    def decrease_font_size(self):
        """减小字体大小"""
        current_size = self.var_font_size.get()
        new_size = max(8, current_size - 2)
        self.var_font_size.set(new_size)
        self.update_preview()
    
    def increase_font_size(self):
        """增大字体大小"""
        current_size = self.var_font_size.get()
        new_size = min(1000, current_size + 2)  # 放宽上限到1000
        self.var_font_size.set(new_size)
        self.update_preview()
    
    def calculate_auto_font_size(self):
        """根据图片尺寸自动计算字体大小"""
        if not self.loaded_images or self.current_image_index >= len(self.loaded_images):
            return 36  # 默认字体大小
        
        current_image = self.loaded_images[self.current_image_index]['image']
        width, height = current_image.size
        
        # 根据图片的较小边来计算字体大小
        min_dimension = min(width, height)
        
        # 字体大小约为图片较小边的1/20到1/15之间
        font_size = max(8, min(1000, int(min_dimension / 18)))
        
        return font_size
    
    def on_opacity_changed(self, value):
        """透明度变化"""
        self.update_preview()
    
    def on_position_changed(self):
        """位置变化"""
        self.update_preview()
    
    def on_margin_changed(self, value):
        """边距变化"""
        self.update_preview()
    
    def on_rotation_changed(self, value):
        """旋转角度变化"""
        self.update_preview()
    
    def choose_color(self):
        """选择颜色"""
        color = colorchooser.askcolor(
            color=self.watermark_color[:3],
            title="选择水印颜色"
        )
        if color[0]:
            # 保持原有的透明度
            self.watermark_color = (*[int(c) for c in color[0]], self.watermark_color[3])
            self.update_preview()
    
    def on_format_changed(self):
        """输出格式变化"""
        # 根据格式显示/隐藏质量设置
        if self.var_output_format.get() == "JPEG":
            self.quality_frame.pack(fill=tk.X, pady=5)
        else:
            self.quality_frame.pack_forget()
    
    def choose_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=self.var_output_dir.get() or str(Path.home() / 'Desktop')
        )
        if directory:
            self.var_output_dir.set(directory)
    
    def export_images(self):
        """导出图片"""
        if not self.loaded_images:
            messagebox.showwarning("警告", "请先导入图片")
            return
        
        output_dir = self.var_output_dir.get()
        if not output_dir:
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 验证输出目录
        input_files = [img['path'] for img in self.loaded_images]
        is_valid, error_msg = validate_output_directory(output_dir, input_files)
        if not is_valid:
            messagebox.showerror("错误", error_msg)
            return
        
        # 在后台线程中执行导出
        def export_thread():
            try:
                self.update_status("正在导出图片...")
                watermark_config = self.get_current_watermark_config()
                
                success_count = 0
                total_count = len(self.loaded_images)
                
                for i, image_info in enumerate(self.loaded_images):
                    self.update_progress((i + 1) / total_count * 100)
                    
                    try:
                        # 创建水印
                        if watermark_config['type'] == 'text':
                            watermark = self.watermark_processor.create_text_watermark(
                                text=watermark_config['text'],
                                font_size=watermark_config['font_size'],
                                color=watermark_config['color']
                            )
                        else:
                            continue  # 暂时跳过图片水印
                        
                        if watermark:
                            # 应用水印
                            result_image = self.watermark_processor.apply_watermark(
                                base_image=image_info['image'],
                                watermark=watermark,
                                position=WatermarkPosition(watermark_config['position']),
                                margin=watermark_config['margin'],
                                rotation=watermark_config['rotation']
                            )
                        else:
                            result_image = image_info['image']
                        
                        # 生成输出文件名
                        output_path = self.image_processor.generate_output_filename(
                            original_path=image_info['path'],
                            output_dir=output_dir,
                            naming_rule=self.var_naming_rule.get(),
                            custom_text=self.var_custom_text.get(),
                            output_format=self.var_output_format.get()
                        )
                        
                        # 保存图片
                        if self.image_processor.save_image(
                            image=result_image,
                            output_path=output_path,
                            format=self.var_output_format.get(),
                            quality=self.var_quality.get()
                        ):
                            success_count += 1
                    
                    except Exception as e:
                        print(f"导出图片失败 {image_info['name']}: {str(e)}")
                
                self.update_progress(0)
                self.update_status(f"导出完成: {success_count}/{total_count}")
                
                if success_count > 0:
                    messagebox.showinfo("完成", f"成功导出 {success_count} 张图片到:\n{output_dir}")
                else:
                    messagebox.showerror("错误", "没有图片导出成功")
            
            except Exception as e:
                self.update_status("导出失败")
                messagebox.showerror("错误", f"导出过程中发生错误:\n{str(e)}")
        
        # 启动导出线程
        threading.Thread(target=export_thread, daemon=True).start()
    
    # 模板管理方法
    def save_template(self):
        """保存当前设置为模板"""
        template_name = simpledialog.askstring("保存模板", "请输入模板名称:")
        if template_name:
            watermark_config = self.get_current_watermark_config()
            export_config = {
                'output_format': self.var_output_format.get(),
                'quality': self.var_quality.get(),
                'naming_rule': self.var_naming_rule.get(),
                'custom_text': self.var_custom_text.get()
            }
            
            if self.config_manager.save_template(template_name, watermark_config, export_config):
                self.update_template_list()
                self.var_current_template.set(template_name)
                messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功")
            else:
                messagebox.showerror("错误", "保存模板失败")
    
    def load_template(self):
        """加载选中的模板"""
        template_name = self.var_current_template.get()
        if not template_name:
            return
        
        template = self.config_manager.get_template(template_name)
        if template:
            self.apply_template(template)
            self.config_manager.set_last_used_template(template_name)
            self.update_status(f"已加载模板: {template_name}")
        else:
            messagebox.showerror("错误", f"模板 '{template_name}' 不存在")
    
    def apply_template(self, template: Dict[str, Any]):
        """应用模板设置"""
        watermark_config = template.get('watermark_config', {})
        export_config = template.get('export_config', {})
        
        # 应用水印设置
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.var_watermark_type.set(watermark_config.get('type', 'text'))
        self.var_watermark_text.set(watermark_config.get('text', current_date))
        self.var_font_size.set(watermark_config.get('font_size', 36))
        self.var_opacity.set(watermark_config.get('opacity', 50))
        self.var_position.set(watermark_config.get('position', 'middle_center'))
        self.var_margin.set(watermark_config.get('margin', 20))
        self.var_rotation.set(watermark_config.get('rotation', 0))
        
        # 应用颜色设置
        color = watermark_config.get('color', [255, 255, 255, 128])
        if len(color) >= 4:
            self.watermark_color = tuple(color)
        
        # 应用导出设置
        self.var_output_format.set(export_config.get('output_format', 'JPEG'))
        self.var_quality.set(export_config.get('quality', 95))
        self.var_naming_rule.set(export_config.get('naming_rule', 'suffix'))
        self.var_custom_text.set(export_config.get('custom_text', '_watermarked'))
        
        # 更新界面
        self.on_format_changed()
        self.update_preview()
    
    def update_template_list(self):
        """更新模板列表"""
        templates = self.config_manager.get_template_list()
        self.template_combo['values'] = templates
        
        if not self.var_current_template.get() and templates:
            self.var_current_template.set(templates[0])
    
    def load_last_template(self):
        """加载最后使用的模板"""
        self.update_template_list()
        
        if self.config_manager.get_setting('auto_load_last_template', True):
            last_template = self.config_manager.get_last_used_template()
            if last_template:
                self.var_current_template.set(last_template)
                self.load_template()
            else:
                # 如果没有保存的模板，确保使用当前日期作为默认水印文本
                current_date = datetime.now().strftime("%Y-%m-%d")
                self.var_watermark_text.set(current_date)
    
    def on_template_selected(self, event=None):
        """模板选择事件"""
        # 可以在这里添加自动加载逻辑
        pass
    
    def manage_templates(self):
        """管理模板对话框"""
        # 这里可以创建一个模板管理对话框
        messagebox.showinfo("提示", "模板管理功能待实现")
    
    def export_template(self):
        """导出模板"""
        template_name = self.var_current_template.get()
        if not template_name:
            messagebox.showwarning("警告", "请选择要导出的模板")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="导出模板",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            if self.config_manager.export_template(template_name, file_path):
                messagebox.showinfo("成功", f"模板已导出到: {file_path}")
            else:
                messagebox.showerror("错误", "导出模板失败")
    
    def import_template(self):
        """导入模板"""
        file_path = filedialog.askopenfilename(
            title="导入模板",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            template_name = simpledialog.askstring("导入模板", "请输入模板名称:")
            if template_name:
                if self.config_manager.import_template(file_path, template_name):
                    self.update_template_list()
                    messagebox.showinfo("成功", f"模板 '{template_name}' 导入成功")
                else:
                    messagebox.showerror("错误", "导入模板失败")
    
    def reset_watermark_settings(self):
        """重置水印设置"""
        result = messagebox.askyesno("确认", "确定要重置所有水印设置吗？")
        if result:
            default_config = self.config_manager.get_default_watermark_config()
            template = {'watermark_config': default_config, 'export_config': self.config_manager.get_default_export_config()}
            self.apply_template(template)
            self.update_status("已重置水印设置")
    
    def remove_selected_image(self):
        """删除选中的图片"""
        selection = self.image_tree.selection()
        if selection:
            item = selection[0]
            index = self.image_tree.index(item)
            
            # 删除图片
            del self.loaded_images[index]
            
            # 更新当前索引
            if self.current_image_index >= len(self.loaded_images):
                self.current_image_index = max(0, len(self.loaded_images) - 1)
            
            # 更新界面
            self.update_image_list()
            if self.loaded_images:
                self.update_preview()
            else:
                self.clear_preview()
            
            self.update_status("已删除选中图片")
    
    def show_in_explorer(self):
        """在文件管理器中显示"""
        selection = self.image_tree.selection()
        if selection:
            item = selection[0]
            index = self.image_tree.index(item)
            file_path = self.loaded_images[index]['path']
            
            import platform
            import subprocess
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(['explorer', '/select,', file_path])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(['open', '-R', file_path])
                else:  # Linux
                    subprocess.run(['xdg-open', str(Path(file_path).parent)])
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件管理器: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """ImageWatermarker v1.0

一个简单易用的图片水印工具

功能特点:
• 支持批量添加文本水印
• 支持多种图片格式
• 实时预览效果
• 模板保存和管理
• 灵活的导出设置

开发: CodeBuddy
"""
        messagebox.showinfo("关于", about_text)
    
    def load_settings(self):
        """加载应用设置"""
        settings = self.config_manager.load_settings()
        
        # 窗口大小和位置
        if 'window_size' in settings:
            width, height = settings['window_size']
            self.root.geometry(f"{width}x{height}")
        
        if 'window_position' in settings and settings['window_position']:
            x, y = settings['window_position']
            self.root.geometry(f"+{x}+{y}")
        
        # 最后使用的目录
        if 'last_output_dir' in settings:
            self.var_output_dir.set(settings['last_output_dir'])
    
    def save_settings(self):
        """保存应用设置"""
        # 获取窗口大小和位置
        geometry = self.root.geometry()
        size_pos = geometry.split('+')
        size = size_pos[0].split('x')
        
        settings = {
            'window_size': [int(size[0]), int(size[1])],
            'last_output_dir': self.var_output_dir.get()
        }
        
        if len(size_pos) >= 3:
            settings['window_position'] = [int(size_pos[1]), int(size_pos[2])]
        
        self.config_manager.save_settings(settings)
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value: float):
        """更新进度条"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def on_closing(self):
        """窗口关闭事件"""
        self.save_settings()
        self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()