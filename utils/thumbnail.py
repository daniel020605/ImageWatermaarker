"""
缩略图管理模块
"""

import os
from typing import Dict, Tuple, Optional
from PIL import Image, ImageTk
import hashlib


class ThumbnailManager:
    """缩略图管理器"""
    
    def __init__(self, cache_size: int = 100):
        """
        初始化缩略图管理器
        
        Args:
            cache_size: 缓存大小
        """
        self.cache_size = cache_size
        self.thumbnail_cache: Dict[str, ImageTk.PhotoImage] = {}
        self.access_order = []  # 用于LRU缓存
    
    def get_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (64, 64)) -> ImageTk.PhotoImage:
        """
        获取图片的缩略图
        
        Args:
            image: PIL图片对象
            size: 缩略图尺寸
            
        Returns:
            tkinter可显示的缩略图
        """
        # 生成缓存键
        cache_key = self._generate_cache_key(image, size)
        
        # 检查缓存
        if cache_key in self.thumbnail_cache:
            self._update_access_order(cache_key)
            return self.thumbnail_cache[cache_key]
        
        # 生成缩略图
        thumbnail = self._create_thumbnail(image, size)
        
        # 添加到缓存
        self._add_to_cache(cache_key, thumbnail)
        
        return thumbnail
    
    def _generate_cache_key(self, image: Image.Image, size: Tuple[int, int]) -> str:
        """生成缓存键"""
        # 使用图片尺寸、模式和目标尺寸生成键
        image_info = f"{image.size}_{image.mode}_{size}"
        return hashlib.md5(image_info.encode()).hexdigest()
    
    def _create_thumbnail(self, image: Image.Image, size: Tuple[int, int]) -> ImageTk.PhotoImage:
        """创建缩略图"""
        # 创建缩略图副本
        thumbnail = image.copy()
        
        # 计算缩放比例，保持宽高比
        img_width, img_height = thumbnail.size
        thumb_width, thumb_height = size
        
        # 计算缩放比例
        width_ratio = thumb_width / img_width
        height_ratio = thumb_height / img_height
        scale_ratio = min(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(img_width * scale_ratio)
        new_height = int(img_height * scale_ratio)
        
        # 调整尺寸
        thumbnail = thumbnail.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建背景（居中显示）
        background = Image.new('RGB', size, (240, 240, 240))
        
        # 计算粘贴位置（居中）
        paste_x = (thumb_width - new_width) // 2
        paste_y = (thumb_height - new_height) // 2
        
        # 粘贴缩略图到背景
        if thumbnail.mode == 'RGBA':
            background.paste(thumbnail, (paste_x, paste_y), thumbnail)
        else:
            background.paste(thumbnail, (paste_x, paste_y))
        
        # 转换为tkinter可用格式
        return ImageTk.PhotoImage(background)
    
    def _add_to_cache(self, cache_key: str, thumbnail: ImageTk.PhotoImage):
        """添加到缓存"""
        # 如果缓存已满，删除最久未使用的项
        if len(self.thumbnail_cache) >= self.cache_size:
            oldest_key = self.access_order.pop(0)
            if oldest_key in self.thumbnail_cache:
                del self.thumbnail_cache[oldest_key]
        
        # 添加新项
        self.thumbnail_cache[cache_key] = thumbnail
        self.access_order.append(cache_key)
    
    def _update_access_order(self, cache_key: str):
        """更新访问顺序"""
        if cache_key in self.access_order:
            self.access_order.remove(cache_key)
        self.access_order.append(cache_key)
    
    def clear_cache(self):
        """清空缓存"""
        self.thumbnail_cache.clear()
        self.access_order.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """获取缓存信息"""
        return {
            'cache_size': len(self.thumbnail_cache),
            'max_size': self.cache_size
        }


class ThumbnailGenerator:
    """缩略图生成器（静态方法）"""
    
    @staticmethod
    def create_thumbnail(image: Image.Image, size: Tuple[int, int], 
                        background_color: Tuple[int, int, int] = (240, 240, 240)) -> Image.Image:
        """
        创建缩略图
        
        Args:
            image: 原图
            size: 目标尺寸
            background_color: 背景颜色
            
        Returns:
            缩略图
        """
        # 创建副本
        thumbnail = image.copy()
        
        # 计算缩放比例
        img_width, img_height = thumbnail.size
        thumb_width, thumb_height = size
        
        width_ratio = thumb_width / img_width
        height_ratio = thumb_height / img_height
        scale_ratio = min(width_ratio, height_ratio)
        
        # 调整尺寸
        new_width = int(img_width * scale_ratio)
        new_height = int(img_height * scale_ratio)
        
        thumbnail = thumbnail.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建背景
        background = Image.new('RGB', size, background_color)
        
        # 居中粘贴
        paste_x = (thumb_width - new_width) // 2
        paste_y = (thumb_height - new_height) // 2
        
        if thumbnail.mode == 'RGBA':
            background.paste(thumbnail, (paste_x, paste_y), thumbnail)
        else:
            background.paste(thumbnail, (paste_x, paste_y))
        
        return background
    
    @staticmethod
    def create_file_thumbnail(file_path: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """
        从文件创建缩略图
        
        Args:
            file_path: 图片文件路径
            size: 目标尺寸
            
        Returns:
            缩略图，失败返回None
        """
        try:
            with Image.open(file_path) as image:
                return ThumbnailGenerator.create_thumbnail(image, size)
        except Exception as e:
            print(f"创建缩略图失败 {file_path}: {e}")
            return None
    
    @staticmethod
    def create_placeholder_thumbnail(size: Tuple[int, int], text: str = "无图片") -> Image.Image:
        """
        创建占位符缩略图
        
        Args:
            size: 尺寸
            text: 显示文本
            
        Returns:
            占位符缩略图
        """
        from PIL import ImageDraw, ImageFont
        
        # 创建背景
        thumbnail = Image.new('RGB', size, (200, 200, 200))
        draw = ImageDraw.Draw(thumbnail)
        
        # 绘制边框
        draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=(150, 150, 150))
        
        # 绘制文本
        try:
            # 尝试使用默认字体
            font = ImageFont.load_default()
        except:
            font = None
        
        # 计算文本位置
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(text) * 6  # 估算
            text_height = 11
        
        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2
        
        draw.text((text_x, text_y), text, fill=(100, 100, 100), font=font)
        
        return thumbnail