from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import argparse
import mimetypes


ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "server-access.log"


def write_log(message):
    with LOG_PATH.open("a", encoding="utf-8") as log:
        log.write(message + "\n")


def is_loader_client(headers):
    accept = headers.get("Accept", "").lower()
    user_agent = headers.get("User-Agent", "").lower()

    if "text/html" in accept:
        return False

    return "roblox" in user_agent or "wininet" in user_agent


class AzuriumHandler(BaseHTTPRequestHandler):
    server_version = "AzuriumLocal/1.0"

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path.rstrip("/") or "/"

        if route == "/load":
            self.handle_load()
            return

        self.handle_static(parsed.path)

    def handle_load(self):
        write_log(
            "LOAD "
            f"accept={self.headers.get('Accept', '')!r} "
            f"ua={self.headers.get('User-Agent', '')!r}"
        )

        if not is_loader_client(self.headers):
            self.send_denied()
            return

        body = (ROOT / "load").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive")
        self.send_header("Content-Disposition", "inline")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_static(self, request_path):
        path = unquote(request_path.split("?", 1)[0])

        if path == "/":
            path = "/index.html"
        elif path == "/denied":
            path = "/denied.html"

        target = (ROOT / path.lstrip("/")).resolve()

        if ROOT not in target.parents and target != ROOT:
            self.not_found()
            return

        if not target.is_file() or target.name == "load":
            self.not_found()
            return

        body = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)

        if target.parts[-2:] and "assets" in target.parts:
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")

        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def not_found(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not Found")

    def send_denied(self):
        body = (ROOT / "denied.html").read_bytes()
        self.send_response(403)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow, noarchive")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Azurium local guarded static server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), AzuriumHandler)
    print(f"Serving Azurium on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
