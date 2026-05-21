#!/bin/bash
set -e

cd /home/kali/catty-reminders-app

echo "[1/2] Обновляем зависимости приложения..."
source .venv/bin/activate
pip install -r requirements.txt --prefer-binary --no-cache-dir

echo "[2/2] Перезапускаем службу приложения через systemd..."
sudo systemctl restart catty.service

echo "Деплой успешно завершен!"
