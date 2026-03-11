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

  function renderTimeline() {
    if (timelineLoaded) return;
    timelineLoaded = true;

    const container = document.querySelector('#timeline-segments');
    if (!container) return;

    const segmentLength = 5;
    const corridorWidth = 6;

    ERAS.forEach((era, i) => {
      const z = -(i * segmentLength);

      // ── Floor segment — brutalist concrete ──
      const floor = document.createElement('a-plane');
      floor.setAttribute('position', `0 0.01 ${z}`);
      floor.setAttribute('rotation', '-90 0 0');
      floor.setAttribute('width', corridorWidth.toString());
      floor.setAttribute('height', segmentLength.toString());
      // Alternating concrete tones
      const floorColor = i % 2 === 0 ? '#2a2a2a' : '#333333';
      floor.setAttribute('material', `color: ${floorColor}; roughness: 0.95; metalness: 0.05`);
      container.appendChild(floor);

      // ── Left wall — concrete dark ──
      const leftWall = document.createElement('a-plane');
      leftWall.setAttribute('position', `${-corridorWidth / 2} 1.5 ${z}`);
      leftWall.setAttribute('rotation', '0 90 0');
      leftWall.setAttribute('width', segmentLength.toString());
      leftWall.setAttribute('height', '3');
      leftWall.setAttribute('material', 'color: #333333; opacity: 0.7; transparent: true; roughness: 0.85; metalness: 0.1');
      container.appendChild(leftWall);

      // ── Right wall — concrete dark ──
      const rightWall = document.createElement('a-plane');
      rightWall.setAttribute('position', `${corridorWidth / 2} 1.5 ${z}`);
      rightWall.setAttribute('rotation', '0 -90 0');
      rightWall.setAttribute('width', segmentLength.toString());
      rightWall.setAttribute('height', '3');
      rightWall.setAttribute('material', 'color: #333333; opacity: 0.7; transparent: true; roughness: 0.85; metalness: 0.1');
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
    });

    // ══════════════════════════════════════════
    //  MEMORIAL SECTION — after last era
    // ══════════════════════════════════════════
    const memorialStartZ = -(ERAS.length * segmentLength) - 3;
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
      'subheading: Lives Lost to U.S. Immigration Enforcement; ' +
      'stat: 38+; ' +
      'statLabel: Deaths in ICE custody, 2025-2026; ' +
      'body: 32 died in 2025 — triple the previous year, the highest toll outside COVID. 6 more in the first three weeks of 2026. 71% died in for-profit facilities. 95% were preventable with basic medical care. At Fort Bliss tent city, a medical examiner ruled one death a HOMICIDE by guards. ICE had called it suicide. Plus 4 civilians shot dead by federal agents.; ' +
      'source: The Appeal / PBS / Physicians for Human Rights / El Paso Medical Examiner; ' +
      'trust: verified; ' +
      'width: 3.5; height: 2.4; variant: memorial'
    );
    container.appendChild(entrancePlacard);

    // ── Contradiction display ──
    const contraZ = memorialStartZ - 2;
    const contraEntity = document.createElement('a-entity');
    contraEntity.setAttribute('position', `0 1.8 ${contraZ}`);
    contraEntity.setAttribute('contradiction',
      'metric: Deaths in ICE Custody (2025-26); ' +
      'govtValue: 9 deaths (claimed by ICE); govtSource: Acting Director Todd Lyons; ' +
      'indepValue: 38+ deaths documented; indepSource: The Appeal / Senate Democrats / PBS; ' +
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

      // ── Featured section floor ──
      const surgeFloor = document.createElement('a-plane');
      surgeFloor.setAttribute('position', `0 0.01 ${featuredStartZ + 1}`);
      surgeFloor.setAttribute('rotation', '-90 0 0');
      surgeFloor.setAttribute('width', corridorWidth.toString());
      surgeFloor.setAttribute('height', '10');
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

      // ── ICE EXPANSION placard — accountability gap ──
      const expansionPlacard = document.createElement('a-entity');
      expansionPlacard.setAttribute('position', `0 2.2 ${featuredStartZ}`);
      expansionPlacard.setAttribute('museum-placard',
        'heading: THE EXPANSION; ' +
        'subheading: ICE Growth Has Outpaced Accountability; ' +
        'stat: $170B; ' +
        'statLabel: Allocated for immigration enforcement; ' +
        'body: 540,000 deportations targeted. 12,000 new ICE agents hired. Training academy shortened from 22 weeks to 8 — a 64% reduction. 130+ new detention facilities opened in 2025. ICE now operates nearly 200 jails nationwide. 60% of Americans believe ICE uses excessive force. Fort Bliss tent city holds 2,000+ daily with 5,000 capacity, and DHS is building an 8,500-bed mega-facility nearby.; ' +
        'source: Brookings Institution / The Appeal / CBO; ' +
        'trust: verified; ' +
        'width: 4; height: 2.4; variant: cost'
      );
      container.appendChild(expansionPlacard);

      // Surge header placard — center wall (offset further)
      const surgeZ = featuredStartZ - 3;
      const surgeHeader = document.createElement('a-entity');
      surgeHeader.setAttribute('position', `0 2.2 ${surgeZ}`);
      surgeHeader.setAttribute('museum-placard',
        'heading: OPERATION METRO SURGE; ' +
        'subheading: Minneapolis-St. Paul / January 2026; ' +
        'stat: 4,000+; ' +
        'statLabel: Arrests in 7 weeks; ' +
        'body: The largest DHS enforcement operation in U.S. history. 3,000 federal agents deployed — many with only 8 weeks training. 2 civilians killed by federal officers. 19 firing incidents nationwide. Cost to Minneapolis: $200M+. Agents drawn from new hires with 64% less training than prior classes.; ' +
        'source: DHS / Minnesota Reformer / Marshall Project / Brookings; ' +
        'trust: contested; ' +
        'width: 4; height: 2.2; variant: memorial'
      );
      container.appendChild(surgeHeader);

      // Extra floor for expansion + surge
      const surgeExtraFloor = document.createElement('a-plane');
      surgeExtraFloor.setAttribute('position', `0 0.01 ${surgeZ + 1.5}`);
      surgeExtraFloor.setAttribute('rotation', '-90 0 0');
      surgeExtraFloor.setAttribute('width', corridorWidth.toString());
      surgeExtraFloor.setAttribute('height', '4');
      surgeExtraFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(surgeExtraFloor);

      // ── RENEE NICOLE GOOD — Left wall, large featured ──
      const reneeZ = surgeZ - 4;

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
        'stat: 19+; ' +
        'statLabel: Shooting incidents during immigration ops; ' +
        'body: Fatal: Keith Porter (LA, Dec 2025), Renee Good (Minneapolis, Jan 7), Alex Pretti (Minneapolis, Jan 24). Non-fatal: Marimar Martinez (Newark, Jan 29), Julio Cesar Sosa-Celis (TX), Patrick Gary Schlegel (Portland). 9 vehicle-related shootings in 4 months — agents claimed self-defense, video contradicted. ICE has no use-of-force database. New agents have 8 weeks training vs 22 previously.; ' +
        'source: PBS NewsHour / Marshall Project / ProPublica / Brookings; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.4; variant: cost'
      );
      container.appendChild(alexData);

      // ══════════════════════════════════════════════
      //  FORT BLISS — The Tent City
      // ══════════════════════════════════════════════
      const blissZ = alexZ - 6;

      // Dark alcove for Fort Bliss
      const blissFloor = document.createElement('a-plane');
      blissFloor.setAttribute('position', `0 0.01 ${blissZ}`);
      blissFloor.setAttribute('rotation', '-90 0 0');
      blissFloor.setAttribute('width', corridorWidth.toString());
      blissFloor.setAttribute('height', '5');
      blissFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(blissFloor);

      const blissLW = document.createElement('a-plane');
      blissLW.setAttribute('position', `${-corridorWidth / 2} 1.5 ${blissZ}`);
      blissLW.setAttribute('rotation', '0 90 0');
      blissLW.setAttribute('width', '5');
      blissLW.setAttribute('height', '3');
      blissLW.setAttribute('color', '#0a0a0a');
      container.appendChild(blissLW);

      const blissRW = document.createElement('a-plane');
      blissRW.setAttribute('position', `${corridorWidth / 2} 1.5 ${blissZ}`);
      blissRW.setAttribute('rotation', '0 -90 0');
      blissRW.setAttribute('width', '5');
      blissRW.setAttribute('height', '3');
      blissRW.setAttribute('color', '#0a0a0a');
      container.appendChild(blissRW);

      // Main placard — left wall: Geraldo Lunas Campos
      const camposPlacard = document.createElement('a-entity');
      camposPlacard.setAttribute('position', `${-(corridorWidth / 2 - 0.06)} 1.8 ${blissZ}`);
      camposPlacard.setAttribute('rotation', '0 90 0');
      camposPlacard.setAttribute('museum-placard',
        'heading: GERALDO LUNAS CAMPOS; ' +
        'subheading: Age 55 | Cuba | January 3, 2026; ' +
        'stat: HOMICIDE; ' +
        'statLabel: Ruled by El Paso County Medical Examiner; ' +
        'body: ICE claimed attempted suicide. The county medical examiner ruled it HOMICIDE — asphyxia from neck and torso compression by guards. A fellow detainee saw guards choking Campos, who repeatedly said "I can\'t breathe" in Spanish. He was a father of two who had lived in the U.S. for years. Civil rights groups had warned 26 days earlier that deaths were imminent at Fort Bliss.; ' +
        'source: The Appeal / El Paso County Medical Examiner; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.4; variant: memorial'
      );
      container.appendChild(camposPlacard);

      // Fort Bliss data — right wall
      const blissData = document.createElement('a-entity');
      blissData.setAttribute('position', `${corridorWidth / 2 - 0.06} 1.8 ${blissZ}`);
      blissData.setAttribute('rotation', '0 -90 0');
      blissData.setAttribute('museum-placard',
        'heading: CAMP EAST MONTANA — FORT BLISS; ' +
        'subheading: The Tent City; ' +
        'stat: 3 DEAD; ' +
        'statLabel: In under 2 months of operation; ' +
        'body: Sprawling tent city on Fort Bliss Army base outside El Paso. Capacity: 5,000. Holds 2,000+ daily. Opened less than 4 months before first death. Conditions: inedible food, medical neglect, solitary confinement, beatings by masked officers, abusive sexual contact by contractors. DHS is building an 8,500-bed mega-facility nearby. The same base held 100,000+ Japanese Americans during WWII.; ' +
        'source: The Appeal / Civil Rights Coalition Letter; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.4; variant: cost'
      );
      container.appendChild(blissData);

      // Fort Bliss contradiction — center
      const blissContra = document.createElement('a-entity');
      blissContra.setAttribute('position', `0 1.6 ${blissZ - 2}`);
      blissContra.setAttribute('contradiction',
        'metric: Campos Death at Fort Bliss; ' +
        'govtValue: Attempted suicide; govtSource: ICE Statement; ' +
        'indepValue: HOMICIDE by guards; indepSource: El Paso County Medical Examiner; ' +
        'severity: high'
      );
      container.appendChild(blissContra);

      // ══════════════════════════════════════════════
      //  WHO PROFITS FROM DETENTION
      // ══════════════════════════════════════════════
      const profitZ = blissZ - 6;

      const profitFloor = document.createElement('a-plane');
      profitFloor.setAttribute('position', `0 0.01 ${profitZ}`);
      profitFloor.setAttribute('rotation', '-90 0 0');
      profitFloor.setAttribute('width', corridorWidth.toString());
      profitFloor.setAttribute('height', '5');
      profitFloor.setAttribute('color', '#0a0a0a');
      container.appendChild(profitFloor);

      // Gold accent line (money)
      const goldLine = document.createElement('a-plane');
      goldLine.setAttribute('position', `0 0.02 ${profitZ + 2}`);
      goldLine.setAttribute('rotation', '-90 0 0');
      goldLine.setAttribute('width', corridorWidth.toString());
      goldLine.setAttribute('height', '0.08');
      goldLine.setAttribute('color', '#D4AC0D');
      container.appendChild(goldLine);

      const profitPlacard = document.createElement('a-entity');
      profitPlacard.setAttribute('position', `${-(corridorWidth / 2 - 0.06)} 1.8 ${profitZ}`);
      profitPlacard.setAttribute('rotation', '0 90 0');
      profitPlacard.setAttribute('museum-placard',
        'heading: WHO PROFITS FROM DETENTION; ' +
        'subheading: Private Prison Industry — By the Numbers; ' +
        'stat: $3B; ' +
        'statLabel: GEO Group projected 2026 revenue; ' +
        'body: GEO Group Q4 2025: net income doubled to $31.8M. Total 2025 revenue: $2.63B. CoreCivic ICE revenue: $245M/quarter (doubled from $120M). CoreCivic 2025 profits: $116.5M (up 70%). GEO holds 24,000 ICE detainees — their highest ever. They told investors they are ready to scale to 100,000+ monitored. 71% of all custody deaths in for-profit facilities.; ' +
        'source: The Appeal / GEO + CoreCivic Earnings Calls; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.6; variant: cost'
      );
      container.appendChild(profitPlacard);

      const profitData = document.createElement('a-entity');
      profitData.setAttribute('position', `${corridorWidth / 2 - 0.06} 1.8 ${profitZ}`);
      profitData.setAttribute('rotation', '0 -90 0');
      profitData.setAttribute('museum-placard',
        'heading: THE DETENTION-TO-DONATION PIPELINE; ' +
        'subheading: Money In, Bodies Out; ' +
        'stat: $528K+; ' +
        'statLabel: Private prison PAC donations to Congress; ' +
        'body: GEO PAC: $280K. CoreCivic PAC: $248K. MTC PAC: $147K. Executives Zoley and Hininger: $1M+ each personally. Republicans: ~$500K, Democrats: $57K. Bipartisan complicity. Dilley family center: $180M/year. GEO has 6,000 beds ready at former federal prisons, potential $300M+ annual revenue. CoreCivic has 13,000 empty beds ready to fill.; ' +
        'source: The Appeal / OpenSecrets / FEC / Earnings Calls; ' +
        'trust: verified; ' +
        'width: 2.8; height: 2.6; variant: cost'
      );
      container.appendChild(profitData);

      // ── Final closing placard ──
      const closingZ = profitZ - 4;
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
        'body: 38+ dead in custody. 4 civilians shot. $170 billion allocated. 71% of deaths in for-profit facilities. 95% preventable. Training cut by 64%. A medical examiner ruled one death a homicide — ICE called it suicide. Every statistic is a person. Every dollar is a choice. These are the consequences of policy decisions made in your name.; ' +
        'source: ICE Data Explorer — All sources cited above; ' +
        'trust: verified; ' +
        'width: 3.5; height: 1.8; variant: memorial'
      );
      container.appendChild(closingPlacard);

      // ── Red particles for featured section ──
      const featuredMid = (featuredStartZ + closingZ) / 2;
      const featuredParticles = document.createElement('a-entity');
      featuredParticles.setAttribute('position', `0 3 ${featuredMid}`);
      featuredParticles.setAttribute('particle-system',
        'preset: dust; ' +
        'color: #C0392B,#1a1a1a; ' +
        'particleCount: 250; ' +
        'size: 0.04; ' +
        'maxAge: 12; ' +
        'velocityValue: 0 -0.08 0; ' +
        'accelerationSpread: 0.5 0.05 0.5; ' +
        'opacity: 0.25'
      );
      container.appendChild(featuredParticles);

      // Second particle emitter for the extended corridor
      const featuredParticles2 = document.createElement('a-entity');
      featuredParticles2.setAttribute('position', `0 3 ${featuredMid - 15}`);
      featuredParticles2.setAttribute('particle-system',
        'preset: dust; ' +
        'color: #D4AC0D,#1a1a1a; ' +
        'particleCount: 150; ' +
        'size: 0.03; ' +
        'maxAge: 10; ' +
        'velocityValue: 0 -0.06 0; ' +
        'accelerationSpread: 0.4 0.05 0.4; ' +
        'opacity: 0.2'
      );
      container.appendChild(featuredParticles2);
    }

    console.log('[timeline] Brutalist corridor + memorial + featured cases generated');
  }

  if (scene.hasLoaded) {
    renderTimeline();
  } else {
    scene.addEventListener('loaded', renderTimeline, { once: true });
  }
});
