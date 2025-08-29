"""
Tests for configuration management.

This module tests the Config class functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path

from co_o2_analyser.utils.config import Config


class TestConfig:
    """Test cases for Config class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        # Test default values
        assert config.get('instrument.ip_address') == '192.168.1.100'
        assert config.get('instrument.port') == 8180
        assert config.get('database.path') == 'data_store.sqlite'
        assert config.get('gui.window_width') == 1200
    
    def test_custom_config_file(self):
        """Test loading from custom config file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"instrument": {"ip_address": "10.0.0.1"}}')
            config_file = f.name
        
        try:
            config = Config(config_file)
            assert config.get('instrument.ip_address') == '10.0.0.1'
        finally:
            os.unlink(config_file)
    
    def test_get_with_default(self):
        """Test getting values with default fallback."""
        config = Config()
        
        # Test non-existent key with default
        assert config.get('nonexistent.key', 'default_value') == 'default_value'
        
        # Test existing key
        assert config.get('instrument.port', 9999) == 8180
    
    def test_set_value(self):
        """Test setting configuration values."""
        config = Config()
        
        # Set new value
        config.set('custom.setting', 'test_value')
        assert config.get('custom.setting') == 'test_value'
        
        # Set nested value
        config.set('nested.deep.value', 42)
        assert config.get('nested.deep.value') == 42
    
    def test_save_config(self):
        """Test saving configuration to file."""
        config = Config()
        
        # Modify a value
        config.set('test.value', 'modified')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config.config_file = f.name
            config.save_config()
        
        try:
            # Load from saved file
            new_config = Config(f.name)
            assert new_config.get('test.value') == 'modified'
        finally:
            os.unlink(f.name)
    
    def test_merge_configs(self):
        """Test merging user config with defaults."""
        config = Config()
        
        # Test that user config overrides defaults
        user_config = {
            'instrument': {
                'ip_address': '192.168.0.100',
                'custom_setting': 'user_value'
            }
        }
        
        config._merge_configs(config.config, user_config)
        
        assert config.get('instrument.ip_address') == '192.168.0.100'
        assert config.get('instrument.custom_setting') == 'user_value'
        # Default values should still exist
        assert config.get('instrument.port') == 8180
