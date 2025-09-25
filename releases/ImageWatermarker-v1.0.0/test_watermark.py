#!/usr/bin/env python3
"""
水印功能测试脚本
用于验证核心水印功能是否正常工作
"""

import sys
from pathlib import Path
from PIL import Image

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.image_processor import ImageProcessor
from core.watermark import WatermarkProcessor, WatermarkPosition
from core.config_manager import ConfigManager


def test_basic_functionality():
    """测试基本功能"""
    print("开始测试基本功能...")
    
    # 初始化处理器
    image_processor = ImageProcessor()
    watermark_processor = WatermarkProcessor()
    config_manager = ConfigManager()
    
    print("✓ 处理器初始化成功")
    
    # 测试图片加载
    test_image_path = "test_images/H.jpg"
    if Path(test_image_path).exists():
        image_info = image_processor.load_image(test_image_path)
        if image_info:
            print(f"✓ 图片加载成功: {image_info['name']} ({image_info['size'][0]}x{image_info['size'][1]})")
            
            # 测试水印创建
            watermark = watermark_processor.create_text_watermark(
                text="测试水印",
                font_size=48,
                color=(255, 255, 255, 128)
            )
            
            if watermark:
                print("✓ 文本水印创建成功")
                
                # 测试水印应用
                result_image = watermark_processor.apply_watermark(
                    base_image=image_info['image'],
                    watermark=watermark,
                    position=WatermarkPosition.MIDDLE_CENTER,
                    margin=20
                )
                
                if result_image:
                    print("✓ 水印应用成功")
                    
                    # 测试图片保存
                    output_path = "test_images/_watermark/test_output.jpg"
                    Path(output_path).parent.mkdir(exist_ok=True)
                    
                    if image_processor.save_image(result_image, output_path, "JPEG", 95):
                        print(f"✓ 图片保存成功: {output_path}")
                    else:
                        print("✗ 图片保存失败")
                else:
                    print("✗ 水印应用失败")
            else:
                print("✗ 文本水印创建失败")
        else:
            print("✗ 图片加载失败")
    else:
        print(f"✗ 测试图片不存在: {test_image_path}")
    
    # 测试配置管理
    default_config = config_manager.get_default_watermark_config()
    if default_config:
        print("✓ 默认配置获取成功")
        
        # 测试模板保存
        export_config = config_manager.get_default_export_config()
        if config_manager.save_template("测试模板", default_config, export_config, "自动测试生成"):
            print("✓ 模板保存成功")
            
            # 测试模板加载
            template = config_manager.get_template("测试模板")
            if template:
                print("✓ 模板加载成功")
            else:
                print("✗ 模板加载失败")
        else:
            print("✗ 模板保存失败")
    else:
        print("✗ 默认配置获取失败")


def test_batch_processing():
    """测试批量处理"""
    print("\n开始测试批量处理...")
    
    image_processor = ImageProcessor()
    watermark_processor = WatermarkProcessor()
    
    # 加载测试图片文件夹
    test_folder = "test_images"
    if Path(test_folder).exists():
        images = image_processor.load_images_from_folder(test_folder)
        if images:
            print(f"✓ 批量加载成功: {len(images)} 张图片")
            
            # 创建水印配置
            watermark_config = {
                'type': 'text',
                'text': '批量水印测试',
                'font_size': 36,
                'color': (255, 0, 0, 128),  # 红色半透明
                'position': 'bottom_right',
                'margin': 15,
                'rotation': 0
            }
            
            # 批量应用水印
            results = watermark_processor.batch_apply_watermark(images, watermark_config)
            if results:
                print(f"✓ 批量水印应用成功: {len(results)} 张图片")
                
                # 保存结果
                output_dir = "test_images/_watermark"
                Path(output_dir).mkdir(exist_ok=True)
                
                success_count = 0
                for result in results:
                    output_path = image_processor.generate_output_filename(
                        result['path'], output_dir, 'suffix', '_batch_test', 'JPEG'
                    )
                    
                    if image_processor.save_image(
                        result['watermarked_image'], output_path, 'JPEG', 90
                    ):
                        success_count += 1
                
                print(f"✓ 批量保存成功: {success_count}/{len(results)} 张图片")
            else:
                print("✗ 批量水印应用失败")
        else:
            print("✗ 文件夹中没有找到图片")
    else:
        print(f"✗ 测试文件夹不存在: {test_folder}")


def test_different_positions():
    """测试不同位置的水印"""
    print("\n开始测试不同位置水印...")
    
    image_processor = ImageProcessor()
    watermark_processor = WatermarkProcessor()
    
    test_image_path = "test_images/H.jpg"
    if Path(test_image_path).exists():
        image_info = image_processor.load_image(test_image_path)
        if image_info:
            positions = [
                ("左上", WatermarkPosition.TOP_LEFT),
                ("上中", WatermarkPosition.TOP_CENTER),
                ("右上", WatermarkPosition.TOP_RIGHT),
                ("左中", WatermarkPosition.MIDDLE_LEFT),
                ("正中", WatermarkPosition.MIDDLE_CENTER),
                ("右中", WatermarkPosition.MIDDLE_RIGHT),
                ("左下", WatermarkPosition.BOTTOM_LEFT),
                ("下中", WatermarkPosition.BOTTOM_CENTER),
                ("右下", WatermarkPosition.BOTTOM_RIGHT)
            ]
            
            output_dir = "test_images/_watermark"
            Path(output_dir).mkdir(exist_ok=True)
            
            for pos_name, position in positions:
                # 创建位置特定的水印
                watermark = watermark_processor.create_text_watermark(
                    text=f"水印-{pos_name}",
                    font_size=32,
                    color=(0, 255, 0, 150)  # 绿色半透明
                )
                
                if watermark:
                    result_image = watermark_processor.apply_watermark(
                        base_image=image_info['image'],
                        watermark=watermark,
                        position=position,
                        margin=10
                    )
                    
                    if result_image:
                        output_path = f"{output_dir}/position_test_{pos_name}.jpg"
                        if image_processor.save_image(result_image, output_path, "JPEG", 95):
                            print(f"✓ {pos_name}位置水印测试成功")
                        else:
                            print(f"✗ {pos_name}位置水印保存失败")
                    else:
                        print(f"✗ {pos_name}位置水印应用失败")
                else:
                    print(f"✗ {pos_name}位置水印创建失败")
        else:
            print("✗ 测试图片加载失败")
    else:
        print(f"✗ 测试图片不存在: {test_image_path}")


def main():
    """主测试函数"""
    print("ImageWatermarker 功能测试")
    print("=" * 50)
    
    try:
        # 基本功能测试
        test_basic_functionality()
        
        # 批量处理测试
        test_batch_processing()
        
        # 位置测试
        test_different_positions()
        
        print("\n" + "=" * 50)
        print("测试完成！请检查 test_images/_watermark 文件夹中的输出结果。")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())