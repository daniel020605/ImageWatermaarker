"""
配置管理模块
负责水印模板的保存、加载和管理
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "templates"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        self.templates_file = self.config_dir / "templates.json"
        self.settings_file = self.config_dir / "settings.json"
        
        # 默认配置
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.default_watermark_config = {
            'type': 'text',
            'text': current_date,
            'font_name': None,
            'font_size': 36,  # 这个会被自动计算覆盖
            'color': [0, 0, 0, 128],  # RGBA - 黑色半透明
            'bold': False,
            'italic': False,
            'shadow': False,
            'stroke': False,
            'stroke_width': 2,
            'stroke_color': [0, 0, 0, 255],
            'position': 'middle_center',
            'custom_pos': None,
            'margin': 20,
            'rotation': 0,
            'opacity': 128,
            'scale_percent': 100.0,
            'image_path': None
        }
        
        self.default_export_config = {
            'output_format': 'JPEG',
            'quality': 95,
            'naming_rule': 'suffix',
            'custom_text': '_watermarked',
            'resize_enabled': False,
            'resize_width': None,
            'resize_height': None,
            'resize_scale': None
        }
        
        # 初始化配置文件
        self._init_config_files()
    
    def _init_config_files(self):
        """初始化配置文件"""
        # 初始化模板文件
        if not self.templates_file.exists():
            default_templates = {
                'templates': {
                    'Default': {
                        'name': 'Default',
                        'description': '默认水印模板',
                        'created_time': datetime.now().isoformat(),
                        'watermark_config': self.default_watermark_config.copy(),
                        'export_config': self.default_export_config.copy()
                    }
                },
                'last_used': 'Default'
            }
            self.save_templates(default_templates)
        
        # 初始化设置文件
        if not self.settings_file.exists():
            default_settings = {
                'window_size': [1200, 800],
                'window_position': None,
                'last_input_dir': str(Path.home()),
                'last_output_dir': str(Path.home() / 'Desktop'),
                'auto_load_last_template': True,
                'preview_size': [400, 300],
                'thumbnail_size': [150, 150]
            }
            self.save_settings(default_settings)
    
    def load_templates(self) -> Dict[str, Any]:
        """加载所有模板"""
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载模板失败: {str(e)}")
            return {'templates': {}, 'last_used': None}
    
    def save_templates(self, templates_data: Dict[str, Any]) -> bool:
        """保存所有模板"""
        try:
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
            return False
    
    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取指定模板"""
        templates_data = self.load_templates()
        return templates_data['templates'].get(template_name)
    
    def save_template(self, template_name: str, watermark_config: Dict[str, Any], 
                     export_config: Dict[str, Any], description: str = "") -> bool:
        """保存水印模板"""
        try:
            templates_data = self.load_templates()
            
            template_data = {
                'name': template_name,
                'description': description,
                'created_time': datetime.now().isoformat(),
                'watermark_config': watermark_config.copy(),
                'export_config': export_config.copy()
            }
            
            templates_data['templates'][template_name] = template_data
            templates_data['last_used'] = template_name
            
            return self.save_templates(templates_data)
            
        except Exception as e:
            print(f"保存模板失败: {str(e)}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """删除模板"""
        try:
            templates_data = self.load_templates()
            
            if template_name in templates_data['templates']:
                del templates_data['templates'][template_name]
                
                # 如果删除的是最后使用的模板，重置为默认
                if templates_data['last_used'] == template_name:
                    if 'Default' in templates_data['templates']:
                        templates_data['last_used'] = 'Default'
                    elif templates_data['templates']:
                        templates_data['last_used'] = list(templates_data['templates'].keys())[0]
                    else:
                        templates_data['last_used'] = None
                
                return self.save_templates(templates_data)
            
            return False
            
        except Exception as e:
            print(f"删除模板失败: {str(e)}")
            return False
    
    def get_template_list(self) -> List[str]:
        """获取所有模板名称列表"""
        templates_data = self.load_templates()
        return list(templates_data['templates'].keys())
    
    def get_last_used_template(self) -> Optional[str]:
        """获取最后使用的模板名称"""
        templates_data = self.load_templates()
        return templates_data.get('last_used')
    
    def set_last_used_template(self, template_name: str) -> bool:
        """设置最后使用的模板"""
        try:
            templates_data = self.load_templates()
            if template_name in templates_data['templates']:
                templates_data['last_used'] = template_name
                return self.save_templates(templates_data)
            return False
        except Exception as e:
            print(f"设置最后使用模板失败: {str(e)}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """加载应用设置"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
            return {}
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """保存应用设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            return False
    
    def get_setting(self, key: str, default_value: Any = None) -> Any:
        """获取单个设置项"""
        settings = self.load_settings()
        return settings.get(key, default_value)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """设置单个设置项"""
        try:
            settings = self.load_settings()
            settings[key] = value
            return self.save_settings(settings)
        except Exception as e:
            print(f"设置配置项失败: {str(e)}")
            return False
    
    def export_template(self, template_name: str, export_path: str) -> bool:
        """导出模板到文件"""
        try:
            template = self.get_template(template_name)
            if template:
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(template, f, ensure_ascii=False, indent=2)
                return True
            return False
        except Exception as e:
            print(f"导出模板失败: {str(e)}")
            return False
    
    def import_template(self, import_path: str, template_name: str = None) -> bool:
        """从文件导入模板"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # 如果没有指定名称，使用文件中的名称或文件名
            if not template_name:
                template_name = template_data.get('name', Path(import_path).stem)
            
            # 确保模板数据完整
            watermark_config = template_data.get('watermark_config', {})
            export_config = template_data.get('export_config', {})
            description = template_data.get('description', f'从 {import_path} 导入')
            
            # 填充缺失的配置项
            for key, value in self.default_watermark_config.items():
                if key not in watermark_config:
                    watermark_config[key] = value
            
            for key, value in self.default_export_config.items():
                if key not in export_config:
                    export_config[key] = value
            
            return self.save_template(template_name, watermark_config, export_config, description)
            
        except Exception as e:
            print(f"导入模板失败: {str(e)}")
            return False
    
    def get_default_watermark_config(self) -> Dict[str, Any]:
        """获取默认水印配置"""
        return self.default_watermark_config.copy()
    
    def get_default_export_config(self) -> Dict[str, Any]:
        """获取默认导出配置"""
        return self.default_export_config.copy()