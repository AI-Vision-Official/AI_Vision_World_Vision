# Open Signal Desk — layout playground

Replace the existing `index.html` in `J:\GIT\PROJECTS\AI_Vision_World_Vision` with the supplied file. Keep your current `server.py` (including the GDELT cache fallback) and `start.bat`.

This version adds a three-column responsive dashboard, draggable cards, saved card order and visibility, a 2D map and 3D globe, and USGS earthquake markers on both maps. It remains a local app with no paid map/API key.

## Map credits and limits

- Map rendering: [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/), open source, loaded from the UNPKG CDN.
- Map tiles and data: [© OpenStreetMap contributors](https://www.openstreetmap.org/copyright), Open Database License (ODbL). Attribution appears on both maps.
- The public OSM tile service is best-effort and governed by its [tile usage policy](https://operations.osmfoundation.org/policies/tiles/). This is suitable for light personal exploration; do not bulk download, prefetch, or assume guaranteed service. Choose another tile provider or host tiles yourself before heavy use.
- Event markers and the event list: [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/earthquakes/feed/).
- Headlines: [GDELT Project](https://www.gdeltproject.org/).
- Weather: [Open-Meteo](https://open-meteo.com/en/terms).

The browser needs internet access for the MapLibre library, map tiles, and public feeds. The local Python server serves the page and proxies data requests; it does not store a research archive.

## Exploring the layout

Use **Customize** to hide/show widgets and set weather coordinates. Drag any card by its header to reorder it; the order and visibility persist in browser local storage. Edit the CSS variables and grid span classes near the top of `index.html` to experiment with colors and card sizing.

For less dependence on OSM's public tile service, swap the raster tile URL for a provider whose terms suit your needs or run your own tile server. Keep the provider's attribution visible.
