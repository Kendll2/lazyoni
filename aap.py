from fastapi import FastAPI
from mediaflow_proxy.main import app as mediaflow_app
import httpx

# Initialize the main FastAPI application
main_app = FastAPI()

# === STREAM İÇİN ZORUNLU HEADER'LAR ===
STREAM_HEADERS = {
    "Origin": "https://inattv1312.xyz",
    "Referer": "https://inattv1312.xyz/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

# Global httpx patch (tüm istekler için)
original_async_client = httpx.AsyncClient

def patched_async_client(*args, **kwargs):
    headers = kwargs.pop("headers", {}) or {}
    # STREAM_HEADERS her zaman eklensin / override edilsin
    headers.update(STREAM_HEADERS)
    kwargs["headers"] = headers
    return original_async_client(*args, **kwargs)

httpx.AsyncClient = patched_async_client

# Manually add only non-static routes from mediaflow_app
for route in mediaflow_app.routes:
    if route.path != "/":
        main_app.router.routes.append(route)

# Run the main app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main_app, host="0.0.0.0", port=8080)
