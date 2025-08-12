FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy all project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Default command uses the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
