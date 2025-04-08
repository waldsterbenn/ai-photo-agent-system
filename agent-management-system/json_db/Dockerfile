FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port for our API (7000)
EXPOSE 7000

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "app.py"]