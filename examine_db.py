#!/usr/bin/env python3
"""
Script to examine the tags.sqlite database structure and data.
"""

import sqlite3
import os

def examine_database(db_path):
    """Examine the database structure and sample data."""
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get detailed data for CO_CONC and O2_CONC tags
        co_tag_id = 398  # CO_CONC
        o2_tag_id = 705  # O2_CONC
        
        print(f"Getting recent data for CO_CONC (ID: {co_tag_id})...")
        cursor.execute("""
            SELECT Value, DateTime 
            FROM TagValues 
            WHERE TagName_id = ? 
            ORDER BY DateTime DESC 
            LIMIT 20
        """, (co_tag_id,))
        co_values = cursor.fetchall()
        
        print(f"CO_CONC values (last 20):")
        for value in co_values:
            print(f"  {value[1]}: {value[0]} ppm")
        
        print(f"\nGetting recent data for O2_CONC (ID: {o2_tag_id})...")
        cursor.execute("""
            SELECT Value, DateTime 
            FROM TagValues 
            WHERE TagName_id = ? 
            ORDER BY DateTime DESC 
            LIMIT 20
        """, (o2_tag_id,))
        o2_values = cursor.fetchall()
        
        print(f"O2_CONC values (last 20):")
        for value in o2_values:
            print(f"  {value[1]}: {value[0]} %")
        
        # Get some statistics
        print(f"\nCalculating statistics...")
        cursor.execute("""
            SELECT 
                MIN(CAST(Value AS FLOAT)) as min_val,
                MAX(CAST(Value AS FLOAT)) as max_val,
                AVG(CAST(Value AS FLOAT)) as avg_val,
                COUNT(*) as count
            FROM TagValues 
            WHERE TagName_id = ? AND Value != ''
        """, (co_tag_id,))
        co_stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                MIN(CAST(Value AS FLOAT)) as min_val,
                MAX(CAST(Value AS FLOAT)) as max_val,
                AVG(CAST(Value AS FLOAT)) as avg_val,
                COUNT(*) as count
            FROM TagValues 
            WHERE TagName_id = ? AND Value != ''
        """, (o2_tag_id,))
        o2_stats = cursor.fetchone()
        
        print(f"\nCO_CONC Statistics:")
        print(f"  Min: {co_stats[0]:.2f} ppm")
        print(f"  Max: {co_stats[1]:.2f} ppm")
        print(f"  Avg: {co_stats[2]:.2f} ppm")
        print(f"  Count: {co_stats[3]}")
        
        print(f"\nO2_CONC Statistics:")
        print(f"  Min: {o2_stats[0]:.2f} %")
        print(f"  Max: {o2_stats[1]:.2f} %")
        print(f"  Avg: {o2_stats[2]:.2f} %")
        print(f"  Count: {o2_stats[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error examining database: {e}")

if __name__ == "__main__":
    db_path = r"E:\Documents\PythonProjects\CO_O2Analyser\CO_O2Analyser\tags.sqlite"
    examine_database(db_path)
