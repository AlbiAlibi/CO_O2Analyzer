#!/usr/bin/env python3
"""
Test script to verify signal file cleanup functionality.
"""

from pathlib import Path

def test_cleanup():
    """Test the cleanup functionality."""
    # Create test signal files
    refresh_file = Path("refresh_signal.txt")
    status_file = Path("analyser_status.txt")
    
    # Create test files
    refresh_file.write_text("TEST_REFRESH")
    status_file.write_text("TEST_STATUS")
    
    print("Created test signal files:")
    print(f"  - refresh_signal.txt: {refresh_file.exists()}")
    print(f"  - analyser_status.txt: {status_file.exists()}")
    
    # Simulate cleanup
    try:
        if refresh_file.exists():
            refresh_file.unlink()
            print("✓ Removed refresh_signal.txt")
        
        if status_file.exists():
            status_file.unlink()
            print("✓ Removed analyser_status.txt")
            
    except Exception as e:
        print(f"✗ Error cleaning up signal files: {e}")
    
    print("\nAfter cleanup:")
    print(f"  - refresh_signal.txt: {refresh_file.exists()}")
    print(f"  - analyser_status.txt: {status_file.exists()}")

if __name__ == "__main__":
    test_cleanup()
