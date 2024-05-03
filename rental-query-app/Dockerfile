# Use an official Node runtime as a parent image
FROM node:latest

# Set the working directory in the container
WORKDIR /usr/src/app

# Update the package list and install ping and curl
RUN apt-get update && apt-get install -y \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package.json AND package-lock.json
COPY package*.json ./

# Install any needed packages
RUN npm install

# Set environment variables before building
ENV REACT_APP_BACKEND_URL=http://127.0.0.1:5000

# Bundle app source
COPY . .

# Build the React application
RUN npm run build

# Install serve to serve your app on port 3000
RUN npm install -g serve
EXPOSE 3000

# Command to run your app using serve
CMD ["serve", "-s", "build"]
