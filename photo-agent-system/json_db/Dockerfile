FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7000

ENV FLASK_APP=app.py

CMD ["gunicorn", "app:app", "--bind [::]:${PORT-7000}"]