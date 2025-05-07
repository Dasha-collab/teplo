#!/usr/bin/env bash
# Установка системных зависимостей
sudo apt-get update
sudo apt-get install -y fonts-dejavu

# Установка Python-зависимостей
pip install -r requirements.txt
