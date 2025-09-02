#!/usr/bin/env python3
"""
Test script for database recreation functionality.

This script tests the enhanced database recreation with the new JSON format
from the /api/taglist endpoint.
"""

import json
import sqlite3
from pathlib import Path
from recreate_database import DynamicDatabaseRecreator

def test_database_recreation():
    """Test the database recreation functionality."""
    print("🧪 Testing Database Recreation Functionality")
    print("=" * 50)
    
    # Test with sample data from the tag_list.json
    sample_taglist = {
        "group": "",
        "tags": [
            {
                "name": "INSTRUMENT_TIME",
                "type": "string",
                "value": "09/01/2025 16:22:11",
                "properties": "{\"Default\":\"\",\"Name\":\"INSTRUMENT_TIME\",\"HmiLabel\":\"Instrument Time\",\"Description\":\"Current time on the instrument\",\"Group\":\"\",\"Units\":\"\",\"IsValueValid\":true,\"IsReadOnly\":false,\"IsNetwork\":true,\"IsVisible\":true,\"IsNonVolatile\":false,\"IsDashboard\":false,\"CanDashboard\":false,\"CANNodeID\":-1,\"CANDataID\":-1}"
            },
            {
                "name": "ACTION_PROGRESS_PERCENT",
                "type": "int",
                "value": "100",
                "properties": "{\"RawMin\":0,\"RawMax\":100,\"EuMin\":0,\"EuMax\":100,\"EuTag\":\"\",\"Default\":100,\"Name\":\"ACTION_PROGRESS_PERCENT\",\"HmiLabel\":\"Current action progress percent\",\"Description\":\"Percentage complete for the current action\",\"Group\":\"TRACK_ALL_UPDATES\",\"Units\":\"%\",\"IsValueValid\":true,\"IsReadOnly\":false,\"IsNetwork\":true,\"IsVisible\":true,\"IsNonVolatile\":false,\"IsDashboard\":true,\"CanDashboard\":false,\"CANNodeID\":-1,\"CANDataID\":-1}"
            },
            {
                "name": "SV_SYSTEM_TOTAL_HOURS",
                "type": "float",
                "value": "0",
                "properties": "{\"Precision\":3,\"RawMin\":0.0,\"RawMax\":500000.0,\"EuMin\":0.0,\"EuMax\":500000.0,\"EuTag\":\"\",\"Default\":0.0,\"Name\":\"SV_SYSTEM_TOTAL_HOURS\",\"HmiLabel\":\"System Hours\",\"Description\":\"Total system runtime hours\",\"Group\":\"CFG\",\"Units\":\"HOURS\",\"IsValueValid\":true,\"IsReadOnly\":false,\"IsNetwork\":true,\"IsVisible\":true,\"IsNonVolatile\":true,\"IsDashboard\":true,\"CanDashboard\":true,\"CANNodeID\":-1,\"CANDataID\":-1}"
            }
        ]
    }
    
    print(f"📊 Sample data contains {len(sample_taglist['tags'])} tags")
    
    # Test the properties parsing
    recreator = DynamicDatabaseRecreator()
    
    print("\n🔍 Testing properties parsing...")
    for tag in sample_taglist['tags']:
        properties = recreator.parse_properties(tag.get('properties', '{}'))
        print(f"  Tag: {tag['name']}")
        print(f"    Description: {properties.get('Description', 'N/A')}")
        print(f"    Units: {properties.get('Units', 'N/A')}")
        print(f"    Group: {properties.get('Group', 'N/A')}")
        print(f"    RawMin: {properties.get('RawMin', 'N/A')}")
        print(f"    RawMax: {properties.get('RawMax', 'N/A')}")
        print()
    
    # Test database creation with sample data
    print("🗄️ Testing database creation...")
    
    # Create a test database
    test_db_path = "test_tags.sqlite"
    original_db_path = recreator.db_path
    recreator.db_path = test_db_path
    
    try:
        # Create database structure
        if recreator.create_database_structure():
            print("✅ Database structure created successfully")
            
            # Populate with sample tags
            if recreator.populate_tag_list(sample_taglist['tags']):
                print("✅ Sample tags populated successfully")
                
                # Verify database
                if recreator.verify_database():
                    print("✅ Database verification passed")
                    
                    # Show sample data from database
                    print("\n📋 Sample data from database:")
                    conn = sqlite3.connect(test_db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("SELECT Name, Type, Description, Units, TagGroup, RawMin, RawMax FROM TagList")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        print(f"  {row[0]} ({row[1]}) - {row[2]}")
                        print(f"    Units: {row[3]}, Group: {row[4]}")
                        print(f"    Range: {row[5]} to {row[6]}")
                        print()
                    
                    conn.close()
                else:
                    print("❌ Database verification failed")
            else:
                print("❌ Failed to populate sample tags")
        else:
            print("❌ Failed to create database structure")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
    
    finally:
        # Cleanup test database
        if Path(test_db_path).exists():
            Path(test_db_path).unlink()
            print(f"🧹 Cleaned up test database: {test_db_path}")
        
        # Restore original database path
        recreator.db_path = original_db_path
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    test_database_recreation()
