#!/bin/bash
# Установка шрифтов и зависимостей
sudo apt-get update
sudo apt-get install -y fonts-dejavu fonts-noto fonts-arial

# Создание директории для шрифтов
mkdir -p /opt/render/project/src/backend/fonts
cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /opt/render/project/src/backend/fonts/
cp /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf /opt/render/project/src/backend/fonts/

# Обновление кэша шрифтов
fc-cache -f -v

# Python зависимости
pip install -r requirements.txt

# Запуск сервера
uvicorn main:app --host 0.0.0.0 --port 10000
