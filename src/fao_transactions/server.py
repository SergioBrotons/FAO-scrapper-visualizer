"""Lightweight HTTP and REST API server for Geneva Property Intelligence Visualizer and Portal Sync."""

import sys
import os
import json
import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fao_transactions.collector.sync_engine import sync_manager

logger = logging.getLogger(__name__)


class CytriaApiHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving Cytria static web assets and REST synchronization API."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json_response(self, data: dict, status: int = 200):
        """Helper to send JSON response with proper CORS headers."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        """Route GET requests between REST API and static files."""
        if self.path == "/api/status" or self.path == "/api/status/":
            status = sync_manager.get_status()
            self._send_json_response({
                "status": "online",
                "service": "Cytria Geneva Real Estate Intelligence Engine",
                "telemetry": status,
            })
            return

        elif self.path.startswith("/api/scan/progress"):
            status = sync_manager.get_status()
            self._send_json_response(status)
            return

        # Fallback to serving static files (index.html, data/exports/..., etc.)
        super().do_GET()

    def do_POST(self):
        """Route POST requests for synchronization controls."""
        if self.path == "/api/scan" or self.path == "/api/scan/":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                body = json.loads(body_bytes.decode("utf-8"))
            except Exception:
                body = {}

            mode = body.get("mode", "quick")
            options = body.get("options", {})

            success = sync_manager.start_scan(mode=mode, options=options)
            if success:
                self._send_json_response({
                    "success": True,
                    "message": f"Scan démarré en mode '{mode}'.",
                    "status": sync_manager.get_status(),
                })
            else:
                self._send_json_response({
                    "success": False,
                    "message": "Un scan est déjà en cours d'exécution.",
                    "status": sync_manager.get_status(),
                }, status=409)
            return

        elif self.path == "/api/scan/cancel" or self.path == "/api/scan/cancel/":
            sync_manager.cancel_scan()
            self._send_json_response({
                "success": True,
                "message": "Arrêt du scan demandé.",
                "status": sync_manager.get_status(),
            })
            return

        self.send_error(404, "Endpoint non trouvé.")


def run_server(port: int = 8080, host: str = "0.0.0.0"):
    """Run multi-threaded HTTP server with REST API."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, CytriaApiHandler)
    print(f"------------- CYTRIA INTELLIGENCE & SYNC SERVER -------------")
    print(f"Serving at http://localhost:{port}/ and http://{host}:{port}/")
    print(f"REST API: http://localhost:{port}/api/status")
    print(f"Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur Cytria.")
        httpd.server_close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_server(port=port)
