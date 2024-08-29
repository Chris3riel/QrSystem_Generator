FROM python:3.11-slim-buster

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    build-essential \
    python3-dev \
    python3-tk

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy application code
COPY . /app

# Set the working directory
WORKDIR /app

# Define the entrypoint
ENTRYPOINT ["python", "app.py"]