#!/usr/bin/env python3
"""
Test script to verify CO_O2_Analyser module installation and functionality.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        # Test main package import
        import co_o2_analyser
        print("✅ Main package imported successfully")
        print(f"   Version: {co_o2_analyser.__version__}")
        
        # Test core modules
        from co_o2_analyser.core.analyzer import COO2Analyzer
        print("✅ COO2Analyzer imported successfully")
        
        from co_o2_analyser.gui.main_window import MainWindow
        print("✅ MainWindow imported successfully")
        
        from co_o2_analyser.utils.config import Config
        print("✅ Config imported successfully")
        
        # Test data models
        from co_o2_analyser.data.models import Measurement
        print("✅ Measurement model imported successfully")
        
        # Test GUI components
        from co_o2_analyser.gui.plot_widget import PlotWidget
        print("✅ PlotWidget imported successfully")
        
        from co_o2_analyser.gui.status_widget import StatusWidget
        print("✅ StatusWidget imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available."""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'PyQt6',
        'matplotlib',
        'numpy',
        'pandas',
        'requests',
        'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                importlib.import_module(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    return True

def test_configuration():
    """Test configuration system."""
    print("\n⚙️  Testing configuration...")
    
    try:
        from co_o2_analyser.utils.config import Config
        
        # Create config instance
        config = Config()
        print("✅ Config instance created")
        
        # Test getting default values
        ip_address = config.get('instrument.ip_address')
        print(f"✅ Default IP address: {ip_address}")
        
        # Test setting values
        config.set('test.value', 'test_data')
        test_value = config.get('test.value')
        print(f"✅ Config set/get test: {test_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_database():
    """Test database functionality."""
    print("\n🗄️  Testing database...")
    
    try:
        from co_o2_analyser.utils.database import DatabaseManager
        
        # Create database manager
        db_manager = DatabaseManager("test_data.sqlite")
        print("✅ Database manager created")
        
        # Test database connection
        conn = db_manager.get_connection()
        if conn:
            print("✅ Database connection successful")
            conn.close()
        else:
            print("❌ Database connection failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_gui_components():
    """Test GUI components (without showing windows)."""
    print("\n🖥️  Testing GUI components...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from co_o2_analyser.gui.main_window import MainWindow
        from co_o2_analyser.utils.config import Config
        
        # Create QApplication (required for GUI components)
        app = QApplication([])
        
        # Test config creation
        config = Config()
        print("✅ Config created for GUI test")
        
        # Test MainWindow creation (without showing)
        window = MainWindow(config)
        print("✅ MainWindow created successfully")
        
        # Clean up
        window.close()
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 CO_O2_Analyser Module Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Dependencies Test", test_dependencies),
        ("Configuration Test", test_configuration),
        ("Database Test", test_database),
        ("GUI Components Test", test_gui_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Module is ready to use.")
        print("\n📋 Next steps:")
        print("1. Run the GUI: python -m co_o2_analyser")
        print("2. Start data collection: python start_data_collector.py")
        print("3. Check the documentation: README.md")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install module: pip install -e .")
        print("3. Check Python version: python --version (requires 3.11+)")
        return 1

if __name__ == "__main__":
    sys.exit(main())
