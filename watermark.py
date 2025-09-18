#!/usr/bin/env python3
"""
Image Watermark Tool - Adds EXIF timestamp watermarks to images
"""

import os
import argparse
from PIL import Image, ImageDraw, ImageFont
import exifread
from datetime import datetime


def get_exif_date(image_path):
    """Extract date from EXIF data"""
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        # Try different EXIF date fields
        date_fields = ['EXIF DateTimeOriginal', 'Image DateTime', 'EXIF DateTimeDigitized']

        for field in date_fields:
            if field in tags:
                date_str = str(tags[field])
                # Parse date string (format: YYYY:MM:DD HH:MM:SS)
                if ':' in date_str:
                    date_part = date_str.split()[0]  # Get YYYY:MM:DD part
                    return date_part.replace(':', '-')

        return None
    except Exception as e:
        print(f"Error reading EXIF from {image_path}: {e}")
        return None


def add_watermark(input_path, output_path, font_size=24, color='white', position='bottom-right'):
    """Add watermark to image"""
    try:
        # Get date from EXIF
        date_text = get_exif_date(input_path)
        if not date_text:
            print(f"No date found in EXIF for {input_path}")
            return False

        # Open image
        image = Image.open(input_path)
        draw = ImageDraw.Draw(image)

        # Create font (using default font)
        try:
            font = ImageFont.truetype("Arial", font_size)
        except:
            font = ImageFont.load_default()

        # Calculate text position
        text_bbox = draw.textbbox((0, 0), date_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        img_width, img_height = image.size

        # Position mapping
        positions = {
            'top-left': (10, 10),
            'top-right': (img_width - text_width - 10, 10),
            'bottom-left': (10, img_height - text_height - 10),
            'bottom-right': (img_width - text_width - 10, img_height - text_height - 10),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2)
        }

        x, y = positions.get(position, positions['bottom-right'])

        # Add text with shadow for better visibility
        shadow_color = 'black' if color == 'white' else 'white'
        draw.text((x+1, y+1), date_text, font=font, fill=shadow_color)
        draw.text((x, y), date_text, font=font, fill=color)

        # Save image
        image.save(output_path)
        print(f"Watermarked: {output_path}")
        return True

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def process_directory(input_dir, font_size=24, color='white', position='bottom-right'):
    """Process all images in directory"""
    # Create output directory
    output_dir = os.path.join(input_dir, f"{os.path.basename(input_dir)}_watermark")
    os.makedirs(output_dir, exist_ok=True)

    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.webp'}

    processed = 0
    skipped = 0

    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        if os.path.isfile(file_path) and any(filename.lower().endswith(ext) for ext in image_extensions):
            output_path = os.path.join(output_dir, filename)

            if add_watermark(file_path, output_path, font_size, color, position):
                processed += 1
            else:
                skipped += 1

    print(f"\nProcessing complete!")
    print(f"Processed: {processed} images")
    print(f"Skipped: {skipped} images")
    print(f"Output directory: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Add EXIF timestamp watermarks to images')
    parser.add_argument('input_dir', help='Input directory containing images')
    parser.add_argument('--font-size', type=int, default=24, help='Font size (default: 24)')
    parser.add_argument('--color', default='white', help='Text color (default: white)')
    parser.add_argument('--position', default='bottom-right',
                       choices=['top-left', 'top-right', 'bottom-left', 'bottom-right', 'center'],
                       help='Watermark position (default: bottom-right)')

    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: {args.input_dir} is not a valid directory")
        return

    process_directory(args.input_dir, args.font_size, args.color, args.position)


if __name__ == "__main__":
    main()