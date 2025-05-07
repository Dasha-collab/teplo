#!/bin/bash
# Установка системных шрифтов
sudo apt-get update
sudo apt-get install -y fonts-dejavu fonts-noto

# Создаем директорию для шрифтов и копируем их
mkdir -p /opt/render/project/src/backend/fonts
cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /opt/render/project/src/backend/fonts/
cp /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf /opt/render/project/src/backend/fonts/

# Обновляем кэш шрифтов
fc-cache -f -v

# Установка Python-зависимостей
pip install -r requirements.txt

# Запуск приложения
uvicorn main:app --host 0.0.0.0 --port 10000
