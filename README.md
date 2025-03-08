THIS IS 100% AI I HATE MAKING IMAGES

# Pix2Text Docker Server

This Docker image sets up a Pix2Text server that can recognize layouts, tables, math formulas (LaTeX), and text in images, converting them into Markdown format. It's a free alternative to Mathpix.

## Features

- Text recognition in 80+ languages
- Mathematical formula recognition
- Layout analysis
- Table recognition
- Conversion of images to Markdown format

## Building and Running

### Using Docker Compose (Recommended)

The easiest way to run the server is with Docker Compose:

```bash
docker-compose up -d
```

This will:
- Build the Docker image
- Start the container in the background
- Map port 8503 to your host
- Create persistent volumes for the models

To stop the server:

```bash
docker-compose down
```

### Using Docker Directly

#### Building the Docker Image

```bash
docker build -t pix2text-server .
```

#### Running the Container

```bash
docker run -p 8503:8503 pix2text-server
```

This will start the Pix2Text server on port 8503.

## Testing the Server

You can use the included test script to verify that the server is running correctly:

```bash
# Install the required packages
pip install requests

# Run the test script
python test_server.py

# Customize the test parameters
python test_server.py --url http://localhost:8503 --retries 15 --interval 10
```

## Using the Server

### Using the Example Script

This repository includes an example script `example.py` that demonstrates how to use the server:

```bash
# Install the required packages
pip install requests

# Run the script with a local image file
python example.py path/to/your/image.jpg

# Run the script with an image URL
python example.py https://example.com/path/to/image.jpg

# Save the output to a file
python example.py path/to/your/image.jpg --output results.json
```

### Using cURL

```bash
# With a local image file
curl -F image=@path/to/your/image.jpg --form 'use_analyzer=true' --form 'resized_shape=600' http://localhost:8503/pix2text

# With an image URL (requires downloading the image first)
curl -o temp_image.jpg https://example.com/path/to/image.jpg
curl -F image=@temp_image.jpg --form 'use_analyzer=true' --form 'resized_shape=600' http://localhost:8503/pix2text
```

### Using Python

```python
import requests
import tempfile
import os

def recognize_from_url(image_url, server_url='http://localhost:8503/pix2text'):
    # Download the image
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    
    # Save to a temporary file
    temp_file = None
    try:
        fd, temp_file = tempfile.mkstemp(suffix='.jpg')
        with os.fdopen(fd, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        
        # Send to Pix2Text server
        data = {
            "use_analyzer": True,
            "resized_shape": 608,
            "embed_sep": " $,$ ",
            "isolated_sep": "$$\n, \n$$"
        }
        files = {
            "image": (os.path.basename(temp_file), open(temp_file, 'rb'))
        }
        
        r = requests.post(server_url, data=data, files=files)
        files["image"][1].close()
        
        outs = r.json()['results']
        only_text = '\n'.join([out['text'] for out in outs])
        return only_text
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)

# Example usage
text = recognize_from_url('https://example.com/path/to/image.jpg')
print(f'Recognized text: {text}')
```

## Customization

### Multilingual Support

To enable support for languages other than English and Simplified Chinese, uncomment the following line in the Dockerfile:

```dockerfile
# RUN pip install --no-cache-dir pix2text[multilingual]
```

Then rebuild the Docker image:

```bash
docker-compose build
docker-compose up -d
```

## First Run

On the first run, the server will download the necessary models, which may take some time depending on your internet connection. The models are stored in Docker volumes, so they will persist between container restarts.

## References

- [Pix2Text GitHub Repository](https://github.com/breezedeus/Pix2Text)
- [Pix2Text Documentation](https://p2t.breezedeus.com) 