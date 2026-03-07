FROM python:3.13-slim

WORKDIR /app

# Install build tools needed for scikit-learn, then clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir "starlette>=0.46.0" "uvicorn>=0.34.0" pandas joblib scikit-learn numpy

# Remove build tools to keep image smaller
RUN apt-get purge -y gcc g++ && apt-get autoremove -y

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]