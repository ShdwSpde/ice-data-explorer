# VR CAVE Companion App — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an A-Frame WebXR VR experience for Meta Quest with a white void hub and four data rooms, pulling live data from the existing ICE Data Explorer REST API.

**Architecture:** Static HTML/JS app in `vr/` directory using A-Frame 1.7.1 + custom components. Calls existing REST API for data. Blender MCP for custom 3D assets. Deployed as static files alongside the Dash app.

**Tech Stack:** A-Frame 1.7.1, WebXR, Three.js (via A-Frame), vanilla JS modules, Blender MCP for GLTF assets

**Design Doc:** `docs/plans/2026-03-02-vr-cave-design.md`

---

## Task 1: Scaffold VR Directory and Index Page

**Files:**
- Create: `vr/index.html`
- Create: `vr/css/hud.css`
- Create: `vr/js/app.js`

**Step 1: Create directory structure**

Run:
```bash
mkdir -p vr/{css,js/components,assets/{models,audio,video,textures}}
```

**Step 2: Create `vr/index.html` — minimal A-Frame scene**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>ICE Data Explorer — VR Experience</title>
  <meta name="description" content="Immersive VR companion to the ICE Data Explorer">
  <script src="https://aframe.io/releases/1.7.1/aframe.min.js"></script>
  <script src="https://unpkg.com/aframe-environment-component@1.3.7/dist/aframe-environment-component.min.js"></script>
  <script src="https://unpkg.com/@c-frame/aframe-particle-system-component@1.2.3/dist/aframe-particle-system-component.min.js"></script>
  <script src="https://unpkg.com/aframe-event-set-component@5.0.0/dist/aframe-event-set-component.min.js"></script>
  <script src="https://unpkg.com/aframe-look-at-component@1.0.0/dist/aframe-look-at-component.min.js"></script>
  <link rel="stylesheet" href="css/hud.css">
</head>
<body>
  <a-scene
    fog="type: exponential; color: #FFFFFF; density: 0.015"
    vr-mode-ui="enabled: true"
    renderer="antialias: true; colorManagement: true"
  >
    <!-- Assets preloader -->
    <a-assets>
    </a-assets>

    <!-- White void sky -->
    <a-sky color="#FFFFFF"></a-sky>

    <!-- Ground grid -->
    <a-plane
      position="0 0 0"
      rotation="-90 0 0"
      width="100"
      height="100"
      material="color: #F5F5F5; opacity: 0.3; transparent: true; wireframe: true"
    ></a-plane>

    <!-- Camera rig -->
    <a-entity id="rig" position="0 0 0">
      <a-entity
        id="camera"
        camera
        position="0 1.6 0"
        look-controls="pointerLockEnabled: false"
        wasd-controls="acceleration: 20"
      >
        <a-entity
          id="cursor"
          cursor="fuse: true; fuseTimeout: 1000"
          position="0 0 -1"
          geometry="primitive: ring; radiusInner: 0.015; radiusOuter: 0.02"
          material="color: #333; shader: flat"
          raycaster="objects: .clickable"
        ></a-entity>
      </a-entity>
      <a-entity id="left-hand" laser-controls="hand: left" raycaster="objects: .clickable"></a-entity>
      <a-entity id="right-hand" laser-controls="hand: right" raycaster="objects: .clickable"></a-entity>
    </a-entity>

    <!-- Hub room (default) -->
    <a-entity id="hub">
      <a-text
        value="ICE DATA EXPLORER"
        position="0 3 -5"
        align="center"
        color="#333"
        width="8"
        font="monoid"
      ></a-text>
      <a-text
        value="VR EXPERIENCE"
        position="0 2.5 -5"
        align="center"
        color="#666"
        width="4"
        font="monoid"
      ></a-text>
    </a-entity>
  </a-scene>

  <script src="js/app.js"></script>
</body>
</html>
```

**Step 3: Create `vr/css/hud.css` — minimal HUD styles**

```css
/* HUD overlay for non-VR fallback info */
.vr-hud {
  position: fixed;
  bottom: 20px;
  left: 20px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 12px;
  color: #333;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border: 1px solid #ddd;
  z-index: 999;
  pointer-events: none;
}
```

**Step 4: Create `vr/js/app.js` — entry point**

```javascript
/**
 * ICE Data Explorer — VR Experience
 * Main application entry point
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('[VR] ICE Data Explorer VR Experience initialized');
});
```

**Step 5: Verify scene loads in browser**

Run:
```bash
cd vr && python3 -m http.server 8081
```

Open `http://localhost:8081` in browser. Verify: white void with title text, fuse cursor visible, VR button in bottom-right.

**Step 6: Commit**

```bash
git add vr/
git commit -m "feat(vr): scaffold A-Frame scene with white void hub"
```

---

## Task 2: Expand REST API for VR Data Needs

**Files:**
- Modify: `app.py:60-65` (API_TABLES list)

**Step 1: Add missing tables to API_TABLES**

The VR app needs these tables not currently in `API_TABLES`:
- `deportations_by_nationality` — globe flow arcs
- `policy_events` — timeline segments
- `corporate_contractors` — corporate layer
- `federal_contracts` — contract values
- `private_prison_contracts` — revenue data
- `lobbying_records` — lobbying spend
- `stock_prices` — stock correlation

In `app.py`, replace the `API_TABLES` list:

```python
API_TABLES = [
    'agency_budgets', 'arrests', 'deaths_in_custody', 'deportations',
    'deportations_by_nationality', 'detention_facilities',
    'detention_population', 'key_statistics', 'source_registry',
    'data_provenance', 'source_contradictions', 'data_changelog',
    'foia_requests', 'news_articles', 'policy_events',
    'corporate_contractors', 'federal_contracts',
    'private_prison_contracts', 'lobbying_records', 'stock_prices'
]
```

**Step 2: Add CORS headers for VR app**

At the top of `app.py`, after the existing imports, add:

```python
from flask import after_this_request
```

Add a CORS handler after the `server = app.server` line:

```python
@server.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
```

**Step 3: Verify API serves new tables**

Run:
```bash
python3 app.py &
curl -s http://localhost:8050/api/tables | python3 -m json.tool
curl -s http://localhost:8050/api/tables/policy_events | python3 -m json.tool
curl -s http://localhost:8050/api/tables/deportations_by_nationality?limit=5 | python3 -m json.tool
```

Expected: JSON responses with data from each new table.

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat(api): expose additional tables and add CORS for VR app"
```

---

## Task 3: Build Data API Client (`data-api.js`)

**Files:**
- Create: `vr/js/data-api.js`

**Step 1: Write the DataAPI class**

```javascript
/**
 * DataAPI — Fetch wrapper for ICE Data Explorer REST API
 * Caches responses in memory. Fetches on room entry.
 */
class DataAPI {
  constructor(baseUrl = '') {
    // Default to same origin; override for cross-origin
    this.baseUrl = baseUrl || window.location.origin.replace(':8081', ':8050');
    this.cache = new Map();
  }

  async _fetch(endpoint) {
    if (this.cache.has(endpoint)) {
      return this.cache.get(endpoint);
    }
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`API ${res.status}: ${url}`);
      const json = await res.json();
      this.cache.set(endpoint, json);
      return json;
    } catch (err) {
      console.error(`[DataAPI] Failed: ${endpoint}`, err);
      return null;
    }
  }

  async getStatistics() {
    return this._fetch('/api/statistics');
  }

  async getSources() {
    return this._fetch('/api/sources');
  }

  async getContradictions() {
    return this._fetch('/api/contradictions');
  }

  async getProvenance() {
    return this._fetch('/api/provenance');
  }

  async getTable(name, limit = 1000, offset = 0) {
    return this._fetch(`/api/tables/${name}?limit=${limit}&offset=${offset}`);
  }

  async getFacilities() {
    return this.getTable('detention_facilities');
  }

  async getPolicyEvents() {
    return this.getTable('policy_events');
  }

  async getDeportationsByNationality() {
    return this.getTable('deportations_by_nationality');
  }

  /**
   * Fetch a time series table and reshape into { year: value } objects.
   * Expects the table to have a 'year' column.
   */
  async getTimeSeries(tableName, valueColumn) {
    const result = await this.getTable(tableName);
    if (!result || !result.data) return [];
    return result.data.map(row => ({
      year: row.year || row.fiscal_year,
      value: row[valueColumn] || 0,
      ...row
    }));
  }

  clearCache() {
    this.cache.clear();
  }
}

// Global singleton
window.dataAPI = new DataAPI();
```

**Step 2: Add script to `index.html`**

Add before `app.js`:
```html
<script src="js/data-api.js"></script>
```

**Step 3: Verify in browser console**

Run:
```bash
cd vr && python3 -m http.server 8081
```

Open `http://localhost:8081`, open console, run:
```javascript
dataAPI.getStatistics().then(d => console.log(d));
```

Expected: JSON object with statistics data (or null if API not running — that's ok, structure is what matters).

**Step 4: Commit**

```bash
git add vr/js/data-api.js vr/index.html
git commit -m "feat(vr): add DataAPI client with caching"
```

---

## Task 4: Build Room Manager Component

**Files:**
- Create: `vr/js/components/room-manager.js`

**Step 1: Write the room-manager component**

```javascript
/**
 * room-manager — Shows/hides room entities, manages transitions
 * Attach to <a-scene>. Each room is an <a-entity> with a `room` attribute.
 */
AFRAME.registerComponent('room-manager', {
  schema: {
    active: { type: 'string', default: 'hub' },
    fadeDuration: { type: 'number', default: 500 }
  },

  init: function () {
    this.rooms = {};
    this.transitioning = false;

    // Collect rooms after scene loads
    this.el.addEventListener('loaded', () => {
      this.el.querySelectorAll('[room]').forEach(el => {
        const name = el.getAttribute('room');
        this.rooms[name] = el;
        el.setAttribute('visible', name === this.data.active);
      });
      console.log('[room-manager] Rooms registered:', Object.keys(this.rooms));
    });

    // Listen for room-change events
    this.el.addEventListener('room-change', (evt) => {
      this.changeRoom(evt.detail.room);
    });
  },

  changeRoom: function (targetRoom) {
    if (this.transitioning) return;
    if (!this.rooms[targetRoom]) {
      console.warn(`[room-manager] Unknown room: ${targetRoom}`);
      return;
    }
    if (targetRoom === this.data.active) return;

    this.transitioning = true;
    const currentEl = this.rooms[this.data.active];
    const targetEl = this.rooms[targetRoom];

    // Fade out current room
    this._fadeOut(currentEl, () => {
      currentEl.setAttribute('visible', false);
      targetEl.setAttribute('visible', true);

      // Reset camera position to room spawn
      const rig = document.getElementById('rig');
      const spawn = targetEl.getAttribute('spawn') || '0 0 0';
      rig.setAttribute('position', spawn);

      // Fade in target room
      this._fadeIn(targetEl, () => {
        this.data.active = targetRoom;
        this.transitioning = false;
        this.el.emit('room-changed', { room: targetRoom });
        console.log(`[room-manager] Now in: ${targetRoom}`);
      });
    });
  },

  _fadeOut: function (el, callback) {
    // Simple visibility toggle for now; can add opacity animation later
    setTimeout(callback, this.data.fadeDuration);
  },

  _fadeIn: function (el, callback) {
    setTimeout(callback, this.data.fadeDuration);
  }
});
```

**Step 2: Add script to `index.html`**

Add before `app.js`:
```html
<script src="js/components/room-manager.js"></script>
```

**Step 3: Add `room-manager` to `<a-scene>` and room attributes to hub**

Update `<a-scene>`:
```html
<a-scene
  room-manager="active: hub"
  fog="type: exponential; color: #FFFFFF; density: 0.015"
  ...
>
```

Update hub entity:
```html
<a-entity id="hub" room="hub" spawn="0 0 0">
```

**Step 4: Verify in console**

Open browser, run in console:
```javascript
document.querySelector('a-scene').emit('room-change', { room: 'hub' });
```

Expected: Console log `[room-manager] Rooms registered: [hub]` on load.

**Step 5: Commit**

```bash
git add vr/js/components/room-manager.js vr/index.html
git commit -m "feat(vr): add room-manager component for scene transitions"
```

---

## Task 5: Build Portal Component

**Files:**
- Create: `vr/js/components/portal.js`

**Step 1: Write the portal component**

```javascript
/**
 * portal — Clickable gateway that triggers room transitions
 * Usage: <a-entity portal="target: landscape; label: Data Landscape; color: #4CC3D9"></a-entity>
 */
AFRAME.registerComponent('portal', {
  schema: {
    target: { type: 'string' },       // room name to transition to
    label: { type: 'string' },        // display text
    color: { type: 'color', default: '#4CC3D9' },
    width: { type: 'number', default: 1.5 },
    height: { type: 'number', default: 2.2 }
  },

  init: function () {
    const d = this.data;

    // Portal frame (rectangle outline)
    const frame = document.createElement('a-entity');
    frame.setAttribute('geometry', `primitive: box; width: ${d.width}; height: ${d.height}; depth: 0.05`);
    frame.setAttribute('material', `color: ${d.color}; opacity: 0.15; transparent: true`);
    frame.classList.add('clickable');
    this.el.appendChild(frame);

    // Inner glow plane
    const inner = document.createElement('a-entity');
    inner.setAttribute('geometry', `primitive: plane; width: ${d.width - 0.1}; height: ${d.height - 0.1}`);
    inner.setAttribute('material', `color: ${d.color}; opacity: 0.08; transparent: true; shader: flat; side: double`);
    inner.setAttribute('position', '0 0 0.03');
    this.el.appendChild(inner);

    // Border edges (4 thin boxes)
    const borderWidth = 0.03;
    const borders = [
      { pos: `0 ${d.height / 2} 0`, scale: `${d.width} ${borderWidth} ${borderWidth}` },
      { pos: `0 ${-d.height / 2} 0`, scale: `${d.width} ${borderWidth} ${borderWidth}` },
      { pos: `${-d.width / 2} 0 0`, scale: `${borderWidth} ${d.height} ${borderWidth}` },
      { pos: `${d.width / 2} 0 0`, scale: `${borderWidth} ${d.height} ${borderWidth}` },
    ];
    borders.forEach(b => {
      const edge = document.createElement('a-entity');
      edge.setAttribute('geometry', 'primitive: box; width: 1; height: 1; depth: 1');
      edge.setAttribute('scale', b.scale);
      edge.setAttribute('position', b.pos);
      edge.setAttribute('material', `color: ${d.color}; shader: flat; emissive: ${d.color}; emissiveIntensity: 0.5`);
      this.el.appendChild(edge);
    });

    // Label above portal
    const label = document.createElement('a-text');
    label.setAttribute('value', d.label);
    label.setAttribute('align', 'center');
    label.setAttribute('position', `0 ${d.height / 2 + 0.3} 0`);
    label.setAttribute('color', '#333');
    label.setAttribute('width', '3');
    label.setAttribute('font', 'monoid');
    this.el.appendChild(label);

    // Click handler
    frame.addEventListener('click', () => {
      console.log(`[portal] Clicked: ${d.target}`);
      this.el.sceneEl.emit('room-change', { room: d.target });
    });

    // Hover effect
    frame.addEventListener('mouseenter', () => {
      frame.setAttribute('material', 'opacity', 0.3);
    });
    frame.addEventListener('mouseleave', () => {
      frame.setAttribute('material', 'opacity', 0.15);
    });
  }
});
```

**Step 2: Add script to `index.html`**

```html
<script src="js/components/portal.js"></script>
```

**Step 3: Add portals to hub**

Inside the `#hub` entity in `index.html`, add four portals in a semicircle:

```html
<!-- Portals -->
<a-entity portal="target: landscape; label: Data Landscape; color: #4CC3D9"
          position="-3 1.1 -4.5" rotation="0 20 0"></a-entity>

<a-entity portal="target: globe; label: Facility Globe; color: #EF2D5E"
          position="3 1.1 -4.5" rotation="0 -20 0"></a-entity>

<a-entity portal="target: timeline; label: Timeline Walk; color: #FFC65D"
          position="0 1.1 -5" rotation="0 0 0"></a-entity>

<a-entity portal="target: footage; label: Raid Footage; color: #666666"
          position="0 1.1 -3" rotation="0 0 0"></a-entity>
```

**Step 4: Verify portals render**

Open browser. Verify: 4 colored rectangular portals with labels visible in white void. Click a portal — console logs `[portal] Clicked: <target>`.

**Step 5: Commit**

```bash
git add vr/js/components/portal.js vr/index.html
git commit -m "feat(vr): add portal component with click-to-transition"
```

---

## Task 6: Build Tooltip-3D Component

**Files:**
- Create: `vr/js/components/tooltip-3d.js`

**Step 1: Write the tooltip-3d component**

```javascript
/**
 * tooltip-3d — Billboard text card that faces user, shown on hover
 * Usage: <a-entity tooltip-3d="title: Deaths 2024; value: 32; source: ICE.gov; trust: contested"></a-entity>
 */
AFRAME.registerComponent('tooltip-3d', {
  schema: {
    title: { type: 'string', default: '' },
    value: { type: 'string', default: '' },
    source: { type: 'string', default: '' },
    trust: { type: 'string', default: 'verified' }, // verified | contested | govt | neutral
    visible: { type: 'boolean', default: false }
  },

  init: function () {
    this.card = document.createElement('a-entity');
    this.card.setAttribute('visible', this.data.visible);

    // Background panel
    const bg = document.createElement('a-plane');
    bg.setAttribute('width', 1.2);
    bg.setAttribute('height', 0.6);
    bg.setAttribute('color', '#FFFFFF');
    bg.setAttribute('opacity', 0.95);
    bg.setAttribute('side', 'double');
    this.card.appendChild(bg);

    // Border
    const border = document.createElement('a-plane');
    border.setAttribute('width', 1.22);
    border.setAttribute('height', 0.62);
    border.setAttribute('color', this._trustColor());
    border.setAttribute('position', '0 0 -0.001');
    border.setAttribute('side', 'double');
    this.card.appendChild(border);

    // Title
    const title = document.createElement('a-text');
    title.setAttribute('value', this.data.title);
    title.setAttribute('color', '#333');
    title.setAttribute('width', 2);
    title.setAttribute('position', '-0.5 0.15 0.01');
    title.setAttribute('font', 'monoid');
    this.card.appendChild(title);

    // Value
    const value = document.createElement('a-text');
    value.setAttribute('value', this.data.value);
    value.setAttribute('color', '#000');
    value.setAttribute('width', 3);
    value.setAttribute('position', '-0.5 -0.02 0.01');
    value.setAttribute('font', 'monoid');
    this.card.appendChild(value);

    // Source + trust
    const source = document.createElement('a-text');
    source.setAttribute('value', `${this.data.source} [${this.data.trust}]`);
    source.setAttribute('color', '#999');
    source.setAttribute('width', 1.5);
    source.setAttribute('position', '-0.5 -0.2 0.01');
    source.setAttribute('font', 'monoid');
    this.card.appendChild(source);

    // Billboard: face camera
    this.card.setAttribute('look-at', '#camera');

    this.card.setAttribute('position', '0 0.8 0');
    this.el.appendChild(this.card);
  },

  _trustColor: function () {
    const colors = {
      verified: '#2ECC71',
      contested: '#E67E22',
      govt: '#3498DB',
      neutral: '#95A5A6'
    };
    return colors[this.data.trust] || colors.neutral;
  },

  show: function () {
    this.card.setAttribute('visible', true);
  },

  hide: function () {
    this.card.setAttribute('visible', false);
  }
});
```

**Step 2: Add script to `index.html`**

```html
<script src="js/components/tooltip-3d.js"></script>
```

**Step 3: Test with a sample tooltip in hub**

Add to hub entity temporarily:
```html
<a-entity position="0 1.5 -3"
          tooltip-3d="title: Test Stat; value: 73,000; source: ICE.gov; trust: govt; visible: true">
</a-entity>
```

**Step 4: Verify tooltip renders and faces camera**

Open browser. Verify: white card with green/blue/orange border visible at center, text readable, card rotates to face camera as you move.

**Step 5: Remove test tooltip, commit**

```bash
git add vr/js/components/tooltip-3d.js vr/index.html
git commit -m "feat(vr): add tooltip-3d billboard component with trust colors"
```

---

## Task 7: Build Data Landscape Room

**Files:**
- Create: `vr/js/components/data-terrain.js`
- Create: `vr/js/components/data-bar.js`
- Create: `vr/js/landscape.js`
- Modify: `vr/index.html`

**Step 1: Write data-bar component**

```javascript
/**
 * data-bar — A single 3D bar rising from the ground
 * Usage: <a-entity data-bar="height: 2; color: #4CC3D9; label: 2020; value: 45000"></a-entity>
 */
AFRAME.registerComponent('data-bar', {
  schema: {
    height: { type: 'number', default: 1 },
    color: { type: 'color', default: '#4CC3D9' },
    width: { type: 'number', default: 0.3 },
    depth: { type: 'number', default: 0.3 },
    label: { type: 'string', default: '' },
    value: { type: 'string', default: '' },
    source: { type: 'string', default: '' },
    trust: { type: 'string', default: 'verified' }
  },

  init: function () {
    const d = this.data;

    // Bar geometry — positioned so bottom sits at y=0
    const bar = document.createElement('a-box');
    bar.setAttribute('width', d.width);
    bar.setAttribute('height', d.height);
    bar.setAttribute('depth', d.depth);
    bar.setAttribute('position', `0 ${d.height / 2} 0`);
    bar.setAttribute('color', d.color);
    bar.setAttribute('opacity', 0.85);
    bar.classList.add('clickable');
    this.el.appendChild(bar);
    this.bar = bar;

    // Tooltip (hidden by default)
    const tip = document.createElement('a-entity');
    tip.setAttribute('tooltip-3d', `title: ${d.label}; value: ${d.value}; source: ${d.source}; trust: ${d.trust}; visible: false`);
    tip.setAttribute('position', `0 ${d.height + 0.5} 0`);
    this.el.appendChild(tip);
    this.tip = tip;

    // Hover handlers
    bar.addEventListener('mouseenter', () => {
      bar.setAttribute('opacity', 1.0);
      tip.components['tooltip-3d'].show();
    });
    bar.addEventListener('mouseleave', () => {
      bar.setAttribute('opacity', 0.85);
      tip.components['tooltip-3d'].hide();
    });
  }
});
```

**Step 2: Write data-terrain component**

```javascript
/**
 * data-terrain — Generates a grid of data-bars from API data
 * Fetches time series data and creates a walkable terrain of bars.
 * Usage: <a-entity data-terrain></a-entity>
 */
AFRAME.registerComponent('data-terrain', {
  schema: {
    maxHeight: { type: 'number', default: 5 },   // max bar height in meters
    spacing: { type: 'number', default: 0.8 },    // space between bars
    barWidth: { type: 'number', default: 0.5 }
  },

  init: function () {
    this.loaded = false;
  },

  loadData: async function () {
    if (this.loaded) return;
    this.loaded = true;

    const api = window.dataAPI;
    if (!api) {
      console.error('[data-terrain] No dataAPI found');
      return;
    }

    // Define metrics: table, column, color, label
    const metrics = [
      { table: 'detention_population', col: 'total_detained', color: '#3498DB', label: 'Detention' },
      { table: 'deportations', col: 'total_removals', color: '#E74C3C', label: 'Deportations' },
      { table: 'arrests', col: 'total_arrests', color: '#E67E22', label: 'Arrests' },
      { table: 'deaths_in_custody', col: 'total_deaths', color: '#2C3E50', label: 'Deaths' },
      { table: 'agency_budgets', col: 'ice_budget_millions', color: '#F1C40F', label: 'Budget ($M)' }
    ];

    // Fetch all time series
    const allData = await Promise.all(
      metrics.map(m => api.getTimeSeries(m.table, m.col))
    );

    // Find global max per metric for normalization
    const maxVals = allData.map(series =>
      Math.max(...series.map(d => d.value || 0), 1)
    );

    // Generate bars
    metrics.forEach((metric, zIdx) => {
      const series = allData[zIdx];
      const maxVal = maxVals[zIdx];

      series.forEach((point, xIdx) => {
        const normalized = (point.value / maxVal) * this.data.maxHeight;
        if (normalized <= 0) return;

        const bar = document.createElement('a-entity');
        const x = xIdx * this.data.spacing - (series.length * this.data.spacing / 2);
        const z = zIdx * (this.data.spacing * 2) - (metrics.length * this.data.spacing);

        bar.setAttribute('position', `${x} 0 ${z}`);
        bar.setAttribute('data-bar',
          `height: ${normalized}; color: ${metric.color}; ` +
          `width: ${this.data.barWidth}; depth: ${this.data.barWidth}; ` +
          `label: ${metric.label} ${point.year}; ` +
          `value: ${point.value ? point.value.toLocaleString() : 'N/A'}; ` +
          `source: API; trust: verified`
        );
        this.el.appendChild(bar);
      });

      // Row label
      const rowLabel = document.createElement('a-text');
      const labelZ = zIdx * (this.data.spacing * 2) - (metrics.length * this.data.spacing);
      rowLabel.setAttribute('value', metric.label);
      rowLabel.setAttribute('position', `${-(series.length * this.data.spacing / 2) - 1.5} 0.5 ${labelZ}`);
      rowLabel.setAttribute('color', metric.color);
      rowLabel.setAttribute('width', '3');
      rowLabel.setAttribute('font', 'monoid');
      rowLabel.setAttribute('align', 'right');
      this.el.appendChild(rowLabel);
    });

    console.log('[data-terrain] Terrain generated');
  }
});
```

**Step 3: Write `landscape.js` — room setup**

```javascript
/**
 * Data Landscape room initialization
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  scene.addEventListener('room-changed', (evt) => {
    if (evt.detail.room === 'landscape') {
      const terrain = document.querySelector('#room-landscape [data-terrain]');
      if (terrain) {
        terrain.components['data-terrain'].loadData();
      }
    }
  });
});
```

**Step 4: Add room entity to `index.html`**

After the hub entity:

```html
<!-- Room: Data Landscape -->
<a-entity id="room-landscape" room="landscape" spawn="0 0 5" visible="false">
  <a-text
    value="DATA LANDSCAPE"
    position="0 4 -5"
    align="center"
    color="#333"
    width="6"
    font="monoid"
  ></a-text>
  <a-text
    value="Walk across 30 years of enforcement data"
    position="0 3.5 -5"
    align="center"
    color="#999"
    width="3"
    font="monoid"
  ></a-text>

  <!-- Data terrain -->
  <a-entity data-terrain position="0 0 0"></a-entity>

  <!-- Return portal -->
  <a-entity portal="target: hub; label: Return to Hub; color: #CCCCCC"
            position="0 1.1 8" rotation="0 180 0"></a-entity>
</a-entity>
```

**Step 5: Add scripts to `index.html`**

```html
<script src="js/components/data-bar.js"></script>
<script src="js/components/data-terrain.js"></script>
<script src="js/landscape.js"></script>
```

**Step 6: Verify landscape renders**

Open browser. Click "Data Landscape" portal. Verify: grid of colored bars appears, hovering shows tooltip, "Return to Hub" portal exists.

**Step 7: Commit**

```bash
git add vr/js/components/data-bar.js vr/js/components/data-terrain.js vr/js/landscape.js vr/index.html
git commit -m "feat(vr): add data landscape room with terrain bars and tooltips"
```

---

## Task 8: Build Facility Globe Room

**Files:**
- Create: `vr/js/components/globe-marker.js`
- Create: `vr/js/components/flow-arc.js`
- Create: `vr/js/globe.js`
- Modify: `vr/index.html`

**Step 1: Write globe-marker component**

```javascript
/**
 * globe-marker — Facility pin on inverted sphere
 * Usage: <a-entity globe-marker="lat: 33.44; lon: -112.07; name: Eloy; capacity: 1500; population: 1200; operator: CoreCivic; type: private"></a-entity>
 */
AFRAME.registerComponent('globe-marker', {
  schema: {
    lat: { type: 'number', default: 0 },
    lon: { type: 'number', default: 0 },
    name: { type: 'string', default: '' },
    capacity: { type: 'number', default: 0 },
    population: { type: 'number', default: 0 },
    operator: { type: 'string', default: '' },
    type: { type: 'string', default: 'government' }, // government | private | mixed
    radius: { type: 'number', default: 4 }  // globe radius
  },

  init: function () {
    const d = this.data;

    // Convert lat/lon to 3D position on inverted sphere
    const pos = this._latLonToVec3(d.lat, d.lon, d.radius);
    this.el.setAttribute('position', pos);

    // Pin color based on type
    const colors = { private: '#E74C3C', government: '#3498DB', mixed: '#9B59B6' };
    const color = colors[d.type] || colors.government;

    // Pin height based on capacity
    const pinHeight = Math.max(0.1, (d.capacity / 5000) * 0.5);

    // Cylinder pin
    const pin = document.createElement('a-cylinder');
    pin.setAttribute('radius', 0.03);
    pin.setAttribute('height', pinHeight);
    pin.setAttribute('color', color);
    pin.setAttribute('opacity', 0.9);
    pin.classList.add('clickable');
    this.el.appendChild(pin);

    // Pulse indicator (population %)
    const fillPct = d.capacity > 0 ? d.population / d.capacity : 0;
    const pulse = document.createElement('a-sphere');
    pulse.setAttribute('radius', 0.05 + fillPct * 0.05);
    pulse.setAttribute('color', color);
    pulse.setAttribute('opacity', 0.4 + fillPct * 0.4);
    pulse.setAttribute('position', `0 ${pinHeight / 2 + 0.05} 0`);
    this.el.appendChild(pulse);

    // Tooltip
    const tip = document.createElement('a-entity');
    tip.setAttribute('tooltip-3d',
      `title: ${d.name}; ` +
      `value: ${d.population.toLocaleString()} / ${d.capacity.toLocaleString()}; ` +
      `source: ${d.operator}; ` +
      `trust: ${d.type === 'private' ? 'contested' : 'govt'}; visible: false`
    );
    tip.setAttribute('position', `0 ${pinHeight + 0.8} 0`);
    this.el.appendChild(tip);
    this.tip = tip;

    pin.addEventListener('mouseenter', () => {
      if (this.tip.components['tooltip-3d']) this.tip.components['tooltip-3d'].show();
    });
    pin.addEventListener('mouseleave', () => {
      if (this.tip.components['tooltip-3d']) this.tip.components['tooltip-3d'].hide();
    });
  },

  _latLonToVec3: function (lat, lon, radius) {
    // Note: for inverted sphere, negate radius
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const y = radius * Math.cos(phi);
    const z = radius * Math.sin(phi) * Math.sin(theta);
    return `${x.toFixed(3)} ${y.toFixed(3)} ${z.toFixed(3)}`;
  }
});
```

**Step 2: Write flow-arc component**

```javascript
/**
 * flow-arc — Animated particle arc between two lat/lon points
 * Simplified version: draws a curved line between origin and destination.
 * Usage: <a-entity flow-arc="fromLat: 33; fromLon: -112; toLat: 19; toLon: -99; volume: 500; color: #E74C3C"></a-entity>
 */
AFRAME.registerComponent('flow-arc', {
  schema: {
    fromLat: { type: 'number', default: 0 },
    fromLon: { type: 'number', default: 0 },
    toLat: { type: 'number', default: 0 },
    toLon: { type: 'number', default: 0 },
    volume: { type: 'number', default: 100 },
    color: { type: 'color', default: '#E74C3C' },
    radius: { type: 'number', default: 4 }
  },

  init: function () {
    const d = this.data;
    const THREE = AFRAME.THREE;

    // Create arc using QuadraticBezierCurve3
    const from = this._latLonToVec3(d.fromLat, d.fromLon, d.radius);
    const to = this._latLonToVec3(d.toLat, d.toLon, d.radius);

    // Midpoint lifted above the sphere surface
    const mid = new THREE.Vector3().addVectors(from, to).multiplyScalar(0.5);
    const liftHeight = from.distanceTo(to) * 0.3;
    mid.normalize().multiplyScalar(d.radius + liftHeight);

    const curve = new THREE.QuadraticBezierCurve3(from, mid, to);
    const points = curve.getPoints(32);

    // Line geometry
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const opacity = Math.min(0.8, 0.2 + (d.volume / 5000));
    const material = new THREE.LineBasicMaterial({
      color: new THREE.Color(d.color),
      opacity: opacity,
      transparent: true
    });

    const line = new THREE.Line(geometry, material);
    this.el.setObject3D('arc', line);
  },

  _latLonToVec3: function (lat, lon, radius) {
    const THREE = AFRAME.THREE;
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    return new THREE.Vector3(
      -(radius * Math.sin(phi) * Math.cos(theta)),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  }
});
```

**Step 3: Write `globe.js` — room setup**

```javascript
/**
 * Facility Globe room — loads facility data and generates markers
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');
  let globeLoaded = false;

  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'globe' || globeLoaded) return;
    globeLoaded = true;

    const api = window.dataAPI;
    if (!api) return;

    const container = document.querySelector('#globe-markers');
    if (!container) return;

    // Fetch facilities
    const facilitiesData = await api.getFacilities();
    if (!facilitiesData || !facilitiesData.data) {
      console.error('[globe] No facility data');
      return;
    }

    facilitiesData.data.forEach(f => {
      if (!f.latitude || !f.longitude) return;

      const marker = document.createElement('a-entity');
      marker.setAttribute('globe-marker',
        `lat: ${f.latitude}; lon: ${f.longitude}; ` +
        `name: ${(f.facility_name || f.name || 'Unknown').replace(/;/g, ',')}; ` +
        `capacity: ${f.capacity || 0}; ` +
        `population: ${f.current_population || f.average_population || 0}; ` +
        `operator: ${(f.operator || 'Unknown').replace(/;/g, ',')}; ` +
        `type: ${f.facility_type || 'government'}`
      );
      container.appendChild(marker);
    });

    // Fetch deportation routes for flow arcs
    const deportData = await api.getDeportationsByNationality();
    if (deportData && deportData.data) {
      const arcContainer = document.querySelector('#globe-arcs');
      // Country centroids (simplified — top deportation destinations)
      const centroids = {
        'Mexico': { lat: 23.6, lon: -102.5 },
        'Guatemala': { lat: 15.5, lon: -90.2 },
        'Honduras': { lat: 14.1, lon: -87.2 },
        'El Salvador': { lat: 13.7, lon: -89.2 },
        'Colombia': { lat: 4.6, lon: -74.1 },
        'Ecuador': { lat: -1.8, lon: -78.2 },
        'Brazil': { lat: -14.2, lon: -51.9 },
        'Dominican Republic': { lat: 18.7, lon: -70.2 },
        'Haiti': { lat: 19.0, lon: -72.4 },
        'Jamaica': { lat: 18.1, lon: -77.3 },
        'India': { lat: 20.6, lon: 78.9 },
        'China': { lat: 35.9, lon: 104.2 }
      };

      // US centroid as origin
      const usLat = 38.9;
      const usLon = -77.0;

      deportData.data.forEach(d => {
        const country = d.nationality || d.country;
        const dest = centroids[country];
        if (!dest) return;

        const arc = document.createElement('a-entity');
        arc.setAttribute('flow-arc',
          `fromLat: ${usLat}; fromLon: ${usLon}; ` +
          `toLat: ${dest.lat}; toLon: ${dest.lon}; ` +
          `volume: ${d.total_deported || d.removals || 100}; ` +
          `color: #E74C3C`
        );
        arcContainer.appendChild(arc);
      });
    }

    console.log('[globe] Facility globe loaded');
  });
});
```

**Step 4: Add room entity to `index.html`**

```html
<!-- Room: Facility Globe -->
<a-entity id="room-globe" room="globe" spawn="0 0 0" visible="false">
  <a-text
    value="FACILITY GLOBE"
    position="0 5 0"
    align="center"
    color="#333"
    width="6"
    font="monoid"
  ></a-text>

  <!-- Inverted globe sphere -->
  <a-sphere
    radius="4.5"
    position="0 1.6 0"
    material="color: #F0F0F0; side: back; wireframe: true; opacity: 0.15"
  ></a-sphere>

  <!-- Landmass sphere (slightly smaller, opaque) -->
  <a-sphere
    radius="4.48"
    position="0 1.6 0"
    material="color: #FAFAFA; side: back; opacity: 0.05; transparent: true"
  ></a-sphere>

  <!-- Facility markers container -->
  <a-entity id="globe-markers" position="0 1.6 0"></a-entity>

  <!-- Flow arcs container -->
  <a-entity id="globe-arcs" position="0 1.6 0"></a-entity>

  <!-- Return portal -->
  <a-entity portal="target: hub; label: Return to Hub; color: #CCCCCC"
            position="0 1.1 5" rotation="0 180 0"></a-entity>
</a-entity>
```

**Step 5: Add scripts to `index.html`**

```html
<script src="js/components/globe-marker.js"></script>
<script src="js/components/flow-arc.js"></script>
<script src="js/globe.js"></script>
```

**Step 6: Verify globe renders**

Open browser. Click "Facility Globe" portal. Verify: wireframe sphere visible, facility pins appear at positions, flow arcs curve between US and destination countries.

**Step 7: Commit**

```bash
git add vr/js/components/globe-marker.js vr/js/components/flow-arc.js vr/js/globe.js vr/index.html
git commit -m "feat(vr): add facility globe room with markers and deportation arcs"
```

---

## Task 9: Build Timeline Walk Room

**Files:**
- Create: `vr/js/timeline.js`
- Modify: `vr/index.html`

**Step 1: Write `timeline.js` — corridor generation**

```javascript
/**
 * Timeline Walk room — generates a corridor of policy eras
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');
  let timelineLoaded = false;

  // Curated policy eras
  const ERAS = [
    { year: '1996', label: 'IIRIRA Signed', desc: 'Illegal Immigration Reform Act expands deportation grounds' },
    { year: '2001', label: 'Post-9/11', desc: 'Immigration enforcement merged into national security framework' },
    { year: '2003', label: 'ICE Created', desc: 'Immigration and Customs Enforcement established under DHS' },
    { year: '2008', label: 'Secure Communities', desc: 'Local police begin sharing fingerprints with ICE' },
    { year: '2014', label: 'Priority Enforcement', desc: 'Obama narrows enforcement priorities; family detention expands' },
    { year: '2017', label: 'Executive Orders', desc: 'Travel ban, border wall, expanded interior enforcement' },
    { year: '2018', label: 'Family Separation', desc: 'Zero Tolerance policy separates children from parents' },
    { year: '2020', label: 'Title 42', desc: 'COVID border expulsion policy bypasses asylum process' },
    { year: '2023', label: 'Post-Title 42', desc: 'Title 42 ends; new asylum restrictions implemented' },
    { year: '2025', label: 'Current Era', desc: 'Mass deportation operations expand; budget reaches $170B' }
  ];

  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'timeline' || timelineLoaded) return;
    timelineLoaded = true;

    const container = document.querySelector('#timeline-segments');
    if (!container) return;

    const api = window.dataAPI;
    const segmentLength = 3; // meters per era

    // Fetch data for stat overlays
    let detentionData = [];
    let deportationData = [];
    if (api) {
      const det = await api.getTimeSeries('detention_population', 'total_detained');
      const dep = await api.getTimeSeries('deportations', 'total_removals');
      detentionData = det || [];
      deportationData = dep || [];
    }

    ERAS.forEach((era, i) => {
      const z = -(i * segmentLength);
      const darkness = Math.min(0.7, i * 0.07);
      const floorColor = `hsl(0, 0%, ${100 - darkness * 100}%)`;

      // Floor segment
      const floor = document.createElement('a-plane');
      floor.setAttribute('position', `0 0.01 ${z}`);
      floor.setAttribute('rotation', '-90 0 0');
      floor.setAttribute('width', '4');
      floor.setAttribute('height', segmentLength.toString());
      floor.setAttribute('color', floorColor);
      container.appendChild(floor);

      // Left wall
      const leftWall = document.createElement('a-plane');
      leftWall.setAttribute('position', `-2 1.5 ${z}`);
      leftWall.setAttribute('rotation', '0 90 0');
      leftWall.setAttribute('width', segmentLength.toString());
      leftWall.setAttribute('height', '3');
      leftWall.setAttribute('color', '#FFFFFF');
      leftWall.setAttribute('opacity', '0.3');
      leftWall.setAttribute('transparent', 'true');
      container.appendChild(leftWall);

      // Right wall
      const rightWall = document.createElement('a-plane');
      rightWall.setAttribute('position', `2 1.5 ${z}`);
      rightWall.setAttribute('rotation', '0 -90 0');
      rightWall.setAttribute('width', segmentLength.toString());
      rightWall.setAttribute('height', '3');
      rightWall.setAttribute('color', '#FFFFFF');
      rightWall.setAttribute('opacity', '0.3');
      rightWall.setAttribute('transparent', 'true');
      container.appendChild(rightWall);

      // Divider (frosted glass)
      const divider = document.createElement('a-plane');
      divider.setAttribute('position', `0 1.5 ${z + segmentLength / 2}`);
      divider.setAttribute('width', '4');
      divider.setAttribute('height', '3');
      divider.setAttribute('color', '#DDDDDD');
      divider.setAttribute('opacity', '0.15');
      divider.setAttribute('transparent', 'true');
      container.appendChild(divider);

      // Year label on divider
      const yearLabel = document.createElement('a-text');
      yearLabel.setAttribute('value', era.year);
      yearLabel.setAttribute('position', `0 2.5 ${z + segmentLength / 2 + 0.01}`);
      yearLabel.setAttribute('align', 'center');
      yearLabel.setAttribute('color', '#333');
      yearLabel.setAttribute('width', '8');
      yearLabel.setAttribute('font', 'monoid');
      container.appendChild(yearLabel);

      // Era title (right wall)
      const title = document.createElement('a-text');
      title.setAttribute('value', era.label);
      title.setAttribute('position', `1.95 2.2 ${z}`);
      title.setAttribute('rotation', '0 -90 0');
      title.setAttribute('align', 'center');
      title.setAttribute('color', '#333');
      title.setAttribute('width', '3');
      title.setAttribute('font', 'monoid');
      container.appendChild(title);

      // Era description (right wall, below title)
      const desc = document.createElement('a-text');
      desc.setAttribute('value', era.desc);
      desc.setAttribute('position', `1.95 1.7 ${z}`);
      desc.setAttribute('rotation', '0 -90 0');
      desc.setAttribute('align', 'center');
      desc.setAttribute('color', '#666');
      desc.setAttribute('width', '2');
      desc.setAttribute('font', 'monoid');
      container.appendChild(desc);

      // Data bars on left wall (detention + deportation for nearest year)
      const eraYear = parseInt(era.year);
      const detPoint = detentionData.find(d => d.year === eraYear);
      const depPoint = deportationData.find(d => d.year === eraYear);

      if (detPoint) {
        const bar = document.createElement('a-entity');
        bar.setAttribute('position', `-1.8 0 ${z - 0.3}`);
        bar.setAttribute('rotation', '0 90 0');
        const h = Math.max(0.1, (detPoint.value / 80000) * 2);
        bar.setAttribute('data-bar',
          `height: ${h}; color: #3498DB; width: 0.2; depth: 0.2; ` +
          `label: Detained ${eraYear}; value: ${detPoint.value.toLocaleString()}; ` +
          `source: ICE; trust: govt`
        );
        container.appendChild(bar);
      }

      if (depPoint) {
        const bar = document.createElement('a-entity');
        bar.setAttribute('position', `-1.8 0 ${z + 0.3}`);
        bar.setAttribute('rotation', '0 90 0');
        const h = Math.max(0.1, (depPoint.value / 500000) * 2);
        bar.setAttribute('data-bar',
          `height: ${h}; color: #E74C3C; width: 0.2; depth: 0.2; ` +
          `label: Deported ${eraYear}; value: ${depPoint.value.toLocaleString()}; ` +
          `source: ICE; trust: govt`
        );
        container.appendChild(bar);
      }
    });

    console.log('[timeline] Corridor generated');
  });
});
```

**Step 2: Add room entity to `index.html`**

```html
<!-- Room: Timeline Walk -->
<a-entity id="room-timeline" room="timeline" spawn="0 0 2" visible="false">
  <a-text
    value="TIMELINE WALK"
    position="0 3 1"
    align="center"
    color="#333"
    width="6"
    font="monoid"
  ></a-text>
  <a-text
    value="Walk forward through 30 years of enforcement"
    position="0 2.5 1"
    align="center"
    color="#999"
    width="3"
    font="monoid"
  ></a-text>

  <a-entity id="timeline-segments"></a-entity>

  <!-- Return portal (at start of corridor) -->
  <a-entity portal="target: hub; label: Return to Hub; color: #CCCCCC"
            position="0 1.1 4" rotation="0 180 0"></a-entity>
</a-entity>
```

**Step 3: Add script to `index.html`**

```html
<script src="js/timeline.js"></script>
```

**Step 4: Verify timeline renders**

Open browser. Click "Timeline Walk" portal. Verify: corridor with floor segments darkening forward, divider walls with years, era titles on right wall, data bars on left wall.

**Step 5: Commit**

```bash
git add vr/js/timeline.js vr/index.html
git commit -m "feat(vr): add timeline walk corridor with policy eras and data bars"
```

---

## Task 10: Build Raid Footage Room

**Files:**
- Create: `vr/js/components/video-panel.js`
- Create: `vr/js/components/content-gate.js`
- Create: `vr/js/footage.js`
- Modify: `vr/index.html`

**Step 1: Write content-gate component**

```javascript
/**
 * content-gate — Content warning barrier requiring confirmation
 * Usage: <a-entity content-gate="message: This room contains sensitive footage.; room: footage"></a-entity>
 */
AFRAME.registerComponent('content-gate', {
  schema: {
    message: { type: 'string', default: 'Content warning: This room contains sensitive material.' },
    room: { type: 'string', default: '' }
  },

  init: function () {
    const d = this.data;

    // Semi-transparent barrier
    const barrier = document.createElement('a-plane');
    barrier.setAttribute('width', '3');
    barrier.setAttribute('height', '2.5');
    barrier.setAttribute('color', '#333');
    barrier.setAttribute('opacity', '0.85');
    barrier.setAttribute('side', 'double');
    this.el.appendChild(barrier);

    // Warning icon (triangle)
    const icon = document.createElement('a-triangle');
    icon.setAttribute('vertex-a', '0 0.3 0');
    icon.setAttribute('vertex-b', '-0.25 -0.15 0');
    icon.setAttribute('vertex-c', '0.25 -0.15 0');
    icon.setAttribute('color', '#F39C12');
    icon.setAttribute('position', '0 0.6 0.01');
    icon.setAttribute('material', 'shader: flat');
    this.el.appendChild(icon);

    // Warning text
    const text = document.createElement('a-text');
    text.setAttribute('value', d.message);
    text.setAttribute('align', 'center');
    text.setAttribute('color', '#FFFFFF');
    text.setAttribute('width', '2.5');
    text.setAttribute('position', '0 0.1 0.01');
    text.setAttribute('font', 'monoid');
    this.el.appendChild(text);

    // Subtext
    const sub = document.createElement('a-text');
    sub.setAttribute('value', 'Contains footage of immigration enforcement operations.\nAll identifiable faces have been blurred.\nYou may exit at any time.');
    sub.setAttribute('align', 'center');
    sub.setAttribute('color', '#AAA');
    sub.setAttribute('width', '2');
    sub.setAttribute('position', '0 -0.3 0.01');
    sub.setAttribute('font', 'monoid');
    this.el.appendChild(sub);

    // "I Understand" button
    const btn = document.createElement('a-plane');
    btn.setAttribute('width', '1.2');
    btn.setAttribute('height', '0.3');
    btn.setAttribute('color', '#555');
    btn.setAttribute('position', '0 -0.85 0.01');
    btn.classList.add('clickable');
    this.el.appendChild(btn);

    const btnText = document.createElement('a-text');
    btnText.setAttribute('value', 'I UNDERSTAND');
    btnText.setAttribute('align', 'center');
    btnText.setAttribute('color', '#FFF');
    btnText.setAttribute('width', '2');
    btnText.setAttribute('position', '0 -0.85 0.02');
    btnText.setAttribute('font', 'monoid');
    this.el.appendChild(btnText);

    // Hover effect
    btn.addEventListener('mouseenter', () => {
      btn.setAttribute('color', '#777');
    });
    btn.addEventListener('mouseleave', () => {
      btn.setAttribute('color', '#555');
    });

    // Click: dismiss gate
    btn.addEventListener('click', () => {
      this.el.setAttribute('visible', false);
      this.el.emit('gate-dismissed');
      console.log('[content-gate] User acknowledged content warning');
    });
  }
});
```

**Step 2: Write video-panel component**

```javascript
/**
 * video-panel — Floating video with gaze-to-play and data overlays
 * Usage: <a-entity video-panel="src: #video1; title: FOIA Release 2024; date: 2024-03-15; location: Houston, TX; statLabel: Arrests that month; statValue: 1,200"></a-entity>
 */
AFRAME.registerComponent('video-panel', {
  schema: {
    src: { type: 'string', default: '' },
    title: { type: 'string', default: '' },
    date: { type: 'string', default: '' },
    location: { type: 'string', default: '' },
    statLabel: { type: 'string', default: '' },
    statValue: { type: 'string', default: '' },
    source: { type: 'string', default: '' },
    trust: { type: 'string', default: 'neutral' },
    width: { type: 'number', default: 2 },
    height: { type: 'number', default: 1.125 } // 16:9 ratio
  },

  init: function () {
    const d = this.data;
    this.playing = false;

    // Video screen (placeholder — gray when no video)
    const screen = document.createElement('a-plane');
    screen.setAttribute('width', d.width);
    screen.setAttribute('height', d.height);
    screen.setAttribute('color', '#1a1a1a');
    screen.setAttribute('opacity', '0.9');
    if (d.src) {
      screen.setAttribute('material', `src: ${d.src}; shader: flat`);
    }
    screen.classList.add('clickable');
    this.el.appendChild(screen);
    this.screen = screen;

    // Thin border frame
    const frame = document.createElement('a-plane');
    frame.setAttribute('width', d.width + 0.04);
    frame.setAttribute('height', d.height + 0.04);
    frame.setAttribute('color', '#444');
    frame.setAttribute('position', '0 0 -0.005');
    this.el.appendChild(frame);
    this.frame = frame;

    // Title label above
    const title = document.createElement('a-text');
    title.setAttribute('value', d.title);
    title.setAttribute('align', 'center');
    title.setAttribute('color', '#CCC');
    title.setAttribute('width', '2.5');
    title.setAttribute('position', `0 ${d.height / 2 + 0.15} 0.01`);
    title.setAttribute('font', 'monoid');
    title.setAttribute('visible', 'false');
    this.el.appendChild(title);
    this.titleEl = title;

    // Date + location (above, right side)
    const dateLoc = document.createElement('a-text');
    dateLoc.setAttribute('value', `${d.date}  ${d.location}`);
    dateLoc.setAttribute('align', 'center');
    dateLoc.setAttribute('color', '#999');
    dateLoc.setAttribute('width', '1.8');
    dateLoc.setAttribute('position', `0 ${d.height / 2 + 0.35} 0.01`);
    dateLoc.setAttribute('font', 'monoid');
    dateLoc.setAttribute('visible', 'false');
    this.el.appendChild(dateLoc);
    this.dateLocEl = dateLoc;

    // Stat overlay (left side)
    if (d.statLabel) {
      const stat = document.createElement('a-entity');
      stat.setAttribute('tooltip-3d',
        `title: ${d.statLabel}; value: ${d.statValue}; source: ${d.source}; trust: ${d.trust}; visible: false`
      );
      stat.setAttribute('position', `${-(d.width / 2 + 0.8)} 0 0`);
      this.el.appendChild(stat);
      this.statEl = stat;
    }

    // Play icon (center of screen)
    const playIcon = document.createElement('a-triangle');
    playIcon.setAttribute('vertex-a', '0.15 0 0');
    playIcon.setAttribute('vertex-b', '-0.1 0.15 0');
    playIcon.setAttribute('vertex-c', '-0.1 -0.15 0');
    playIcon.setAttribute('color', '#FFF');
    playIcon.setAttribute('opacity', '0.7');
    playIcon.setAttribute('position', '0 0 0.01');
    playIcon.setAttribute('material', 'shader: flat');
    this.el.appendChild(playIcon);
    this.playIcon = playIcon;

    // Gaze/click handler
    screen.addEventListener('click', () => {
      this._togglePlay();
    });

    // Hover: show title
    screen.addEventListener('mouseenter', () => {
      this.titleEl.setAttribute('visible', true);
      this.dateLocEl.setAttribute('visible', true);
      this.frame.setAttribute('color', '#666');
    });
    screen.addEventListener('mouseleave', () => {
      if (!this.playing) {
        this.titleEl.setAttribute('visible', false);
        this.dateLocEl.setAttribute('visible', false);
      }
      this.frame.setAttribute('color', '#444');
    });
  },

  _togglePlay: function () {
    this.playing = !this.playing;

    if (this.playing) {
      // Show overlays
      this.titleEl.setAttribute('visible', true);
      this.dateLocEl.setAttribute('visible', true);
      this.playIcon.setAttribute('visible', false);
      if (this.statEl && this.statEl.components['tooltip-3d']) {
        this.statEl.components['tooltip-3d'].show();
      }
      // Emit event so other panels can pause
      this.el.sceneEl.emit('video-playing', { panel: this.el });
    } else {
      this.playIcon.setAttribute('visible', true);
      if (this.statEl && this.statEl.components['tooltip-3d']) {
        this.statEl.components['tooltip-3d'].hide();
      }
    }
  },

  pause: function () {
    this.playing = false;
    this.playIcon.setAttribute('visible', true);
    this.titleEl.setAttribute('visible', false);
    this.dateLocEl.setAttribute('visible', false);
    if (this.statEl && this.statEl.components['tooltip-3d']) {
      this.statEl.components['tooltip-3d'].hide();
    }
  }
});
```

**Step 3: Write `footage.js` — room setup**

```javascript
/**
 * Raid Footage room — sets up video panels and manages playback
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  // Only one video plays at a time
  scene.addEventListener('video-playing', (evt) => {
    const panels = document.querySelectorAll('#room-footage [video-panel]');
    panels.forEach(p => {
      if (p !== evt.detail.panel && p.components['video-panel']) {
        p.components['video-panel'].pause();
      }
    });
  });

  // Load footage room data when entered
  let footageLoaded = false;
  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'footage' || footageLoaded) return;
    footageLoaded = true;

    // Dim the panels that need data overlays
    const api = window.dataAPI;
    if (!api) return;

    // Fetch contradictions for overlay
    const contradictions = await api.getContradictions();
    if (contradictions && contradictions.data && contradictions.data.length > 0) {
      // Store for panels to reference
      window._footageContradictions = contradictions.data;
    }

    console.log('[footage] Room data loaded');
  });
});
```

**Step 4: Add room entity to `index.html`**

```html
<!-- Room: Raid Footage -->
<a-entity id="room-footage" room="footage" spawn="0 0 0" visible="false">
  <!-- Content warning gate -->
  <a-entity content-gate="room: footage" position="0 1.6 -2"></a-entity>

  <a-text
    value="RAID FOOTAGE"
    position="0 3.5 0"
    align="center"
    color="#555"
    width="5"
    font="monoid"
  ></a-text>

  <!-- Video panels in a ring (placeholders — no actual video files yet) -->
  <a-entity video-panel="title: FOIA Release — Houston Workplace Raid; date: 2024-03-15; location: Houston, TX; statLabel: Arrests that week; statValue: 280; source: ICE ERO; trust: govt"
            position="-2.5 1.8 -3" rotation="0 30 0"></a-entity>

  <a-entity video-panel="title: C-SPAN — Oversight Hearing Testimony; date: 2023-11-08; location: Washington, DC; statLabel: Deaths in custody (year); statValue: 28; source: DHS OIG; trust: contested"
            position="0 2.2 -4" rotation="0 0 0"></a-entity>

  <a-entity video-panel="title: Community Documentation — Residential Raid; date: 2024-07-22; location: Nashville, TN; statLabel: Local arrests; statValue: 45; source: ACLU; trust: verified"
            position="2.5 1.8 -3" rotation="0 -30 0"></a-entity>

  <a-entity video-panel="title: News Broadcast — Detention Facility Conditions; date: 2024-01-10; location: Adelanto, CA; statLabel: Facility capacity; statValue: 1,940; source: GEO Group; trust: contested"
            position="-3 1.5 -1" rotation="0 60 0"></a-entity>

  <a-entity video-panel="title: FOIA Release — Airport Transfer Operations; date: 2023-09-03; location: Alexandria, LA; statLabel: Transfers that month; statValue: 3,200; source: ICE Air; trust: govt"
            position="3 1.5 -1" rotation="0 -60 0"></a-entity>

  <a-entity video-panel="title: Congressional Record — Family Separation Testimony; date: 2024-05-14; location: Washington, DC; statLabel: Children separated (total); statValue: 5,500+; source: HHS OIG; trust: verified"
            position="0 2 -2" rotation="0 0 0"></a-entity>

  <!-- Exit portal (always visible, glowing white) -->
  <a-entity portal="target: hub; label: Exit; color: #FFFFFF"
            position="0 1.1 4" rotation="0 180 0"></a-entity>
</a-entity>
```

**Step 5: Add scripts to `index.html`**

```html
<script src="js/components/content-gate.js"></script>
<script src="js/components/video-panel.js"></script>
<script src="js/footage.js"></script>
```

**Step 6: Verify footage room renders**

Open browser. Click "Raid Footage" portal. Verify: content warning gate appears first, "I Understand" button dismisses it, 6 video panels visible in a ring (dark placeholders), play icon on each, hovering shows title/date, clicking shows data overlays, exit portal visible.

**Step 7: Commit**

```bash
git add vr/js/components/content-gate.js vr/js/components/video-panel.js vr/js/footage.js vr/index.html
git commit -m "feat(vr): add raid footage room with content gate, video panels, and data overlays"
```

---

## Task 11: Build Contradiction Component

**Files:**
- Create: `vr/js/components/contradiction.js`
- Modify: `vr/index.html`

**Step 1: Write contradiction component**

```javascript
/**
 * contradiction — Split display showing two conflicting data values
 * Usage: <a-entity contradiction="metric: Deaths in Custody; govtValue: 10; govtSource: ICE; indepValue: 21; indepSource: ACLU; severity: high"></a-entity>
 */
AFRAME.registerComponent('contradiction', {
  schema: {
    metric: { type: 'string', default: '' },
    govtValue: { type: 'string', default: '' },
    govtSource: { type: 'string', default: '' },
    indepValue: { type: 'string', default: '' },
    indepSource: { type: 'string', default: '' },
    severity: { type: 'string', default: 'medium' } // high | medium | low
  },

  init: function () {
    const d = this.data;
    const sevColors = { high: '#E74C3C', medium: '#E67E22', low: '#F1C40F' };
    const color = sevColors[d.severity] || sevColors.medium;

    // Dividing line
    const divider = document.createElement('a-plane');
    divider.setAttribute('width', '0.02');
    divider.setAttribute('height', '0.8');
    divider.setAttribute('color', color);
    divider.setAttribute('position', '0 0.4 0.01');
    divider.setAttribute('material', 'shader: flat');
    this.el.appendChild(divider);

    // Background
    const bg = document.createElement('a-plane');
    bg.setAttribute('width', '1.6');
    bg.setAttribute('height', '0.9');
    bg.setAttribute('color', '#FFFFFF');
    bg.setAttribute('opacity', '0.95');
    bg.setAttribute('position', '0 0.4 0');
    this.el.appendChild(bg);

    // Border
    const border = document.createElement('a-plane');
    border.setAttribute('width', '1.62');
    border.setAttribute('height', '0.92');
    border.setAttribute('color', color);
    border.setAttribute('position', '0 0.4 -0.001');
    this.el.appendChild(border);

    // Metric title
    const title = document.createElement('a-text');
    title.setAttribute('value', `CONTESTED: ${d.metric}`);
    title.setAttribute('color', color);
    title.setAttribute('width', '2');
    title.setAttribute('align', 'center');
    title.setAttribute('position', '0 0.75 0.02');
    title.setAttribute('font', 'monoid');
    this.el.appendChild(title);

    // Govt side (left)
    const govtLabel = document.createElement('a-text');
    govtLabel.setAttribute('value', `GOVT: ${d.govtValue}`);
    govtLabel.setAttribute('color', '#3498DB');
    govtLabel.setAttribute('width', '1.8');
    govtLabel.setAttribute('align', 'center');
    govtLabel.setAttribute('position', '-0.4 0.45 0.02');
    govtLabel.setAttribute('font', 'monoid');
    this.el.appendChild(govtLabel);

    const govtSrc = document.createElement('a-text');
    govtSrc.setAttribute('value', d.govtSource);
    govtSrc.setAttribute('color', '#999');
    govtSrc.setAttribute('width', '1.2');
    govtSrc.setAttribute('align', 'center');
    govtSrc.setAttribute('position', '-0.4 0.25 0.02');
    govtSrc.setAttribute('font', 'monoid');
    this.el.appendChild(govtSrc);

    // Independent side (right)
    const indepLabel = document.createElement('a-text');
    indepLabel.setAttribute('value', `INDEP: ${d.indepValue}`);
    indepLabel.setAttribute('color', '#2ECC71');
    indepLabel.setAttribute('width', '1.8');
    indepLabel.setAttribute('align', 'center');
    indepLabel.setAttribute('position', '0.4 0.45 0.02');
    indepLabel.setAttribute('font', 'monoid');
    this.el.appendChild(indepLabel);

    const indepSrc = document.createElement('a-text');
    indepSrc.setAttribute('value', d.indepSource);
    indepSrc.setAttribute('color', '#999');
    indepSrc.setAttribute('width', '1.2');
    indepSrc.setAttribute('align', 'center');
    indepSrc.setAttribute('position', '0.4 0.25 0.02');
    indepSrc.setAttribute('font', 'monoid');
    this.el.appendChild(indepSrc);

    // Billboard
    this.el.setAttribute('look-at', '#camera');
  }
});
```

**Step 2: Add script to `index.html`**

```html
<script src="js/components/contradiction.js"></script>
```

**Step 3: Commit**

```bash
git add vr/js/components/contradiction.js vr/index.html
git commit -m "feat(vr): add contradiction component for contested data display"
```

---

## Task 12: Add Vercel Route for VR Static Files

**Files:**
- Modify: `vercel.json`

**Step 1: Add VR static file route**

Add to the `builds` array:
```json
{
  "src": "vr/**",
  "use": "@vercel/static"
}
```

Add to the `routes` array (BEFORE the catch-all route):
```json
{
  "src": "/vr/(.*)",
  "dest": "/vr/$1"
}
```

Full updated `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    },
    {
      "src": "assets/**",
      "use": "@vercel/static"
    },
    {
      "src": "vr/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/assets/(.*)",
      "dest": "/assets/$1"
    },
    {
      "src": "/vr/(.*)",
      "dest": "/vr/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

**Step 2: Commit**

```bash
git add vercel.json
git commit -m "feat(deploy): add Vercel route for VR static files"
```

---

## Task 13: Blender MCP — Create Portal Frame Asset

**Files:**
- Create: `vr/assets/models/portal-frame.glb` (via Blender MCP)

**Step 1: Open Blender with MCP addon running on port 9876**

Ensure Blender is open and the MCP server addon is active.

**Step 2: Use Blender MCP to create portal frame**

Describe to Blender MCP:
> Create a rectangular archway frame. Outer dimensions: 1.5m wide, 2.2m tall, 0.05m deep. The frame border is 0.04m thick. Material: white (#FFFFFF) with slight emissive glow. Keep under 1200 triangles. Export as GLB.

**Step 3: Export to `vr/assets/models/portal-frame.glb`**

**Step 4: Update portal component to load model**

In `portal.js`, add an option to use the GLTF model instead of primitives when available:

At the top of `init`, add:
```javascript
// Try to load custom model, fall back to primitives
this.el.setAttribute('gltf-model', 'url(assets/models/portal-frame.glb)');
```

**Step 5: Commit**

```bash
git add vr/assets/models/portal-frame.glb vr/js/components/portal.js
git commit -m "feat(vr): add Blender portal frame model"
```

---

## Task 14: Blender MCP — Create Remaining Assets

**Files:**
- Create: `vr/assets/models/facility-pin.glb`
- Create: `vr/assets/models/divider-wall.glb`
- Create: `vr/assets/models/video-panel-frame.glb`
- Create: `vr/assets/models/content-warning-gate.glb`

**Step 1: Facility pin**

Describe to Blender MCP:
> Create a tapered column / pin. Base radius 0.03m, top radius 0.01m, height 0.3m. Small flat disc at top (radius 0.05m) for tooltip attachment. White material. Under 800 triangles. Export as GLB.

Export to `vr/assets/models/facility-pin.glb`

**Step 2: Divider wall**

Describe to Blender MCP:
> Create a flat rectangular panel, 4m wide, 3m tall, 0.02m thick. Material: frosted glass look — white, 15% opacity. A rectangular cutout or etched area near the top center (0.8m x 0.2m) for year text. Under 500 triangles. Export as GLB.

Export to `vr/assets/models/divider-wall.glb`

**Step 3: Video panel frame**

Describe to Blender MCP:
> Create a thin rectangular frame, 2.04m wide, 1.17m tall, border thickness 0.02m. Dark gray (#444). Small attachment nubs at top-center, left-center, and right-center for data card positioning. Under 800 triangles. Export as GLB.

Export to `vr/assets/models/video-panel-frame.glb`

**Step 4: Content warning gate**

Describe to Blender MCP:
> Create a semi-transparent barrier panel, 3m wide, 2.5m tall, 0.01m thick. Dark material (#333333). Small triangular warning icon shape extruded near the top center. Under 400 triangles. Export as GLB.

Export to `vr/assets/models/content-warning-gate.glb`

**Step 5: Commit all models**

```bash
git add vr/assets/models/
git commit -m "feat(vr): add Blender MCP 3D assets (pin, divider, video frame, gate)"
```

---

## Task 15: Integration Testing and Polish

**Step 1: Run full local test**

Start the Dash app and VR server:
```bash
python3 app.py &
cd vr && python3 -m http.server 8081
```

**Step 2: Desktop browser testing checklist**

- [ ] Hub loads with white void, 4 portals visible
- [ ] Click each portal → transitions to correct room
- [ ] Data Landscape: bars generate from API data, tooltips show on hover
- [ ] Facility Globe: markers appear at positions, flow arcs render
- [ ] Timeline Walk: corridor segments visible, era labels readable, data bars present
- [ ] Raid Footage: content gate blocks entry, dismisses on click, 6 panels visible, click shows overlays
- [ ] Return portals work from every room
- [ ] Console: no errors, all `[room-manager]`, `[data-terrain]`, etc. logs appear

**Step 3: Quest browser testing**

Connect Quest to same network. Open `http://<local-ip>:8081` in Quest Browser. Verify:
- [ ] VR mode enters correctly
- [ ] Laser pointer interactions work
- [ ] Text is readable at VR scale
- [ ] Portal transitions work
- [ ] Performance feels smooth (no dropped frames)

**Step 4: Fix any issues found**

Address any rendering, interaction, or performance issues.

**Step 5: Final commit**

```bash
git add -A
git commit -m "fix(vr): integration fixes from testing"
```

---

## Task 16: Add VR Link to Main Dash App

**Files:**
- Modify: `app.py` — add a nav link or button pointing to `/vr/`

**Step 1: Add a VR link in the nav**

Find the navigation section in `app.py` and add a link:

```python
dbc.NavItem(
    dbc.NavLink(
        "VR Experience",
        href="/vr/",
        target="_blank",
        className="nav-link",
        external_link=True
    )
)
```

**Step 2: Verify link appears in nav and opens VR page**

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add VR Experience link to main app navigation"
```

---

## Summary

| Task | Description | Est. Effort |
|------|-------------|-------------|
| 1 | Scaffold VR directory + A-Frame scene | Small |
| 2 | Expand REST API (7 tables + CORS) | Small |
| 3 | DataAPI client class | Small |
| 4 | Room manager component | Small |
| 5 | Portal component | Medium |
| 6 | Tooltip-3D component | Small |
| 7 | Data Landscape room | Large |
| 8 | Facility Globe room | Large |
| 9 | Timeline Walk room | Large |
| 10 | Raid Footage room | Large |
| 11 | Contradiction component | Small |
| 12 | Vercel deployment route | Small |
| 13 | Blender MCP: portal frame | Medium |
| 14 | Blender MCP: remaining assets | Medium |
| 15 | Integration testing | Medium |
| 16 | Nav link in main app | Small |

**Total: 16 tasks, ~15-20 commits**
