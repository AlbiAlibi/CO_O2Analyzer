#!/usr/bin/env python3
"""
Basic usage example for CO_O2_Analyser.

This example demonstrates how to use the analyzer programmatically
without the GUI.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from co_o2_analyser.utils.config import Config
from co_o2_analyser.core.analyzer import COO2Analyzer
from co_o2_analyser.utils.logger import setup_logger


def main():
    """Main example function."""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting basic usage example")
    
    # Create configuration
    config = Config()
    
    # Customize configuration for your instrument
    config.set('instrument.ip_address', '192.168.1.100')  # Replace with your instrument IP
    config.set('instrument.port', 8180)
    
    try:
        # Create analyzer instance
        with COO2Analyzer(config) as analyzer:
            logger.info("Analyzer created successfully")
            
            # Test connection
            if analyzer.start_monitoring():
                logger.info("Monitoring started successfully")
                
                # Get current measurement
                measurement = analyzer.get_current_measurement()
                if measurement:
                    logger.info(f"Current measurement: CO={measurement.co_concentration} ppm, "
                              f"O2={measurement.o2_concentration}%")
                else:
                    logger.warning("No measurement data received")
                
                # Get measurement history
                history = analyzer.get_measurement_history(limit=10)
                logger.info(f"Retrieved {len(history)} historical measurements")
                
                # Stop monitoring
                analyzer.stop_monitoring()
                logger.info("Monitoring stopped")
            else:
                logger.error("Failed to start monitoring")
                
    except Exception as e:
        logger.error(f"Example failed: {e}")
        return 1
    
    logger.info("Example completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
