# Use official slim Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies needed for YOLO and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project source code into the container
COPY . .

# Create uploads folder and set permissions
RUN mkdir uploads && chmod 775 uploads

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Create a non-root user for better security practices
RUN useradd -m appuser

# Change ownership of the uploads folder so that appuser can write to it
RUN chown -R appuser:appuser /app/uploads

# Switch to the non-root user
USER appuser

# Command to run the FastAPI server with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
