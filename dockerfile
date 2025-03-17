FROM python:3.11-slim

WORKDIR /

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

COPY . .

CMD ["python", "./web/app.py"]

