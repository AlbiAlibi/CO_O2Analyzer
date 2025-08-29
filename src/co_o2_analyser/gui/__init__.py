"""
Graphical User Interface for CO_O2_Analyser.

This module contains all GUI-related components including the main window,
plots, and user interface elements.
"""

from .main_window import MainWindow
from .plot_widget import PlotWidget
from .status_widget import StatusWidget

__all__ = [
    "MainWindow",
    "PlotWidget",
    "StatusWidget",
]
