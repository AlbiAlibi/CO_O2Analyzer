# CO_O2_Analyser Usage Guide

This guide explains how to use the CO_O2_Analyser Python module and its various components.

## 🚀 Quick Start

### Basic Usage

1. **Install the module:**
   ```bash
   pip install -e .
   ```

2. **Run the GUI application:**
   ```bash
   python -m co_o2_analyser
   # or
   python main.py
   ```

3. **Start data collection:**
   ```bash
   python start_data_collector.py
   ```

## 📚 Module Usage

### Import the Module

```python
import co_o2_analyser
from co_o2_analyser import COO2Analyzer, MainWindow
```

### Basic Analyzer Usage

```python
from co_o2_analyser import COO2Analyzer
from co_o2_analyser.utils.config import Config

# Load configuration
config = Config()

# Create analyzer instance
analyzer = COO2Analyzer(config)

# Get current measurement
measurement = analyzer.get_current_measurement()
print(f"CO: {measurement.co_concentration} ppm")
print(f"O2: {measurement.o2_concentration}%")

# Start monitoring
analyzer.start_monitoring()

# Stop monitoring
analyzer.stop_monitoring()

# Close analyzer
analyzer.close()
```

### GUI Application Usage

```python
from co_o2_analyser.gui.main_window import main

# Run the GUI application
main()
```

### Data Collection Service

```python
from co_o2_analyser.core.CO_O2Analyser import InstrumentDataCollector
from co_o2_analyser.utils.config import Config

# Create data collector
config = Config()
collector = InstrumentDataCollector(config)

# Start data collection
collector.start_collection()

# Stop data collection
collector.stop_collection()
```

## 🔧 Configuration

### Programmatic Configuration

```python
from co_o2_analyser.utils.config import Config

# Create config with custom settings
config = Config()

# Set instrument IP
config.set('instrument.ip_address', '192.168.1.100')

# Set data collection intervals
config.set('data_collection.intervals.concentration_interval', 2.0)

# Save configuration
config.save_config()
```

### Configuration File

The application uses a JSON configuration file:

```json
{
  "instrument": {
    "ip_address": "192.168.1.1",
    "port": 8180,
    "timeout": 30,
    "retry_attempts": 3,
    "simulation_mode": false,
    "tags": {
      "concentration_tags": ["CO_CONC", "O2_CONC"],
      "warning_tags": ["BOX_TEMP_WARN", "BENCH_TEMP_WARN"],
      "flow_tags": ["AI_PUMP_FLOW", "AI_SAMPLE_TEMP"]
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
  "data_collection": {
    "intervals": {
      "all_values_interval": 60,
      "concentration_interval": 1.5,
      "status_check_interval": 10
    }
  }
}
```

## 📊 Data Access

### Database Operations

```python
from co_o2_analyser.utils.database import DatabaseManager

# Create database manager
db_manager = DatabaseManager("data.sqlite")

# Get recent measurements
recent_data = db_manager.get_recent_data(seconds=300)  # Last 5 minutes

# Get measurements by time range
from datetime import datetime, timedelta
start_time = datetime.now() - timedelta(hours=1)
end_time = datetime.now()
measurements = db_manager.get_measurements_by_time_range(start_time, end_time)

# Export data to CSV
db_manager.export_to_csv("export.csv", start_time, end_time)
```

### Measurement Sessions

```python
# Start a measurement session
session_path = analyzer.start_measurement_session(duration_minutes=10)

# Add measurements to session
analyzer.add_measurement_to_session(
    co_concentration=5.2,
    o2_concentration=21.5,
    sample_temp=25.0,
    sample_flow=1.0
)

# Stop measurement session
analyzer.stop_measurement_session()
```

## 🎛️ Instrument Management

### Time Synchronization

```python
from co_o2_analyser.gui.instrument_management_dialog import InstrumentManagementDialog

# Create instrument management dialog
dialog = InstrumentManagementDialog()

# Synchronize instrument time
dialog._sync_instrument_time()
```

### Instrument Control

```python
# Restart instrument
dialog._restart_instrument()

# Shutdown instrument
dialog._shutdown_instrument()
```

## 📈 Data Visualization

### Custom Plotting

```python
from co_o2_analyser.gui.plot_widget import PlotWidget
import matplotlib.pyplot as plt

# Create plot widget
plot_widget = PlotWidget()

# Add measurement data
measurement = {
    'timestamp': datetime.now(),
    'co_concentration': 5.2,
    'o2_concentration': 21.5
}
plot_widget.add_measurement(measurement)

# Get matplotlib figure for custom plotting
fig = plot_widget.get_figure()
plt.show()
```

## 🔍 Logging and Debugging

### Enable Debug Logging

```python
import logging

# Set logging level
logging.basicConfig(level=logging.DEBUG)

# Or configure specific logger
logger = logging.getLogger('co_o2_analyser')
logger.setLevel(logging.DEBUG)
```

### Custom Logging

```python
from co_o2_analyser.utils.logger import setup_logger

# Setup custom logger
logger = setup_logger('my_module', 'my_module.log')

# Use logger
logger.info("Application started")
logger.error("An error occurred")
```

## 🧪 Testing

### Unit Testing

```python
import pytest
from co_o2_analyser.core.analyzer import COO2Analyzer
from co_o2_analyser.utils.config import Config

def test_analyzer_initialization():
    config = Config()
    analyzer = COO2Analyzer(config)
    assert analyzer is not None
    analyzer.close()

def test_config_loading():
    config = Config()
    ip_address = config.get('instrument.ip_address')
    assert ip_address == '192.168.1.1'
```

### Integration Testing

```python
def test_instrument_communication():
    from co_o2_analyser.core.instrument_communication import InstrumentCommunication
    
    config = Config()
    instrument = InstrumentCommunication(config)
    
    # Test connection
    is_connected = instrument.test_connection()
    assert is_connected == True
```

## 📦 Package Distribution

### Install from Source

```bash
# Clone repository
git clone https://github.com/yourusername/CO_O2Analyser.git
cd CO_O2Analyser

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev,test,docs]"
```

### Create Distribution Package

```bash
# Build source and wheel distributions
python -m build

# Install from wheel
pip install dist/co_o2_analyser-1.0.0-py3-none-any.whl
```

### Create Standalone Executable

```bash
# Using PyInstaller
pyinstaller --onefile --windowed main.py

# Using cx_Freeze
python setup_cx_freeze.py build
```

## 🔧 Advanced Configuration

### Custom Tag Configuration

```python
# Add custom tags to configuration
config.set('instrument.tags.custom_tags', ['CUSTOM_TAG_1', 'CUSTOM_TAG_2'])

# Update tag groups
config.set('instrument.tags.concentration_tags', ['CO_CONC', 'O2_CONC', 'CUSTOM_CONC'])
```

### Database Customization

```python
# Custom database path
config.set('database.path', '/custom/path/data.sqlite')

# Custom backup interval (in seconds)
config.set('database.backup_interval', 1800)  # 30 minutes
```

### GUI Customization

```python
# Custom window size
config.set('gui.window_width', 1920)
config.set('gui.window_height', 1080)

# Custom theme (if implemented)
config.set('gui.theme', 'dark')
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors:**
   ```python
   # Ensure the module is installed
   pip install -e .
   
   # Check Python path
   import sys
   print(sys.path)
   ```

2. **Configuration Issues:**
   ```python
   # Check configuration file location
   from co_o2_analyser.utils.config import Config
   config = Config()
   print(f"Config path: {config.config_path}")
   ```

3. **Database Issues:**
   ```python
   # Check database file
   import sqlite3
   conn = sqlite3.connect('data.sqlite')
   cursor = conn.cursor()
   cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
   print(cursor.fetchall())
   conn.close()
   ```

### Debug Mode

```python
# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
python -m co_o2_analyser --debug
```

## 📞 Support

For additional help:

- **Documentation**: Check the [README.md](README.md) file
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/CO_O2Analyser/issues)
- **Logs**: Check `co_o2_analyser.log` for detailed error information
