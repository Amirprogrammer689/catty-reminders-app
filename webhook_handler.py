import json
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

HOOK_PORT = 8080
APP_PORT = 8181

class GitHubWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
            
            if 'ref' in payload:
                print(f"\n[Webhook] Обнаружен push в ветку {payload['ref']}. Запуск деплоя...")
                
                # 1. Подтягиваем свежий код приложения
                print("[1/3] Обновление локального репозитория...")
                subprocess.run(["git", "pull", "origin", "lab1"], check=True)
                
                # 2. Убиваем старый процесс приложения на порту 8181
                print(f"[2/3] Освобождение порта {APP_PORT}...")
                try:
                    pids = subprocess.check_output(["lsof", "-t", f"-i:{APP_PORT}"]).decode().strip()
                    if pids:
                        for pid in pids.split("\n"):
                            subprocess.run(["kill", "-9", pid], check=True)
                except subprocess.CalledProcessError:
                    print(f"Порт {APP_PORT} уже был свободен.")
                
                # 3. Запускаем приложение заново в фоновом режиме на порту 8181
                print(f"[3/3] Перезапуск Uvicorn на порту {APP_PORT}...")
                runtime_log = open("server_runtime.log", "w")
                subprocess.Popen(
                    ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(APP_PORT)],
                    stdout=runtime_log, stderr=runtime_log, preexec_fn=os.setpgrp
                )
                print("=== Автоматический деплой успешно завершен! ===")
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            
        except Exception as e:
            print(f"Ошибка при обработке вебхука: {e}")
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', HOOK_PORT), GitHubWebhookHandler)
    print(f"Сервер обработки вебхуков запущен на стандартном порту {HOOK_PORT}...")
    server.serve_forever()
