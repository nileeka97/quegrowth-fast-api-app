FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY worker.py .

# Change ownership and switch to non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser /app
USER appuser

# Run worker process
CMD ["python", "worker.py"]
