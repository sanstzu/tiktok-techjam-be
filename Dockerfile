# Use the official Python image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements-be.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add uvicorn to path
ENV PATH="/root/.local/bin:${PATH}"

# Copy the rest of your application's code into the container
COPY ./app /app

EXPOSE 8000