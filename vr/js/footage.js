/**
 * Raid Footage room — sets up video panels, manages playback,
 * and adds museum placards below each panel with context.
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  // Context data for the 6 video panels (matches order in index.html)
  const FOOTAGE_CONTEXT = [
    {
      body: 'FOIA-released body camera footage from a workplace raid in Houston. ICE Enforcement and Removal Operations conducted the operation targeting undocumented workers. Raids like this increased 40% year-over-year.',
      stat: '280',
      statLabel: 'Arrests that week',
      source: 'ICE ERO FOIA Release',
      trust: 'govt'
    },
    {
      body: 'Congressional oversight hearing where DHS officials testified on detention conditions. Inspector General reports documented systemic medical neglect across facilities.',
      stat: '28',
      statLabel: 'Deaths in custody (that year)',
      source: 'DHS OIG / C-SPAN',
      trust: 'contested'
    },
    {
      body: 'Community-documented footage of a residential raid in Nashville. Bystanders recorded ICE agents entering a neighborhood. ACLU filed complaints about Fourth Amendment violations.',
      stat: '45',
      statLabel: 'Local arrests',
      source: 'ACLU Tennessee',
      trust: 'verified'
    },
    {
      body: 'News investigation into conditions at Adelanto ICE Processing Center operated by GEO Group. Reports of inadequate medical staffing and overcrowding beyond rated capacity.',
      stat: '1,940',
      statLabel: 'Facility rated capacity',
      source: 'GEO Group / DHS OIG',
      trust: 'contested'
    },
    {
      body: 'FOIA-released documentation of ICE Air transfer operations through Alexandria staging facility. Detainees are flown across the country, often separated from legal counsel.',
      stat: '3,200',
      statLabel: 'Transfers that month',
      source: 'ICE Air Operations',
      trust: 'govt'
    },
    {
      body: 'Congressional testimony on the impact of family separation policy. HHS OIG documented that the government had no system to track or reunite separated families.',
      stat: '5,500+',
      statLabel: 'Children separated (total)',
      source: 'HHS OIG / Congressional Record',
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
