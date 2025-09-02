#!/usr/bin/env python3
"""
Quick Database Recreation Script

This script quickly recreates the tags.sqlite database using the current
instrument settings (192.168.1.1:8180) without user input.
"""

import requests
import sqlite3
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def recreate_database():
    """Recreate the database with current instrument tags."""
    
    # Instrument settings
    instrument_ip = "192.168.1.1"
    instrument_port = "8180"
    valuelist_url = f"http://{instrument_ip}:{instrument_port}/api/valuelist"
    db_path = "tags.sqlite"
    
    print(f"🔄 Recreating database from instrument at {instrument_ip}:{instrument_port}")
    
    try:
        # Step 1: Backup existing database
        if Path(db_path).exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"tags_backup_{timestamp}.sqlite"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backed up existing database to: {backup_path}")
        
        # Step 2: Fetch current valuelist from instrument
        print(f"📡 Fetching current valuelist from: {valuelist_url}")
        response = requests.get(valuelist_url, timeout=30)
        response.raise_for_status()
        
        # Parse JSON content
        json_content = response.text
        print(f"📊 Received valuelist with {len(json_content)} characters")
        
        # Parse JSON to get all tags
        tags = []
        try:
            import json
            data = json.loads(json_content)
            
            if 'values' in data and isinstance(data['values'], list):
                for item in data['values']:
                    if isinstance(item, dict) and 'name' in item:
                        tag_name = item['name'].strip()
                        if tag_name:  # Only add non-empty tag names
                            tags.append(tag_name)
            else:
                print("⚠️  Warning: Unexpected JSON structure in valuelist")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return False
        
        print(f"🏷️  Found {len(tags)} tags in current valuelist")
        
        # Step 3: Create new database structure
        print("🗄️  Creating database structure...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        cursor.execute("DROP TABLE IF EXISTS TagValues")
        cursor.execute("DROP TABLE IF EXISTS TagList")
        
        # Create TagList table
        cursor.execute("""
            CREATE TABLE TagList (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT UNIQUE NOT NULL,
                Description TEXT,
                Unit TEXT,
                DataType TEXT,
                MinValue REAL,
                MaxValue REAL,
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create TagValues table
        cursor.execute("""
            CREATE TABLE TagValues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                TagName_id INTEGER NOT NULL,
                Value TEXT,
                DateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                Quality TEXT DEFAULT 'GOOD',
                FOREIGN KEY (TagName_id) REFERENCES TagList (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tagvalues_tagname ON TagValues(TagName_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tagvalues_datetime ON TagValues(DateTime)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_taglist_name ON TagList(Name)")
        
        # Step 4: Populate with current tags
        print(f"📝 Inserting {len(tags)} tags into database...")
        for tag_name in tags:
            try:
                cursor.execute("""
                    INSERT INTO TagList (Name, Description, Unit, DataType)
                    VALUES (?, ?, ?, ?)
                """, (tag_name, f"Tag: {tag_name}", "", "REAL"))
            except Exception as e:
                print(f"⚠️  Warning: Failed to insert tag {tag_name}: {e}")
        
        conn.commit()
        conn.close()
        
        # Step 5: Verify database
        print("✅ Verifying database...")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM TagList")
        tag_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TagValues'")
        tagvalues_exists = cursor.fetchone() is not None
        
        db_size = Path(db_path).stat().st_size
        
        conn.close()
        
        print(f"📊 Database verification:")
        print(f"  - TagList records: {tag_count}")
        print(f"  - TagValues table exists: {tagvalues_exists}")
        print(f"  - Database file size: {db_size} bytes")
        
        if tag_count > 0 and tagvalues_exists and db_size > 0:
            print("\n🎉 SUCCESS: Database has been recreated with current instrument tags!")
            print(f"📈 Total tags: {tag_count}")
            print("💡 You can now start the data collection service to begin harvesting data.")
            return True
        else:
            print("\n❌ FAILED: Database verification failed.")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to instrument: {e}")
        print("💡 Please check:")
        print("   - Instrument is powered on and connected to network")
        print("   - IP address is correct (currently: 192.168.1.1)")
        print("   - Port is correct (currently: 8180)")
        print("   - Network connection is working")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Quick Database Recreation Tool")
    print("=" * 50)
    
    success = recreate_database()
    
    if success:
        print("\n✅ Ready to start data collection!")
    else:
        print("\n❌ Database recreation failed. Please check the errors above.")
        exit(1)
