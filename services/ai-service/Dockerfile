FROM python:3.13-alpine

WORKDIR /app

# Install only the dependency — single layer, no extra tooling
COPY pyproject.toml ./
RUN pip install --no-cache-dir "starlette>=0.46.0"

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]