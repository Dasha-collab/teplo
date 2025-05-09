#!/bin/bash
# Установка зависимостей
sudo apt-get update
sudo apt-get install -y fonts-dejavu fonts-noto

# Создание директории для шрифтов
mkdir -p /opt/render/project/src/backend/fonts
cp /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf /opt/render/project/src/backend/fonts/

# Установка Python-зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Бесконечный цикл для поддержания работы сервера
while true; do
  # Запуск сервера с таймаутом 55 минут (меньше 60-минутного лимита Render)
  timeout 3300 uvicorn main:app --host 0.0.0.0 --port 10000
  sleep 5
done
