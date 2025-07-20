# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and uv.lock files to the working directory
COPY pyproject.toml uv.lock ./ 

# Install uv and then install dependencies using uv
RUN pip install uv && uv pip sync

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]