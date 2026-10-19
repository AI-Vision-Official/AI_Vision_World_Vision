# Open Signal Desk

A personal, English-language OSINT and world-monitoring dashboard starter. It runs on Windows on `localhost`, has no paid API keys, and stores widget preferences in your browser. It is inspired by the modular idea behind World Monitor and the research-tool discovery approach of Bellingcat; it is an independent starter, not an official fork.

## Start on Windows

1. Install Python 3.10 or newer if it is not already installed.
2. Open this folder in File Explorer.
3. Double-click `start.bat`.
4. The dashboard opens at `http://127.0.0.1:8765`.

To stop it, close the console window. The server binds only to the local computer.

## Included modules

- **GDELT headlines:** recent article links for a broad global query; the free public endpoint can change and is not a curated breaking-news wire.
- **USGS earthquakes:** public GeoJSON feed for the past day.
- **Open-Meteo weather:** current conditions for editable latitude/longitude; free for non-commercial use under its published terms. No key required.
- **Customization:** hide/show widgets and save the selection and coordinates in browser local storage.
- **Research links:** Bellingcat's Online Investigation Toolkit, World Monitor source repository, and an MCP server directory.

The dashboard does not scrape social networks, bypass access controls, geolocate people, or present unverified reports as facts. It links to source articles so a researcher can verify them independently.

## Cost and limits

Software and included sources currently require no paid API key. They still depend on an internet connection and third-party availability, fair-use limits, and source-specific terms. GDELT and USGS can throttle or change endpoints. Open-Meteo's free hosted API is intended for non-commercial use; commercial use or high volume may require a paid plan. This local app does not provide guaranteed uptime or archive upstream data.

Potential free additions (check current terms before enabling):

- **RSS / Atom feeds:** add trusted newsrooms, government, and humanitarian-monitoring feeds.
- **NASA FIRMS:** useful satellite fire detections; requires a free account/API key and must be protected locally.
- **GDACS:** international disaster alerts; use its official feed and attribution guidance.
- **OpenStreetMap:** maps and geocoding; public tile servers have a usage policy, so do not bulk-download or rely on them for heavy traffic.
- **MCP servers:** optional local tools for browsing, maps, or research. Each server may access files or network services; install only projects you trust and inspect their permissions.

Avoid placing API keys in front-end JavaScript or publishing this local server to the internet. If adding key-based sources later, keep credentials in a local `.env` file that is excluded from version control.

## Suggested next steps

1. Pick watch topics and a few trusted primary-source RSS feeds.
2. Add a feed registry (`sources.json`) with name, URL, category, refresh interval, and attribution.
3. Add a map using a provider whose tile terms fit your use; keep the layer optional.
4. Add event filters and saved watchlists, then optionally SQLite for a local evidence log.
5. For a more complete map-first product, evaluate self-hosting World Monitor itself. Its source is AGPL-3.0-only; review the license before modifying or redistributing it. Its hosted APIs are a separate service and are not assumed free here.

## References

- [World Monitor repository](https://github.com/koala73/worldmonitor) and [license notes](https://github.com/koala73/worldmonitor/blob/main/docs/license.mdx)
- [Bellingcat Online Investigation Toolkit](https://bellingcat.gitbook.io/toolkit)
- [USGS Earthquake Catalog feeds](https://earthquake.usgs.gov/earthquakes/feed/)
- [USGS FDSN API documentation](https://earthquake.usgs.gov/fdsnws/event/1/)
- [Open-Meteo API and terms](https://open-meteo.com/en/terms)
- [GDELT Project](https://www.gdeltproject.org/)
- [MCP server directory](https://github.com/punkpeye/awesome-mcp-servers)
