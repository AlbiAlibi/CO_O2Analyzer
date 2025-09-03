#!/usr/bin/env python3
"""
CO_O2Analyser - Data Collection Service

This module runs as a separate process to collect data from Teledyne N300M analyzer
and store it in the tags.sqlite database. It communicates with the instrument
via HTTP REST API and stores all data locally for the main application to consume.

Usage:
    python CO_O2Analyser.py
"""

import json
import sqlite3
import requests
import logging
import time
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.co_o2_analyser.utils.config import Config

# Configure logging
def setup_logging():
    """Setup logging configuration for the data collection service."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "co_o2_analyser.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()


class InstrumentDataCollector:
    """Collects data from Teledyne N300M analyzer and stores it in SQLite database."""
    
    def __init__(self, config: Config):
        """Initialize the data collector.
        
        Args:
            config: Application configuration object
        """
        self.config = config
        self.db_file = "data.sqlite"
        self.status_file = "analyser_status.txt"
        self.connected = False
        
        # Get instrument configuration
        self.ip_address = config.get('instrument.ip_address', '192.168.1.1')
        self.port = config.get('instrument.port', 8180)
        self.timeout = config.get('instrument.timeout', 30)
        self.retry_attempts = config.get('instrument.retry_attempts', 3)
        
        # Construct URLs from configuration
        self.instrument_url = f"http://{self.ip_address}:{self.port}/api/valuelist"
        
        # Get concentration tags from configuration
        self.concentration_tags = config.get('instrument.tags.concentration_tags', ['CO_CONC', 'O2_CONC'])
        
        # Get all other tags for status collection
        self.all_other_tags = []
        for tag_group in ['instrument_status', 'flow_tags', 'temperature', 'warning_tags', 'order_tags']:
            tags = config.get(f'instrument.tags.{tag_group}', [])
            self.all_other_tags.extend(tags)
        
        # Remove duplicates and concentration tags from other tags
        self.all_other_tags = list(set(self.all_other_tags) - set(self.concentration_tags))
        
        # Get data collection intervals from configuration
        self.all_values_interval = config.get('data_collection.intervals.all_values_interval', 300)  # 5 minutes
        self.concentration_interval = config.get('data_collection.intervals.concentration_interval', 1.5)  # 1.5 seconds
        self.status_check_interval = config.get('data_collection.intervals.status_check_interval', 30)  # 0.5 minutes
        
        logger.info(f"Initialized data collector for {self.ip_address}:{self.port}")
        logger.info(f"Batch URL: {self.instrument_url}")
        logger.info(f"Concentration tags: {self.concentration_tags}")
        logger.info(f"Other tags: {len(self.all_other_tags)} tags")
        logger.info(f"Intervals - All values: {self.all_values_interval}s, Concentration: {self.concentration_interval}s")
        
        # Ensure the SQLite database and tables are created
        self.create_database()
    
    def create_database(self):
        """Check if the database exists and has the correct structure."""
        try:
            # Check if database file exists
            if not Path(self.db_file).exists():
                logger.warning(f"Database file {self.db_file} not found. Please run create_unified_database.py first.")
                return
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Check if TagList table exists and has the correct structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TagList'")
            if not cursor.fetchone():
                logger.error("TagList table not found. Please run create_unified_database.py first.")
                conn.close()
                return
            
            # Check if TagValues table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TagValues'")
            if not cursor.fetchone():
                logger.error("TagValues table not found. Please run create_unified_database.py first.")
                conn.close()
                return
            
            # Check if required tags exist
            required_tags = ['CO_CONC', 'O2_CONC', 'AI_SAMPLE_TEMP', 'AI_PUMP_FLOW']
            missing_tags = []
            
            for tag_name in required_tags:
                cursor.execute('SELECT id FROM TagList WHERE Name = ?', (tag_name,))
                if not cursor.fetchone():
                    missing_tags.append(tag_name)
            
            if missing_tags:
                logger.warning(f"Missing required tags: {missing_tags}")
                logger.warning("Please run create_unified_database.py to recreate the database with all tags.")
            else:
                logger.info("Database structure verified successfully")
                logger.info("All required tags are present")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to verify database: {e}")
            raise
    
    def update_status(self, status: str):
        """Update the status file with current status.
        
        Args:
            status: Status message to write
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.status_file, "a") as f:
                f.write(f"{timestamp} - {status}\n")
            logger.info(f"Status updated: {status}")
        except Exception as e:
            logger.error(f"Failed to update status file: {e}")
    
    def get_api_data(self, url: str) -> dict:
        """Fetch data from the instrument API.
        
        Args:
            url: API endpoint URL
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If the request fails
        """
        start_time = time.time()
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                elapsed_time = time.time() - start_time
                logger.debug(f"Request to {url} took {elapsed_time:.3f} seconds")
                
                return data
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def insert_tag_values(self, data: dict, filter_tags: list = None):
        """Insert tag values from the batch JSON data into the TagValues table.
        
        Args:
            data: JSON data containing tag values from /api/valuelist
            filter_tags: Optional list of tag names to filter. If None, insert all tags.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            
            values = data.get("values", [])
            inserted_count = 0
            
            for value in values:
                tag_name = value.get("name")
                if not tag_name:
                    continue
                
                # Filter tags if specified
                if filter_tags and tag_name not in filter_tags:
                    continue
                
                # Get tag ID from TagList
                cursor.execute('SELECT id FROM TagList WHERE Name = ?', (tag_name,))
                result = cursor.fetchone()
                
                if result:
                    tag_id = result[0]
                    cursor.execute('''
                        INSERT INTO TagValues (TagName_id, Value, DateTime)
                        VALUES (?, ?, ?)
                    ''', (tag_id, value.get("value"), current_time))
                    inserted_count += 1
                else:
                    logger.warning(f"Tag {tag_name} not found in TagList")
            
            conn.commit()
            conn.close()
            logger.debug(f"Inserted {inserted_count} tag values")
            
        except Exception as e:
            logger.error(f"Failed to insert tag values: {e}")
            self.update_status(f"ERROR: Database insert failed - {e}")
    
    def collect_all_data(self):
        """Collect all data from the instrument using batch valuelist endpoint (every all_values_interval)."""
        try:
            logger.info("Collecting all data from instrument...")
            data = self.get_api_data(self.instrument_url)
            self.insert_tag_values(data)  # Insert all values
            logger.info("All data collected successfully")
            
        except Exception as e:
            error_msg = f"Failed to collect all data: {e}"
            logger.error(error_msg)
            self.update_status(error_msg)
    
    def collect_concentration_data(self):
        """Collect concentration data from the instrument using batch valuelist endpoint (every concentration_interval)."""
        try:
            logger.debug("Collecting concentration data...")
            data = self.get_api_data(self.instrument_url)
            self.insert_tag_values(data, filter_tags=self.concentration_tags)
            logger.debug("Concentration data collected successfully")
            
        except Exception as e:
            error_msg = f"Failed to collect concentration data: {e}"
            logger.error(error_msg)
            self.update_status(error_msg)
    
    def collect_status_warnings_data(self):
        """Collect status and warnings data from the instrument using batch valuelist endpoint (every status_check_interval)."""
        try:
            logger.debug("Collecting status and warnings data...")
            data = self.get_api_data(self.instrument_url)
            
            # Filter for status and warning tags
            status_warning_tags = []
            for tag_group in ['instrument_status', 'warning_tags', 'flow_tags', 'temperature']:
                tags = self.config.get(f'instrument.tags.{tag_group}', [])
                status_warning_tags.extend(tags)
            
            # Remove duplicates
            status_warning_tags = list(set(status_warning_tags))
            
            self.insert_tag_values(data, filter_tags=status_warning_tags)
            logger.debug("Status and warnings data collected successfully")
            
        except Exception as e:
            error_msg = f"Failed to collect status and warnings data: {e}"
            logger.error(error_msg)
            self.update_status(error_msg)
    
    def connect_instrument(self) -> bool:
        """Test connection to the instrument.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info("Testing connection to instrument...")
            data = self.get_api_data(self.instrument_url)
            
            # Connection successful
            if not self.connected:
                # Status changed from disconnected to connected
                self.connected = True
                self.update_status("CONNECTED")
                logger.info("Instrument connected successfully")
            # If already connected, no need to update status file again
            
            return True
            
        except Exception as e:
            error_msg = f"Connection failed: {e}"
            logger.error(error_msg)
            
            # Connection failed
            if self.connected:
                # Status changed from connected to disconnected
                self.connected = False
                self.update_status(error_msg)
            else:
                # Was already disconnected, just log the error
                self.connected = False
            
            return False
    
    def run(self):
        """Main data collection loop."""
        logger.info("Starting CO_O2Analyser data collection service...")
        
        # Initial connection test
        if not self.connect_instrument():
            logger.error("Failed to establish initial connection. Exiting.")
            return
        
        # Initialize counters with current time to avoid immediate execution
        current_time = time.time()
        all_data_counter = current_time
        conc_counter = current_time
        status_warnings_counter = current_time
        connection_check_counter = current_time
        
        logger.info(f"Data collection started:")
        logger.info(f"  - All data: every {self.all_values_interval}s")
        logger.info(f"  - Concentration: every {self.concentration_interval}s")
        logger.info(f"  - Status/Warnings: every {self.status_check_interval}s")
        
        try:
            while True:
                current_time = time.time()
                
                # Collect all data every all_values_interval (default: 5 minutes)
                if current_time - all_data_counter >= self.all_values_interval:
                    self.collect_all_data()
                    all_data_counter = current_time
                
                # Collect concentration data every concentration_interval (default: 1.5 seconds)
                if current_time - conc_counter >= self.concentration_interval:
                    self.collect_concentration_data()
                    conc_counter = current_time
                
                # Collect status and warnings data every status_check_interval (default: 30 seconds)
                if current_time - status_warnings_counter >= self.status_check_interval:
                    self.collect_status_warnings_data()
                    status_warnings_counter = current_time
                
                # Re-check connection every 5 minutes
                if current_time - connection_check_counter >= 300:  # 5 minutes
                    self.connect_instrument()
                    connection_check_counter = current_time
                
                # Sleep for a short time to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Data collection service stopped by user")
            self.update_status("STOPPED by user")
        except Exception as e:
            error_msg = f"Unexpected error in data collection loop: {e}"
            logger.error(error_msg)
            self.update_status(error_msg)
            raise


def main():
    """Main entry point for the data collection service."""
    try:
        # Load configuration
        config = Config()
        
        # Create and run the data collector
        collector = InstrumentDataCollector(config)
        collector.run()
        
    except Exception as e:
        logger.error(f"Failed to start data collection service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()