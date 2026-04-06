FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV PMS_DB_PATH=/data/pms.db

RUN mkdir -p /data

EXPOSE 8000

CMD ["python", "run.py"]
