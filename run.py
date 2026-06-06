from flask import Flask, Response, request
import requests
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# Varsayılan Headers (Referer çok önemli!)
def get_headers(referer=None):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": referer or "https://inattv1312.xyz/",
        "Origin": "https://inattv1312.xyz/"
    }

# -------------------------
# Dinamik Playlist Proxy
# -------------------------
@app.route("/proxy/stream")
def stream_proxy():
    m3u8_url = request.args.get("d")
    if not m3u8_url:
        return "Missing ?d= parameter (m3u8 URL)", 400

    # Güvenlik kontrolü (sadece https ve belirli domainler)
    if not m3u8_url.startswith("https://"):
        return "Only HTTPS URLs are allowed", 403

    headers = get_headers(referer=urlparse(m3u8_url).scheme + "://" + urlparse(m3u8_url).netloc + "/")

    try:
        r = requests.get(m3u8_url, headers=headers, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Error fetching playlist: {str(e)}", 502

    content = r.text
    lines = []

    base_url = m3u8_url.rsplit('/', 1)[0] + '/'  # m3u8'in klasörü

    for line in content.splitlines():
        line = line.strip()
        if not line:
            lines.append("")
            continue
        if line.startswith("#"):
            lines.append(line)
        else:
            # Mutlak veya göreli URL'yi tam URL'ye çevir
            if line.startswith(("http://", "https://")):
                segment_url = line
            else:
                segment_url = urljoin(base_url, line)
            
            # Kendi proxy'ine yönlendir
            lines.append(f"/proxy/segment?url={segment_url}")

    modified = "\n".join(lines)
    return Response(modified, content_type="application/vnd.apple.mpegurl")


# -------------------------
# Segment Proxy
# -------------------------
@app.route("/proxy/segment")
def segment_proxy():
    url = request.args.get("url")
    if not url:
        return "Missing url parameter", 400

    headers = get_headers(referer=urlparse(url).netloc)

    try:
        r = requests.get(url, headers=headers, stream=True, timeout=20)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        return "Failed to fetch segment", 502

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
    app.run(host="0.0.0.0", port=7860, debug=False)
