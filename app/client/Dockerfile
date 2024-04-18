FROM python:3.12

WORKDIR /app/client

COPY . .

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]