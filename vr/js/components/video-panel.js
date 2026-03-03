/**
 * video-panel — Surveillance-style footage panel with always-visible metadata
 *
 * Displays as a labeled screen with title, date, location, stat overlay,
 * and source badge. Without a video src, renders as a dark monitor with
 * text overlays resembling a surveillance still frame.
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
    height: { type: 'number', default: 1.125 }
  },

  init: function () {
    const d = this.data;
    this.playing = false;

    const w = d.width;
    const h = d.height;

    // ── Steel frame ──
    const frame = document.createElement('a-plane');
    frame.setAttribute('width', w + 0.06);
    frame.setAttribute('height', h + 0.06);
    frame.setAttribute('color', '#444');
    frame.setAttribute('position', '0 0 -0.005');
    this.el.appendChild(frame);
    this.frame = frame;

    // ── Dark screen ──
    const screen = document.createElement('a-plane');
    screen.setAttribute('width', w);
    screen.setAttribute('height', h);
    screen.setAttribute('color', '#111111');
    if (d.src) {
      screen.setAttribute('material', `src: ${d.src}; shader: flat`);
    }
    screen.classList.add('clickable');
    this.el.appendChild(screen);
    this.screen = screen;

    // ── Scanline effect ──
    const scanlineCount = 8;
    for (let i = 0; i < scanlineCount; i++) {
      const line = document.createElement('a-plane');
      const y = (h / 2) - (i * (h / scanlineCount)) - (h / scanlineCount / 2);
      line.setAttribute('width', w);
      line.setAttribute('height', h / scanlineCount * 0.25);
      line.setAttribute('position', `0 ${y} 0.002`);
      line.setAttribute('color', '#000000');
      line.setAttribute('opacity', '0.12');
      line.setAttribute('transparent', 'true');
      this.el.appendChild(line);
    }

    // ── Always-visible title (top, large) ──
    if (d.title) {
      // Truncate long titles across two lines
      const maxChars = 35;
      let titleStr = d.title;
      if (titleStr.length > maxChars) {
        titleStr = titleStr.substring(0, maxChars - 2) + '..';
      }
      const title = document.createElement('a-text');
      title.setAttribute('value', titleStr.toUpperCase());
      title.setAttribute('align', 'left');
      title.setAttribute('color', '#ECF0F1');
      title.setAttribute('width', w * 0.85);
      title.setAttribute('position', `${-w / 2 + 0.08} ${h / 2 - 0.12} 0.01`);
      title.setAttribute('font', 'monoid');
      title.setAttribute('baseline', 'top');
      title.setAttribute('wrap-count', 40);
      this.el.appendChild(title);
    }

    // ── Date + location (top-right area) ──
    if (d.date || d.location) {
      const dateText = document.createElement('a-text');
      dateText.setAttribute('value', d.date);
      dateText.setAttribute('align', 'right');
      dateText.setAttribute('color', '#95A5A6');
      dateText.setAttribute('width', w * 0.55);
      dateText.setAttribute('position', `${w / 2 - 0.08} ${h / 2 - 0.12} 0.01`);
      dateText.setAttribute('font', 'monoid');
      dateText.setAttribute('baseline', 'top');
      this.el.appendChild(dateText);

      if (d.location) {
        const locText = document.createElement('a-text');
        locText.setAttribute('value', d.location);
        locText.setAttribute('align', 'right');
        locText.setAttribute('color', '#666666');
        locText.setAttribute('width', w * 0.5);
        locText.setAttribute('position', `${w / 2 - 0.08} ${h / 2 - 0.24} 0.01`);
        locText.setAttribute('font', 'monoid');
        locText.setAttribute('baseline', 'top');
        this.el.appendChild(locText);
      }
    }

    // ── Large stat callout (center) ──
    if (d.statValue) {
      const statVal = document.createElement('a-text');
      statVal.setAttribute('value', d.statValue);
      statVal.setAttribute('align', 'center');
      statVal.setAttribute('color', '#ECF0F1');
      statVal.setAttribute('width', w * 1.4);
      statVal.setAttribute('position', `0 0.05 0.01`);
      statVal.setAttribute('font', 'monoid');
      this.el.appendChild(statVal);

      if (d.statLabel) {
        const statLbl = document.createElement('a-text');
        statLbl.setAttribute('value', d.statLabel.toUpperCase());
        statLbl.setAttribute('align', 'center');
        statLbl.setAttribute('color', '#95A5A6');
        statLbl.setAttribute('width', w * 0.6);
        statLbl.setAttribute('position', `0 -0.12 0.01`);
        statLbl.setAttribute('font', 'monoid');
        this.el.appendChild(statLbl);
      }
    }

    // ── Source + trust badge (bottom-left) ──
    if (d.source) {
      const trustColors = {
        verified: '#27AE60',
        govt: '#2C3E50',
        contested: '#E74C3C',
        neutral: '#666666'
      };
      const badgeColor = trustColors[d.trust] || '#666666';

      // Trust dot
      const dot = document.createElement('a-circle');
      dot.setAttribute('radius', 0.02);
      dot.setAttribute('position', `${-w / 2 + 0.1} ${-h / 2 + 0.1} 0.01`);
      dot.setAttribute('color', badgeColor);
      this.el.appendChild(dot);

      const srcText = document.createElement('a-text');
      srcText.setAttribute('value', d.source.toUpperCase());
      srcText.setAttribute('align', 'left');
      srcText.setAttribute('color', '#666666');
      srcText.setAttribute('width', w * 0.45);
      srcText.setAttribute('position', `${-w / 2 + 0.16} ${-h / 2 + 0.1} 0.01`);
      srcText.setAttribute('font', 'monoid');
      this.el.appendChild(srcText);
    }

    // ── REC indicator (top-left) ──
    const recDot = document.createElement('a-circle');
    recDot.setAttribute('radius', 0.018);
    recDot.setAttribute('position', `${-w / 2 + 0.08} ${h / 2 - 0.06} 0.015`);
    recDot.setAttribute('color', '#C0392B');
    this.el.appendChild(recDot);

    // ── Play icon (center, semi-transparent) ──
    if (!d.src) {
      const playIcon = document.createElement('a-triangle');
      playIcon.setAttribute('vertex-a', '0.12 0 0');
      playIcon.setAttribute('vertex-b', '-0.08 0.12 0');
      playIcon.setAttribute('vertex-c', '-0.08 -0.12 0');
      playIcon.setAttribute('color', '#ECF0F1');
      playIcon.setAttribute('opacity', '0.2');
      playIcon.setAttribute('position', `0 0 0.005`);
      playIcon.setAttribute('material', 'shader: flat; transparent: true');
      this.el.appendChild(playIcon);
      this.playIcon = playIcon;
    }

    // Hover effect
    screen.addEventListener('mouseenter', () => {
      frame.setAttribute('color', '#666');
    });
    screen.addEventListener('mouseleave', () => {
      frame.setAttribute('color', '#444');
    });

    // Click handler
    screen.addEventListener('click', () => {
      this._togglePlay();
    });
  },

  _togglePlay: function () {
    this.playing = !this.playing;
    if (this.playing) {
      if (this.playIcon) this.playIcon.setAttribute('visible', false);
      this.el.sceneEl.emit('video-playing', { panel: this.el });
    } else {
      if (this.playIcon) this.playIcon.setAttribute('visible', true);
    }
  },

  pause: function () {
    this.playing = false;
    if (this.playIcon) this.playIcon.setAttribute('visible', true);
  }
});
