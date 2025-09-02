"""
Data harvester module for CO_O2_Analyser.

This module provides classes to harvest data from various sources,
including the local SQLite database populated by CO_O2Analyser.py.
"""

import sqlite3
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLiteDataHarvester:
    """Harvests data from the local SQLite database populated by CO_O2Analyser.py."""
    
    def __init__(self, db_path: str = "data.sqlite"):
        """Initialize the SQLite data harvester.
        
        Args:
            db_path: Path to the data.sqlite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the database file exists."""
        if not Path(self.db_path).exists():
            logger.warning(f"Database {self.db_path} not found. Data harvesting will fail.")
    
    def _get_connection(self):
        """Get a database connection."""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return None
    
    def get_tag_precision(self, tag_name: str) -> Optional[int]:
        """Get the precision for a specific tag from TagList.
        
        Args:
            tag_name: Name of the tag to get precision for
            
        Returns:
            Precision value (number of decimal places) or None if not found
        """
        conn = self._get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Precision FROM TagList WHERE Name = ?", (tag_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get precision for tag {tag_name}: {e}")
            return None
        finally:
            conn.close()
    
    def get_tag_units(self, tag_name: str) -> Optional[str]:
        """Get the units for a specific tag from TagList.
        
        Args:
            tag_name: Name of the tag to get units for
            
        Returns:
            Units string or None if not found
        """
        conn = self._get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT Units FROM TagList WHERE Name = ?", (tag_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Failed to get units for tag {tag_name}: {e}")
            return None
        finally:
            conn.close()
    
    def format_tag_value(self, tag_name: str, value: Any, include_units: bool = True) -> str:
        """Format a tag value using its precision and units from TagList.
        
        Args:
            tag_name: Name of the tag
            value: Value to format
            include_units: Whether to include units in the formatted string
            
        Returns:
            Formatted value string with optional units
        """
        try:
            # Try to convert to float
            float_value = float(value)
            
            # Get precision from database
            precision = self.get_tag_precision(tag_name)
            
            if precision is not None:
                # Use precision from database
                formatted_value = f"{float_value:.{precision}f}"
            else:
                # Default formatting if precision not found
                formatted_value = f"{float_value:.2f}"
            
            # Add units if requested
            if include_units:
                units = self.get_tag_units(tag_name)
                if units:
                    return f"{formatted_value} {units}"
                else:
                    return formatted_value
            else:
                return formatted_value
                
        except (ValueError, TypeError):
            # Not a numeric value, return as string
            return str(value)
    
    def get_latest_tag_value(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """Get the latest value for a specific tag.
        
        Args:
            tag_name: Name of the tag to retrieve
            
        Returns:
            Dictionary with 'value' and 'timestamp' or None if not found
        """
        conn = self._get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            # Get the latest value for the tag
            cursor.execute('''
                SELECT tv.Value, tv.DateTime, tl.name
                FROM TagValues tv
                JOIN TagList tl ON tv.TagName_id = tl.id
                WHERE tl.name = ?
                ORDER BY tv.DateTime DESC
                LIMIT 1
            ''', (tag_name,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'value': result[0],
                    'timestamp': result[1],
                    'tag_name': result[2]
                }
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get latest value for {tag_name}: {e}")
            return None
        finally:
            conn.close()
    
    def get_tag_values(self, tag_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get multiple values for a specific tag.
        
        Args:
            tag_name: Name of the tag to retrieve
            limit: Maximum number of values to return
            
        Returns:
            List of dictionaries with 'value' and 'timestamp'
        """
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT tv.Value, tv.DateTime, tl.name
                FROM TagValues tv
                JOIN TagList tl ON tv.TagName_id = tl.id
                WHERE tl.name = ?
                ORDER BY tv.DateTime DESC
                LIMIT ?
            ''', (tag_name, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'value': row[0],
                    'timestamp': row[1],
                    'tag_name': row[2]
                })
            
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get values for {tag_name}: {e}")
            return []
        finally:
            conn.close()
    
    def get_latest_measurements(self) -> Dict[str, Any]:
        """Get the latest measurements for all key parameters.
        
        Returns:
            Dictionary with latest measurement values
        """
        key_tags = ['CO_CONC', 'O2_CONC', 'AI_SAMPLE_TEMP', 'AI_PUMP_FLOW']
        measurements = {}
        
        for tag in key_tags:
            tag_data = self.get_latest_tag_value(tag)
            if tag_data:
                try:
                    # Convert value to float if possible
                    value = float(tag_data['value'])
                    measurements[tag.lower()] = value
                except (ValueError, TypeError):
                    measurements[tag.lower()] = tag_data['value']
        
        return measurements
    
    def get_measurement_history(self, hours: int = 24) -> Dict[str, List[Tuple[datetime, float]]]:
        """Get measurement history for the specified time period.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary mapping tag names to lists of (timestamp, value) tuples
        """
        conn = self._get_connection()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor()
            
            # Calculate the cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_str = cutoff_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # Get all measurements since cutoff time
            cursor.execute('''
                SELECT tv.Value, tv.DateTime, tl.name
                FROM TagValues tv
                JOIN TagList tl ON tv.TagName_id = tl.id
                WHERE tv.DateTime >= ?
                ORDER BY tl.name, tv.DateTime ASC
            ''', (cutoff_str,))
            
            # Group by tag name
            history = {}
            for row in cursor.fetchall():
                value, timestamp_str, tag_name = row
                
                try:
                    # Parse timestamp
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                    # Convert value to float
                    float_value = float(value)
                    
                    if tag_name not in history:
                        history[tag_name] = []
                    
                    history[tag_name].append((timestamp, float_value))
                    
                except (ValueError, TypeError) as e:
                    logger.debug(f"Failed to parse data for {tag_name}: {e}")
                    continue
            
            return history
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get measurement history: {e}")
            return {}
        finally:
            conn.close()
    
    def get_all_tag_names(self) -> List[str]:
        """Get all tag names from the database.
        
        Returns:
            List of all tag names
        """
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            cursor.execute('SELECT Name FROM TagList ORDER BY Name')
            
            tag_names = [row[0] for row in cursor.fetchall()]
            return tag_names
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get all tag names: {e}")
            return []
        finally:
            conn.close()
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database status information.
        
        Returns:
            Dictionary with database status information
        """
        conn = self._get_connection()
        if not conn:
            return {'status': 'disconnected', 'error': 'Failed to connect'}
        
        try:
            cursor = conn.cursor()
            
            # Get total record count
            cursor.execute('SELECT COUNT(*) FROM TagValues')
            total_records = cursor.fetchone()[0]
            
            # Get latest record timestamp
            cursor.execute('SELECT MAX(DateTime) FROM TagValues')
            latest_record = cursor.fetchone()[0]
            
            # Get tag count
            cursor.execute('SELECT COUNT(*) FROM TagList')
            total_tags = cursor.fetchone()[0]
            
            return {
                'status': 'connected',
                'total_records': total_records,
                'total_tags': total_tags,
                'latest_record': latest_record,
                'database_path': str(Path(self.db_path).absolute())
            }
            
        except sqlite3.Error as e:
            logger.error(f"Failed to get database status: {e}")
            return {'status': 'error', 'error': str(e)}
        finally:
            conn.close()
