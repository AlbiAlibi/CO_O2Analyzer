#!/usr/bin/env python3
"""Check if data is being collected in the database."""

import sqlite3

def check_data():
    """Check if data is being collected."""
    try:
        conn = sqlite3.connect('tags.sqlite')
        cursor = conn.cursor()
        
        # Check total records
        cursor.execute('SELECT COUNT(*) FROM TagValues')
        total_records = cursor.fetchone()[0]
        
        # Check latest record
        cursor.execute('SELECT MAX(DateTime) FROM TagValues')
        latest_record = cursor.fetchone()[0]
        
        print(f"📊 Database Status:")
        print(f"  Total records: {total_records}")
        print(f"  Latest record: {latest_record}")
        
        if total_records > 0:
            print("\n✅ Data collection is working!")
            
            # Show some recent records
            cursor.execute('''
                SELECT t.Name, v.Value, v.DateTime 
                FROM TagValues v 
                JOIN TagList t ON v.TagName_id = t.id 
                ORDER BY v.DateTime DESC 
                LIMIT 5
            ''')
            recent_records = cursor.fetchall()
            
            print(f"\n📝 Recent records:")
            for record in recent_records:
                print(f"  {record[0]}: {record[1]} at {record[2]}")
        else:
            print("\n❌ No data collected yet.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_data()
