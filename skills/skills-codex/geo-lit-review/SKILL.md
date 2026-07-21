---
name: geo-lit-review
description: "Earth-science-domain literature review — AGU / EGU / GSA / GeoRef / USGS searches, venue tiering, and keyword strategies for geosciences. Use when the task is about physical geography, geology, hydrology, climatology, ecology, remote sensing, geophysics, environmental science or natural hazards and the user wants papers, related work, a survey, or a landscape summary."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch
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
  3. Custom path in `AGENT_GUIDE.md` under `## Paper Library`
- **MAX_LOCAL_PAPERS = 20**: Maximum number of local PDFs to scan.

## Source Selection

Parse `$ARGUMENTS` for a `— sources:` directive.

If `— sources:` is specified, only search the listed sources. If not specified, default to `agu egu gsa web`.

Valid source values:

| Source | Scope | Access |
|---|---|---|
| `agu` | AGU journals: JGR-ES, GRL, WRR, Earth's Future, G-Cubed, Tectonics | agupubs.onlinelibrary.wiley.com |
| `egu` | EGU journals: HESS, NHESS, ESSD, GMD, TC, BG, SE, GI, SOIL | egu.eu (Open Access) |
| `gsa` / `gsw` | GSA Bulletin, Geology; GeoScienceWorld journals | pubs.geoscienceworld.org |
| `usgs` | USGS Publications Warehouse | pubs.usgs.gov |
| `georef` | GeoRef — comprehensive geoscience bibliography (AGI) | Via institutional access |
| `web` | General web search (Google Scholar, Semantic Scholar) | Open |
| `local` | Local PDF folders (see PAPER_LIBRARY constant) | Filesystem |

## Search Keywords per Subdomain

### Hydrology / Water Resources
```
(streamflow OR groundwater OR "water balance" OR "hydrological modelling")
  AND (trend OR change OR projection OR climate)
  AND (catchment OR watershed OR basin OR aquifer)
```

### Geology / Geomorphology
```
(landslide OR erosion OR tectonics OR fault OR lithology)
  AND (susceptibility OR hazard OR inventory OR mapping)
  AND (GIS OR "remote sensing" OR "machine learning")
```

### Climatology / Meteorology
```
(climate OR precipitation OR temperature OR extreme)
  AND (trend OR projection OR variability OR "climate change")
  AND (downscaling OR GCM OR RCM OR CMIP5 OR CMIP6)
```

### Remote Sensing
```
(satellite OR "remote sensing" OR Earth observation OR SAR OR optical)
  AND (classification OR segmentation OR change detection OR mapping)
  AND ("land cover" OR vegetation OR water OR urban)
```

### Natural Hazards
```
(earthquake OR flood OR landslide OR wildfire OR drought OR tsunami)
  AND (hazard OR risk OR vulnerability OR susceptibility OR exposure)
  AND (modelling OR assessment OR mapping OR prediction)
```

## Venue Tiering

| Tier | Scope |
|---|---|
| **A** | Nature Geoscience, Science Advances, PNAS, AGU/EGU top journals per subdomain |
| **B** | Other AGU/EGU/GSW journals, IAH/IAHS/IUGG journals |
| **C** | Local journals, conference proceedings (AGU Fall Meeting, EGU GA), reports, theses |

## Boundary Cases

- **Include:** research with spatial/geographic component AND earth science context
- **Exclude:** pure ML without Earth data; pure engineering; pure ecology without geospatial context

## Output

Structured review with: number of papers per source, key themes, gaps, most relevant papers.
