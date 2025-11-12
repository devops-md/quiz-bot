FROM python:3.13-alpine

WORKDIR /app/

# Copy requirements file first for better Docker layer caching
COPY requirements.txt .

# Install dependencies from requirements file
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

CMD [ "python", "-m", "src.main" ]