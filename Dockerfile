# Use Python 3.11 as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY .env .

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python scripts into the container
COPY db_interaction.py main.py ./

# Command to run on container start
CMD ["python", "main.py"]
