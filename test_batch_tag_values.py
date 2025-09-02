#!/usr/bin/env python3
"""
Test script for batch tag value retrieval using the Teledyne N300M API.

This script demonstrates how to use the /api/valuelist endpoint to get all tag values
in one request instead of querying each tag individually. This is much more efficient
for real-time monitoring applications.

Based on the TAPI Tag REST Interface documentation, the /api/valuelist endpoint
returns all tag values in a single JSON response.

Usage:
    python test_batch_tag_values.py [instrument_ip] [port]
    
Example:
    python test_batch_tag_values.py 192.168.1.100 8180
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Optional, Dict, List

class BatchTagValueTester:
    """Test class for batch tag value retrieval."""
    
    def __init__(self, instrument_ip: str = "192.168.1.1", port: int = 8180):
        self.base_url = f"http://{instrument_ip}:{port}/api"
        self.session = requests.Session()
        self.session.timeout = 5  # 5 second timeout
        
    def test_connection(self) -> bool:
        """Test basic connection to the instrument."""
        try:
            response = self.session.get(f"{self.base_url}/taglist")
            if response.status_code == 200:
                print(f"✅ Connection successful to {self.base_url}")
                return True
            else:
                print(f"❌ Connection failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_available_tags(self) -> Optional[List[str]]:
        """Get list of available tags from the instrument."""
        try:
            response = self.session.get(f"{self.base_url}/taglist")
            if response.status_code == 200:
                data = response.json()
                tags = [tag['name'] for tag in data.get('tags', [])]
                print(f"📋 Found {len(tags)} available tags")
                return tags
            else:
                print(f"❌ Failed to get tag list: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting tag list: {e}")
            return None
    
    def test_batch_tag_values(self, group: Optional[str] = None) -> Optional[Dict]:
        """Test the batch tag value retrieval endpoint."""
        try:
            # Build URL with optional group filter
            url = f"{self.base_url}/valuelist"
            if group:
                url += f"?group={group}"
            
            print(f"🔄 Testing batch tag values endpoint: {url}")
            
            start_time = time.time()
            response = self.session.get(url)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
                print(f"✅ Batch request successful!")
                print(f"   Response time: {response_time:.2f} ms")
                print(f"   Tags received: {len(values)}")
                print(f"   Group: {data.get('group', 'all')}")
                return data
            else:
                print(f"❌ Batch request failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error in batch request: {e}")
            return None
    
    def test_individual_tag_values(self, tags: List[str], max_tags: int = 5) -> float:
        """Test individual tag value requests for comparison."""
        if not tags:
            return 0.0
            
        # Limit the number of tags to test for performance comparison
        test_tags = tags[:max_tags]
        print(f"🔄 Testing individual tag requests for {len(test_tags)} tags...")
        
        total_time = 0.0
        successful_requests = 0
        
        for tag in test_tags:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/tag/{tag}/value")
                end_time = time.time()
                
                if response.status_code == 200:
                    request_time = (end_time - start_time) * 1000
                    total_time += request_time
                    successful_requests += 1
                    print(f"   {tag}: {request_time:.2f} ms")
                else:
                    print(f"   {tag}: Failed (HTTP {response.status_code})")
                    
            except Exception as e:
                print(f"   {tag}: Error - {e}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"📊 Individual requests average: {avg_time:.2f} ms")
            return avg_time
        return 0.0
    
    def simulate_real_time_monitoring(self, interval: float = 1.5):
        """Simulate real-time monitoring with batch requests."""
        print(f"\n🚀 Starting real-time monitoring simulation (every {interval} seconds)")
        print("Press Ctrl+C to stop...")
        print("-" * 60)
        
        try:
            while True:
                start_time = time.time()
                
                # Get batch values
                batch_data = self.test_batch_tag_values()
                if batch_data:
                    values = batch_data.get('values', [])
                    current_time = datetime.now().strftime("%H:%M:%S")
                    
                    # Display some key values (first 5)
                    print(f"[{current_time}] Batch: {len(values)} tags")
                    for i, value in enumerate(values[:5]):
                        print(f"   {value['name']}: {value['value']}")
                    if len(values) > 5:
                        print(f"   ... and {len(values) - 5} more tags")
                
                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of all functionality."""
        print("🧪 CO_O2Analyser Batch Tag Values Test")
        print("=" * 50)
        
        # Test 1: Connection
        if not self.test_connection():
            print("❌ Cannot proceed without connection")
            return False
        
        print()
        
        # Test 2: Get available tags
        tags = self.get_available_tags()
        if not tags:
            print("❌ Cannot proceed without tag list")
            return False
        
        print()
        
        # Test 3: Test batch endpoint
        batch_data = self.test_batch_tag_values()
        if not batch_data:
            print("❌ Batch endpoint test failed")
            return False
        
        print()
        
        # Test 4: Performance comparison
        print("📊 Performance Comparison")
        print("-" * 30)
        
        # Test batch performance
        batch_start = time.time()
        for _ in range(5):  # Test 5 batch requests
            self.test_batch_tag_values()
        batch_total = (time.time() - batch_start) * 1000
        batch_avg = batch_total / 5
        
        print(f"Batch requests (5x): {batch_avg:.2f} ms average")
        
        # Test individual performance
        individual_avg = self.test_individual_tag_values(tags)
        if individual_avg > 0:
            improvement = ((individual_avg * len(tags)) - batch_avg) / (individual_avg * len(tags)) * 100
            print(f"Individual requests: {individual_avg:.2f} ms average per tag")
            print(f"Performance improvement: {improvement:.1f}%")
        
        print()
        
        # Test 5: Group filtering
        print("🔍 Testing group filtering...")
        batch_data_msr = self.test_batch_tag_values(group="msr")
        if batch_data_msr:
            values = batch_data_msr.get('values', [])
            print(f"   MSR group: {len(values)} tags")
        
        return True

def main():
    """Main function."""
    # Parse command line arguments
    instrument_ip = "192.168.1.1"
    port = 8180
    
    if len(sys.argv) > 1:
        instrument_ip = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("❌ Invalid port number")
            sys.exit(1)
    
    print(f"🎯 Testing instrument at {instrument_ip}:{port}")
    print()
    
    # Create tester and run tests
    tester = BatchTagValueTester(instrument_ip, port)
    
    if tester.run_comprehensive_test():
        print("✅ All tests completed successfully!")
        print()
        
        # Ask user if they want to start real-time monitoring
        try:
            response = input("🚀 Start real-time monitoring simulation? (y/n): ").lower()
            if response in ['y', 'yes']:
                tester.simulate_real_time_monitoring()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
