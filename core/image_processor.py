"""
图像处理核心模块
负责图片的加载、保存、格式转换和尺寸调整
"""

import os
from PIL import Image, ImageTk
from pathlib import Path
from typing import List, Tuple, Optional, Union


class ImageProcessor:
    """图像处理器"""
    
    # 支持的输入格式
    SUPPORTED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    # 支持的输出格式
    SUPPORTED_OUTPUT_FORMATS = {'JPEG', 'PNG'}
    
    def __init__(self):
        self.images = []  # 存储加载的图片信息
        
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_INPUT_FORMATS
    
    def load_image(self, file_path: str) -> Optional[dict]:
        """
        加载单张图片
        返回包含图片信息的字典
        """
        try:
            if not self.is_supported_format(file_path):
                raise ValueError(f"不支持的文件格式: {file_path}")
            
            # 打开图片
            image = Image.open(file_path)
            
            # 如果是RGBA模式但保存为JPEG，需要转换
            if image.mode == 'RGBA':
                # 保持RGBA模式以支持透明度
                pass
            elif image.mode not in ('RGB', 'RGBA', 'L'):
                # 转换为RGB模式
                image = image.convert('RGB')
            
            # 创建图片信息字典
            image_info = {
                'path': file_path,
                'name': Path(file_path).name,
                'image': image,
                'size': image.size,
                'mode': image.mode,
                'format': image.format
            }
            
            return image_info
            
        except Exception as e:
            print(f"加载图片失败 {file_path}: {str(e)}")
            return None
    
    def load_images(self, file_paths: List[str]) -> List[dict]:
        """批量加载图片"""
        loaded_images = []
        for file_path in file_paths:
            image_info = self.load_image(file_path)
            if image_info:
                loaded_images.append(image_info)
        return loaded_images
    
    def load_images_from_folder(self, folder_path: str) -> List[dict]:
        """从文件夹加载所有支持的图片"""
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return []
        
        image_files = []
        for file_path in folder.iterdir():
            if file_path.is_file() and self.is_supported_format(str(file_path)):
                image_files.append(str(file_path))
        
        return self.load_images(image_files)
    
    def create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (150, 150)) -> Image.Image:
        """创建缩略图"""
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        return thumbnail
    
    def resize_image(self, image: Image.Image, width: Optional[int] = None, 
                    height: Optional[int] = None, scale_percent: Optional[float] = None) -> Image.Image:
        """
        调整图片尺寸
        可以按宽度、高度或百分比缩放
        """
        original_width, original_height = image.size
        
        if scale_percent:
            # 按百分比缩放
            new_width = int(original_width * scale_percent / 100)
            new_height = int(original_height * scale_percent / 100)
        elif width and height:
            # 指定宽度和高度
            new_width, new_height = width, height
        elif width:
            # 按宽度等比缩放
            ratio = width / original_width
            new_width = width
            new_height = int(original_height * ratio)
        elif height:
            # 按高度等比缩放
            ratio = height / original_height
            new_width = int(original_width * ratio)
            new_height = height
        else:
            # 没有指定尺寸，返回原图
            return image
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def save_image(self, image: Image.Image, output_path: str, 
                  format: str = 'JPEG', quality: int = 95) -> bool:
        """
        保存图片
        """
        try:
            # 确保输出目录存在
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 处理不同格式的保存
            if format.upper() == 'JPEG':
                # JPEG不支持透明度，需要转换RGBA到RGB
                if image.mode == 'RGBA':
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为mask
                    image = background
                elif image.mode not in ('RGB', 'L'):
                    image = image.convert('RGB')
                
                image.save(output_path, format='JPEG', quality=quality, optimize=True)
            
            elif format.upper() == 'PNG':
                # PNG支持透明度
                if image.mode not in ('RGBA', 'RGB', 'L'):
                    image = image.convert('RGBA')
                
                image.save(output_path, format='PNG', optimize=True)
            
            else:
                raise ValueError(f"不支持的输出格式: {format}")
            
            return True
            
        except Exception as e:
            print(f"保存图片失败 {output_path}: {str(e)}")
            return False
    
    def generate_output_filename(self, original_path: str, output_dir: str, 
                               naming_rule: str, custom_text: str = "", 
                               output_format: str = "JPEG") -> str:
        """
        生成输出文件名
        naming_rule: 'original', 'prefix', 'suffix'
        """
        original_name = Path(original_path).stem
        
        if naming_rule == 'prefix':
            new_name = f"{custom_text}{original_name}"
        elif naming_rule == 'suffix':
            new_name = f"{original_name}{custom_text}"
        else:  # 'original'
            new_name = original_name
        
        # 确定文件扩展名
        ext = '.jpg' if output_format.upper() == 'JPEG' else '.png'
        
        return str(Path(output_dir) / f"{new_name}{ext}")
    
    def get_image_info(self, image: Image.Image) -> dict:
        """获取图片详细信息"""
        return {
            'size': image.size,
            'mode': image.mode,
            'format': getattr(image, 'format', 'Unknown'),
            'width': image.size[0],
            'height': image.size[1]
        }