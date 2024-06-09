FROM python:3.12-slim

# Устанавливаем рабочий каталог
WORKDIR /app/backend

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

# Копируем файлы
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
