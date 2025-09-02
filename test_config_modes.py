#!/usr/bin/env python3
"""
Test script to verify configuration modes work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from co_o2_analyser.utils.config import Config
from co_o2_analyser.core.instrument_communication import InstrumentCommunication

def test_config_modes():
    """Test different configuration modes."""
    print("🔍 Testing Configuration Modes...")
    
    # Load config
    config = Config()
    print(f"✅ Config loaded")
    print(f"   Simulation mode: {config.get('instrument.simulation_mode', False)}")
    print(f"   Data simulation: {config.get('instrument.data_simulation', False)}")
    
    # Test instrument communication
    comm = InstrumentCommunication(config)
    print(f"✅ Instrument communication initialized")
    print(f"   Is simulation: {comm.is_simulation}")
    
    # Test connection
    if comm.test_connection():
        print("✅ Connection test passed")
    else:
        print("❌ Connection test failed")
        return
    
    # Get current values
    values = comm.get_current_values()
    if values:
        print(f"✅ Current values retrieved: {values}")
    else:
        print("❌ No values retrieved")

if __name__ == "__main__":
    test_config_modes()
