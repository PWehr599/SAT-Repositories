# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /satqubolib_groundstates

# Copy the current directory contents into the container
COPY . .

# Install any dependencies (if necessary)
RUN pip install -r requirements.txt

# Declare a volume for data persistence (optional)
VOLUME ["/satqubolib_groundstates"]

# Define the command to run the Python script with arguments passed at runtime
ENTRYPOINT ["python", "main_args.py"]


