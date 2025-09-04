#!/usr/bin/env python3
"""
Script to restart the data collector with updated code.
This will stop any running data collector processes and start a fresh one.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def stop_data_collector_processes():
    """Stop any running data collector processes."""
    try:
        # Find and kill Python processes running start_data_collector.py
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True, text=True, shell=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                if 'start_data_collector.py' in line or 'CO_O2Analyser' in line:
                    # Extract PID and kill the process
                    parts = line.split(',')
                    if len(parts) > 1:
                        pid = parts[1].strip('"')
                        try:
                            subprocess.run(['taskkill', '/PID', pid, '/F'], check=True)
                            print(f"Stopped process PID: {pid}")
                        except subprocess.CalledProcessError:
                            pass
        
        print("Data collector processes stopped.")
        return True
        
    except Exception as e:
        print(f"Error stopping processes: {e}")
        return False

def start_data_collector():
    """Start the data collector with updated code."""
    try:
        # Get the path to start_data_collector.py
        project_root = Path(__file__).parent
        collector_script = project_root / "start_data_collector.py"
        
        # Use the virtual environment Python
        venv_python = project_root / "venv" / "Scripts" / "python.exe"
        if venv_python.exists():
            python_executable = str(venv_python)
        else:
            python_executable = sys.executable
        
        print(f"Starting data collector with: {python_executable}")
        print(f"Script: {collector_script}")
        
        # Start the process
        process = subprocess.Popen(
            [python_executable, str(collector_script)],
            cwd=str(project_root)
        )
        
        print(f"Data collector started with PID: {process.pid}")
        return process
        
    except Exception as e:
        print(f"Error starting data collector: {e}")
        return None

def main():
    """Main function to restart the data collector."""
    print("Restarting CO_O2Analyser data collector...")
    print("=" * 50)
    
    # Step 1: Stop existing processes
    print("1. Stopping existing data collector processes...")
    stop_data_collector_processes()
    
    # Wait a moment for processes to stop
    time.sleep(2)
    
    # Step 2: Start fresh data collector
    print("2. Starting fresh data collector with updated code...")
    process = start_data_collector()
    
    if process:
        print("✅ Data collector restarted successfully!")
        print("The TagList will now be updated from the instrument URL on startup.")
        print("Check the logs to see the database update process.")
    else:
        print("❌ Failed to restart data collector.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
