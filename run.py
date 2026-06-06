from flask import Flask, Response, request
import requests
from urllib.parse import urljoin

app = Flask(__name__)

ORIGIN = "https://example.com/live/"  # HLS kaynağın kökü

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*"
}

# -------------------------
# M3U8 PLAYLIST PROXY
# -------------------------
@app.route("/live/<path:playlist>")
def playlist_proxy(playlist):

    url = urljoin(ORIGIN, playlist)

    r = requests.get(url, headers=HEADERS, timeout=15)

    content = r.text

    # Segment URL'lerini rewrite et
    lines = []
    for line in content.splitlines():
        if line and not line.startswith("#"):
            # segmentleri kendi serverına yönlendir
            line = f"/segment?url={urljoin(ORIGIN, line)}"
        lines.append(line)

    modified = "\n".join(lines)

    return Response(modified, content_type="application/vnd.apple.mpegurl")


# -------------------------
# SEGMENT PROXY
# -------------------------
@app.route("/segment")
def segment_proxy():

    url = request.args.get("url")

    if not url:
        return "Missing URL", 400

    r = requests.get(url, headers=HEADERS, stream=True, timeout=15)

    return Response(
        r.content,
        content_type=r.headers.get("Content-Type", "video/mp2t")
    )


# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
