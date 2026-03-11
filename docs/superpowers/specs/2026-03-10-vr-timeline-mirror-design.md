# VR Timeline — Mirror Design Spec
**Date:** 2026-03-10
**Status:** Approved
**Scope:** Project Watchtower — Phase 1 (Timeline Walk only)

---

## Summary

Strip the VR experience to a single linear room. Users flash into a classified-document title card ("Project Watchtower"), then land directly in the timeline tunnel. No hub, no portals, no navigation choices. Just walk forward through 30 years of enforcement history.

The left and right walls mirror each other: the right speaks in institutional language (policy, budgets, official sources); the left speaks back in watchdog audits, OIG findings, and first-person testimony. Same events. Two worlds. The viewer walks the line between them and is never told which one is the propaganda.

---

## Experience Flow

```
[Load] → Project Watchtower flash (2–3s) → fade to black → fade in at tunnel entry (1996)
→ Walk forward through 10 eras → Memorial section → Featured cases → End
```

No back button. No room selector. No portal UI. HUD shows "WALK FORWARD ↑" on entry, fades after 4 seconds.

---

## Project Watchtower Flash

**Aesthetic:** DHS classified document. Black background, CRT scanline overlay.

**Elements:**
- `DEPARTMENT OF HOMELAND SECURITY` — 9px monospace, red `#cc0000`, letter-spacing 4px
- `CLASSIFIED // FOUO` — same treatment
- `PROJECT` / `WATCHTOWER` — 28px, white, letter-spacing 8px, bold
- `UNAUTHORIZED ACCESS PROHIBITED` — 8px, dark grey
- `CASE FILE: ICE-DATA-2025-0001` — 8px, darker grey
- Red border around the document block
- CRT scanlines via CSS repeating-gradient

**Timing:**
- Appears immediately on load (replaces current loading spinner)
- Holds 2.5 seconds
- Fades to black over 0.5s
- Scene fades in over 1s

**Implementation:** Replace the current loading screen HTML in `vr/index.html` with the Watchtower card. Existing fade-in logic in `app.js` can drive the timing.

---

## Structural Changes

### `vr/index.html`
- Remove: hub room entity (`#hub-room`)
- Remove: globe, landscape, footage room entities
- Remove: portal entities and back-button
- Keep: `#timeline-room` as the only active room
- Loading screen → Watchtower classified doc card
- Scene spawns at timeline corridor entrance (position `0 1.6 2`, looking toward -Z)

### `vr/js/app.js`
- Remove: hub/portal room management
- Remove: room selector UI
- Simplify: Watchtower flash timing → fade into timeline
- Keep: loading logic, letterbox fade, minimal HUD
- HUD: show "WALK FORWARD ↑" for 4s on entry, then hide

### `vr/js/timeline.js`
- Remove: `detentionData` / `deportationData` API calls (no longer needed)
- Remove: left-wall data bar rendering (lines 167–272 in current file)
- Remove: bar legend
- Add: `counter` field to each ERA object (see content below)
- Add: left-wall `narrative-placard` entity per era (mirrors right-wall placard logic)

---

## New Component: `narrative-placard.js`

**File:** `vr/js/components/narrative-placard.js`
**Registration:** `AFRAME.registerComponent('narrative-placard', ...)`
**Load:** add `<script>` tag to `index.html` before `timeline.js`

### Schema

```js
schema: {
  type:    { type: 'string', default: 'watchdog' }, // 'watchdog' | 'testimony'
  speaker: { type: 'string', default: '' },          // OIG report name or person
  date:    { type: 'string', default: '' },
  body:    { type: 'string', default: '' },
  source:  { type: 'string', default: '' },
  width:   { type: 'number', default: 2.2 },
  height:  { type: 'number', default: 1.5 }
}
```

### Visual Treatment

| Property | `watchdog` | `testimony` |
|---|---|---|
| Background | `#1a0e00` | `#1a0810` |
| Border | `#5a3a00` | `#5a1030` |
| Accent line (top) | `#c8902a` | `#c8506a` |
| Speaker color | `#c8902a` | `#c8506a` |
| Body style | normal | italic |
| Badge text | `WATCHDOG` | `TESTIMONY` |
| Badge bg | `#2a1a00` | `#1a0010` |
| Badge color | `#9a6a20` | `#9a3050` |

Rendered as A-Frame planes + text entities (same approach as `museum-placard`). Billboard not needed — fixed to left wall.

---

## Left Wall Content — All 10 Eras

| Year | Type | Speaker / Source | Body |
|------|------|-----------------|------|
| 1996 | watchdog | Congressional Record / GAO 1997 | "The most anti-immigrant legislation since the Chinese Exclusion Act." — Rep. Barney Frank. No cost-benefit analysis. Retroactive provisions stripped rights from 300,000 legal permanent residents who had already served sentences. |
| 2001 | watchdog | DOJ Office of Inspector General, 2003 | 762 immigrants detained post-9/11. "We found significant physical and verbal abuse, detainees held in solitary for months, denied attorneys. We found no evidence that the detainees were connected to terrorism." |
| 2003 | testimony | Anonymous, Age 31 — Mexico (ACLU, 2003) | "They transferred me three times in two weeks. No one knew who was responsible for my case. ICE had just started. One guard told me, 'We're learning too.' I didn't see a lawyer for 34 days." |
| 2008 | watchdog | DHS Office of Inspector General, 2011 | "93% of those removed under Secure Communities had no criminal record. Program's stated purpose was targeting serious criminals. We found no evidence this objective was achieved. U.S. citizens were detained in at least 3,600 cases." |
| 2014 | testimony | Unnamed Mother, Age 28 — Honduras (ACLU, 2015) | "My daughter stopped eating after the third week. The doctor came once. She said it was stress. We had been there 47 days. My daughter was four years old." |
| 2017 | testimony | Eduardo R., Age 44 — El Salvador (The Intercept, 2017) | "I've lived here 22 years. My kids are U.S. citizens. I was taken from the parking lot of my job — the same week I filed a wage theft complaint against my employer. No one said that was a coincidence." |
| 2018 | testimony | Rosa M., Age 34 — Guatemala (ACLU / Amnesty, 2018) | "They said we were going for a shower. When I came back, she was gone. No one told me where. I didn't see her for 14 months. She doesn't call me 'mama' anymore." |
| 2020 | watchdog | CDC Internal Memo / Washington Post FOIA, 2022 | "The scientific evidence does not support the use of Title 42 for border expulsions. This is a policy decision being laundered as a public health measure." CDC career scientists formally objected. Withheld two years; released under FOIA. |
| 2023 | testimony | Anonymous Family — Guatemala (Human Rights Watch, 2023) | "We applied in Mexico first, as required by the new rules. Denied in 8 days. No interpreter present. We were told we had no right to appeal. We had been in Mexico 4 months waiting for the appointment." |
| 2025 | testimony | James T. — U.S. Army Veteran (ProPublica, 2025) | "I served two tours in Afghanistan. I had my DD-214, passport, and birth certificate. They held me 6 days in a facility they couldn't name. They said their system flagged me. My congressman had to make calls." |

---

## What Stays Untouched

- Memorial section (individual death placards)
- Contradiction displays
- Renee Good, Alex Pretti, Fort Bliss, Private Prison profit sections
- Particle effects
- `museum-placard.js` component (right wall uses it unchanged)
- `room-atmosphere.js`, `room-lighting.js`
- REST API (still serves data; timeline just doesn't fetch it for left wall)

---

## Files Changed

| File | Change |
|------|--------|
| `vr/index.html` | Replace loading screen with Watchtower card; remove hub/portal/globe/landscape/footage rooms |
| `vr/js/app.js` | Simplify to Watchtower timing + single-room load; strip portal/hub logic |
| `vr/js/timeline.js` | Swap left-wall data bars → narrative-placard; add counter field to ERAS; remove API calls |
| `vr/js/components/narrative-placard.js` | **New file** — watchdog/testimony component |
| `vr/css/hud.css` | Strip portal/hub/room-selector styles; keep minimal tunnel HUD |

---

## Non-Goals (Phase 1)

- Globe, landscape, footage rooms — deferred, not deleted
- Audio narration — future phase
- Gaze-based interaction on placards — future phase
- Back navigation — not needed in linear tunnel
