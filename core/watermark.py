"""
水印处理模块
负责文本水印和图片水印的生成与应用
"""

import math
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Union
from enum import Enum


class WatermarkPosition(Enum):
    """水印位置枚举"""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_CENTER = "middle_center"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"
    CUSTOM = "custom"


class WatermarkProcessor:
    """水印处理器"""
    
    def __init__(self):
        self.default_font_size = 36
        self.default_font_color = (255, 255, 255, 128)  # 白色，50%透明度
        self.default_margin = 20  # 边距
    
    def calculate_position(self, image_size: Tuple[int, int], 
                          watermark_size: Tuple[int, int],
                          position: WatermarkPosition,
                          custom_pos: Optional[Tuple[int, int]] = None,
                          margin: int = None) -> Tuple[int, int]:
        """
        计算水印位置
        """
        if margin is None:
            margin = self.default_margin
            
        img_width, img_height = image_size
        wm_width, wm_height = watermark_size
        
        if position == WatermarkPosition.CUSTOM and custom_pos:
            return custom_pos
        
        # 九宫格位置计算
        positions = {
            WatermarkPosition.TOP_LEFT: (margin, margin),
            WatermarkPosition.TOP_CENTER: ((img_width - wm_width) // 2, margin),
            WatermarkPosition.TOP_RIGHT: (img_width - wm_width - margin, margin),
            WatermarkPosition.MIDDLE_LEFT: (margin, (img_height - wm_height) // 2),
            WatermarkPosition.MIDDLE_CENTER: ((img_width - wm_width) // 2, (img_height - wm_height) // 2),
            WatermarkPosition.MIDDLE_RIGHT: (img_width - wm_width - margin, (img_height - wm_height) // 2),
            WatermarkPosition.BOTTOM_LEFT: (margin, img_height - wm_height - margin),
            WatermarkPosition.BOTTOM_CENTER: ((img_width - wm_width) // 2, img_height - wm_height - margin),
            WatermarkPosition.BOTTOM_RIGHT: (img_width - wm_width - margin, img_height - wm_height - margin)
        }
        
        return positions.get(position, positions[WatermarkPosition.MIDDLE_CENTER])
    
    def get_font(self, font_name: str = None, font_size: int = None) -> ImageFont.ImageFont:
        """
        获取字体对象
        """
        if font_size is None:
            font_size = self.default_font_size
            
        try:
            if font_name:
                # 尝试加载指定字体
                font = ImageFont.truetype(font_name, font_size)
            else:
                # 使用默认字体
                font = ImageFont.load_default()
        except (OSError, IOError):
            # 字体加载失败，使用默认字体
            font = ImageFont.load_default()
            
        return font
    
    def create_text_watermark(self, text: str, font_name: str = None, 
                            font_size: int = None, color: Tuple[int, int, int, int] = None,
                            bold: bool = False, italic: bool = False,
                            shadow: bool = False, stroke: bool = False,
                            stroke_width: int = 2, stroke_color: Tuple[int, int, int, int] = None) -> Image.Image:
        """
        创建文本水印图像
        """
        if color is None:
            color = self.default_font_color
        if stroke_color is None:
            stroke_color = (0, 0, 0, 255)  # 黑色描边
            
        font = self.get_font(font_name, font_size)
        
        # 获取文本尺寸
        # 创建临时图像来测量文本尺寸
        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # 计算文本边界框
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 为描边和阴影预留空间
        padding = stroke_width * 2 if stroke else 0
        shadow_offset = 3 if shadow else 0
        
        # 创建水印图像
        watermark_width = text_width + padding * 2 + shadow_offset
        watermark_height = text_height + padding * 2 + shadow_offset
        watermark = Image.new('RGBA', (watermark_width, watermark_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 文本位置
        text_x = padding
        text_y = padding
        
        # 绘制阴影
        if shadow:
            shadow_color = (0, 0, 0, color[3] // 2)  # 半透明黑色阴影
            draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
                     font=font, fill=shadow_color)
        
        # 绘制描边
        if stroke:
            # 绘制描边（通过在周围绘制多次文本实现）
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), text, 
                                font=font, fill=stroke_color)
        
        # 绘制主文本
        draw.text((text_x, text_y), text, font=font, fill=color)
        
        return watermark
    
    def create_image_watermark(self, watermark_path: str, 
                             scale_percent: float = 100.0,
                             opacity: int = 255) -> Optional[Image.Image]:
        """
        创建图片水印
        """
        try:
            watermark = Image.open(watermark_path)
            
            # 确保图片有透明通道
            if watermark.mode != 'RGBA':
                watermark = watermark.convert('RGBA')
            
            # 缩放水印
            if scale_percent != 100.0:
                original_size = watermark.size
                new_size = (
                    int(original_size[0] * scale_percent / 100),
                    int(original_size[1] * scale_percent / 100)
                )
                watermark = watermark.resize(new_size, Image.Resampling.LANCZOS)
            
            # 调整透明度
            if opacity < 255:
                # 获取alpha通道
                alpha = watermark.split()[-1]
                # 调整alpha值
                alpha = alpha.point(lambda p: int(p * opacity / 255))
                # 重新组合
                watermark.putalpha(alpha)
            
            return watermark
            
        except Exception as e:
            print(f"创建图片水印失败: {str(e)}")
            return None
    
    def rotate_watermark(self, watermark: Image.Image, angle: float) -> Image.Image:
        """
        旋转水印
        """
        if angle == 0:
            return watermark
            
        # 旋转图像，保持透明背景
        rotated = watermark.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))
        return rotated
    
    def apply_watermark(self, base_image: Image.Image, watermark: Image.Image,
                       position: WatermarkPosition = WatermarkPosition.MIDDLE_CENTER,
                       custom_pos: Optional[Tuple[int, int]] = None,
                       margin: int = None,
                       rotation: float = 0) -> Image.Image:
        """
        将水印应用到基础图像上
        """
        # 确保基础图像有透明通道
        if base_image.mode != 'RGBA':
            base_image = base_image.convert('RGBA')
        
        # 旋转水印
        if rotation != 0:
            watermark = self.rotate_watermark(watermark, rotation)
        
        # 计算水印位置
        wm_pos = self.calculate_position(
            base_image.size, 
            watermark.size, 
            position, 
            custom_pos, 
            margin
        )
        
        # 创建结果图像
        result = base_image.copy()
        
        # 粘贴水印
        result.paste(watermark, wm_pos, watermark)
        
        return result
    
    def batch_apply_watermark(self, images: list, watermark_config: dict) -> list:
        """
        批量应用水印
        watermark_config包含水印的所有配置信息
        """
        results = []
        
        for image_info in images:
            try:
                base_image = image_info['image']
                
                # 根据配置创建水印
                if watermark_config['type'] == 'text':
                    watermark = self.create_text_watermark(
                        text=watermark_config['text'],
                        font_name=watermark_config.get('font_name'),
                        font_size=watermark_config.get('font_size', self.default_font_size),
                        color=watermark_config.get('color', self.default_font_color),
                        bold=watermark_config.get('bold', False),
                        italic=watermark_config.get('italic', False),
                        shadow=watermark_config.get('shadow', False),
                        stroke=watermark_config.get('stroke', False),
                        stroke_width=watermark_config.get('stroke_width', 2),
                        stroke_color=watermark_config.get('stroke_color')
                    )
                elif watermark_config['type'] == 'image':
                    watermark = self.create_image_watermark(
                        watermark_path=watermark_config['image_path'],
                        scale_percent=watermark_config.get('scale_percent', 100.0),
                        opacity=watermark_config.get('opacity', 255)
                    )
                else:
                    continue
                
                if watermark is None:
                    continue
                
                # 应用水印
                result_image = self.apply_watermark(
                    base_image=base_image,
                    watermark=watermark,
                    position=WatermarkPosition(watermark_config.get('position', 'middle_center')),
                    custom_pos=watermark_config.get('custom_pos'),
                    margin=watermark_config.get('margin'),
                    rotation=watermark_config.get('rotation', 0)
                )
                
                # 创建结果信息
                result_info = image_info.copy()
                result_info['watermarked_image'] = result_image
                results.append(result_info)
                
            except Exception as e:
                print(f"处理图片失败 {image_info.get('name', 'Unknown')}: {str(e)}")
                continue
        
        return results