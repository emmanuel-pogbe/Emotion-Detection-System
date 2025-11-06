FROM python:3.11-slim

# Install required system libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your app
EXPOSE 8000
CMD ["sh", "-c", "echo 'Container started'; ls -l; python -m flask --version; sleep 600"]


