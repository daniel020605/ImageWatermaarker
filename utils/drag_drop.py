"""
拖拽功能模块
支持文件和文件夹的拖拽导入
"""

import tkinter as tk
from typing import Callable, Optional, List


class DragDropHandler:
    """拖拽处理器"""
    
    def __init__(self, widget):
        """
        初始化拖拽处理器
        
        Args:
            widget: 要支持拖拽的控件
        """
        self.widget = widget
        self.drop_callback: Optional[Callable[[List[str]], None]] = None
        
        # 尝试导入tkinterdnd2
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            
            # 如果根窗口不是TkinterDnD类型，需要转换
            root = widget.winfo_toplevel()
            if not isinstance(root, TkinterDnD.Tk):
                print("警告: 根窗口不支持拖拽功能，请使用TkinterDnD.Tk")
                self.dnd_available = False
                return
            
            # 注册拖拽事件
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind('<<Drop>>', self.on_drop)
            self.dnd_available = True
            
        except ImportError:
            print("警告: tkinterdnd2未安装，拖拽功能不可用")
            self.dnd_available = False
        except Exception as e:
            print(f"拖拽功能初始化失败: {e}")
            self.dnd_available = False
    
    def on_drop(self, event):
        """拖拽释放事件处理"""
        if not self.drop_callback:
            return
        
        # 解析拖拽的文件路径
        files = self.parse_drop_data(event.data)
        if files:
            self.drop_callback(files)
    
    def parse_drop_data(self, data: str) -> List[str]:
        """
        解析拖拽数据
        
        Args:
            data: 拖拽数据字符串
            
        Returns:
            文件路径列表
        """
        files = []
        
        # 处理不同格式的拖拽数据
        if data.startswith('{') and data.endswith('}'):
            # 处理包含空格的路径（用大括号包围）
            data = data[1:-1]
        
        # 分割多个文件路径
        import re
        # 使用正则表达式分割路径，考虑空格和特殊字符
        paths = re.findall(r'[^\s]+(?:\s+[^\s]+)*', data)
        
        for path in paths:
            path = path.strip().strip('"').strip("'")
            if path:
                files.append(path)
        
        return files
    
    def set_drop_callback(self, callback: Callable[[List[str]], None]):
        """
        设置拖拽回调函数
        
        Args:
            callback: 回调函数，接收文件路径列表
        """
        self.drop_callback = callback
    
    def is_available(self) -> bool:
        """检查拖拽功能是否可用"""
        return self.dnd_available


class SimpleDragDropHandler:
    """简化的拖拽处理器（不依赖tkinterdnd2）"""
    
    def __init__(self, widget):
        """初始化简化拖拽处理器"""
        self.widget = widget
        self.drop_callback: Optional[Callable[[List[str]], None]] = None
        
        # 绑定基本的拖拽事件
        widget.bind('<Button-1>', self.on_click)
        widget.bind('<B1-Motion>', self.on_drag)
        widget.bind('<ButtonRelease-1>', self.on_release)
        
        print("使用简化拖拽处理器（功能有限）")
    
    def on_click(self, event):
        """鼠标点击事件"""
        pass
    
    def on_drag(self, event):
        """鼠标拖拽事件"""
        pass
    
    def on_release(self, event):
        """鼠标释放事件"""
        pass
    
    def set_drop_callback(self, callback: Callable[[List[str]], None]):
        """设置拖拽回调函数"""
        self.drop_callback = callback
    
    def is_available(self) -> bool:
        """检查拖拽功能是否可用"""
        return False  # 简化版本不支持真正的拖拽


def create_drag_drop_handler(widget) -> DragDropHandler:
    """
    创建拖拽处理器工厂函数
    
    Args:
        widget: 要支持拖拽的控件
        
    Returns:
        拖拽处理器实例
    """
    try:
        return DragDropHandler(widget)
    except:
        return SimpleDragDropHandler(widget)