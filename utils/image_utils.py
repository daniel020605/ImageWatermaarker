"""
图像处理工具模块
"""

from PIL import Image, ImageTk
import tkinter as tk
from typing import Tuple, Optional, Union
import io
import base64


def pil_to_tkinter(pil_image: Image.Image) -> ImageTk.PhotoImage:
    """
    将PIL图像转换为Tkinter可显示的PhotoImage
    """
    # 确保图像模式兼容
    if pil_image.mode not in ('RGB', 'RGBA', 'L'):
        pil_image = pil_image.convert('RGB')
    
    photo = ImageTk.PhotoImage(pil_image)
    
    # 保持引用防止垃圾回收
    if not hasattr(pil_to_tkinter, '_photo_refs'):
        pil_to_tkinter._photo_refs = []
    pil_to_tkinter._photo_refs.append(photo)
    
    # 限制引用数量，避免内存泄漏
    if len(pil_to_tkinter._photo_refs) > 100:
        pil_to_tkinter._photo_refs = pil_to_tkinter._photo_refs[-50:]
    
    return photo


def resize_for_display(image: Image.Image, max_size: Tuple[int, int], 
                      maintain_aspect: bool = True) -> Image.Image:
    """
    调整图像大小以适合显示区域
    """
    if not maintain_aspect:
        return image.resize(max_size, Image.Resampling.LANCZOS)
    
    # 计算缩放比例
    img_width, img_height = image.size
    max_width, max_height = max_size
    
    # 计算宽度和高度的缩放比例
    width_ratio = max_width / img_width
    height_ratio = max_height / img_height
    
    # 选择较小的比例以确保图像完全适合
    scale_ratio = min(width_ratio, height_ratio)
    
    # 如果图像已经足够小，不需要缩放
    if scale_ratio >= 1.0:
        return image
    
    # 计算新尺寸
    new_width = int(img_width * scale_ratio)
    new_height = int(img_height * scale_ratio)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def create_thumbnail_with_border(image: Image.Image, size: Tuple[int, int], 
                                border_color: Tuple[int, int, int] = (200, 200, 200),
                                border_width: int = 1) -> Image.Image:
    """
    创建带边框的缩略图
    """
    # 创建缩略图
    thumbnail = image.copy()
    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
    
    # 创建带边框的图像
    bordered_size = (size[0] + border_width * 2, size[1] + border_width * 2)
    bordered_image = Image.new('RGB', bordered_size, border_color)
    
    # 计算居中位置
    paste_x = (bordered_size[0] - thumbnail.size[0]) // 2
    paste_y = (bordered_size[1] - thumbnail.size[1]) // 2
    
    # 粘贴缩略图
    bordered_image.paste(thumbnail, (paste_x, paste_y))
    
    return bordered_image


def get_image_aspect_ratio(image: Image.Image) -> float:
    """
    获取图像宽高比
    """
    width, height = image.size
    return width / height if height != 0 else 1.0


def calculate_fit_size(image_size: Tuple[int, int], container_size: Tuple[int, int]) -> Tuple[int, int]:
    """
    计算图像适合容器的尺寸（保持宽高比）
    """
    img_width, img_height = image_size
    container_width, container_height = container_size
    
    # 计算缩放比例
    width_ratio = container_width / img_width
    height_ratio = container_height / img_height
    
    # 选择较小的比例
    scale_ratio = min(width_ratio, height_ratio)
    
    # 计算新尺寸
    new_width = int(img_width * scale_ratio)
    new_height = int(img_height * scale_ratio)
    
    return new_width, new_height


def create_preview_image(base_image: Image.Image, watermark_image: Image.Image,
                        position: Tuple[int, int], preview_size: Tuple[int, int]) -> Image.Image:
    """
    创建预览图像
    """
    # 首先调整基础图像大小以适合预览
    preview_base = resize_for_display(base_image, preview_size)
    
    # 计算缩放比例
    scale_x = preview_base.size[0] / base_image.size[0]
    scale_y = preview_base.size[1] / base_image.size[1]
    
    # 调整水印大小和位置
    watermark_width = int(watermark_image.size[0] * scale_x)
    watermark_height = int(watermark_image.size[1] * scale_y)
    preview_watermark = watermark_image.resize((watermark_width, watermark_height), Image.Resampling.LANCZOS)
    
    # 调整水印位置
    preview_position = (
        int(position[0] * scale_x),
        int(position[1] * scale_y)
    )
    
    # 确保基础图像有透明通道
    if preview_base.mode != 'RGBA':
        preview_base = preview_base.convert('RGBA')
    
    # 粘贴水印
    preview_base.paste(preview_watermark, preview_position, preview_watermark)
    
    return preview_base


def image_to_base64(image: Image.Image, format: str = 'PNG') -> str:
    """
    将PIL图像转换为base64字符串
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str


def base64_to_image(base64_str: str) -> Optional[Image.Image]:
    """
    将base64字符串转换为PIL图像
    """
    try:
        img_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(img_data))
        return image
    except Exception as e:
        print(f"base64转图像失败: {str(e)}")
        return None


def get_dominant_color(image: Image.Image, num_colors: int = 5) -> Tuple[int, int, int]:
    """
    获取图像的主要颜色
    """
    try:
        # 缩小图像以提高性能
        small_image = image.resize((50, 50))
        
        # 转换为RGB模式
        if small_image.mode != 'RGB':
            small_image = small_image.convert('RGB')
        
        # 获取颜色统计
        colors = small_image.getcolors(maxcolors=256*256*256)
        
        if colors:
            # 按出现频率排序
            colors.sort(key=lambda x: x[0], reverse=True)
            # 返回最常见的颜色
            return colors[0][1]
        else:
            # 如果无法获取颜色，返回白色
            return (255, 255, 255)
            
    except Exception:
        return (255, 255, 255)


def create_gradient_background(size: Tuple[int, int], 
                             start_color: Tuple[int, int, int] = (240, 240, 240),
                             end_color: Tuple[int, int, int] = (200, 200, 200),
                             direction: str = 'vertical') -> Image.Image:
    """
    创建渐变背景
    direction: 'vertical', 'horizontal', 'diagonal'
    """
    width, height = size
    image = Image.new('RGB', size)
    
    if direction == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            for x in range(width):
                image.putpixel((x, y), (r, g, b))
    
    elif direction == 'horizontal':
        for x in range(width):
            ratio = x / width
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            
            for y in range(height):
                image.putpixel((x, y), (r, g, b))
    
    return image


def add_drop_shadow(image: Image.Image, offset: Tuple[int, int] = (5, 5),
                   shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 128),
                   blur_radius: int = 3) -> Image.Image:
    """
    为图像添加阴影效果
    """
    try:
        from PIL import ImageFilter
        
        # 确保图像有透明通道
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 创建阴影图像
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow.paste(shadow_color, (0, 0, image.size[0], image.size[1]))
        
        # 使用原图的alpha通道作为阴影的mask
        shadow.putalpha(image.split()[-1])
        
        # 模糊阴影
        if blur_radius > 0:
            shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
        
        # 创建结果图像
        result_size = (
            image.size[0] + abs(offset[0]),
            image.size[1] + abs(offset[1])
        )
        result = Image.new('RGBA', result_size, (0, 0, 0, 0))
        
        # 粘贴阴影
        shadow_pos = (
            max(0, offset[0]),
            max(0, offset[1])
        )
        result.paste(shadow, shadow_pos, shadow)
        
        # 粘贴原图
        image_pos = (
            max(0, -offset[0]),
            max(0, -offset[1])
        )
        result.paste(image, image_pos, image)
        
        return result
        
    except ImportError:
        # 如果没有ImageFilter，返回原图
        return image
    except Exception as e:
        print(f"添加阴影失败: {str(e)}")
        return image


def validate_image_file(file_path: str) -> Tuple[bool, str]:
    """
    验证图像文件是否有效
    返回 (是否有效, 错误信息)
    """
    try:
        with Image.open(file_path) as img:
            # 尝试加载图像数据
            img.load()
            return True, ""
    except Exception as e:
        return False, f"无效的图像文件: {str(e)}"