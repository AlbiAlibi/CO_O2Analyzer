"""
Plot widget for CO_O2_Analyser.

This module contains the plotting widget that displays
measurement data in real-time graphs.
"""

import logging
from typing import Optional, List
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import QTimer, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

from ..data.models import Measurement

logger = logging.getLogger(__name__)


class PlotWidget(QWidget):
    """Widget for displaying measurement plots."""
    
    def __init__(self):
        """Initialize plot widget."""
        super().__init__()
        self.measurements: List[Measurement] = []
        self.max_points = 1000  # Maximum number of points to display
        
        self._init_ui()
        self._setup_plot()
        
        # Timer for plot updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_plot)
        self.update_timer.start(1000)  # Update every second
        
        logger.info("Plot widget initialized")
    
    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Plot type selector
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["Real-time", "Historical", "Statistics"])
        self.plot_type_combo.currentTextChanged.connect(self._on_plot_type_changed)
        control_layout.addWidget(QLabel("Plot Type:"))
        control_layout.addWidget(self.plot_type_combo)
        
        # Time range selector
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["1 hour", "6 hours", "24 hours", "7 days"])
        self.time_range_combo.currentTextChanged.connect(self._on_time_range_changed)
        control_layout.addWidget(QLabel("Time Range:"))
        control_layout.addWidget(self.time_range_combo)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Status label
        self.status_label = QLabel("No data available")
        layout.addWidget(self.status_label)
    
    def _setup_plot(self):
        """Setup the matplotlib plot."""
        # Create subplots
        self.ax1 = self.figure.add_subplot(211)  # CO concentration
        self.ax2 = self.figure.add_subplot(212)  # O2 concentration
        
        # Configure axes
        self.ax1.set_title("Carbon Monoxide Concentration")
        self.ax1.set_ylabel("CO (ppm)")
        self.ax1.grid(True)
        
        self.ax2.set_title("Oxygen Concentration")
        self.ax2.set_ylabel("O₂ (%)")
        self.ax2.set_xlabel("Time")
        self.ax2.grid(True)
        
        # Format x-axis for time
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        
        # Rotate x-axis labels
        plt.setp(self.ax1.xaxis.get_majorticklabels(), rotation=45)
        plt.setp(self.ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # Adjust layout
        self.figure.tight_layout()
        
        # Initialize empty lines
        self.co_line, = self.ax1.plot([], [], 'r-', label='CO', linewidth=2)
        self.o2_line, = self.ax2.plot([], [], 'b-', label='O₂', linewidth=2)
        
        # Add legends
        self.ax1.legend()
        self.ax2.legend()
    
    def add_measurement(self, measurement: Measurement):
        """Add a new measurement to the plot.
        
        Args:
            measurement: New measurement to add
        """
        try:
            # Add to measurements list
            self.measurements.append(measurement)
            
            # Limit the number of points
            if len(self.measurements) > self.max_points:
                self.measurements = self.measurements[-self.max_points:]
            
            # Update status
            self.status_label.setText(f"Last update: {measurement.timestamp.strftime('%H:%M:%S')}")
            
            logger.debug(f"Added measurement: CO={measurement.co_concentration}, O2={measurement.o2_concentration}")
            
        except Exception as e:
            logger.error(f"Failed to add measurement: {e}")
    
    def _update_plot(self):
        """Update the plot with current data."""
        if not self.measurements:
            return
        
        try:
            # Extract data
            timestamps = [m.timestamp for m in self.measurements]
            co_values = [m.co_concentration for m in self.measurements]
            o2_values = [m.o2_concentration for m in self.measurements]
            
            # Filter out None values
            valid_data = [(t, co, o2) for t, co, o2 in zip(timestamps, co_values, o2_values) 
                         if co is not None and o2 is not None]
            
            if not valid_data:
                return
            
            # Unzip valid data
            valid_times, valid_co, valid_o2 = zip(*valid_data)
            
            # Update plot data
            self.co_line.set_data(valid_times, valid_co)
            self.o2_line.set_data(valid_times, valid_o2)
            
            # Auto-scale axes
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            
            # Update canvas
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Failed to update plot: {e}")
    
    def _on_plot_type_changed(self, plot_type: str):
        """Handle plot type change.
        
        Args:
            plot_type: New plot type
        """
        logger.info(f"Plot type changed to: {plot_type}")
        # TODO: Implement different plot types
    
    def _on_time_range_changed(self, time_range: str):
        """Handle time range change.
        
        Args:
            time_range: New time range
        """
        logger.info(f"Time range changed to: {time_range}")
        # TODO: Implement time range filtering
    
    def clear_plot(self):
        """Clear all data from the plot."""
        self.measurements.clear()
        self.co_line.set_data([], [])
        self.o2_line.set_data([], [])
        self.canvas.draw()
        self.status_label.setText("No data available")
        logger.info("Plot cleared")
    
    def export_plot(self, filename: str):
        """Export the current plot to an image file.
        
        Args:
            filename: Output filename
        """
        try:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            logger.info(f"Plot exported to: {filename}")
        except Exception as e:
            logger.error(f"Failed to export plot: {e}")
    
    def get_statistics(self) -> dict:
        """Get statistics for the current data.
        
        Returns:
            Dictionary containing statistics
        """
        if not self.measurements:
            return {}
        
        try:
            co_values = [m.co_concentration for m in self.measurements if m.co_concentration is not None]
            o2_values = [m.o2_concentration for m in self.measurements if m.o2_concentration is not None]
            
            stats = {}
            
            if co_values:
                stats['co'] = {
                    'min': min(co_values),
                    'max': max(co_values),
                    'mean': np.mean(co_values),
                    'std': np.std(co_values)
                }
            
            if o2_values:
                stats['o2'] = {
                    'min': min(o2_values),
                    'max': max(o2_values),
                    'mean': np.mean(o2_values),
                    'std': np.std(o2_values)
                }
            
            stats['total_measurements'] = len(self.measurements)
            stats['time_range'] = {
                'start': self.measurements[0].timestamp.isoformat(),
                'end': self.measurements[-1].timestamp.isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to calculate statistics: {e}")
            return {}
