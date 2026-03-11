// vr/js/components/narrative-placard.js
AFRAME.registerComponent('narrative-placard', {
  schema: {
    type:    { type: 'string',  default: 'watchdog' },
    speaker: { type: 'string',  default: '' },
    date:    { type: 'string',  default: '' },
    body:    { type: 'string',  default: '' },
    source:  { type: 'string',  default: '' },
    width:   { type: 'number',  default: 2.2 },
    height:  { type: 'number',  default: 1.5 }
  },

  init: function () {
    const d = this.data;
    const el = this.el;

    const isTestimony = d.type === 'testimony';

    // Palette
    const bg          = isTestimony ? '#1a0810' : '#1a0e00';
    const border      = isTestimony ? '#5a1030' : '#5a3a00';
    const accent      = isTestimony ? '#c8506a' : '#c8902a';
    const speakerClr  = isTestimony ? '#c8506a' : '#c8902a';
    const bodyClr     = isTestimony ? '#8a3a5a' : '#8a6a30';
    const badge       = isTestimony ? 'TESTIMONY' : 'WATCHDOG';
    const badgeBg     = isTestimony ? '#1a0010' : '#2a1a00';
    const badgeBorder = isTestimony ? '#5a0030' : '#5a3a00';
    const badgeColor  = isTestimony ? '#9a3050' : '#9a6a20';

    const w = d.width;
    const h = d.height;

    // Border frame (behind bg)
    const frame = document.createElement('a-plane');
    frame.setAttribute('width', w + 0.04);
    frame.setAttribute('height', h + 0.04);
    frame.setAttribute('color', border);
    frame.setAttribute('position', '0 0 -0.005');
    el.appendChild(frame);

    // Background plane
    const bgPlane = document.createElement('a-plane');
    bgPlane.setAttribute('width', w);
    bgPlane.setAttribute('height', h);
    bgPlane.setAttribute('material', `color: ${bg}; roughness: 0.95; metalness: 0.0`);
    bgPlane.setAttribute('position', '0 0 0');
    el.appendChild(bgPlane);

    // Accent line — top edge
    const accentLine = document.createElement('a-plane');
    accentLine.setAttribute('width', w);
    accentLine.setAttribute('height', 0.025);
    accentLine.setAttribute('color', accent);
    accentLine.setAttribute('position', `0 ${h / 2 - 0.012} 0.002`);
    el.appendChild(accentLine);

    // Speaker / source name
    const speakerText = document.createElement('a-text');
    speakerText.setAttribute('value', d.speaker);
    speakerText.setAttribute('color', speakerClr);
    speakerText.setAttribute('width', w * 1.8);
    speakerText.setAttribute('wrap-count', 32);
    speakerText.setAttribute('font', 'monoid');
    speakerText.setAttribute('align', 'left');
    speakerText.setAttribute('position', `${-(w / 2) + 0.1} ${h / 2 - 0.15} 0.003`);
    el.appendChild(speakerText);

    // Date
    const dateText = document.createElement('a-text');
    dateText.setAttribute('value', d.date);
    dateText.setAttribute('color', bodyClr);
    dateText.setAttribute('width', w * 1.4);
    dateText.setAttribute('font', 'monoid');
    dateText.setAttribute('align', 'left');
    dateText.setAttribute('position', `${-(w / 2) + 0.1} ${h / 2 - 0.28} 0.003`);
    el.appendChild(dateText);

    // Divider line
    const divLine = document.createElement('a-plane');
    divLine.setAttribute('width', w - 0.2);
    divLine.setAttribute('height', 0.008);
    divLine.setAttribute('color', border);
    divLine.setAttribute('position', `0 ${h / 2 - 0.36} 0.002`);
    el.appendChild(divLine);

    // Body text — semicolons stripped (A-Frame attribute parsing)
    const safeBody = d.body.replace(/;/g, ',');
    const bodyText = document.createElement('a-text');
    bodyText.setAttribute('value', safeBody);
    bodyText.setAttribute('color', bodyClr);
    bodyText.setAttribute('width', w * 1.65);
    bodyText.setAttribute('wrap-count', 36);
    bodyText.setAttribute('font', 'monoid');
    bodyText.setAttribute('align', 'left');
    bodyText.setAttribute('baseline', 'top');
    bodyText.setAttribute('position', `${-(w / 2) + 0.1} ${h / 2 - 0.46} 0.003`);
    el.appendChild(bodyText);

    // Badge border
    const badgeBorderPlane = document.createElement('a-plane');
    badgeBorderPlane.setAttribute('width', 0.57);
    badgeBorderPlane.setAttribute('height', 0.12);
    badgeBorderPlane.setAttribute('color', badgeBorder);
    badgeBorderPlane.setAttribute('position', `${-(w / 2) + 0.375} ${-(h / 2) + 0.1} 0.002`);
    el.appendChild(badgeBorderPlane);

    // Badge background
    const badgeBgPlane = document.createElement('a-plane');
    badgeBgPlane.setAttribute('width', 0.55);
    badgeBgPlane.setAttribute('height', 0.1);
    badgeBgPlane.setAttribute('color', badgeBg);
    badgeBgPlane.setAttribute('position', `${-(w / 2) + 0.375} ${-(h / 2) + 0.1} 0.003`);
    el.appendChild(badgeBgPlane);

    // Badge text
    const badgeText = document.createElement('a-text');
    badgeText.setAttribute('value', badge);
    badgeText.setAttribute('color', badgeColor);
    badgeText.setAttribute('width', 0.9);
    badgeText.setAttribute('font', 'monoid');
    badgeText.setAttribute('align', 'center');
    badgeText.setAttribute('position', `${-(w / 2) + 0.375} ${-(h / 2) + 0.1} 0.004`);
    el.appendChild(badgeText);

    // Source text
    const safeSource = d.source.replace(/;/g, ',');
    const sourceText = document.createElement('a-text');
    sourceText.setAttribute('value', safeSource);
    sourceText.setAttribute('color', bodyClr);
    sourceText.setAttribute('width', w * 1.2);
    sourceText.setAttribute('wrap-count', 36);
    sourceText.setAttribute('font', 'monoid');
    sourceText.setAttribute('align', 'left');
    sourceText.setAttribute('position', `${-(w / 2) + 0.7} ${-(h / 2) + 0.1} 0.003`);
    el.appendChild(sourceText);
  }
});
