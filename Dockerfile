FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files
COPY pyproject.toml ./

# Configure Poetry (no virtualenv in container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code (handled by volumes in dev, but needed for build)
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY .streamlit/ ./.streamlit/

# Expose ports (overridden per service in docker-compose)
EXPOSE 8501 8000

# Default command (overridden in docker-compose per service)
CMD ["streamlit", "run", "src/ui/main.py", "--server.address", "0.0.0.0"]
