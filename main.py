#!/usr/bin/env python3
"""
Main entry point for CO_O2_Analyser application.

This script launches the main GUI application and handles command-line arguments.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from co_o2_analyser.gui.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from co_o2_analyser.utils.logger import setup_logger
from co_o2_analyser.utils.config import Config


def main():
    """Main application entry point."""
    # Load configuration
    config = Config()

    # Setup logging (enable file logging from config)
    logger = setup_logger(
        level=config.get('logging.level', 'INFO'),
        log_file=config.get('logging.file')
    )
    logger.info("Starting CO_O2_Analyser application")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("CO_O2_Analyser")
    app.setApplicationVersion("1.0.0")
    
    # Create and show main window
    main_window = MainWindow(config)
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
