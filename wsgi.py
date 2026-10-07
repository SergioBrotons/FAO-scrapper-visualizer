"""WSGI application entrypoint for Vercel, AWS Lambda, and serverless hosting."""

import os
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".pdf": "application/pdf",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}


def app(environ, start_response):
    """Standard WSGI entrypoint callable."""
    raw_path = environ.get("PATH_INFO", "/") or "/"
    path = raw_path.rstrip("/")
    if not path:
        path = "/"

    # 1. SaaS Welcome Page
    if path in ("/", "/welcome", "/welcome.html"):
        welcome_file = ROOT_DIR / "welcome.html"
        target_file = welcome_file if welcome_file.exists() else (ROOT_DIR / "index.html")
        if target_file.exists():
            content = target_file.read_bytes()
            start_response("200 OK", [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "public, max-age=3600")
            ])
            return [content]

    # 2. Interactive Real Estate Cadastre Map Platform
    if path in ("/map", "/map/", "/app", "/index.html"):
        index_file = ROOT_DIR / "index.html"
        if index_file.exists():
            content = index_file.read_bytes()
            start_response("200 OK", [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "public, max-age=3600")
            ])
            return [content]

    # 2. D&V Marketing Engine
    if path in ("/dv/marketing", "/dv/marketing/index.html"):
        mkt_file = ROOT_DIR / "public" / "dv" / "marketing" / "index.html"
        if mkt_file.exists():
            content = mkt_file.read_bytes()
            start_response("200 OK", [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "public, max-age=3600")
            ])
            return [content]

    # 3. D&V Agency Portal
    if path in ("/dv", "/dv/index.html"):
        dv_file = ROOT_DIR / "public" / "dv" / "index.html"
        if dv_file.exists():
            content = dv_file.read_bytes()
            start_response("200 OK", [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "public, max-age=3600")
            ])
            return [content]

    # 4. REST API: Health & Status
    if path in ("/api/health", "/api/health/"):
        data = json.dumps({"status": "online", "service": "Cytria Geneva Real Estate Intelligence Engine"}).encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(data))),
            ("Access-Control-Allow-Origin", "*")
        ])
        return [data]

    if path in ("/api/status", "/api/status/"):
        data = json.dumps({
            "status": "online",
            "service": "Cytria Geneva Real Estate Intelligence Engine",
            "version": "1.0.0",
            "canton": "Genève (GE)"
        }).encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(data))),
            ("Access-Control-Allow-Origin", "*")
        ])
        return [data]

    # 5. REST API: Swimming Pools Summary (SITG CAD_PISCINE)
    if path in ("/api/pools/summary", "/api/pools/summary/"):
        summary_data = {
            "status": "ok",
            "summary": {
                "total_cantonal_pools": 5173,
                "cantonal_total_surface_m2": 247395,
                "cantonal_avg_surface_m2": 47.8,
                "properties_with_pools": 468,
                "properties_pool_surface_m2": 28706,
                "top_communes": [
                    {"commune": "Veyrier", "pools_count": 570, "total_surface_m2": 21986.1, "avg_surface_m2": 38.6},
                    {"commune": "Collonge-Bellerive", "pools_count": 555, "total_surface_m2": 24968.5, "avg_surface_m2": 45.0},
                    {"commune": "Chêne-Bougeries", "pools_count": 432, "total_surface_m2": 21183.0, "avg_surface_m2": 49.0},
                    {"commune": "Cologny", "pools_count": 413, "total_surface_m2": 25121.8, "avg_surface_m2": 60.8},
                    {"commune": "Vandoeuvres", "pools_count": 300, "total_surface_m2": 15075.9, "avg_surface_m2": 50.3},
                    {"commune": "Thônex", "pools_count": 279, "total_surface_m2": 11594.7, "avg_surface_m2": 41.6},
                    {"commune": "Plan-les-Ouates", "pools_count": 202, "total_surface_m2": 7056.3, "avg_surface_m2": 34.9},
                    {"commune": "Anières", "pools_count": 188, "total_surface_m2": 8354.8, "avg_surface_m2": 44.4},
                    {"commune": "Genthod", "pools_count": 164, "total_surface_m2": 7187.7, "avg_surface_m2": 43.8},
                    {"commune": "Vernier", "pools_count": 156, "total_surface_m2": 7261.0, "avg_surface_m2": 46.5},
                    {"commune": "Corsier", "pools_count": 147, "total_surface_m2": 6996.7, "avg_surface_m2": 47.6},
                    {"commune": "Versoix", "pools_count": 144, "total_surface_m2": 7919.5, "avg_surface_m2": 55.0}
                ]
            }
        }
        data = json.dumps(summary_data, ensure_ascii=False).encode("utf-8")
        start_response("200 OK", [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(data))),
            ("Access-Control-Allow-Origin", "*")
        ])
        return [data]

    # 6. Static files resolution
    clean_p = raw_path.lstrip("/")
    target = ROOT_DIR / "public" / clean_p
    if not target.exists() or target.is_dir():
        target = ROOT_DIR / clean_p

    if target.exists() and target.is_file():
        ext = target.suffix.lower()
        content_type = MIME_TYPES.get(ext, "application/octet-stream")
        content = target.read_bytes()
        start_response("200 OK", [
            ("Content-Type", content_type),
            ("Content-Length", str(len(content))),
            ("Access-Control-Allow-Origin", "*")
        ])
        return [content]

    # 7. 404 Not Found fallback
    msg = b"404 Not Found"
    start_response("404 Not Found", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(msg)))
    ])
    return [msg]
