FROM python:3.12.6-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда запуска
CMD ["python", "run_bot.py"]

# Команда для запуска Django сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
