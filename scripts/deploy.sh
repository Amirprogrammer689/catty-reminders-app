#!/bin/bash

BRANCH=$1
SHA=$2
PROJECT_DIR="/home/kali/catty-reminders-app"

echo "=== СТАРТ CD ДЕПЛОЯ ДЛЯ ВЕТКИ $BRANCH (SHA: $SHA) ==="

cd $PROJECT_DIR

git fetch origin
git checkout -f $BRANCH
git reset --hard origin/$BRANCH

echo "[1/2] Очистка портов..."
fuser -k -9 8181/tcp || true
pkill -9 -f uvicorn || true
sleep 3

echo "[2/2] Запуск сервера uvicorn..."
DEPLOY_REF=$SHA ./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8181 > server_runtime.log 2>&1 &

echo "=== ДЕПЛОЙ УСПЕШНО ЗАВЕРШЕН ==="
