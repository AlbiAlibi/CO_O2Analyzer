#!/usr/bin/env python3
"""
Comprehensive error checker for the CO_O2_Analyser system.
"""

import sys
import traceback
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Checking imports...")
    try:
        import PyQt6
        print("   ✅ PyQt6 imported successfully")
    except ImportError as e:
        print(f"   ❌ PyQt6 import failed: {e}")
        return False
    
    try:
        from co_o2_analyser.utils.config import Config
        print("   ✅ Config imported successfully")
    except ImportError as e:
        print(f"   ❌ Config import failed: {e}")
        return False
    
    try:
        from co_o2_analyser.core.analyzer import COO2Analyzer
        print("   ✅ COO2Analyzer imported successfully")
    except ImportError as e:
        print(f"   ❌ COO2Analyzer import failed: {e}")
        return False
    
    try:
        from co_o2_analyser.utils.database import MeasurementDatabaseManager
        print("   ✅ MeasurementDatabaseManager imported successfully")
    except ImportError as e:
        print(f"   ❌ MeasurementDatabaseManager import failed: {e}")
        return False
    
    try:
        from co_o2_analyser.gui.main_window import MainWindow
        print("   ✅ MainWindow imported successfully")
    except ImportError as e:
        print(f"   ❌ MainWindow import failed: {e}")
        return False
    
    return True

def check_config():
    """Check if configuration loads properly."""
    print("\n🔍 Checking configuration...")
    try:
        from co_o2_analyser.utils.config import Config
        config = Config()
        print("   ✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"   ❌ Configuration failed: {e}")
        traceback.print_exc()
        return False

def check_database():
    """Check if database operations work."""
    print("\n🔍 Checking database operations...")
    try:
        from co_o2_analyser.utils.database import MeasurementDatabaseManager
        db_manager = MeasurementDatabaseManager()
        print("   ✅ MeasurementDatabaseManager initialized")
        
        # Test session listing
        sessions = db_manager.list_measurement_sessions()
        print(f"   ✅ Found {len(sessions)} existing sessions")
        
        return True
    except Exception as e:
        print(f"   ❌ Database operations failed: {e}")
        traceback.print_exc()
        return False

def check_analyzer():
    """Check if analyzer initializes properly."""
    print("\n🔍 Checking analyzer initialization...")
    try:
        from co_o2_analyser.utils.config import Config
        from co_o2_analyser.core.analyzer import COO2Analyzer
        
        config = Config()
        analyzer = COO2Analyzer(config)
        print("   ✅ Analyzer initialized successfully")
        
        # Test measurement session methods
        status = analyzer.get_measurement_session_status()
        print(f"   ✅ Session status retrieved: {status.get('is_collecting', False)}")
        
        sessions = analyzer.list_measurement_sessions()
        print(f"   ✅ Session listing works: {len(sessions)} sessions")
        
        return True
    except Exception as e:
        print(f"   ❌ Analyzer initialization failed: {e}")
        traceback.print_exc()
        return False

def check_gui_imports():
    """Check if GUI can be imported without errors."""
    print("\n🔍 Checking GUI imports...")
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog
        print("   ✅ PyQt6 widgets imported successfully")
        
        from co_o2_analyser.gui.main_window import MainWindow
        print("   ✅ MainWindow imported successfully")
        
        return True
    except Exception as e:
        print(f"   ❌ GUI imports failed: {e}")
        traceback.print_exc()
        return False

def check_file_permissions():
    """Check if we can write to the measurements directory."""
    print("\n🔍 Checking file permissions...")
    try:
        measurements_dir = Path("measurements")
        measurements_dir.mkdir(exist_ok=True)
        print("   ✅ Measurements directory accessible")
        
        # Test file creation
        test_file = measurements_dir / "test_permissions.tmp"
        test_file.write_text("test")
        test_file.unlink()
        print("   ✅ File write/delete permissions OK")
        
        return True
    except Exception as e:
        print(f"   ❌ File permissions failed: {e}")
        return False

def main():
    """Run all checks."""
    print("🚀 CO_O2_Analyser Error Checker")
    print("=" * 50)
    
    checks = [
        ("Imports", check_imports),
        ("Configuration", check_config),
        ("Database", check_database),
        ("Analyzer", check_analyzer),
        ("GUI Imports", check_gui_imports),
        ("File Permissions", check_file_permissions),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n📊 Summary:")
    print("=" * 30)
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {name:20} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! The system should be working correctly.")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()
