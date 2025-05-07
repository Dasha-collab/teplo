#!/bin/bash
# Установка системных шрифтов
sudo apt-get update
sudo apt-get install -y fonts-dejavu

# Установка зависимостей Python
pip install -r requirements.txt
