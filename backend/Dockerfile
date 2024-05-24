FROM python:3.12-slim

# Устанавливаем рабочий каталог
WORKDIR /app/backend

# Копируем файлы
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
