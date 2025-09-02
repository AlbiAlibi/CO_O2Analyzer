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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_database_exists():
    """Ensure the data.sqlite database exists and is up-to-date."""
    try:
        logger.info("🔍 Checking if data.sqlite database exists and is up-to-date...")
        
        # Check if database exists
        db_path = Path("data.sqlite")
        if not db_path.exists():
            logger.info("📊 Database not found. Creating new database with current instrument tags...")
            return create_database()
        
        # Check if database is recent (less than 24 hours old)
        import time
        db_age_hours = (time.time() - db_path.stat().st_mtime) / 3600
        if db_age_hours > 24:
            logger.info(f"📊 Database is {db_age_hours:.1f} hours old. Updating with current instrument tags...")
            return create_database()
        
        logger.info("✅ Database exists and is recent. Proceeding with data collection...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking database: {e}")
        logger.info("🔄 Attempting to create database anyway...")
        return create_database()

def create_database():
    """Create/update the database using the local tag_list.json file."""
    try:
        logger.info("🔄 Starting database creation/update process...")
        
        # Import the database recreator
        from recreate_database import DynamicDatabaseRecreator
        
        # Use default instrument settings (can be configured via environment variables)
        instrument_ip = os.getenv("INSTRUMENT_IP", "192.168.1.1")
        instrument_port = os.getenv("INSTRUMENT_PORT", "8180")
        
        logger.info(f"🔌 Using instrument configuration: {instrument_ip}:{instrument_port}")
        
        # Create recreator and run
        recreator = DynamicDatabaseRecreator(instrument_ip, instrument_port)
        
        # Override the fetch method to use local file
        def fetch_from_local_file(self):
            """Fetch tags from local JSON file instead of API."""
            try:
                tag_list_path = "notatki/tag_list.json"
                if not Path(tag_list_path).exists():
                    logger.error(f"Local tag list file not found: {tag_list_path}")
                    return None
                
                import json
                with open(tag_list_path, 'r') as f:
                    data = json.load(f)
                    tags = data.get('tags', [])
                    logger.info(f"Loaded {len(tags)} tags from local file")
                    return tags
            except Exception as e:
                logger.error(f"Failed to load local tag list: {e}")
                return None
        
        # Replace the fetch method
        recreator.fetch_current_taglist = lambda: fetch_from_local_file(recreator)
        
        if recreator.recreate_database():
            logger.info("✅ Database created/updated successfully!")
            return True
        else:
            logger.error("❌ Failed to create/update database")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Failed to import database recreator: {e}")
        logger.error("Make sure recreate_database.py is in the same directory")
        return False
    except Exception as e:
        logger.error(f"❌ Error creating database: {e}")
        return False

def main():
    """Start the data collection service with automatic database setup."""
    try:
        print("🚀 Starting CO_O2Analyser data collection service...")
        print("=" * 60)
        
        # Step 1: Ensure database exists and is up-to-date
        if not ensure_database_exists():
            print("❌ Failed to setup database. Cannot proceed with data collection.")
            print("💡 Please check the logs and ensure the instrument is accessible.")
            sys.exit(1)
        
        print("✅ Database setup completed successfully!")
        print()
        
        # Step 2: Start the data collection service
        print("🔄 Starting data collection service...")
        print("This service will run continuously and collect data from the instrument.")
        print("Press Ctrl+C to stop the service.")
        print()
        
        # Import and run the data collector
        from src.co_o2_analyser.core.CO_O2Analyser import main as run_collector
        run_collector()
        
    except KeyboardInterrupt:
        print("\n🛑 Data collection service stopped by user.")
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start data collection service: {e}")
        logger.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
