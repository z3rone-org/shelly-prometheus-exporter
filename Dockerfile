FROM python:3.14-alpine

RUN pip install httpx flask

COPY exporter.py .

CMD ["python", "exporter.py"]