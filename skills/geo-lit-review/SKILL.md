---
name: geo-lit-review
description: "Earth-science-domain literature review — AGU / EGU / GSA / GeoRef / USGS searches, venue tiering, and keyword strategies for geosciences. Use when the task is about physical geography, geology, hydrology, climatology, ecology, remote sensing, geophysics, environmental science or natural hazards and the user wants papers, related work, a survey, or a landscape summary."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, mcp__zotero__*
---

# Geo Lit Review: Earth Science Literature Review

Research topic: $ARGUMENTS

## Purpose

Use this skill for earth-science-domain literature review when the topic is about:

- physical geography, geomorphology, soil science
- geology, structural geology, sedimentology, paleontology
- hydrology, hydrogeology, water resources, limnology
- climatology, meteorology, atmospheric science, paleoclimate
- ecology, biogeography, vegetation dynamics, conservation
- remote sensing, satellite imagery, Earth observation
- geophysics, seismology, volcanology, geodesy
- environmental science, natural hazards, global change

If the centre of gravity is generic ML architecture research, pure engineering without geospatial context, or software/API documentation rather than papers, fall back to a general literature skill.

## Constants

- **PAPER_LIBRARY**: Check local PDFs in this order:
  1. `papers/` in the current project
  2. `literature/` in the current project
  3. Custom path in `CLAUDE.md` under `## Paper Library`
- **MAX_LOCAL_PAPERS = 20**: Maximum number of local PDFs to scan.

## Source Selection

Parse `$ARGUMENTS` for a `— sources:` directive.

If `— sources:` is specified, only search the listed sources. If not specified, default to `agu egu gsa web`.

Valid source values:

| Source | Scope | Access |
|---|---|---|
| `agu` | AGU journals: JGR-ES, GRL, WRR, Earth's Future, G-Cubed, Tectonics, Paleoceanography | agupubs.onlinelibrary.wiley.com |
| `egu` | EGU journals: HESS, NHESS, ESSD, GMD, TC, BG, SE, GI, SOIL, WES, ANGEO | egu.eu (Open Access) |
| `gsa` / `gsw` | GSA Bulletin, Geology; GeoScienceWorld journals (AAPG, SEG, SEPM) | pubs.geoscienceworld.org |
| `usgs` | USGS Publications Warehouse — reports, maps, professional papers | pubs.usgs.gov |
| `georef` | GeoRef — comprehensive geoscience bibliography (AGI) | Via institutional access |
| `web` | General web search (Google Scholar, Semantic Scholar) | Open |
| `zotero` | Local Zotero library; searches full-text notes and tags | Via MCP |
| `local` | Local PDF folders (see PAPER_LIBRARY constant) | Filesystem |

## Search Keywords per Subdomain

### Hydrology / Water Resources
```
(streamflow OR groundwater OR "water balance" OR "hydrological modelling")
  AND (trend OR change OR projection OR climate)
  AND (catchment OR watershed OR basin OR aquifer)
```
Target journals: J. Hydrol., HESS, WRR, Hydrol. Process., J. Hydrometeorol.

### Geology / Geomorphology
```
(landslide OR erosion OR tectonics OR fault OR "rock type" OR lithology)
  AND (susceptibility OR hazard OR inventory OR mapping)
  AND (GIS OR remote sensing OR "machine learning" OR "deep learning")
```
Target journals: GSA Bulletin, Geology, JGR-ES, Geomorphology, Eng. Geol.

### Climatology / Meteorology
```
(climate OR precipitation OR temperature OR extreme)
  AND (trend OR projection OR variability OR "climate change")
  AND (downscaling OR GCM OR RCM OR CMIP5 OR CMIP6)
```
Target journals: J. Climate, Clim. Dyn., IJoC, J. Hydrometeorol., JGR-Atmos.

### Remote Sensing / Earth Observation
```
(satellite OR "remote sensing" OR Earth observation OR SAR OR optical)
  AND (classification OR segmentation OR change detection OR mapping)
  AND (land cover OR vegetation OR water OR urban)
```
Target journals: Remote Sens. Environ., IEEE TGRS, ISPRS JPRS, Int. J. Remote Sens.

### Natural Hazards
```
(earthquake OR flood OR landslide OR wildfire OR drought OR tsunami)
  AND (hazard OR risk OR vulnerability OR exposure OR susceptibility)
  AND (modelling OR assessment OR mapping OR prediction)
```
Target journals: Nat. Hazards, NHESS, Eng. Geol., J. Flood Risk Manag.

## Venue Tiering

### Tier A: Top geoscience journals (start here)

| Subdomain | Journals |
|---|---|
| Hydrology | HESS, WRR, J. Hydrol., J. Hydrometeorol. |
| Geology | GSA Bulletin, Geology, JGR-ES, Geomorphology |
| Climate | J. Climate, Clim. Dyn., IJoC, JGR-Atmos. |
| Remote Sensing | RSE, IEEE TGRS, ISPRS JPRS |
| Hazards | NHESS, Nat. Hazards, Eng. Geol. |
| General | Nature Geoscience, Science Advances, PNAS, ESSD |

### Tier B: Strong mainstream venues

AGU journals (GRL, JGR series), EGU journals (TC, BG, GI, SE, SOIL), GSW journals, journals from IAH, IAHS, IUGG.

### Tier C: Broader literature

Local/institutional journals, conference proceedings (AGU Fall Meeting, EGU General Assembly, IAHS), reports, theses.

## Boundary Cases

- **Include:** any research with a spatial/geographic component AND earth science domain context
- **Exclude (fall back to general lit skill):** pure ML methodology without Earth-science data; pure civil/structural engineering; pure ecology with no spatial component; software documentation

## Output

Deliver a structured literature review with:
1. Number of papers found per source
2. Key themes and trends identified
3. Gaps or controversies in the literature
4. Most relevant papers for the research question (with full citations)
5. **审查状态：** 数据源审查 [通过/不适用]、中国合规审查 [通过/不适用]、
   结果审查 [通过/不适用] — **必须注明**

---

## ⚠️ 审查与关键检查 (Review & Critical Checks) ⛔ 强制环节

> **⛔ 硬性规定：** 在输出任何文献综述结果前，**必须先完成以下全部审查并确认通过，
> 否则不得交付结果。禁止跳过审查环节。**

### ⚡ 数据源黄金规则 (Golden Rule — Do NOT Fabricate Data)

用户要求绘制或补充任何地理要素（如九段线、国界线、海岸线等）时：
1. **必须查找官方数据源** — 天地图、国家基础地理信息中心、自然资源部发布的权威数据
2. **严禁用代码手画** — 不要自己用 Python 或 PyQGIS 代码绘制地理要素边界，这不是科学严谨的做法
3. **找不到数据则如实告知** — 如果无法找到官方数据源，明确告知用户"未找到相关官方数据"
4. **唯一例外** — 用户明确要求"用代码绘制"时才可这样做

### 1. 数据源审查 (Data Source Audit)
- [ ] 涉及中国区域的地学文献，是否覆盖了国内重要期刊（如《地理学报》《地球信息科学学报》等）？
- [ ] 数据来源（论文 PDF、数据集 URL）是否完整记录？

### 2. 中国合规审查 (China Compliance Audit)
- [ ] 综述中涉及中国领土、边界、台湾等表述是否正确？
- [ ] 台湾的研究机构表述为"中国台湾"或"Taiwan, China"
- [ ] 南海、藏南等区域的地名使用官方标准名称

### 3. 结果审查 (Output Audit)
- [ ] 文献检索策略可复现？
- [ ] 关键论文的全引用信息完整？
- [ ] 知识空白和争议点已明确标注？
