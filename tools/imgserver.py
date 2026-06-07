# -*- coding: utf-8 -*-
"""
配图工具的本地服务（端口 8767）：
  GET  /            → 画廊（site/ 静态文件）
  GET  /__pei__     → 配图工具页面
  POST /__upload__  → 接收一张图：Pillow 压缩 → 存 images/<codexId>/<entryId>.jpg
                      → 更新 site/data/<codexId>.json 的 entry.image
用法：python tools/imgserver.py  （或双击 配图工具.bat）
"""
import http.server, socketserver, json, base64, io, os, threading
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
DATA = os.path.join(SITE, "data")
TOOL_HTML = os.path.join(os.path.dirname(__file__), "pei.html")
MAXDIM = 1100          # 例图最长边压到 1100px
PORT = 8767
LOCK = threading.Lock()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def end_headers(self):
        # data/*.json 不缓存，保证配图后刷新能看到
        if self.path.endswith(".json"):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path.split("?")[0] == "/__pei__":
            try:
                with open(TOOL_HTML, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as ex:
                self.send_error(500, str(ex))
            return
        return super().do_GET()

    def do_POST(self):
        if self.path != "/__upload__":
            self.send_error(404); return
        try:
            ln = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(ln))
            cid, eid, durl = data["codexId"], data["entryId"], data["dataURL"]
            raw = base64.b64decode(durl.split(",", 1)[1])
            im = Image.open(io.BytesIO(raw))
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            im.thumbnail((MAXDIM, MAXDIM), Image.LANCZOS)
            outdir = os.path.join(SITE, "images", cid)
            os.makedirs(outdir, exist_ok=True)
            fn = eid + ".jpg"
            im.save(os.path.join(outdir, fn), "JPEG", quality=86, optimize=True)
            with LOCK:
                jp = os.path.join(DATA, cid + ".json")
                with open(jp, encoding="utf-8") as f:
                    d = json.load(f)
                for e in d["entries"]:
                    if e["id"] == eid:
                        e["image"] = fn; break
                d["imagedCount"] = sum(1 for e in d["entries"] if e.get("image"))
                with open(jp, "w", encoding="utf-8") as f:
                    json.dump(d, f, ensure_ascii=False)
            self._json({"ok": True, "image": fn, "imagedCount": d["imagedCount"]})
        except Exception as ex:
            self._json({"ok": False, "error": str(ex)}, 500)

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with Server(("127.0.0.1", PORT), Handler) as s:
        print(f"配图工具已启动 -> http://localhost:{PORT}/__pei__")
        print(f"画廊预览       -> http://localhost:{PORT}/")
        s.serve_forever()
