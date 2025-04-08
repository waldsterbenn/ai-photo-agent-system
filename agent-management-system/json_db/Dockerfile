FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port for our API (7000)
EXPOSE 7000

CMD ["python", "app.py"]