FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create persistent data directory
RUN mkdir -p /app/data

# Set environment variable to track first run (optional)
ENV INSTALL_MARKER=/app/data/.installed

# Run main.py by default
CMD ["python", "-m", "src.main"]
