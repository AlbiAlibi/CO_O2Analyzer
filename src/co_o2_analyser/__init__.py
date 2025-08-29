"""
CO_O2_Analyser - Carbon Monoxide and Oxygen Analyzer Software

A software tool designed to communicate with the Teledyne N300M carbon monoxide analyzer
via HTTP protocol, retrieve air quality data, and store it in a database.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "Carbon Monoxide and Oxygen Analyzer Software"

from .core.analyzer import COO2Analyzer
from .gui.main_window import MainWindow

__all__ = [
    "COO2Analyzer",
    "MainWindow",
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]
