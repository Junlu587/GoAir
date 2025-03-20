FROM python:3.10-slim

# Install system dependencies for psycopg2 & cryptography
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "GoAir.wsgi:application", "--bind", "0.0.0.0:8000"]
