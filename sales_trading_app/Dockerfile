# Use official Python image as a base
FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose the port Django runs on
EXPOSE 8000

# Run Django migrations and start the server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sales_trading_app.wsgi:application"]
