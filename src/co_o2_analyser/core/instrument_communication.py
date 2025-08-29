"""
Instrument communication module for CO_O2_Analyser.

This module handles communication with the Teledyne N300M analyzer
via HTTP REST API, with simulation mode support.
"""

import requests
import logging
import random
import time
import math
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.config import Config

logger = logging.getLogger(__name__)


class SimulatedInstrumentCommunication:
    """Simulates instrument communication for testing and development."""
    
    def __init__(self, config: Config):
        """Initialize simulated instrument communication."""
        self.config = config
        self.start_time = time.time()
        
        # Real industrial measurement ranges based on actual data
        self.operational_modes = {
            'clean_air': {
                'co_concentration': (27.0, 28.0),      # Normal ambient air
                'o2_concentration': (20.8, 21.0),      # Normal oxygen levels
                'temperature': (20.0, 25.0),            # Room temperature
                'humidity': (40.0, 60.0),              # Normal humidity
                'pressure': (1010.0, 1020.0),          # Normal atmospheric pressure
                'status': 'OK'
            },
            'industrial_exhaust': {
                'co_concentration': (290.0, 350.0),    # High CO from oven fumes
                'o2_concentration': (7.8, 8.0),        # Depleted oxygen
                'temperature': (35.0, 45.0),            # Elevated temperature
                'humidity': (20.0, 40.0),              # Lower humidity
                'pressure': (1005.0, 1015.0),          # Slightly lower pressure
                'status': 'WARNING - High CO'
            },
            'extreme_fumes': {
                'co_concentration': (795.0, 905.0),    # Extreme CO - centered around 500 ppm
                'o2_concentration': (4.8, 5.2),        # Very low oxygen - centered around 5%
                'temperature': (50.0, 60.0),            # High temperature
                'humidity': (15.0, 25.0),              # Very low humidity
                'pressure': (1000.0, 1010.0),          # Lower pressure
                'status': 'CRITICAL - Extreme CO'
            }
        }
        
        # Start in clean air mode, switch every 30 seconds through 3 modes
        self.current_mode = 'clean_air'
        self.mode_switch_time = 30.0
        
        # Add realistic noise and drift based on real measurements
        self.noise_levels = {
            'co_concentration': (0.1, 6.5),    # ±0.1-0.5 ppm noise
            'o2_concentration': (0.01, 1.5),  # ±0.01-0.05% noise
            'temperature': (0.1, 0.3),         # ±0.1-0.3°C noise
            'humidity': (0.5, 1.5),            # ±0.5-1.5% noise
            'pressure': (0.1, 0.5)             # ±0.1-0.5 hPa noise
        }
        
        logger.info("Initialized simulated instrument communication with industrial data")
    
    def _get_current_mode(self):
        """Determine current operational mode based on time."""
        elapsed_time = time.time() - self.start_time
        mode_index = int(elapsed_time / self.mode_switch_time) % 3
        
        if mode_index == 0:
            return 'clean_air'
        elif mode_index == 1:
            return 'industrial_exhaust'
        else:
            return 'extreme_fumes'
    
    def _add_realistic_noise(self, base_value: float, parameter: str) -> float:
        """Add realistic noise based on actual measurement patterns."""
        if parameter in self.noise_levels:
            noise_range = self.noise_levels[parameter]
            noise = random.uniform(-noise_range[0], noise_range[0])
            return base_value + noise
        return base_value
    
    def test_connection(self) -> bool:
        """Simulate successful connection."""
        return True
    
    def get_tag_list(self) -> Dict[str, Any]:
        """Simulate tag list response."""
        return {
            "tags": [
                {"name": "CO_Concentration", "description": "Carbon Monoxide Concentration", "unit": "ppm"},
                {"name": "O2_Concentration", "description": "Oxygen Concentration", "unit": "%"},
                {"name": "Temperature", "description": "Ambient Temperature", "unit": "°C"},
                {"name": "Humidity", "description": "Relative Humidity", "unit": "%"},
                {"name": "Pressure", "description": "Atmospheric Pressure", "unit": "hPa"},
                {"name": "Status", "description": "Instrument Status", "unit": ""}
            ]
        }
    
    def get_tag_value(self, tag_name: str) -> Dict[str, Any]:
        """Simulate tag value response with realistic industrial data."""
        tag_mapping = {
            'CO_Concentration': 'co_concentration',
            'O2_Concentration': 'o2_concentration',
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'Pressure': 'pressure',
            'Status': 'status'
        }
        
        if tag_name in tag_mapping:
            field = tag_mapping[tag_name]
            current_mode = self._get_current_mode()
            mode_data = self.operational_modes[current_mode]
            
            if field == 'status':
                value = mode_data[field]
            else:
                # Get base value from current mode
                base_range = mode_data[field]
                base_value = random.uniform(base_range[0], base_range[1])
                
                # Add realistic noise
                value = self._add_realistic_noise(base_value, field)
                
                # Add slight drift over time (like real sensors)
                time_factor = (time.time() - self.start_time) / 3600  # hours
                drift = 0.1 * math.sin(time_factor * 2 * math.pi / 24)  # Daily cycle
                value += drift
                
                # Ensure values stay in reasonable ranges
                if field == 'co_concentration':
                    value = max(0, min(1000, value))  # 0-800 ppm (allow extreme_fumes to exceed 500)
                elif field == 'o2_concentration':
                    value = max(3, min(25, value))   # 3-25% (allow extreme_fumes to go below 5%)
                elif field == 'temperature':
                    value = max(-10, min(70, value))  # -10 to 70°C
                elif field == 'humidity':
                    value = max(0, min(100, value))   # 0-100%
                elif field == 'pressure':
                    value = max(800, min(1200, value))  # 800-1200 hPa
        else:
            value = "Unknown"
        
        return {"value": value, "timestamp": datetime.now().isoformat()}
    
    def set_tag_value(self, tag_name: str, value: Any) -> bool:
        """Simulate setting tag value."""
        logger.info(f"Simulated: Set tag {tag_name} to {value}")
        return True
    
    def get_current_values(self) -> Dict[str, Any]:
        """Get current simulated measurement values."""
        measurement_data = {}
        current_mode = self._get_current_mode()
        
        # Log mode changes
        if current_mode != self.current_mode:
            logger.info(f"Simulation mode changed to: {current_mode}")
            self.current_mode = current_mode
        
        for tag_name in ['CO_Concentration', 'O2_Concentration', 'Temperature', 'Humidity', 'Pressure', 'Status']:
            tag_value = self.get_tag_value(tag_name)
            if tag_value:
                field_name = tag_name.lower().replace('_', '')
                measurement_data[field_name] = tag_value.get('value')
        
        logger.debug(f"Retrieved simulated current values ({current_mode}): {measurement_data}")
        return measurement_data
    
    def get_logged_data(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict[str, Any]:
        """Simulate logged data response with realistic patterns."""
        # Generate historical data that shows mode transitions
        data_points = []
        current_time = datetime.now()
        
        for i in range(20):  # Last 20 data points
            timestamp = current_time.replace(second=current_time.second - i * 30)  # Every 30 seconds
            
            # Determine mode for this historical point
            historical_time = timestamp.timestamp()
            time_diff = historical_time - self.start_time
            historical_mode_index = int(time_diff / self.mode_switch_time) % 3
            if historical_mode_index == 0:
                historical_mode = 'clean_air'
            elif historical_mode_index == 1:
                historical_mode = 'industrial_exhaust'
            else:
                historical_mode = 'extreme_fumes'
            
            # Generate data for this historical point
            mode_data = self.operational_modes[historical_mode]
            
            point = {
                "timestamp": timestamp.isoformat(),
                "co_concentration": self._add_realistic_noise(
                    random.uniform(*mode_data['co_concentration']), 'co_concentration'
                ),
                "o2_concentration": self._add_realistic_noise(
                    random.uniform(*mode_data['o2_concentration']), 'o2_concentration'
                ),
                "temperature": self._add_realistic_noise(
                    random.uniform(*mode_data['temperature']), 'temperature'
                ),
                "humidity": self._add_realistic_noise(
                    random.uniform(*mode_data['humidity']), 'humidity'
                ),
                "pressure": self._add_realistic_noise(
                    random.uniform(*mode_data['pressure']), 'pressure'
                )
            }
            data_points.append(point)
        
        return {"data": data_points}


class InstrumentCommunication:
    """Handles communication with the Teledyne N300M analyzer."""
    
    def __init__(self, config: Config):
        """Initialize instrument communication.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Check if simulation mode is enabled
        if config.get('instrument.simulation_mode', False):
            self.simulator = SimulatedInstrumentCommunication(config)
            self.is_simulation = True
            logger.info("Running in simulation mode")
        else:
            self.base_url = f"http://{config.get('instrument.ip_address')}:{config.get('instrument.port')}"
            self.timeout = config.get('instrument.timeout', 30)
            self.retry_attempts = config.get('instrument.retry_attempts', 3)
            self.is_simulation = False
            logger.info(f"Initialized communication with instrument at {self.base_url}")
    
    def test_connection(self) -> bool:
        """Test connection to the instrument."""
        if self.is_simulation:
            return self.simulator.test_connection()
        
        try:
            response = requests.get(f"{self.base_url}/api/taglist", timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_tag_list(self) -> Optional[Dict[str, Any]]:
        """Get list of available tags from the instrument."""
        if self.is_simulation:
            return self.simulator.get_tag_list()
        
        try:
            response = requests.get(f"{self.base_url}/api/taglist", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get tag list: {e}")
            return None
    
    def get_tag_value(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """Get value of a specific tag."""
        if self.is_simulation:
            return self.simulator.get_tag_value(tag_name)
        
        try:
            response = requests.get(f"{self.base_url}/api/tag/{tag_name}/value", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get tag value for {tag_name}: {e}")
            return None
    
    def set_tag_value(self, tag_name: str, value: Any) -> bool:
        """Set value of a specific tag."""
        if self.is_simulation:
            return self.simulator.set_tag_value(tag_name, value)
        
        try:
            data = {"value": value}
            response = requests.put(
                f"{self.base_url}/api/tag/{tag_name}/value",
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            logger.info(f"Set tag {tag_name} to {value}")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to set tag value for {tag_name}: {e}")
            return False
    
    def get_current_values(self) -> Optional[Dict[str, Any]]:
        """Get current measurement values from the instrument."""
        if self.is_simulation:
            return self.simulator.get_current_values()
        
        try:
            # Get tag list first
            tag_list = self.get_tag_list()
            if not tag_list:
                return None
            
            # Get values for key measurement tags
            measurement_data = {}
            key_tags = ['CO_Concentration', 'O2_Concentration', 'Temperature', 'Humidity', 'Pressure', 'Status']
            
            for tag in key_tags:
                tag_value = self.get_tag_value(tag)
                if tag_value:
                    measurement_data[tag.lower().replace('_', '')] = tag_value.get('value')
            
            logger.debug(f"Retrieved current values: {measurement_data}")
            return measurement_data
            
        except Exception as e:
            logger.error(f"Failed to get current values: {e}")
            return None
    
    def get_logged_data(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get logged data from the instrument."""
        if self.is_simulation:
            return self.simulator.get_logged_data(start_time, end_time)
        
        try:
            url = f"{self.base_url}/api/dataloglist"
            params = {}
            
            if start_time:
                params['start'] = start_time
            if end_time:
                params['end'] = end_time
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Failed to get logged data: {e}")
            return None
