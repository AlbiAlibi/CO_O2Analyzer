# CO_O2_Analyser Installation Guide

This guide explains how to install and use the CO_O2_Analyser Python module.

## 📦 Installation Methods

### Method 1: Install from Source (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/CO_O2Analyser.git
   cd CO_O2Analyser
   ```

2. **Create a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the package in development mode:**
   ```bash
   pip install -e .
   ```

### Method 2: Install Dependencies Only

1. **Install runtime dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python main.py
   ```

### Method 3: Install with Development Tools

1. **Install with all development dependencies:**
   ```bash
   pip install -e ".[dev,test,docs]"
   ```

## 🚀 Running the Application

### Option 1: Run as Python Module
```bash
python -m co_o2_analyser
```

### Option 2: Run Main Script
```bash
python main.py
```

### Option 3: Run Data Collector
```bash
python start_data_collector.py
```

### Option 4: Use Command Line Entry Points (after installation)
```bash
# GUI application
co-o2-analyser-gui

# Command line interface (if implemented)
co-o2-analyser
```

## 🔧 Configuration

The application will automatically create a configuration file on first run:

- **Windows**: `C:\Users\{username}\.co_o2_analyser\config.json`
- **macOS/Linux**: `/home/{username}/.co_o2_analyser/config.json`

### Default Configuration
```json
{
  "instrument": {
    "ip_address": "192.168.1.1",
    "port": 8180,
    "timeout": 30,
    "retry_attempts": 3,
    "simulation_mode": false
  },
  "database": {
    "path": "data.sqlite",
    "backup_interval": 3600
  },
  "gui": {
    "window_width": 1200,
    "window_height": 800,
    "theme": "light"
  }
}
```

## 📋 System Requirements

- **Python**: 3.11 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free disk space
- **Network**: Ethernet connection to Teledyne N300M analyzer

## 🐍 Python Dependencies

### Core Dependencies
- **PyQt6** (>=6.4.0): GUI framework
- **matplotlib** (>=3.6.0): Data visualization
- **numpy** (>=1.21.0): Numerical computing
- **pandas** (>=1.3.0): Data manipulation
- **requests** (>=2.25.0): HTTP communication
- **python-dateutil** (>=2.8.0): Date/time utilities

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **sphinx**: Documentation generation

## 🔨 Building Distribution Packages

### Build Source Distribution
```bash
python -m build --sdist
```

### Build Wheel Distribution
```bash
python -m build --wheel
```

### Build Both
```bash
python -m build
```

## 📦 Creating Standalone Executable

### Using PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "CO_O2_Analyser" main.py
```

### Using cx_Freeze
```bash
# Install cx_Freeze
pip install cx_Freeze

# Create executable
python setup_cx_freeze.py build
```

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=co_o2_analyser
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## 📚 Development Setup

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

### Setup Pre-commit Hooks
```bash
pre-commit install
```

### Code Formatting
```bash
black src/ tests/
```

### Code Linting
```bash
flake8 src/ tests/
```

### Type Checking
```bash
mypy src/
```

## 🐛 Troubleshooting

### Common Issues

1. **PyQt6 Installation Issues:**
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install python3-pyqt6
   
   # On macOS with Homebrew
   brew install pyqt6
   ```

2. **Permission Errors:**
   ```bash
   # Use --user flag
   pip install --user -e .
   ```

3. **Virtual Environment Issues:**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -e .
   ```

4. **Import Errors:**
   ```bash
   # Ensure you're in the project root directory
   cd CO_O2Analyser
   python -m co_o2_analyser
   ```

### Getting Help

- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/CO_O2Analyser/issues)
- **Documentation**: Check the [README.md](README.md) file
- **Logs**: Check `co_o2_analyser.log` for detailed error information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
