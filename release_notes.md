# ImageWatermarker v1.0.0 🎉

## 🚀 首次发布

ImageWatermarker 是一个功能强大、易于使用的图片水印本地应用程序，支持 Windows 和 macOS 平台。

## ✨ 主要功能

### 📁 文件处理
- **多格式支持**：JPEG, PNG, BMP, TIFF（PNG支持透明通道）
- **灵活导入**：单张图片拖拽、批量选择、整个文件夹导入
- **智能导出**：自定义输出文件夹、多种命名规则、质量调节

### 🏷️ 水印功能
- **文本水印**：自定义文本、字体、颜色、透明度
- **九宫格定位**：一键放置到九个预设位置
- **实时预览**：所见即所得的水印效果
- **批量处理**：高效处理多张图片

### ⚙️ 配置管理
- **模板系统**：保存和加载水印配置
- **设置持久化**：自动记住上次使用的设置
- **跨平台兼容**：Windows/macOS/Linux 全平台支持

## 📦 安装方式

### 方式一：下载发布包（推荐）
1. 下载 `ImageWatermarker-v1.0.0.zip`
2. 解压到任意目录
3. 双击运行启动脚本：
   - Windows: `启动程序.bat`
   - macOS/Linux: `启动程序.sh`

### 方式二：从源码运行
```bash
git clone https://github.com/daniel020605/ImageWatermarker.git
cd ImageWatermarker
pip3 install -r requirements.txt
python3 main.py
```

## 🎯 快速开始

1. **导入图片**：拖拽图片到界面或点击"导入图片"按钮
2. **设置水印**：输入水印文本，选择位置和样式
3. **实时预览**：在预览窗口查看效果
4. **批量导出**：选择输出文件夹，一键生成水印图片

## 🏗️ 技术特性

- **模块化架构**：清晰的代码结构，易于维护和扩展
- **错误处理**：完善的异常处理和用户提示
- **线程安全**：支持多线程批量处理
- **内存优化**：高效的图像处理算法

## 📚 文档

- [需求文档](需求文档.md) - 详细的功能需求说明
- [使用指南](使用指南.md) - 完整的用户操作手册
- [项目总结](项目总结.md) - 技术实现和架构说明

## 🧪 测试验证

所有功能都经过全面测试：
- ✅ 基本功能测试（图片加载、水印创建、保存）
- ✅ 批量处理测试（多图片同时处理）
- ✅ 九宫格位置测试（所有位置验证）
- ✅ 跨平台兼容性测试

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)，可自由使用、修改和分发。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**下载地址**: [ImageWatermarker-v1.0.0.zip](https://github.com/daniel020605/ImageWatermarker/releases/download/v1.0.0/ImageWatermarker-v1.0.0.zip)

**仓库地址**: https://github.com/daniel020605/ImageWatermarker