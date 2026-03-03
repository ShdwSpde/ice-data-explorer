/**
 * Raid Footage room — sets up video panels, manages playback,
 * and adds museum placards below each panel with context.
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  // Context data for the 6 video panels (matches order in index.html)
  const FOOTAGE_CONTEXT = [
    {
      body: 'FOIA-released body camera footage from a Houston workplace raid. Operations like this expanded under Operation Metro Surge. 12,000 new agents hired with training cut from 22 weeks to 8. Raids increased 40% year-over-year. 540,000 deportation target for 2025.',
      stat: '4,000+',
      statLabel: 'Arrests in Operation Metro Surge alone',
      source: 'ICE ERO / Brookings Institution',
      trust: 'govt'
    },
    {
      body: 'Congressional oversight hearing on detention deaths. In 2025, 32 people died in ICE custody — triple the previous year. 95% of deaths preventable per Physicians for Human Rights. At Fort Bliss, a medical examiner ruled one death a homicide by guards. ICE had called it suicide.',
      stat: '38+',
      statLabel: 'Deaths in ICE custody (2025-26)',
      source: 'DHS OIG / The Appeal / PBS',
      trust: 'contested'
    },
    {
      body: 'Community footage of a residential raid. Police in 18+ "sanctuary cities" documented illegally sharing data with ICE. In D.C., officers patrolled with DHS despite Sanctuary Values Act. In Providence, police set perimeters for ICE arrests. None were self-reported.',
      stat: '18+',
      statLabel: 'Sanctuary cities with police-ICE violations',
      source: 'The Appeal / ACLU',
      trust: 'verified'
    },
    {
      body: 'Investigation into GEO Group-operated Adelanto facility. GEO expects $1B+ in ICE contracts for 2025, projects $3B revenue for 2026. CoreCivic doubled ICE revenue to $245M/quarter. 71% of all ICE custody deaths occur in for-profit facilities. Their PACs donated $528K+ to Congress.',
      stat: '$3B',
      statLabel: 'GEO Group projected 2026 revenue',
      source: 'The Appeal / GEO Earnings Call',
      trust: 'contested'
    },
    {
      body: 'FOIA documentation of ICE Air transfer operations. Detainees flown across the country, separated from legal counsel. Victor Manuel Diaz was arrested in Minnesota and transferred to Fort Bliss tent city in Texas, where he died. GEO subsidiary monitors 42,000+ people via GPS ankle bracelets.',
      stat: '42,000+',
      statLabel: 'People on GPS ankle monitors',
      source: 'ICE Air / GEO Group BI Inc.',
      trust: 'govt'
    },
    {
      body: 'Congressional testimony on family separation. 5,500+ children taken. Now, the Dilley family detention center generates $180M annual revenue for CoreCivic. Fort Bliss — built on a base that held 100,000+ Japanese Americans in WWII — has 5,000-bed capacity with an 8,500-bed expansion planned.',
      stat: '5,500+',
      statLabel: 'Children separated from families',
      source: 'HHS OIG / The Appeal',
      trust: 'verified'
    }
  ];

  // Video panel positions from index.html (matching order)
  const PANEL_POSITIONS = [
    { pos: '-4.3 1.8 -2.5', rot: '0 60 0' },
    { pos: '-2.5 1.8 -4.3', rot: '0 30 0' },
    { pos: '2.5 1.8 -4.3', rot: '0 -30 0' },
    { pos: '4.3 1.8 -2.5', rot: '0 -60 0' },
    { pos: '4.3 1.8 2.5', rot: '0 -120 0' },
    { pos: '-4.3 1.8 2.5', rot: '0 120 0' }
  ];

  // Only one video plays at a time
  scene.addEventListener('video-playing', (evt) => {
    const panels = document.querySelectorAll('#room-footage [video-panel]');
    panels.forEach(p => {
      if (p !== evt.detail.panel && p.components['video-panel']) {
        p.components['video-panel'].pause();
      }
    });
  });

  let footageLoaded = false;
  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'footage' || footageLoaded) return;
    footageLoaded = true;

    const api = window.dataAPI;
    if (!api) return;

    const contradictions = await api.getContradictions();
    if (contradictions && contradictions.data && contradictions.data.length > 0) {
      window._footageContradictions = contradictions.data;
    }

    // Add museum placards below each video panel
    const footageRoom = document.querySelector('#room-footage');
    if (!footageRoom) return;

    FOOTAGE_CONTEXT.forEach((ctx, i) => {
      if (i >= PANEL_POSITIONS.length) return;

      const panelPos = PANEL_POSITIONS[i].pos.split(' ').map(Number);
      const panelRot = PANEL_POSITIONS[i].rot;

      // Offset placard below video panel (y - 1.2)
      const placardY = panelPos[1] - 1.4;

      const placard = document.createElement('a-entity');
      placard.setAttribute('position', `${panelPos[0]} ${placardY} ${panelPos[2]}`);
      placard.setAttribute('rotation', panelRot);

      // Escape semicolons
      const safeBody = ctx.body.replace(/;/g, ',');
      const safeSource = ctx.source.replace(/;/g, ',');

      placard.setAttribute('museum-placard',
        `heading: CONTEXT; ` +
        `body: ${safeBody}; ` +
        `stat: ${ctx.stat}; ` +
        `statLabel: ${ctx.statLabel}; ` +
        `source: ${safeSource}; ` +
        `trust: ${ctx.trust}; ` +
        `width: 1.8; height: 1.2; variant: standard`
      );
      footageRoom.appendChild(placard);
    });

    console.log('[footage] Room data loaded with placards');
  });
});
