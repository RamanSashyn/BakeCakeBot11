FROM python:3.12.6-slim

# Устанавливаем зависимости
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Команда запуска
CMD ["sh", "-c", "python manage.py migrate && python run_bot.py & python manage.py runserver 0.0.0.0:$PORT"]
