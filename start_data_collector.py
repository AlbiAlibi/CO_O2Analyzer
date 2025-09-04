#!/usr/bin/env python3
"""
Startup script for CO_O2Analyser data collection service.

This script automatically creates/updates the data.sqlite database at startup
by fetching the current tag list from the instrument's /api/taglist endpoint,
then starts the data collection service that runs in the background
and collects data from the Teledyne N300M analyzer.

Usage:
    python start_data_collector.py
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the proper logger setup
from co_o2_analyser.utils.logger import setup_logger

# Setup logging using the proper logger configuration
logger = setup_logger(
    name="start_data_collector",
    level="INFO",
    log_file="co_o2_analyser.log"
)

def ensure_database_exists():
    """Ensure the data.sqlite database exists and is up-to-date."""
    try:
        logger.info("Checking if data.sqlite database exists and updating with fresh instrument data...")
        
        # Check if database exists
        db_path = Path("data.sqlite")
        if not db_path.exists():
            logger.info("Database not found. Creating new database with current instrument tags...")
            return create_database()
        
        # Try to update the database with fresh instrument data on startup
        logger.info("Attempting to update database with fresh instrument tag data...")
        try:
            return create_database()
        except Exception as e:
            logger.warning(f"Failed to update database with fresh data: {e}")
            logger.info("Continuing with existing database...")
            return True  # Continue with existing database
        
    except Exception as e:
        logger.error(f"Error checking database: {e}")
        logger.info("Attempting to create database anyway...")
        return create_database()

def create_database():
    """Create/update the database using fresh data from instrument URL."""
    try:
        logger.info("Starting database creation/update process...")
        
        # Import the database recreator
        from recreate_database import DynamicDatabaseRecreator
        
        # Use default instrument settings (can be configured via environment variables)
        instrument_ip = os.getenv("INSTRUMENT_IP", "192.168.1.1")
        instrument_port = os.getenv("INSTRUMENT_PORT", "8180")
        
        logger.info(f"Using instrument configuration: {instrument_ip}:{instrument_port}")
        
        # Create recreator and run - this will fetch from instrument URL
        recreator = DynamicDatabaseRecreator(instrument_ip, instrument_port)
        
        if recreator.recreate_database():
            logger.info("Database created/updated successfully with fresh instrument data!")
            return True
        else:
            logger.error("Failed to create/update database")
            return False
            
    except ImportError as e:
        logger.error(f"Failed to import database recreator: {e}")
        logger.error("Make sure recreate_database.py is in the same directory")
        return False
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def main():
    """Start the data collection service with automatic database setup."""
    try:
        print("Starting CO_O2Analyser data collection service...")
        print("=" * 60)
        
        # Step 1: Ensure database exists and is up-to-date
        if not ensure_database_exists():
            print("Warning: Failed to update database with fresh instrument data.")
            print("Continuing with existing database if available...")
            # Don't exit, just continue with existing database
        
        print("Database setup completed successfully!")
        print()
        
        # Step 2: Start the data collection service
        print("Starting data collection service...")
        print("This service will run continuously and collect data from the instrument.")
        print("Press Ctrl+C to stop the service.")
        print()
        
        # Import and run the data collector
        from src.co_o2_analyser.core.CO_O2Analyser import main as run_collector
        run_collector()
        
    except KeyboardInterrupt:
        print("\nData collection service stopped by user.")
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start data collection service: {e}")
        logger.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
