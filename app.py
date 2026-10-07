import os
from wsgi import app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8088))
    print(f"Serving on port {port}...")
    with make_server("", port, app) as httpd:
        httpd.serve_forever()
