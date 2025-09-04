"""
Database management for CO_O2_Analyser.

This module handles database operations including connection management,
data storage, and retrieval for measurement data.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for the application.
    
    This class handles the main data.sqlite database which contains:
    - TagList: Instrument tag metadata
    - TagValues: Time-series tag values
    """
    
    def __init__(self, db_path: str = "data.sqlite"):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"Database connection initialized: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def get_recent_data(self, seconds: int = 5) -> bool:
        """Check if there is recent data in the TagValues table.
        
        Args:
            seconds: Number of seconds to look back for recent data
            
        Returns:
            True if recent data exists, False otherwise
        """
        try:
            if not self.connection:
                return False
                
            # Calculate timestamp threshold
            from datetime import datetime, timedelta
            threshold = datetime.now() - timedelta(seconds=seconds)
            
            # Check if there's any data within the time threshold
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM TagValues 
                WHERE DateTime >= ?
            """, (threshold,))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Exception as e:
            logger.error(f"Failed to check for recent data: {e}")
            return False


class MeasurementDatabaseManager:
    """Manages measurement session databases with date-based naming."""
    
    def __init__(self, base_path: str = "."):
        """Initialize measurement database manager.
        
        Args:
            base_path: Base directory for measurement databases
        """
        self.base_path = Path(base_path)
        self.current_session = None
        self.session_start_time = None
        self.session_end_time = None
        self.collection_duration = 600  # 10 minutes in seconds
        self.is_collecting = False
        
        # Ensure measurements directory exists
        self.measurements_dir = self.base_path / "measurements"
        self.measurements_dir.mkdir(exist_ok=True)
        
        logger.info(f"Measurement database manager initialized in {self.measurements_dir}")
    
    def start_measurement_session(self, duration_minutes: int = 10) -> str:
        """Start a new measurement session.
        
        Args:
            duration_minutes: Duration of measurement session in minutes
            
        Returns:
            Path to the created measurement database
        """
        try:
            # Create date-based database name
            now = datetime.now()
            db_name = f"measurement{now.strftime('%d%m%y')}.sqlite"
            db_path = self.measurements_dir / db_name
            
            # Initialize session
            self.current_session = db_path
            self.session_start_time = now
            self.collection_duration = duration_minutes * 60  # Convert to seconds
            self.is_collecting = True
            
            # Create database and tables
            self._create_measurement_database(db_path)
            
            logger.info(f"Started measurement session: {db_path}")
            logger.info(f"Session duration: {duration_minutes} minutes")
            
            return str(db_path)
            
        except Exception as e:
            logger.error(f"Failed to start measurement session: {e}")
            raise
    
    def stop_measurement_session(self) -> Optional[str]:
        """Stop the current measurement session.
        
        Returns:
            Path to the measurement database or None if no active session
        """
        try:
            if not self.is_collecting or not self.current_session:
                logger.warning("No active measurement session to stop")
                return None
            
            self.session_end_time = datetime.now()
            self.is_collecting = False
            
            # Update session metadata
            self._update_session_metadata()
            
            session_path = str(self.current_session)
            logger.info(f"Stopped measurement session: {session_path}")
            logger.info(f"Session duration: {self._get_session_duration():.1f} seconds")
            
            # Reset session
            self.current_session = None
            self.session_start_time = None
            self.session_end_time = None
            
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
            if not self.current_session:
                logger.info("No measurement session to force stop")
                return None
            
            # Force set end time if not already set
            if not self.session_end_time:
                self.session_end_time = datetime.now()
                logger.info("Force setting end_time for interrupted session")
            
            # Update session metadata
            self._update_session_metadata()
            
            session_path = str(self.current_session)
            logger.info(f"Force stopped measurement session: {session_path}")
            logger.info(f"Session duration: {self._get_session_duration():.1f} seconds")
            
            # Reset session
            self.current_session = None
            self.session_start_time = None
            self.session_end_time = None
            
            return session_path
            
        except Exception as e:
            logger.error(f"Failed to force stop measurement session: {e}")
            return None
    
    def _create_measurement_database(self, db_path: Path):
        """Create a new measurement database with tables.
        
        Args:
            db_path: Path to the database file
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Session metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    duration_seconds INTEGER,
                    total_measurements INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Measurements table with fume limit calculations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    co_concentration REAL,
                    o2_concentration REAL,
                    sample_temp REAL,
                    sample_flow REAL,
                    fume_limit_mg_m3 REAL,
                    percentage_to_limit REAL,
                    air_quality_status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert initial session metadata
            cursor.execute("""
                INSERT INTO session_metadata (start_time, duration_seconds)
                VALUES (?, ?)
            """, (self.session_start_time.isoformat(), self.collection_duration))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created measurement database: {db_path}")
            
        except Exception as e:
            logger.error(f"Failed to create measurement database: {e}")
            raise
    
    def _update_session_metadata(self):
        """Update session metadata with end time and measurement count."""
        try:
            if not self.current_session:
                return
            
            conn = sqlite3.connect(self.current_session)
            cursor = conn.cursor()
            
            # Get measurement count
            cursor.execute("SELECT COUNT(*) FROM measurements")
            total_measurements = cursor.fetchone()[0]
            
            # Update session metadata
            cursor.execute("""
                UPDATE session_metadata 
                SET end_time = ?, total_measurements = ?
                WHERE id = 1
            """, (self.session_end_time.isoformat(), total_measurements))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated session metadata: {total_measurements} measurements")
            
        except Exception as e:
            logger.error(f"Failed to update session metadata: {e}")
    
    def add_measurement(self, co_concentration: float, o2_concentration: float, 
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
        try:
            if not self.is_collecting or not self.current_session:
                logger.warning("No active measurement session")
                return False
            
            # Calculate fume limit and percentage to limit
            fume_limit, percentage_to_limit, air_quality = self._calculate_fume_metrics(
                co_concentration, o2_concentration
            )
            
            # Insert measurement
            conn = sqlite3.connect(self.current_session)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO measurements 
                (timestamp, co_concentration, o2_concentration, sample_temp, sample_flow,
                 fume_limit_mg_m3, percentage_to_limit, air_quality_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                co_concentration,
                o2_concentration,
                sample_temp,
                sample_flow,
                fume_limit,
                percentage_to_limit,
                air_quality
            ))
            
            conn.commit()
            conn.close()
            
            logger.debug(f"Added measurement: CO={co_concentration:.2f}, O2={o2_concentration:.2f}, "
                        f"Fume={fume_limit:.1f}mg/m³ ({percentage_to_limit:.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add measurement: {e}")
            return False
    
    def _calculate_fume_metrics(self, co_concentration: float, o2_concentration: float) -> tuple:
        """Calculate fume limit metrics based on CO and O2 concentrations.
        
        Args:
            co_concentration: CO concentration in ppm
            o2_concentration: O2 concentration in %
            
        Returns:
            Tuple of (fume_limit_mg_m3, percentage_to_limit, air_quality_status)
        """
        try:
            # Check if this is fresh air (O2 close to 21%, CO low)
            if o2_concentration >= 18.0 and co_concentration <= 50:
                # Fresh air conditions - simple conversion
                fume_limit = co_concentration * 1.25
                air_quality = "Fresh Air"
            elif o2_concentration < 18.0:  # Industrial exhaust conditions
                # Use the full formula for exhaust fumes
                fume_limit = (co_concentration * 1.25 * 
                             ((21 - 13) / (21 - o2_concentration)))
                air_quality = "Industrial Exhaust"
            else:
                # Invalid conditions
                fume_limit = 0.0
                air_quality = "Invalid O₂"
            
            # Calculate percentage to 500 mg/m³ limit
            co_limit = 500.0  # mg/m³
            percentage_to_limit = (fume_limit / co_limit) * 100 if co_limit > 0 else 0
            
            return fume_limit, percentage_to_limit, air_quality
            
        except Exception as e:
            logger.error(f"Failed to calculate fume metrics: {e}")
            return 0.0, 0.0, "Error"
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status.
        
        Returns:
            Dictionary with session status information
        """
        try:
            if not self.is_collecting or not self.current_session:
                return {
                    'is_collecting': False,
                    'session_path': None,
                    'start_time': None,
                    'elapsed_time': 0,
                    'remaining_time': 0,
                    'measurement_count': 0
                }
            
            # Get measurement count
            conn = sqlite3.connect(self.current_session)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM measurements")
            measurement_count = cursor.fetchone()[0]
            conn.close()
            
            # Calculate times
            elapsed_time = (datetime.now() - self.session_start_time).total_seconds()
            remaining_time = max(0, self.collection_duration - elapsed_time)
            
            return {
                'is_collecting': True,
                'session_path': str(self.current_session),
                'start_time': self.session_start_time.isoformat(),
                'elapsed_time': elapsed_time,
                'remaining_time': remaining_time,
                'measurement_count': measurement_count,
                'duration_minutes': self.collection_duration / 60
            }
            
        except Exception as e:
            logger.error(f"Failed to get session status: {e}")
            return {'is_collecting': False, 'error': str(e)}
    
    def get_measurements(self, session_path: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get measurements from a specific session.
        
        Args:
            session_path: Path to the measurement database
            limit: Maximum number of measurements to return
            
        Returns:
            List of measurement dictionaries
        """
        try:
            if not Path(session_path).exists():
                logger.error(f"Measurement database not found: {session_path}")
                return []
            
            conn = sqlite3.connect(session_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT timestamp, co_concentration, o2_concentration, sample_temp, sample_flow,
                       fume_limit_mg_m3, percentage_to_limit, air_quality_status
                FROM measurements 
                ORDER BY timestamp ASC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to list of dictionaries
            measurements = []
            field_names = ['timestamp', 'co_concentration', 'o2_concentration', 'sample_temp', 
                          'sample_flow', 'fume_limit_mg_m3', 'percentage_to_limit', 'air_quality_status']
            
            for row in rows:
                measurement_dict = dict(zip(field_names, row))
                measurements.append(measurement_dict)
            
            logger.info(f"Retrieved {len(measurements)} measurements from {session_path}")
            return measurements
            
        except Exception as e:
            logger.error(f"Failed to get measurements: {e}")
            return []
    
    def _get_session_duration(self) -> float:
        """Get the duration of the current session in seconds."""
        if self.session_start_time and self.session_end_time:
            return (self.session_end_time - self.session_start_time).total_seconds()
        elif self.session_start_time:
            return (datetime.now() - self.session_start_time).total_seconds()
        return 0.0
    
    def list_measurement_sessions(self) -> List[Dict[str, Any]]:
        """List all available measurement sessions.
        
        Returns:
            List of session information dictionaries
        """
        try:
            sessions = []
            
            for db_file in self.measurements_dir.glob("measurement*.sqlite"):
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Get session metadata
                    cursor.execute("""
                        SELECT start_time, end_time, duration_seconds, total_measurements
                        FROM session_metadata 
                        ORDER BY id DESC 
                        LIMIT 1
                    """)
                    
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        start_time, end_time, duration_seconds, total_measurements = result
                        sessions.append({
                            'file_path': str(db_file),
                            'file_name': db_file.name,
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration_seconds': duration_seconds,
                            'total_measurements': total_measurements,
                            'file_size': db_file.stat().st_size
                        })
                        
                except Exception as e:
                    logger.warning(f"Failed to read session metadata from {db_file}: {e}")
                    continue
            
            # Sort by start time (newest first)
            sessions.sort(key=lambda x: x['start_time'], reverse=True)
            
            logger.info(f"Found {len(sessions)} measurement sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list measurement sessions: {e}")
            return []
    
    def fix_incomplete_sessions(self) -> int:
        """Fix sessions that don't have end_time recorded.
        
        This method finds sessions without end_time and sets it to the last measurement timestamp.
        
        Returns:
            Number of sessions fixed
        """
        try:
            fixed_count = 0
            
            for db_file in self.measurements_dir.glob("measurement*.sqlite"):
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Check if there are sessions without end_time
                    cursor.execute("""
                        SELECT id, start_time FROM session_metadata 
                        WHERE end_time IS NULL OR end_time = ''
                    """)
                    
                    incomplete_sessions = cursor.fetchall()
                    
                    for session_id, start_time in incomplete_sessions:
                        # Get the last measurement timestamp
                        cursor.execute("""
                            SELECT MAX(timestamp) FROM measurements
                        """)
                        
                        last_measurement = cursor.fetchone()[0]
                        
                        if last_measurement:
                            # Update the session with end_time
                            cursor.execute("""
                                UPDATE session_metadata 
                                SET end_time = ?
                                WHERE id = ?
                            """, (last_measurement, session_id))
                            
                            # Also update total_measurements count
                            cursor.execute("SELECT COUNT(*) FROM measurements")
                            total_measurements = cursor.fetchone()[0]
                            
                            cursor.execute("""
                                UPDATE session_metadata 
                                SET total_measurements = ?
                                WHERE id = ?
                            """, (total_measurements, session_id))
                            
                            fixed_count += 1
                            logger.info(f"Fixed incomplete session {session_id} in {db_file.name}")
                        else:
                            # No measurements, set end_time to start_time
                            cursor.execute("""
                                UPDATE session_metadata 
                                SET end_time = ?, total_measurements = 0
                                WHERE id = ?
                            """, (start_time, session_id))
                            
                            fixed_count += 1
                            logger.info(f"Fixed empty session {session_id} in {db_file.name}")
                    
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    logger.warning(f"Failed to fix sessions in {db_file}: {e}")
                    continue
            
            if fixed_count > 0:
                logger.info(f"Fixed {fixed_count} incomplete measurement sessions")
            else:
                logger.info("No incomplete sessions found")
            
            return fixed_count
            
        except Exception as e:
            logger.error(f"Failed to fix incomplete sessions: {e}")
            return 0
