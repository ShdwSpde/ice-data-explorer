/**
 * security-feed — Surveillance monitor panel for facility data
 *
 * Displays a single facility as a dark surveillance monitor with:
 *  - Facility name overlay
 *  - Location text
 *  - Capacity bar (green < 80%, yellow 80-100%, red > 100%)
 *  - Scanline effect
 *  - Optional flicker animation
 *
 * Usage:
 *   <a-entity security-feed="name: Adelanto ICE; location: Adelanto, CA; capacity: 1940; population: 2100; isVideo: true"></a-entity>
 */
AFRAME.registerComponent('security-feed', {
  schema: {
    name:       { type: 'string', default: 'UNKNOWN FACILITY' },
    location:   { type: 'string', default: '' },
    capacity:   { type: 'number', default: 0 },
    population: { type: 'number', default: 0 },
    operator:   { type: 'string', default: '' },
    type:       { type: 'string', default: 'government' },
    isVideo:    { type: 'boolean', default: false },
    width:      { type: 'number', default: 1.2 },
    height:     { type: 'number', default: 0.8 }
  },

  init: function () {
    this.build();
    if (this.data.isVideo) {
      this.flickerInterval = null;
      this.startFlicker();
    }
  },

  build: function () {
    const d = this.data;
    const w = d.width;
    const h = d.height;

    // ── Steel frame ──
    const frame = document.createElement('a-plane');
    frame.setAttribute('width', w + 0.06);
    frame.setAttribute('height', h + 0.06);
    frame.setAttribute('color', '#444444');
    frame.setAttribute('position', '0 0 -0.005');
    this.el.appendChild(frame);

    // ── Dark screen ──
    this.screen = document.createElement('a-plane');
    this.screen.setAttribute('width', w);
    this.screen.setAttribute('height', h);
    this.screen.setAttribute('color', '#1a1a1a');
    this.screen.classList.add('security-screen');
    this.el.appendChild(this.screen);

    // ── Scanline overlay (striped opacity) ──
    // Create multiple thin semi-transparent lines
    const scanlineCount = 12;
    for (let i = 0; i < scanlineCount; i++) {
      const line = document.createElement('a-plane');
      const y = (h / 2) - (i * (h / scanlineCount)) - (h / scanlineCount / 2);
      line.setAttribute('width', w);
      line.setAttribute('height', h / scanlineCount * 0.3);
      line.setAttribute('position', `0 ${y} 0.002`);
      line.setAttribute('color', '#000000');
      line.setAttribute('opacity', '0.15');
      line.setAttribute('transparent', 'true');
      this.el.appendChild(line);
    }

    // ── Status dot (top-right) ──
    const ratio = d.capacity > 0 ? d.population / d.capacity : 0;
    const statusColor = ratio > 1 ? '#C0392B' : '#27AE60';
    const statusDot = document.createElement('a-circle');
    statusDot.setAttribute('radius', 0.025);
    statusDot.setAttribute('position', `${w / 2 - 0.06} ${h / 2 - 0.06} 0.003`);
    statusDot.setAttribute('color', statusColor);
    this.el.appendChild(statusDot);

    // ── Facility name (bottom-left, monoid, small) ──
    const nameText = document.createElement('a-text');
    // Truncate long names
    const displayName = d.name.length > 22 ? d.name.substring(0, 20) + '..' : d.name;
    nameText.setAttribute('value', displayName.toUpperCase());
    nameText.setAttribute('position', `${-w / 2 + 0.06} ${-h / 2 + 0.18} 0.003`);
    nameText.setAttribute('color', '#ECF0F1');
    nameText.setAttribute('width', w * 0.75);
    nameText.setAttribute('font', 'monoid');
    nameText.setAttribute('align', 'left');
    nameText.setAttribute('baseline', 'bottom');
    this.el.appendChild(nameText);

    // ── Location (below name) ──
    if (d.location) {
      const locText = document.createElement('a-text');
      locText.setAttribute('value', d.location);
      locText.setAttribute('position', `${-w / 2 + 0.06} ${-h / 2 + 0.08} 0.003`);
      locText.setAttribute('color', '#666666');
      locText.setAttribute('width', w * 0.6);
      locText.setAttribute('font', 'monoid');
      locText.setAttribute('align', 'left');
      locText.setAttribute('baseline', 'bottom');
      this.el.appendChild(locText);
    }

    // ── Capacity bar (thin horizontal) ──
    if (d.capacity > 0) {
      const barW = w * 0.6;
      const barH = 0.03;
      const barY = -h / 2 + 0.3;
      const barX = w / 2 - barW / 2 - 0.06;

      // Background
      const barBg = document.createElement('a-plane');
      barBg.setAttribute('width', barW);
      barBg.setAttribute('height', barH);
      barBg.setAttribute('position', `${barX} ${barY} 0.003`);
      barBg.setAttribute('color', '#333333');
      this.el.appendChild(barBg);

      // Fill
      const fillRatio = Math.min(ratio, 1.5);
      const fillW = barW * (fillRatio / 1.5);
      let fillColor = '#27AE60';  // green
      if (ratio > 1.0) fillColor = '#C0392B';       // red
      else if (ratio > 0.8) fillColor = '#D4AC0D';  // yellow

      const barFill = document.createElement('a-plane');
      barFill.setAttribute('width', fillW);
      barFill.setAttribute('height', barH);
      barFill.setAttribute('position', `${barX - (barW - fillW) / 2} ${barY} 0.004`);
      barFill.setAttribute('color', fillColor);
      this.el.appendChild(barFill);

      // Capacity text
      const capText = document.createElement('a-text');
      capText.setAttribute('value', `${d.population}/${d.capacity}`);
      capText.setAttribute('position', `${barX + barW / 2 + 0.02} ${barY} 0.003`);
      capText.setAttribute('color', '#95A5A6');
      capText.setAttribute('width', w * 0.35);
      capText.setAttribute('font', 'monoid');
      capText.setAttribute('align', 'left');
      capText.setAttribute('anchor', 'left');
      this.el.appendChild(capText);
    }

    // ── "REC" indicator if video ──
    if (d.isVideo) {
      const recDot = document.createElement('a-circle');
      recDot.setAttribute('radius', 0.02);
      recDot.setAttribute('position', `${-w / 2 + 0.08} ${h / 2 - 0.06} 0.003`);
      recDot.setAttribute('color', '#C0392B');
      this.el.appendChild(recDot);

      const recText = document.createElement('a-text');
      recText.setAttribute('value', 'REC');
      recText.setAttribute('position', `${-w / 2 + 0.16} ${h / 2 - 0.06} 0.003`);
      recText.setAttribute('color', '#C0392B');
      recText.setAttribute('width', w * 0.4);
      recText.setAttribute('font', 'monoid');
      recText.setAttribute('align', 'left');
      this.el.appendChild(recText);
    }
  },

  startFlicker: function () {
    if (!this.screen) return;
    let on = true;
    this.flickerInterval = setInterval(() => {
      on = !on;
      this.screen.setAttribute('opacity', on ? 1 : 0.85);
    }, 2000 + Math.random() * 3000);
  },

  remove: function () {
    if (this.flickerInterval) {
      clearInterval(this.flickerInterval);
    }
  }
});
