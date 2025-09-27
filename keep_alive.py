
# keep_alive.py
from flask import Flask, request
from threading import Thread
from datetime import datetime

app = Flask('')

@app.route('/')
def home():
    ip = request.remote_addr
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[KEEP_ALIVE] Ping từ {ip} lúc {now}")
    return "✅ Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
