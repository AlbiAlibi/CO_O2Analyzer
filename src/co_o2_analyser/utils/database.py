"""
Database management for CO_O2_Analyser.

This module handles database operations including connection management,
data storage, and retrieval for measurement data.
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for the application."""
    
    def __init__(self, db_path: str = "data_store.sqlite"):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            logger.info(f"Database initialized: {self.db_path}")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.connection.cursor()
        
        # Measurements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                co_concentration REAL,
                o2_concentration REAL,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                instrument_status TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                unit TEXT,
                data_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Log entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                source TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
        logger.info("Database tables created successfully")
    
    def insert_measurement(self, data: Dict[str, Any]) -> int:
        """Insert a new measurement record.
        
        Args:
            data: Dictionary containing measurement data
            
        Returns:
            ID of the inserted record
        """
        cursor = self.connection.cursor()
        
        # Ensure timestamp is present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().isoformat()
        
        # Prepare data for insertion
        fields = ['timestamp', 'co_concentration', 'o2_concentration', 
                 'temperature', 'humidity', 'pressure', 'instrument_status']
        
        values = [data.get(field) for field in fields]
        placeholders = ', '.join(['?' for _ in fields])
        field_names = ', '.join(fields)
        
        query = f"INSERT INTO measurements ({field_names}) VALUES ({placeholders})"
        
        try:
            cursor.execute(query, values)
            self.connection.commit()
            measurement_id = cursor.lastrowid
            logger.debug(f"Measurement inserted with ID: {measurement_id}")
            return measurement_id
            
        except sqlite3.Error as e:
            logger.error(f"Failed to insert measurement: {e}")
            self.connection.rollback()
            raise
    
    def get_measurements(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve measurements from database.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of measurement dictionaries
        """
        cursor = self.connection.cursor()
        
        query = """
            SELECT * FROM measurements 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """
        
        try:
            cursor.execute(query, (limit, offset))
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            measurements = []
            for row in rows:
                measurements.append(dict(row))
            
            return measurements
            
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve measurements: {e}")
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
