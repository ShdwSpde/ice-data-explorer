/**
 * Timeline Walk room — generates a brutalist corridor of policy eras
 * with museum placards and a memorial section at the end.
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');
  let timelineLoaded = false;

  const ERAS = [
    {
      year: '1996', label: 'IIRIRA Signed',
      desc: 'Illegal Immigration Reform Act expands deportation grounds and mandates detention for broad categories of immigrants.',
      stat: '300,000', statLabel: 'Annual deportations begin',
      source: 'Congressional Record', trust: 'govt'
    },
    {
      year: '2001', label: 'Post-9/11 Shift',
      desc: 'Immigration enforcement merged into national security framework. INS abolished; functions split between new DHS agencies.',
      stat: '$5.5B', statLabel: 'INS final budget',
      source: 'DHS Transition Report', trust: 'govt'
    },
    {
      year: '2003', label: 'ICE Created',
      desc: 'Immigration and Customs Enforcement established under DHS with unprecedented enforcement powers and budget.',
      stat: '$3.3B', statLabel: 'Initial ICE budget',
      source: 'DHS Appropriations', trust: 'govt'
    },
    {
      year: '2008', label: 'Secure Communities',
      desc: 'Local police begin sharing fingerprints with ICE. The line between local law enforcement and immigration enforcement blurs permanently.',
      stat: '34,000', statLabel: 'Average daily detention pop.',
      source: 'ICE ERO Statistics', trust: 'govt'
    },
    {
      year: '2014', label: 'Priority Enforcement',
      desc: 'Obama narrows enforcement priorities but family detention expands. Artesia and Karnes facilities open for mothers and children.',
      stat: '414,000', statLabel: 'Deportations (FY2014 peak)',
      source: 'ICE ERO Annual Report', trust: 'govt'
    },
    {
      year: '2017', label: 'Executive Orders',
      desc: 'Travel ban, border wall, expanded interior enforcement. Every undocumented person becomes a priority for removal.',
      stat: '$7.6B', statLabel: 'ICE budget',
      source: 'DHS Budget-in-Brief', trust: 'govt'
    },
    {
      year: '2018', label: 'Family Separation',
      desc: 'Zero Tolerance policy separates children from parents at the border. Over 5,500 children taken from families before reversal.',
      stat: '5,500+', statLabel: 'Children separated',
      source: 'HHS OIG', trust: 'verified'
    },
    {
      year: '2020', label: 'Title 42',
      desc: 'COVID border expulsion policy bypasses asylum process entirely. Over 1.7 million expulsions under public health authority.',
      stat: '1.7M', statLabel: 'Title 42 expulsions',
      source: 'CBP Enforcement Statistics', trust: 'govt'
    },
    {
      year: '2023', label: 'Post-Title 42',
      desc: 'Title 42 ends. New asylum restrictions implemented. Transit ban requires applying in third countries first.',
      stat: '38,000', statLabel: 'Average daily detained',
      source: 'ICE Detention Management', trust: 'govt'
    },
    {
      year: '2025', label: 'Current Era',
      desc: 'Mass deportation operations expand dramatically. ICE budget reaches historic high. Military bases converted to detention.',
      stat: '$170B', statLabel: 'Proposed enforcement spending',
      source: 'CBO Analysis, News Reports', trust: 'contested'
    }
  ];

  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'timeline' || timelineLoaded) return;
    timelineLoaded = true;

    const container = document.querySelector('#timeline-segments');
    if (!container) return;

    const api = window.dataAPI;
    const segmentLength = 5;

    let detentionData = [];
    let deportationData = [];
    if (api) {
      const det = await api.getTimeSeries('detention_population', 'population');
      const dep = await api.getTimeSeries('deportations', 'removals');
      detentionData = det || [];
      deportationData = dep || [];
    }

    ERAS.forEach((era, i) => {
      const z = -(i * segmentLength);

      const corridorWidth = 6;

      // ── Floor segment — brutalist concrete ──
      const floor = document.createElement('a-plane');
      floor.setAttribute('position', `0 0.01 ${z}`);
      floor.setAttribute('rotation', '-90 0 0');
      floor.setAttribute('width', corridorWidth.toString());
      floor.setAttribute('height', segmentLength.toString());
      // Alternating concrete tones
      const floorColor = i % 2 === 0 ? '#2a2a2a' : '#333333';
      floor.setAttribute('color', floorColor);
      container.appendChild(floor);

      // ── Left wall — concrete dark ──
      const leftWall = document.createElement('a-plane');
      leftWall.setAttribute('position', `${-corridorWidth / 2} 1.5 ${z}`);
      leftWall.setAttribute('rotation', '0 90 0');
      leftWall.setAttribute('width', segmentLength.toString());
      leftWall.setAttribute('height', '3');
      leftWall.setAttribute('color', '#333333');
      leftWall.setAttribute('opacity', '0.7');
      leftWall.setAttribute('transparent', 'true');
      container.appendChild(leftWall);

      // ── Right wall — concrete dark ──
      const rightWall = document.createElement('a-plane');
      rightWall.setAttribute('position', `${corridorWidth / 2} 1.5 ${z}`);
      rightWall.setAttribute('rotation', '0 -90 0');
      rightWall.setAttribute('width', segmentLength.toString());
      rightWall.setAttribute('height', '3');
      rightWall.setAttribute('color', '#333333');
      rightWall.setAttribute('opacity', '0.7');
      rightWall.setAttribute('transparent', 'true');
      container.appendChild(rightWall);

      // ── Heavy divider slab ──
      const divider = document.createElement('a-plane');
      divider.setAttribute('position', `0 1.5 ${z + segmentLength / 2}`);
      divider.setAttribute('width', corridorWidth.toString());
      divider.setAttribute('height', '3');
      divider.setAttribute('color', '#1a1a1a');
      divider.setAttribute('opacity', '0.3');
      divider.setAttribute('transparent', 'true');
      container.appendChild(divider);

      // ── Year label on divider — oversized ──
      const yearLabel = document.createElement('a-text');
      yearLabel.setAttribute('value', era.year);
      yearLabel.setAttribute('position', `0 2.5 ${z + segmentLength / 2 + 0.01}`);
      yearLabel.setAttribute('align', 'center');
      yearLabel.setAttribute('color', '#ECF0F1');
      yearLabel.setAttribute('width', '10');
      yearLabel.setAttribute('font', 'monoid');
      container.appendChild(yearLabel);

      // ── Museum placard on right wall ──
      const rightX = corridorWidth / 2 - 0.06;
      const placard = document.createElement('a-entity');
      placard.setAttribute('position', `${rightX} 1.8 ${z}`);
      placard.setAttribute('rotation', '0 -90 0');

      // Escape semicolons in text for A-Frame attribute parsing
      const safeDesc = era.desc.replace(/;/g, ',');
      const safeSource = era.source.replace(/;/g, ',');

      placard.setAttribute('museum-placard',
        `heading: ${era.label}; ` +
        `subheading: ${era.year}; ` +
        `body: ${safeDesc}; ` +
        `stat: ${era.stat}; ` +
        `statLabel: ${era.statLabel}; ` +
        `source: ${safeSource}; ` +
        `trust: ${era.trust}; ` +
        `width: 2.2; height: 1.5; variant: standard`
      );
      container.appendChild(placard);

      // ── Data bars on left wall with labels ──
      const leftBarX = -(corridorWidth / 2 - 0.2);
      const eraYear = parseInt(era.year);
      const detPoint = detentionData.find(d => d.year === eraYear);
      const depPoint = deportationData.find(d => d.year === eraYear);

      if (detPoint) {
        const bar = document.createElement('a-entity');
        bar.setAttribute('position', `${leftBarX} 0 ${z - 0.5}`);
        bar.setAttribute('rotation', '0 90 0');
        const h = Math.max(0.1, (detPoint.value / 80000) * 2);
        bar.setAttribute('data-bar',
          `height: ${h}; color: #2C3E50; width: 0.3; depth: 0.3; ` +
          `label: Detained ${eraYear}; value: ${detPoint.value.toLocaleString()}; ` +
          `source: ICE; trust: govt`
        );
        container.appendChild(bar);

        // Value label on bar
        const detLabel = document.createElement('a-text');
        detLabel.setAttribute('value', (detPoint.value / 1000).toFixed(0) + 'K');
        detLabel.setAttribute('position', `${leftBarX} ${h + 0.15} ${z - 0.5}`);
        detLabel.setAttribute('rotation', '0 90 0');
        detLabel.setAttribute('color', '#2C3E50');
        detLabel.setAttribute('width', '1.8');
        detLabel.setAttribute('font', 'monoid');
        detLabel.setAttribute('align', 'center');
        container.appendChild(detLabel);
      }

      if (depPoint) {
        const bar = document.createElement('a-entity');
        bar.setAttribute('position', `${leftBarX} 0 ${z + 0.5}`);
        bar.setAttribute('rotation', '0 90 0');
        const h = Math.max(0.1, (depPoint.value / 500000) * 2);
        bar.setAttribute('data-bar',
          `height: ${h}; color: #E74C3C; width: 0.3; depth: 0.3; ` +
          `label: Deported ${eraYear}; value: ${depPoint.value.toLocaleString()}; ` +
          `source: ICE; trust: govt`
        );
        container.appendChild(bar);

        // Value label on bar
        const depLabel = document.createElement('a-text');
        depLabel.setAttribute('value', (depPoint.value / 1000).toFixed(0) + 'K');
        depLabel.setAttribute('position', `${leftBarX} ${h + 0.15} ${z + 0.5}`);
        depLabel.setAttribute('rotation', '0 90 0');
        depLabel.setAttribute('color', '#E74C3C');
        depLabel.setAttribute('width', '1.8');
        depLabel.setAttribute('font', 'monoid');
        depLabel.setAttribute('align', 'center');
        container.appendChild(depLabel);
      }

      // ── Legend on left wall (first era only) ──
      if (i === 0) {
        const legendX = leftBarX;
        const legendZ = z + segmentLength / 2 - 0.5;

        // Legend background
        const legendBg = document.createElement('a-plane');
        legendBg.setAttribute('position', `${legendX} 2.4 ${legendZ}`);
        legendBg.setAttribute('rotation', '0 90 0');
        legendBg.setAttribute('width', '2.2');
        legendBg.setAttribute('height', '0.6');
        legendBg.setAttribute('color', '#1a1a1a');
        container.appendChild(legendBg);

        // Detention legend swatch
        const detSwatch = document.createElement('a-plane');
        detSwatch.setAttribute('position', `${legendX} 2.5 ${legendZ + 0.2}`);
        detSwatch.setAttribute('rotation', '0 90 0');
        detSwatch.setAttribute('width', '0.15');
        detSwatch.setAttribute('height', '0.15');
        detSwatch.setAttribute('color', '#2C3E50');
        container.appendChild(detSwatch);

        const detLegendText = document.createElement('a-text');
        detLegendText.setAttribute('value', 'DETAINED');
        detLegendText.setAttribute('position', `${legendX} 2.5 ${legendZ - 0.05}`);
        detLegendText.setAttribute('rotation', '0 90 0');
        detLegendText.setAttribute('color', '#ECF0F1');
        detLegendText.setAttribute('width', '1.5');
        detLegendText.setAttribute('font', 'monoid');
        detLegendText.setAttribute('align', 'left');
        container.appendChild(detLegendText);

        // Deportation legend swatch
        const depSwatch = document.createElement('a-plane');
        depSwatch.setAttribute('position', `${legendX} 2.25 ${legendZ + 0.2}`);
        depSwatch.setAttribute('rotation', '0 90 0');
        depSwatch.setAttribute('width', '0.15');
        depSwatch.setAttribute('height', '0.15');
        depSwatch.setAttribute('color', '#E74C3C');
        container.appendChild(depSwatch);

        const depLegendText = document.createElement('a-text');
        depLegendText.setAttribute('value', 'DEPORTED');
        depLegendText.setAttribute('position', `${legendX} 2.25 ${legendZ - 0.05}`);
        depLegendText.setAttribute('rotation', '0 90 0');
        depLegendText.setAttribute('color', '#ECF0F1');
        depLegendText.setAttribute('width', '1.5');
        depLegendText.setAttribute('font', 'monoid');
        depLegendText.setAttribute('align', 'left');
        container.appendChild(depLegendText);
      }
    });

    // ══════════════════════════════════════════
    //  MEMORIAL SECTION — after last era
    // ══════════════════════════════════════════
    const memorialStartZ = -(ERAS.length * segmentLength) - 3;
    const corridorWidth = 6;
    const memorial = DataAPI.MEMORIAL_DATA;
    if (!memorial || memorial.length === 0) {
      console.warn('[timeline] No memorial data available');
    }

    // ── Transition: dark floor into memorial ──
    const transFloor = document.createElement('a-plane');
    transFloor.setAttribute('position', `0 0.01 ${memorialStartZ + 2}`);
    transFloor.setAttribute('rotation', '-90 0 0');
    transFloor.setAttribute('width', corridorWidth.toString());
    transFloor.setAttribute('height', '6');
    transFloor.setAttribute('color', '#1a1a1a');
    container.appendChild(transFloor);

    // ── Entrance slab placard ──
    const entrancePlacard = document.createElement('a-entity');
    entrancePlacard.setAttribute('position', `0 2 ${memorialStartZ}`);
    entrancePlacard.setAttribute('museum-placard',
      'heading: IN MEMORIAM; ' +
      'subheading: Lives Lost in U.S. Immigration Detention; ' +
      'stat: 14+; ' +
      'statLabel: Documented deaths (partial count); ' +
      'body: Average age 44. Average detention 80 days. 95% of deaths linked to inadequate medical care or neglect. These are not statistics — they are people.; ' +
      'source: ACLU / Human Rights Watch / ICE FOIA; ' +
      'trust: verified; ' +
      'width: 3.5; height: 2; variant: memorial'
    );
    container.appendChild(entrancePlacard);

    // ── Contradiction display ──
    const contraZ = memorialStartZ - 2;
    const contraEntity = document.createElement('a-entity');
    contraEntity.setAttribute('position', `0 1.8 ${contraZ}`);
    contraEntity.setAttribute('contradiction',
      'metric: Deaths in ICE Custody (Annual); ' +
      'govtValue: ~10 per year; govtSource: ICE ERO Statistics; ' +
      'indepValue: 30-40 per year; indepSource: ACLU / Guardian / HRW; ' +
      'severity: high'
    );
    container.appendChild(contraEntity);

    // ── Individual memorial placards along both walls ──
    if (memorial && memorial.length > 0) {
      const memStartZ = contraZ - 3;
      const spacing = 2.2;

      memorial.forEach((person, i) => {
        const z = memStartZ - (i * spacing);
        const isLeft = i % 2 === 0;
        const x = isLeft ? -(corridorWidth / 2 - 0.06) : (corridorWidth / 2 - 0.06);
        const rotY = isLeft ? 90 : -90;

        // Dark floor segment for each pair
        if (i % 2 === 0) {
          const segFloor = document.createElement('a-plane');
          segFloor.setAttribute('position', `0 0.01 ${z}`);
          segFloor.setAttribute('rotation', '-90 0 0');
          segFloor.setAttribute('width', corridorWidth.toString());
          segFloor.setAttribute('height', spacing.toString());
          segFloor.setAttribute('color', '#111111');
          container.appendChild(segFloor);

          // Dark walls
          const lw = document.createElement('a-plane');
          lw.setAttribute('position', `${-corridorWidth / 2} 1.5 ${z}`);
          lw.setAttribute('rotation', '0 90 0');
          lw.setAttribute('width', spacing.toString());
          lw.setAttribute('height', '3');
          lw.setAttribute('color', '#1a1a1a');
          lw.setAttribute('opacity', '0.8');
          lw.setAttribute('transparent', 'true');
          container.appendChild(lw);

          const rw = document.createElement('a-plane');
          rw.setAttribute('position', `${corridorWidth / 2} 1.5 ${z}`);
          rw.setAttribute('rotation', '0 -90 0');
          rw.setAttribute('width', spacing.toString());
          rw.setAttribute('height', '3');
          rw.setAttribute('color', '#1a1a1a');
          rw.setAttribute('opacity', '0.8');
          rw.setAttribute('transparent', 'true');
          container.appendChild(rw);
        }

        // Truncate story for VR readability
        const shortStory = person.story.length > 160
          ? person.story.substring(0, 157) + '...'
          : person.story;

        const placard = document.createElement('a-entity');
        placard.setAttribute('position', `${x} 1.6 ${z}`);
        placard.setAttribute('rotation', `0 ${rotY} 0`);

        // Escape semicolons
        const safeName = person.name.replace(/;/g, ',');
        const safeFacility = person.facility.replace(/;/g, ',');
        const safeCause = person.cause.replace(/;/g, ',');
        const safeStory = shortStory.replace(/;/g, ',');
        const safeSource = person.source.replace(/;/g, ',');

        const daysStr = typeof person.detained_days === 'number'
          ? person.detained_days + ' days'
          : person.detained_days;

        placard.setAttribute('museum-placard',
          `heading: ${safeName}; ` +
          `subheading: Age ${person.age} | ${person.origin} | ${person.date}; ` +
          `stat: ${daysStr}; ` +
          `statLabel: detained before death; ` +
          `body: ${safeFacility}. Cause: ${safeCause}. ${safeStory}; ` +
          `source: ${safeSource}; ` +
          `trust: verified; ` +
          `width: 2.2; height: 1.8; variant: memorial`
        );
        container.appendChild(placard);
      });

      // ── Particle effect in memorial section ──
      const particleZ = memStartZ - (memorial.length * spacing / 2);
      const particles = document.createElement('a-entity');
      particles.setAttribute('position', `0 3 ${particleZ}`);
      particles.setAttribute('particle-system',
        'preset: dust; ' +
        'color: #ECF0F1,#95A5A6; ' +
        'particleCount: 200; ' +
        'size: 0.05; ' +
        'maxAge: 8; ' +
        'velocityValue: 0 -0.1 0; ' +
        'accelerationSpread: 0.5 0.1 0.5; ' +
        'opacity: 0.3'
      );
      container.appendChild(particles);

      // ══════════════════════════════════════════════════
      //  FEATURED: OPERATION METRO SURGE — Jan 2026
      //  Renee Nicole Good & Alex Pretti
      // ══════════════════════════════════════════════════
      const featuredStartZ = memStartZ - (memorial.length * spacing) - 4;

      // ── Operation Metro Surge header ──
      const surgeFloor = document.createElement('a-plane');
      surgeFloor.setAttribute('position', `0 0.01 ${featuredStartZ + 1}`);
      surgeFloor.setAttribute('rotation', '-90 0 0');
      surgeFloor.setAttribute('width', corridorWidth.toString());
      surgeFloor.setAttribute('height', '8');
      surgeFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(surgeFloor);

      // Red accent line across floor
      const redLine = document.createElement('a-plane');
      redLine.setAttribute('position', `0 0.02 ${featuredStartZ + 2}`);
      redLine.setAttribute('rotation', '-90 0 0');
      redLine.setAttribute('width', corridorWidth.toString());
      redLine.setAttribute('height', '0.08');
      redLine.setAttribute('color', '#B22234');
      container.appendChild(redLine);

      // Surge header placard — center wall
      const surgeHeader = document.createElement('a-entity');
      surgeHeader.setAttribute('position', `0 2.2 ${featuredStartZ}`);
      surgeHeader.setAttribute('museum-placard',
        'heading: OPERATION METRO SURGE; ' +
        'subheading: Minneapolis-St. Paul / January 2026; ' +
        'stat: 4,000+; ' +
        'statLabel: Arrests in 7 weeks; ' +
        'body: The largest DHS enforcement operation in U.S. history. 3,000 federal agents deployed to Minnesota. 2 civilians killed by federal officers. 19 firing incidents nationwide during immigration operations. Cost to Minneapolis: $200M+.; ' +
        'source: DHS / Minnesota Reformer / Marshall Project; ' +
        'trust: contested; ' +
        'width: 4; height: 2.2; variant: memorial'
      );
      container.appendChild(surgeHeader);

      // ── RENEE NICOLE GOOD — Left wall, large featured ──
      const reneeZ = featuredStartZ - 4;

      // Dark alcove for Renee
      const reneeFloor = document.createElement('a-plane');
      reneeFloor.setAttribute('position', `0 0.01 ${reneeZ}`);
      reneeFloor.setAttribute('rotation', '-90 0 0');
      reneeFloor.setAttribute('width', corridorWidth.toString());
      reneeFloor.setAttribute('height', '5');
      reneeFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(reneeFloor);

      // Left wall
      const reneeLW = document.createElement('a-plane');
      reneeLW.setAttribute('position', `${-corridorWidth / 2} 1.5 ${reneeZ}`);
      reneeLW.setAttribute('rotation', '0 90 0');
      reneeLW.setAttribute('width', '5');
      reneeLW.setAttribute('height', '3');
      reneeLW.setAttribute('color', '#0a0a0a');
      container.appendChild(reneeLW);

      // Right wall
      const reneeRW = document.createElement('a-plane');
      reneeRW.setAttribute('position', `${corridorWidth / 2} 1.5 ${reneeZ}`);
      reneeRW.setAttribute('rotation', '0 -90 0');
      reneeRW.setAttribute('width', '5');
      reneeRW.setAttribute('height', '3');
      reneeRW.setAttribute('color', '#0a0a0a');
      container.appendChild(reneeRW);

      // Main placard — left wall
      const reneePlacard = document.createElement('a-entity');
      reneePlacard.setAttribute('position', `${-(corridorWidth / 2 - 0.06)} 1.8 ${reneeZ}`);
      reneePlacard.setAttribute('rotation', '0 90 0');
      reneePlacard.setAttribute('museum-placard',
        'heading: RENEE NICOLE GOOD; ' +
        'subheading: Age 37 | American Citizen | January 7, 2026; ' +
        'stat: 3 CHILDREN; ' +
        'statLabel: Left without their mother; ' +
        'body: Mother of three, poet, singer. Shot by ICE agent Jonathan Ross during Operation Metro Surge in Minneapolis. Good had just dropped her 6-year-old son at school when she encountered federal agents. Ross fired 3 shots as her car moved past him. DHS claimed self-defense, video evidence contradicted the account. Her death sparked nationwide protests.; ' +
        'source: CNN / NBC News / ABC News; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.2; variant: memorial'
      );
      container.appendChild(reneePlacard);

      // Data breakdown — right wall
      const reneeData = document.createElement('a-entity');
      reneeData.setAttribute('position', `${corridorWidth / 2 - 0.06} 1.8 ${reneeZ}`);
      reneeData.setAttribute('rotation', '0 -90 0');
      reneeData.setAttribute('museum-placard',
        'heading: THE OPERATION THAT KILLED HER; ' +
        'subheading: Operation Metro Surge — By the Numbers; ' +
        'stat: 3,000; ' +
        'statLabel: Federal agents deployed to Minneapolis; ' +
        'body: Jan 6: DHS announces largest operation ever. Jan 7: Renee Good killed. 2,000 initial agents expanded to 3,000. Minneapolis cost: $200M+ for January alone. ICE detainee flights from Minneapolis doubled. Warrantless arrests, citizen detentions, aggressive clashes documented.; ' +
        'source: DHS / Minnesota Reformer; ' +
        'trust: contested; ' +
        'width: 2.8; height: 2.2; variant: cost'
      );
      container.appendChild(reneeData);

      // ── ALEX PRETTI — Next section ──
      const alexZ = reneeZ - 6;

      // Dark alcove for Alex
      const alexFloor = document.createElement('a-plane');
      alexFloor.setAttribute('position', `0 0.01 ${alexZ}`);
      alexFloor.setAttribute('rotation', '-90 0 0');
      alexFloor.setAttribute('width', corridorWidth.toString());
      alexFloor.setAttribute('height', '5');
      alexFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(alexFloor);

      // Walls
      const alexLW = document.createElement('a-plane');
      alexLW.setAttribute('position', `${-corridorWidth / 2} 1.5 ${alexZ}`);
      alexLW.setAttribute('rotation', '0 90 0');
      alexLW.setAttribute('width', '5');
      alexLW.setAttribute('height', '3');
      alexLW.setAttribute('color', '#0a0a0a');
      container.appendChild(alexLW);

      const alexRW = document.createElement('a-plane');
      alexRW.setAttribute('position', `${corridorWidth / 2} 1.5 ${alexZ}`);
      alexRW.setAttribute('rotation', '0 -90 0');
      alexRW.setAttribute('width', '5');
      alexRW.setAttribute('height', '3');
      alexRW.setAttribute('color', '#0a0a0a');
      container.appendChild(alexRW);

      // Main placard — left wall
      const alexPlacard = document.createElement('a-entity');
      alexPlacard.setAttribute('position', `${-(corridorWidth / 2 - 0.06)} 1.8 ${alexZ}`);
      alexPlacard.setAttribute('rotation', '0 90 0');
      alexPlacard.setAttribute('museum-placard',
        'heading: ALEX JEFFREY PRETTI; ' +
        'subheading: Age 37 | American Citizen | January 24, 2026; ' +
        'stat: 10 SHOTS; ' +
        'statLabel: Fired by two CBP agents; ' +
        'body: ICU nurse at Minneapolis VA hospital. Registered nurse since 2021, no criminal record, licensed to carry. Pretti was recording federal agents during an immigration arrest when he was tackled. Agents removed his holstered firearm, then two agents fired 10 shots. Officers did not perform CPR. A pediatrician who witnessed from her apartment was initially prevented from helping. DHS called him a domestic terrorist. Video contradicted their account.; ' +
        'source: Bellingcat / ProPublica / Marshall Project; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.2; variant: memorial'
      );
      container.appendChild(alexPlacard);

      // Data breakdown — right wall
      const alexData = document.createElement('a-entity');
      alexData.setAttribute('position', `${corridorWidth / 2 - 0.06} 1.8 ${alexZ}`);
      alexData.setAttribute('rotation', '0 -90 0');
      alexData.setAttribute('museum-placard',
        'heading: FEDERAL AGENTS FIRING ON CIVILIANS; ' +
        'subheading: Nationwide Pattern — 2025-2026; ' +
        'stat: 19; ' +
        'statLabel: Shooting incidents during immigration ops; ' +
        'body: 8 non-fatal shootings. 9 vehicle-related shootings in 4 months where agents claimed drivers tried to strike them. Multiple cases where body camera footage contradicted official accounts. Victims include: Silverio Villegas Gonzalez (Chicago, Sep 2025), Isaias Sanchez Barboza (TX, Dec 2025), Keith Porter (LA, Dec 2025), Renee Good and Alex Pretti (Minneapolis, Jan 2026).; ' +
        'source: Marshall Project / ProPublica / CBS News; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.2; variant: cost'
      );
      container.appendChild(alexData);

      // ── Final closing placard ──
      const closingZ = alexZ - 4;
      const closingFloor = document.createElement('a-plane');
      closingFloor.setAttribute('position', `0 0.01 ${closingZ}`);
      closingFloor.setAttribute('rotation', '-90 0 0');
      closingFloor.setAttribute('width', corridorWidth.toString());
      closingFloor.setAttribute('height', '4');
      closingFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(closingFloor);

      const closingPlacard = document.createElement('a-entity');
      closingPlacard.setAttribute('position', `0 1.8 ${closingZ}`);
      closingPlacard.setAttribute('museum-placard',
        'heading: THE COST OF ENFORCEMENT; ' +
        'subheading: What these numbers represent; ' +
        'body: Every statistic in this corridor represents a human life, a family torn apart, a community terrorized. The data is not neutral. The enforcement is not abstract. These are the consequences of policy choices made in your name.; ' +
        'source: ICE Data Explorer; ' +
        'trust: verified; ' +
        'width: 3.5; height: 1.6; variant: memorial'
      );
      container.appendChild(closingPlacard);

      // ── Red particles for featured section ──
      const featuredParticles = document.createElement('a-entity');
      featuredParticles.setAttribute('position', `0 3 ${(featuredStartZ + closingZ) / 2}`);
      featuredParticles.setAttribute('particle-system',
        'preset: dust; ' +
        'color: #C0392B,#1a1a1a; ' +
        'particleCount: 150; ' +
        'size: 0.04; ' +
        'maxAge: 10; ' +
        'velocityValue: 0 -0.08 0; ' +
        'accelerationSpread: 0.3 0.05 0.3; ' +
        'opacity: 0.25'
      );
      container.appendChild(featuredParticles);
    }

    console.log('[timeline] Brutalist corridor + memorial + featured cases generated');
  });
});
