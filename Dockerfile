FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY main.py .
COPY generate_ssl.sh .

# Делаем скрипт исполняемым
RUN chmod +x generate_ssl.sh

# Генерируем SSL сертификат
RUN ./generate_ssl.sh

# Открываем порт
EXPOSE 8000

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO

# Запускаем приложение
CMD ["python", "main.py"] 