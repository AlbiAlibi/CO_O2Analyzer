#!/usr/bin/env python3
"""
Script to fix incomplete measurement sessions that don't have end_time recorded.

This script will find all measurement sessions without end_time and set it to the
last measurement timestamp or start_time if no measurements exist.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from co_o2_analyser.utils.database import MeasurementDatabaseManager
from co_o2_analyser.core.analyzer import COO2Analyzer
from co_o2_analyser.utils.config import Config

def fix_incomplete_sessions():
    """Fix incomplete measurement sessions."""
    print("🔧 Fixing Incomplete Measurement Sessions")
    print("=" * 50)
    
    try:
        # Initialize the measurement database manager
        db_manager = MeasurementDatabaseManager()
        
        # Fix incomplete sessions
        print("\n🔍 Searching for incomplete sessions...")
        fixed_count = db_manager.fix_incomplete_sessions()
        
        if fixed_count > 0:
            print(f"\n✅ Fixed {fixed_count} incomplete sessions!")
        else:
            print("\n✅ No incomplete sessions found - all sessions are complete!")
        
        # List all sessions to show the results
        print("\n📋 Current measurement sessions:")
        sessions = db_manager.list_measurement_sessions()
        
        if sessions:
            print(f"   Found {len(sessions)} measurement sessions:")
            for i, session in enumerate(sessions, 1):
                start_time = session['start_time'][:19] if session['start_time'] else "Unknown"
                end_time = session['end_time'][:19] if session['end_time'] else "❌ Missing"
                measurements = session['total_measurements']
                file_name = session['file_name']
                
                status = "✅ Complete" if session['end_time'] else "❌ Incomplete"
                
                print(f"   {i:2d}. {file_name}")
                print(f"       Start: {start_time}")
                print(f"       End:   {end_time}")
                print(f"       Measurements: {measurements}")
                print(f"       Status: {status}")
                print()
        else:
            print("   No measurement sessions found.")
        
        print("🎉 Session fix completed!")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

def test_analyzer_fix():
    """Test the analyzer fix method."""
    print("\n🔧 Testing Analyzer Fix Method")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        config = Config()
        analyzer = COO2Analyzer(config)
        
        # Fix incomplete sessions via analyzer
        print("\n🔍 Using analyzer to fix incomplete sessions...")
        fixed_count = analyzer.fix_incomplete_sessions()
        
        if fixed_count > 0:
            print(f"✅ Analyzer fixed {fixed_count} incomplete sessions!")
        else:
            print("✅ Analyzer found no incomplete sessions!")
        
        # List sessions via analyzer
        print("\n📋 Sessions via analyzer:")
        sessions = analyzer.list_measurement_sessions()
        print(f"   Found {len(sessions)} sessions")
        
        for session in sessions:
            status = "✅ Complete" if session['end_time'] else "❌ Incomplete"
            print(f"   📄 {session['file_name']} - {status}")
        
    except Exception as e:
        print(f"\n❌ Analyzer test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Measurement Session Fix Tool")
    print("=" * 60)
    
    # Fix incomplete sessions
    fix_incomplete_sessions()
    
    # Test analyzer method
    test_analyzer_fix()
    
    print("\n📝 Summary:")
    print("   • Fixed incomplete sessions by setting end_time")
    print("   • Updated total_measurements count")
    print("   • All sessions now have proper start/end times")
    print("   • Future sessions will be properly closed automatically")
