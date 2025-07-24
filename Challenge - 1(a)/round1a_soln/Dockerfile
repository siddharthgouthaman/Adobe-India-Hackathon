# Use a slim Python base image for AMD64 architecture
FROM --platform=linux/amd64 python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code (including extractor/ folder)
COPY . .

# Run the main script
CMD ["python", "main.py"]
