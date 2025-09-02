# 📊 Measurement Session System - User Guide

## 🎯 Overview

The new measurement session system allows you to collect CO and O₂ concentration data for a specific duration (default 10 minutes) and automatically calculate fume limits. Each session creates a separate database file to avoid interference with the main data collection service.

## 🚀 How to Use

### 1. **Start the Application**
```bash
# Activate virtual environment
venv\Scripts\Activate.ps1

# Run the GUI
python main.py
```

### 2. **Start Data Collection Service**
- Click **"Start Data Collection"** button in the toolbar
- This starts the background service that continuously collects data from the Teledyne N300M analyzer
- The service runs independently and stores data in `data.sqlite`

### 3. **Start a Measurement Session**
- Click **"Start Measurement Session"** button in the toolbar
- A dialog will appear asking for the duration (default: 10 minutes)
- Enter the desired duration (1-60 minutes)
- Click OK to start the session

### 4. **During the Session**
- The system automatically collects CO and O₂ data every second
- Each measurement is stored in the session database with:
  - Timestamp
  - CO concentration (ppm)
  - O₂ concentration (%)
  - Temperature (°C)
  - Pressure/Flow rate
  - **Fume limit (mg/m³)** - automatically calculated
  - **Percentage to limit** - percentage of 500 mg/m³ limit
  - **Air quality status** - Fresh Air/Industrial Exhaust/Invalid O₂

### 5. **Session Completion**
- The session automatically stops after the specified duration
- A completion dialog shows the database path
- Data is saved to `measurements/measurement{DDmmYY}.sqlite`

## 📁 File Structure

```
CO_O2Analyser/
├── data.sqlite                    # Main data collection (continuous)
├── measurements/                  # Measurement session databases
│   ├── measurement020925.sqlite   # Session from 02/09/25
│   ├── measurement030925.sqlite   # Session from 03/09/25
│   └── ...
└── logs/                         # Application logs
```

## 🧮 Fume Limit Calculations

The system automatically calculates fume limits using the same formula as the status widget:

### **Fresh Air Conditions** (O₂ ≥ 18%, CO ≤ 50 ppm):
```
Fume Limit = CO (ppm) × 1.25
```

### **Industrial Exhaust Conditions** (O₂ < 18%):
```
Fume Limit = CO (ppm) × 1.25 × ((21 - 13) / (21 - O₂ %))
```

### **Percentage to Limit**:
```
Percentage = (Fume Limit / 500 mg/m³) × 100%
```

## 📊 Database Schema

### **Session Metadata Table**:
```sql
CREATE TABLE session_metadata (
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_seconds INTEGER,
    total_measurements INTEGER DEFAULT 0
);
```

### **Measurements Table**:
```sql
CREATE TABLE measurements (
    timestamp DATETIME NOT NULL,
    co_concentration REAL,
    o2_concentration REAL,
    temperature REAL,
    pressure REAL,
    fume_limit_mg_m3 REAL,        -- Calculated fume limit
    percentage_to_limit REAL,      -- Percentage to 500 mg/m³ limit
    air_quality_status TEXT        -- Fresh Air/Industrial Exhaust/Invalid O₂
);
```

## 🔧 Key Features

### ✅ **No Interference**
- GUI and data collection service work independently
- Each measurement session gets its own database
- Main data collection continues uninterrupted

### ✅ **Automatic Calculations**
- Fume limits calculated for each measurement
- Percentage to regulatory limit (500 mg/m³)
- Air quality categorization

### ✅ **User-Friendly Interface**
- Simple button interface
- Configurable duration
- Automatic start/stop
- Completion notifications

### ✅ **Data Export**
- Use the Export button to export session data
- CSV format with all calculated values
- Includes fume limits and percentages

## 🧪 Testing

Run the test script to verify everything works:
```bash
# Activate virtual environment
venv\Scripts\Activate.ps1

# Run tests
python test_measurement_system.py
```

## 🚨 Troubleshooting

### **"Start Measurement Session" Button Not Working**
1. Make sure you're running in the virtual environment
2. Check that PyQt6 is installed: `pip list | findstr PyQt6`
3. Look for error messages in the logs

### **No Data Being Collected**
1. Ensure "Start Data Collection" is running first
2. Check that the instrument is connected
3. Verify the data collection service is active

### **Database Creation Issues**
1. Check that the `measurements/` directory exists
2. Ensure write permissions in the project directory
3. Look for database errors in the logs

## 📝 Example Workflow

1. **Start Application**: `python main.py`
2. **Start Data Collection**: Click "Start Data Collection"
3. **Start Measurement Session**: Click "Start Measurement Session"
4. **Enter Duration**: 10 minutes (default)
5. **Wait for Completion**: System automatically stops after 10 minutes
6. **Export Data**: Use Export button to get CSV file
7. **Review Results**: Check `measurements/measurement{DDmmYY}.sqlite`

## 🎉 Benefits

- **Separate Databases**: No interference between systems
- **Automatic Calculations**: Fume limits calculated in real-time
- **Configurable Duration**: 1-60 minutes per session
- **Complete Data**: All measurements with timestamps and calculations
- **Easy Export**: CSV format with all calculated values
- **User-Friendly**: Simple button interface

The system is now ready for professional measurement sessions with automatic fume limit calculations!
