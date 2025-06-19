
FROM python:3.11-slim


WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy the actual FastAPI app
COPY ./app /app

# Create uploads directory inside the container
RUN mkdir -p /app/uploads


# Expose port
EXPOSE 8000


# Start app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
