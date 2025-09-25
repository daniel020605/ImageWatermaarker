#!/usr/bin/env python3
"""
GitHub Release 创建脚本
用于自动创建GitHub Release并上传文件
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 项目信息
PROJECT_NAME = "ImageWatermarker"
VERSION = "1.0.0"
TAG_NAME = f"v{VERSION}"

def check_git_status():
    """检查Git状态"""
    print("🔍 检查Git状态...")
    
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  发现未提交的更改:")
            print(result.stdout)
            return False
        
        # 检查是否有远程仓库
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, check=True)
        
        if not result.stdout.strip():
            print("❌ 未找到远程仓库，请先添加GitHub远程仓库")
            print("示例: git remote add origin https://github.com/username/ImageWatermarker.git")
            return False
        
        print("✅ Git状态检查通过")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git命令执行失败: {e}")
        return False

def create_tag():
    """创建Git标签"""
    print(f"🏷️  创建标签 {TAG_NAME}...")
    
    try:
        # 创建带注释的标签
        tag_message = f"{PROJECT_NAME} v{VERSION}\n\n首次发布版本，包含完整的图片水印功能。"
        
        subprocess.run(['git', 'tag', '-a', TAG_NAME, '-m', tag_message], 
                      check=True)
        
        print(f"✅ 标签 {TAG_NAME} 创建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        if "already exists" in str(e):
            print(f"⚠️  标签 {TAG_NAME} 已存在")
            return True
        else:
            print(f"❌ 创建标签失败: {e}")
            return False

def push_to_github():
    """推送到GitHub"""
    print("📤 推送到GitHub...")
    
    try:
        # 推送代码
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ 代码推送成功")
        
        # 推送标签
        subprocess.run(['git', 'push', 'origin', TAG_NAME], check=True)
        print("✅ 标签推送成功")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送失败: {e}")
        return False

def create_release_notes():
    """创建发布说明"""
    release_notes = f"""# {PROJECT_NAME} v{VERSION} 🎉

## 新功能特性

### 🖼️ 图片处理
- 支持多种格式导入: JPEG, PNG, BMP, TIFF
- PNG透明通道完全支持
- 批量图片处理能力
- 智能防覆盖机制

### 🎨 水印功能
- 文本水印自定义 (内容、大小、颜色、透明度)
- 九宫格位置布局系统
- 水印旋转功能 (0-360度)
- 实时预览效果

### ⚙️ 高级功能
- 水印模板保存和管理
- 灵活的导出设置
- 多种文件命名规则
- JPEG质量调节

### 🖥️ 用户界面
- 直观易用的图形界面
- 处理进度显示
- 状态反馈系统
- 跨平台支持 (Windows/macOS)

## 安装使用

### 系统要求
- Python 3.8+
- 支持的系统: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### 快速开始
1. 下载发布包并解压
2. Windows: 双击 `启动程序.bat`
3. macOS/Linux: 运行 `./启动程序.sh`

### 手动安装
```bash
pip3 install -r requirements.txt
python3 main.py
```

## 文档资源
- 📖 [使用指南](使用指南.md) - 详细操作说明
- 📋 [需求文档](需求文档.md) - 功能规格说明
- 🧪 [测试脚本](test_watermark.py) - 功能验证

## 技术架构
- **GUI框架**: Tkinter + ttk
- **图像处理**: Pillow (PIL)
- **配置管理**: JSON
- **架构设计**: 模块化分层架构

---

**首次发布版本** - 包含完整的图片水印处理功能！
"""
    
    return release_notes

def show_manual_instructions():
    """显示手动操作说明"""
    print("\n" + "="*60)
    print("📋 GitHub Release 手动创建说明")
    print("="*60)
    
    print("\n1. 访问GitHub仓库页面")
    print("2. 点击 'Releases' 标签")
    print("3. 点击 'Create a new release' 按钮")
    print("4. 填写以下信息:")
    print(f"   - Tag version: {TAG_NAME}")
    print(f"   - Release title: {PROJECT_NAME} v{VERSION}")
    print("   - Description: 复制下面的发布说明")
    print("\n5. 上传发布包:")
    print("   - 将 releases/ 目录下的 .zip 文件拖拽到页面")
    print("\n6. 点击 'Publish release' 发布")
    
    print("\n📝 发布说明内容:")
    print("-" * 40)
    print(create_release_notes())
    print("-" * 40)

def main():
    """主函数"""
    print(f"🚀 准备创建 {PROJECT_NAME} v{VERSION} GitHub Release")
    print("="*60)
    
    # 检查Git状态
    if not check_git_status():
        return 1
    
    # 创建标签
    if not create_tag():
        return 1
    
    # 推送到GitHub
    if not push_to_github():
        return 1
    
    # 构建发布包
    print("\n📦 构建发布包...")
    build_script = Path(__file__).parent / "build_release.py"
    
    try:
        subprocess.run([sys.executable, str(build_script)], check=True)
        print("✅ 发布包构建完成")
    except subprocess.CalledProcessError as e:
        print(f"❌ 发布包构建失败: {e}")
        return 1
    
    # 显示手动操作说明
    show_manual_instructions()
    
    print(f"\n🎉 {PROJECT_NAME} v{VERSION} 准备工作完成!")
    print("请按照上述说明在GitHub上创建Release并上传发布包。")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())