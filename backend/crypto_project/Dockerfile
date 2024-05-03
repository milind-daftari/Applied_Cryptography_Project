# Use an official Python runtime as a parent image
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies for OpenFHE and JupyterLab
RUN apt-get update && apt-get install -y \
    apt-utils \
    iputils-ping \    
    git \
    cmake \
    build-essential \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    sudo \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install "pybind11[global]"

# Clone and build OpenFHE
RUN git clone --depth 1 https://github.com/openfheorg/openfhe-development.git \
    && cd openfhe-development \
    && mkdir build \
    && cd build \
    && cmake -DBUILD_UNITTESTS=OFF -DBUILD_EXAMPLES=OFF -DBUILD_BENCHMARKS=OFF .. \
    && make -j$(nproc) \
    && make install

# Set environment variables to find OpenFHE libraries
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}

# Clone and build OpenFHE Python bindings
RUN git clone --depth 1 https://github.com/openfheorg/openfhe-python.git \
    && cd openfhe-python \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && make install

# Set the working directory in the container to /app
WORKDIR /app

# Copy everything from the current directory to /app in the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
