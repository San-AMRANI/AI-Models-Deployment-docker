# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir flask openai

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
