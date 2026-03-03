/**
 * Timeline Walk room — generates a corridor of policy eras
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');
  let timelineLoaded = false;

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
    const segmentLength = 5;

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

      const corridorWidth = 6;

      // Floor segment
      const floor = document.createElement('a-plane');
      floor.setAttribute('position', `0 0.01 ${z}`);
      floor.setAttribute('rotation', '-90 0 0');
      floor.setAttribute('width', corridorWidth.toString());
      floor.setAttribute('height', segmentLength.toString());
      floor.setAttribute('color', floorColor);
      container.appendChild(floor);

      // Left wall
      const leftWall = document.createElement('a-plane');
      leftWall.setAttribute('position', `${-corridorWidth / 2} 1.5 ${z}`);
      leftWall.setAttribute('rotation', '0 90 0');
      leftWall.setAttribute('width', segmentLength.toString());
      leftWall.setAttribute('height', '3');
      leftWall.setAttribute('color', '#EEEEEE');
      leftWall.setAttribute('opacity', '0.5');
      leftWall.setAttribute('transparent', 'true');
      container.appendChild(leftWall);

      // Right wall
      const rightWall = document.createElement('a-plane');
      rightWall.setAttribute('position', `${corridorWidth / 2} 1.5 ${z}`);
      rightWall.setAttribute('rotation', '0 -90 0');
      rightWall.setAttribute('width', segmentLength.toString());
      rightWall.setAttribute('height', '3');
      rightWall.setAttribute('color', '#EEEEEE');
      rightWall.setAttribute('opacity', '0.5');
      rightWall.setAttribute('transparent', 'true');
      container.appendChild(rightWall);

      // Divider (frosted glass)
      const divider = document.createElement('a-plane');
      divider.setAttribute('position', `0 1.5 ${z + segmentLength / 2}`);
      divider.setAttribute('width', corridorWidth.toString());
      divider.setAttribute('height', '3');
      divider.setAttribute('color', '#DDDDDD');
      divider.setAttribute('opacity', '0.2');
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
      const rightX = corridorWidth / 2 - 0.05;
      const title = document.createElement('a-text');
      title.setAttribute('value', era.label);
      title.setAttribute('position', `${rightX} 2.2 ${z}`);
      title.setAttribute('rotation', '0 -90 0');
      title.setAttribute('align', 'center');
      title.setAttribute('color', '#333');
      title.setAttribute('width', '3');
      title.setAttribute('font', 'monoid');
      container.appendChild(title);

      // Era description (right wall, below title)
      const desc = document.createElement('a-text');
      desc.setAttribute('value', era.desc);
      desc.setAttribute('position', `${rightX} 1.7 ${z}`);
      desc.setAttribute('rotation', '0 -90 0');
      desc.setAttribute('align', 'center');
      desc.setAttribute('color', '#666');
      desc.setAttribute('width', '2');
      desc.setAttribute('font', 'monoid');
      container.appendChild(desc);

      // Data bars on left wall
      const leftBarX = -(corridorWidth / 2 - 0.2);
      const eraYear = parseInt(era.year);
      const detPoint = detentionData.find(d => d.year === eraYear);
      const depPoint = deportationData.find(d => d.year === eraYear);

      if (detPoint) {
        const bar = document.createElement('a-entity');
        bar.setAttribute('position', `${leftBarX} 0 ${z - 0.3}`);
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
        bar.setAttribute('position', `${leftBarX} 0 ${z + 0.3}`);
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
