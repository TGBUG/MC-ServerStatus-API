from fastapi import FastAPI, HTTPException, Response, Query
from starlette.responses import FileResponse, JSONResponse
from mcstatus import JavaServer
from utils.cache import get_cached_json, cache_json, get_cached_img_path, cache_img_meta, clear_expired_img_cache, generate_cache_key, background_cache_cleaner
from utils.image import render_image
from utils.dns import resolve_srv
from security.ratelimit import global_limiter
from config import CACHE_TTL_SECONDS, IMG_CACHE_DIR
import os

app = FastAPI()

if not os.path.exists(IMG_CACHE_DIR):
    os.makedirs(IMG_CACHE_DIR, exist_ok=True)

background_cache_cleaner(interval_seconds=300)

@app.get("/json/{address}")
async def json_status(address: str):
    if not global_limiter.allow():
        raise HTTPException(status_code=403, detail="Rate limit exceeded")

    ip, port, original_address = parse_address(address)
    cache_key = f"{ip}:{port}"
    cached = get_cached_json(cache_key)
    if cached:
        return JSONResponse(cached)

    try:
        server = JavaServer.lookup(f"{ip}:{port}")
        status = server.status()
        data = {
            "host": ip,
            "port": port,
            "players_online": status.players.online,
            "players_max": status.players.max,
            "version_name": str(status.version.name or "Unknown"),
            "version_protocol": status.version.protocol,
            "motd": status.description.get("text") if isinstance(status.description, dict) else str(status.description),
            "online": True,
            "latency": status.latency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server status error: {str(e)}")

    cache_json(cache_key, data)
    return JSONResponse(data)


@app.get("/img/{address}")
@app.get("/img/{address}/{number}")
async def img_status(address: str, number: int = None, server_name: str = Query(None)):
    if not global_limiter.allow():
        raise HTTPException(status_code=403, detail="Rate limit exceeded")

    ip, port, original_address = parse_address(address)

    cache_key = generate_cache_key("img", address, number, server_name)
    path = get_cached_img_path(cache_key)
    if path and os.path.exists(path):
        return FileResponse(path, media_type="image/png")

    json_cache_key = f"{ip}:{port}"
    data = get_cached_json(json_cache_key)
    if not data:
        server = JavaServer.lookup(f"{ip}:{port}")
        status = server.status()
        data = {
            "host": ip,
            "port": port,
            "players_online": status.players.online,
            "players_max": status.players.max,
            "version_name": str(status.version.name or "Unknown"),
            "version_protocol": status.version.protocol,
            "motd": status.description.get("text") if isinstance(status.description, dict) else str(status.description),
            "online": True
        }
        cache_json(json_cache_key, data)
    else:
        data["online"] = True

    try:
        path = render_image(data, image_number=number, cache_key=cache_key, server_name=server_name, original_address=original_address)
    except Exception as e:
        data["online"] = False
        path = render_image(data, image_number=number, cache_key=cache_key, server_name=server_name, original_address=original_address)

    cache_img_meta(cache_key, path)
    return FileResponse(path, media_type="image/png")

def parse_address(address: str):
    if ':' in address:
        ip, port = address.split(":")
        return ip, int(port), address
    else:
        resolved_ip, resolved_port = resolve_srv(address)
        if not resolved_port:
            raise HTTPException(status_code=400, detail="Missing port and SRV not found")
        return resolved_ip, resolved_port, address
