"""
文件处理工具模块
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Tuple


def get_safe_filename(filename: str) -> str:
    """
    获取安全的文件名，移除或替换不安全字符
    """
    # 不安全的字符
    unsafe_chars = '<>:"/\\|?*'
    safe_filename = filename
    
    for char in unsafe_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # 移除前后空格和点
    safe_filename = safe_filename.strip(' .')
    
    # 确保文件名不为空
    if not safe_filename:
        safe_filename = 'untitled'
    
    return safe_filename


def ensure_unique_filename(file_path: str) -> str:
    """
    确保文件名唯一，如果文件已存在则添加数字后缀
    """
    path = Path(file_path)
    
    if not path.exists():
        return file_path
    
    # 分离文件名和扩展名
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_path = parent / new_name
        
        if not new_path.exists():
            return str(new_path)
        
        counter += 1


def create_directory(dir_path: str) -> bool:
    """
    创建目录，如果不存在的话
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败 {dir_path}: {str(e)}")
        return False


def is_same_directory(path1: str, path2: str) -> bool:
    """
    检查两个路径是否指向同一个目录
    """
    try:
        return Path(path1).resolve() == Path(path2).resolve()
    except Exception:
        return False


def get_file_size(file_path: str) -> Optional[int]:
    """
    获取文件大小（字节）
    """
    try:
        return Path(file_path).stat().st_size
    except Exception:
        return None


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_available_fonts() -> List[str]:
    """
    获取系统可用字体列表
    """
    import platform
    
    fonts = []
    system = platform.system()
    
    if system == "Windows":
        font_dirs = [
            "C:/Windows/Fonts",
            os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts")
        ]
    elif system == "Darwin":  # macOS
        font_dirs = [
            "/System/Library/Fonts",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts")
        ]
    else:  # Linux
        font_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            os.path.expanduser("~/.fonts"),
            os.path.expanduser("~/.local/share/fonts")
        ]
    
    # 支持的字体格式
    font_extensions = {'.ttf', '.otf', '.ttc'}
    
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            try:
                for root, dirs, files in os.walk(font_dir):
                    for file in files:
                        if Path(file).suffix.lower() in font_extensions:
                            font_path = os.path.join(root, file)
                            fonts.append(font_path)
            except PermissionError:
                continue
    
    return sorted(fonts)


def get_font_name_from_path(font_path: str) -> str:
    """
    从字体文件路径获取字体名称
    """
    return Path(font_path).stem


def validate_output_directory(output_dir: str, input_files: List[str]) -> Tuple[bool, str]:
    """
    验证输出目录是否有效
    返回 (是否有效, 错误信息)
    """
    if not output_dir:
        return False, "请选择输出目录"
    
    output_path = Path(output_dir)
    
    # 检查目录是否存在，如果不存在尝试创建
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"无法创建输出目录: {str(e)}"
    
    # 检查是否有写入权限
    if not os.access(output_path, os.W_OK):
        return False, "输出目录没有写入权限"
    
    # 检查是否与输入文件在同一目录（防止覆盖原文件）
    for input_file in input_files:
        input_dir = Path(input_file).parent
        if is_same_directory(str(output_path), str(input_dir)):
            return False, "输出目录不能与输入文件在同一目录，以防止覆盖原文件"
    
    return True, ""


def backup_file(file_path: str, backup_dir: str = None) -> Optional[str]:
    """
    备份文件
    """
    try:
        source_path = Path(file_path)
        
        if backup_dir:
            backup_path = Path(backup_dir) / source_path.name
        else:
            backup_path = source_path.with_suffix(f".backup{source_path.suffix}")
        
        # 确保备份目录存在
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果备份文件已存在，生成唯一名称
        backup_path = Path(ensure_unique_filename(str(backup_path)))
        
        shutil.copy2(source_path, backup_path)
        return str(backup_path)
        
    except Exception as e:
        print(f"备份文件失败 {file_path}: {str(e)}")
        return None


def clean_temp_files(temp_dir: str, max_age_hours: int = 24):
    """
    清理临时文件
    """
    try:
        import time
        
        temp_path = Path(temp_dir)
        if not temp_path.exists():
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for file_path in temp_path.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
                        
    except Exception as e:
        print(f"清理临时文件失败: {str(e)}")