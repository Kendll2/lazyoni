from flask import Flask, redirect, request
import requests

app = Flask(__name__)

API_BASE = "https://core-api.kablowebtv.com/api"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJjZ2QiOiIwOTNENzIwQS01MDJDLTQxRUQtQTgwRi0yQjgxNjk4NEZCOTUiLCJkaSI6IjcxYzZkZTE5LWExMzAtNGY5Yi04ODFkLTZiMjkzZGExNjk5NyIsImFwdiI6IjEuMC4wIiwiZW52IjoiTElWRSIsImFibiI6IjEwMDAiLCJzcGdkIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwiaWNoIjoiMCIsInNnZCI6ImIyNTk1ZjhhLWRlOTUtNDI4MC1hNDU3LTk0ZTA2MmRjZTg1MiIsImlkbSI6IjAiLCJkY3QiOiIzRUY3NSIsImlhIjoiODguMjQzLjY3LjExNyIsImNzaCI6IlRSS1NUIiwiaXBiIjoiMCJ9.7-F3sUNEgPTKRw5FGuHpoRHuCYEbmwkFikqduSQhbf4"  # localStorage'daki shared-token-r1

@app.route("/live/<channel_uid>")
def live(channel_uid):
    try:
        r = requests.get(
            f"{API_BASE}/channels/detail?channelUId={channel_uid}",
            headers={
                "Authorization": f"Bearer {TOKEN}",
                "Origin": "https://www.tvheryerde.com.tr",
                "Referer": "https://www.tvheryerde.com.tr/",
            }
        )
        return str(r.json())
        return redirect(url)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
