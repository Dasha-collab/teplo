#!/bin/bash
# Установка шрифтов и зависимостей
sudo apt-get update
sudo apt-get install -y fonts-dejavu fonts-noto fonts-noto-cjk fonts-noto-core fonts-arial

# Создание директории для шрифтов
mkdir -p /opt/render/project/src/backend/fonts

# Копирование основных шрифтов
cp /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf /opt/render/project/src/backend/fonts/
cp /usr/share/fonts/truetype/noto/NotoSans-Bold.ttf /opt/render/project/src/backend/fonts/
cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /opt/render/project/src/backend/fonts/

# Попытка скопировать Arial Unicode (если доступен)
cp /usr/share/fonts/truetype/arialuni.ttf /opt/render/project/src/backend/fonts/ 2>/dev/null || true

# Обновление кэша шрифтов
fc-cache -f -v

# Python зависимости
pip install -r requirements.txt

# Запуск сервера
uvicorn main:app --host 0.0.0.0 --port 10000
