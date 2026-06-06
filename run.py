from flask import Flask, Response, request
import requests
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

ORIGIN = "https://2i4.d72577a9dd0ec71.cfd/b2/mono.m3u8"

# Önemli: Referer buraya doğru siteyi koy
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://2i4.d72577a9dd0ec71.cfd/",   # ← Burayı doğru referer ile değiştir
    "Origin": "https://2i4.d72577a9dd0ec71.cfd"
}

# -------------------------
# M3U8 PLAYLIST PROXY
# -------------------------
@app.route("/live/<path:playlist>")
def playlist_proxy(playlist):
    url = urljoin(ORIGIN, playlist)
    
    r = requests.get(url, headers=HEADERS, timeout=20)
    
    if r.status_code != 200:
        return Response(r.text, status=r.status_code, content_type=r.headers.get("Content-Type"))

    content = r.text
    lines = []

    for line in content.splitlines():
        line = line.strip()
        if not line:
            lines.append(line)
            continue
            
        if line.startswith("#"):
            lines.append(line)
        else:
            # Mutlak URL mi yoksa göreli mi kontrol et
            if line.startswith("http://") or line.startswith("https://"):
                segment_url = line
            else:
                segment_url = urljoin(url, line)  # base URL'e göre birleştir
            
            # Kendi proxy'ine yönlendir
            lines.append(f"/segment?url={segment_url}")
    
    modified = "\n".join(lines)
    return Response(modified, content_type="application/vnd.apple.mpegurl")


# -------------------------
# SEGMENT PROXY
# -------------------------
@app.route("/segment")
def segment_proxy():
    url = request.args.get("url")
    if not url:
        return "Missing URL parameter", 400

    # Güvenlik: Sadece ORIGIN domain'inden gelen istekleri kabul et (opsiyonel)
    if not url.startswith("https://2i4.d72577a9dd0ec71.cfd"):
        return "Invalid URL", 403

    r = requests.get(url, headers=HEADERS, stream=True, timeout=20)
    
    if r.status_code != 200:
        return Response(r.content, status=r.status_code)

    def generate():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return Response(
        generate(),
        content_type=r.headers.get("Content-Type", "video/mp2t"),
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Cache-Control": "no-cache"
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
