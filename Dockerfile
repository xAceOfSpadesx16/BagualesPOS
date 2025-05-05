# Use an official lightweight Python image
FROM python:3.13.3-slim

# Install any needed packages specified in requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy requirements first to leverage Docker's cache
COPY requirements.txt .

# Install the dependencies
# Asegúrate de que requirements.txt contiene psycopg[binary]
RUN pip install --user -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Asegúrate de que este comando es correcto para tu proyecto (django_project.settings vs tu_proyecto.settings)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
