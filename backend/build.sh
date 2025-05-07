#!/bin/bash
# Установка системных шрифтов
sudo apt-get update
sudo apt-get install -y fonts-dejavu

# Установка Python-зависимостей
pip install -r requirements.txt

# Запуск приложения
uvicorn main:app --host 0.0.0.0 --port 10000
