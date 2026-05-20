#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/home/kali/catty-reminders-app"
echo "Deploying via Docker into '$APP_DIR'"
cd "$APP_DIR"

# Авторизация в реестре через переданный токен с использованием sudo
echo "$GITHUB_TOKEN" | sudo docker login ghcr.io -u "$GITHUB_ACTOR" --password-stdin

echo "Pulling Docker image: $IMAGE"
sudo docker pull "$IMAGE"

echo "Stopping old container..."
sudo docker stop catty-test || true
sudo docker rm catty-test || true

# Контрольная очистка портов (на случай зависших фоновых процессов)
sudo fuser -k -9 8181/tcp || true
sleep 2

echo "Starting new Docker container..."
sudo docker run -d \
  -p 8181:8181 \
  --name catty-test \
  --restart unless-stopped \
  -e DEPLOY_REF="$DEPLOY_REF" \
  "$IMAGE"

echo "Docker deployment completed successfully!"
