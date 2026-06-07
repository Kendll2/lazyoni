from fastapi import FastAPI
from mediaflow_proxy.main import app as mediaflow_app
import httpx

# Initialize the main FastAPI application
main_app = FastAPI()

# === ZORUNLU HEADER'LAR ===
DEFAULT_HEADERS = {
    "Origin": "https://inattv1312.xyz",
    "Referer": "https://inattv1312.xyz/",          # Bu çok önemli, zorunlu
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

# httpx Client'larını patch'leyerek her outgoing request'e header ekliyoruz
original_client = httpx.Client
original_async_client = httpx.AsyncClient

def patched_client(*args, **kwargs):
    headers = kwargs.pop("headers", {}) or {}
    # Mevcut header'ları koru, bizimkileri zorunlu olarak ekle/override et
    headers.update(DEFAULT_HEADERS)
    kwargs["headers"] = headers
    return original_client(*args, **kwargs)

def patched_async_client(*args, **kwargs):
    headers = kwargs.pop("headers", {}) or {}
    headers.update(DEFAULT_HEADERS)
    kwargs["headers"] = headers
    return original_async_client(*args, **kwargs)

# Patch'leri uygula
httpx.Client = patched_client
httpx.AsyncClient = patched_async_client

# Manually add only non-static routes from mediaflow_app
for route in mediaflow_app.routes:
    if route.path != "/":  # Exclude the static file path
        main_app.router.routes.append(route)

# Run the main app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(main_app, host="0.0.0.0", port=8080)
