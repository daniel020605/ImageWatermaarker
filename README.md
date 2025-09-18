# Image Watermark Tool

A command-line tool for adding timestamp watermarks to images based on EXIF metadata or file modification time.

## Features

- 📅 **EXIF Date Extraction**: Automatically extracts shooting dates from image EXIF metadata
- 🎨 **Customizable Watermarks**: Adjust font size, text color, and position
- 📍 **Multiple Positions**: Support for top-left, top-right, bottom-left, bottom-right, and center positions
- 🔄 **Fallback Handling**: Uses file modification time when EXIF data is unavailable
- 📁 **Batch Processing**: Processes all images in a directory automatically
- 🗂️ **Smart Output**: Creates organized output directory structure

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ImageWatermarker
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

```bash
python3 watermark.py [input_directory] [options]
```

### Options

- `--font-size`: Font size for watermark text (default: 24)
- `--color`: Text color (default: white)
- `--position`: Watermark position - choices: `top-left`, `top-right`, `bottom-left`, `bottom-right`, `center` (default: bottom-right)

### Examples

1. Basic usage with default settings:
```bash
python3 watermark.py ./photos
```

2. Custom font size and color:
```bash
python3 watermark.py ./photos --font-size 30 --color black
```

3. Top-left positioning:
```bash
python3 watermark.py ./photos --position top-left
```

4. All custom options:
```bash
python3 watermark.py ./photos --font-size 36 --color yellow --position center
```

## Output

Processed images are saved in a new subdirectory named `[original_directory]_watermark` with the same filenames.

## Supported Image Formats

- JPEG/JPG
- PNG
- TIFF
- BMP
- WebP

## Dependencies

- Python 3.6+
- Pillow >= 10.0.0
- exifread >= 3.0.0

## License

MIT License
