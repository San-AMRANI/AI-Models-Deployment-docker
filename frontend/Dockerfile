# Step 1: Use the official Nginx image as the base
FROM nginx:alpine

# Step 2: Copy the app content to the Nginx default directory
COPY . /usr/share/nginx/html

# Expose the default Nginx port
EXPOSE 80

# Start Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]
