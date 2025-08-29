#!/usr/bin/env python3
# instr_simulator.py
#
# Writes synthetic TagValues rows every 2 s.
# Each new value = previous value ±1 %.

import argparse
import random
import sqlite3
import sys
import time
from datetime import datetime

# -------------------------------- helpers ---------------------------------- #

def iso_now() -> str:
    """Return current timestamp like 2024-12-18 14:21:37.997 (millis)."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

def get_last_value(cur, tag_id: int, default: float) -> float:
    """Fetch most recent value for tag or use default."""
    cur.execute(
        "SELECT Value FROM TagValues WHERE TagName_id=? ORDER BY id DESC LIMIT 1",
        (tag_id,),
    )
    row = cur.fetchone()
    return float(row[0]) if row else default

def next_value(prev: float) -> float:
    """±1 % random drift."""
    return prev * (1 + random.uniform(-0.005, 0.005))

# --------------------------------- main ------------------------------------ #

def run(db_path: str, interval: float = 2.0):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Ensure table exists (harmless if it already does)
    cur.execute(
        """CREATE TABLE IF NOT EXISTS TagValues(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                TagName_id INTEGER,
                Value TEXT,
                DateTime TEXT
           )"""
    )
    conn.commit()

    # tag_id -> starting value if table is empty
    seeds = {398: 5.2, 705: 21.5}
    last_vals = {tid: get_last_value(cur, tid, seeds[tid]) for tid in seeds}

    print("Simulating…  Ctrl-C to stop.")
    try:
        while True:
            ts = iso_now()
            for tid in (398, 705):
                val = next_value(last_vals[tid])
                cur.execute(
                    "INSERT INTO TagValues(TagName_id,Value,DateTime) VALUES(?,?,?)",
                    (tid, val, ts),
                )
                last_vals[tid] = val
            conn.commit()
            time.sleep(interval)     
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        conn.close()

# ------------------------------ entry point -------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab-instrument DB simulator")
    parser.add_argument(
        "db", nargs="?", default="tags.sqlite", help="SQLite file (default: tags.sqlite)"
    )
    parser.add_argument(
        "-i", "--interval", type=float, default=2.0, help="Seconds between inserts (default: 2)"
    )
    args = parser.parse_args()

    run(args.db, args.interval)