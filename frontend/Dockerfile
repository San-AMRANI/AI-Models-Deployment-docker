# Stage 1: Build the app using Node.js
FROM node:18-alpine AS build

# Set the working directory in the container
WORKDIR /app


RUN npm run build

# Stage 2: Serve the app using Nginx
FROM nginx:alpine

# Copy the built app from the first stage into the Nginx HTML directory
COPY  . /usr/share/nginx/html

# Expose the default Nginx port
EXPOSE 80

# Start Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]
