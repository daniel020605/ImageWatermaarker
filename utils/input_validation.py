"""
输入验证工具模块
提供各种输入验证和数据清理功能
"""

import re
from typing import Union, Optional, Tuple


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_integer(value: Union[str, int], min_val: int = None, max_val: int = None, default: int = None) -> int:
        """
        验证并转换整数输入
        
        Args:
            value: 输入值
            min_val: 最小值
            max_val: 最大值
            default: 默认值
            
        Returns:
            验证后的整数值
        """
        try:
            # 如果是字符串，先清理
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return default if default is not None else 0
                
                # 移除非数字字符（除了负号）
                value = re.sub(r'[^\d-]', '', value)
                if not value or value == '-':
                    return default if default is not None else 0
            
            # 转换为整数
            result = int(value)
            
            # 应用范围限制
            if min_val is not None:
                result = max(result, min_val)
            if max_val is not None:
                result = min(result, max_val)
                
            return result
            
        except (ValueError, TypeError):
            return default if default is not None else 0
    
    @staticmethod
    def validate_float(value: Union[str, float], min_val: float = None, max_val: float = None, default: float = None) -> float:
        """
        验证并转换浮点数输入
        """
        try:
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    return default if default is not None else 0.0
                
                # 移除非数字字符（除了小数点和负号）
                value = re.sub(r'[^\d.-]', '', value)
                if not value or value in ['-', '.', '-.']:
                    return default if default is not None else 0.0
            
            result = float(value)
            
            if min_val is not None:
                result = max(result, min_val)
            if max_val is not None:
                result = min(result, max_val)
                
            return result
            
        except (ValueError, TypeError):
            return default if default is not None else 0.0
    
    @staticmethod
    def validate_color_hex(value: str, default: str = "#000000") -> str:
        """
        验证十六进制颜色值
        """
        if not isinstance(value, str):
            return default
            
        value = value.strip()
        
        # 添加#前缀如果缺失
        if not value.startswith('#'):
            value = '#' + value
        
        # 验证格式
        if re.match(r'^#[0-9A-Fa-f]{6}$', value):
            return value.upper()
        elif re.match(r'^#[0-9A-Fa-f]{3}$', value):
            # 转换3位格式到6位
            return '#' + ''.join([c*2 for c in value[1:]])
        else:
            return default
    
    @staticmethod
    def validate_opacity(value: Union[str, int], default: int = 128) -> int:
        """
        验证透明度值 (0-255)
        """
        return InputValidator.validate_integer(value, 0, 255, default)
    
    @staticmethod
    def validate_percentage(value: Union[str, int, float], default: float = 100.0) -> float:
        """
        验证百分比值 (0-100)
        """
        return InputValidator.validate_float(value, 0.0, 100.0, default)
    
    @staticmethod
    def validate_font_size(value: Union[str, int], default: int = 48) -> int:
        """
        验证字体大小 (8-1000)
        """
        return InputValidator.validate_integer(value, 8, 1000, default)
    
    @staticmethod
    def validate_quality(value: Union[str, int], default: int = 95) -> int:
        """
        验证JPEG质量 (1-100)
        """
        return InputValidator.validate_integer(value, 1, 100, default)
    
    @staticmethod
    def hex_to_rgba(hex_color: str, opacity: int) -> Tuple[int, int, int, int]:
        """
        将十六进制颜色和透明度转换为RGBA元组
        """
        hex_color = InputValidator.validate_color_hex(hex_color)
        opacity = InputValidator.validate_opacity(opacity)
        
        # 移除#前缀
        hex_color = hex_color.lstrip('#')
        
        # 转换为RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        return (r, g, b, opacity)


class NumericEntry:
    """数字输入框验证器"""
    
    @staticmethod
    def create_integer_validator(min_val: int = None, max_val: int = None, default: int = None):
        """
        创建整数输入验证函数
        """
        def validate(value):
            return str(InputValidator.validate_integer(value, min_val, max_val, default))
        return validate
    
    @staticmethod
    def create_float_validator(min_val: float = None, max_val: float = None, default: float = None):
        """
        创建浮点数输入验证函数
        """
        def validate(value):
            return str(InputValidator.validate_float(value, min_val, max_val, default))
        return validate


def register_numeric_validation(root, entry_widget, validator_func):
    """
    为Entry控件注册数字验证
    """
    vcmd = (root.register(validator_func), '%P')
    entry_widget.config(validate='key', validatecommand=vcmd)
    
    # 失去焦点时也验证
    def on_focus_out(event):
        current_value = entry_widget.get()
        validated_value = validator_func(current_value)
        if current_value != validated_value:
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, validated_value)
    
    entry_widget.bind('<FocusOut>', on_focus_out)