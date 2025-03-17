# 1) Use an official Python base image
FROM python:3.10-slim

# 2) Set a working directory
WORKDIR /app

# 3) Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Copy the rest of your code
COPY . .

# 5) Expose the port (optional)
EXPOSE 8000

# 6) Set the command to run your Django app
CMD ["gunicorn", "GoAir.wsgi:application", "--bind", "0.0.0.0:8000"]
