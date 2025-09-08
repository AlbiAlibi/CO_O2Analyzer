#!/usr/bin/env python3
"""
Main entry point for CO_O2_Analyser when run as a module.

This allows the package to be run with: python -m co_o2_analyser
"""

import sys
import logging
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from co_o2_analyser.gui.main_window import main

if __name__ == "__main__":
    main()
