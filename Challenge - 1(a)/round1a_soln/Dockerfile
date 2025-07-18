# Use a slim Python base image for AMD64 architecture
FROM --platform=linux/amd64 python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your main application script
COPY main.py .

# Command to run your script when the container starts
# This will execute the process_pdfs_in_directory function in main.py
CMD ["python", "main.py"]