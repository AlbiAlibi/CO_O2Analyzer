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
- **Configurable Settings**: Easy configuration management for instrument settings
- **Logging & Monitoring**: Comprehensive logging and error handling
- **Cross-platform**: Works on Windows, macOS, and Linux

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

# Or install and run as module
pip install -e .
co-o2-analyser
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
│       │   ├── analyzer.py       # Main analyzer class
│       │   ├── data_processor.py # Data processing
│       │   └── instrument_communication.py # Instrument communication
│       ├── data/                 # Data models
│       │   └── models.py         # Data classes
│       ├── gui/                  # Graphical interface
│       │   ├── main_window.py    # Main window
│       │   ├── plot_widget.py    # Plotting widget
│       │   └── status_widget.py  # Status display
│       └── utils/                # Utilities
│           ├── config.py         # Configuration management
│           ├── database.py       # Database operations
│           └── logger.py         # Logging setup
├── tests/                        # Test suite
├── docs/                         # Documentation
├── examples/                     # Usage examples
├── main.py                       # Main entry point
├── pyproject.toml               # Project configuration
├── requirements.txt              # Runtime dependencies
└── README.md                     # This file
```

## 🔧 Configuration

### Instrument Settings

```json
{
  "instrument": {
    "ip_address": "192.168.1.100",
    "port": 8180,
    "timeout": 30,
    "retry_attempts": 3
  }
}
```

### Database Settings

```json
{
  "database": {
    "path": "data_store.sqlite",
    "backup_interval": 3600
  }
}
```

### GUI Settings

```json
{
  "gui": {
    "window_width": 1200,
    "window_height": 800,
    "theme": "light"
  }
}
```

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
