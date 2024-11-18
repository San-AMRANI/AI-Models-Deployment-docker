# Step 1: Use a Python base image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container
COPY . /app/

# Step 4: Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose the port the app will run on
EXPOSE 5000

# Step 6: Run the Flask app
CMD ["python", "app.py"]
