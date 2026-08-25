FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including PostgreSQL development libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    curl \
    libpq-dev \
    build-essential \
    netcat-openbsd \
    redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p instance

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "--worker-class", "gevent", "--worker-connections", "1000", "--bind", "0.0.0.0:8080", "wsgi:app"] 