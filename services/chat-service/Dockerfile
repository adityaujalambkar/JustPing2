
# Use an official Python base image
FROM python:3.11-slim



# Set working directory
WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code
COPY . .

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

