FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120"]
