#!/usr/bin/env python3
"""
Example script to demonstrate how to use the Pix2Text server.
"""

import argparse
import requests
import json
import tempfile
import os
from pathlib import Path
from urllib.parse import urlparse


def is_url(string):
    """
    Check if a string is a URL.
    
    Args:
        string (str): The string to check
        
    Returns:
        bool: True if the string is a URL, False otherwise
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except:
        return False


def download_image(url):
    """
    Download an image from a URL.
    
    Args:
        url (str): The URL of the image
        
    Returns:
        str: Path to the downloaded image
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Check if the content type is an image
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            print(f"Warning: URL may not point to an image (Content-Type: {content_type})")
        
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.jpg')
        
        # Write the image to the temporary file
        with os.fdopen(fd, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        return temp_path
    except Exception as e:
        raise Exception(f"Failed to download image from URL: {e}")


def recognize_image(image_path_or_url, server_url="http://localhost:8503/pix2text"):
    """
    Send an image to the Pix2Text server for recognition.
    
    Args:
        image_path_or_url (str): Path to the image file or URL of the image
        server_url (str): URL of the Pix2Text server
        
    Returns:
        dict: The recognition results
    """
    temp_file = None
    
    try:
        # Check if the input is a URL
        if is_url(image_path_or_url):
            print(f"Downloading image from URL: {image_path_or_url}")
            temp_file = download_image(image_path_or_url)
            image_path = temp_file
        else:
            image_path = Path(image_path_or_url)
            
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Prepare the request
        data = {
            "use_analyzer": True,
            "resized_shape": 608,
            "embed_sep": " $,$ ",
            "isolated_sep": "$$\n, \n$$"
        }
        
        files = {
            "image": (os.path.basename(image_path), open(image_path, 'rb'))
        }
        
        # Send the request
        try:
            response = requests.post(server_url, data=data, files=files)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the response
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error sending request to server: {e}")
            return None
        finally:
            files["image"][1].close()  # Close the file
    
    finally:
        # Clean up the temporary file if it was created
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


def main():
    parser = argparse.ArgumentParser(description="Recognize text and formulas in an image using Pix2Text server")
    parser.add_argument("image", help="Path to the image file or URL of the image")
    parser.add_argument("--server", default="http://localhost:8503/pix2text", help="URL of the Pix2Text server")
    parser.add_argument("--output", help="Path to save the output JSON")
    
    args = parser.parse_args()
    
    # Recognize the image
    result = recognize_image(args.image, args.server)
    
    if result:
        # Extract just the text
        if 'results' in result:
            try:
                # Handle different response formats
                if isinstance(result['results'], list):
                    # If results is a list of dictionaries with 'text' keys
                    if all(isinstance(item, dict) and 'text' in item for item in result['results']):
                        only_text = '\n'.join([out['text'] for out in result['results']])
                    # If results is a list of strings
                    else:
                        only_text = '\n'.join(result['results'])
                # If results is a single string
                elif isinstance(result['results'], str):
                    only_text = result['results']
                # If results is a dictionary
                elif isinstance(result['results'], dict):
                    only_text = json.dumps(result['results'], ensure_ascii=False, indent=2)
                else:
                    only_text = str(result['results'])
                
                print("\n=== Recognized Text ===")
                print(only_text)
            except Exception as e:
                print(f"Error processing results: {e}")
                print("Raw results:")
                print(result)
        else:
            print("\n=== Results ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Save the full result to a file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nFull results saved to {args.output}")
        else:
            print("\n=== Full Results ===")
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main() 