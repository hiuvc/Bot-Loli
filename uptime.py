# uptime.py
import json
import os
from datetime import datetime

UPTIME_FILE = "uptime.json"

def save_start_time():
    """Lưu thời gian bot bắt đầu chạy"""
    data = {"start_time": datetime.now().isoformat()}
    with open(UPTIME_FILE, "w") as f:
        json.dump(data, f)

def get_last_uptime():
    """Tính uptime của lần chạy trước"""
    if not os.path.exists(UPTIME_FILE):
        return None

    try:
        with open(UPTIME_FILE, "r") as f:
            data = json.load(f)
        start_time = datetime.fromisoformat(data["start_time"])
        end_time = datetime.now()
        delta = end_time - start_time
        return delta
    except Exception:
        return None
