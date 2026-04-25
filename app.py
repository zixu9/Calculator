"""
Calculator With History — Python HTTP Server Backend
Run: python server.py
Opens at: http://localhost:8000
"""

import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "history.json")
STATIC_DIR   = os.path.dirname(__file__)

MIME = {
    ".html": "text/html",
    ".css":  "text/css",
    ".js":   "application/javascript",
    ".json": "application/json",
    ".ico":  "image/x-icon",
}

# ─────────────────────────── Data helpers ───────────────────────────

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def do_calculate(num1, operator, num2):
    """Perform arithmetic and return (result, error)."""
    ops = {"+", "-", "*", "/"}
    if operator not in ops:
        return None, f"Invalid operator '{operator}'. Use +, -, *, or /."
    if operator == "/" and num2 == 0:
        return None, "Cannot divide by zero."

    if operator == "+": result = num1 + num2
    elif operator == "-": result = num1 - num2
    elif operator == "*": result = num1 * num2
    else:                 result = num1 / num2

    # Tidy floating-point noise
    result = round(result, 10)
    if result == int(result) and abs(result) < 1e15:
        result = int(result)

    return result, None


# ─────────────────────────── Handler ───────────────────────────

class CalcHandler(BaseHTTPRequestHandler):

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _error(self, msg, status=400):
        self._json({"error": msg}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}

    def _static(self, path):
        if path in ("/", ""):
            path = "/index.html"
        file_path = os.path.normpath(os.path.join(STATIC_DIR, path.lstrip("/")))
        if not file_path.startswith(os.path.abspath(STATIC_DIR)):
            self.send_response(403); self.end_headers(); return
        if not os.path.isfile(file_path):
            self.send_response(404); self.end_headers()
            self.wfile.write(b"404 Not Found"); return
        ext  = os.path.splitext(file_path)[1]
        mime = MIME.get(ext, "application/octet-stream")
        with open(file_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── Routing ──────────────────────────────────────────────────────

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/history":
            self._json({"history": load_history()})
        else:
            self._static(path)

    def do_POST(self):
        path = urlparse(self.path).path

        # ── POST /api/calculate ──────────────────────────────────────
        if path == "/api/calculate":
            body = self._read_body()
            try:
                num1     = float(body.get("num1"))
                operator = str(body.get("operator", "")).strip()
                num2     = float(body.get("num2"))
            except (TypeError, ValueError):
                self._error("num1 and num2 must be valid numbers."); return

            result, err = do_calculate(num1, num2=num2, operator=operator)
            if err:
                self._json({"error": err}, 422); return

            # Pretty-print the numbers (drop .0 when integer)
            def nice(n):
                if isinstance(n, float) and n == int(n) and abs(n) < 1e15:
                    return int(n)
                return n

            entry = {
                "num1":     nice(num1),
                "operator": operator,
                "num2":     nice(num2),
                "result":   result,
                "expr":     f"{nice(num1)} {operator} {nice(num2)}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            history = load_history()
            history.append(entry)
            save_history(history)

            self._json({"result": result, "entry": entry}, 200)

        # ── POST /api/history/clear ──────────────────────────────────
        elif path == "/api/history/clear":
            save_history([])
            self._json({"message": "History cleared."})

        else:
            self._error("Not found.", 404)

    def do_DELETE(self):
        path = urlparse(self.path).path
        # DELETE /api/history  — same as clear
        if path == "/api/history":
            save_history([])
            self._json({"message": "History cleared."})
        else:
            self._error("Not found.", 404)

    def log_message(self, fmt, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {fmt % args}")


# ─────────────────────────── Entry point ───────────────────────────

if __name__ == "__main__":
    HOST, PORT = "localhost", 8000
    server = HTTPServer((HOST, PORT), CalcHandler)
    print(f"""
╔══════════════════════════════════════════════╗
║   🧮  Calculator With History — Server       ║
║   http://{HOST}:{PORT}                        ║
║   Press Ctrl+C to stop                       ║
╚══════════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] Stopped.")
