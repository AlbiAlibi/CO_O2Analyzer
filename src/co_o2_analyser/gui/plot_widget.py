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
        
        # Measurement session tracking
        self.measurement_sessions = []  # List of (start_time, end_time, session_number)
        self.current_session_number = 0
        
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
        self.time_range_combo.addItems(["1 min", "5 min", "10 min", "30 min", "1 hour", "3 hours"])
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
    
    def start_measurement_session(self):
        """Mark the start of a new measurement session."""
        try:
            self.current_session_number += 1
            start_time = datetime.now()
            self.measurement_sessions.append((start_time, None, self.current_session_number))
            logger.info(f"Started measurement session #{self.current_session_number} at {start_time}")
        except Exception as e:
            logger.error(f"Failed to start measurement session: {e}")
    
    def stop_measurement_session(self):
        """Mark the end of the current measurement session."""
        try:
            if self.measurement_sessions and self.measurement_sessions[-1][1] is None:
                end_time = datetime.now()
                start_time, _, session_number = self.measurement_sessions[-1]
                self.measurement_sessions[-1] = (start_time, end_time, session_number)
                logger.info(f"Stopped measurement session #{session_number} at {end_time}")
        except Exception as e:
            logger.error(f"Failed to stop measurement session: {e}")
    
    def _update_plot(self):
        """Update the plot with current data."""
        if not self.measurements:
            return
        
        try:
            # Get current time range selection
            current_range = self.time_range_combo.currentText()
            
            # Calculate the cutoff time based on the selected range
            now = datetime.now()
            if current_range == "1 min":
                cutoff_time = now - timedelta(minutes=1)
            elif current_range == "5 min":
                cutoff_time = now - timedelta(minutes=5)
            elif current_range == "10 min":
                cutoff_time = now - timedelta(minutes=10)
            elif current_range == "30 min":
                cutoff_time = now - timedelta(minutes=30)
            elif current_range == "1 hour":
                cutoff_time = now - timedelta(hours=1)
            elif current_range == "3 hours":
                cutoff_time = now - timedelta(hours=3)
            else:
                # Default to 1 hour if unknown
                cutoff_time = now - timedelta(hours=1)
            
            # Filter measurements within the time range
            filtered_measurements = [
                m for m in self.measurements 
                if m.timestamp >= cutoff_time
            ]
            
            # Update the plot with filtered data
            if filtered_measurements:
                self._update_plot_with_data(filtered_measurements)
            else:
                # Clear plot if no data in range
                self.co_line.set_data([], [])
                self.o2_line.set_data([], [])
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
        
        # Trigger a plot update with the new time range
        self._update_plot()
    
    def _update_plot_with_data(self, measurements: List[Measurement]):
        """Update the plot with specific measurement data.
        
        Args:
            measurements: List of measurements to display
        """
        try:
            # Extract data
            timestamps = [m.timestamp for m in measurements]
            co_values = [m.co_concentration for m in measurements]
            o2_values = [m.o2_concentration for m in measurements]
            
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
            
            # Draw measurement session markers
            self._draw_measurement_markers()
            
            # Auto-scale axes
            self.ax1.relim()
            self.ax1.autoscale_view()
            self.ax2.relim()
            self.ax2.autoscale_view()
            
            # Update canvas
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Failed to update plot with data: {e}")
    
    def _draw_measurement_markers(self):
        """Draw measurement session markers on both plots."""
        try:
            # Clear existing markers
            for ax in [self.ax1, self.ax2]:
                # Remove existing vertical lines and text
                for line in ax.lines[:]:
                    if hasattr(line, '_is_measurement_marker'):
                        line.remove()
                for text in ax.texts[:]:
                    if hasattr(text, '_is_measurement_marker'):
                        text.remove()
            
            if not self.measurement_sessions:
                return
            
            # Get current time range for filtering
            current_range = self.time_range_combo.currentText()
            now = datetime.now()
            if current_range == "1 min":
                cutoff_time = now - timedelta(minutes=1)
            elif current_range == "5 min":
                cutoff_time = now - timedelta(minutes=5)
            elif current_range == "10 min":
                cutoff_time = now - timedelta(minutes=10)
            elif current_range == "30 min":
                cutoff_time = now - timedelta(minutes=30)
            elif current_range == "1 hour":
                cutoff_time = now - timedelta(hours=1)
            elif current_range == "3 hours":
                cutoff_time = now - timedelta(hours=3)
            else:
                cutoff_time = now - timedelta(hours=1)
            
            # Draw markers for each session - only if ANY part of the session is within range
            for start_time, end_time, session_number in self.measurement_sessions:
                # Check if session overlaps with current time range
                session_end = end_time if end_time else now
                
                # Session overlaps if:
                # 1. Session starts within the current range, OR
                # 2. Session ends within the current range, OR  
                # 3. Session completely encompasses the current range
                session_overlaps = (
                    (start_time >= cutoff_time and start_time <= now) or  # Start within range
                    (session_end >= cutoff_time and session_end <= now) or  # End within range
                    (start_time <= cutoff_time and session_end >= now)  # Session encompasses range
                )
                
                if session_overlaps:
                    self._draw_session_markers(start_time, end_time, session_number)
                    
        except Exception as e:
            logger.error(f"Failed to draw measurement markers: {e}")
    
    def _draw_session_markers(self, start_time, end_time, session_number):
        """Draw markers for a single measurement session.
        
        Args:
            start_time: Start time of the session
            end_time: End time of the session (None if ongoing)
            session_number: Session number
        """
        try:
            # Get current time range for clipping
            current_range = self.time_range_combo.currentText()
            now = datetime.now()
            if current_range == "1 min":
                cutoff_time = now - timedelta(minutes=1)
            elif current_range == "5 min":
                cutoff_time = now - timedelta(minutes=5)
            elif current_range == "10 min":
                cutoff_time = now - timedelta(minutes=10)
            elif current_range == "30 min":
                cutoff_time = now - timedelta(minutes=30)
            elif current_range == "1 hour":
                cutoff_time = now - timedelta(hours=1)
            elif current_range == "3 hours":
                cutoff_time = now - timedelta(hours=3)
            else:
                cutoff_time = now - timedelta(hours=1)
            
            # Get y-axis limits for both plots
            y1_min, y1_max = self.ax1.get_ylim()
            y2_min, y2_max = self.ax2.get_ylim()
            
            # Only draw start marker if it's within the visible time range
            if start_time >= cutoff_time and start_time <= now:
                for ax, y_min, y_max in [(self.ax1, y1_min, y1_max), (self.ax2, y2_min, y2_max)]:
                    start_line = ax.axvline(x=start_time, color='blue', linestyle=':', linewidth=1, alpha=0.7)
                    start_line._is_measurement_marker = True
                    
                    # Add session number text at the top
                    text = ax.text(start_time, y_max * 0.95, f"#{session_number}", 
                                 color='blue', fontsize=8, ha='center', va='top')
                    text._is_measurement_marker = True
            
            # Only draw end marker if it's within the visible time range
            if end_time and end_time >= cutoff_time and end_time <= now:
                for ax, y_min, y_max in [(self.ax1, y1_min, y1_max), (self.ax2, y2_min, y2_max)]:
                    end_line = ax.axvline(x=end_time, color='red', linestyle=':', linewidth=1, alpha=0.7)
                    end_line._is_measurement_marker = True
                    
                    # Add session number text at the top
                    text = ax.text(end_time, y_max * 0.95, f"#{session_number}", 
                                 color='red', fontsize=8, ha='center', va='top')
                    text._is_measurement_marker = True
                    
                    # Draw horizontal connecting line (black) only if both start and end are visible
                    if start_time >= cutoff_time and start_time <= now and start_time != end_time:
                        for ax, y_min, y_max in [(self.ax1, y1_min, y1_max), (self.ax2, y2_min, y2_max)]:
                            # Draw horizontal line at the top
                            h_line = ax.plot([start_time, end_time], [y_max * 0.9, y_max * 0.9], 
                                           color='green', linewidth=1, alpha=0.5)[0]
                            h_line._is_measurement_marker = True
                            
        except Exception as e:
            logger.error(f"Failed to draw session markers: {e}")
    
    def clear_plot(self):
        """Clear all data from the plot."""
        self.measurements.clear()
        self.measurement_sessions.clear()
        self.current_session_number = 0
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
