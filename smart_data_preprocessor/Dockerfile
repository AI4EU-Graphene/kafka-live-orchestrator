FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir kafka-python pandas

CMD ["python", "preprocessor_service.py"]
