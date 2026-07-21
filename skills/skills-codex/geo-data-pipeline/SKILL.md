---
name: geo-data-pipeline
description: "Geoscience data acquisition and preprocessing — OSM (Overpass/osmnx), ChinaGeoSS (国产卫星), Tianditu (天地图), RESDC (中科院资源环境中心), gscloud (地理空间数据云), Sentinel, Landsat, ERA5, STAC. Use when the research needs to obtain or prepare geospatial data for earth science analysis."
argument-hint: "[data-requirements-or-query]"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch
---

# Geo Data Pipeline: Geoscience Data Acquisition & Preprocessing

Data request: $ARGUMENTS

## Purpose

Automated data acquisition from public geoscience data sources, with preprocessing instructions.

## 1. OpenStreetMap (OSM)

Access OSM vector data via Overpass API (`overpy`), OSMnx for road networks, QGIS QuickOSM plugin, or bulk PBF downloads (Geofabrik, BBBike). Covers: roads, water bodies, buildings, land use, POIs.

## 2. ChinaGeoSS (chinageoss.cn)

中国国家综合地球观测数据共享平台. GF-series (高分1–7), ZY-3, HJ-series satellites. SAR, optical, hyperspectral, stereo sensors from 0.8m–50m resolution.

## 3. 天地图目录 (mulu.tianditu.gov.cn)

国家地理信息公共服务平台 with WMTS tile service, geocoding/routing APIs, administrative boundaries, place names, POI.

## 4. 中科院资源环境中心 (resdc.cn)

CAS Resource and Environment Data Center: CNLUCC land use (30m × 5yr), climate grids (1 km), population/GDP grids, ecosystem assessments, etc. Free registration required.

## 5. 地理空间数据云 (gscloud.cn)

Domestic mirror for SRTM/ASTER DEM (30m/90m), Landsat, MODIS, Sentinel. No VPN needed for Chinese users.

## 6. International Open Data

- **Copernicus** — Sentinel-1/2/3 via `sentinelsat`
- **USGS** — Landsat, SRTM, NASADEM via `landsatxplore`
- **CDS** — ERA5 climate reanalysis via `cdsapi`
- **LP DAAC** — MODIS products via `earthaccess`

## 7. STAC

Standardised API for raster data discovery: Microsoft Planetary Computer, Earth Search, NASA CMR STAC.

## 8. Common Preprocessing

- Atmospheric correction: Sen2Cor (Sentinel-2), 6S (general)
- Cloud masking: FMask, s2cloudless, QA bands
- Reprojection/resampling: `gdalwarp`, `rasterio.warp.reproject`
- Mosaicking/clipping: `gdalbuildvrt`, `rasterio.merge`

## 9. Output

`data/` directory with raw/processed/boundaries subdirs + `README.md` provenance log (source, date, CRS, preprocessing steps).
