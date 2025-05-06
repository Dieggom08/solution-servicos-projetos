# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libcairo-gobject2 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Ensure the virtual environment is not used here, install directly
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY ./src /app/src
COPY ./venv /app/venv # Include venv just in case, though not strictly needed for runtime

# Make port 5000 available to the world outside this container
# Cloud Run will automatically use the PORT environment variable, but good practice to expose
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=src/main.py
ENV FLASK_RUN_HOST=0.0.0.0
# Cloud Run provides the PORT env var, Gunicorn will use it
# ENV PORT=5000 # Not needed if using Gunicorn with Cloud Run

# Install Gunicorn for production WSGI server
RUN pip install gunicorn

# Run the app using Gunicorn when the container launches
# Use the PORT environment variable provided by Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 src.main:app

