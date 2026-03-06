FROM python:3.11-slim

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files first (better Docker caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies with uv
RUN uv sync --no-dev

# Copy application code
COPY . .


EXPOSE 8000

# Run FastAPI
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]