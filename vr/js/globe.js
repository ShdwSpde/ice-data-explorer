/**
 * Security Feed room — replaces the globe with a surveillance monitor wall
 * Fetches facility data and generates a grid of security-feed monitors.
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');
  let feedLoaded = false;

  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'globe' || feedLoaded) return;
    feedLoaded = true;

    const api = window.dataAPI;
    if (!api) return;

    const container = document.querySelector('#security-monitors');
    if (!container) return;

    const facilitiesData = await api.getFacilities();
    if (!facilitiesData || !facilitiesData.data) {
      console.error('[security-feed] No facility data');
      return;
    }

    const facilities = facilitiesData.data;

    // Monitor grid layout: 3 walls, each with rows x cols
    const monitorW = 1.2;
    const monitorH = 0.8;
    const gapX = 0.12;
    const gapY = 0.1;
    const cols = 6;
    const rows = 3;

    // Wall definitions (position, rotation, normal direction)
    const walls = [
      { // Front wall
        basePos: [0, 1.8, -6],
        rotation: '0 0 0',
      },
      { // Left wall
        basePos: [-6, 1.8, 0],
        rotation: '0 90 0',
      },
      { // Right wall
        basePos: [6, 1.8, 0],
        rotation: '0 -90 0',
      }
    ];

    // Concrete wall panels behind monitors
    walls.forEach(wall => {
      const wallPanel = document.createElement('a-plane');
      const wallW = cols * (monitorW + gapX) + 0.5;
      const wallH = rows * (monitorH + gapY) + 1;
      wallPanel.setAttribute('width', wallW);
      wallPanel.setAttribute('height', wallH);
      wallPanel.setAttribute('position', `${wall.basePos[0]} ${wall.basePos[1]} ${wall.basePos[2]}`);
      wallPanel.setAttribute('rotation', wall.rotation);
      wallPanel.setAttribute('color', '#222222');
      container.appendChild(wallPanel);
    });

    let facilityIdx = 0;
    let monitorCount = 0;

    walls.forEach(wall => {
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          if (facilityIdx >= facilities.length) break;

          const f = facilities[facilityIdx];
          facilityIdx++;
          monitorCount++;

          // Local position relative to wall center
          const localX = (col - (cols - 1) / 2) * (monitorW + gapX);
          const localY = ((rows - 1) / 2 - row) * (monitorH + gapY);

          // Parse wall rotation to compute world position
          const rotY = parseFloat(wall.rotation.split(' ')[1]) * (Math.PI / 180);
          const cosR = Math.cos(rotY);
          const sinR = Math.sin(rotY);

          // For front wall (rot 0): x offset is localX, z stays
          // For left wall (rot 90): z offset is localX, x stays
          // For right wall (rot -90): z offset is -localX, x stays
          const worldX = wall.basePos[0] + localX * cosR;
          const worldY = wall.basePos[1] + localY;
          const worldZ = wall.basePos[2] - localX * sinR;

          const monitor = document.createElement('a-entity');
          monitor.setAttribute('position', `${worldX} ${worldY} ${worldZ}`);
          monitor.setAttribute('rotation', wall.rotation);

          // Every 5th monitor is "video" (flickering)
          const isVideo = monitorCount % 5 === 0;

          const name = (f.facility_name || f.name || 'Unknown').replace(/;/g, ',');
          const loc = (f.city && f.state) ? `${f.city}, ${f.state}` : (f.location || '');
          const safeLoc = loc.replace(/;/g, ',');
          const capacity = f.capacity || 0;
          const pop = f.current_population || f.average_population || 0;

          monitor.setAttribute('security-feed',
            `name: ${name}; ` +
            `location: ${safeLoc}; ` +
            `capacity: ${capacity}; ` +
            `population: ${pop}; ` +
            `isVideo: ${isVideo}; ` +
            `width: ${monitorW}; height: ${monitorH}`
          );
          container.appendChild(monitor);
        }
      }
    });

    // Dark industrial floor
    const floor = document.createElement('a-plane');
    floor.setAttribute('position', '0 0.01 0');
    floor.setAttribute('rotation', '-90 0 0');
    floor.setAttribute('width', '14');
    floor.setAttribute('height', '14');
    floor.setAttribute('color', '#1a1a1a');
    container.appendChild(floor);

    // Room title slab on ceiling
    const titleSlab = document.createElement('a-entity');
    titleSlab.setAttribute('position', '0 3.5 -3');

    const titleBg = document.createElement('a-plane');
    titleBg.setAttribute('width', '6');
    titleBg.setAttribute('height', '0.8');
    titleBg.setAttribute('color', '#1a1a1a');
    titleSlab.appendChild(titleBg);

    const titleText = document.createElement('a-text');
    titleText.setAttribute('value', 'SECURITY FEED');
    titleText.setAttribute('position', '0 0.1 0.01');
    titleText.setAttribute('align', 'center');
    titleText.setAttribute('color', '#ECF0F1');
    titleText.setAttribute('width', '6');
    titleText.setAttribute('font', 'monoid');
    titleSlab.appendChild(titleText);

    const subtitleText = document.createElement('a-text');
    subtitleText.setAttribute('value', `${monitorCount} FACILITIES MONITORED`);
    subtitleText.setAttribute('position', '0 -0.15 0.01');
    subtitleText.setAttribute('align', 'center');
    subtitleText.setAttribute('color', '#95A5A6');
    subtitleText.setAttribute('width', '3');
    subtitleText.setAttribute('font', 'monoid');
    titleSlab.appendChild(subtitleText);

    container.appendChild(titleSlab);

    console.log(`[security-feed] Generated ${monitorCount} monitors from ${facilities.length} facilities`);
  });
});
