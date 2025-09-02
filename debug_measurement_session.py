#!/usr/bin/env python3
"""
Debug script to test the measurement session functionality.
"""

import sys
import traceback
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_measurement_session():
    """Test measurement session with detailed error reporting."""
    try:
        print("🔍 Testing Measurement Session...")
        
        # Test 1: Import modules
        print("\n1. Testing imports...")
        from co_o2_analyser.utils.database import MeasurementDatabaseManager
        from co_o2_analyser.core.analyzer import COO2Analyzer
        from co_o2_analyser.utils.config import Config
        print("   ✅ All imports successful")
        
        # Test 2: Initialize components
        print("\n2. Testing initialization...")
        config = Config()
        print("   ✅ Config loaded")
        
        analyzer = COO2Analyzer(config)
        print("   ✅ Analyzer initialized")
        
        # Test 3: Start measurement session
        print("\n3. Testing measurement session start...")
        session_path = analyzer.start_measurement_session(duration_minutes=1)
        print(f"   ✅ Session started: {session_path}")
        
        # Test 4: Check session status
        print("\n4. Testing session status...")
        status = analyzer.get_measurement_session_status()
        print(f"   ✅ Session status: {status}")
        
        # Test 5: Add measurement
        print("\n5. Testing measurement addition...")
        success = analyzer.add_measurement_to_session(100.0, 15.0, 30.0, 500.0)
        print(f"   ✅ Measurement added: {success}")
        
        # Test 6: Stop session
        print("\n6. Testing session stop...")
        final_path = analyzer.stop_measurement_session()
        print(f"   ✅ Session stopped: {final_path}")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_measurement_session()
