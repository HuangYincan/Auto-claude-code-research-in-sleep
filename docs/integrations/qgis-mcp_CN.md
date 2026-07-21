# QGIS-MCP 集成指南

[QGIS-MCP](https://github.com/nkarasiak/qgis-mcp) 通过模型上下文协议（MCP）将 **QGIS Desktop**（开源 GIS 桌面应用）与 Claude Code 连接起来。它让大语言模型能够驱动地理空间分析：加载 GIS 数据、运行处理算法、渲染地图和执行 PyQGIS 代码——全部在研究流水线中完成。

## 架构

```
Claude Code（MCP 主机）
     ↕ stdio（JSON-RPC，通过 FastMCP）
mcp-servers/qgis/server.py     ← ARIS 自带的 MCP 服务器
     ↕ TCP socket（localhost:9876，长度前缀帧协议）
QGIS MCP 插件（QGIS 内部）    ← 单独安装（nkarasiak/qgis-mcp）
     ↕ PyQGIS API
QGIS Desktop
```

**QGIS 插件**（来自 [nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp) 仓库）在 QGIS 内部运行，启动一个 socket 服务器。**ARIS MCP 服务器**（`mcp-servers/qgis/server.py`）连接到该 socket，将 MCP 工具调用转换成 QGIS 命令。

## 前提条件

1. **uv** — MCP 注册命令需要：
   ```bash
   brew install uv          # macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh   # 其他平台
   ```

2. **QGIS Desktop 3.x** — [下载地址](https://qgis.org/download/)

3. **Python 3.12+** — QGIS 自带或系统安装

## 安装

### 1. 安装 QGIS 插件

[nkarasiak/qgis-mcp](https://github.com/nkarasiak/qgis-mcp) 仓库同时提供 QGIS 插件和规范的 MCP 服务器。我们只需要把插件装进 QGIS。

**选项 A — 自动安装（推荐）：**
```bash
git clone https://github.com/nkarasiak/qgis-mcp.git /path/to/qgis-mcp
cd /path/to/qgis-mcp
python install.py            # 自动创建插件软链接 + 配置客户端
```

**选项 B — 手动创建软链接：**
```bash
git clone https://github.com/nkarasiak/qgis-mcp.git /path/to/qgis-mcp

# macOS
ln -s /path/to/qgis-mcp/qgis_mcp_plugin \
  ~/Library/Application\ Support/QGIS/QGIS3/profiles/default/python/plugins/qgis_mcp

# Linux
ln -s /path/to/qgis-mcp/qgis_mcp_plugin \
  ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/qgis_mcp

# Windows PowerShell（无需管理员权限）
# New-Item -ItemType Junction -Path "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins\qgis_mcp" -Target "C:\path\to\qgis-mcp\qgis_mcp_plugin"
```

重启 QGIS，然后通过 **插件 → 管理并安装插件 → QGIS MCP** 启用该插件。

### 2. 在 QGIS 中启动服务器

打开 QGIS MCP 面板（**插件 → QGIS MCP → QGIS MCP**），确认端口（默认 9876），然后点击 **Start Server**。状态应显示 "Server: Running on port 9876"。

### 3. 向 Claude Code 注册 MCP 服务器

提供两种注册方式：

**选项 A — 本地服务器（15 个核心工具）：**
使用 ARIS 自带的 `mcp-servers/qgis/` 服务器：
```bash
claude mcp add qgis -s project -- \
  uv --directory /path/to/aris/mcp-servers/qgis run server.py
```
执行该命令时，`uv` 会自动创建隔离的虚拟环境（在 uv 缓存或 `mcp-servers/qgis/.venv` 中），安装 `mcp` SDK，然后启动服务器。

**选项 B — 远程/上游（102 个工具，更简单）：**
直接从 GitHub 拉取规范的服务器，无需本地代码：
```bash
claude mcp add qgis -s project -- \
  uvx --from https://github.com/nkarasiak/qgis-mcp/archive/refs/heads/main.zip \
  qgis-mcp-server
```

> **注意：** 两种方式都要求 QGIS 正在运行且插件服务器已启动。选项 B 设置更简单，提供上游全部 102 个工具，但依赖 GitHub 仓库的可访问性。

### 4. 验证

在 Claude Code 中输入 `/qgis-mcp` 并执行 `ping`。如果 QGIS 正在运行且插件服务器已启动，你应该会看到成功的响应。

```bash
claude mcp list | grep qgis
```

## 暴露的工具（本地服务器 — 15 个）

| 工具 | 功能 |
|---|---|
| `ping` | 检查与 QGIS 插件的连接 |
| `get_qgis_info` | 返回 QGIS 版本和环境信息 |
| `load_project` | 从路径加载 .qgz / .qgs 项目 |
| `create_new_project` | 创建并保存一个新的空项目 |
| `get_project_info` | 当前项目元数据（CRS、图层等） |
| `add_vector_layer` | 添加 shapefile / GeoPackage / GeoJSON 等矢量图层 |
| `add_raster_layer` | 添加 GeoTIFF 等栅格图层 |
| `get_layers` | 列出项目中所有图层 |
| `remove_layer` | 按 ID 移除图层 |
| `zoom_to_layer` | 将画布缩放到某图层范围 |
| `get_layer_features` | 查询要素（属性 + WKT 几何） |
| `execute_processing` | 运行任意 QGIS 处理工具箱算法 |
| `save_project` | 保存当前项目 |
| `render_map` | 将画布渲染为 PNG 图像 |
| `execute_code` | 执行任意 PyQGIS 代码（⚠ 谨慎使用） |

**远程/上游路径** 提供 102 个工具，包括图层样式、图集导出、3D 视图、打印布局构造、SQL 查询等。

## 在研究流水线中的使用

`/qgis-mcp` 技能（见 `skills/qgis-mcp/`）将 QGIS 集成到 ARIS 工作流中：

- **空间数据发现** — 加载、检查和查询地理空间数据集
- **自动化地图制作** — 以编程方式渲染出版级地图
- **地理空间 ML 预处理** — 将 QGIS 处理算法用作特征工程步骤
- **结果可视化** — 在底图上叠加研究输出

与 `/research-pipeline` 结合使用可实现端到端地理空间 ML 研究：

```
/research-pipeline "基于深度学习的滑坡易发性制图" -- qgis-mcp: true
```

## 故障排除

| 症状 | 检查 |
|---|---|
| `uv: command not found` | 安装 uv：`brew install uv` 或 `curl -LsSf https://astral.sh/uv/install.sh | sh` |
| `mcp module not found` | uv 未能解析依赖——检查 `mcp-servers/qgis/` 下是否存在 `pyproject.toml` |
| `Could not connect to QGIS` | QGIS 是否正在运行？插件服务器是否已启动？ |
| `Connection refused` | 端口不匹配——插件和服务器的默认端口都是 9876 |
| 工具返回空数据 | 是否已加载项目？QGIS 中的图层是否可见？ |

## 相关文件

| 路径 | 用途 |
|---|---|
| `mcp-servers/qgis/server.py` | ARIS 自带的 MCP 服务器（FastMCP，TCP socket 客户端） |
| `mcp-servers/qgis/pyproject.toml` | Python 项目配置（uv 包，`mcp[cli]` 依赖） |
| `mcp-servers/qgis/README.md` | 服务器设置指南 |
| `skills/qgis-mcp/SKILL.md` | ARIS 的 QGIS 工作流技能 |
| `.env`（项目根目录） | `QGIS_MCP_HOST`、`QGIS_MCP_PORT` |
