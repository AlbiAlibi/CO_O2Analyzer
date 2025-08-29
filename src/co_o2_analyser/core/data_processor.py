"""
Data processing module for CO_O2_Analyser.

This module handles data processing, validation, and conversion
of raw instrument data.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes and validates raw instrument data."""
    
    def __init__(self):
        """Initialize data processor."""
        self.logger = logging.getLogger(__name__)
    
    def process_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data from the instrument.
        
        Args:
            raw_data: Raw data from instrument
            
        Returns:
            Processed and validated data
        """
        try:
            processed_data = {}
            
            # Process CO concentration
            if 'coconcentration' in raw_data:
                processed_data['co_concentration'] = self._validate_numeric(
                    raw_data['coconcentration'], 'CO concentration'
                )
            
            # Process O2 concentration
            if 'o2concentration' in raw_data:
                processed_data['o2_concentration'] = self._validate_numeric(
                    raw_data['o2concentration'], 'O2 concentration'
                )
            
            # Process temperature
            if 'temperature' in raw_data:
                processed_data['temperature'] = self._validate_numeric(
                    raw_data['temperature'], 'temperature'
                )
            
            # Process humidity
            if 'humidity' in raw_data:
                processed_data['humidity'] = self._validate_numeric(
                    raw_data['humidity'], 'humidity'
                )
            
            # Process pressure
            if 'pressure' in raw_data:
                processed_data['pressure'] = self._validate_numeric(
                    raw_data['pressure'], 'pressure'
                )
            
            # Process status
            if 'status' in raw_data:
                processed_data['status'] = self._validate_status(raw_data['status'])
            
            # Add timestamp
            processed_data['timestamp'] = datetime.now().isoformat()
            
            self.logger.debug(f"Processed raw data: {processed_data}")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Failed to process raw data: {e}")
            return {}
    
    def _validate_numeric(self, value: Any, field_name: str) -> Optional[float]:
        """Validate and convert numeric values.
        
        Args:
            value: Value to validate
            field_name: Name of the field for logging
            
        Returns:
            Validated numeric value or None if invalid
        """
        try:
            if value is None:
                return None
            
            # Convert to float
            numeric_value = float(value)
            
            # Check for reasonable ranges
            if field_name == 'CO concentration':
                if not (0 <= numeric_value <= 1000):  # ppm range
                    self.logger.warning(f"CO concentration out of range: {numeric_value}")
            elif field_name == 'O2 concentration':
                if not (0 <= numeric_value <= 25):  # % range
                    self.logger.warning(f"O2 concentration out of range: {numeric_value}")
            elif field_name == 'temperature':
                if not (-50 <= numeric_value <= 100):  # Celsius range
                    self.logger.warning(f"Temperature out of range: {numeric_value}")
            elif field_name == 'humidity':
                if not (0 <= numeric_value <= 100):  # % range
                    self.logger.warning(f"Humidity out of range: {numeric_value}")
            elif field_name == 'pressure':
                if not (800 <= numeric_value <= 1200):  # hPa range
                    self.logger.warning(f"Pressure out of range: {numeric_value}")
            
            return numeric_value
            
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Invalid {field_name} value: {value} ({e})")
            return None
    
    def _validate_status(self, status: Any) -> str:
        """Validate instrument status.
        
        Args:
            status: Status value to validate
            
        Returns:
            Validated status string
        """
        if status is None:
            return "Unknown"
        
        status_str = str(status).strip()
        
        # Normalize common status values
        status_lower = status_str.lower()
        if 'ok' in status_lower or 'normal' in status_lower:
            return "OK"
        elif 'error' in status_lower or 'fault' in status_lower:
            return "Error"
        elif 'warning' in status_lower:
            return "Warning"
        elif 'calibrating' in status_lower or 'cal' in status_lower:
            return "Calibrating"
        elif 'warming' in status_lower or 'warm' in status_lower:
            return "Warming"
        else:
            return status_str
    
    def calculate_statistics(self, measurements: list) -> Dict[str, Any]:
        """Calculate statistics from a list of measurements.
        
        Args:
            measurements: List of measurement objects
            
        Returns:
            Dictionary containing calculated statistics
        """
        if not measurements:
            return {}
        
        try:
            stats = {}
            
            # Extract numeric values
            co_values = [m.co_concentration for m in measurements if m.co_concentration is not None]
            o2_values = [m.o2_concentration for m in measurements if m.o2_concentration is not None]
            temp_values = [m.temperature for m in measurements if m.temperature is not None]
            humidity_values = [m.humidity for m in measurements if m.humidity is not None]
            pressure_values = [m.pressure for m in measurements if m.pressure is not None]
            
            # Calculate statistics for each parameter
            if co_values:
                stats['co_concentration'] = self._calculate_numeric_stats(co_values)
            if o2_values:
                stats['o2_concentration'] = self._calculate_numeric_stats(o2_values)
            if temp_values:
                stats['temperature'] = self._calculate_numeric_stats(temp_values)
            if humidity_values:
                stats['humidity'] = self._calculate_numeric_stats(humidity_values)
            if pressure_values:
                stats['pressure'] = self._calculate_numeric_stats(pressure_values)
            
            # Add count and time range
            stats['count'] = len(measurements)
            if measurements:
                stats['time_range'] = {
                    'start': measurements[-1].timestamp.isoformat(),
                    'end': measurements[0].timestamp.isoformat()
                }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {e}")
            return {}
    
    def _calculate_numeric_stats(self, values: list) -> Dict[str, float]:
        """Calculate basic statistics for numeric values.
        
        Args:
            values: List of numeric values
            
        Returns:
            Dictionary containing min, max, mean, std
        """
        if not values:
            return {}
        
        try:
            import statistics
            
            return {
                'min': min(values),
                'max': max(values),
                'mean': statistics.mean(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0.0
            }
        except Exception as e:
            self.logger.error(f"Failed to calculate numeric stats: {e}")
            return {}
