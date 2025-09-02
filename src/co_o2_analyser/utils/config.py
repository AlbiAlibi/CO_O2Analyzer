"""
Configuration management for CO_O2_Analyser.

This module handles application configuration including instrument settings,
database configuration, and user preferences.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the application."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            config_file: Path to configuration file. If None, uses default.
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        config_dir = Path.home() / ".co_o2_analyser"
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            "instrument": {
                "ip_address": "192.168.1.1",
                "port": 8180,
                "timeout": 30,
                "retry_attempts": 3,
                "simulation_mode": False,  # Enable simulation mode by default
                "data_simulation": False,  # Enable data simulation by default
                "tags": {
                    "instrument_status": [
                        "INSTRUMENT_TIME",
                        "NETWORK_IP_ADDRESS",
                        "OS_VERSION"
                    ],
                    "concentration_tags": [
                        "CO_CONC",
                        "O2_CONC"
                    ],
                    "warning_tags": [
                        "BOX_TEMP_WARN",
                        "BENCH_TEMP_WARN",
                        "WHEEL_TEMP_WARN",
                        "LOW_MEMORY_WARNING",
                        "SYS_INVALID_CONC_WARNING",
                        "SF_O2_SENSOR_WARN_MALFUNCTION"
                    ],
                    "flow_tags": [
                        "AI_PUMP_FLOW",
                        "PUMP_CONTROL_MODULE_STATE",
                        "AI_SAMPLE_TEMP",
                        "AI_SAMPLE_PRESSURE",
                        "AI_ATMOSPHERIC_PRESSURE"
                    ],
                    "temperature": [
                        "AI_SAMPLE_TEMP",
                        "AI_DETECTOR_TEMP",
                        "AI_BOX_TEMP",
                        "AI_BENCH_TEMP",
                        "AI_O2_HEATER_TEMP"
                    ]
                }
            },
            "database": {
                "path": "data.sqlite",
                "backup_interval": 3600
            },
            "gui": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "light"
            },
            "logging": {
                "level": "INFO",
                "file": "co_o2_analyser.log",
                "max_size": 10485760  # 10MB
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults (user config takes precedence)
                    merged_config = self._merge_configs(default_config, user_config)
                    # Use the merged config and DON'T save it back (preserve user changes)
                    self.config = merged_config
                    return merged_config
            except (json.JSONDecodeError, IOError):
                # If file exists but is corrupted, create new one with defaults
                logger.warning(f"Config file {self.config_file} is corrupted, creating new one with defaults")
                self.config = default_config
                self.save_config()
                return default_config
        else:
            # File doesn't exist, create it with defaults
            logger.info(f"Config file {self.config_file} not found, creating with defaults")
            self.config = default_config
            self.save_config()
            return default_config
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge user configuration with defaults."""
        import copy
        # Create a deep copy of default to avoid modifying the original
        merged = copy.deepcopy(default)
        
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def save_config(self):
        """Save current configuration to file."""
        config_dir = Path(self.config_file).parent
        config_dir.mkdir(exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
