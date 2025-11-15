# Stage 1: Use an official Python runtime as a parent image
FROM python:3.11-slim

# Stage 2: Set the working directory in the container
WORKDIR /app

# Stage 3: Copy the dependencies file and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 4: Copy the rest of the backend application code
COPY . .

# Stage 5: Expose the port the app will run on
# This matches the 'target_port' in Terraform
EXPOSE 8000

# Stage 6: Define the command to run the application
# This tells uvicorn to run the 'app' object from the 'main.py' file
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]