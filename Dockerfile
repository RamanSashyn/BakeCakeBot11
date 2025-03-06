FROM python:3.12.6-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папку для статических файлов, если её нет
RUN mkdir -p /app/staticfiles

# Собираем статические файлы (если нужно)
RUN python manage.py collectstatic --noinput

# Команда запуска
CMD ["sh", "-c", "sleep 10 && python manage.py migrate && python run_bot.py && python manage.py runserver 0.0.0.0:8080"]
