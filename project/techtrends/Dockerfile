# Use Python base image version 3.8
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Initialize the database
RUN python init_db.py

# Expose the application port
EXPOSE 3111

# Define the command to run the application
CMD ["python", "app.py"]
