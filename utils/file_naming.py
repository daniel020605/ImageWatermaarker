"""
文件命名规则模块
提供灵活的文件命名选项
"""

import os
from typing import Optional, Dict, Any
from enum import Enum


class NamingRule(Enum):
    """文件命名规则枚举"""
    KEEP_ORIGINAL = "keep_original"      # 保留原文件名
    ADD_PREFIX = "add_prefix"            # 添加前缀
    ADD_SUFFIX = "add_suffix"            # 添加后缀
    PREFIX_AND_SUFFIX = "prefix_suffix"  # 前缀和后缀


class FileNamingManager:
    """文件命名管理器"""
    
    def __init__(self):
        """初始化文件命名管理器"""
        self.default_prefix = "wm_"
        self.default_suffix = "_watermarked"
    
    def generate_filename(self, 
                         original_path: str,
                         output_dir: str,
                         naming_rule: NamingRule = NamingRule.ADD_SUFFIX,
                         custom_prefix: str = "",
                         custom_suffix: str = "",
                         output_format: str = "JPEG") -> str:
        """
        根据命名规则生成输出文件名
        
        Args:
            original_path: 原始文件路径
            output_dir: 输出目录
            naming_rule: 命名规则
            custom_prefix: 自定义前缀
            custom_suffix: 自定义后缀
            output_format: 输出格式 (JPEG/PNG)
            
        Returns:
            完整的输出文件路径
        """
        try:
            # 获取原始文件信息
            original_name = os.path.basename(original_path)
            name_without_ext = os.path.splitext(original_name)[0]
            
            # 确定输出扩展名
            if output_format.upper() == "JPEG":
                new_ext = ".jpg"
            elif output_format.upper() == "PNG":
                new_ext = ".png"
            else:
                # 保持原扩展名
                new_ext = os.path.splitext(original_name)[1]
            
            # 根据命名规则生成新文件名
            if naming_rule == NamingRule.KEEP_ORIGINAL:
                new_name = name_without_ext + new_ext
                
            elif naming_rule == NamingRule.ADD_PREFIX:
                prefix = custom_prefix if custom_prefix else self.default_prefix
                new_name = prefix + name_without_ext + new_ext
                
            elif naming_rule == NamingRule.ADD_SUFFIX:
                suffix = custom_suffix if custom_suffix else self.default_suffix
                new_name = name_without_ext + suffix + new_ext
                
            elif naming_rule == NamingRule.PREFIX_AND_SUFFIX:
                prefix = custom_prefix if custom_prefix else self.default_prefix
                suffix = custom_suffix if custom_suffix else self.default_suffix
                new_name = prefix + name_without_ext + suffix + new_ext
                
            else:
                # 默认添加后缀
                new_name = name_without_ext + self.default_suffix + new_ext
            
            # 生成完整路径
            output_path = os.path.join(output_dir, new_name)
            
            # 处理文件名冲突
            output_path = self.handle_filename_conflict(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"生成文件名失败: {e}")
            # 返回默认命名
            fallback_name = os.path.splitext(os.path.basename(original_path))[0] + "_watermarked.jpg"
            return os.path.join(output_dir, fallback_name)
    
    def handle_filename_conflict(self, file_path: str) -> str:
        """
        处理文件名冲突，如果文件已存在则添加数字后缀
        
        Args:
            file_path: 原始文件路径
            
        Returns:
            不冲突的文件路径
        """
        if not os.path.exists(file_path):
            return file_path
        
        # 分离路径、文件名和扩展名
        dir_path = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name_without_ext, ext = os.path.splitext(filename)
        
        # 添加数字后缀直到找到不冲突的文件名
        counter = 1
        while True:
            new_name = f"{name_without_ext}_{counter}{ext}"
            new_path = os.path.join(dir_path, new_name)
            
            if not os.path.exists(new_path):
                return new_path
            
            counter += 1
            
            # 防止无限循环
            if counter > 9999:
                break
        
        # 如果还是冲突，使用时间戳
        import time
        timestamp = int(time.time())
        new_name = f"{name_without_ext}_{timestamp}{ext}"
        return os.path.join(dir_path, new_name)
    
    def validate_output_directory(self, output_dir: str, original_paths: list) -> tuple:
        """
        验证输出目录，检查是否会覆盖原文件
        
        Args:
            output_dir: 输出目录
            original_paths: 原始文件路径列表
            
        Returns:
            (is_valid, warning_message)
        """
        try:
            if not output_dir:
                return False, "请选择输出目录"
            
            if not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                except Exception as e:
                    return False, f"无法创建输出目录: {str(e)}"
            
            # 检查是否会覆盖原文件
            original_dirs = set()
            for path in original_paths:
                original_dirs.add(os.path.dirname(os.path.abspath(path)))
            
            output_dir_abs = os.path.abspath(output_dir)
            
            if output_dir_abs in original_dirs:
                return False, "输出目录不能与原图片目录相同，以防止覆盖原文件"
            
            return True, ""
            
        except Exception as e:
            return False, f"验证输出目录时发生错误: {str(e)}"
    
    def get_naming_rule_description(self, rule: NamingRule) -> str:
        """获取命名规则的描述"""
        descriptions = {
            NamingRule.KEEP_ORIGINAL: "保留原文件名",
            NamingRule.ADD_PREFIX: "添加前缀",
            NamingRule.ADD_SUFFIX: "添加后缀", 
            NamingRule.PREFIX_AND_SUFFIX: "添加前缀和后缀"
        }
        return descriptions.get(rule, "未知规则")
    
    def preview_filename(self, 
                        original_name: str,
                        naming_rule: NamingRule,
                        custom_prefix: str = "",
                        custom_suffix: str = "",
                        output_format: str = "JPEG") -> str:
        """
        预览生成的文件名（不包含路径）
        
        Args:
            original_name: 原始文件名
            naming_rule: 命名规则
            custom_prefix: 自定义前缀
            custom_suffix: 自定义后缀
            output_format: 输出格式
            
        Returns:
            预览的文件名
        """
        try:
            name_without_ext = os.path.splitext(original_name)[0]
            
            # 确定扩展名
            if output_format.upper() == "JPEG":
                ext = ".jpg"
            elif output_format.upper() == "PNG":
                ext = ".png"
            else:
                ext = os.path.splitext(original_name)[1]
            
            # 生成预览名称
            if naming_rule == NamingRule.KEEP_ORIGINAL:
                return name_without_ext + ext
                
            elif naming_rule == NamingRule.ADD_PREFIX:
                prefix = custom_prefix if custom_prefix else self.default_prefix
                return prefix + name_without_ext + ext
                
            elif naming_rule == NamingRule.ADD_SUFFIX:
                suffix = custom_suffix if custom_suffix else self.default_suffix
                return name_without_ext + suffix + ext
                
            elif naming_rule == NamingRule.PREFIX_AND_SUFFIX:
                prefix = custom_prefix if custom_prefix else self.default_prefix
                suffix = custom_suffix if custom_suffix else self.default_suffix
                return prefix + name_without_ext + suffix + ext
            
            return name_without_ext + self.default_suffix + ext
            
        except Exception as e:
            print(f"预览文件名失败: {e}")
            return original_name


class NamingRuleWidget:
    """文件命名规则控件"""
    
    def __init__(self, parent):
        """初始化命名规则控件"""
        import tkinter as tk
        from tkinter import ttk
        
        self.parent = parent
        self.naming_manager = FileNamingManager()
        
        # 变量
        self.var_naming_rule = tk.StringVar(value=NamingRule.ADD_SUFFIX.value)
        self.var_custom_prefix = tk.StringVar(value="wm_")
        self.var_custom_suffix = tk.StringVar(value="_watermarked")
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.var_naming_rule.trace('w', self.on_rule_change)
        self.var_custom_prefix.trace('w', self.on_text_change)
        self.var_custom_suffix.trace('w', self.on_text_change)
    
    def create_widgets(self):
        """创建界面控件"""
        import tkinter as tk
        from tkinter import ttk
        
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="文件命名规则", padding="10")
        
        # 命名规则选择
        rule_frame = ttk.Frame(self.frame)
        rule_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rule_frame, text="命名规则:").pack(side=tk.LEFT)
        
        # 单选按钮
        rules = [
            (NamingRule.KEEP_ORIGINAL, "保留原名"),
            (NamingRule.ADD_PREFIX, "添加前缀"),
            (NamingRule.ADD_SUFFIX, "添加后缀"),
            (NamingRule.PREFIX_AND_SUFFIX, "前缀+后缀")
        ]
        
        for rule, text in rules:
            ttk.Radiobutton(rule_frame, text=text, variable=self.var_naming_rule,
                           value=rule.value).pack(side=tk.LEFT, padx=(10, 0))
        
        # 前缀设置
        self.prefix_frame = ttk.Frame(self.frame)
        self.prefix_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(self.prefix_frame, text="前缀:").pack(side=tk.LEFT)
        self.prefix_entry = ttk.Entry(self.prefix_frame, textvariable=self.var_custom_prefix, width=15)
        self.prefix_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # 后缀设置
        self.suffix_frame = ttk.Frame(self.frame)
        self.suffix_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.suffix_frame, text="后缀:").pack(side=tk.LEFT)
        self.suffix_entry = ttk.Entry(self.suffix_frame, textvariable=self.var_custom_suffix, width=15)
        self.suffix_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # 预览
        self.preview_frame = ttk.Frame(self.frame)
        self.preview_frame.pack(fill=tk.X)
        
        ttk.Label(self.preview_frame, text="预览:").pack(side=tk.LEFT)
        self.preview_label = ttk.Label(self.preview_frame, text="", foreground="blue")
        self.preview_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 初始化显示状态
        self.on_rule_change()
    
    def on_rule_change(self, *args):
        """命名规则改变时的处理"""
        rule = NamingRule(self.var_naming_rule.get())
        
        # 控制控件显示状态
        if rule in [NamingRule.ADD_PREFIX, NamingRule.PREFIX_AND_SUFFIX]:
            self.prefix_entry.configure(state="normal")
        else:
            self.prefix_entry.configure(state="disabled")
        
        if rule in [NamingRule.ADD_SUFFIX, NamingRule.PREFIX_AND_SUFFIX]:
            self.suffix_entry.configure(state="normal")
        else:
            self.suffix_entry.configure(state="disabled")
        
        # 更新预览
        self.update_preview()
    
    def on_text_change(self, *args):
        """文本改变时更新预览"""
        self.update_preview()
    
    def update_preview(self):
        """更新文件名预览"""
        try:
            rule = NamingRule(self.var_naming_rule.get())
            preview = self.naming_manager.preview_filename(
                "example.jpg",
                rule,
                self.var_custom_prefix.get(),
                self.var_custom_suffix.get(),
                "JPEG"
            )
            self.preview_label.configure(text=preview)
        except Exception as e:
            self.preview_label.configure(text="预览错误")
    
    def get_naming_config(self) -> Dict[str, Any]:
        """获取当前命名配置"""
        return {
            'rule': NamingRule(self.var_naming_rule.get()),
            'prefix': self.var_custom_prefix.get(),
            'suffix': self.var_custom_suffix.get()
        }
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)