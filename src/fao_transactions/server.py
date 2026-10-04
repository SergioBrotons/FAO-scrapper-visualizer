"""Lightweight HTTP and REST API server for Geneva Property Intelligence Visualizer and Portal Sync."""

import sys
import os
import json
import logging
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
import threading
import time

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Prevent incompatible external Python 3.13 user site-packages from polluting the 3.12 virtualenv
sys.path = [p for p in sys.path if "Python313" not in p and "Python311" not in p]

from fao_transactions.collector.sync_engine import sync_manager
from fao_transactions.config import settings

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
        """Helper to send JSON response with proper CORS and Content-Length headers."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

    protocol_version = "HTTP/1.1"

    def do_GET(self):
        """Route GET requests between REST API and static files."""
        if self.path in ("/", "/index.html", ""):
            index_path = ROOT_DIR / "index.html"
            if index_path.exists():
                try:
                    content = index_path.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.send_header("Connection", "close")
                    self.send_header("Cache-Control", "no-cache, must-revalidate")
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    logger.error(f"Error serving index.html: {e}")

        if self.path == "/api/health" or self.path == "/api/health/":
            self._send_json_response({
                "status": "online",
                "service": "Cytria Geneva Real Estate Intelligence Engine",
            })
            return

        elif self.path == "/api/status" or self.path == "/api/status/":
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

        # Fallback to serving static files (data/exports/..., etc.)
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
            suite = body.get("suite", "MARKET")
            source = body.get("source", "ALL")
            headed = body.get("headed", not settings.browser.headless)
            options = body.get("options", {})
            options["suite"] = suite
            options["source"] = source
            options["headed"] = headed
            options["fao"] = body.get("fao", source in ["FAO", "ALL"] or suite in ["MARKET", "SOURCING"])
            options["sitg"] = body.get("sitg", source in ["CADASTRE", "ALL"] or suite in ["MARKET", "SOURCING"])
            options["agencies"] = body.get("agencies", source in ["AGENCY_BI", "ALL"] or suite == "AGENCY_BI")

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


class RobustThreadingHTTPServer(ThreadingHTTPServer):
    """Threading HTTPServer with daemon threads and socket timeout."""
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        """Silently ignore normal client disconnects (BrokenPipe / ConnectionReset)."""
        exc_type, exc_val, _ = sys.exc_info()
        if exc_type in (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            return
        super().handle_error(request, client_address)


def start_background_scheduler(interval_hours: int = 6):
    """Run an automated background synchronization loop without any terminal or user intervention."""
    def _worker():
        # Allow server to initialize before first background check
        time.sleep(15)
        while True:
            try:
                if not sync_manager.is_scanning:
                    logger.info("[SCHEDULER] Démarrage de la veille automatique d'arrière-plan FAO...")
                    sync_manager.start_scan(
                        mode="quick",
                        options={
                            "headed": False,
                            "source": "ALL",
                            "fao": True,
                            "sitg": True,
                            "agencies": True,
                        }
                    )
            except Exception as e:
                logger.error(f"[SCHEDULER Error] {e}")
            time.sleep(interval_hours * 3600)

    sched_thread = threading.Thread(target=_worker, daemon=True, name="CytriaBackgroundScheduler")
    sched_thread.start()
    logger.info(f"[SCHEDULER] Veille automatique d'arrière-plan activée (intervalle: {interval_hours}h).")


def run_server(port: int = 8080, host: str = "0.0.0.0", auto_sync_hours: int = 6):
    """Run multi-threaded HTTP server with REST API and background scheduler."""
    server_address = (host, port)
    httpd = RobustThreadingHTTPServer(server_address, CytriaApiHandler)
    
    # Start automated background synchronization engine
    if auto_sync_hours > 0:
        start_background_scheduler(interval_hours=auto_sync_hours)

    print(f"------------- CYTRIA INTELLIGENCE & SYNC SERVER -------------")
    print(f"Serving at http://localhost:{port}/ and http://{host}:{port}/")
    print(f"REST API: http://localhost:{port}/api/status")
    print(f"Background Sync: Auto-scraping every {auto_sync_hours}h (100% automated)")
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
