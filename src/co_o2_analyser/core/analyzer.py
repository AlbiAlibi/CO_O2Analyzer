"""
Main analyzer class for CO_O2_Analyser.

This module contains the main analyzer logic that coordinates
instrument communication, data processing, and storage.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import asdict

from ..data.models import Measurement
from ..utils.config import Config
from ..utils.database import DatabaseManager
from .instrument_communication import InstrumentCommunication
from .data_processor import DataProcessor


logger = logging.getLogger(__name__)


class COO2Analyzer:
    """Main analyzer class that coordinates all operations."""
    
    def __init__(self, config: Config):
        """Initialize the analyzer.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.db_manager = DatabaseManager(config.get('database.path'))
        self.instrument = InstrumentCommunication(config)
        self.data_processor = DataProcessor()
        
        logger.info("COO2Analyzer initialized")
    
    def start_monitoring(self) -> bool:
        """Start continuous monitoring of the instrument.
        
        Returns:
            True if monitoring started successfully
        """
        try:
            # Test connection to instrument
            if not self.instrument.test_connection():
                logger.error("Failed to connect to instrument")
                return False
            
            logger.info("Monitoring started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        logger.info("Monitoring stopped")
    
    def get_current_measurement(self) -> Optional[Measurement]:
        """Get the current measurement from the instrument.
        
        Returns:
            Current measurement or None if failed
        """
        try:
            # Get raw data from instrument
            raw_data = self.instrument.get_current_values()
            if not raw_data:
                logger.warning("No data received from instrument")
                return None
            
            # Process the data
            processed_data = self.data_processor.process_raw_data(raw_data)
            
            # Create measurement object
            measurement = Measurement(
                timestamp=datetime.now(),
                co_concentration=processed_data.get('co_concentration'),
                o2_concentration=processed_data.get('o2_concentration'),
                temperature=processed_data.get('temperature'),
                humidity=processed_data.get('humidity'),
                pressure=processed_data.get('pressure'),
                instrument_status=processed_data.get('status')
            )
            
            # Store in database
            self.db_manager.insert_measurement(measurement.to_dict())
            
            logger.debug(f"Measurement recorded: CO={measurement.co_concentration}, O2={measurement.o2_concentration}")
            return measurement
            
        except Exception as e:
            logger.error(f"Failed to get current measurement: {e}")
            return None
    
    def get_measurement_history(self, limit: int = 100) -> List[Measurement]:
        """Get measurement history from database.
        
        Args:
            limit: Maximum number of measurements to return
            
        Returns:
            List of measurements
        """
        try:
            raw_data = self.db_manager.get_measurements(limit=limit)
            measurements = [Measurement.from_dict(data) for data in raw_data]
            logger.debug(f"Retrieved {len(measurements)} measurements from history")
            return measurements
            
        except Exception as e:
            logger.error(f"Failed to get measurement history: {e}")
            return []
    
    def export_data(self, format: str = 'csv', start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None) -> str:
        """Export measurement data to file.
        
        Args:
            format: Export format ('csv', 'json', 'excel')
            start_date: Start date for export range
            end_date: End date for export range
            
        Returns:
            Path to exported file
        """
        try:
            # Get measurements for the date range
            measurements = self.get_measurement_history(limit=10000)  # Large limit for export
            
            if start_date:
                measurements = [m for m in measurements if m.timestamp >= start_date]
            if end_date:
                measurements = [m for m in measurements if m.timestamp <= end_date]
            
            # Export based on format
            if format.lower() == 'csv':
                return self._export_to_csv(measurements)
            elif format.lower() == 'json':
                return self._export_to_json(measurements)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise
    
    def _export_to_csv(self, measurements: List[Measurement]) -> str:
        """Export measurements to CSV file."""
        import csv
        from pathlib import Path
        
        export_path = Path(f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        with open(export_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'co_concentration', 'o2_concentration', 
                         'temperature', 'humidity', 'pressure', 'instrument_status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for measurement in measurements:
                writer.writerow(measurement.to_dict())
        
        logger.info(f"Data exported to CSV: {export_path}")
        return str(export_path)
    
    def _export_to_json(self, measurements: List[Measurement]) -> str:
        """Export measurements to JSON file."""
        import json
        from pathlib import Path
        
        export_path = Path(f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        data = [measurement.to_dict() for measurement in measurements]
        
        with open(export_path, 'w') as jsonfile:
            json.dump(data, jsonfile, indent=2)
        
        logger.info(f"Data exported to JSON: {export_path}")
        return str(export_path)
    
    def close(self):
        """Clean up resources."""
        if self.db_manager:
            self.db_manager.close()
        logger.info("COO2Analyzer closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
