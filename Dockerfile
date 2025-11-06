# Use an official Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create and switch to /app
WORKDIR /app

# Copy everything into the container
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose a port (for clarity only)
EXPOSE 8000

# Debug: show files and sleep for a while
CMD ["sh", "-c", "echo 'Container started ✅'; pwd; ls -la; sleep 600"]
