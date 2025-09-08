#!/usr/bin/env python3
"""
Setup script for creating standalone executable with cx_Freeze.

This script creates a standalone executable that includes all dependencies.
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies to include
build_exe_options = {
    "packages": [
        "PyQt6",
        "matplotlib",
        "numpy",
        "pandas",
        "requests",
        "sqlite3",
        "json",
        "datetime",
        "pathlib",
        "logging",
        "threading",
        "subprocess",
        "signal",
        "time",
        "os",
        "sys"
    ],
    "excludes": [
        "tkinter",
        "unittest",
        "pydoc",
        "doctest",
        "test",
        "tests"
    ],
    "include_files": [
        ("README.md", "README.md"),
        ("LICENSE", "LICENSE"),
        ("docs/", "docs/"),
        ("examples/", "examples/")
    ],
    "zip_include_packages": "*",
    "zip_exclude_packages": "",
    "optimize": 2,
}

# GUI application
gui_executable = Executable(
    "main.py",
    base="Win32GUI" if sys.platform == "win32" else None,
    target_name="CO_O2_Analyser.exe" if sys.platform == "win32" else "CO_O2_Analyser",
    icon="icon.ico" if sys.platform == "win32" else None,
    shortcut_name="CO_O2_Analyser",
    shortcut_dir="DesktopFolder"
)

# Console application for data collector
console_executable = Executable(
    "start_data_collector.py",
    base="Console",
    target_name="CO_O2_DataCollector.exe" if sys.platform == "win32" else "CO_O2_DataCollector"
)

setup(
    name="CO_O2_Analyser",
    version="1.0.0",
    description="Carbon Monoxide and Oxygen Analyzer Software",
    author="Your Name",
    author_email="your.email@example.com",
    options={"build_exe": build_exe_options},
    executables=[gui_executable, console_executable]
)
