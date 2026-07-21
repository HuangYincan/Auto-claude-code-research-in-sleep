---
name: geo-data-pipeline
description: "Geoscience data acquisition and preprocessing — OSM (Overpass/osmnx), ChinaGeoSS (国产卫星), Tianditu (天地图), RESDC (中科院资源环境中心), gscloud (地理空间数据云), Sentinel, Landsat, ERA5, STAC. Use when the research needs to obtain or prepare geospatial data for earth science analysis."
argument-hint: "[data-requirements-or-query]"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch
---

# Geo Data Pipeline: Geoscience Data Acquisition & Preprocessing

Data request: $ARGUMENTS

## Purpose

Automated data acquisition from public geoscience data sources, with preprocessing instructions. This skill covers the full pipeline from source discovery to ready-to-analyse data.

## 1. OpenStreetMap (OSM)

Access **OpenStreetMap** vector data for base maps, road networks, water bodies, buildings, and land use.

### Overpass API Query

```overpass
[out:json];
area["name"="Beijing"];
nwr["highway"](area);
out geom;
```

Apply filters: `["highway"]`, `["waterway"]`, `["building"]`, `["landuse"]`, `["natural"]`.

Python with `overpy`:
```python
import overpy
api = overpy.Overpass()
result = api.query("""
  [out:json];
  area["name"="Beijing"]->.a;
  nwr["amenity"="school"](area.a);
  out center;
""")
for node in result.nodes:
    print(node.tags.get("name"), node.lat, node.lon)
```

### OSMnx (Road Network Analysis)

```python
import osmnx as ox

# Download road network for a place
G = ox.graph_from_place("Beijing, China", network_type="drive")
# Basic stats
print(ox.basic_stats(G))
# Save to Shapefile / GeoPackage
ox.save_graph_geopackage(G, "data/beijing_roads.gpkg")
# Isolate area calculation
area = ox.projection.project_gdf(ox.graph_to_gdfs(G, nodes=False)).area.sum()
```

### QGIS QuickOSM Plugin

For visual OSM data query directly within QGIS: Plugins → QuickOSM → select key/value/extent → Load layer.

### Data Downloads

- Geofabrik: https://download.geofabrik.de/ — regional OSM extracts (.pbf)
- BBBike: https://extract.bbbike.org/ — custom area OSM extracts

---

## 2. ChinaGeoSS (chinageoss.cn)

中国国家综合地球观测数据共享平台 — National Comprehensive Earth Observation Data Sharing Platform.

Available satellite series:

| Satellite | Sensor | Resolution | Primary Use |
|---|---|---|---|
| GF-1 (高分一号) | PMS/WFV | 2m/16m | Land use, agriculture |
| GF-2 (高分二号) | PMS | 0.8m/4m | Urban mapping, survey |
| GF-3 (高分三号) | SAR (C-band) | 1–500m | Flood, deformation, marine |
| GF-4 (高分四号) | Geostationary optical | 50m | Disaster monitoring |
| GF-5 (高分五号) | Hyperspectral | 30m | Environment, mineralogy |
| GF-6 (高分六号) | PMS/WFV | 2m/16m | Agriculture, forestry |
| GF-7 (高分七号) | Stereo mapping | 0.8m | DEM, 3D |
| ZY-3 (资源三号) | Stereo | 2.1m | Topographic mapping |
| HJ-1/2 (环境一号/二号) | CCD/IR | 30m | Environment, disaster |

Process: register → search by area/time → apply (may require approval) → download → process.

---

## 3. 天地图目录 (Tianditu Directory, mulu.tianditu.gov.cn)

国家地理信息公共服务平台 — national geospatial data service directory.

Available data:
- 行政区划 — administrative boundaries (nation → province → city → county)
- 地名地址 — place names and addresses
- POI — points of interest
- 遥感影像 — satellite image base maps
- 数字高程 — digital elevation
- 交通路网 — road networks
- 水系 — water systems

API Services:
- **WMTS Tile Service** — raster/vector tile base maps
- **Geocoding API** — address → coordinates (forward) and coordinates → address (reverse)
- **Routing API** — driving/walking directions

Access: open for non-commercial use; free API key registration required.

---

## 4. 中科院资源环境科学与数据中心 (resdc.cn)

中国科学院 — Resource and Environment Science and Data Center, CAS.

Key datasets:

| Dataset | Description | Resolution | Period |
|---|---|---|---|
| CNLUCC | China Land Use/Cover (多期土地利用遥感监测) | 30m × 5-year | 1980–2020 |
| Climate grids | Monthly precipitation, temperature, radiation | 1 km | 1980–2020 |
| Population/GDP | Population density, GDP per km² grids | 1 km | 1990–2020 |
| Soil erosion | Water/wind erosion intensity classification | 1 km | Multi-period |
| Ecosystem assessment | NPP, NDVI, ecosystem service values | 1 km | 2000–2020 |
| Agricultural | Cropland distribution, irrigation zones | Various | Updated |

Access: free registration, data download via web interface (some datasets require institutional approval).

---

## 5. 地理空间数据云 (gscloud.cn)

国内镜像 — Chinese domestic mirror for international remote sensing data.

Available downloads (no VPN required for Chinese users):
- **SRTM DEM** — 90m (global), 30m (US)
- **ASTER GDEM** — 30m global DEM
- **Landsat 5/7/8/9** — USGS archive mirror
- **MODIS products** — MOD09, MOD11, MOD13, MOD15, MOD17
- **Sentinel-1/2** — partial mirror
- Online preprocessing: mosaicking, subsetting, format conversion

---

## 6. International Open Data

### Copernicus Open Access Hub (Sentinel)

Data: Sentinel-1 (SAR), Sentinel-2 (optical 10–60m), Sentinel-3 (OLCI/SLSTR), Sentinel-5P (atmospheric)

Python with `sentinelsat`:
```python
from sentinelsat import SentinelAPI
api = SentinelAPI("user", "password")
products = api.query(
    area="POLYGON((...))",
    date=("2023-01-01", "2023-12-31"),
    platformname="Sentinel-2",
    processinglevel="Level-2A",
    cloudcoverpercentage=(0, 20)
)
api.download_all(products)
```

### USGS EarthExplorer

Data: Landsat (4–9), SRTM, NASADEM (30m), ASTER GDEM, MODIS, NAIP.

Python with `landsatxplore`:
```python
from landsatxplore.api import API
api = API("user", "password")
scenes = api.search(
    dataset="landsat_ot_c2_l2",
    latitude=40, longitude=116,
    start_date="2023-01-01", end_date="2023-12-31",
    max_cloud_cover=20
)
```

### Copernicus Climate Data Store (CDS)

Data: ERA5 hourly reanalysis (~31km), seasonal forecasts, CORDEX regional projections.

Python with `cdsapi`:
```python
import cdsapi
c = cdsapi.Client()
c.retrieve("reanalysis-era5-single-levels", {
    "variable": "2m_temperature",
    "year": "2023", "month": "01", "day": "01",
    "time": "12:00", "format": "netcdf"
}, "data/era5_temp.nc")
```

### MODIS LP DAAC

Access via `earthaccess`:
```python
import earthaccess
earthaccess.login()
results = earthaccess.search_data(
    short_name="MOD13Q1",
    bounding_box=(-180, -90, 180, 90),
    temporal=("2023-01-01", "2023-12-31")
)
earthaccess.download(results, "./data")
```

---

## 7. STAC (SpatioTemporal Asset Catalog)

A standardised API for geospatial raster data discovery.

```python
import pystac_client

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1"
)
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=[116.0, 39.8, 117.0, 40.2],
    datetime="2023-06-01/2023-09-30",
    max_cloud_cover=20
)
items = list(search.items())
```

Popular STAC endpoints:
- **Microsoft Planetary Computer** — Landsat, Sentinel, NAIP, MODIS
- **Earth Search** (Element 84) — Sentinel-2 Landsat 8/9
- **Copernicus Data Space** — Sentinel-1/2
- **NASA CMR STAC** — NASA Earth observations

---

## 8. Common Preprocessing Steps

### Atmospheric Correction

| Sensor | Tool | Command |
|---|---|---|
| Sentinel-2 | Sen2Cor | `L2A_Process --resolution 10 S2A_*.SAFE` |
| Sentinel-2 | `snappy` | ESA SNAP Python bridge |
| Landsat | LaSRC / 6S | Landsat Level-2 products (already corrected) |
| General | Py6S | Python 6S wrapper |

### Cloud Masking

**FMask** (for Landsat, Sentinel-2):
```bash
# Using C version
fmask_sentinel2 -i S2A_*.SAFE -o cloud_mask.tif
```

**Sentinel-2 s2cloudless** (Python):
```python
from s2cloudless import S2PixelCloudDetector
cloud_detector = S2PixelCloudDetector()
cloud_masks = cloud_detector.get_cloud_masks(s2_bands)
```

**QA bands** (Landsat):
```python
import rasterio
with rasterio.open("LC08_BQA.tif") as src:
    qa = src.read(1)
# Bit 3: cloud shadow; Bits 4-5: cloud
cloud_mask = ((qa >> 3) & 1) | ((qa >> 4) & 1)
```

### Reprojection & Resampling

```bash
gdalwarp -t_srs EPSG:32650 -tr 30 30 -r bilinear input.tif output.tif
```

Python:
```python
import rasterio
from rasterio.warp import reproject, Resampling

with rasterio.open("input.tif") as src:
    transform, width, height = calculate_default_transform(...)
    destination = np.zeros((height, width))
    reproject(
        source=src.read(1), destination=destination,
        src_transform=src.transform, src_crs=src.crs,
        dst_transform=transform, dst_crs="EPSG:32650",
        resampling=Resampling.bilinear)
```

### Mosaicking & Clipping

```bash
gdalbuildvrt mosaic.vrt tile_1.tif tile_2.tif tile_3.tif
gdal_translate -projwin ulx uly lrx lry mosaic.vrt clipped.tif
```

Python:
```python
import rasterio
from rasterio.merge import merge
mosaic, out_trans = merge([src1, src2, src3])
```

---

## 9. Output

- All downloaded data goes to `data/` directory
- Preprocessed outputs in `data/processed/`
- A `data/README.md` log file recording:
  - Source URL / DOI / API query
  - Download date
  - CRS and spatial extent
  - Preprocessing steps applied
  - Processing parameters and software versions

```
data/
├── README.md                # Data provenance log
├── raw/                     # Original downloads
├── processed/               # Preprocessed (reprojected, masked, mosaicked)
└── boundaries/              # Study area boundary files
```

---

## ⚠️ 审查与关键检查 (Review & Critical Checks)

**在提交任何数据产品前，必须执行以下审查。所有地学任务必须重视审查环节。**

### ⚡ 数据源黄金规则 (Golden Rule — Do NOT Fabricate Data)

用户要求绘制或补充任何地理要素（如九段线、国界线、海岸线等）时：
1. **必须查找官方数据源** — 天地图、国家基础地理信息中心、自然资源部发布的权威数据
2. **严禁用代码手画** — 不要自己用 Python 或 PyQGIS 代码绘制地理要素边界，这不是科学严谨的做法
3. **找不到数据则如实告知** — 如果无法找到官方数据源，明确告知用户"未找到相关官方数据"
4. **唯一例外** — 用户明确要求"用代码绘制"时才可这样做

### 1. 数据源审查 (Data Source Audit)
- [ ] 涉及中国区域的数据，是否优先使用中国官方源（天地图、国家基础地理信息中心、RESDC、gscloud.cn）？
- [ ] 是否避免了 OpenStreetMap 等可能存在边界错误的国际源？
- [ ] 数据来源 URL / DOI / API 查询是否完整记录在 `data/README.md`？

### 2. 空间参考审查 (CRS Audit)
- [ ] 所有下载/预处理数据的 CRS 已确认？
- [ ] 距离/面积分析使用投影坐标系？
- [ ] 单独涉及中国区域的数据使用 CGCS2000 或 EPSG:102012？

### 3. 中国合规审查 (China Compliance Audit)
- [ ] 涉及中国区域的数据边界（国界线、九段线等）使用官方来源
- [ ] 台湾地区数据标注为"中国台湾"
- [ ] 阿克赛钦/藏南区域数据使用官方边界

### 4. 结果审查 (Output Audit)
- [ ] `data/README.md` 数据处理日志完整？
- [ ] 预处理步骤可复现（参数、软件版本记录）？
- [ ] 中间文件和最终文件命名规范？
