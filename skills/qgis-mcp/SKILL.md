---
name: qgis-mcp
description: Geospatial analysis via QGIS-MCP — load GIS data, run processing algorithms, render maps, and execute PyQGIS code from a research pipeline.
argument-hint: "[task description]"
allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit
---

# QGIS-MCP: Geospatial Analysis via QGIS

{{ARGUMENTS}}

## Prerequisites

Before using this skill, you need:

1. **uv** — `brew install uv` (macOS) or `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **QGIS Desktop 3.x** running with the **QGIS MCP plugin** started
   (Plugins → QGIS MCP → Start Server).
   See `docs/integrations/qgis-mcp.md` for full setup.

Register the MCP server with Claude Code (pick one path):

**Local** (self-contained — 15 core tools):
```bash
claude mcp add qgis -s project -- uv --directory /path/to/aris/mcp-servers/qgis run server.py
```

**Remote** (upstream — 102 tools, simpler setup):
```bash
claude mcp add qgis -s project -- uvx --from https://github.com/nkarasiak/qgis-mcp/archive/refs/heads/main.zip qgis-mcp-server
```

Verify:
```bash
claude mcp list | grep qgis
```

> **QGIS must be running** with the plugin server started. Otherwise every
> tool call returns a connection error.

## Workflow

### Step 1: Understand the Task

Identify the geospatial task and the data available:
- What data do we need (vector layers, raster layers)?
- What analysis should be performed (spatial query, processing algorithm, map rendering)?
- What is the expected output (a rendered map, analysis results, code)?

### Data Source Priority

When the task requires geospatial data (base maps, DEM, imagery, administrative
boundaries, POIs, road networks, etc.), prefer sources in this order:

1. **中国官方/国内源（Chinese domestic sources）** — 天地图（Tianditu,
   https://www.tianditu.gov.cn/）、国家基础地理信息中心、各省市地理信息
   公共服务平台、中国科学院资源环境科学与数据中心（https://www.resdc.cn/）、
   全国地理信息资源目录服务系统（https://www.webmap.cn/）等。
   - 天地图提供 WMTS 瓦片、行政区划、地名地址、POI 等 API
   - 许多国内源无需翻墙，延迟低，数据适合中国区域

   > ⚠️ **涉及中国疆域的地图，必须优先使用中国官方数据源。**
   > OpenStreetMap 等国际开源数据可能在中国国界线、台湾归属、
   > 九段线、阿克赛钦/藏南边界等方面存在错误，**不可用于涉及
   > 中国领土的出版级地图的底图或边界数据**。
   >
   > ⚡ **数据源黄金规则：** 用户要求绘制或补充任何地理要素（九段线、
   > 国界线、海岸线等）时，**必须查找官方数据源，严禁用代码手画**。
   > 找不到数据则如实告知用户，不要自行补画。除非用户明确要求用代码绘制。
2. **大型国际开放平台** — OpenStreetMap（https://www.openstreetmap.org/，
   通过 QGIS OSM 插件或 QuickOSM）、Natural Earth（https://www.naturalearthdata.com/）、
   USGS EarthExplorer、ESA Copernicus、Google Earth Engine（如有权限）等
3. **科研及专业数据源** — 所在项目或实验室已有的数据集、导师/合作者
   提供的专有数据、论文附带的数据集仓库

> **注意：** 如果任务只需要处理用户已有数据（本地的 .shp / .gpkg / .tif
> 等文件），直接从 Step 2 开始即可。优先使用国内源的指引主要适用于
> **需要获取底图或外部辅助数据**的场景。

### Step 2: Connect and Verify

Use `ping` to verify the connection:
```
<FunctionCall>ping</FunctionCall>
```

Then gather context with `get_qgis_info` and (if a project is loaded)
`get_project_info`.

### Step 3: Execute Geospatial Task

Available tools (callable by name — the MCP host dispatches them):

| Tool | When to Use |
|---|---|
| `load_project` / `create_new_project` | Open existing or create new QGIS project |
| `add_vector_layer` / `add_raster_layer` | Load GIS data from disk |
| `get_layers` / `get_layer_features` | Inspect data contents and attributes |
| `zoom_to_layer` / `render_map` | Visualize data and export map images |
| `execute_processing` | Run QGIS native/GDAL/GRASS algorithms |
| `execute_code` | Run arbitrary PyQGIS for custom analysis |
| `save_project` | Persist project state |

> **Cartographic layout guidance:** When using `execute_code` to create a
> QGIS `QgsLayout` for maps involving Chinese territory (or any publication
> map), follow the layout standards in `/geo-mapping` — see its
> **Cartographic Layout Standards** section for fonts (宋体/黑体/Times New Roman),
> neatline, north arrow rules, and the **Map Output Audit Checklist** for
> post-generation review.

### Step 4: Return Results

Summarize what was accomplished, including:
- Layers loaded or created
- Processing algorithms run and their outputs
- Map images rendered (note the file path)
- Any data extracts or analysis results

Combine with `/analyze-results` or other ARIS skills as needed for
research workflows.

## Example Usage

```
/qgis-mcp "Load Thailand election data from ~/data/thailand_2007.qgz, inspect the layers, and render a map to ~/output/map.png"
```

Or as part of a broader research pipeline:

```
/research-pipeline "landslide susceptibility mapping using deep learning" -- qgis-mcp: true
```
