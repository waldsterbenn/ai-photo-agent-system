FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_APP=app.py
#ENV FLASK_ENV=production

ENV AGENT_SERVICE_URL=https://ai-agents-ti7y.onrender.com
ENV DB_SERVICE_URL=https://json-db-rj13.onrender.com

CMD ["gunicorn", "app:app", "--bind [::]:${PORT-5000}"]