# VR CAVE Companion App — Design Document

**Date:** 2026-03-02
**Status:** Approved
**Stack:** A-Frame 1.7.1 + WebXR + Blender MCP (custom assets)
**Target:** Meta Quest (2/3/Pro) via Quest Browser
**Audience:** Journalism / documentary — self-guided, educational
**Data Source:** Existing ICE Data Explorer REST API (8 endpoints, 36 tables)

---

## 1. Overview

An immersive WebXR experience that accompanies the ICE Data Explorer web app. The user enters a white void environment and navigates between four rooms via portals, each presenting immigration enforcement data in a different spatial format. A fifth element — real raid footage with data overlays — grounds the abstract data in reality.

The experience pulls live data from the existing REST API, maintaining the same source transparency, verification badges, and contradiction tracking as the web app.

---

## 2. Architecture

### Project Structure

```
ice-data-explorer/
├── app.py                  # Existing Dash app (unchanged)
├── database.py             # Existing DB (unchanged)
├── vr/                     # NEW — VR companion app
│   ├── index.html          # A-Frame scene entry point
│   ├── css/
│   │   └── hud.css         # HUD overlay styles
│   ├── js/
│   │   ├── app.js          # Scene init, portal logic
│   │   ├── data-api.js     # Fetch wrapper for REST API
│   │   ├── hub.js          # Central hub room
│   │   ├── landscape.js    # Data terrain room
│   │   ├── globe.js        # Facility globe room
│   │   ├── timeline.js     # Timeline corridor room
│   │   ├── footage.js      # Raid footage room
│   │   └── components/     # Custom A-Frame components
│   │       ├── data-bar.js
│   │       ├── data-terrain.js
│   │       ├── video-panel.js
│   │       ├── portal.js
│   │       ├── tooltip-3d.js
│   │       ├── globe-marker.js
│   │       ├── flow-arc.js
│   │       ├── contradiction.js
│   │       ├── content-gate.js
│   │       └── room-manager.js
│   ├── assets/
│   │   ├── models/         # GLTF from Blender MCP
│   │   ├── audio/          # Spatial audio files
│   │   ├── video/          # Raid footage clips
│   │   └── textures/       # Terrain, UI textures
│   └── README.md
```

### Data Flow

```
VR App (A-Frame) → fetch() → REST API (/api/*) → SQLite/PostgreSQL → JSON response → 3D rendering
```

### Deployment

Static files served from the same Vercel deployment or a subdomain. No separate backend required.

---

## 3. Central Hub (White Void)

### Environment

- Infinite white `<a-sky color="#FFFFFF">`
- Subtle fog (`<a-scene fog="type: exponential; color: #FFF; density: 0.02">`) for depth
- Faint ground grid (transparent plane with grid texture) for orientation
- Ambient spatial audio: low, barely perceptible hum

### Portal Layout

Four portals in a semicircle, 5m from user spawn, at eye level:

```
                    [Timeline Walk]
                         |
        [Data Landscape] · [Facility Globe]
                         |
                   [Raid Footage]

              ← 5m →  [USER]  ← 5m →
```

### Portal Design

Each portal is a 2m tall rectangular archway (Blender MCP asset):
- Title label floating above
- Live data preview rendered inside (like a window into the room)
- Particle drift at edges (aframe-particle-system)
- Unique spatial audio tone that intensifies on approach

### Hub HUD

- Verification badge (matches Dash app's global indicator bar)
- Data freshness timestamp
- Source filter toggle: govt-only / independent / all (maps to existing presets)
- "Return to hub" gesture: hold both controllers together for 1 second

---

## 4. Room 1 — Data Landscape

### Concept

A walkable terrain generated from real enforcement data. Height = metric value. The user physically traverses 30 years of data.

### Terrain Mesh

- X-axis: time (1994–2026, one column per year)
- Z-axis: metric category (detention, deportations, arrests, deaths, budget)
- Y-axis: value (height), normalized per category
- White/light gray base mesh

### Visual Elements

- Color-coded ridgelines: detention (blue), deportations (red), deaths (black), budget (gold), arrests (orange)
- Contradiction zones: amber glow with pulsing ring — step on one to see govt vs independent figures side-by-side
- Data gap zones: particle rain + wireframe/transparent terrain sections

### Data Sources

- `/api/statistics` — key stats
- `/api/tables/detention_population` — detention time series
- `/api/tables/deportations` — deportation time series
- `/api/tables/arrests` — arrest time series
- `/api/tables/deaths_in_custody` — death time series
- `/api/tables/agency_budgets` — budget time series
- `/api/contradictions` — contradiction overlays

### Interaction

- Teleport to any year
- Point at a ridge to see data card (value, source, trust level)
- Grab and pull a ridge upward to scale/zoom that metric

### Blender MCP Assets

- Contradiction marker: small cracked/split column (~1000 tris)
- Data gap indicator: transparent wireframe terrain section

---

## 5. Room 2 — Facility Globe

### Concept

The user stands at the center of a room-scale inverted globe (8m diameter), looking outward at the Earth's surface from inside.

### Globe Rendering

- Inverted sphere geometry — continents on the inside surface
- Minimal cartography: white landmasses, light gray borders
- 57 facility markers at real GPS coordinates (from `detention_facilities` + `facilities_geo`)

### Facility Markers

- Vertical pins scaled by capacity
- Color: private (red), government (blue), mixed (purple)
- Pulse intensity = current population as % of capacity
- Hover detail: name, operator, capacity, current pop, deaths

### Deportation Flow Arcs

- Animated particle arcs from US facilities → destination countries
- Arc thickness = deportation volume to that country
- Color = operating contractor
- Data: `deportations_by_nationality`

### Corporate Layer Toggle

- Highlight all facilities by contractor (GEO = gold, CoreCivic = blue)
- Floating revenue figure + contract value + lobbying spend
- Data: `private_prison_contracts`, `lobbying_records`, `stock_prices`

### Data Sources

- `/api/tables/detention_facilities`
- `/api/tables/deportations_by_nationality`
- `/api/tables/corporate_contractors`
- `/api/tables/federal_contracts`

### Interaction

- Grab air to rotate globe
- Teleport gaze to facility for detail view
- Pinch to filter by contractor, state, or capacity

### Blender MCP Assets

- Facility pin: tapered column with data-card attachment point (~800 tris)

---

## 6. Room 3 — Timeline Walk

### Concept

A long white corridor (~30m). Each segment is a policy era. The user walks forward through time.

### Corridor Structure

- 12-15 curated segments (not every year)
- Translucent divider walls with year/era etched on them
- Floor transitions from white to progressively darker gray

### Wall Content Per Segment

- Left wall: floating 3D bar charts (detention pop, deportations, budget for that era)
- Right wall: policy event cards (from `policy_events`) — title, date, description
- Ceiling: news sentiment indicator — warm colors (negative), cool (neutral/positive)

### Key Segments

1. Pre-ICE / INS era (pre-2003)
2. ICE creation (2003)
3. Secure Communities rollout (2008)
4. Priority Enforcement Program (2014)
5. Family separation (2018)
6. Title 42 (2020)
7. Post-Title 42 (2023)
8. Current era (2025-2026)

### Transition Moments

- At major policy shifts, corridor widens into a small room
- Data "explosion" — numbers scatter outward showing before/after impact
- Spatial audio tone shift at each transition

### Data Sources

- `/api/tables/policy_events`
- `/api/tables/detention_population`
- `/api/tables/deportations`
- `/api/tables/news_articles`

### Interaction

- Walk or teleport forward/backward
- Grab a policy card to pull closer and read
- Tap a stat bar to hear narrated summary

### Blender MCP Assets

- Divider wall: frosted glass panel with year text slot (~500 tris)
- Policy card frame: floating document/dossier look (~600 tris)

---

## 7. Room 4 — Raid Footage Chamber

### Concept

The most emotionally intense room. Real footage (FOIA releases, C-SPAN hearings, news clips) played on floating panels with live data overlays. Trauma-informed design throughout.

### Entry

- Content warning on portal: subject matter, estimated duration, explicit "I understand" confirmation
- Portal visually distinct: darker frame, no particles, somber audio
- `content-gate` component blocks entry until confirmed

### Room Layout

- Circular chamber, 10m diameter
- Off-white walls fading to gray at edges
- 6-8 floating video panels in a ring at varying heights/distances
- Each panel ~2m wide, angled toward user

### Video Panel Behavior

- Inactive state: frozen thumbnail
- Gaze at panel for 1 second → plays
- Only one panel active at a time — others dim
- Spatial audio tied to active panel's position

### Data Overlay System

When a video plays, contextual data fades in:
- Above: date and location
- Left: relevant statistics from that time period
- Right: source attribution and trust level badge
- Below (if applicable): contradiction card with both figures

All overlays use existing provenance metadata and source registry.

### Trauma-Informed Design Rules

- Nothing auto-plays — user controls all pacing
- Exit portal always visible and reachable (glowing white door)
- No jump scares or sudden audio spikes
- Volume hard-capped at 70% system max
- All identifiable faces blurred in preprocessing
- 30-second gentle fade-to-white before clip ends, with context text card
- Maximum clip length: 90 seconds

### Data Sources

- `/api/provenance` — metadata overlays
- `/api/sources` — source attribution
- `/api/contradictions` — contradiction cards
- Video files from `vr/assets/video/`

### Blender MCP Assets

- Video panel frame: thin-bordered floating screen with data card attachment points (~800 tris)
- Content warning gate: semi-transparent barrier with text (~400 tris)

---

## 8. Technical Specification

### Dependencies

```html
<script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>

<!-- Community components -->
aframe-particle-system-component  — portal effects, data gap rain
aframe-environment-component      — base environment presets
aframe-teleport-controls          — movement between points
aframe-event-set-component        — declarative event handling
aframe-look-at-component          — tooltips face user
aframe-state-component            — shared state across rooms
```

### Custom A-Frame Components

| Component | File | Purpose |
|-----------|------|---------|
| `data-terrain` | `components/data-terrain.js` | Heightfield mesh from API time series |
| `data-bar` | `components/data-bar.js` | Single 3D bar with label and color |
| `video-panel` | `components/video-panel.js` | Floating video, gaze-to-play, overlays |
| `portal` | `components/portal.js` | Room transition with preview + particles |
| `tooltip-3d` | `components/tooltip-3d.js` | Billboard text card, shows on hover |
| `globe-marker` | `components/globe-marker.js` | Facility pin on inverted sphere |
| `flow-arc` | `components/flow-arc.js` | Animated particle arc between coordinates |
| `contradiction` | `components/contradiction.js` | Split display of conflicting values |
| `content-gate` | `components/content-gate.js` | Content warning barrier |
| `room-manager` | `components/room-manager.js` | Room visibility + transitions |

### Room Management

All rooms exist in scene, only one visible at a time:

```html
<a-scene room-manager="active: hub">
  <a-entity id="hub" room="name: hub">...</a-entity>
  <a-entity id="room-landscape" room="name: landscape" visible="false">...</a-entity>
  <a-entity id="room-globe" room="name: globe" visible="false">...</a-entity>
  <a-entity id="room-timeline" room="name: timeline" visible="false">...</a-entity>
  <a-entity id="room-footage" room="name: footage" visible="false">...</a-entity>
</a-scene>
```

Portal click → `room-change` event → fade out current → fade in target → reposition user.

### Data API Layer

```javascript
class DataAPI {
  constructor(baseUrl)
  getStatistics()               // GET /api/statistics
  getSources()                  // GET /api/sources
  getContradictions()           // GET /api/contradictions
  getProvenance()               // GET /api/provenance
  getTable(name, limit, offset) // GET /api/tables/<name>
  getFacilities()               // GET /api/tables/detention_facilities
  getTimeSeries(table, years)   // fetch + reshape for terrain/timeline
}
```

In-memory cache. Fetches on room entry, not scene load.

### State Management

```javascript
AFRAME.registerState({
  initialState: {
    activeRoom: 'hub',
    sourceFilter: 'all',        // 'govt' | 'independent' | 'all'
    activeVideo: null,
    selectedYear: null,
    selectedFacility: null,
    verificationLevel: 'verified'
  }
});
```

Source filter persists across rooms.

### Performance Budget (Quest 2)

| Metric | Target |
|--------|--------|
| Draw calls / frame | < 100 |
| Triangles / room | < 200k |
| Texture memory | < 256MB total |
| Framerate | 72fps steady |
| Room load time | < 3 seconds |
| App size (excl. video) | < 30MB |

Strategies:
- One room rendered at a time
- GLTF with Draco compression
- KTX2 textures (basis universal)
- Adaptive video resolution (720p Quest 2, 1080p Quest 3)
- Terrain LOD (high detail near user, simplified at distance)

### Blender MCP Workflow

1. Describe asset to Blender MCP → generates mesh
2. Apply materials (white/gray palette, emissive accents)
3. Export as `.glb` with Draco compression
4. Place in `vr/assets/models/`
5. Reference: `<a-entity gltf-model="url(assets/models/name.glb)">`

Poly budget per asset: 500–2000 triangles.

---

## 9. Audio Design

| Location | Sound | Behavior |
|----------|-------|----------|
| Hub | Low ambient hum | Constant, spatial center |
| Hub portals | Distinct tone per portal | Louder on approach |
| Data Landscape | Wind-like generative drone | Pitch shifts with terrain height |
| Landscape contradictions | Dissonant chord | Triggered on step |
| Globe | Earth-from-space ambient | Constant, enveloping |
| Globe flow arcs | Faint whoosh | Spatial, follows arc |
| Timeline corridor | Evolving drone, darkens over time | Crossfades per segment |
| Timeline transitions | Low impact thud | On segment boundary |
| Footage chamber | Near silence | Deliberate contrast |
| Footage active panel | Video audio | Spatialized to panel position |

Format: MP3/OGG, mono for spatial sources, stereo for ambient.

---

## 10. Accessibility & Content Safety

### VR Comfort

- Teleport-only locomotion (no smooth movement)
- Minimum text height: 0.05m at 1.5m distance
- High contrast: dark text on light surfaces
- No flickering or rapid color changes

### Content Safety (Footage Room)

- Content warning gate with explicit confirmation
- Exit portal always visible from any position
- Max clip length: 90 seconds
- Auto-fade to white in final 5 seconds
- Volume capped at 70% system max
- All faces blurred in preprocessing (not runtime)

### Data Integrity

- Every data point links to source via tooltip
- Verification badges match Dash app (unchanged)
- Contradictions never hidden
- "Last updated" timestamp always in HUD

---

## 11. Blender MCP Asset Manifest

| Asset | Room | Est. Triangles | Description |
|-------|------|----------------|-------------|
| Portal frame | Hub | 1200 | Rectangular archway with emissive edge glow |
| Verification badge | Hub/HUD | 500 | Shield with checkmark |
| Contradiction marker | Landscape | 1000 | Cracked/split column |
| Data gap indicator | Landscape | 800 | Wireframe terrain section |
| Facility pin | Globe | 800 | Tapered column with card attachment |
| Divider wall | Timeline | 500 | Frosted glass panel with year slot |
| Policy card frame | Timeline | 600 | Floating document/dossier |
| Video panel frame | Footage | 800 | Thin-bordered screen with attachment points |
| Content warning gate | Footage | 400 | Semi-transparent barrier |
| **Total** | | **~6600** | Well within Quest budget |

---

## 12. Footage Sourcing Guide

### Public Domain / No Licensing Required

| Source | Type | Notes |
|--------|------|-------|
| **DVIDS** (Defense Visual Information Distribution Service) | ICE/DHS-produced raid footage | Public domain, downloadable. Stanford Law documented ICE films operations and posts them here. |
| **C-SPAN** | Congressional hearings, oversight testimony | Public domain. Detention conditions hearings, family separation testimony. |
| **FOIA Releases** | Government-produced enforcement footage | Requestable via FOIA. Stanford Immigrants' Rights Clinic successfully sued for California 2020 raid footage. |

### Investigative Journalism (Attribution Required)

| Source | Type | Notes |
|--------|------|-------|
| **Bellingcat** | OSINT forensic analysis of enforcement footage | Frame-by-frame analysis of Minneapolis CBP/ICE operations (Jan 2026). Public methodology. |
| **WITNESS Library** (library.witness.org) | Human rights video documentation frameworks | Free guides on ethical filming, consent, privacy, chain of custody. Informs our trauma-informed design. |
| **Wired** — "How to Film ICE" | Legal framework for documenting ICE operations | Rights of bystanders to film, legal protections. |

### Licensed (Budget Required)

| Source | Type | Notes |
|--------|------|-------|
| **Shutterstock** | Professional stock footage of ICE operations | Commercial license required. High quality. |
| **BBC News** | Broadcast journalism, field reporting | Licensing needed. Minneapolis deployment coverage. |
| **AP / Reuters** | Wire service footage | Standard news licensing. |

### Ethical Framework (from WITNESS.org)

All footage in the VR experience must follow WITNESS principles:
- **Informed consent** where possible; blur faces when consent not obtained
- **Do no harm** — footage must not endanger subjects or their families
- **Chain of custody** — metadata preserved from source to presentation
- **Contextualization** — never present footage without data context (dates, stats, source attribution)
- **Right to refuse** — content gate ensures users choose to view; exit always available
