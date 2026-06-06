from flask import Flask, Response, request
import requests
from urllib.parse import urljoin, urlparse
import time

app = Flask(__name__)

def get_headers(referer):
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": referer,
        "Origin": referer.rstrip('/'),
        "Connection": "keep-alive",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    }

@app.route("/proxy/stream")
def stream_proxy():
    m3u8_url = request.args.get("d")
    if not m3u8_url or not m3u8_url.startswith("https://"):
        return "Invalid or missing ?d= parameter", 400

    referer = urlparse(m3u8_url).scheme + "://" + urlparse(m3u8_url).netloc + "/"
    headers = get_headers(referer)

    session = requests.Session()
    session.headers.update(headers)

    try:
        r = session.get(m3u8_url, timeout=15)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Playlist fetch failed: {str(e)}", 502

    content = r.text
    lines = []
    base_url = m3u8_url.rsplit('/', 1)[0] + '/'

    for line in content.splitlines():
        line = line.strip()
        if not line:
            lines.append(line)
            continue
        if line.startswith("#"):
            lines.append(line)
        else:
            if line.startswith(("http://", "https://")):
                segment_url = line
            else:
                segment_url = urljoin(base_url, line)
            lines.append(f"/proxy/segment?url={segment_url}")

    return Response("\n".join(lines), content_type="application/vnd.apple.mpegurl")


@app.route("/proxy/segment")
def segment_proxy():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400

    referer = urlparse(url).scheme + "://" + urlparse(url).netloc + "/"
    headers = get_headers(referer)

    session = requests.Session()
    session.headers.update(headers)

    try:
        r = session.get(url, stream=True, timeout=15)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Segment fetch failed: {str(e)}", 502

    def generate():
        try:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        except Exception:
            pass  # bağlantı kesilirse sessizce bitir

    return Response(
        generate(),
        content_type=r.headers.get("Content-Type", "video/mp2t"),
        headers={
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "no-cache"
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
