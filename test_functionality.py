"""
功能验证测试
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_plugin_system():
    """测试插件系统"""
    print("测试插件系统...")
    
    try:
        from src.plugin.base import IScanPlugin
        print("✓ 插件基础接口导入成功")
        
        from src.plugins.builtin.keyword_plugin import KeywordScanPlugin
        plugin = KeywordScanPlugin()
        print(f"✓ 关键字插件创建成功: {plugin.plugin_id}")
        
        # 测试插件初始化
        config = {"keywords": ["TODO", "FIXME"], "case_sensitive": False}
        if plugin.initialize(config):
            print("✓ 插件初始化成功")
        else:
            print("✗ 插件初始化失败")
            
        # 测试插件扫描功能
        context = {"repo_path": "."}
        results = plugin.scan_line("test.py", 10, "# TODO: 实现功能", context)
        print(f"✓ 插件扫描完成，发现 {len(results)} 个问题")
        
    except Exception as e:
        print(f"✗ 插件系统测试失败: {e}")
        return False
    
    return True

def test_config_manager():
    """测试配置管理器"""
    print("\n测试配置管理器...")
    
    try:
        from src.config.config_manager import ConfigManager
        config_manager = ConfigManager()
        print("✓ 配置管理器创建成功")
        
        # 测试获取配置
        repo_path = config_manager.get_repo_path()
        print(f"✓ 仓库路径: {repo_path}")
        
        ignore_dirs = config_manager.get_ignore_dirs()
        print(f"✓ 忽略目录: {ignore_dirs}")
        
        enabled_plugins = config_manager.get_enabled_plugins()
        print(f"✓ 启用插件: {enabled_plugins}")
        
    except Exception as e:
        print(f"✗ 配置管理器测试失败: {e}")
        return False
    
    return True

def test_scan_engine():
    """测试扫描引擎"""
    print("\n测试扫描引擎...")
    
    try:
        from src.engine.grep_scanner import GrepScanner
        print("✓ Grep扫描器导入成功")
        
        from src.plugin.manager import PluginManager
        from src.config.config_manager import ConfigManager
        from src.engine.scan_engine import OptimizedScanEngine
        
        config_manager = ConfigManager()
        plugin_manager = PluginManager(config_manager)
        if plugin_manager.initialize():
            print("✓ 插件管理器初始化成功")
        else:
            print("✗ 插件管理器初始化失败")
            
        scan_engine = OptimizedScanEngine(config_manager, plugin_manager)
        print("✓ 扫描引擎创建成功")
        
        # 获取统计信息
        stats = scan_engine.get_stats()
        print(f"✓ 扫描引擎统计信息: {stats}")
        
    except Exception as e:
        print(f"✗ 扫描引擎测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("Hello-Scan-Code 功能验证测试")
    print("=" * 40)
    
    tests = [
        test_plugin_system,
        test_config_manager,
        test_scan_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过！")
        return 0
    else:
        print("✗ 部分测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())