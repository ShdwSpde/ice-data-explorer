/**
 * room-manager — Shows/hides room entities, manages transitions
 * Attach to <a-scene>. Each room is an <a-entity> with a `room` attribute.
 */
AFRAME.registerComponent('room-manager', {
  schema: {
    active: { type: 'string', default: 'hub' },
    fadeDuration: { type: 'number', default: 500 }
  },

  init: function () {
    this.rooms = {};
    this.transitioning = false;

    // Collect rooms after scene loads
    this.el.addEventListener('loaded', () => {
      this.el.querySelectorAll('[room]').forEach(el => {
        const name = el.getAttribute('room');
        this.rooms[name] = el;
        el.setAttribute('visible', name === this.data.active);
      });
      console.log('[room-manager] Rooms registered:', Object.keys(this.rooms));
    });

    // Listen for room-change events
    this.el.addEventListener('room-change', (evt) => {
      this.changeRoom(evt.detail.room);
    });
  },

  changeRoom: function (targetRoom) {
    if (this.transitioning) return;
    if (!this.rooms[targetRoom]) {
      console.warn(`[room-manager] Unknown room: ${targetRoom}`);
      return;
    }
    if (targetRoom === this.data.active) return;

    this.transitioning = true;
    const currentEl = this.rooms[this.data.active];
    const targetEl = this.rooms[targetRoom];

    // Fade out current room
    this._fadeOut(currentEl, () => {
      currentEl.setAttribute('visible', false);
      targetEl.setAttribute('visible', true);

      // Reset camera position to room spawn
      const rig = document.getElementById('rig');
      const spawn = targetEl.getAttribute('spawn') || '0 0 0';
      rig.setAttribute('position', spawn);

      // Fade in target room
      this._fadeIn(targetEl, () => {
        this.data.active = targetRoom;
        this.transitioning = false;
        this.el.emit('room-changed', { room: targetRoom });
        console.log(`[room-manager] Now in: ${targetRoom}`);
      });
    });
  },

  _fadeOut: function (el, callback) {
    // Simple visibility toggle for now; can add opacity animation later
    setTimeout(callback, this.data.fadeDuration);
  },

  _fadeIn: function (el, callback) {
    setTimeout(callback, this.data.fadeDuration);
  }
});
