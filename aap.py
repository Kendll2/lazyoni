from flask import Flask, Response, request
import requests
from urllib.parse import urljoin
import random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
]

def get_headers(referer):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/vnd.apple.mpegurl, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": referer,
        "Origin": referer.rstrip('/'),
        "Connection": "keep-alive",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

@app.route("/proxy/stream")
def stream_proxy():
    m3u8_url = request.args.get("d")
    if not m3u8_url:
        return "Missing ?d= parameter", 400

    print(f"[LOG] Playlist: {m3u8_url}")

    referer = "https://inattv1312.xyz/"   # Ana site refereri
    headers = get_headers(referer)

    session = requests.Session()
    session.headers.update(headers)

    try:
        r = session.get(m3u8_url, timeout=20, allow_redirects=True)
        print(f"[LOG] Status: {r.status_code} - {r.reason}")
        
        if r.status_code == 403:
            return "403 Forbidden - Site koruması çok güçlü.", 403
            
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return f"Cannot connect to source: {str(e)}", 502

    # M3U8 içeriğini proxy için yeniden yaz
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
            segment_url = line if line.startswith(("http://", "https://")) else urljoin(base_url, line)
            lines.append(f"/proxy/segment?url={segment_url}")

    return Response("\n".join(lines), content_type="application/vnd.apple.mpegurl")


@app.route("/proxy/segment")
def segment_proxy():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400

    referer = "https://inattv1312.xyz/"
    headers = get_headers(referer)

    session = requests.Session()
    session.headers.update(headers)

    try:
        r = session.get(url, stream=True, timeout=25)
        r.raise_for_status()
    except Exception as e:
        print(f"[Segment Error] {str(e)}")
        return "Segment fetch failed", 502

    def generate():
        for chunk in r.iter_content(chunk_size=16384):
            if chunk:
                yield chunk

    return Response(
        generate(),
        content_type=r.headers.get("Content-Type", "video/mp2t"),
        headers={"Access-Control-Allow-Origin": "*"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
