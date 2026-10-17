import os
import threading
import time
from datetime import datetime, timezone

import requests
import yaml
from flask import Flask, request, send_from_directory

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/config/config.yaml")
SITE_DIR = os.environ.get("SITE_DIR", "/app/site")

app = Flask(__name__)
last_seen = {}          # ip -> timestamp of last notification
lock = threading.Lock()


def load_config():
    # Re-read on every request so you can edit config.yaml without rebuilding
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f) or {}


def client_ip(visits_cfg):
    if visits_cfg.get("trust_proxy_headers"):
        fwd = request.headers.get("X-Forwarded-For")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.remote_addr


def send_webhook(cfg, info):
    wh = cfg.get("webhook", {})
    url = wh.get("url")
    if not url:
        return
    method = wh.get("method", "POST").upper()
    timeout = wh.get("timeout", 5)

    try:
        if method == "GET":
            # GET can't carry a body, so the visit info goes in the query string
            requests.get(url, params=info, timeout=timeout)
        else:
            if wh.get("format", "discord") == "discord":
                text = f"New visit to `{info['path']}` at {info['time']}"
                if "ip" in info:
                    text += f" from {info['ip']}"
                payload = {"content": text}
            else:
                payload = info
            requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException as e:
        print(f"Webhook failed: {e}", flush=True)


@app.after_request
def notify_on_visit(response):
    try:
        cfg = load_config()
        visits = cfg.get("visits", {})
        path = request.path

        if request.method != "GET" or response.status_code != 200:
            return response
        if visits.get("only_pages", True) and not (path == "/" or path.endswith(".html")):
            return response

        ip = client_ip(visits)
        if ip in visits.get("ignore_ips", []):
            return response

        cooldown = visits.get("cooldown_seconds", 60)
        now = time.time()
        with lock:
            if now - last_seen.get(ip, 0) < cooldown:
                return response
            last_seen[ip] = now

        info = {
            "path": path,
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "user_agent": request.headers.get("User-Agent", ""),
        }
        if visits.get("include_ip", True):
            info["ip"] = ip

        threading.Thread(target=send_webhook, args=(cfg, info), daemon=True).start()
    except Exception as e:
        print(f"Visit handler error: {e}", flush=True)
    return response


@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve(path):
    return send_from_directory(SITE_DIR, path)
