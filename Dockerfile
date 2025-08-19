# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# The --no-cache-dir option is used to keep the image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY ./app /code/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using uvicorn. Port 8000 is standard for App Service.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]