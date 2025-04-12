FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

ENV AGENT_SERVICE_URL=http://ai_agents.railway.internal:6000
ENV DB_SERVICE_URL=http://json_db.railway.internal:7000

CMD ["gunicorn", "app:app", "--bind [::]:${PORT-5000}"]