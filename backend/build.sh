#!/bin/bash
sudo apt-get update
sudo apt-get install -y fonts-dejavu fonts-noto
mkdir -p /opt/render/project/src/backend/fonts
cp /usr/share/fonts/truetype/noto/NotoSans-Regular.ttf /opt/render/project/src/backend/fonts/
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000
