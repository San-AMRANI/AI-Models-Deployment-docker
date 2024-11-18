# Use the official Python image as the base
FROM python:3.10-slim


# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app and other files
COPY . .

# Create the directory where you want to store uploaded files
RUN mkdir -p static/uploads

# Expose the port Flask will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
