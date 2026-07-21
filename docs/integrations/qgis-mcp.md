# QGIS-MCP Integration

[QGIS-MCP](https://github.com/nkarasiak/qgis-mcp) bridges **QGIS Desktop** (the open-source GIS
application) with Claude Code via the Model Context Protocol. It allows LLM-driven geospatial
analysis: loading GIS data, running processing algorithms, rendering maps, and executing PyQGIS
code — all from a research pipeline.

## Architecture

```
Claude Code (MCP host)
     ↕ stdio (JSON-RPC via FastMCP)
mcp-servers/qgis/server.py     ← ARIS-bundled MCP server
     ↕ TCP socket (localhost:9876, length-prefixed JSON)
QGIS MCP Plugin (inside QGIS)  ← installed separately (nkarasiak/qgis-mcp)
     ↕ PyQGIS API
QGIS Desktop
```

The **QGIS plugin** (from the [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp) repo)
runs inside QGIS and opens a socket server. The **ARIS MCP server**
(`mcp-servers/qgis/server.py`) connects to that socket and translates MCP tool calls into QGIS
commands.

## Prerequisites

1. **uv** — required by the MCP registration command:
   ```bash
   brew install uv          # macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh   # any platform
   ```

2. **QGIS Desktop 3.x** — [Download](https://qgis.org/download/)

3. **Python 3.12+** — bundled with QGIS or system-wide

## Installation

### 1. Install the QGIS Plugin

The [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp) repo provides both the QGIS plugin
and the canonical MCP server. We only need the plugin installed into QGIS.

**Option A — Automated (recommended):**
```bash
git clone https://github.com/nkarasiak/qgis-mcp.git /path/to/qgis-mcp
cd /path/to/qgis-mcp
python install.py            # symlinks plugin + configures clients interactively
```

**Option B — Manual symlink:**
```bash
git clone https://github.com/nkarasiak/qgis-mcp.git /path/to/qgis-mcp

# macOS
ln -s /path/to/qgis-mcp/qgis_mcp_plugin \
  ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/qgis_mcp

# Linux
ln -s /path/to/qgis-mcp/qgis_mcp_plugin \
  ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_mcp

# Windows PowerShell (admin not required for junction)
# New-Item -ItemType Junction -Path "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\qgis_mcp" -Target "C:\path\to\qgis-mcp\qgis_mcp_plugin"
```

Restart QGIS, then enable the plugin via **Plugins → Manage and Install Plugins → QGIS MCP**.

### 2. Start the Server in QGIS

Open the QGIS MCP dock widget (**Plugins → QGIS MCP → QGIS MCP**), confirm the port
(default 9876), and click **Start Server**. The status should show "Server: Running on port 9876".

### 3. Register with Claude Code

You have two options:

**Option A — Local (self-contained, 15 core tools):**
Uses the ARIS-bundled server at `mcp-servers/qgis/`:
```bash
claude mcp add qgis -s project -- \
  uv --directory /path/to/aris/mcp-servers/qgis run server.py
```
When this command runs, `uv` automatically creates an isolated virtual environment
(in uv's cache or `mcp-servers/qgis/.venv`), installs the `mcp` SDK, and starts the server.

**Option B — Remote/Upstream (102 tools, simpler):**
Pulls the canonical server directly from GitHub — no local server code needed:
```bash
claude mcp add qgis -s project -- \
  uvx --from https://github.com/nkarasiak/qgis-mcp/archive/refs/heads/main.zip \
  qgis-mcp-server
```

> **Note:** Both options require QGIS to be running with the plugin server
> started. Option B is simpler to set up and provides all 102 upstream tools,
> but depends on the GitHub archive being accessible.

### 4. Verify

In Claude Code, type `/qgis-mcp` and run `ping`. If QGIS is running with the plugin started,
you should see a successful response.

```bash
claude mcp list | grep qgis
```

## Exposed Tools (Local Server — 15)

| Tool | Description |
|---|---|
| `ping` | Check connectivity with the QGIS plugin |
| `get_qgis_info` | Return QGIS version and environment info |
| `load_project` | Load a .qgz / .qgs project from path |
| `create_new_project` | Create and save a new empty project |
| `get_project_info` | Current project metadata (CRS, layers, …) |
| `add_vector_layer` | Add shapefile / GeoPackage / GeoJSON etc. |
| `add_raster_layer` | Add GeoTIFF / other raster layer |
| `get_layers` | List all layers in the project |
| `remove_layer` | Remove a layer by ID |
| `zoom_to_layer` | Zoom canvas to a layer's extent |
| `get_layer_features` | Query features (attributes + WKT geometry) |
| `execute_processing` | Run any Processing Toolbox algorithm |
| `save_project` | Save the current project |
| `render_map` | Render canvas to a PNG image |
| `execute_code` | Run arbitrary PyQGIS code (⚠ cautious) |

The **remote/upstream path** exposes 102 tools including layer styling, atlas
export, 3D views, print layout construction, SQL queries, and more.

## Usage in Research Pipelines

The `/qgis-mcp` skill (see `skills/qgis-mcp/`) integrates QGIS into ARIS workflows:

- **Spatial data discovery** — load, inspect, and query geospatial datasets
- **Automated map production** — render publication-quality maps programmatically
- **Geo-ML preprocessing** — use QGIS Processing algorithms as feature-engineering steps
- **Result visualization** — overlay research outputs on base maps

Combine with `/research-pipeline` for end-to-end geo-spatial ML research:
`/research-pipeline "landslide susceptibility mapping using deep learning" -- qgis-mcp: true`

## Troubleshooting

| Symptom | Check |
|---|---|
| `uv: command not found` | Install uv: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh` |
| `mcp module not found` | uv didn't resolve dependencies — ensure `pyproject.toml` exists in `mcp-servers/qgis/` |
| `Could not connect to QGIS` | Is QGIS running? Is the plugin server started? |
| `Connection refused` | Port mismatch — default is 9876 in both plugin and server |
| Tools return empty data | Is a project loaded? Are layers visible in QGIS? |

## Files

| Path | Purpose |
|---|---|
| `mcp-servers/qgis/server.py` | ARIS-bundled MCP server (FastMCP, TCP socket client) |
| `mcp-servers/qgis/pyproject.toml` | Python project config (uv package, `mcp[cli]` dependency) |
| `mcp-servers/qgis/README.md` | Server setup guide |
| `skills/qgis-mcp/SKILL.md` | ARIS skill for QGIS workflows |
| `.env` (project root) | `QGIS_MCP_HOST`, `QGIS_MCP_PORT` |
