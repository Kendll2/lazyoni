from flask import Flask, Response
import requests

app = Flask(__name__)

STREAM_URL = "https://2i4.d72577a9dd0ec71.cfd/b2/mono.m3u8"

@app.route("/live/<channel_uid>")
def live(channel_uid):
    r = requests.get(
        STREAM_URL,
        headers={
            "Origin": "https://inattv1312.xyz",
            "Referer": "https://inattv1312.xyz/",
            "User-Agent": "Mozilla/5.0"
        }
    )

    return Response(
        r.text,
        content_type="application/vnd.apple.mpegurl"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
