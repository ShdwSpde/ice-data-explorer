/**
 * content-gate — Content warning barrier requiring confirmation
 */
AFRAME.registerComponent('content-gate', {
  schema: {
    message: { type: 'string', default: 'Content warning: This room contains sensitive material.' },
    room: { type: 'string', default: '' }
  },

  init: function () {
    const d = this.data;

    const barrier = document.createElement('a-plane');
    barrier.setAttribute('width', '3');
    barrier.setAttribute('height', '2.5');
    barrier.setAttribute('color', '#333');
    barrier.setAttribute('opacity', '0.85');
    barrier.setAttribute('side', 'double');
    this.el.appendChild(barrier);

    const icon = document.createElement('a-triangle');
    icon.setAttribute('vertex-a', '0 0.3 0');
    icon.setAttribute('vertex-b', '-0.25 -0.15 0');
    icon.setAttribute('vertex-c', '0.25 -0.15 0');
    icon.setAttribute('color', '#F39C12');
    icon.setAttribute('position', '0 0.6 0.01');
    icon.setAttribute('material', 'shader: flat');
    this.el.appendChild(icon);

    const text = document.createElement('a-text');
    text.setAttribute('value', d.message);
    text.setAttribute('align', 'center');
    text.setAttribute('color', '#FFFFFF');
    text.setAttribute('width', '2.5');
    text.setAttribute('position', '0 0.1 0.01');
    text.setAttribute('font', 'monoid');
    this.el.appendChild(text);

    const sub = document.createElement('a-text');
    sub.setAttribute('value', 'Contains footage of immigration enforcement operations.\nAll identifiable faces have been blurred.\nYou may exit at any time.');
    sub.setAttribute('align', 'center');
    sub.setAttribute('color', '#AAA');
    sub.setAttribute('width', '2');
    sub.setAttribute('position', '0 -0.3 0.01');
    sub.setAttribute('font', 'monoid');
    this.el.appendChild(sub);

    const btn = document.createElement('a-plane');
    btn.setAttribute('width', '1.2');
    btn.setAttribute('height', '0.3');
    btn.setAttribute('color', '#555');
    btn.setAttribute('position', '0 -0.85 0.01');
    btn.classList.add('clickable');
    this.el.appendChild(btn);

    const btnText = document.createElement('a-text');
    btnText.setAttribute('value', 'I UNDERSTAND');
    btnText.setAttribute('align', 'center');
    btnText.setAttribute('color', '#FFF');
    btnText.setAttribute('width', '2');
    btnText.setAttribute('position', '0 -0.85 0.02');
    btnText.setAttribute('font', 'monoid');
    this.el.appendChild(btnText);

    btn.addEventListener('mouseenter', () => {
      btn.setAttribute('color', '#777');
    });
    btn.addEventListener('mouseleave', () => {
      btn.setAttribute('color', '#555');
    });

    btn.addEventListener('click', () => {
      this.el.setAttribute('visible', false);
      this.el.emit('gate-dismissed');
      console.log('[content-gate] User acknowledged content warning');
    });
  }
});
