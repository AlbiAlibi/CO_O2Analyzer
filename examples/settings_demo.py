#!/usr/bin/env python3
"""
Settings Dialog Demo

This script demonstrates how to use the settings dialog
to manage configuration files.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from co_o2_analyser.gui.settings_dialog import SettingsDialog

class SettingsDemo(QMainWindow):
    """Demo window for settings dialog."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings Dialog Demo")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add button to open settings
        settings_btn = QPushButton("Open Settings Dialog")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)
        
        # Add button to show current config
        show_config_btn = QPushButton("Show Current Config")
        show_config_btn.clicked.connect(self.show_config)
        layout.addWidget(show_config_btn)
        
        central_widget.setLayout(layout)
        
        # Config path
        self.config_path = Path.home() / ".co_o2_analyser" / "config.json"
    
    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(str(self.config_path), self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()
    
    def on_settings_changed(self, new_config):
        """Handle settings changes."""
        print("Settings changed!")
        print(f"New instrument IP: {new_config['instrument']['ip_address']}")
        print(f"New database path: {new_config['database']['path']}")
        print(f"New log level: {new_config['logging']['level']}")
    
    def show_config(self):
        """Show current configuration."""
        import json
        
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            print("\n=== Current Configuration ===")
            print(f"Instrument IP: {config['instrument']['ip_address']}")
            print(f"Port: {config['instrument']['port']}")
            print(f"Database: {config['database']['path']}")
            print(f"Log Level: {config['logging']['level']}")
            print(f"Window Size: {config['gui']['window_width']}x{config['gui']['window_height']}")
            print("=============================\n")
        else:
            print("No configuration file found.")

def main():
    """Main function."""
    app = QApplication(sys.argv)
    
    demo = SettingsDemo()
    demo.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
