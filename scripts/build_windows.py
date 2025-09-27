#!/usr/bin/env python3
"""
Windows平台构建脚本 - 适配新架构

自动化执行PyInstaller打包流程
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import argparse
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindowsBuilder:
    """Windows平台构建器 - 适配新架构"""
    
    def __init__(self, project_root: str = None):
        """
        初始化构建器
        
        Args:
            project_root: 项目根目录
        """
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.build_dir = self.project_root / "build" / "windows"
        self.dist_dir = self.project_root / "dist" / "windows"
        self.spec_file = self.build_dir / "hello-scan-code.spec"
        
        # 添加项目路径到Python路径
        sys.path.insert(0, str(self.project_root))
    
    def check_requirements(self) -> bool:
        """
        检查构建要求
        
        Returns:
            bool: 是否满足构建要求
        """
        logger.info("检查构建要求...")
        
        # 检查操作系统
        if platform.system() != "Windows":
            logger.warning("当前不是Windows系统，但仍可尝试构建")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version < (3, 10):
            logger.error(f"Python版本过低: {python_version}, 需要3.10+")
            return False
        
        # 检查PyInstaller
        try:
            import PyInstaller
            logger.info(f"PyInstaller版本: {PyInstaller.__version__}")
        except ImportError:
            logger.error("PyInstaller未安装，请执行: pip install pyinstaller")
            return False
        
        # 检查项目依赖
        required_packages = ['loguru', 'pandas', 'openpyxl', 'sqlalchemy', 'alembic']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"缺少依赖包: {', '.join(missing_packages)}")
            logger.error("请执行: pip install -r requirements.txt")
            return False
        
        # 检查新架构的配置模块
        try:
            from src.config import ConfigManager, get_config_manager
            from src.packaging import ResourceBundler, get_hidden_imports
            logger.info("新架构模块检查通过")
        except ImportError as e:
            logger.error(f"新架构模块导入失败: {e}")
            return False
        
        # 检查spec文件
        if not self.spec_file.exists():
            logger.error(f"spec文件不存在: {self.spec_file}")
            return False
        
        logger.info("所有构建要求已满足")
        return True
    
    def clean_build(self):
        """清理构建目录"""
        logger.info("清理构建目录...")
        
        clean_dirs = [
            self.dist_dir,
            self.project_root / "build" / "__pycache__",
            self.project_root / "dist" / "__pycache__",
        ]
        
        for dir_path in clean_dirs:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logger.info(f"已清理: {dir_path}")
    
    def install_dependencies(self):
        """安装构建依赖"""
        logger.info("安装构建依赖...")
        
        try:
            # 升级PyInstaller到最新版本
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"
            ], check=True)
            
            logger.info("依赖安装完成")
        except subprocess.CalledProcessError as e:
            logger.error(f"依赖安装失败: {e}")
            raise
    
    def prepare_config_template(self):
        """准备配置模板文件"""
        logger.info("准备配置模板文件...")
        
        try:
            from src.config import get_config_manager
            manager = get_config_manager()
            manager.create_config_template()
            logger.info("配置模板准备完成")
        except Exception as e:
            logger.warning(f"配置模板准备失败: {e}")
    
    def build_executable(self) -> bool:
        """
        构建可执行文件
        
        Returns:
            bool: 是否构建成功
        """
        logger.info("开始构建可执行文件...")
        
        try:
            # 切换到项目根目录
            os.chdir(self.project_root)
            
            # 执行PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                str(self.spec_file)
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("构建成功！")
                logger.info(f"构建输出: {result.stdout}")
                return True
            else:
                logger.error("构建失败！")
                logger.error(f"错误输出: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"构建过程中出现异常: {e}")
            return False
    
    def post_build_tasks(self):
        """构建后任务"""
        logger.info("执行构建后任务...")
        
        # 检查输出文件
        exe_file = self.dist_dir / "hello-scan-code.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            logger.info(f"可执行文件大小: {file_size:.2f} MB")
        else:
            logger.error("可执行文件未生成")
            return False
        
        # 创建并复制配置模板
        try:
            from src.config import get_json_loader
            loader = get_json_loader()
            
            # 检查是否存在配置模板
            if loader.template_path and os.path.exists(loader.template_path):
                shutil.copy2(loader.template_path, self.dist_dir / "config.template.json")
                logger.info("已复制配置模板文件")
            else:
                # 创建配置模板
                loader.save_config_template()
                if os.path.exists(loader.template_path):
                    shutil.copy2(loader.template_path, self.dist_dir / "config.template.json")
                    logger.info("已创建并复制配置模板文件")
        except Exception as e:
            logger.warning(f"配置模板处理失败: {e}")
        
        # 复制README和LICENSE
        for doc_file in ["README.md", "LICENSE", "PYINSTALLER_GUIDE.md"]:
            src_file = self.project_root / doc_file
            if src_file.exists():
                shutil.copy2(src_file, self.dist_dir / doc_file)
                logger.info(f"已复制: {doc_file}")
        
        return True
    
    def create_distribution_package(self):
        """创建分发包"""
        logger.info("创建分发包...")
        
        try:
            # 创建版本号
            version = "1.0.0"  # 可以从git或配置文件读取
            
            # 压缩包名称
            package_name = f"hello-scan-code-v{version}-windows"
            package_path = self.project_root / "dist" / f"{package_name}.zip"
            
            # 创建压缩包
            shutil.make_archive(
                str(package_path.with_suffix('')),
                'zip',
                self.dist_dir.parent,
                'windows'
            )
            
            logger.info(f"分发包已创建: {package_path}")
            
        except Exception as e:
            logger.error(f"创建分发包失败: {e}")
    
    def run_build(self, clean: bool = True, install_deps: bool = False) -> bool:
        """
        运行完整构建流程
        
        Args:
            clean: 是否清理构建目录
            install_deps: 是否安装依赖
            
        Returns:
            bool: 是否构建成功
        """
        logger.info("开始Windows平台构建...")
        
        try:
            # 检查要求
            if not self.check_requirements():
                return False
            
            # 清理构建目录
            if clean:
                self.clean_build()
            
            # 安装依赖
            if install_deps:
                self.install_dependencies()
            
            # 准备配置模板
            self.prepare_config_template()
            
            # 构建可执行文件
            if not self.build_executable():
                return False
            
            # 构建后任务
            if not self.post_build_tasks():
                return False
            
            # 创建分发包
            self.create_distribution_package()
            
            logger.info("Windows构建完成！")
            return True
            
        except Exception as e:
            logger.error(f"构建失败: {e}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Windows平台构建脚本")
    parser.add_argument("--no-clean", action="store_true", help="不清理构建目录")
    parser.add_argument("--install-deps", action="store_true", help="安装构建依赖")
    parser.add_argument("--project-root", help="项目根目录路径")
    
    args = parser.parse_args()
    
    builder = WindowsBuilder(args.project_root)
    success = builder.run_build(
        clean=not args.no_clean,
        install_deps=args.install_deps
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()