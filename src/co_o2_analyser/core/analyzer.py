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
from ..utils.database import DatabaseManager, MeasurementDatabaseManager
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
        self.measurement_db_manager = MeasurementDatabaseManager()
        self.instrument = InstrumentCommunication(config)
        self.data_processor = DataProcessor()
        
        # Fix any incomplete sessions from previous runs
        try:
            fixed_count = self.measurement_db_manager.fix_incomplete_sessions()
            if fixed_count > 0:
                logger.info(f"Fixed {fixed_count} incomplete measurement sessions from previous runs")
        except Exception as e:
            logger.warning(f"Failed to fix incomplete sessions: {e}")
        
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
                sample_temp=processed_data.get('sample_temp'),
                sample_flow=processed_data.get('sample_flow'),
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
                         'temperature', 'humidity', 'pressure', 'instrument_status', 'fume_limit_mg_m3', 'percentage_to_limit']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for measurement in measurements:
                # Calculate fume limit for each measurement
                measurement_dict = measurement.to_dict()
                if (measurement.co_concentration is not None and 
                    measurement.o2_concentration is not None):
                    
                    # Check if this is fresh air (O2 close to 21%, CO low)
                    if (measurement.o2_concentration >= 18.0 and 
                        measurement.co_concentration <= 50):
                        # Fresh air conditions - simple conversion
                        fume_limit = measurement.co_concentration * 1.25
                        measurement_dict['fume_limit_mg_m3'] = f"{fume_limit:.1f}"
                    elif measurement.o2_concentration < 18.0:  # Industrial exhaust conditions
                        # Use the full formula for exhaust fumes
                        fume_limit = (measurement.co_concentration * 1.25 * 
                                     ((21 - 13) / (21 - measurement.o2_concentration)))
                        
                        # Calculate percentage to 500 mg/m³ limit
                        co_limit = 500.0  # mg/m³
                        percentage_to_limit = (fume_limit / co_limit) * 100
                        
                        # Add both fume limit and percentage to CSV
                        measurement_dict['fume_limit_mg_m3'] = f"{fume_limit:.1f}"
                        measurement_dict['percentage_to_limit'] = f"{percentage_to_limit:.1f}%"
                    else:
                        measurement_dict['fume_limit_mg_m3'] = "--"
                        measurement_dict['percentage_to_limit'] = "--"
                else:
                    measurement_dict['fume_limit_mg_m3'] = "--"
                
                writer.writerow(measurement_dict)
        
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
    
    def start_measurement_session(self, duration_minutes: int = 10) -> str:
        """Start a new measurement session.
        
        Args:
            duration_minutes: Duration of measurement session in minutes
            
        Returns:
            Path to the created measurement database
        """
        try:
            session_path = self.measurement_db_manager.start_measurement_session(duration_minutes)
            logger.info(f"Started measurement session: {session_path}")
            return session_path
        except Exception as e:
            logger.error(f"Failed to start measurement session: {e}")
            raise
    
    def stop_measurement_session(self) -> Optional[str]:
        """Stop the current measurement session.
        
        Returns:
            Path to the measurement database or None if no active session
        """
        try:
            session_path = self.measurement_db_manager.stop_measurement_session()
            if session_path:
                logger.info(f"Stopped measurement session: {session_path}")
            return session_path
        except Exception as e:
            logger.error(f"Failed to stop measurement session: {e}")
            return None
    
    def force_stop_measurement_session(self) -> Optional[str]:
        """Force stop any active measurement session (for cleanup).
        
        This method ensures that even if a session was interrupted,
        the end_time is recorded properly.
        
        Returns:
            Path to the measurement database or None if no active session
        """
        try:
            session_path = self.measurement_db_manager.force_stop_measurement_session()
            if session_path:
                logger.info(f"Force stopped measurement session: {session_path}")
            return session_path
        except Exception as e:
            logger.error(f"Failed to force stop measurement session: {e}")
            return None
    
    def get_measurement_session_status(self) -> Dict[str, Any]:
        """Get current measurement session status.
        
        Returns:
            Dictionary with session status information
        """
        return self.measurement_db_manager.get_session_status()
    
    def add_measurement_to_session(self, co_concentration: float, o2_concentration: float, 
                                  sample_temp: Optional[float] = None, sample_flow: Optional[float] = None) -> bool:
        """Add a measurement to the current session.
        
        Args:
            co_concentration: CO concentration in ppm
            o2_concentration: O2 concentration in %
            sample_temp: Sample temperature in °C
            sample_flow: Sample flow rate in cc/min
            
        Returns:
            True if measurement was added successfully
        """
        return self.measurement_db_manager.add_measurement(
            co_concentration, o2_concentration, sample_temp, sample_flow
        )
    
    def get_measurement_session_data(self, session_path: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get measurements from a specific session.
        
        Args:
            session_path: Path to the measurement database
            limit: Maximum number of measurements to return
            
        Returns:
            List of measurement dictionaries
        """
        return self.measurement_db_manager.get_measurements(session_path, limit)
    
    def list_measurement_sessions(self) -> List[Dict[str, Any]]:
        """List all available measurement sessions.
        
        Returns:
            List of session information dictionaries
        """
        return self.measurement_db_manager.list_measurement_sessions()
    
    def fix_incomplete_sessions(self) -> int:
        """Fix sessions that don't have end_time recorded.
        
        This method finds sessions without end_time and sets it to the last measurement timestamp.
        
        Returns:
            Number of sessions fixed
        """
        return self.measurement_db_manager.fix_incomplete_sessions()
    
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
