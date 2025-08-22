# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install dependencies from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory into the container
COPY src/ /app/src/

# Set the working directory to the src directory
WORKDIR /app/src

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["python", "_cli.py"]