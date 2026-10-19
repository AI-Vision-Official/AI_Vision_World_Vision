from __future__ import annotations

import json
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HOST, PORT = "127.0.0.1", 8765
_cache: dict[str, tuple[float, object]] = {}


def fetch_json(url: str, ttl: int = 300):
    cached = _cache.get(url)
    if cached and cached[0] > time.time():
        return cached[1]
    req = Request(url, headers={"User-Agent": "OpenSignalDesk/0.1 (local personal dashboard)"})
    with urlopen(req, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    _cache[url] = (time.time() + ttl, data)
    return data


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/earthquakes"):
            self.proxy("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")
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

    def proxy(self, url):
        try:
            self.json_response(fetch_json(url, 120))
        except (URLError, TimeoutError, ValueError) as exc:
            self.json_response({"error": str(exc)}, 502)

    def weather(self):
        from urllib.parse import parse_qs, urlsplit
        params = parse_qs(urlsplit(self.path).query)
        try:
            lat = max(-90, min(90, float(params.get("lat", ["52.37"])[0])))
            lon = max(-180, min(180, float(params.get("lon", ["4.90"])[0])))
            query = urlencode({"latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code", "timezone": "auto"})
            self.json_response(fetch_json("https://api.open-meteo.com/v1/forecast?" + query, 600))
        except (URLError, TimeoutError, ValueError) as exc:
            self.json_response({"error": str(exc)}, 502)

    def gdelt(self):
        query = urlencode({"query": "(conflict OR protest OR attack OR earthquake OR sanctions)", "mode": "artlist", "maxrecords": "30", "format": "json", "sort": "DateDesc"})
        self.proxy("https://api.gdeltproject.org/api/v2/doc/doc?" + query)


if __name__ == "__main__":
    print(f"Open Signal Desk is running at http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
