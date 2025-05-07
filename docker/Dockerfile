# Use an official lightweight Python image
FROM python:3.13.3-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy requirements first to leverage Docker's cache
COPY ../pyproject.toml .

# Install the dependencies
RUN uv run pip install -r pyproject.toml

# Copy the application code
COPY .. .

# Expose the port the app runs on
EXPOSE 8000

ENTRYPOINT [ "bash ", "-c", "docker/entrypoint.${SETTINGS_MODULE}.sh" ]
