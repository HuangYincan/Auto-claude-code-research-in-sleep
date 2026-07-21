#!/usr/bin/env python3
"""
QGIS MCP Server — bridges Claude Code with QGIS Desktop.

Architecture:
  Claude Code (MCP host)
       ↕ stdio (JSON-RPC via FastMCP)
  server.py                    ← this file
       ↕ TCP socket (localhost:9876, length-prefixed framing)
  QGIS MCP Plugin              ← runs inside QGIS, exposes PyQGIS API

Protocol (matches qgis-mcp upstream):
  Each message is framed as [4-byte big-endian length][UTF-8 JSON payload].
  The JSON has the form {"type": "<cmd>", "params": {...}} for requests
  and {"status": "success", "data": ...} for responses.

Prerequisites:
  1. QGIS Desktop 3.x installed.
  2. QGIS MCP plugin installed — see docs/integrations/qgis-mcp.md.
  3. QGIS running with plugin server started (Plugins → QGIS MCP → Start Server).

Environment:
  QGIS_MCP_HOST    — default: localhost
  QGIS_MCP_PORT    — default: 9876
  QGIS_MCP_LOG_FILE — optional log file path
  QGIS_MCP_LOG_LEVEL — optional: DEBUG, INFO (default), WARNING
"""

from __future__ import annotations

import asyncio
import json
import logging
import logging.handlers
import os
import socket
import struct
import threading
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from mcp.server.fastmcp import FastMCP, Context

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876
SOCKET_TIMEOUT = 120.0  # seconds — generous timeout for processing algorithms

HEADER_FORMAT = "!I"  # 4-byte big-endian unsigned int
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
MAX_RESPONSE_SIZE = 100 * 1024 * 1024  # 100 MB

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_logger: logging.Logger | None = None


def _setup_logging() -> logging.Logger:
    global _logger
    if _logger is not None:
        return _logger

    root = logging.getLogger("QgisMCP")
    root.setLevel(os.environ.get("QGIS_MCP_LOG_LEVEL", "INFO").upper())

    # stderr handler (what the MCP host captures)
    stderr = logging.StreamHandler()
    stderr.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    root.addHandler(stderr)

    # Optional rotating file handler
    log_file = os.environ.get("QGIS_MCP_LOG_FILE")
    if log_file:
        fh = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=3
        )
        fh.setFormatter(logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        root.addHandler(fh)

    _logger = root
    return root


logger = _setup_logging()

# ---------------------------------------------------------------------------
# Socket client — thread-safe, length-prefixed framing
# ---------------------------------------------------------------------------


class QgisSocketError(ConnectionError):
    """Raised on socket-level failures."""


class QgisSocketClient:
    """TCP socket client with length-prefixed JSON framing.

    Uses a 4-byte big-endian header to delimit messages — same protocol as
    the upstream qgis-mcp plugin, avoiding the "read-until-JSON-parses"
    fragility that desyncs under concurrent access.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout: float = SOCKET_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self._sock: socket.socket | None = None
        self._lock = threading.Lock()
        self._timeout = timeout
        self._last_used: float = 0.0

    # ---- lifecycle -------------------------------------------------------

    def connect(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self._timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            sock.connect((self.host, self.port))
        except OSError as exc:
            sock.close()
            raise QgisSocketError(
                f"Cannot connect to QGIS plugin at {self.host}:{self.port} — {exc}"
            ) from exc
        self._sock = sock
        self._last_used = time.monotonic()
        logger.info("Connected to QGIS plugin at %s:%s", self.host, self.port)

    def disconnect(self) -> None:
        sock, self._sock = self._sock, None
        if sock:
            try:
                sock.close()
            except OSError:
                pass
            logger.info("Disconnected from QGIS plugin")

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def health_check(self) -> bool:
        """Quick TCP-level check — does not require a QGIS round-trip."""
        if not self._sock:
            return False
        try:
            self._sock.getpeername()
            return True
        except OSError:
            return False

    # ---- send / recv -----------------------------------------------------

    def send(self, cmd_type: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a command and return the parsed JSON response.

        Thread-safe: uses a re-entrant lock so concurrent asyncio.to_thread
        calls do not interleave frames on the wire.
        """
        with self._lock:
            self._ensure_connected()
            payload = json.dumps(
                {"type": cmd_type, "params": params or {}},
                ensure_ascii=False,
            )
            data = payload.encode("utf-8")

            # Length-prefixed send: [4-byte header][payload]
            header = struct.pack(HEADER_FORMAT, len(data))
            try:
                self._sock.sendall(header)
                self._sock.sendall(data)
            except OSError as exc:
                self.disconnect()
                raise QgisSocketError(
                    f"Send failed for '{cmd_type}': {exc}"
                ) from exc

            # Read response: [4-byte header][payload]
            raw_header = self._recv_exact(HEADER_SIZE)
            if raw_header is None:
                self.disconnect()
                raise QgisSocketError(
                    f"Connection closed by QGIS plugin while reading header for '{cmd_type}'"
                )
            payload_len = struct.unpack(HEADER_FORMAT, raw_header)[0]
            if payload_len > MAX_RESPONSE_SIZE:
                self.disconnect()
                raise QgisSocketError(
                    f"Response too large: {payload_len} bytes (max {MAX_RESPONSE_SIZE})"
                )

            raw_body = self._recv_exact(payload_len)
            if raw_body is None:
                self.disconnect()
                raise QgisSocketError(
                    f"Connection closed while reading body for '{cmd_type}'"
                )

            self._last_used = time.monotonic()

            try:
                return json.loads(raw_body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise QgisSocketError(
                    f"Invalid JSON response for '{cmd_type}': {exc}"
                ) from exc

    def _ensure_connected(self) -> None:
        if self._sock is None or not self.health_check():
            self.disconnect()
            self.connect()

    def _recv_exact(self, n: int) -> bytes | None:
        """Read exactly *n* bytes, or return None on EOF."""
        buf = bytearray(n)
        view = memoryview(buf)
        while view:
            try:
                nread = self._sock.recv_into(view, len(view))
            except OSError:
                return None
            if nread == 0:
                return None
            view = view[nread:]
        return bytes(buf)


# ---------------------------------------------------------------------------
# Connection management — singleton with health TTL
# ---------------------------------------------------------------------------

_qgis: QgisSocketClient | None = None
_qgis_lock = threading.Lock()
_HEALTH_TTL = 5.0  # seconds between health checks


def get_qgis_connection() -> QgisSocketClient:
    """Return a healthy singleton connection (lazy init + TTL check)."""
    global _qgis

    # Fast path: already connected and recently checked
    if _qgis is not None:
        if (time.monotonic() - _qgis._last_used) < _HEALTH_TTL:
            return _qgis
        # TTL expired — health-check lazily
        if _qgis.health_check():
            _qgis._last_used = time.monotonic()
            return _qgis
        # Connection is dead
        logger.warning("QGIS connection stale — reconnecting")
        _qgis.disconnect()
        _qgis = None

    with _qgis_lock:
        # Double-checked locking
        if _qgis is not None:
            return _qgis
        client = QgisSocketClient()
        client.connect()
        _qgis = client
        return client


def invalidate_connection() -> None:
    """Force-close the connection (e.g. after a critical error)."""
    global _qgis
    if _qgis:
        _qgis.disconnect()
        _qgis = None


# ---------------------------------------------------------------------------
# Command dispatch with retry
# ---------------------------------------------------------------------------

_RETRY_DELAYS = (0.5, 1.0, 2.0)  # seconds
_FIRST_RETRY_DELAYS = (0.5, 1.0, 2.0, 4.0, 8.0)  # first-ever connect


def _send_sync(
    cmd_type: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Synchronous send with retry — call from asyncio.to_thread."""
    delays = _FIRST_RETRY_DELAYS if _qgis is None else _RETRY_DELAYS
    last_exc: Exception | None = None

    for attempt, delay in enumerate(delays):
        try:
            qgis = get_qgis_connection()
            return qgis.send(cmd_type, params)
        except QgisSocketError as exc:
            last_exc = exc
            logger.warning(
                "Attempt %d/%d failed for '%s': %s",
                attempt + 1, len(delays), cmd_type, exc,
            )
            invalidate_connection()
            if attempt < len(delays) - 1:
                time.sleep(delay)
        except Exception as exc:
            last_exc = exc
            logger.error("Unexpected error in '%s': %s", cmd_type, exc)
            invalidate_connection()
            raise

    # All retries exhausted
    hint = _get_error_hint(cmd_type, last_exc)
    if hint:
        msg = f"QGIS plugin did not respond after {len(delays)} attempts.\n{hint}"
    else:
        msg = f"QGIS plugin did not respond after {len(delays)} attempts: {last_exc}"
    raise QgisSocketError(msg)


_ERROR_HINTS: dict[str, str] = {
    "ping": (
        "  • Is QGIS running?\n"
        "  • Is the QGIS MCP plugin started? (Plugins → QGIS MCP → Start Server)\n"
        "  • Port match? Default 9876 in both plugin and server."
    ),
    "load_project": (
        "  • File exists and is readable?\n"
        "  • Path uses forward slashes or raw string on Windows?"
    ),
    "add_vector_layer": (
        "  • File exists? Supported formats: .shp, .gpkg, .geojson, .gml, .kml\n"
        "  • File not currently open in another application?"
    ),
    "add_raster_layer": (
        "  • File exists? Supported: .tif/.tiff, .asc, .hdf\n"
        "  • Corrupted raster or wrong driver?"
    ),
    "execute_processing": (
        "  • Algorithm ID correct? Run list_processing_algorithms first.\n"
        "  • Parameter names and types match the algorithm.\n"
        "  • Input layers are loaded in the current project."
    ),
    "render_map": (
        "  • At least one visible layer in the project?\n"
        "  • Output path writable?"
    ),
    "execute_code": (
        "  • PyQGIS syntax error — test in QGIS Python console first.\n"
        "  • Code accesses a layer that doesn't exist."
    ),
}


def _get_error_hint(cmd_type: str, exc: Exception | None) -> str:
    """Return a user-friendly hint for common errors."""
    msg = str(exc) if exc else ""
    if "Connection refused" in msg or "Cannot connect" in msg:
        return (
            "QGIS plugin is not reachable.\n"
            "  • Is QGIS running?\n"
            "  • Is the QGIS MCP plugin server started?\n"
            "  • Check port: QGIS_MCP_PORT (default 9876) must match the plugin setting."
        )
    if "ModuleNotFoundError" in msg or "No module named" in msg:
        return (
            "Missing Python dependency. Try:\n"
            "  uv sync --directory mcp-servers/qgis\n"
            "then re-register with claude mcp add."
        )
    return _ERROR_HINTS.get(cmd_type, "")


async def _send(
    cmd_type: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Async wrapper around _send_sync (runs in thread to avoid blocking)."""
    return await asyncio.to_thread(_send_sync, cmd_type, params)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[dict[str, Any]]:
    """Server lifespan — connect on start, disconnect on stop.

    Does NOT crash if QGIS is unavailable — logs a warning and defers
    connection to first tool call (lazy).
    """
    logger.info("QGIS MCP server starting up")
    try:
        get_qgis_connection()
    except QgisSocketError as exc:
        logger.warning("QGIS not available at startup: %s", exc)
        logger.warning("Tools will attempt connection on first use.")
    try:
        yield {}
    finally:
        invalidate_connection()
        logger.info("QGIS MCP server shut down")


# ---------------------------------------------------------------------------
# FastMCP instance
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "QgisMCP",
    instructions=(
        "QGIS MCP server — bridges Claude Code with QGIS Desktop for "
        "geospatial analysis. Use get_qgis_info before starting work; "
        "load layers with add_vector_layer / add_raster_layer; inspect "
        "data with get_layer_features; process with execute_processing; "
        "render maps to PNG with render_map."
    ),
    lifespan=server_lifespan,
)

# ---------------------------------------------------------------------------
# Tools (15) — matching existing skills and docs
# ---------------------------------------------------------------------------


@mcp.tool(
    description="Check connectivity with the QGIS plugin.",
)
async def ping(ctx: Context) -> str:
    return await _send("ping")


@mcp.tool(
    description="Return QGIS version and environment information.",
)
async def get_qgis_info(ctx: Context) -> str:
    result = await _send("get_qgis_info")
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Load a QGIS project (.qgz / .qgs) from *path*.",
)
async def load_project(ctx: Context, path: str) -> str:
    result = await _send("load_project", {"path": path})
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Create and save a new (empty) QGIS project at *path*.",
)
async def create_new_project(ctx: Context, path: str) -> str:
    result = await _send("create_new_project", {"path": path})
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Return metadata about the current project (CRS, layers, extent).",
)
async def get_project_info(ctx: Context) -> str:
    result = await _send("get_project_info")
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Add a vector layer (shapefile, GeoPackage, GeoJSON, …) to the project.",
)
async def add_vector_layer(
    ctx: Context,
    path: str,
    provider: str = "ogr",
    name: str | None = None,
) -> str:
    params: dict[str, Any] = {"path": path, "provider": provider}
    if name is not None:
        params["name"] = name
    result = await _send("add_vector_layer", params)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Add a raster layer (GeoTIFF, …) to the project.",
)
async def add_raster_layer(
    ctx: Context,
    path: str,
    provider: str = "gdal",
    name: str | None = None,
) -> str:
    params: dict[str, Any] = {"path": path, "provider": provider}
    if name is not None:
        params["name"] = name
    result = await _send("add_raster_layer", params)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="List all layers in the current project.",
)
async def get_layers(ctx: Context) -> str:
    result = await _send("get_layers")
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Remove a layer from the project by its *layer_id*.",
)
async def remove_layer(ctx: Context, layer_id: str) -> str:
    result = await _send("remove_layer", {"layer_id": layer_id})
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Zoom the map canvas to the extent of the layer identified by *layer_id*.",
)
async def zoom_to_layer(ctx: Context, layer_id: str) -> str:
    result = await _send("zoom_to_layer", {"layer_id": layer_id})
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Return features (attributes + geometry WKT) from a vector layer (max *limit*).",
)
async def get_layer_features(ctx: Context, layer_id: str, limit: int = 10) -> str:
    result = await _send(
        "get_layer_features",
        {"layer_id": layer_id, "limit": min(limit, 1000)},
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Run a QGIS Processing algorithm by *algorithm* ID with *parameters* dict.",
)
async def execute_processing(ctx: Context, algorithm: str, parameters: dict) -> str:
    result = await _send(
        "execute_processing",
        {"algorithm": algorithm, "parameters": parameters},
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Save the current project. If *path* is omitted, saves in-place.",
)
async def save_project(ctx: Context, path: str | None = None) -> str:
    params: dict[str, Any] = {}
    if path is not None:
        params["path"] = path
    result = await _send("save_project", params)
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Render the current map canvas to a PNG image at *path* (default 800×600).",
)
async def render_map(
    ctx: Context,
    path: str,
    width: int = 800,
    height: int = 600,
) -> str:
    result = await _send(
        "render_map",
        {"path": path, "width": width, "height": height},
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


@mcp.tool(
    description="Execute arbitrary PyQGIS code inside QGIS (use with extreme caution).",
)
async def execute_code(ctx: Context, code: str) -> str:
    result = await _send("execute_code", {"code": code})
    return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    """Start the MCP server (stdio transport)."""
    logger.info("Starting QGIS MCP server (transport=stdio)")
    mcp.run()


if __name__ == "__main__":
    main()
