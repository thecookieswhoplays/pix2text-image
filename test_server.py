#!/usr/bin/env python3
"""
Test script to verify the Pix2Text server is working correctly.
"""

import requests
import time
import sys
import argparse


def check_server(url, max_retries=10, retry_interval=5):
    """
    Check if the Pix2Text server is running and responding.
    
    Args:
        url (str): The base URL of the server
        max_retries (int): Maximum number of retry attempts
        retry_interval (int): Time to wait between retries in seconds
        
    Returns:
        bool: True if the server is running, False otherwise
    """
    for attempt in range(max_retries):
        try:
            # Try to access the server's root endpoint
            response = requests.get(f"{url}")
            
            if response.status_code == 200:
                print(f"✅ Server is running at {url}")
                return True
            else:
                print(f"⚠️ Server returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt + 1}/{max_retries}: Server not responding ({str(e)})")
        
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
    
    print(f"❌ Server is not running at {url} after {max_retries} attempts")
    return False


def main():
    parser = argparse.ArgumentParser(description="Test if the Pix2Text server is running")
    parser.add_argument("--url", default="http://localhost:8503", help="Base URL of the Pix2Text server")
    parser.add_argument("--retries", type=int, default=10, help="Maximum number of retry attempts")
    parser.add_argument("--interval", type=int, default=5, help="Time to wait between retries in seconds")
    
    args = parser.parse_args()
    
    if check_server(args.url, args.retries, args.interval):
        print("\nServer test successful! You can now use the Pix2Text server.")
        sys.exit(0)
    else:
        print("\nServer test failed. Please check if the server is running correctly.")
        sys.exit(1)


if __name__ == "__main__":
    main() 