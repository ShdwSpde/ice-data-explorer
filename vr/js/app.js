/**
 * ICE Data Explorer — VR Experience
 * Main application entry point
 */

document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  // --- Create HTML overlay elements ---

  // Back button
  const backBtn = document.createElement('button');
  backBtn.id = 'back-to-hub';
  backBtn.textContent = '\u2190 Back to Hub';
  document.body.appendChild(backBtn);

  backBtn.addEventListener('click', () => {
    scene.emit('room-change', { room: 'hub' });
  });

  // Room label
  const roomLabel = document.createElement('div');
  roomLabel.id = 'room-label';
  document.body.appendChild(roomLabel);

  // Navigation hint
  const navHint = document.createElement('div');
  navHint.id = 'nav-hint';
  navHint.textContent = 'WASD to move \u2022 Mouse to look \u2022 Click portals to navigate';
  document.body.appendChild(navHint);

  const ROOM_NAMES = {
    hub: 'HUB',
    landscape: 'DATA LANDSCAPE',
    timeline: 'TIMELINE WALK',
    globe: 'SECURITY FEED',
    footage: 'RAID FOOTAGE'
  };

  // Update overlay on room change
  scene.addEventListener('room-changed', (evt) => {
    const room = evt.detail.room;
    const isHub = room === 'hub';

    // Show/hide back button
    backBtn.classList.toggle('visible', !isHub);

    // Show/hide room label
    if (!isHub) {
      roomLabel.textContent = ROOM_NAMES[room] || room.toUpperCase();
      roomLabel.classList.add('visible');
    } else {
      roomLabel.classList.remove('visible');
    }
  });

  // Hide overlay elements when entering VR
  scene.addEventListener('enter-vr', () => {
    backBtn.style.display = 'none';
    roomLabel.style.display = 'none';
    navHint.style.display = 'none';
  });

  scene.addEventListener('exit-vr', () => {
    backBtn.style.display = '';
    roomLabel.style.display = '';
    navHint.style.display = '';
  });

  console.log('[VR] ICE Data Explorer VR Experience initialized');
});
