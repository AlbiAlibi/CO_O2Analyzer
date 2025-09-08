#!/usr/bin/env python3
"""
Example script demonstrating how to use the CO_O2_Analyser module.

This script shows various ways to use the module programmatically.
"""

import sys
import time
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from co_o2_analyser import COO2Analyzer
from co_o2_analyser.utils.config import Config
from co_o2_analyser.data.models import Measurement

def example_basic_usage():
    """Basic usage example."""
    print("🔬 Basic Usage Example")
    print("-" * 30)
    
    try:
        # Load configuration
        config = Config()
        print("✅ Configuration loaded")
        
        # Create analyzer instance
        analyzer = COO2Analyzer(config)
        print("✅ Analyzer created")
        
        # Get current measurement
        measurement = analyzer.get_current_measurement()
        if measurement:
            print(f"📊 Current Measurement:")
            print(f"   CO Concentration: {measurement.co_concentration} ppm")
            print(f"   O2 Concentration: {measurement.o2_concentration}%")
            print(f"   Sample Temperature: {measurement.sample_temp}°C")
            print(f"   Sample Flow: {measurement.sample_flow} L/min")
        else:
            print("⚠️  No measurement data available")
        
        # Close analyzer
        analyzer.close()
        print("✅ Analyzer closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_configuration():
    """Configuration example."""
    print("\n⚙️  Configuration Example")
    print("-" * 30)
    
    try:
        # Create config
        config = Config()
        
        # Get default values
        ip_address = config.get('instrument.ip_address')
        port = config.get('instrument.port')
        print(f"📡 Instrument: {ip_address}:{port}")
        
        # Set custom values
        config.set('instrument.ip_address', '192.168.1.100')
        config.set('data_collection.intervals.concentration_interval', 2.0)
        
        # Save configuration
        config.save_config()
        print("✅ Configuration updated and saved")
        
        # Verify changes
        new_ip = config.get('instrument.ip_address')
        new_interval = config.get('data_collection.intervals.concentration_interval')
        print(f"📡 New IP: {new_ip}")
        print(f"⏱️  New interval: {new_interval} seconds")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_database_operations():
    """Database operations example."""
    print("\n🗄️  Database Operations Example")
    print("-" * 30)
    
    try:
        from co_o2_analyser.utils.database import DatabaseManager
        
        # Create database manager
        db_manager = DatabaseManager("example_data.sqlite")
        print("✅ Database manager created")
        
        # Get recent data
        recent_data = db_manager.get_recent_data(seconds=300)  # Last 5 minutes
        print(f"📊 Recent data points: {len(recent_data)}")
        
        # Get measurement sessions
        sessions = db_manager.get_measurement_sessions()
        print(f"📁 Measurement sessions: {len(sessions)}")
        
        # Close database
        db_manager.close()
        print("✅ Database closed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_measurement_session():
    """Measurement session example."""
    print("\n📋 Measurement Session Example")
    print("-" * 30)
    
    try:
        config = Config()
        analyzer = COO2Analyzer(config)
        
        # Start a measurement session
        print("🚀 Starting measurement session...")
        session_path = analyzer.start_measurement_session(duration_minutes=1)  # 1 minute session
        print(f"📁 Session path: {session_path}")
        
        # Simulate adding measurements
        print("📊 Adding sample measurements...")
        for i in range(3):
            analyzer.add_measurement_to_session(
                co_concentration=5.0 + i * 0.5,
                o2_concentration=21.0 + i * 0.1,
                sample_temp=25.0 + i,
                sample_flow=1.0
            )
            print(f"   Measurement {i+1} added")
            time.sleep(0.5)  # Small delay
        
        # Stop the session
        print("⏹️  Stopping measurement session...")
        analyzer.stop_measurement_session()
        print("✅ Session completed")
        
        # Close analyzer
        analyzer.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

def example_simulation_mode():
    """Simulation mode example."""
    print("\n🎮 Simulation Mode Example")
    print("-" * 30)
    
    try:
        config = Config()
        
        # Enable simulation mode
        config.set('instrument.simulation_mode', True)
        print("🎮 Simulation mode enabled")
        
        # Create analyzer with simulation
        analyzer = COO2Analyzer(config)
        print("✅ Analyzer created in simulation mode")
        
        # Get simulated measurements
        for i in range(3):
            measurement = analyzer.get_current_measurement()
            if measurement:
                print(f"📊 Simulated Measurement {i+1}:")
                print(f"   CO: {measurement.co_concentration:.2f} ppm")
                print(f"   O2: {measurement.o2_concentration:.2f}%")
            time.sleep(1)
        
        # Close analyzer
        analyzer.close()
        print("✅ Simulation completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all examples."""
    print("🚀 CO_O2_Analyser Module Usage Examples")
    print("=" * 50)
    
    examples = [
        example_basic_usage,
        example_configuration,
        example_database_operations,
        example_measurement_session,
        example_simulation_mode
    ]
    
    for example_func in examples:
        try:
            example_func()
        except KeyboardInterrupt:
            print("\n⏹️  Example interrupted by user")
            break
        except Exception as e:
            print(f"❌ Example failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Examples completed!")
    print("\n📚 For more information:")
    print("- Check the USAGE.md file")
    print("- Run: python test_module.py")
    print("- Read the README.md file")

if __name__ == "__main__":
    main()
