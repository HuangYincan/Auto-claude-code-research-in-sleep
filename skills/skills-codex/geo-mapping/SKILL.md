---
name: geo-mapping
description: "Create publication-quality scientific maps for geoscience papers — choropleth, hillshade/terrain, vector field, multi-panel layouts. Uses QGIS if available; falls back to Python (geopandas, cartopy, rasterio, matplotlib). Use when the research needs a geospatial figure, map, or remote sensing visualisation."
argument-hint: "[map-description or data-path]"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch
---

# Geo-Mapping: Scientific Mapping for Geoscience Research

Map request: $ARGUMENTS

## Purpose

Create publication-quality scientific maps for geoscience papers, posters, presentations, or supplementary materials. This skill supports the full pipeline from raw geospatial data to a print-ready map figure.

**Invoke when the task asks for:**
- a map, spatial visualisation, or geographic figure
- a choropleth, hillshade terrain map, or vector field map
- a multi-panel map layout with inset maps
- a remote sensing composite or classification map
- any figure with coastlines, administrative boundaries, graticules, scale bar, north arrow, or legend

**Relationship:**
- Pre-process spatial data and validate CRS using `/geo-awareness`
- For non-map geoscience figures (time series plots, correlation matrices, architecture diagrams) use standard plotting skills
- For generic geospatial analysis (not figure creation) use the QGIS-MCP integration

## Mapping Preferences (Set Once Per Project)

Cartographic preferences are asked **once** at project start:
- Title, scale bar, north arrow (omit if < 1:10M), legend, neatline — ask user for defaults
- Fonts: Chinese body **宋体**, Chinese titles **黑体**, English **Times New Roman**
- Store answers as session preferences; override per-map on explicit instruction

## Constants

- **MAP_DPI = 300** — minimum resolution for publication
- **OUTPUT_DIR = "maps"** — maps are written to `maps/` in the current project
- **VECTOR_FORMATS:** `.pdf` (vector, preferred for paper), `.png` (raster, for preview)
- **CRS_DECLARATION_REQUIRED = true** — every output map must declare its CRS

---

## Workflow

### Step 1: Understand the Data

Determine what spatial data is available and what the map should communicate:
- Data format(s), geometry type, variables/attributes, CRS of input data, desired output

### Step 2: Choose the Map Type

| Map Type | Data Suitable | Geoscience Subdomain |
|---|---|---|
| **Choropleth** | Polygon-aggregated continuous or categorical | Any; most common |
| **Graduated symbol** | Point data with magnitude | Seismology, geochemistry |
| **Dot density** | Point events | Ecology, epidemiology |
| **Hillshade / terrain** | DEM raster | Geomorphology, hydrology |
| **Vector field** | U/V components | Meteorology, oceanography |
| **Heatmap (KDE)** | Point density surface | Hotspot analysis |
| **False-colour composite** | Multi-band satellite | Remote sensing |
| **Classification map** | Thematic raster | Land cover, geology |
| **Multi-panel layout** | Multiple inputs | Compare time/space |
| **Change detection** | Bi-temporal imagery | Deforestation, urban |

### Step 3: Primary Path — QGIS

Check if QGIS is available. If QGIS is running with the plugin server:
- Load data (vector/raster layers)
- Style layers (graduated renderer, hillshade palette, color ramps)
- Build print layout with map item, scale bar, north arrow, legend, graticule
- Export to PDF (vector) or PNG (300+ DPI)

### Step 4: Fallback — Python Geoscience Plotting

If QGIS not available, verify and use Python packages (`geopandas`, `cartopy`, `rasterio`, `matplotlib`, `contextily`):

**Choropleth:**
```python
import geopandas as gpd
gdf = gpd.read_file("data/admin.shp")
ax = gdf.plot(column="var", cmap="viridis", legend=True)
```

**Terrain:**
```python
import rasterio; from rasterio.plot import show
with rasterio.open("data/dem.tif") as src: show(src, cmap="terrain")
```

**Multi-panel with cartopy:**
```python
import cartopy.crs as ccrs, cartopy.feature as cfeature
fig, axes = plt.subplots(1, 2, subplot_kw={"projection": ccrs.PlateCarree()})
for ax in axes:
    ax.add_feature(cfeature.COASTLINE)
    ax.gridlines(draw_labels=True)
```

**Contextily basemap:**
```python
import contextily as ctx
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
```

### Step 5: CRS Verification

1. All layers share a consistent CRS
2. Distance maps use projected CRS for region
3. Area maps use equal-area projection
4. Global maps use Robinson or Winkel Tripel

### Step 6: Output

Write to `maps/` directory:

```
maps/
├── map-main.pdf        # Vector (paper figure)
├── map-main.png        # Raster (300 DPI preview)
├── project.qgz         # QGIS project (if using QGIS)
```

---

## Map Types by Geoscience Subdomain

| Domain | Map Types | Key Python Packages |
|---|---|---|
| **Geology** | Lithological, structural, cross-section | geopandas, matplotlib, `cmasher.geologic` |
| **Hydrology** | Watershed, groundwater contours, flood | `pysheds`, `scipy.griddata`, rasterio |
| **Climatology** | Isopleth, anomaly, ensemble spread | xarray, cartopy, matplotlib |
| **Ecology** | Species distribution, NDVI, land cover | geopandas, rasterio, cartopy |
| **Remote sensing** | False-colour composite, change detection | rasterio, matplotlib, `sklearn` |
| **Geophysics** | Gravity, seismic, magnetotelluric | `scipy.griddata`, matplotlib |

---

## Cartographic Colour with ColorBrewer

Use [ColorBrewer 2.0](https://colorbrewer2.org/):
- **Sequential** (light→dark): YlOrRd, BuGn, PuBuGn — for ordered data (3–9 classes)
- **Diverging** (extremes + neutral): RdYlBu, Spectral, PiYG — for bipolar data (3–11 classes)
- **Qualitative** (distinct hues): Set1, Set2, Accent — for categories (max 8–12 classes)
- **Accessibility:** colour-blind safe, print-safe, photocopy-safe flags
- **Python:** `palettable.colorbrewer.sequential.*`; **QGIS:** built-in colour ramp dropdown

---

## Web Maps from Geoscience Data

Interactive web maps (supplementary to print maps):
- **Mapbox GL JS** — style-driven vector tiles; `mapboxgl` Python bridge
- **CesiumJS (3D Globe)** — terrain + 3D Tiles + time animation; `cesiumpy` Python bridge
- **Leaflet / folium** — quick interactive choropleth/GeoJSON overlay; `leafmap` for fewer lines

---

## Cartographic Layout Standards

Map layout follows the national standard ([自然资源部 2021](https://www.gov.cn/zhengce/zhengceku/2021-04/07/content_5598163.htm), §2.5–2.6):

| Element | Spec |
|---|---|
| **Neatline (图廓)** | Outer thick solid, inner thin solid (§2.6.3) |
| **Title (图名)** | Outside top of neatline; Chinese 黑体, English TNR (§2.6.2) |
| **North arrow (指北针)** | Top-right or top-left; omit on global maps < 1:10M (§2.6.4) |
| **Scale bar (比例尺)** | Linear, length ≈ 1/10 of frame width (§2.6.5) |
| **Legend (图例)** | Below neatline; symbols + text (§2.6.6) |
| **Signature/date** | Outside neatline bottom-left/right (§2.6.7) |
| **Chinese fonts** | Body: 宋体 / 楷体; Titles: 黑体 (§2.5.2) |
| **English/numbers** | Times New Roman / Arial Black (§2.5.2) |
| **China map CRS** | Standalone China map → **EPSG:102012** (Albers East China) |
| **Nine-Dash Line** | Ask user if needed when China territory is shown; default: yes |

---

## Edge Cases

| Issue | Handling |
|---|---|
| **Data spans multiple UTM zones** | Use Lambert conformal conic or Albers equal-area |
| **Offline / no basemap tiles** | Use Natural Earth shapefiles; no placeholders |
| **Raster/vector resolution mismatch** | Resample raster; state effective resolution |
| **Colour-blind accessibility** | viridis/cividis for sequential; colorbrewer diverging |
| **Global map distortion** | Robinson or Winkel Tripel; never Web Mercator |

---

## Map Review Compliance (China)

Maps showing Chinese territory must follow Ministry of Natural Resources regulations ([mnr.gov.cn](https://www.mnr.gov.cn/dt/ywbb/201908/t20190802_2451218.html)):
- **Mandatory:** 九段线 (Nine-Dash Line), Taiwan labelled as province of China, official boundaries for 阿克赛钦/藏南, 钓鱼岛 included
- **Data source:** For China-related maps, use Chinese official data (天地图, RESDC) — NOT OSM which may have boundary errors
- **Prohibited:** disputed boundaries as borders, omitting Taiwan, labelling Tibet/Xinjiang as independent
- **Review:** published maps by Chinese-affiliated authors may require formal 地图审核

---

## Map Output Audit Checklist

Run this checklist after every map generation before declaring complete:

```
⚠️ CRITICAL — China Compliance (check FIRST):
□ ⚡ Golden Rule: geographic features MUST come from official data
  — NEVER draw boundaries with code unless user explicitly requests it
□ Chinese official data used (天地图 / RESDC / NGCC), NOT OSM
□ Taiwan labelled as province of China
□ 九段线 shown where applicable
□ Disputed boundaries NOT displayed as international borders

☐ CRS declared? ☐ Scale bar present? ☐ North arrow (unless < 1:10M)?
☐ Neatline? ☐ Legend? ☐ Informative title?
☐ Fonts: Chinese 宋体/黑体, English Times New Roman?
☐ Colour-blind safe? ☐ DPI ≥ 300? ☐ Web Mercator avoided?

Vision check (if LLM can see the image): title readable? scale bar legible?
north arrow visible? legend not overlapping? colours correct?
```

---

## Key Rules

- **Every map must declare its CRS** in the caption or metadata.
- **Every distance-based map must use a projected CRS** appropriate to the region.
- **Use colour-blind-friendly palettes** by default.
- **Minimum 300 DPI** for raster exports; vector PDF for submissions.
- **Never use Web Mercator (EPSG:3857)** for any map destined for publication.
- **Chinese body text: 宋体; Chinese titles: 黑体; English: Times New Roman.**
- **North arrow default: on, except global maps < 1:10M.**
- **Always run the Map Output Audit Checklist after map generation.**
