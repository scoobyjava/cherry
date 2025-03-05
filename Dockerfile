# Use the official slim Python 3.9 image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install required Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run the application
CMD ["python", "api/main.py"]
