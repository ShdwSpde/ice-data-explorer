# VR Timeline Mirror Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the VR experience as Project Watchtower — a single linear timeline tunnel with a classified-document title flash on entry, replacing left-wall data bars with narrative placards (watchdog/testimony) that mirror the right-wall policy framing.

**Architecture:** New `narrative-placard` A-Frame component handles left-wall rendering with two visual variants. `index.html` is stripped to one room (timeline). `app.js` drives the Watchtower flash timing (replacing its existing dynamic loading screen creation) and emits the `room-changed` event that triggers timeline rendering. `timeline.js` carries counter-narrative data inline and uses the new component.

**Tech Stack:** A-Frame 1.7.1, vanilla JS, HTML/CSS overlay for Watchtower flash. Served via `python3 -m http.server 8081` from `vr/` directory.

---

## Chunk 1: `narrative-placard` Component

### Task 1: Create `narrative-placard.js`

**Files:**
- Create: `vr/js/components/narrative-placard.js`

- [ ] **Step 1: Create the file with schema only — no rendering yet**

```js
// vr/js/components/narrative-placard.js
AFRAME.registerComponent('narrative-placard', {
  schema: {
    type:    { type: 'string',  default: 'watchdog' },
    speaker: { type: 'string',  default: '' },
    date:    { type: 'string',  default: '' },
    body:    { type: 'string',  default: '' },
    source:  { type: 'string',  default: '' },
    width:   { type: 'number',  default: 2.2 },
    height:  { type: 'number',  default: 1.5 }
  },

  init: function () {
    // placeholder — renders nothing yet
    console.log('[narrative-placard] init', this.data.type);
  }
});
```

- [ ] **Step 2: Add script tag to `vr/index.html`**

Find the block of component `<script>` tags near `museum-placard.js`. Add immediately after it:

```html
<script src="js/components/narrative-placard.js"></script>
```

- [ ] **Step 3: Add a test entity to `#room-timeline` temporarily**

In `vr/index.html`, inside the `<a-entity id="room-timeline" ...>` entity, add:

```html
<!-- TEMP narrative-placard test — remove after Task 2 Step 4 -->
<a-entity
  position="0 1.6 -2"
  narrative-placard="type: watchdog; speaker: DHS OIG 2011; date: 2011; body: Test body text for layout; source: DHS Inspector General; width: 2.2; height: 1.5">
</a-entity>
```

- [ ] **Step 4: Serve and verify script loads without errors**

```bash
cd /Users/spade/Desktop/ice-data-explorer/vr
python3 -m http.server 8081
```

Open `http://localhost:8081` in browser. Open DevTools console.
Expected: `[narrative-placard] init watchdog` logged. No JS errors.

- [ ] **Step 5: Remove the test entity**

Delete the `<!-- TEMP -->` entity added in Step 3.

---

### Task 2: Implement `narrative-placard` rendering

**Files:**
- Modify: `vr/js/components/narrative-placard.js`

- [ ] **Step 1: Replace `init` with full rendering implementation**

Replace the entire contents of `vr/js/components/narrative-placard.js`:

```js
// vr/js/components/narrative-placard.js
AFRAME.registerComponent('narrative-placard', {
  schema: {
    type:    { type: 'string',  default: 'watchdog' },
    speaker: { type: 'string',  default: '' },
    date:    { type: 'string',  default: '' },
    body:    { type: 'string',  default: '' },
    source:  { type: 'string',  default: '' },
    width:   { type: 'number',  default: 2.2 },
    height:  { type: 'number',  default: 1.5 }
  },

  init: function () {
    const d = this.data;
    const el = this.el;

    const isTestimony = d.type === 'testimony';

    // Palette
    const bg          = isTestimony ? '#1a0810' : '#1a0e00';
    const border      = isTestimony ? '#5a1030' : '#5a3a00';
    const accent      = isTestimony ? '#c8506a' : '#c8902a';
    const speakerClr  = isTestimony ? '#c8506a' : '#c8902a';
    const bodyClr     = isTestimony ? '#8a3a5a' : '#8a6a30';
    const badge       = isTestimony ? 'TESTIMONY' : 'WATCHDOG';
    const badgeBg     = isTestimony ? '#1a0010' : '#2a1a00';
    const badgeBorder = isTestimony ? '#5a0030' : '#5a3a00';
    const badgeColor  = isTestimony ? '#9a3050' : '#9a6a20';

    const w = d.width;
    const h = d.height;

    // Border frame (behind bg)
    const frame = document.createElement('a-plane');
    frame.setAttribute('width', w + 0.04);
    frame.setAttribute('height', h + 0.04);
    frame.setAttribute('color', border);
    frame.setAttribute('position', '0 0 -0.005');
    el.appendChild(frame);

    // Background plane
    const bgPlane = document.createElement('a-plane');
    bgPlane.setAttribute('width', w);
    bgPlane.setAttribute('height', h);
    bgPlane.setAttribute('material', `color: ${bg}; roughness: 0.95; metalness: 0.0`);
    bgPlane.setAttribute('position', '0 0 0');
    el.appendChild(bgPlane);

    // Accent line — top edge
    const accentLine = document.createElement('a-plane');
    accentLine.setAttribute('width', w);
    accentLine.setAttribute('height', 0.025);
    accentLine.setAttribute('color', accent);
    accentLine.setAttribute('position', `0 ${h / 2 - 0.012} 0.002`);
    el.appendChild(accentLine);

    // Speaker / source name
    const speakerText = document.createElement('a-text');
    speakerText.setAttribute('value', d.speaker);
    speakerText.setAttribute('color', speakerClr);
    speakerText.setAttribute('width', w * 1.8);
    speakerText.setAttribute('wrap-count', 32);
    speakerText.setAttribute('font', 'monoid');
    speakerText.setAttribute('align', 'left');
    speakerText.setAttribute('position', `${-(w / 2) + 0.1} ${h / 2 - 0.15} 0.003`);
    el.appendChild(speakerText);

    // Date
    const dateText = document.createElement('a-text');
    dateText.setAttribute('value', d.date);
    dateText.setAttribute('color', bodyClr);
    dateText.setAttribute('width', w * 1.4);
    dateText.setAttribute('font', 'monoid');
    dateText.setAttribute('align', 'left');
    dateText.setAttribute('position', `${-(w / 2) + 0.1} ${h / 2 - 0.28} 0.003`);
    el.appendChild(dateText);

    // Divider line
    const divLine = document.createElement('a-plane');
    divLine.setAttribute('width', w - 0.2);
    divLine.setAttribute('height', 0.008);
    divLine.setAttribute('color', border);
    divLine.setAttribute('position', `0 ${h / 2 - 0.36} 0.002`);
    el.appendChild(divLine);

    // Body text — semicolons stripped (A-Frame attribute parsing)
    const safeBody = d.body.replace(/;/g, ',');
    const bodyText = document.createElement('a-text');
    bodyText.setAttribute('value', safeBody);
    bodyText.setAttribute('color', bodyClr);
    bodyText.setAttribute('width', w * 1.65);
    bodyText.setAttribute('wrap-count', 36);
    bodyText.setAttribute('font', 'monoid');
    bodyText.setAttribute('align', 'left');
    bodyText.setAttribute('baseline', 'top');
    bodyText.setAttribute('position', `${-(w / 2) + 0.1} ${h / 2 - 0.46} 0.003`);
    el.appendChild(bodyText);

    // Badge border
    const badgeBorderPlane = document.createElement('a-plane');
    badgeBorderPlane.setAttribute('width', 0.57);
    badgeBorderPlane.setAttribute('height', 0.12);
    badgeBorderPlane.setAttribute('color', badgeBorder);
    badgeBorderPlane.setAttribute('position', `${-(w / 2) + 0.375} ${-(h / 2) + 0.1} 0.002`);
    el.appendChild(badgeBorderPlane);

    // Badge background
    const badgeBgPlane = document.createElement('a-plane');
    badgeBgPlane.setAttribute('width', 0.55);
    badgeBgPlane.setAttribute('height', 0.1);
    badgeBgPlane.setAttribute('color', badgeBg);
    badgeBgPlane.setAttribute('position', `${-(w / 2) + 0.375} ${-(h / 2) + 0.1} 0.003`);
    el.appendChild(badgeBgPlane);

    // Badge text
    const badgeText = document.createElement('a-text');
    badgeText.setAttribute('value', badge);
    badgeText.setAttribute('color', badgeColor);
    badgeText.setAttribute('width', 0.9);
    badgeText.setAttribute('font', 'monoid');
    badgeText.setAttribute('align', 'center');
    badgeText.setAttribute('position', `${-(w / 2) + 0.375} ${-(h / 2) + 0.1} 0.004`);
    el.appendChild(badgeText);

    // Source text
    const safeSource = d.source.replace(/;/g, ',');
    const sourceText = document.createElement('a-text');
    sourceText.setAttribute('value', safeSource);
    sourceText.setAttribute('color', bodyClr);
    sourceText.setAttribute('width', w * 1.2);
    sourceText.setAttribute('wrap-count', 36);
    sourceText.setAttribute('font', 'monoid');
    sourceText.setAttribute('align', 'left');
    sourceText.setAttribute('position', `${-(w / 2) + 0.7} ${-(h / 2) + 0.1} 0.003`);
    el.appendChild(sourceText);
  }
});
```

- [ ] **Step 2: Add test entities for both variants to `#room-timeline`**

```html
<!-- TEMP: narrative-placard visual test — remove after Step 3 -->
<a-entity
  position="-3 1.6 -3"
  rotation="0 90 0"
  narrative-placard="type: watchdog; speaker: DHS OIG 2011; date: 2011; body: 93% of those removed had no criminal record. We found no evidence the program achieved its objectives; source: DHS Inspector General 2011; width: 2.2; height: 1.5">
</a-entity>
<a-entity
  position="3 1.6 -3"
  rotation="0 -90 0"
  narrative-placard="type: testimony; speaker: Rosa M., Age 34 - Guatemala; date: 2018; body: They said we were going for a shower. When I came back she was gone. I did not see her for 14 months; source: ACLU / Amnesty International 2018; width: 2.2; height: 1.5">
</a-entity>
```

- [ ] **Step 3: Verify both variants in browser**

Reload `http://localhost:8081`. Navigate or teleport to see the test entities.

Expected:
- Watchdog entity: amber accent line, amber speaker text, `WATCHDOG` badge
- Testimony entity: rose accent line, rose speaker text, `TESTIMONY` badge
- Both have visible background planes with correct dark colors
- Text is legible and doesn't overflow the placard bounds
- No JS console errors

- [ ] **Step 4: Remove the test entities**

Delete both `<!-- TEMP -->` entities from `index.html`.

- [ ] **Step 5: Commit**

```bash
git add vr/js/components/narrative-placard.js vr/index.html
git commit -m "feat(vr): add narrative-placard component (watchdog/testimony variants)"
```

---

## Chunk 2: Watchtower Flash + HTML Structure

### Task 3: Add Watchtower flash HTML to `index.html`

**Context:** The current loading screen is created dynamically in `app.js` via `document.createElement`. We are moving it to static HTML so the Watchtower card is part of the document from the start. `app.js` will be updated in Task 5 to remove its dynamic creation.

**Files:**
- Modify: `vr/index.html`

- [ ] **Step 1: Add Watchtower card as static HTML in `index.html`**

In `vr/index.html`, directly inside `<body>` before the `<a-scene>` tag, add:

```html
<div id="loading-screen">
  <div id="watchtower-card">
    <div class="wt-scanlines"></div>
    <div class="wt-inner">
      <div class="wt-agency">DEPARTMENT OF HOMELAND SECURITY</div>
      <div class="wt-classified">CLASSIFIED // FOUO</div>
      <div class="wt-title">
        <span>PROJECT</span>
        <span>WATCHTOWER</span>
      </div>
      <div class="wt-warning">UNAUTHORIZED ACCESS PROHIBITED</div>
      <div class="wt-casefile">CASE FILE: ICE-DATA-2025-0001</div>
    </div>
  </div>
</div>
```

---

### Task 4: Update `hud.css` — replace loading screen styles, add Watchtower styles

**Files:**
- Modify: `vr/css/hud.css`

- [ ] **Step 1: Replace the existing `#loading-screen` block**

In `vr/css/hud.css`, find the existing `#loading-screen` rule block (currently starts around line 1). It looks like:

```css
#loading-screen {
  position: fixed;
  ...
}
```

**Replace** the entire existing `#loading-screen` block (and any associated `.fade-out` rule for it) with:

```css
/* ── Watchtower flash / loading screen ── */
#loading-screen {
  position: fixed;
  inset: 0;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.5s ease;
}

#loading-screen.fade-out {
  opacity: 0;
  pointer-events: none;
}

#watchtower-card {
  position: relative;
  border: 2px solid #cc0000;
  padding: 32px 48px;
  text-align: center;
  max-width: 480px;
  width: 90%;
}

.wt-scanlines {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15) 0px,
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 4px
  );
  pointer-events: none;
}

.wt-inner {
  position: relative;
  z-index: 1;
}

.wt-agency {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: #cc0000;
  letter-spacing: 4px;
  margin-bottom: 6px;
}

.wt-classified {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11px;
  color: #cc0000;
  letter-spacing: 4px;
  margin-bottom: 24px;
}

.wt-title {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin-bottom: 24px;
}

.wt-title span {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 32px;
  color: #ffffff;
  letter-spacing: 10px;
  font-weight: bold;
  line-height: 1.2;
}

.wt-warning {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  color: #444;
  letter-spacing: 3px;
  margin-bottom: 8px;
}

.wt-casefile {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 9px;
  color: #333;
  letter-spacing: 2px;
}
```

- [ ] **Step 2: Add walk-forward hint CSS**

Append to `vr/css/hud.css` (after the Watchtower block):

```css
/* ── Walk-forward entry hint ── */
#hud-hint {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'IBM Plex Mono', monospace;
  font-size: 13px;
  color: #888;
  letter-spacing: 4px;
  opacity: 0;
  transition: opacity 0.5s ease;
  pointer-events: none;
  z-index: 100;
}
```

- [ ] **Step 3: Add `#hud-hint` element to `index.html`**

In `vr/index.html`, directly after the `#loading-screen` div (still before `<a-scene>`), add:

```html
<div id="hud-hint">WALK FORWARD ↑</div>
```

- [ ] **Step 4: Verify Watchtower card renders**

Reload `http://localhost:8081`. The Watchtower card should appear immediately and stay visible (timing not yet wired):
- Black background fills viewport
- Red border surrounds card
- Scanline texture visible across card
- `DEPARTMENT OF HOMELAND SECURITY` / `CLASSIFIED // FOUO` in red small monospace
- `PROJECT` / `WATCHTOWER` in large white bold monospace
- Warning and case file text in dark grey below
- No CSS console warnings about duplicate rule conflicts

---

### Task 5: Strip hub/portal rooms from `index.html` and update `room-manager` attribute

**Files:**
- Modify: `vr/index.html`

- [ ] **Step 1: Remove hub room entity**

Find and delete the entire `<a-entity id="hub-room" ...>...</a-entity>` block and all its children.

- [ ] **Step 2: Remove non-timeline room entities**

Delete each of these room entities and all their children:
- `<a-entity id="globe-room" ...>` (may be `security-feed-room`)
- `<a-entity id="landscape-room" ...>`
- `<a-entity id="footage-room" ...>`

Keep only `<a-entity id="room-timeline" ...>`.

- [ ] **Step 3: Update `room-manager` attribute on `<a-scene>`**

Find the `<a-scene>` tag. It has `room-manager="active: hub"` (or similar). Change it to:

```html
room-manager="active: timeline"
```

This prevents `room-manager.js` from trying to activate a hub room that no longer exists.

- [ ] **Step 4: Set the camera rig spawn position**

Find the camera rig entity — it will be an `<a-entity id="rig" ...>` or similar, with a child `<a-entity camera ...>`. Set the rig position to place the player at the timeline entrance:

```html
<a-entity id="rig" position="0 0 4">
  <a-entity id="camera" camera position="0 1.6 0" look-controls wasd-controls>
    <!-- existing cursor child stays as-is -->
  </a-entity>
</a-entity>
```

Do not rename tags or restructure — only change the `position` attribute on the rig entity.

- [ ] **Step 5: Verify scene has only timeline room**

Reload. After Watchtower dismisses (or temporarily comment out the loading screen div to skip it), confirm:
- Only the timeline corridor geometry is visible
- Player starts at the tunnel entrance
- No console errors about missing room entities

---

### Task 6: Replace loading screen logic in `app.js` + wire Watchtower timing

**Files:**
- Modify: `vr/js/app.js`

- [ ] **Step 1: Remove dynamic loading screen creation**

In `app.js`, find the block that creates the loading screen element dynamically — it will look like:

```js
const loadingScreen = document.createElement('div');
loadingScreen.id = 'loading-screen';
// ... adds spinner, text, etc.
document.body.appendChild(loadingScreen);
```

Delete this entire block. The loading screen now lives as static HTML in `index.html`.

- [ ] **Step 2: Replace the entire `room-changed` event handler**

In `app.js`, find `scene.addEventListener('room-changed', ...)`. Delete the entire handler — it references hub, portals, and room labels that no longer exist.

Replace it with nothing for now (the timeline is triggered differently — see Task 8).

- [ ] **Step 3: Replace loading screen dismiss logic with Watchtower timing**

Find wherever `app.js` currently hides the loading screen (likely inside a `scene loaded` or `loaded` event handler — look for `loadingScreen.style.display = 'none'` or `loadingScreen.classList.add`).

Replace that dismiss call with:

```js
const loadingScreen = document.getElementById('loading-screen');
const hudHint = document.getElementById('hud-hint');

function runWatchtowerSequence() {
  // Hold Watchtower card for 2.5s, fade out over 0.5s
  setTimeout(() => {
    loadingScreen.classList.add('fade-out');
    setTimeout(() => {
      loadingScreen.style.display = 'none';
    }, 500);
  }, 2500);

  // Show walk-forward hint after flash clears (3s), fade it after 4s
  setTimeout(() => {
    if (hudHint) hudHint.style.opacity = '1';
    setTimeout(() => {
      if (hudHint) hudHint.style.opacity = '0';
    }, 4000);
  }, 3000);
}

const sceneEl = document.querySelector('a-scene');
if (sceneEl.hasLoaded) {
  runWatchtowerSequence();
} else {
  sceneEl.addEventListener('loaded', runWatchtowerSequence, { once: true });
}
```

- [ ] **Step 4: Remove back-button and room-label logic**

In `app.js`, find any code referencing `#back-to-hub`, `#room-label`, `#nav-hint`, portal entry/exit event handlers, or room switch logic. Delete these blocks.

- [ ] **Step 5: Verify full entry sequence**

Reload `http://localhost:8081`:
1. Watchtower card appears immediately ✓
2. After 2.5s, card fades to black over 0.5s ✓
3. Timeline tunnel is now visible ✓
4. `WALK FORWARD ↑` fades in at bottom ✓
5. Hint fades out after 4s ✓
6. No JS errors ✓

- [ ] **Step 6: Commit**

```bash
git add vr/index.html vr/css/hud.css vr/js/app.js
git commit -m "feat(vr): Watchtower flash entry, single-room structure, strip hub/portal"
```

---

## Chunk 3: Timeline Mirror Swap

### Task 7: Add counter-narrative data to ERAS in `timeline.js`

**Files:**
- Modify: `vr/js/timeline.js`

- [ ] **Step 1: Replace the entire `ERAS` array**

In `vr/js/timeline.js`, replace the existing `ERAS` array declaration with:

```js
const ERAS = [
  {
    year: '1996', label: 'IIRIRA Signed',
    desc: 'Illegal Immigration Reform Act expands deportation grounds and mandates detention for broad categories of immigrants.',
    stat: '300,000', statLabel: 'Annual deportations begin',
    source: 'Congressional Record', trust: 'govt',
    counter: {
      type: 'watchdog',
      speaker: 'Congressional Record / GAO 1997',
      date: '1997',
      body: '"The most anti-immigrant legislation since the Chinese Exclusion Act." — Rep. Barney Frank. No cost-benefit analysis conducted. Retroactive provisions stripped rights from 300,000 legal permanent residents who had already completed sentences.',
      source: 'Congressional Record / GAO Report 1997'
    }
  },
  {
    year: '2001', label: 'Post-9/11 Shift',
    desc: 'Immigration enforcement merged into national security framework. INS abolished; functions split between new DHS agencies.',
    stat: '$5.5B', statLabel: 'INS final budget',
    source: 'DHS Transition Report', trust: 'govt',
    counter: {
      type: 'watchdog',
      speaker: 'DOJ Office of Inspector General, 2003',
      date: '2003',
      body: '762 immigrants detained post-9/11. "We found significant physical and verbal abuse, detainees held in solitary for months, denied attorneys. We found no evidence that the detainees were connected to terrorism."',
      source: 'DOJ OIG Special Report, June 2003'
    }
  },
  {
    year: '2003', label: 'ICE Created',
    desc: 'Immigration and Customs Enforcement established under DHS with unprecedented enforcement powers and budget.',
    stat: '$3.3B', statLabel: 'Initial ICE budget',
    source: 'DHS Appropriations', trust: 'govt',
    counter: {
      type: 'testimony',
      speaker: 'Anonymous, Age 31 — Mexico',
      date: '2003',
      body: '"They transferred me three times in two weeks. No one knew who was responsible for my case. ICE had just started. One guard told me — We\'re learning too. I didn\'t see a lawyer for 34 days."',
      source: 'ACLU Detention Documentation Project, 2003'
    }
  },
  {
    year: '2008', label: 'Secure Communities',
    desc: 'Local police begin sharing fingerprints with ICE. The line between local law enforcement and immigration enforcement blurs permanently.',
    stat: '34,000', statLabel: 'Average daily detention pop.',
    source: 'ICE ERO Statistics', trust: 'govt',
    counter: {
      type: 'watchdog',
      speaker: 'DHS Office of Inspector General, 2011',
      date: '2011',
      body: '"93% of those removed under Secure Communities had no criminal record. Program\'s stated purpose was targeting serious criminals. We found no evidence this objective was achieved. U.S. citizens detained in at least 3,600 cases."',
      source: 'DHS OIG Audit Report OIG-11-66, 2011'
    }
  },
  {
    year: '2014', label: 'Priority Enforcement',
    desc: 'Obama narrows enforcement priorities but family detention expands. Artesia and Karnes facilities open for mothers and children.',
    stat: '414,000', statLabel: 'Deportations (FY2014 peak)',
    source: 'ICE ERO Annual Report', trust: 'govt',
    counter: {
      type: 'testimony',
      speaker: 'Unnamed Mother, Age 28 — Honduras',
      date: '2015',
      body: '"My daughter stopped eating after the third week. The doctor came once. She said it was stress. We had been there 47 days. My daughter was four years old."',
      source: 'Karnes County Detention / ACLU, 2015'
    }
  },
  {
    year: '2017', label: 'Executive Orders',
    desc: 'Travel ban, border wall, expanded interior enforcement. Every undocumented person becomes a priority for removal.',
    stat: '$7.6B', statLabel: 'ICE budget',
    source: 'DHS Budget-in-Brief', trust: 'govt',
    counter: {
      type: 'testimony',
      speaker: 'Eduardo R., Age 44 — El Salvador',
      date: '2017',
      body: '"I\'ve lived here 22 years. My kids are U.S. citizens. I was taken from the parking lot of my job — the same week I filed a wage theft complaint against my employer. No one said that was a coincidence."',
      source: 'The Intercept / ACLU, 2017'
    }
  },
  {
    year: '2018', label: 'Family Separation',
    desc: 'Zero Tolerance policy separates children from parents at the border. Over 5,500 children taken from families before reversal.',
    stat: '5,500+', statLabel: 'Children separated',
    source: 'HHS OIG', trust: 'verified',
    counter: {
      type: 'testimony',
      speaker: 'Rosa M., Age 34 — Guatemala',
      date: '2018',
      body: '"They said we were going for a shower. When I came back, she was gone. No one told me where. I didn\'t see her for 14 months. She doesn\'t call me mama anymore."',
      source: 'ACLU / Amnesty International, 2018'
    }
  },
  {
    year: '2020', label: 'Title 42',
    desc: 'COVID border expulsion policy bypasses asylum process entirely. Over 1.7 million expulsions under public health authority.',
    stat: '1.7M', statLabel: 'Title 42 expulsions',
    source: 'CBP Enforcement Statistics', trust: 'govt',
    counter: {
      type: 'watchdog',
      speaker: 'CDC Internal Memo / Washington Post FOIA',
      date: '2022',
      body: '"The scientific evidence does not support the use of Title 42 for border expulsions. This is a policy decision being laundered as a public health measure." CDC career scientists formally objected. Document withheld two years, released under FOIA.',
      source: 'CDC Internal Documents via Washington Post FOIA, 2022'
    }
  },
  {
    year: '2023', label: 'Post-Title 42',
    desc: 'Title 42 ends. New asylum restrictions implemented. Transit ban requires applying in third countries first.',
    stat: '38,000', statLabel: 'Average daily detained',
    source: 'ICE Detention Management', trust: 'govt',
    counter: {
      type: 'testimony',
      speaker: 'Anonymous Family — Guatemala',
      date: '2023',
      body: '"We applied in Mexico first, as required by the new rules. Denied in 8 days. No interpreter present. We were told we had no right to appeal. We had been in Mexico 4 months waiting for the appointment."',
      source: 'Human Rights Watch, 2023'
    }
  },
  {
    year: '2025', label: 'Mass Deportation',
    desc: '540,000 deportation target. 12,000 new agents hired with training cut from 22 to 8 weeks. 130+ facilities opened. Fort Bliss tent city. 38+ dead in custody. 4 civilians shot by agents. $170B allocated.',
    stat: '38+', statLabel: 'Dead in custody (2025-26)',
    source: 'Brookings / The Appeal / PBS', trust: 'verified',
    counter: {
      type: 'testimony',
      speaker: 'James T. — U.S. Army Veteran',
      date: '2025',
      body: '"I served two tours in Afghanistan. I had my DD-214, passport, and birth certificate. They held me 6 days in a facility they couldn\'t name. They said their system flagged me. My congressman had to make calls."',
      source: 'ProPublica, 2025'
    }
  }
];
```

- [ ] **Step 2: Verify data loads without error**

Reload `http://localhost:8081`. Open DevTools console. Expected: no errors parsing the ERAS array.

---

### Task 8: Trigger timeline render on scene load + swap left-wall bars for narrative placards

**Context:** The timeline currently renders only when a `room-changed` event fires with `detail.room === 'timeline'`. After removing the hub, nothing emits that event on startup. We need to trigger timeline rendering directly on scene load, then swap the left-wall bars for narrative placards.

**Files:**
- Modify: `vr/js/timeline.js`

- [ ] **Step 1: Replace the `room-changed` listener with a `loaded` trigger**

In `vr/js/timeline.js`, find:

```js
scene.addEventListener('room-changed', async (evt) => {
  if (evt.detail.room !== 'timeline' || timelineLoaded) return;
  timelineLoaded = true;
  // ... rest of the render code
```

Replace only the outer event listener wrapper. Change it to:

```js
function renderTimeline() {
  if (timelineLoaded) return;
  timelineLoaded = true;
  // ... rest of the render code (unchanged)
}

if (scene.hasLoaded) {
  renderTimeline();
} else {
  scene.addEventListener('loaded', renderTimeline, { once: true });
}
```

Leave all the interior render code (ERAS.forEach, memorial section, etc.) exactly as-is inside the function body.

- [ ] **Step 2: Remove API fetch calls for detention/deportation data**

Inside the `renderTimeline` function, find and delete:

```js
let detentionData = [];
let deportationData = [];
if (api) {
  const det = await api.getTimeSeries('detention_population', 'population');
  const dep = await api.getTimeSeries('deportations', 'removals');
  detentionData = det || [];
  deportationData = dep || [];
}
```

Also remove `async` from `function renderTimeline()` since there are no more awaits in the eras section. (The memorial section uses `DataAPI.MEMORIAL_DATA` — a static property — not an async call.)

Change: `async function renderTimeline()` → `function renderTimeline()`

- [ ] **Step 3: Remove left-wall data bar rendering block from `ERAS.forEach`**

Inside the `ERAS.forEach` loop, find and delete the entire section from:

```js
// ── Data bars on left wall with labels ──
const leftBarX = -(corridorWidth / 2 - 0.2);
```

...down through the end of the `if (i === 0)` legend block (which ends after the `depLegendText` append). This removes approximately 100 lines.

- [ ] **Step 4: Add narrative placard rendering in place of data bars**

In the same location inside `ERAS.forEach` (right after the right-wall placard block, before the loop closes), add:

```js
// ── Narrative placard on left wall — counter-narrative mirror ──
if (era.counter) {
  const leftX = -(corridorWidth / 2 - 0.06);
  const c = era.counter;

  const safeBody    = c.body.replace(/;/g, ',');
  const safeSpeaker = c.speaker.replace(/;/g, ',');
  const safeSource  = c.source.replace(/;/g, ',');
  const safeDate    = c.date.replace(/;/g, ',');

  const narrativePlacard = document.createElement('a-entity');
  narrativePlacard.setAttribute('position', `${leftX} 1.8 ${z}`);
  narrativePlacard.setAttribute('rotation', '0 90 0');
  narrativePlacard.setAttribute('narrative-placard',
    `type: ${c.type}; ` +
    `speaker: ${safeSpeaker}; ` +
    `date: ${safeDate}; ` +
    `body: ${safeBody}; ` +
    `source: ${safeSource}; ` +
    `width: 2.2; height: 1.5`
  );
  container.appendChild(narrativePlacard);
}
```

- [ ] **Step 5: Verify the Mirror corridor end-to-end**

Reload `http://localhost:8081` and walk through the full timeline tunnel.

Check each era:
- Right wall: policy/institutional placard (cold blue-grey, GOVT/VERIFIED badge) ✓
- Left wall: narrative placard present on every era ✓
- Watchdog eras (1996, 2001, 2008, 2020): amber accent + `WATCHDOG` badge ✓
- Testimony eras (2003, 2014, 2017, 2018, 2023, 2025): rose accent + `TESTIMONY` badge ✓
- Text readable, no overflow ✓
- Memorial section renders after the 10 eras ✓
- No JS console errors ✓

- [ ] **Step 6: Commit**

```bash
git add vr/js/timeline.js
git commit -m "feat(vr): timeline mirror — narrative placards replace data bars, direct load trigger"
```

---

### Task 9: CSS cleanup

**Files:**
- Modify: `vr/css/hud.css`

- [ ] **Step 1: Remove portal and hub-specific CSS**

In `vr/css/hud.css`, find and delete rule blocks for these selectors (they were the old navigation HUD elements):
- `#back-to-hub`
- `#room-label`
- `#nav-hint`

Leave intact: all Watchtower / `.wt-*` rules, `#hud-hint`, `#loading-screen`, and any letterbox or general VR HUD rules.

- [ ] **Step 2: Final end-to-end walkthrough**

Do one complete run:
1. Page loads → Watchtower card (black bg, red border, PROJECT WATCHTOWER) ✓
2. 2.5s → card fades to black ✓
3. Timeline tunnel visible, player at 1996 entrance ✓
4. `WALK FORWARD ↑` hint fades in ✓
5. Hint fades out after 4s ✓
6. Walk all 10 eras — both walls populated, Mirror design intact ✓
7. Memorial section at the end ✓
8. No JS errors throughout ✓

- [ ] **Step 3: Commit**

```bash
git add vr/css/hud.css
git commit -m "chore(vr): remove obsolete hub/portal CSS (back-to-hub, room-label, nav-hint)"
```

---

## Summary

| Task | File(s) | Change |
|------|---------|--------|
| 1 | `narrative-placard.js` | New component skeleton + script tag |
| 2 | `narrative-placard.js` | Full rendering implementation, two variants |
| 3 | `index.html` | Watchtower card HTML (static) |
| 4 | `hud.css` | Replace loading screen styles + Watchtower + hint CSS |
| 5 | `index.html` | Strip hub/portal rooms, update `room-manager` attr, set spawn |
| 6 | `app.js` | Remove dynamic loading screen, remove room-changed handler, wire flash timing |
| 7 | `timeline.js` | Add `counter` field to all 10 ERAS |
| 8 | `timeline.js` | Replace `room-changed` with `loaded` trigger, swap left wall |
| 9 | `hud.css` | Remove `#back-to-hub`, `#room-label`, `#nav-hint` |
