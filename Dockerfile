FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

#requirements.txt first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Load .env file
COPY .env .env

# Expose FastAPI app port
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "fastapi_chatbot_backend:app", "--host", "0.0.0.0", "--port", "8000"]
