/**
 * museum-placard — Brutalist museum-style information placard
 *
 * Variants:
 *   standard  — Concrete dark bg (#333), stark white text, color-coded accent
 *   memorial  — Black bg (#1a1a1a), white text, blood-red accent (#C0392B)
 *   cost      — Dark bg, budget-gold accent (#D4AC0D)
 *
 * Usage:
 *   <a-entity museum-placard="heading: Title; body: Description; stat: 45,000; statLabel: Detained"></a-entity>
 */
AFRAME.registerComponent('museum-placard', {
  schema: {
    heading:    { type: 'string', default: '' },
    subheading: { type: 'string', default: '' },
    body:       { type: 'string', default: '' },
    stat:       { type: 'string', default: '' },
    statLabel:  { type: 'string', default: '' },
    source:     { type: 'string', default: '' },
    trust:      { type: 'string', default: 'verified' },
    width:      { type: 'number', default: 2.4 },
    height:     { type: 'number', default: 1.6 },
    variant:    { type: 'string', default: 'standard' },  // standard | memorial | cost
    billboard:  { type: 'boolean', default: false }
  },

  init: function () {
    this.build();
  },

  build: function () {
    const d = this.data;
    const w = d.width;
    const h = d.height;

    // Variant-specific colors
    const VARIANTS = {
      standard: { bg: '#333333', text: '#ECF0F1', accent: '#666666', statColor: '#ECF0F1', meta: '#95A5A6' },
      memorial: { bg: '#1a1a1a', text: '#ECF0F1', accent: '#C0392B', statColor: '#C0392B', meta: '#95A5A6' },
      cost:     { bg: '#1a1a1a', text: '#ECF0F1', accent: '#D4AC0D', statColor: '#D4AC0D', meta: '#95A5A6' }
    };
    const v = VARIANTS[d.variant] || VARIANTS.standard;

    // Trust-based accent override for standard variant
    if (d.variant === 'standard') {
      const trustColors = {
        verified: '#2C3E50',
        govt: '#2C3E50',
        contested: '#E74C3C',
        independent: '#D4AC0D',
        neutral: '#666666'
      };
      v.accent = trustColors[d.trust] || v.accent;
    }

    // Billboard behavior
    if (d.billboard) {
      this.el.setAttribute('look-at', '[camera]');
    }

    // ── Main backing plane ──
    const border = document.createElement('a-plane');
    border.setAttribute('width', w + 0.08);
    border.setAttribute('height', h + 0.08);
    border.setAttribute('color', '#1a1a1a');
    border.setAttribute('position', '0 0 -0.005');
    this.el.appendChild(border);

    const bg = document.createElement('a-plane');
    bg.setAttribute('width', w);
    bg.setAttribute('height', h);
    bg.setAttribute('color', v.bg);
    this.el.appendChild(bg);

    // ── Left accent bar ──
    const accent = document.createElement('a-plane');
    accent.setAttribute('width', 0.08);
    accent.setAttribute('height', h);
    accent.setAttribute('position', `${-w / 2 + 0.04} 0 0.001`);
    accent.setAttribute('color', v.accent);
    this.el.appendChild(accent);

    // ── Text layout (top-down) ──
    let yPos = h / 2 - 0.18;  // start near top
    const leftMargin = -w / 2 + 0.22;

    // Heading
    if (d.heading) {
      const heading = document.createElement('a-text');
      heading.setAttribute('value', d.heading.toUpperCase());
      heading.setAttribute('position', `${leftMargin} ${yPos} 0.01`);
      heading.setAttribute('color', v.text);
      heading.setAttribute('width', w * 1.1);
      heading.setAttribute('font', 'monoid');
      heading.setAttribute('align', 'left');
      heading.setAttribute('baseline', 'top');
      heading.setAttribute('wrap-count', Math.floor(w * 12));
      this.el.appendChild(heading);
      yPos -= 0.22;
    }

    // Subheading
    if (d.subheading) {
      const sub = document.createElement('a-text');
      sub.setAttribute('value', d.subheading);
      sub.setAttribute('position', `${leftMargin} ${yPos} 0.01`);
      sub.setAttribute('color', v.meta);
      sub.setAttribute('width', w * 0.7);
      sub.setAttribute('font', 'monoid');
      sub.setAttribute('align', 'left');
      sub.setAttribute('baseline', 'top');
      this.el.appendChild(sub);
      yPos -= 0.18;
    }

    // Stat callout (large bold number)
    if (d.stat) {
      yPos -= 0.05;
      const statText = document.createElement('a-text');
      statText.setAttribute('value', d.stat);
      statText.setAttribute('position', `${leftMargin} ${yPos} 0.01`);
      statText.setAttribute('color', v.statColor);
      statText.setAttribute('width', w * 1.6);
      statText.setAttribute('font', 'monoid');
      statText.setAttribute('align', 'left');
      statText.setAttribute('baseline', 'top');
      this.el.appendChild(statText);
      yPos -= 0.24;

      if (d.statLabel) {
        const label = document.createElement('a-text');
        label.setAttribute('value', d.statLabel.toUpperCase());
        label.setAttribute('position', `${leftMargin} ${yPos} 0.01`);
        label.setAttribute('color', v.meta);
        label.setAttribute('width', w * 0.6);
        label.setAttribute('font', 'monoid');
        label.setAttribute('align', 'left');
        label.setAttribute('baseline', 'top');
        this.el.appendChild(label);
        yPos -= 0.2;
      }
    }

    // Body text
    if (d.body) {
      yPos -= 0.02;
      const body = document.createElement('a-text');
      body.setAttribute('value', d.body);
      body.setAttribute('position', `${leftMargin} ${yPos} 0.01`);
      body.setAttribute('color', v.text);
      body.setAttribute('width', w * 0.65);
      body.setAttribute('font', 'monoid');
      body.setAttribute('align', 'left');
      body.setAttribute('baseline', 'top');
      body.setAttribute('wrap-count', Math.floor(w * 18));
      this.el.appendChild(body);
      // Estimate lines for body text
      const charsPerLine = Math.floor(w * 18);
      const lines = Math.ceil(d.body.length / charsPerLine);
      yPos -= lines * 0.08 + 0.1;
    }

    // Source citation (bottom)
    if (d.source) {
      const sourceY = -h / 2 + 0.12;
      const src = document.createElement('a-text');
      src.setAttribute('value', 'SOURCE: ' + d.source.toUpperCase());
      src.setAttribute('position', `${leftMargin} ${sourceY} 0.01`);
      src.setAttribute('color', v.meta);
      src.setAttribute('width', w * 0.45);
      src.setAttribute('font', 'monoid');
      src.setAttribute('align', 'left');
      src.setAttribute('baseline', 'bottom');
      src.setAttribute('wrap-count', Math.floor(w * 22));
      this.el.appendChild(src);
    }
  }
});
