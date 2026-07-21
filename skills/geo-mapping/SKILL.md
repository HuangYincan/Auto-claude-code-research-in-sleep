---
name: geo-mapping
description: "Create publication-quality scientific maps for geoscience papers — choropleth, hillshade/terrain, vector field, multi-panel layouts. Uses QGIS via `/qgis-mcp` if available; falls back to Python (geopandas, cartopy, rasterio, matplotlib). Use when the research needs a geospatial figure, map, or remote sensing visualisation."
argument-hint: "[map-description or data-path]"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Skill(qgis-mcp), mcp__codex__codex
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
- For non-map geoscience figures (time series plots, correlation matrices, architecture diagrams) use standard ARIS plotting skills
- For generic geospatial analysis (not figure creation) use `/qgis-mcp`

## Mapping Preferences (Set Once Per Project)

Since ARIS is a long-running pipeline, cartographic preferences are asked **once** at the
start of the project (or the first time a map is needed), then applied consistently to
all maps in the session. The user can override on a specific map.

**Ask the user at project start:**
```
Which map elements do you want by default?
  ☐ Title (图名) — default ON
  ☐ Scale bar (比例尺) — default ON
  ☐ North arrow (指北针) — default ON (except global maps < 1:10M)
  ☐ Legend (图例) — default ON
  ☐ Neatline / map frame (图廓) — default ON
  ☐ Signature & date — default ON
  Font — Chinese: 宋体 (body) / 黑体 (titles); English: Times New Roman
  Colour palette preference? (default: colour-blind safe)
```

Store the answers as session-level preferences and apply them to every map in this project.

## Constants

- **MAP_DPI = 300** — minimum resolution for publication
- **OUTPUT_DIR = "maps"** — maps are written to `maps/` in the current project
- **VECTOR_FORMATS:** `.pdf` (vector, preferred for paper), `.png` (raster, for preview)
- **CRS_DECLARATION_REQUIRED = true** — every output map must declare its CRS

---

## Workflow

### Step 1: Understand the Data

Determine what spatial data is available and what the map should communicate:

- **Data format(s):** vector (Shapefile, GeoPackage, GeoJSON) or raster (GeoTIFF, NetCDF)
- **Geometry type:** points, lines, polygons, continuous rasters
- **Variables / attributes:** what to map (e.g. population density, elevation, temperature anomaly, land cover class)
- **CRS of input data:** verify before any reprojection
- **Desired output:** paper figure, presentation slide, interactive web map, supplementary material

### Step 2: Choose the Map Type

| Map Type | Data Suitable | Geoscience Subdomain |
|---|---|---|
| **Choropleth** | Polygon-aggregated continuous or categorical | Any; most common (demographics, hazards, climate zones) |
| **Graduated symbol** | Point data with magnitude | Seismology (earthquake magnitudes), geochemistry (sample concentrations) |
| **Dot density** | Point events | Ecology (species occurrences), epidemiology |
| **Hillshade / terrain** | DEM raster | Geomorphology, hydrology, structural geology |
| **Vector field** | U/V components | Meteorology (wind), oceanography (currents), geophysics (magnetic) |
| **Heatmap (KDE)** | Point density surface | Hotspot analysis, crime mapping, point cluster visualisation |
| **False-colour composite** | Multi-band satellite | Remote sensing (NIR-R-G, SWIR-NIR-R composites) |
| **Classification map** | Thematic raster | Land cover, geological units, soil types |
| **Multi-panel layout** | Multiple inputs | Compare time steps, regions, methods; context + detail maps |
| **Change detection** | Bi-temporal imagery | Deforestation, urban expansion, flood mapping |

### Step 3: Primary Path — QGIS via `/qgis-mcp`

Check if QGIS MCP is available:

```bash
claude mcp list | grep qgis
```

If QGIS is running with the plugin server started:

#### 3a. Load or create a QGIS project

```
/qgis-mcp "Load data from ./data/ and create a map project"
```

The `/qgis-mcp` skill handles layer loading (`add_vector_layer`, `add_raster_layer`), project management (`create_new_project`, `load_project`), and QGIS connectivity.

#### 3b. Style the layers

Use `execute_processing` or `execute_code` for QGIS-native styling:

- **Choropleth:** `qgis:setlayerstyle` or PyQGIS `QgsGraduatedSymbolRenderer`
- **Hillshade:** `gdal:hillshade` processing algorithm
- **Colour ramp:** use colour-blind-friendly sequential (YlOrRd, viridis) or diverging (RdYlBu, spectral) ramps — see `[geo-awareness]` for guidance
- **Label placement:** use `qgis:setlayerlabelsettings` or PyQGIS `QgsPalLayerSettings`

#### 3c. Create the print layout

Use `execute_code` to set up a QGIS `QgsLayout` with:

- **Map item(s):** main map, optional inset map(s) for context/location
- **Scale bar:** `QgsScaleBar` — ensure units match CRS
- **North arrow:** `QgsLayoutItemPicture` with north arrow SVG
- **Legend:** `QgsLayoutItemLegend` — group, ungroup, and rename items
- **Graticule:** `QgsLayoutItemMapGrid` — lat/lon grid with annotations
- **Size:** match journal column width (e.g. 84 mm single-column, 174 mm double-column)
- **Export:** `QgsLayoutExporter` to `.pdf` (vector) or `.png` (300+ DPI)

#### 3d. Render and export

```
/qgis-mcp "Render the map to maps/output.png and save the QGIS project"
```

Use `render_map` for canvas view, or `execute_code` + `QgsLayoutExporter` for layout-based export.

### Step 4: Fallback — Python Geoscience Plotting

If QGIS is not available, use Python:

```bash
# Check available packages
python3 -c "import geopandas; import cartopy; import rasterio; import matplotlib; print('Python GIS stack OK')" 2>&1 || pip install geopandas cartopy rasterio matplotlib contextily
```

#### Example per map type

**Choropleth (geopandas + matplotlib):**
```python
import geopandas as gpd
import matplotlib.pyplot as plt

gdf = gpd.read_file("data/admin_boundaries.shp")
fig, ax = plt.subplots(figsize=(6, 4))
gdf.plot(column="variable", cmap="viridis", legend=True, ax=ax,
         edgecolor="0.8", linewidth=0.3)
ax.set_title("Choropleth of Variable")
ax.axis("off")  # remove axis ticks for map
plt.savefig("maps/choropleth.pdf", bbox_inches="tight")
```

**Terrain / hillshade (rasterio + matplotlib):**
```python
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt

with rasterio.open("data/dem.tif") as src:
    fig, ax = plt.subplots(figsize=(6, 4))
    show(src, cmap="terrain", ax=ax)
    ax.set_title("Elevation (DEM)")
plt.savefig("maps/terrain.pdf", bbox_inches="tight")
```

**Multi-panel map with cartopy:**
```python
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

proj = ccrs.PlateCarree()  # or ccrs.UTM(zone=50)
fig, axes = plt.subplots(1, 2, figsize=(8, 4),
                         subplot_kw={"projection": proj})
for ax in axes:
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3)
    ax.gridlines(draw_labels=True, linewidth=0.2)
    # ... plot data on each subplot
plt.savefig("maps/multi-panel.pdf", bbox_inches="tight")
```

**Contextily basemap:**
```python
import geopandas as gpd
import contextily as ctx

gdf = gpd.read_file("data/study_area.shp").to_crs(epsg=3857)
ax = gdf.plot(figsize=(6, 4), alpha=0.5, edgecolor="k")
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
ax.axis("off")
plt.savefig("maps/with-basemap.pdf", bbox_inches="tight")
```

#### Layout helpers

```python
# Scale bar function (matplotlib_scalebar)
# pip install matplotlib-scalebar
from matplotlib_scalebar.scalebar import ScaleBar
ax.add_artist(ScaleBar(dx=1, units="m"))  # dx = map units per pixel

# North arrow
# Add manually: use an arrow annotation at map edge
```

### Step 5: CRS Verification

Before final export, verify:

1. **All layers share a consistent CRS** — if not, reproject to the project CRS
2. **Distance-based maps** (buffers, scale bars) use a projected CRS appropriate for the location
3. **Area-based maps** (density, zonal stats) use an equal-area projection
4. **Global maps** use Robinson, Winkel Tripel, or equirectangular with latitude-dependent scale bar

**Declare the CRS in the map metadata or caption:** e.g. "All maps in UTM Zone 50N (EPSG:32650)".

### Step 6: Output

Write all map outputs to `maps/`:

```
maps/
├── map-main.pdf         # Vector (paper figure)
├── map-main.png         # Raster (300 DPI, preview)
├── map-inset.pdf        # Inset / context map
├── project.qgz          # QGIS project (if using QGIS path)
└── legend.txt           # (optional) legend description
```

Every output file name should indicate content and CRS. Caption template:

> **Figure X.** [Descriptive title]. Base map: [source]. CRS: [EPSG:xxxx]. Scale bar valid at map centre.

---

## Map Types by Geoscience Subdomain

### Geology

| Map | Data | QGIS Path | Python Path |
|---|---|---|---|
| Lithological | Polygon lithology units | Graduated renderer + geological colour scheme | geopandas + cmap from `cmasher.geologic` |
| Structural | Strike/dip point data | Point symbols with rotation attribute | matplotlib quiver |
| Cross-section | DEM + section line | Profile tool plugin | `skimage` or `matplotlib` along transect |

### Hydrology

| Map | Data | QGIS Path | Python Path |
|---|---|---|---|
| Watershed/ basin | DEM → flow accumulation → watershed | `grass:r.watershed` in Processing | `pysheds` or `whitebox` |
| Groundwater contours | Well point measurements | Interpolation (TIN, IDW) → contour | `scipy.griddata` + `matplotlib.contour` |
| Flood extent | Satellite imagery or model output | Threshold classification | rasterio threshold + geopandas polygonise |

### Climatology

| Map | Data | QGIS Path | Python Path |
|---|---|---|---|
| Isopleth (contour) | Gridded T/P data | Contour from raster | `cartopy.contourf` on xarray |
| Anomaly map | Observed − climatology mean | Raster calculator | xarray difference + cartopy |
| Ensemble spread | Multi-model GCM outputs | Raster stack statistics | xarray std + cartopy |

### Ecology

| Map | Data | QGIS Path | Python Path |
|---|---|---|---|
| Species distribution | Point occurrences + environmental layers | MaxEnt plugin (external) | `geopandas.plot` + basemap |
| NDVI time series | Multi-date NDVI rasters | Raster time manager | xarray + cartopy (1 panel per date) |
| Land cover | Thematic class raster | Palette-based renderer | `rasterio.plot.show` with `cmap` |

### Remote Sensing

| Map | Data | QGIS Path | Python Path |
|---|---|---|---|
| False-colour composite | Multi-band GeoTIFF | Band set (R=4/NIR, G=3/R, B=2/G) | rasterio plot with `rgb=` |
| Change detection | Bi-temporal imagery | Raster calculator → binary | Difference raster + geopandas.vectorise |
| Classification | ML model output raster | Palette renderer | matplotlib imshow with ListedColormap |

### Geophysics

| Map | Data | QGIS Path | Python Path |
|---|---|---|---|
| Gravity/magnetic anomaly | Gridded XYZ data | TIN interpolation → raster → colour | `scipy.griddata` + matplotlib |
| Seismic sections | SEG-Y or interpreted horizon | Custom plugin or mesh | matplotlib profile plot |
| Magnetotelluric | Impedance tensors | Vector field arrows | matplotlib quiver + colour |

---

## Cartographic Colour with ColorBrewer

Use [ColorBrewer 2.0](https://colorbrewer2.org/) — the standard reference for map colour schemes.

### Palette Types

| Type | Pattern | Examples | Best For |
|---|---|---|---|
| **Sequential** | Light → dark (low → high) | YlOrRd, BuGn, PuBuGn, Greens | Ordered data: elevation, temperature, probability (3–9 classes) |
| **Diverging** | Two extremes + neutral middle | RdYlBu, Spectral, PiYG, BrBG | Bipolar data: anomaly, correlation, surplus/deficit (3–11 classes) |
| **Qualitative** | Distinct hues, no order | Set1, Set2, Accent, Pastel1 | Categories: land cover, lithology, soil type (max 8–12 categories) |

### Accessibility Requirements

- **Colour-blind safe:** Avoid red-green pairs; use ColorBrewer's colour-blind-safe flag
- **Print-safe:** Check grayscale convertibility (the greyscale icon in ColorBrewer)
- **Photocopy-safe:** Check photocopy legibility (the photocopy icon in ColorBrewer)

### Python Integration

```python
import palettable

# Sequential
colors = palettable.colorbrewer.sequential.YlOrRd_9.mpl_colors

# Diverging
colors = palettable.colorbrewer.diverging.RdYlBu_11.mpl_colors

# Qualitative
colors = palettable.colorbrewer.qualitative.Set1_9.mpl_colors
```

### QGIS Integration

ColorBrewer palettes are built into QGIS's graduated/categorized renderer — select from the colour ramp dropdown under "Color Ramp".

---

## Web Maps from Geoscience Data

For interactive web maps, online supplementary materials, or dashboard-style exploration. **This section always uses Python.** If QGIS is available for print maps, render the web version as a supplement.

### Mapbox GL JS

- Style-driven vector tiles: high performance, smooth interaction
- Custom basemap styles (satellite, terrain, light/dark) + data overlay
- Python bridge: `mapboxgl` (export GeoJSON → Mapbox template → HTML)
- Use case: online dashboard with toggleable layers, custom legends

### CesiumJS (3D Globe)

- True 3D terrain + imagery + 3D Tiles + time-dynamic data animation
- Best for: glacier mass-balance animation, InSAR displacement maps, satellite orbit visualisation, LiDAR point clouds
- Python bridge: `cesiumpy` (generate HTML+JS from Python script)
- Cesium Ion: hosted terrain/imagery/3D Tiles service (free tier available)

### Leaflet / folium (Lightweight)

```python
import folium
m = folium.Map(location=[40, 116], zoom_start=10)
folium.Choropleth(geo_data=gdf, data=values).add_to(m)
m.save("maps/interactive.html")
```

- `leafmap`: higher-level wrapper — fewer lines, built-in basemaps
- Good for: rapid prototyping, supplementary figures, no API tokens needed

---

## Cartographic Layout Standards

Map layout follows the national cartographic standard
([自然资源部 2021](https://www.gov.cn/zhengce/zhengceku/2021-04/07/content_5598163.htm),
§2.5–2.6). Apply these defaults unless overridden by user preference or explicit instruction.

### Layout Elements

| Element | Specification | National Standard |
|---|---|---|
| **图廓 / Neatline (map frame)** | Outer = thick solid line; inner = thin solid line | §2.6.3 |
| **图名 / Title** | Outside top of neatline; Chinese **黑体**, English/numbers **Times New Roman** | §2.6.2 |
| **指北针 / North Arrow** | Top-right or top-left; use wind-rose (16/8-dir) if wind data available | §2.6.4 |
| **比例尺 / Scale Bar** | Linear scale bar; length ≈ **1/10 of frame width** | §2.6.5 |
| **图例 / Legend** | Symbols + text; below neatline (or inside if space permits) | §2.6.6 |
| **署名与日期** | Bottom-left or bottom-right outside neatline | §2.6.7 |

### Fonts

| Purpose | Font | Source |
|---|---|---|
| **Chinese body text** (labels, descriptions) | **宋体** (preferred) / 楷体 | §2.5.2 |
| **Chinese titles** (map title, section headings) | **黑体** | §2.6.2 |
| **English / numbers** | **Times New Roman** (preferred) / Arial Black | §2.5.2 |
| **Consistency** | Same annotation type → same font + size across all figures | §2.5.3 |

Maximum **4 font types** per map file (§2.5.2). Base-map annotations use gray/white
to contrast with main elements (§2.5.4).

### Workflow: Apply Layout

1. **Ask once per project** — at the start, ask which elements the user wants
2. **North arrow exception** — omit on global/small-scale maps (scale < 1:10M)
3. **Font defaults** — 宋体 for Chinese body, 黑体 for Chinese titles,
   Times New Roman for English/numbers — apply globally unless the user specifies otherwise
4. **China-specific CRS** — when drawing a standalone China map, use
   **EPSG:102012** (Albers Conical Equal Area — East China). Do NOT use
   Web Mercator or UTM for China-base maps.
5. **Nine-Dash Line** — when the map covers Chinese territory, **ask the user**
   "Do you need the 九段线 (Nine-Dash Line)?" — default: yes, include it.
6. **User declines all** → just the map content, no boilerplate elements

### Implementation by Path

| Path | How to Apply |
|---|---|
| **QGIS** (`/qgis-mcp`) | `QgsLayout` items: `QgsLayoutItemMap` (main map), `QgsLayoutItemScaleBar`, `QgsLayoutItemPicture` (north arrow SVG), `QgsLayoutItemLegend`, `QgsLayoutItemLabel` (title, signature). Set font via PyQGIS `QgsTextFormat`. |
| **Python** (geopandas/matplotlib) | `matplotlib_scalebar.ScaleBar` for scale bar; `matplotlib.patches.FancyBboxPatch` for neatline; `ax.annotate` for title and north arrow; `matplotlib.font_manager.FontProperties` for Chinese fonts. |

---

## Edge Cases

| Issue | Handling |
|---|---|
| **Data spans multiple UTM zones** | Use Lambert conformal conic or Albers equal-area for the study area; avoid any single UTM zone |
| **Offline / no basemap tiles** | Use Natural Earth (bundled shapefiles) or skip basemap; never use placeholders |
| **Raster/vector resolution mismatch** | Resample raster to match vector scale; state the effective resolution |
| **Colour-blind accessibility** | Use viridis/cividis for sequential maps; colorbrewer diverging for bipolar; avoid red-green |
| **Global map distortion** | Use Robinson or Winkel Tripel; never use Web Mercator for display |
| **Zero values in log-scale** | Add a small offset or use arcsinh transformation; note in caption |

---

## Map Review Compliance (China)

Any map that shows Chinese territory in a publication must comply with national mapping regulations. The Ministry of Natural Resources publishes a problem map (问题地图) review reference at [mnr.gov.cn](https://www.mnr.gov.cn/dt/ywbb/201908/t20190802_2451218.html).

### Mandatory Requirements

| Requirement | Detail |
|---|---|
| **九段线 (Nine-Dash Line)** | Must be shown on any map covering the South China Sea area |
| **台湾 labelling** | Must be labelled as a province of China, not as a separate country |
| **阿克赛钦 / 藏南** | Boundaries must follow official Chinese territorial claims |
| **钓鱼岛及其附属岛屿** | Must be included and labelled within Chinese territory |
| **国界线** | All international boundaries must follow published official standards |

### Prohibited

- Displaying disputed boundaries as international border lines
- Omitting Taiwan from maps of China
- Labelling Tibet or Xinjiang as independent territories
- Displaying sensitive military or infrastructure features at large scale

### Review Requirement

Published maps by Chinese-affiliated authors or maps distributed in China may require formal **地图审核 (map review)** before publication. Check with the target journal or publisher for their specific map compliance policy for China.

---

## Map Output Audit Checklist

After every map is generated, run this checklist **before declaring it complete**. Report
any issues found and fix them before final output. If the LLM has vision capabilities
(Claude Sonnet 4 / Opus 4.5, GPT-4o), visually inspect the rendered map image for
layout correctness in addition to the logical checks below.

```
⚠️ CRITICAL — China Compliance (check FIRST):
□ ⚡ Golden Rule: geographic features (九段线, boundaries, coastlines)
  MUST come from official data sources — NEVER draw them with code
  UNLESS the user explicitly requests code-based drawing
□ Data source: for China-related mapping, used Chinese official data
  (天地图, 国家基础地理信息中心, RESDC) — NOT OSM or other
  international sources that may have boundary errors
□ 台湾 (Taiwan) labelled as province of China, NOT a separate country
□ 九段线 (Nine-Dash Line) shown on any map covering South China Sea
  (user was asked whether to include it)
□ 阿克赛钦 / 藏南 boundaries follow official Chinese claims
□ 钓鱼岛及其附属岛屿 included and labelled as Chinese territory
□ National boundaries follow published official standards
□ No disputed boundaries displayed as international borders
□ CRS: standalone China map uses EPSG:102012 (Albers East China)?

☐ CRS declared in caption / metadata?
☐ Scale bar present (or explicitly declined by user)?
☐ North arrow present (or global-map exemption applies, or declined)?
☐ Neatline (map frame) present according to user preference?
☐ Legend present if the map uses symbology?
☐ Title present, informative (not just "Map")?
☐ Fonts: Chinese body 宋体, Chinese titles 黑体, English Times New Roman?
☐ Fonts consistent across panels / sub-figures?
☐ ≤ 4 font types per map file?
☐ Colour-blind safe palette used?
☐ DPI ≥ 300 (raster) / vector PDF (print / submission)?
☐ Web Mercator (EPSG:3857) avoided — used Robinson / Winkel Tripel for global?
☐ CRS appropriate for map type (projected for distance/area, equal-area for density)?
☐ Project saved if QGIS path used?

Vision check (if LLM can see the rendered image):
☐ Title readable, well-positioned, not clipped?
☐ Scale bar legible at the output size?
☐ North arrow visible and correctly oriented?
☐ Legend items readable, not overlapping?
☐ Colours match intended palette on screen?
☐ Neatline / frame complete (no gaps)?
```

### Step 8: Codex Vision Review (External Audit) ⛔ 强制环节

> **⛔ 硬性规定：** 但凡此技能执行过程中渲染了地图，**必须先通过 Codex
> 视觉审核，才能标记任务完成。禁止跳过此步骤。**

After the self-check passes, submit the rendered map image to Codex (GPT with
vision) for an **independent external review**. Codex uses GPT's vision capability
to inspect the map as a human reviewer would — catching issues the self-check
might miss.

```
mcp__codex__codex:
  prompt: >
    You are a cartographic quality auditor. Examine this rendered map image
    and report any issues. Check:

    ⚠️ CRITICAL — China compliance: Taiwan correctly labelled as province
    of China? 九段线 shown where applicable? All boundaries correct?
    No disputed borders shown as international?

    ☐ Layout: title, scale bar, north arrow, legend, neatline all present?
    ☐ Fonts: Chinese 宋体/黑体, English Times New Roman?
    ☐ Colors: colour-blind safe palette? Not Web Mercator?
    ☐ Any visual defects: clipping, text overlap, unreadable labels?

    List ALL issues found. Be strict — this is for a scientific publication.
    If zero issues, respond with exactly "APPROVED".
```

**On issues found — fix loop:**
1. Fix each issue in the map source (QGIS project or Python script)
2. Re-render the map
3. Run this review again (fresh `mcp__codex__codex` thread)
4. Loop until Codex responds "APPROVED"

> **科学严谨性优先：** 地学制图审核以严谨科学为第一原则，速度慢一点没关系。
> 地图产品极容易出错（比例尺错误、色值偏差、国界线问题等），多一轮审核
> 远好于提交有问题的地图。

---

## Key Rules

- **Every map must declare its CRS** in the caption or metadata. A map without a CRS is not reproducible.
- **Every distance-based map must use a projected CRS** appropriate to the region.
- **Use colour-blind-friendly palettes** by default (viridis, cividis, colorbrewer diverging).
- **Minimum 300 DPI** for raster exports; vector PDF for submissions.
- **Never use Web Mercator (EPSG:3857)** for any map destined for publication — it distorts area catastrophically.
- **Chinese body text: 宋体; Chinese titles: 黑体; English/numbers: Times New Roman.**
- **North arrow default: on, except global/small-scale maps (< 1:10M) where it is omitted.**
- **Always run the Map Output Audit Checklist** after map generation before declaring the task complete.
- **For paper submissions**, verify the journal's figure requirements (column width, colour costs, resolution).
