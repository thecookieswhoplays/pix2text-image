FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Pix2Text with HTTP server support
RUN pip install --no-cache-dir pix2text[serve]

# For multilingual support (uncomment if needed)
# RUN pip install --no-cache-dir pix2text[multilingual]

# Expose the port the app runs on
EXPOSE 8503

# Command to run the app
CMD ["p2t", "serve", "-p", "8503", "-H", "0.0.0.0"]
