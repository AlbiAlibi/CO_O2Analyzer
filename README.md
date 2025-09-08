# CO_O2_Analyser

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**CO_O2_Analyser** is a professional software tool designed to communicate with the **Teledyne N300M** carbon monoxide analyzer via HTTP protocol, retrieve air quality data, and store it in a database. The software provides a graphical interface for real-time monitoring of **CO (Carbon Monoxide) and O₂ (Oxygen)** concentrations over time.

## 🚀 Features

- **Real-time Data Monitoring**: Displays CO and O₂ levels over time with live updates
- **Modern Graphical User Interface**: Built with PyQt6 for a professional look and feel
- **Automated Data Harvesting**: Retrieves data from the Teledyne N300M using RESTful API
- **Database Integration**: SQLite database for historical measurement storage
- **Data Export**: Export measurements to CSV, JSON, and other formats
- **Settings Management**: Comprehensive settings dialog for configuration management
- **Instrument Management**: Time synchronization, shutdown, and restart functionality
- **Logging & Monitoring**: Comprehensive logging and error handling
- **Cross-platform**: Works on Windows, macOS, and Linux

## 📋 TO-DO List

### High Priority Improvements

1. **✅ Start Monitoring Button Enhancement** *(COMPLETED)*
   - ✅ Modified "Start Monitoring" button to launch `start_data_collector.py` as a new process
   - ✅ Implemented proper process management and cleanup
   - ✅ Added connection status monitoring from data collector to GUI
   - ✅ GUI displays "Connected" (green) or "Disconnected" (red) based on data flow to database
   - ✅ Connection status checks recent data in TagValues table (within 5 seconds) every 5 seconds

2. **✅ Data Refresh Functionality** *(COMPLETED)*
   - ✅ Implemented comprehensive data refresh when "Refresh" button is clicked
   - ✅ Uses refresh_signal.txt file to send signals to data collector process
   - ✅ Data collector processes refresh signal and executes collect_all_data()
   - ✅ Updates all data displays, graphs, and statistics in GUI

3. **✅ Statistics Block Update Frequency** *(COMPLETED)*
   - ✅ Statistics update frequency configured via config.json (60 seconds)
   - ✅ Both 'warnings flags' and 'Statistics' sections update with data collection
   - ✅ Performance optimized with proper intervals (60s all data, 1.5s concentration, 10s status)

4. **✅ CSV Export Fix** *(COMPLETED)*
   - ✅ Fixed CSV export functionality with proper field handling
   - ✅ Implemented per-measurement session export with datetime stamps
   - ✅ Added comprehensive data formatting and file generation
   - ✅ Created organized results folder structure

5. **✅ Data Collection Time Configuration** *(COMPLETED)*
   - ✅ Implemented dialog box for "start data collection" time configuration
   - ✅ Default value: 10 minutes (configurable)
   - ✅ User can modify collection duration through measurement session dialog

6. **✅ Settings Management System** *(COMPLETED)*
   - ✅ Comprehensive settings dialog with tabbed interface
   - ✅ Instrument configuration (IP, port, timeout, retry attempts)
   - ✅ Database settings (path, backup interval)
   - ✅ GUI settings (window size, theme)
   - ✅ Data collection intervals configuration
   - ✅ Logging configuration (level, file, max size)
   - ✅ Settings validation and testing functionality
   - ✅ Automatic config file creation and management

7. **✅ Instrument Management System** *(COMPLETED)*
   - ✅ Time synchronization with computer time
   - ✅ Instrument shutdown and restart functionality
   - ✅ Data collector process management
   - ✅ Real-time operation logging and status display
   - ✅ Safety confirmations for critical operations
   - ✅ Integration with main application menu

8. **✅ Active Collection Visualization** *(COMPLETED)*
   - ✅ Display blue line on graph when "Start Data Collection" button is active
   - ✅ Line persists across all "Time Range" views
   - ✅ Visual indicator for active data collection periods

9. **Dynamic Fume Limit Line**
   - Implement dynamic Fume Limit line on CO graph
   - Convert limit from mg/m³ to PPM CO units
   - Real-time recalculation and display

10. **CO Auto Zero Module** *(IN DEVELOPMENT)*
    - CO zero point correction functionality using CO_ZERO_CONC_1 tag
    - Dynamic zero calibration enable/disable using SV_DYNAMIC_ZERO_ENABLE tag
    - Test sequence with values -3, 0, 3, 4 and 5-second delays
    - **Status**: Currently disabled and in development

### Technical Considerations

- **Process Management**: Ensure proper handling of background data collection processes
- **Memory Management**: Optimize data handling for long-running collection sessions
- **Error Handling**: Robust error handling for data collection interruptions
- **Performance**: Optimize update frequencies and data processing
- **User Experience**: Smooth transitions and clear visual feedback

## 📋 System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.11 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free disk space
- **Network**: Ethernet connection to Teledyne N300M analyzer

## 🛠️ Installation

### Prerequisites

1. **Python 3.11+**: Download and install from [python.org](https://www.python.org/downloads/)
2. **Git**: Download and install from [git-scm.com](https://git-scm.com/)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/CO_O2Analyser.git
   cd CO_O2Analyser
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install in development mode** (optional):
   ```bash
   pip install -e .
   ```

## 🚀 Quick Start

### Running the GUI Application

```bash
python main.py
```

### Running from Command Line

```bash
# Basic usage example
python examples/basic_usage.py

# Settings dialog demonstration
python examples/settings_demo.py

# Or install and run as module
pip install -e .
co-o2-analyser
```

### Installing as a Python Module

1. **Install from source:**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/CO_O2Analyser.git
   cd CO_O2Analyser
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install the module
   pip install -e .
   ```

2. **Install dependencies only:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the installation:**
   ```bash
   python test_module.py
   ```

4. **Run the application:**
   ```bash
   # GUI application
   python -m co_o2_analyser
   
   # Or use the entry point
   co-o2-analyser
   
   # Data collector service
   python start_data_collector.py
   ```

### Creating Standalone Executable

```bash
# Using the build script
python build.py exe

# Or manually with PyInstaller
pip install pyinstaller
pyinstaller --onefile --windowed main.py

# Or with cx_Freeze
pip install cx_Freeze
python setup_cx_freeze.py build
```

### Configuration

1. **Edit configuration**: The application will create a default configuration file
2. **Set instrument IP**: Update `instrument.ip_address` in the config
3. **Verify port**: Default port is 8180 (Teledyne N300M standard)

## 📁 Project Structure

```
CO_O2Analyser/
├── src/                          # Source code
│   └── co_o2_analyser/          # Main package
│       ├── core/                 # Core functionality
│       │   ├── analyzer.py       # Main analyzer class (system coordinator)
│       │   ├── CO_O2Analyser.py  # Data collection service (background process)
│       │   ├── data_harvester.py # SQLite data harvesting from local database
│       │   ├── data_processor.py # Data processing and validation
│       │   └── instrument_communication.py # Instrument communication & simulation
│       ├── data/                 # Data models
│       │   └── models.py         # Data classes and structures
│       ├── gui/                  # Graphical interface
│       │   ├── main_window.py    # Main window (GUI coordinator)
│       │   ├── plot_widget.py    # Real-time plotting widget
│       │   ├── status_widget.py  # Status display with color-coded values
│       │   ├── settings_dialog.py # Settings management dialog
│       │   └── instrument_management_dialog.py # Instrument control dialog
│       └── utils/                # Utilities
│           ├── config.py         # Configuration management
│           ├── CSVharvester.py   # CSV export utilities
│           ├── database.py       # Database operations & measurement sessions
│           ├── instr_simulator.py # Instrument simulation for testing
│           └── logger.py         # Logging setup
├── tests/                        # Test suite
├── docs/                         # Documentation
├── examples/                     # Usage examples
│   ├── basic_usage.py           # Basic usage example
│   └── settings_demo.py         # Settings dialog demonstration
├── notatki/                      # Development notes and documentation
├── logs/                         # Application logs
├── measurements/                 # Measurement session databases
│   └── measurement{DDmmYY}.sqlite # Session-specific databases
├── main.py                       # Main GUI entry point
├── start_data_collector.py       # Data collection service entry point
├── data.sqlite                   # Main SQLite database (continuous logging)
├── analyser_status.txt           # Data collection status file
├── pyproject.toml               # Project configuration
├── requirements.txt              # Runtime dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package setup script
└── README.md                     # This file
```

## 🏗️ Software Architecture

### Core Components

#### `analyzer.py` - System Coordinator
The **`COO2Analyzer`** class in `analyzer.py` serves as the **central coordinator** of your CO_O2_Analyser software. It orchestrates all major operations:

**Key Responsibilities:**
- **System Orchestration**: Coordinates between instrument communication, data processing, and database storage
- **Monitoring Management**: Controls the start/stop of continuous monitoring of the Teledyne N300M analyzer
- **Data Collection**: Retrieves current measurements from the instrument and processes them through the data processor
- **Database Operations**: Stores processed measurements in the SQLite database and retrieves historical data
- **Measurement Sessions**: Manages session-specific databases with configurable duration and fume limit calculations
- **Data Export**: Provides CSV and JSON export functionality with advanced fume limit calculations
- **Business Logic**: Implements the core application logic for measurement management

**Architecture Role:**
- Acts as the **main API layer** between the GUI and the underlying data collection infrastructure
- Provides a **clean interface** for the main window to interact with the system
- Handles **error management** and **logging** for all operations
- Manages the **lifecycle** of measurement collection and storage

#### Data Collection Architecture
Your software uses a **two-process architecture**:

1. **GUI Process** (`main.py`): 
   - Runs the PyQt6 graphical interface
   - Uses `analyzer.py` to interact with the system
   - Displays real-time data and controls

2. **Data Collection Process** (`start_data_collector.py` → `CO_O2Analyser.py`):
   - Runs as a separate background process [[memory:7897981]]
   - Continuously collects data from the Teledyne N300M analyzer
   - Stores data in the local SQLite database (`data.sqlite`)
   - Updates status in `analyser_status.txt`

#### Data Flow
```
Teledyne N300M → CO_O2Analyser.py → data.sqlite → data_harvester.py → analyzer.py → GUI
```

#### Measurement Sessions
The system supports **session-based measurements** with the following features:

- **Session-Specific Databases**: Each measurement session creates a separate database file (`measurement{DDmmYY}.sqlite`)
- **Configurable Duration**: Default 10 minutes, user-configurable
- **Fume Limit Calculations**: Automatic calculation of fume limits and percentage to limit for each measurement
- **Session Management**: Start/stop sessions with proper timestamp recording
- **Data Isolation**: Session data is separate from continuous logging data
- **Session History**: Track all measurement sessions with metadata (start time, end time, duration, measurement count)

#### Data Export System
The application provides comprehensive data export functionality with the following features:

**Export Button Functionality:**
- **One-Click Export**: Click the "Export" button to export all measurement sessions
- **Per-Session Files**: Each measurement session is exported to a separate CSV file
- **Organized Storage**: All exports are saved in the `results/` folder
- **Timestamp Naming**: Files are named with session start time (`measurement_YYYYMMDD_HHMMSS.csv`)

**Export File Structure:**
```
results/
├── measurement_20250903_102603.csv  # Session from 03/09/25 at 10:26:03
├── measurement_20250904_161055.csv  # Session from 04/09/25 at 16:10:55
└── measurement_20250905_143000.csv  # Session from 05/09/25 at 14:30:00
```

**CSV File Contents:**
Each exported CSV file includes:
- **Session Metadata Header**: Comments with session start/end times, duration, and measurement count
- **Complete Measurement Data**: All fields from the measurement database
- **Fume Limit Calculations**: Automatic fume limit and percentage to limit calculations
- **Air Quality Status**: Fresh Air/Industrial Exhaust/Invalid O₂ classifications
- **Comprehensive Fields**: timestamp, co_concentration, o2_concentration, sample_temp, sample_flow, fume_limit_mg_m3, percentage_to_limit, air_quality_status, instrument_status, error_code, warning_flags

**Export Process:**
1. **Session Discovery**: Automatically finds all measurement sessions in the `measurements/` folder
2. **Data Retrieval**: Extracts measurement data from each session database
3. **Metadata Extraction**: Retrieves session start/end times and measurement counts
4. **File Generation**: Creates timestamped CSV files with proper formatting
5. **Error Handling**: Continues exporting other sessions if one fails
6. **User Feedback**: Shows success message with list of exported files

**Technical Implementation:**
- **Field Compatibility**: Handles all measurement model fields including optional ones
- **Data Filtering**: Removes None values and converts lists to strings for CSV compatibility
- **Error Recovery**: Robust error handling ensures partial failures don't stop the entire export
- **Memory Efficient**: Processes sessions one at a time to minimize memory usage

## 🔧 Configuration

### Configuration File

The application uses a JSON configuration file to manage all settings. The configuration system works with a **default configuration** in the code and a **user configuration file** that overrides the defaults.

#### Configuration File Location

**Default Path**: `~/.co_o2_analyser/config.json`

- **Windows**: `C:\Users\{username}\.co_o2_analyser\config.json`
- **macOS/Linux**: `/home/{username}/.co_o2_analyser/config.json`

#### Configuration Priority

1. **User Configuration File** - Highest priority (overrides all defaults)
2. **Default Configuration** - Fallback values defined in `src/co_o2_analyser/utils/config.py`

#### Creating Configuration File

The configuration file is automatically created on first run with default values. You can also manually create it:

```bash
# The application will create the config directory and file automatically
python main.py
```

#### Configuration Structure

```json
{
  "instrument": {
    "ip_address": "192.168.1.1",
    "port": 8180,
    "timeout": 30,
    "retry_attempts": 3,
    "simulation_mode": false,
    "data_simulation": false,
    "tags": {
      "instrument_status": ["INSTRUMENT_TIME", "NETWORK_IP_ADDRESS", "OS_VERSION"],
      "concentration_tags": ["CO_CONC", "O2_CONC"],
      "warning_tags": ["BOX_TEMP_WARN", "BENCH_TEMP_WARN", "WHEEL_TEMP_WARN"],
      "flow_tags": ["AI_PUMP_FLOW", "AI_SAMPLE_TEMP", "AI_SAMPLE_PRESSURE"],
      "temperature": ["AI_SAMPLE_TEMP", "AI_DETECTOR_TEMP", "AI_BOX_TEMP"]
    }
  },
  "database": {
    "path": "data.sqlite",
    "backup_interval": 3600
  },
  "gui": {
    "window_width": 1920,
    "window_height": 1009,
    "theme": "light"
  },
  "logging": {
    "level": "INFO",
    "file": "co_o2_analyser.log",
    "max_size": 10485760
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

### Instrument Settings

```json
{
  "instrument": {
    "ip_address": "192.168.1.1",
    "port": 8180,
    "timeout": 30,
    "retry_attempts": 3,
    "simulation_mode": false,
    "data_simulation": false
  }
}
```

#### Key Instrument Settings

- **`ip_address`**: IP address of the Teledyne N300M analyzer
- **`port`**: HTTP port (default: 8180)
- **`timeout`**: Request timeout in seconds
- **`retry_attempts`**: Number of retry attempts for failed requests
- **`simulation_mode`**: Enable/disable instrument simulation mode
- **`data_simulation`**: Enable/disable data simulation (unused)

### Database Settings

```json
{
  "database": {
    "path": "data.sqlite",
    "backup_interval": 3600
  }
}
```

#### Key Database Settings

- **`path`**: Path to the main SQLite database file
- **`backup_interval`**: Database backup interval in seconds (3600 = 1 hour)

### Data Collection Settings

```json
{
  "data_collection": {
    "intervals": {
      "all_values_interval": 60,
      "concentration_interval": 1.5,
      "status_check_interval": 10
    }
  }
}
```

#### Key Data Collection Settings

- **`all_values_interval`**: Interval for collecting all instrument values (60 seconds = 1 minute)
- **`concentration_interval`**: Interval for collecting CO and O2 concentration data (1.5 seconds)
- **`status_check_interval`**: Interval for checking instrument status (10 seconds)

### Database Schema

The system uses two types of databases:

#### Main Database (`data.sqlite`)
- **Continuous logging** of all instrument data
- **Table**: `measurements`
- **Fields**: `timestamp`, `co_concentration`, `o2_concentration`, `sample_temp`, `sample_flow`, `instrument_status`

#### Session Databases (`measurement{DDmmYY}.sqlite`)
- **Session-specific** measurement data
- **Table**: `measurements` (same schema as main database)
- **Additional fields**: `fume_limit`, `percentage_to_limit`
- **Session metadata**: Tracked in main database `measurement_sessions` table

### GUI Settings

```json
{
  "gui": {
    "window_width": 1920,
    "window_height": 1009,
    "theme": "light"
  }
}
```

#### Key GUI Settings

- **`window_width`**: Initial window width in pixels
- **`window_height`**: Initial window height in pixels
- **`theme`**: GUI theme (currently only "light" supported)

### Logging Settings

```json
{
  "logging": {
    "level": "INFO",
    "file": "co_o2_analyser.log",
    "max_size": 10485760
  }
}
```

#### Key Logging Settings

- **`level`**: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **`file`**: Log file name
- **`max_size`**: Maximum log file size in bytes (10485760 = 10MB)

### Configuration Management

#### Settings Dialog

The application now includes a comprehensive **Settings Dialog** accessible via **Tools → Settings** in the main menu. The dialog provides:

**Tabbed Interface:**
- **Instrument Tab**: IP address, port, timeout, retry attempts, simulation mode, tag configuration
- **Database Tab**: Database path, backup interval settings
- **GUI Tab**: Window dimensions, theme selection
- **Data Collection Tab**: Collection intervals for different data types
- **Logging Tab**: Log level, file path, and size limits

**Settings Testing:**
- **Test Settings Button**: Validates all configuration settings
- **Instrument Connection Test**: Tests connectivity to the instrument
- **Database Path Test**: Validates database file accessibility
- **Logging Config Test**: Verifies log file write permissions

**Configuration Management:**
- **Load/Save**: Automatic loading and saving of config.json
- **Default Values**: Fallback to sensible defaults
- **Validation**: Input validation and error handling
- **Restore Defaults**: Reset all settings to default values

#### Editing Configuration

1. **Settings Dialog**: Use the GUI settings dialog for easy configuration
2. **Automatic Creation**: The config file is created automatically on first run
3. **Manual Editing**: Edit the JSON file directly with any text editor
4. **Hot Reload**: Configuration changes require application restart
5. **Validation**: Invalid JSON will cause the application to use default values

#### Configuration Examples

**Enable Simulation Mode**:
```json
{
  "instrument": {
    "simulation_mode": true
  }
}
```

**Change Data Collection Intervals**:
```json
{
  "data_collection": {
    "intervals": {
      "concentration_interval": 2.0,
      "all_values_interval": 600
    }
  }
}
```

**Custom Database Path**:
```json
{
  "database": {
    "path": "custom_data.sqlite"
  }
}
```

## 🔧 Instrument Management

The application includes comprehensive **Instrument Management** capabilities accessible via **Tools → Instrument Settings** in the main menu.

### Features

**Time Synchronization:**
- **Automatic Sync**: Synchronize instrument time with computer time
- **Real-time Display**: Shows current computer time in the dialog
- **Configuration Setup**: Automatically configures time sync settings
- **Verification**: Confirms time changes on the instrument

**Instrument Control:**
- **Restart Instrument**: Send restart command to the instrument
- **Shutdown Instrument**: Send shutdown command to the instrument
- **Data Collector Management**: Automatically stops data collector before operations
- **Safety Confirmations**: User confirmation for critical operations

**Operation Monitoring:**
- **Real-time Logging**: Detailed operation logs with timestamps
- **Progress Indicators**: Visual feedback during operations
- **Status Display**: Shows data collector status and operation results
- **Error Handling**: Comprehensive error handling with user-friendly messages

### Usage

1. **Open Instrument Management**: Go to **Tools** → **🔧 Instrument Settings**
2. **Time Sync**: Click "🕐 Synchronize Instrument Time" to sync with computer time
3. **Restart**: Click "🔄 Restart Instrument" to restart the instrument
4. **Shutdown**: Click "⏹️ Shutdown Instrument" to shutdown the instrument
5. **Monitor**: Watch the operation logs for real-time feedback

### Safety Features

- **Data Collector Stop**: Automatically stops data collection before shutdown/restart
- **Confirmation Dialogs**: User confirmation required for critical operations
- **Connection Validation**: Checks instrument connectivity before operations
- **Error Recovery**: Graceful handling of connection failures
- **Application Exit Shutdown**: Option to shutdown instrument when closing the application

## 📊 API Documentation

The software communicates with the **Teledyne N300M** using the **TAPI Tag REST Interface**:

### Endpoints

- **GET** `/api/taglist` - Retrieve available instrument tags
- **GET** `/api/tag/{tagName}/value` - Get current tag value
- **PUT** `/api/tag/{tagName}/value` - Set tag value
- **GET** `/api/dataloglist` - Retrieve logged data

### Example Usage

```python
from co_o2_analyser.core.instrument_communication import InstrumentCommunication
from co_o2_analyser.utils.config import Config

config = Config()
instrument = InstrumentCommunication(config)

# Get tag list
tags = instrument.get_tag_list()

# Get CO concentration
co_value = instrument.get_tag_value("CO_Concentration")
```

## 🧪 Development

### Setting Up Development Environment

1. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

### Code Quality

- **Formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for code linting
- **Type checking**: Use `mypy` for static type checking
- **Testing**: Use `pytest` for testing

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📚 Documentation

- **User Guide**: See `docs/user_guide/` for detailed usage instructions
- **API Reference**: See `docs/api/` for complete API documentation
- **Developer Guide**: See `docs/developer/` for development information

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Verify instrument IP address and port
   - Check network connectivity
   - Ensure instrument is powered on and accessible

2. **No Data Received**:
   - Check instrument status
   - Verify tag names are correct
   - Check API endpoint accessibility

3. **GUI Not Starting**:
   - Verify PyQt6 installation
   - Check Python version (3.11+)
   - Review error logs

4. **Settings Dialog Issues**:
   - Check config file permissions
   - Verify JSON syntax in config file
   - Use "Test Settings" button to validate configuration

5. **Instrument Management Issues**:
   - Verify instrument is powered on and connected
   - Check network connectivity to instrument IP
   - Ensure data collector is stopped before shutdown/restart operations

### Getting Help

- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/CO_O2Analyser/issues)
- **Discussions**: Use [GitHub Discussions](https://github.com/yourusername/CO_O2Analyser/discussions)
- **Documentation**: Check the [documentation](https://co-o2-analyser.readthedocs.io/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Teledyne API Technologies** for the N300M analyzer
- **PyQt6** team for the excellent GUI framework
- **Matplotlib** team for plotting capabilities
- **SQLite** for reliable data storage

## 📞 Support

For support and questions:

- **Email**: software@farfallelab.com
- **GitHub**: [@yourusername](https://github.com/AlbiAlibi)
- **Documentation**: [Read the Docs](https://co-o2-analyser.readthedocs.io/)

---

**Made with ❤️ for environmental monitoring and air quality research**
