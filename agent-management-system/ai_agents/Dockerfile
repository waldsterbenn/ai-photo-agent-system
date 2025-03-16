FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5678 6000

#CMD ["python", "-m", "debugpy", "--wait-for-client","--listen","0.0.0.0:5678", "app.py"]
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "app.py"]