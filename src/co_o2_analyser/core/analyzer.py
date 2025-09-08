"""
Main analyzer class for CO_O2_Analyser.

This module contains the main analyzer logic that coordinates
instrument communication, data processing, and storage.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import asdict
from pathlib import Path

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
        self.db_manager = DatabaseManager(config.get('database.path', 'data.sqlite'))
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
            
            # Add to current measurement session if active
            if self.measurement_db_manager.is_collecting:
                self.measurement_db_manager.add_measurement(
                    measurement.co_concentration or 0.0,
                    measurement.o2_concentration or 0.0,
                    measurement.sample_temp,
                    measurement.sample_flow
                )
            
            logger.debug(f"Measurement recorded: CO={measurement.co_concentration}, O2={measurement.o2_concentration}")
            return measurement
            
        except Exception as e:
            logger.error(f"Failed to get current measurement: {e}")
            return None
    
    def get_measurement_history(self, limit: int = 100) -> List[Measurement]:
        """Get measurement history from the most recent session.
        
        Args:
            limit: Maximum number of measurements to return
            
        Returns:
            List of measurements
        """
        try:
            # Get the most recent session
            sessions = self.measurement_db_manager.list_measurement_sessions()
            if not sessions:
                logger.info("No measurement sessions found")
                return []
            
            # Get measurements from the most recent session
            latest_session = sessions[0]
            raw_data = self.measurement_db_manager.get_measurements(
                latest_session['file_path'], limit
            )
            
            # Convert to Measurement objects
            measurements = []
            for data in raw_data:
                measurement = Measurement(
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    co_concentration=data['co_concentration'],
                    o2_concentration=data['o2_concentration'],
                    sample_temp=data['sample_temp'],
                    sample_flow=data['sample_flow'],
                    instrument_status=data.get('air_quality_status', 'Unknown')
                )
                measurements.append(measurement)
            
            logger.debug(f"Retrieved {len(measurements)} measurements from latest session")
            return measurements
            
        except Exception as e:
            logger.error(f"Failed to get measurement history: {e}")
            return []
    
    def export_data(self, format: str = 'csv', start_date: Optional[datetime] = None, 
                   end_date: Optional[datetime] = None, session_path: Optional[str] = None) -> str:
        """Export measurement data to file.
        
        Args:
            format: Export format ('csv', 'json', 'excel')
            start_date: Start date for export range
            end_date: End date for export range
            session_path: Specific session to export (if None, uses most recent)
            
        Returns:
            Path to exported file
        """
        try:
            if session_path:
                # Export specific session
                raw_data = self.measurement_db_manager.get_measurements(session_path, limit=10000)
            else:
                # Get measurements from most recent session
                measurements = self.get_measurement_history(limit=10000)
                raw_data = [m.to_dict() for m in measurements]
            
            # Filter by date range if specified
            if start_date or end_date:
                filtered_data = []
                for data in raw_data:
                    timestamp = datetime.fromisoformat(data['timestamp'])
                    if start_date and timestamp < start_date:
                        continue
                    if end_date and timestamp > end_date:
                        continue
                    filtered_data.append(data)
                raw_data = filtered_data
            
            # Export based on format
            if format.lower() == 'csv':
                return self._export_to_csv(raw_data)
            elif format.lower() == 'json':
                return self._export_to_json(raw_data)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise
    
    def export_measurement_session(self, session_path: str, format: str = 'csv') -> str:
        """Export data from a specific measurement session.
        
        Args:
            session_path: Path to the measurement session database
            format: Export format ('csv', 'json')
            
        Returns:
            Path to exported file
        """
        try:
            # Get session metadata to create a meaningful filename
            session_metadata = self._get_session_metadata(session_path)
            
            # Get measurements from the session
            raw_data = self.measurement_db_manager.get_measurements(session_path, limit=10000)
            
            if not raw_data:
                raise ValueError(f"No data found in session: {session_path}")
            
            # Create results directory if it doesn't exist
            results_dir = Path("results")
            results_dir.mkdir(exist_ok=True)
            
            # Create filename with session date and time
            session_date = session_metadata.get('start_time', datetime.now().strftime('%Y%m%d_%H%M%S'))
            if isinstance(session_date, str):
                session_date = datetime.fromisoformat(session_date)
            
            filename = f"measurement_{session_date.strftime('%Y%m%d_%H%M%S')}.{format}"
            export_path = results_dir / filename
            
            # Export based on format
            if format.lower() == 'csv':
                return self._export_session_to_csv(raw_data, export_path, session_metadata)
            elif format.lower() == 'json':
                return self._export_session_to_json(raw_data, export_path, session_metadata)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Failed to export measurement session: {e}")
            raise
    
    def _get_session_metadata(self, session_path: str) -> Dict[str, Any]:
        """Get metadata for a measurement session.
        
        Args:
            session_path: Path to the measurement session database
            
        Returns:
            Dictionary with session metadata
        """
        try:
            import sqlite3
            conn = sqlite3.connect(session_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT start_time, end_time, duration_seconds, total_measurements
                FROM session_metadata 
                ORDER BY id DESC 
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'start_time': row[0],
                    'end_time': row[1],
                    'duration_seconds': row[2],
                    'total_measurements': row[3]
                }
            else:
                return {}
                
        except Exception as e:
            logger.warning(f"Failed to get session metadata: {e}")
            return {}
    
    def _export_session_to_csv(self, measurements: List[Dict[str, Any]], export_path: Path, 
                              session_metadata: Dict[str, Any]) -> str:
        """Export session measurements to CSV file with metadata header."""
        import csv
        
        with open(export_path, 'w', newline='') as csvfile:
            # Write session metadata as comments at the top
            csvfile.write("# Measurement Session Export\n")
            csvfile.write(f"# Session Start: {session_metadata.get('start_time', 'Unknown')}\n")
            csvfile.write(f"# Session End: {session_metadata.get('end_time', 'Unknown')}\n")
            csvfile.write(f"# Duration: {session_metadata.get('duration_seconds', 'Unknown')} seconds\n")
            csvfile.write(f"# Total Measurements: {session_metadata.get('total_measurements', 'Unknown')}\n")
            csvfile.write("#\n")
            
            # Include all possible fields from Measurement model
            fieldnames = ['timestamp', 'co_concentration', 'o2_concentration', 
                         'sample_temp', 'sample_flow', 'fume_limit_mg_m3', 
                         'percentage_to_limit', 'air_quality_status', 'instrument_status',
                         'error_code', 'warning_flags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for measurement in measurements:
                # Filter out None values and convert lists to strings for CSV
                filtered_measurement = {}
                for key, value in measurement.items():
                    if value is not None:
                        if isinstance(value, list):
                            filtered_measurement[key] = str(value)
                        else:
                            filtered_measurement[key] = value
                
                # Write only the fields that exist in the measurement
                writer.writerow(filtered_measurement)
        
        logger.info(f"Session data exported to CSV: {export_path}")
        return str(export_path)
    
    def _export_session_to_json(self, measurements: List[Dict[str, Any]], export_path: Path,
                               session_metadata: Dict[str, Any]) -> str:
        """Export session measurements to JSON file with metadata."""
        import json
        
        export_data = {
            'session_metadata': session_metadata,
            'measurements': measurements
        }
        
        with open(export_path, 'w') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, default=str)
        
        logger.info(f"Session data exported to JSON: {export_path}")
        return str(export_path)
    
    def _export_to_csv(self, measurements: List[Dict[str, Any]]) -> str:
        """Export measurements to CSV file."""
        import csv
        from pathlib import Path
        
        # Create results directory if it doesn't exist
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        export_path = results_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(export_path, 'w', newline='') as csvfile:
            # Include all possible fields from Measurement model
            fieldnames = ['timestamp', 'co_concentration', 'o2_concentration', 
                         'sample_temp', 'sample_flow', 'fume_limit_mg_m3', 
                         'percentage_to_limit', 'air_quality_status', 'instrument_status',
                         'error_code', 'warning_flags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for measurement in measurements:
                # Filter out None values and convert lists to strings for CSV
                filtered_measurement = {}
                for key, value in measurement.items():
                    if value is not None:
                        if isinstance(value, list):
                            filtered_measurement[key] = str(value)
                        else:
                            filtered_measurement[key] = value
                
                # Write only the fields that exist in the measurement
                writer.writerow(filtered_measurement)
        
        logger.info(f"Data exported to CSV: {export_path}")
        return str(export_path)
    
    def _export_to_json(self, measurements: List[Dict[str, Any]]) -> str:
        """Export measurements to JSON file."""
        import json
        from pathlib import Path
        
        export_path = Path(f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(export_path, 'w') as jsonfile:
            json.dump(measurements, jsonfile, indent=2)
        
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
