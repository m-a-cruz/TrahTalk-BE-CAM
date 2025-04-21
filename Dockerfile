# Use a minimal Python base image
FROM python:3.10-slim

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory inside container
WORKDIR /app

# Copy all files from your project into the container
COPY . .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port used by Railway (default is 8080)
ENV PORT=8080

# Run your app using Gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080"]
