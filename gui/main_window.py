"""
主窗口模块
应用程序的主界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

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
        # 水印设置变量
        self.var_watermark_type = tk.StringVar(value="text")
        self.var_watermark_text = tk.StringVar(value="Sample Watermark")
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
        
        # 颜色变量
        self.watermark_color = (255, 255, 255, 128)  # 默认白色半透明
    
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
        font_size_scale = ttk.Scale(self.text_settings_frame, from_=12, to=100, 
                                   variable=self.var_font_size, orient=tk.HORIZONTAL,
                                   command=self.on_font_size_changed)
        font_size_scale.grid(row=1, column=1, sticky=tk.EW, pady=2)
        ttk.Label(self.text_settings_frame, textvariable=self.var_font_size).grid(row=1, column=2, pady=2)
        
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
        
        # 更新模板列表
        self.update_template_list()
    
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
    
    # 事件处理方法将在下一部分继续...
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()