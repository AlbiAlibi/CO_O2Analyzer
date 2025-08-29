import json
import sqlite3
from datetime import datetime
import time
import requests
import os

class InstrumentConnection:
    def __init__(self):
        # URL for general tag list data. Adjust as needed.
        self.instrument_url = "http://192.168.1.1:8180/api/valuelist"
        # URLs for individual concentration values.
        self.conc_urls = [
            "http://192.168.1.1:8180/api/tag/CO_CONC/value",
            "http://192.168.1.1:8180/api/tag/O2_CONC/value"
        ]
        self.db_file = "tags.sqlite"
        self.status_file = "analyser_status.txt"
        self.connected = False
        # Ensure the SQLite database and tables are created.
        self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TagList (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT,
                value TEXT,
                properties TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TagValues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                TagName_id INTEGER,
                Value TEXT,
                DateTime TEXT,
                FOREIGN KEY (TagName_id) REFERENCES TagList(id)
            )
        ''')
        conn.commit()
        conn.close()

    def update_status(self, status):
        """
        Appends the provided status string with a timestamp to the status file.
        This file is read by main_gui.py to update the Connect button's appearance,
        and previous log entries will be preserved.
        """
        if status == "CONNECTED":
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(self.status_file, "a") as f:
                    f.write(f"---{timestamp}---\n{status}\n")
            except Exception as e:
                 print("Error writing status file:", e)
        else:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(self.status_file, "a") as f:
                    f.write(f"{timestamp} - {status}\n")
            except Exception as e:
                print("Error writing status file:", e)
                

    def get_api_data(self, url):
        """
        Performs a GET request to the provided URL and returns the parsed JSON.
        Prints the request time.
        """
        start_time = time.time()
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        elapsed_time = time.time() - start_time
        print(f"Request to {url} took {elapsed_time:.3f} seconds")
        return data

    def connect_instrument(self):
        """
        Attempts to contact the instrument by fetching data from instrument_url.
        If successful, updates the status file with "CONNECTED".
        Otherwise, saves detailed error information.
        """
        try:
            data = self.get_api_data(self.instrument_url)
            # Only update status if we weren't connected before
            if not self.connected:
                self.connected = True
                self.update_status("CONNECTED")
                print("Instrument connected.")
            return True
        except Exception as e:
            error_msg = f"ERROR: {str(e)}"
            print("Connection error:", error_msg)
            self.connected = False
            self.update_status(error_msg)
            return False

    def insert_tag_value(self, data):
        """
        Inserts tag values from the JSON data into the TagValues table.
        Assumes that the TagList table already contains the tag names.
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            for value in data.get("values", []):
                tag_name = value.get("name")
                cursor.execute('SELECT id FROM TagList WHERE name = ?', (tag_name,))
                result = cursor.fetchone()
                if result:
                    tag_id = result[0]
                    cursor.execute('''
                        INSERT INTO TagValues (TagName_id, Value, DateTime)
                        VALUES (?, ?, ?)
                    ''', (tag_id, value.get("value"), current_time))
            conn.commit()
            conn.close()
        except Exception as e:
            error_msg = f"ERROR while inserting tag values: {str(e)}"
            print(error_msg)
            self.update_status(error_msg)

    def insert_conc_tag_value(self, data, current_time, cursor):
        """
        Inserts concentration tag values into the TagValues table.
        This method is meant to be used within an existing database transaction.
        """
        tag_name = data.get("name")
        cursor.execute('SELECT id FROM TagList WHERE name = ?', (tag_name,))
        result = cursor.fetchone()
        if result:
            tag_id = result[0]
            cursor.execute('''
                INSERT INTO TagValues (TagName_id, Value, DateTime)
                VALUES (?, ?, ?)
            ''', (tag_id, data.get("value"), current_time))

    def run(self):
        """
        Main loop for connecting to the instrument and collecting data continuously.
        First, it tries to establish a connection. If the connection fails, the process will exit.
        Once connected, it enters a loop that fetches data from the instrument and concentration endpoints,
        updating the database and the status file with detailed error messages if issues occur.
        """
        print("Attempting to connect to the instrument...")
        if not self.connect_instrument():
            print("Failed to connect to the instrument. Exiting.")
            return
        
        while True:
            #try:
            # Fetch general tag values and store them.
            data = self.get_api_data(self.instrument_url)
            self.insert_tag_value(data)
            counter = 0
            while counter <= 200:
                # For concentration values, open a transaction and insert values.
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                for url_con in self.conc_urls:
                    data_con = self.get_api_data(url_con)
                    self.insert_conc_tag_value(data_con, current_time, cursor)
                conn.commit()
                conn.close()
                counter += 1
                time.sleep(2)
            
            # Re-check the instrument status to update if necessary.
            self.connect_instrument()
                                
            """ except Exception as e:
                error_msg = f"ERROR during data collection: {str(e)}"
                print(error_msg)
                self.update_status(error_msg)
                time.sleep(2) """

if __name__ == "__main__":
    conn_obj = InstrumentConnection()
    conn_obj.run()