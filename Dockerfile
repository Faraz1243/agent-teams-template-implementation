FROM python:3.12-slim

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8080

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set the working directory
WORKDIR /app

# Copy Poetry files and README.md
ADD pyproject.toml ./
ADD poetry.lock /app/poetry.lock

# Install the project dependencies
RUN poetry config virtualenvs.create false \
&& poetry install --no-interaction --no-ansi --without dev

# Copy the application files
# ADD models /app/models
# ADD config /app/config
# ADD tools /app/tools
# ADD app.py /app/app.py
# ADD chatbot.py /app/chatbot.py
# ADD SYSTEM_PROMPT.txt /app/SYSTEM_PROMPT.txt
COPY . /app/

# Expose the application port
EXPOSE ${PORT}

# Use shell form to allow environment variable expansion
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:${PORT}", "app:app"]
CMD exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT app:app

