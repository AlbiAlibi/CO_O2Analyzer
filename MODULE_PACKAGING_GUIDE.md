# CO_O2_Analyser Module Packaging Guide

This guide explains how to prepare the CO_O2_Analyser as a ready-to-use Python module with all required libraries.

## 📦 What's Included

### Core Files
- **`pyproject.toml`** - Modern Python packaging configuration
- **`setup.py`** - Backward compatibility setup script
- **`requirements.txt`** - Runtime dependencies
- **`requirements-dev.txt`** - Development dependencies

### Entry Points
- **`src/co_o2_analyser/__main__.py`** - Module entry point (`python -m co_o2_analyser`)
- **`src/co_o2_analyser/gui/main_window.py`** - GUI entry point with `main()` function
- **Command line scripts** - `co-o2-analyser` and `co-o2-analyser-gui`

### Build Tools
- **`build.py`** - Automated build script
- **`setup_cx_freeze.py`** - Standalone executable creation
- **`test_module.py`** - Module functionality testing

### Documentation
- **`INSTALLATION.md`** - Detailed installation instructions
- **`USAGE.md`** - Comprehensive usage guide
- **`MODULE_PACKAGING_GUIDE.md`** - This guide

## 🚀 Quick Start

### 1. Install the Module

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

### 2. Test the Installation

```bash
# Run the test script
python test_module.py

# Run example usage
python examples/module_usage.py
```

### 3. Run the Application

```bash
# GUI application
python -m co_o2_analyser

# Or use the entry point
co-o2-analyser

# Data collector service
python start_data_collector.py
```

## 🔧 Installation Methods

### Method 1: Development Installation (Recommended)

```bash
# Install in development mode with all dependencies
pip install -e ".[dev,test,docs]"
```

### Method 2: Runtime Installation

```bash
# Install only runtime dependencies
pip install -r requirements.txt
pip install -e .
```

### Method 3: Production Installation

```bash
# Build and install from wheel
python -m build
pip install dist/co_o2_analyser-1.0.0-py3-none-any.whl
```

## 📦 Creating Distribution Packages

### Build All Distributions

```bash
# Using the build script
python build.py all

# Or manually
python -m build
```

### Build Specific Types

```bash
# Source distribution only
python build.py source

# Wheel distribution only
python build.py wheel

# Standalone executable
python build.py exe
```

## 🎯 Entry Points

The module provides several ways to run the application:

### 1. Python Module
```bash
python -m co_o2_analyser
```

### 2. Command Line Scripts
```bash
# GUI application
co-o2-analyser

# GUI application (alternative)
co-o2-analyser-gui
```

### 3. Direct Script Execution
```bash
# Main GUI
python main.py

# Data collector
python start_data_collector.py
```

## 🧪 Testing the Module

### Automated Testing
```bash
# Run comprehensive tests
python test_module.py

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Manual Testing
```bash
# Test imports
python -c "import co_o2_analyser; print('✅ Module imported successfully')"

# Test configuration
python -c "from co_o2_analyser.utils.config import Config; c = Config(); print('✅ Config works')"

# Test GUI (without showing window)
python -c "from co_o2_analyser.gui.main_window import main; print('✅ GUI module works')"
```

## 📚 Dependencies

### Runtime Dependencies
- **PyQt6** (>=6.4.0) - GUI framework
- **matplotlib** (>=3.6.0) - Data visualization
- **numpy** (>=1.21.0) - Numerical computing
- **pandas** (>=1.3.0) - Data manipulation
- **requests** (>=2.25.0) - HTTP communication
- **python-dateutil** (>=2.8.0) - Date/time utilities

### Development Dependencies
- **pytest** - Testing framework
- **black** - Code formatting
- **flake8** - Code linting
- **mypy** - Type checking
- **sphinx** - Documentation generation

## 🔨 Build Process

### 1. Clean Build
```bash
python build.py clean
```

### 2. Install Dependencies
```bash
python build.py deps
```

### 3. Build Packages
```bash
python build.py all
```

### 4. Create Executable
```bash
python build.py exe
```

### 5. Full Build
```bash
python build.py full
```

## 📁 Generated Files

After building, you'll find:

### Distribution Packages
- **`dist/co_o2_analyser-1.0.0.tar.gz`** - Source distribution
- **`dist/co_o2_analyser-1.0.0-py3-none-any.whl`** - Wheel distribution

### Standalone Executables
- **`dist/CO_O2_Analyser.exe`** - Windows executable
- **`dist/CO_O2_Analyser`** - Linux/macOS executable
- **`dist/CO_O2_DataCollector.exe`** - Data collector executable

## 🚀 Deployment Options

### 1. PyPI Distribution
```bash
# Build packages
python -m build

# Upload to PyPI
twine upload dist/*
```

### 2. Local Installation
```bash
# Install from local wheel
pip install dist/co_o2_analyser-1.0.0-py3-none-any.whl
```

### 3. Standalone Executable
```bash
# Create executable
python build.py exe

# Distribute the executable from dist/ folder
```

### 4. Docker Container
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["python", "-m", "co_o2_analyser"]
```

## 🔧 Configuration

The module automatically creates configuration files:

### Windows
```
C:\Users\{username}\.co_o2_analyser\config.json
```

### macOS/Linux
```
/home/{username}/.co_o2_analyser/config.json
```

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

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure module is installed
   pip install -e .
   
   # Check Python path
   python -c "import sys; print(sys.path)"
   ```

2. **Missing Dependencies**
   ```bash
   # Install all dependencies
   pip install -r requirements.txt
   
   # Or install with extras
   pip install -e ".[dev,test,docs]"
   ```

3. **GUI Issues**
   ```bash
   # Test GUI components
   python test_module.py
   
   # Check PyQt6 installation
   python -c "import PyQt6; print('PyQt6 OK')"
   ```

4. **Build Issues**
   ```bash
   # Clean and rebuild
   python build.py clean
   python build.py deps
   python build.py all
   ```

## 📞 Support

For additional help:

- **Documentation**: Check `README.md`, `INSTALLATION.md`, and `USAGE.md`
- **Examples**: Run `python examples/module_usage.py`
- **Testing**: Run `python test_module.py`
- **Issues**: Report on GitHub Issues

## 🎉 Success Indicators

You'll know the module is ready when:

1. ✅ `python test_module.py` passes all tests
2. ✅ `python -m co_o2_analyser` starts the GUI
3. ✅ `co-o2-analyser` command works
4. ✅ All dependencies are properly installed
5. ✅ Configuration file is created automatically
6. ✅ Database operations work correctly

The CO_O2_Analyser is now a fully packaged, ready-to-use Python module! 🚀
