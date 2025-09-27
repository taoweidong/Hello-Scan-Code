#!/usr/bin/env python3
"""
配置迁移工具

帮助用户将Python配置转换为JSON配置格式
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# 添加src目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.config import AppConfig, JSONConfigAdapter
from loguru import logger


def migrate_config_to_json(output_path: str = "config.json") -> bool:
    """
    将当前的AppConfig配置迁移到JSON格式
    
    Args:
        output_path: 输出JSON配置文件路径
        
    Returns:
        是否迁移成功
    """
    try:
        # 创建当前配置实例
        app_config = AppConfig()
        app_config.load_from_env()
        
        # 转换为JSON格式
        json_config = JSONConfigAdapter.to_json_config(app_config)
        
        # 调整一些默认值使其更适合用户使用
        json_config["repo_path"] = "."  # 使用当前目录作为默认值
        
        # 保存JSON配置文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"配置已成功迁移到: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"配置迁移失败: {e}")
        return False


def create_template_config(output_path: str = "config.template.json") -> bool:
    """
    创建配置模板文件
    
    Args:
        output_path: 输出模板文件路径
        
    Returns:
        是否创建成功
    """
    try:
        from src.config import get_config_loader
        
        loader = get_config_loader()
        return loader.save_template_config(output_path)
        
    except Exception as e:
        logger.error(f"创建配置模板失败: {e}")
        return False


def validate_json_config(config_path: str) -> bool:
    """
    验证JSON配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置是否有效
    """
    try:
        from src.config import get_config_loader
        
        loader = get_config_loader()
        config = loader.load_config(config_path)
        
        if loader.validate_config(config):
            logger.info("配置文件验证通过")
            return True
        else:
            logger.error("配置文件验证失败")
            return False
            
    except Exception as e:
        logger.error(f"配置验证过程中发生错误: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="配置迁移和管理工具")
    parser.add_argument("--migrate", action="store_true", help="迁移当前配置到JSON格式")
    parser.add_argument("--template", action="store_true", help="创建配置模板文件")
    parser.add_argument("--validate", type=str, help="验证指定的JSON配置文件")
    parser.add_argument("--output", type=str, help="输出文件路径")
    
    args = parser.parse_args()
    
    if args.migrate:
        output_path = args.output or "config.json"
        success = migrate_config_to_json(output_path)
        sys.exit(0 if success else 1)
    
    elif args.template:
        output_path = args.output or "config.template.json"
        success = create_template_config(output_path)
        sys.exit(0 if success else 1)
    
    elif args.validate:
        success = validate_json_config(args.validate)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()