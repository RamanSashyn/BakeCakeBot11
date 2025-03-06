# Используем официальный Python образ
FROM python:3.12.6-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app/

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Создаем папку для статических файлов, если её нет
RUN mkdir -p /app/staticfiles

# Сборка статики
RUN python manage.py collectstatic --noinput

# Открываем порт
EXPOSE 8080

# Команда для запуска вашего приложения
CMD ["sh", "-c", "gunicorn cake_bot.wsgi:application --bind 0.0.0.0:$PORT & python run_bot.py"]
