FROM python:3.11-alpine

WORKDIR /app

# Install runtime dependency
RUN apk add --no-cache libffi

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and SSL cert
COPY . /app

# Default command
CMD ["python", "-m", "src.main"]
