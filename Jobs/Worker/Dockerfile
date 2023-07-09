FROM python:3.10

COPY . .

RUN pip install redis requests

CMD ["python", "worker.py"]