"""
模板管理模块
完整的水印模板保存、加载和管理功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板存储目录
        """
        self.templates_dir = templates_dir
        self.ensure_templates_dir()
    
    def ensure_templates_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def save_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """
        保存模板
        
        Args:
            name: 模板名称
            template_data: 模板数据
            
        Returns:
            是否保存成功
        """
        try:
            # 添加元数据
            template_data['metadata'] = {
                'name': name,
                'created_time': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # 保存到文件
            file_path = os.path.join(self.templates_dir, f"{name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
    
    def load_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        加载模板
        
        Args:
            name: 模板名称
            
        Returns:
            模板数据，失败返回None
        """
        try:
            file_path = os.path.join(self.templates_dir, f"{name}.json")
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"加载模板失败: {e}")
            return None
    
    def delete_template(self, name: str) -> bool:
        """
        删除模板
        
        Args:
            name: 模板名称
            
        Returns:
            是否删除成功
        """
        try:
            file_path = os.path.join(self.templates_dir, f"{name}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
            
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
    
    def list_templates(self) -> List[str]:
        """
        列出所有模板
        
        Returns:
            模板名称列表
        """
        try:
            templates = []
            for file in os.listdir(self.templates_dir):
                if file.endswith('.json'):
                    templates.append(os.path.splitext(file)[0])
            return sorted(templates)
            
        except Exception as e:
            print(f"列出模板失败: {e}")
            return []


class TemplateQuickAccess:
    """模板快速访问控件"""
    
    def __init__(self, parent, template_manager: TemplateManager):
        """
        初始化模板快速访问控件
        
        Args:
            parent: 父控件
            template_manager: 模板管理器
        """
        self.parent = parent
        self.template_manager = template_manager
        
        # 回调函数
        self.save_callback = None
        self.load_callback = None
        
        # 创建控件
        self.create_widgets()
        self.refresh_template_list()
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.LabelFrame(self.parent, text="模板管理", padding="10")
        
        # 保存模板
        save_frame = ttk.Frame(self.frame)
        save_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(save_frame, text="保存为模板:").pack(side=tk.LEFT)
        
        self.save_entry = ttk.Entry(save_frame, width=15)
        self.save_entry.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        ttk.Button(save_frame, text="保存", command=self.save_template).pack(side=tk.LEFT)
        
        # 加载模板
        load_frame = ttk.Frame(self.frame)
        load_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(load_frame, text="加载模板:").pack(side=tk.LEFT)
        
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(
            load_frame, textvariable=self.template_var,
            state="readonly", width=15
        )
        self.template_combo.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        ttk.Button(load_frame, text="加载", command=self.load_template).pack(side=tk.LEFT)
        
        # 刷新按钮
        ttk.Button(self.frame, text="刷新列表", command=self.refresh_template_list).pack(pady=(5, 0))
    
    def refresh_template_list(self):
        """刷新模板列表"""
        templates = self.template_manager.list_templates()
        self.template_combo['values'] = templates
        
        if templates and not self.template_var.get():
            self.template_var.set(templates[0])
    
    def save_template(self):
        """保存模板"""
        name = self.save_entry.get().strip()
        if not name:
            messagebox.showwarning("警告", "请输入模板名称")
            return
        
        # 检查名称是否已存在
        if name in self.template_manager.list_templates():
            if not messagebox.askyesno("确认", f"模板 '{name}' 已存在，是否覆盖？"):
                return
        
        # 获取当前设置
        if self.save_callback:
            template_data = self.save_callback()
            if template_data:
                if self.template_manager.save_template(name, template_data):
                    messagebox.showinfo("成功", f"模板 '{name}' 保存成功")
                    self.save_entry.delete(0, tk.END)
                    self.refresh_template_list()
                else:
                    messagebox.showerror("错误", "模板保存失败")
            else:
                messagebox.showwarning("警告", "无法获取当前设置")
        else:
            messagebox.showwarning("警告", "保存功能未配置")
    
    def load_template(self):
        """加载模板"""
        name = self.template_var.get()
        if not name:
            messagebox.showwarning("警告", "请选择一个模板")
            return
        
        template_data = self.template_manager.load_template(name)
        if template_data:
            if self.load_callback:
                self.load_callback(template_data)
                messagebox.showinfo("成功", f"模板 '{name}' 加载成功")
            else:
                messagebox.showwarning("警告", "加载功能未配置")
        else:
            messagebox.showerror("错误", "模板加载失败")
    
    def set_save_callback(self, callback):
        """设置保存回调函数"""
        self.save_callback = callback
    
    def set_load_callback(self, callback):
        """设置加载回调函数"""
        self.load_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)