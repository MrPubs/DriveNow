FROM python:3.12-slim

# Set working directory
WORKDIR /containedapp

# Install dependencies
COPY app/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/api/start.sh .
RUN sed -i 's/\r$//' ./start.sh 
RUN chmod +x start.sh

# Copy project
COPY ./app ./app
# COPY ./logs ./logs

# Expose API port
EXPOSE 8000

# Install curl for health checks and clean up apt cache
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* 
CMD ["./start.sh"]
# CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]