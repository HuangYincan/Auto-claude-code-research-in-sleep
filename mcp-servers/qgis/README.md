# QGIS MCP Server (ARIS)

This directory contains the **QGIS MCP server** bundled with ARIS. It bridges
Claude Code (or any MCP host) with QGIS Desktop for geospatial analysis.

## Architecture

```
Claude Code (MCP host)
     ↕ stdio (JSON-RPC via FastMCP)
server.py                     ← this file
     ↕ TCP socket (localhost:9876, length-prefixed JSON)
QGIS MCP Plugin (inside QGIS) ← installed separately
     ↕ PyQGIS API
QGIS Desktop
```

The server is a thin proxy: it receives MCP tool calls from Claude Code,
forwards them as JSON commands over TCP to the QGIS MCP plugin running
inside QGIS, and returns the results.

## Prerequisites

1. **uv** — required for dependency management:
   ```bash
   brew install uv          # macOS
   # or: curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **QGIS Desktop 3.x** — [Download](https://qgis.org/download/)

3. **QGIS MCP plugin** — from the
   [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp) repo.
   See [docs/integrations/qgis-mcp.md](../../docs/integrations/qgis-mcp.md) for
   installation steps.

## Registration

### Local (self-contained — uses this cloned server)

```bash
claude mcp add qgis -s project -- \
  uv --directory /path/to/aris/mcp-servers/qgis run server.py
```

Replace `/path/to/aris` with the absolute path to the ARIS repository.

### Remote (upstream — simpler, pulls from GitHub)

```bash
claude mcp add qgis -s project -- \
  uvx --from https://github.com/nkarasiak/qgis-mcp/archive/refs/heads/main.zip \
  qgis-mcp-server
```

> **Note:** Both paths require QGIS to be running with the plugin server
> started. The remote path provides 102 tools (upstream); the local path
> provides 15 core tools matching the ARIS skill docs.

## Usage

After registration, restart Claude Code. Run:

```
/qgis-mcp "Load my project and render a map"
```

Or call tools directly:
- `ping` — check connectivity with the QGIS plugin
- `get_qgis_info` — inspect QGIS version and environment
- `add_vector_layer` / `add_raster_layer` — load data
- `execute_processing` — run Processing Toolbox algorithms
- `render_map` — export the current canvas to PNG
- `execute_code` — run arbitrary PyQGIS code

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `QGIS_MCP_HOST` | `localhost` | QGIS plugin host |
| `QGIS_MCP_PORT` | `9876` | QGIS plugin port |
| `QGIS_MCP_LOG_FILE` | *(none)* | Path to rotating log file |
| `QGIS_MCP_LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING |

Set these in `.env` at the ARIS project root or export them in your shell.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `uv: command not found` | uv not installed | `brew install uv` |
| `mcp module not found` | Dependencies not resolved | Ensure `pyproject.toml` exists in this directory; run `uv sync --directory .` |
| `Cannot connect to QGIS` | QGIS not running or plugin server not started | Start QGIS, enable plugin, click "Start Server" |
| `Connection refused` | Port mismatch | Default port is 9876 — check QGIS plugin settings |
| Tools return empty data | No project loaded or no visible layers | Load a project with `load_project` first |

## Files

| File | Purpose |
|---|---|
| `server.py` | MCP server implementation (FastMCP, TCP socket client) |
| `pyproject.toml` | Python project configuration (uv, dependencies) |
