from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import Request, urlopen

HOST, PORT = "127.0.0.1", 8765
_cache: dict[str, tuple[float, object]] = {}
_cooldowns: dict[str, float] = {}
CACHE_DIR = Path(__file__).resolve().parent / ".osd-cache"
GDELT_COOLDOWN_SECONDS = 900


def _cache_path(url: str) -> Path:
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    return CACHE_DIR / f"{key}.json"


def _load_persistent(url: str, ttl: int):
    try:
        saved = json.loads(_cache_path(url).read_text(encoding="utf-8"))
        _cooldowns[url] = float(saved.get("retry_after", 0))
        fetched_at = float(saved["fetched_at"])
        data = saved["data"]
        _cache[url] = (fetched_at + ttl, data)
        return _cache[url]
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _save_persistent(url: str, data, fetched_at: float, retry_after: float = 0):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _cache_path(url)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({
        "fetched_at": fetched_at,
        "retry_after": retry_after,
        "data": data,
    }), encoding="utf-8")
    temporary.replace(path)


def fetch_json(url: str, ttl: int = 300, persistent: bool = False):
    cached = _cache.get(url)
    if cached is None and persistent:
        cached = _load_persistent(url, ttl)
    now = time.time()
    if cached and cached[0] > now:
        return cached[1]

    cooldown = _cooldowns.get(url, 0)
    if cooldown > now:
        if cached:
            print(f"GDELT cooldown active; serving saved news for another {int(cooldown-now)}s", flush=True)
            _cache[url] = (cooldown, cached[1])
            return cached[1]
        raise RuntimeError(f"GDELT cooldown active for another {int(cooldown-now)} seconds")

    req = Request(url, headers={"User-Agent": "OpenSignalDesk/0.3 (local personal dashboard)"})
    try:
        with urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        fetched_at = time.time()
        _cache[url] = (fetched_at + ttl, data)
        _cooldowns[url] = 0
        if persistent:
            _save_persistent(url, data, fetched_at)
        return data
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        retry_seconds = GDELT_COOLDOWN_SECONDS
        if isinstance(exc, HTTPError) and exc.headers:
            try:
                retry_seconds = max(retry_seconds, int(exc.headers.get("Retry-After", "0")))
            except ValueError:
                pass
        retry_at = time.time() + retry_seconds
        if persistent:
            _cooldowns[url] = retry_at
            if cached:
                _save_persistent(url, cached[1], time.time() - ttl - 1, retry_at)
            else:
                # Persist the cooldown even before the first successful response.
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                path = _cache_path(url)
                temporary = path.with_suffix(".tmp")
                temporary.write_text(json.dumps({"retry_after": retry_at}), encoding="utf-8")
                temporary.replace(path)
        if cached:
            print(f"Upstream temporarily unavailable; serving cached data: {exc}", flush=True)
            _cache[url] = (retry_at, cached[1])
            if persistent:
                _save_persistent(url, cached[1], time.time() - ttl - 1, retry_at)
            return cached[1]
        raise


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
        elif self.path.startswith("/api/earthquakes"):
            self.proxy("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson", 180)
        elif self.path.startswith("/api/weather"):
            self.weather()
        elif self.path.startswith("/api/gdelt"):
            self.gdelt()
        else:
            super().do_GET()

    def json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def proxy(self, url, ttl=300, persistent=False):
        try:
            self.json_response(fetch_json(url, ttl, persistent=persistent))
        except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as exc:
            print(f"Source request failed for {url}: {exc}", flush=True)
            self.json_response({"error": str(exc)}, 502)

    def weather(self):
        params = parse_qs(urlsplit(self.path).query)
        try:
            lat = max(-90, min(90, float(params.get("lat", ["52.37"])[0])))
            lon = max(-180, min(180, float(params.get("lon", ["4.90"])[0])))
            query = urlencode({
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "auto",
            })
            self.json_response(fetch_json("https://api.open-meteo.com/v1/forecast?" + query, 600))
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            print(f"Weather request failed: {exc}", flush=True)
            self.json_response({"error": str(exc)}, 502)

    def gdelt(self):
        query = urlencode({
            "query": "(conflict OR protest OR attack OR earthquake OR sanctions)",
            "mode": "artlist",
            "maxrecords": "30",
            "format": "json",
            "sort": "DateDesc",
            "timespan": "1day",
        })
        self.proxy("https://api.gdeltproject.org/api/v2/doc/doc?" + query, 900, persistent=True)


if __name__ == "__main__":
    print(f"Open Signal Desk is running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
