#!/bin/bash
sudo apt-get update
sudo apt-get install -y fonts-dejavu
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000
