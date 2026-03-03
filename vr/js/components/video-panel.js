/**
 * video-panel — Floating video with gaze-to-play and data overlays
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

    const screen = document.createElement('a-plane');
    screen.setAttribute('width', d.width);
    screen.setAttribute('height', d.height);
    screen.setAttribute('color', '#1a1a1a');
    screen.setAttribute('opacity', '0.9');
    if (d.src) {
      screen.setAttribute('material', `src: ${d.src}; shader: flat`);
    }
    screen.classList.add('clickable');
    this.el.appendChild(screen);
    this.screen = screen;

    const frame = document.createElement('a-plane');
    frame.setAttribute('width', d.width + 0.04);
    frame.setAttribute('height', d.height + 0.04);
    frame.setAttribute('color', '#444');
    frame.setAttribute('position', '0 0 -0.005');
    this.el.appendChild(frame);
    this.frame = frame;

    const title = document.createElement('a-text');
    title.setAttribute('value', d.title);
    title.setAttribute('align', 'center');
    title.setAttribute('color', '#CCC');
    title.setAttribute('width', '2.5');
    title.setAttribute('position', `0 ${d.height / 2 + 0.15} 0.01`);
    title.setAttribute('font', 'monoid');
    title.setAttribute('visible', 'false');
    this.el.appendChild(title);
    this.titleEl = title;

    const dateLoc = document.createElement('a-text');
    dateLoc.setAttribute('value', `${d.date}  ${d.location}`);
    dateLoc.setAttribute('align', 'center');
    dateLoc.setAttribute('color', '#999');
    dateLoc.setAttribute('width', '1.8');
    dateLoc.setAttribute('position', `0 ${d.height / 2 + 0.35} 0.01`);
    dateLoc.setAttribute('font', 'monoid');
    dateLoc.setAttribute('visible', 'false');
    this.el.appendChild(dateLoc);
    this.dateLocEl = dateLoc;

    if (d.statLabel) {
      const stat = document.createElement('a-entity');
      stat.setAttribute('tooltip-3d',
        `title: ${d.statLabel}; value: ${d.statValue}; source: ${d.source}; trust: ${d.trust}; visible: false`
      );
      stat.setAttribute('position', `${-(d.width / 2 + 0.8)} 0 0`);
      this.el.appendChild(stat);
      this.statEl = stat;
    }

    const playIcon = document.createElement('a-triangle');
    playIcon.setAttribute('vertex-a', '0.15 0 0');
    playIcon.setAttribute('vertex-b', '-0.1 0.15 0');
    playIcon.setAttribute('vertex-c', '-0.1 -0.15 0');
    playIcon.setAttribute('color', '#FFF');
    playIcon.setAttribute('opacity', '0.7');
    playIcon.setAttribute('position', '0 0 0.01');
    playIcon.setAttribute('material', 'shader: flat');
    this.el.appendChild(playIcon);
    this.playIcon = playIcon;

    screen.addEventListener('click', () => {
      this._togglePlay();
    });

    screen.addEventListener('mouseenter', () => {
      this.titleEl.setAttribute('visible', true);
      this.dateLocEl.setAttribute('visible', true);
      this.frame.setAttribute('color', '#666');
    });
    screen.addEventListener('mouseleave', () => {
      if (!this.playing) {
        this.titleEl.setAttribute('visible', false);
        this.dateLocEl.setAttribute('visible', false);
      }
      this.frame.setAttribute('color', '#444');
    });
  },

  _togglePlay: function () {
    this.playing = !this.playing;

    if (this.playing) {
      this.titleEl.setAttribute('visible', true);
      this.dateLocEl.setAttribute('visible', true);
      this.playIcon.setAttribute('visible', false);
      if (this.statEl && this.statEl.components['tooltip-3d']) {
        this.statEl.components['tooltip-3d'].show();
      }
      this.el.sceneEl.emit('video-playing', { panel: this.el });
    } else {
      this.playIcon.setAttribute('visible', true);
      if (this.statEl && this.statEl.components['tooltip-3d']) {
        this.statEl.components['tooltip-3d'].hide();
      }
    }
  },

  pause: function () {
    this.playing = false;
    this.playIcon.setAttribute('visible', true);
    this.titleEl.setAttribute('visible', false);
    this.dateLocEl.setAttribute('visible', false);
    if (this.statEl && this.statEl.components['tooltip-3d']) {
      this.statEl.components['tooltip-3d'].hide();
    }
  }
});
