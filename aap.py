from flask import Flask, Response, request
import requests
from urllib.parse import urljoin
import random

app = Flask(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
]

def get_headers(referer):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/vnd.apple.mpegurl, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
        "Referer": referer,
        "Origin": referer.rstrip('/'),
        "Connection": "keep-alive",
    }

@app.route("/proxy/stream")
def stream_proxy():
    m3u8_url = request.args.get("d")
    if not m3u8_url:
        return "Missing ?d= parameter", 400

    print(f"[LOG] Playlist: {m3u8_url}")
    referer = "https://inattv1312.xyz/"
    headers = get_headers(referer)

    session = requests.Session()
    session.headers.update(headers)

    try:
        r = session.get(m3u8_url, timeout=20)
        print(f"[LOG] Status: {r.status_code} {r.reason}")
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return f"Cannot connect to source: {str(e)}", 502

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

    headers = get_headers("https://inattv1312.xyz/")

    session = requests.Session()
    session.headers.update(headers)

    try:
        r = session.get(url, stream=True, timeout=25)
        r.raise_for_status()
    except Exception as e:
        print(f"[Segment Error] {str(e)}")
        return "Segment failed", 502

    def generate():
        for chunk in r.iter_content(chunk_size=16384):
            if chunk:
                yield chunk

    return Response(generate(), content_type="video/mp2t", headers={"Access-Control-Allow-Origin": "*"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
