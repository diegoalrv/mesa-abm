FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sumo sumo-tools sumo-doc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Default command
CMD ["python", "simulation/traffic_simulation.py"]
