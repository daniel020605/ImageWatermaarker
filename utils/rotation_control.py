"""
旋转控制模块
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class RotationControl:
    """旋转控制器"""
    
    def __init__(self, parent):
        """
        初始化旋转控制器
        
        Args:
            parent: 父控件
        """
        self.parent = parent
        
        # 变量
        self.var_rotation = tk.IntVar(value=0)
        
        # 回调函数
        self.rotation_change_callback: Optional[Callable] = None
        
        # 创建控件
        self.create_widgets()
        
        # 绑定事件
        self.var_rotation.trace('w', self.on_rotation_change)
    
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        self.frame = ttk.Frame(self.parent)
        
        # 旋转标签
        ttk.Label(self.frame, text="旋转角度:").pack(side=tk.LEFT)
        
        # 旋转滑块
        self.rotation_scale = ttk.Scale(
            self.frame, from_=-180, to=180, variable=self.var_rotation,
            orient=tk.HORIZONTAL, length=100
        )
        self.rotation_scale.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        # 数值输入框
        self.rotation_spinbox = ttk.Spinbox(
            self.frame, from_=-180, to=180, textvariable=self.var_rotation, width=6
        )
        self.rotation_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 度数标签
        ttk.Label(self.frame, text="°").pack(side=tk.LEFT, padx=(2, 0))
        
        # 重置按钮
        ttk.Button(self.frame, text="重置", command=self.reset_rotation).pack(side=tk.LEFT, padx=(10, 0))
    
    def on_rotation_change(self, *args):
        """旋转角度改变"""
        if self.rotation_change_callback:
            self.rotation_change_callback(self.get_rotation())
    
    def get_rotation(self) -> int:
        """获取旋转角度"""
        return self.var_rotation.get()
    
    def set_rotation(self, angle: int):
        """设置旋转角度"""
        # 确保角度在有效范围内
        angle = max(-180, min(180, angle))
        self.var_rotation.set(angle)
    
    def reset_rotation(self):
        """重置旋转角度"""
        self.var_rotation.set(0)
    
    def set_rotation_change_callback(self, callback: Callable):
        """设置旋转改变回调"""
        self.rotation_change_callback = callback
    
    def pack(self, **kwargs):
        """打包控件"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """网格布局控件"""
        self.frame.grid(**kwargs)