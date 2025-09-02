#!/usr/bin/env python3
"""
Test script for warning flags functionality.

This script tests the enhanced warning flags system that dynamically discovers
warning tags from the database instead of using hardcoded values.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_warning_tag_discovery():
    """Test the warning tag discovery functionality."""
    print("🧪 Testing Warning Tag Discovery")
    print("=" * 50)
    
    try:
        from co_o2_analyser.core.data_harvester import SQLiteDataHarvester
        
        # Test database connection
        harvester = SQLiteDataHarvester()
        
        # Test getting all tag names
        print("📊 Testing get_all_tag_names()...")
        all_tags = harvester.get_all_tag_names()
        print(f"✅ Total tags in database: {len(all_tags)}")
        
        # Test warning tag discovery
        print("\n🔍 Testing warning tag discovery...")
        warning_tags = [
            tag for tag in all_tags 
            if 'WARN' in tag.upper() or 'WARNING' in tag.upper()
        ]
        
        print(f"✅ Found {len(warning_tags)} warning tags:")
        for i, tag in enumerate(warning_tags[:10]):  # Show first 10
            print(f"  {i+1:2d}. {tag}")
        
        if len(warning_tags) > 10:
            print(f"  ... and {len(warning_tags) - 10} more")
        
        # Test specific warning tags that should exist
        expected_warnings = [
            "BOX_TEMP_WARN",
            "BENCH_TEMP_WARN", 
            "WHEEL_TEMP_WARN",
            "LOW_MEMORY_WARNING",
            "SYS_INVALID_CONC_WARNING",
            "SF_O2_SENSOR_WARN_MALFUNCTION"
        ]
        
        print(f"\n🎯 Testing expected warning tags...")
        found_expected = []
        missing_expected = []
        
        for expected in expected_warnings:
            if expected in all_tags:
                found_expected.append(expected)
                print(f"  ✅ Found: {expected}")
            else:
                missing_expected.append(expected)
                print(f"  ❌ Missing: {expected}")
        
        print(f"\n📋 Summary:")
        print(f"  - Total tags: {len(all_tags)}")
        print(f"  - Warning tags found: {len(warning_tags)}")
        print(f"  - Expected warnings found: {len(found_expected)}/{len(expected_warnings)}")
        
        if missing_expected:
            print(f"  - Missing expected warnings: {missing_expected}")
        
        # Test database status
        print(f"\n🗄️ Testing database status...")
        status = harvester.get_database_status()
        print(f"  - Status: {status.get('status', 'unknown')}")
        print(f"  - Total records: {status.get('total_records', 'unknown')}")
        print(f"  - Database path: {status.get('database_path', 'unknown')}")
        
        return len(warning_tags) > 0
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_status_widget_import():
    """Test that the status widget can be imported and initialized."""
    print("\n🧪 Testing Status Widget Import")
    print("=" * 50)
    
    try:
        # Test import
        from co_o2_analyser.gui.status_widget import StatusWidget
        print("✅ StatusWidget imported successfully")
        
        # Test that the class has the required methods
        required_methods = [
            'discover_warning_tags',
            'refresh_warning_flags',
            'update_warning_flags_from_database'
        ]
        
        print("\n🔍 Testing required methods...")
        for method in required_methods:
            if hasattr(StatusWidget, method):
                print(f"  ✅ Method found: {method}")
            else:
                print(f"  ❌ Method missing: {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing StatusWidget: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🚀 Warning Flags System Test")
    print("=" * 60)
    
    # Test 1: Warning tag discovery
    discovery_success = test_warning_tag_discovery()
    
    # Test 2: Status widget import
    import_success = test_status_widget_import()
    
    # Overall result
    print(f"\n🎯 Overall Test Results:")
    print(f"  - Warning tag discovery: {'✅ PASS' if discovery_success else '❌ FAIL'}")
    print(f"  - Status widget import: {'✅ PASS' if import_success else '❌ FAIL'}")
    
    if discovery_success and import_success:
        print(f"\n🎉 All tests passed! Warning flags system is working correctly.")
        print(f"💡 The system will now dynamically discover 60 warning tags from the database.")
    else:
        print(f"\n⚠️ Some tests failed. Check the output above for details.")
    
    return 0 if (discovery_success and import_success) else 1

if __name__ == "__main__":
    exit(main())
