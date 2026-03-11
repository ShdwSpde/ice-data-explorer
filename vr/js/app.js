/**
 * ICE Data Explorer — VR Experience
 * Main application entry point
 */

document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  // --- Letterbox bars (desktop only) ---
  const letterboxTop = document.createElement('div');
  letterboxTop.className = 'letterbox-top';
  document.body.appendChild(letterboxTop);

  const letterboxBottom = document.createElement('div');
  letterboxBottom.className = 'letterbox-bottom';
  document.body.appendChild(letterboxBottom);

  // --- Watchtower loading sequence ---
  const loadingScreen = document.getElementById('loading-screen');
  const hudHint = document.getElementById('hud-hint');

  function runWatchtowerSequence() {
    // Hold Watchtower card for 2.5s, fade out over 0.5s
    setTimeout(() => {
      loadingScreen.classList.add('fade-out');
      setTimeout(() => {
        loadingScreen.style.display = 'none';
      }, 500);
    }, 2500);

    // Show walk-forward hint after flash clears (3s), fade it after 4s
    setTimeout(() => {
      if (hudHint) hudHint.style.opacity = '1';
      setTimeout(() => {
        if (hudHint) hudHint.style.opacity = '0';
      }, 4000);
    }, 3000);
  }

  const sceneEl = document.querySelector('a-scene');
  if (sceneEl.hasLoaded) {
    runWatchtowerSequence();
  } else {
    sceneEl.addEventListener('loaded', runWatchtowerSequence, { once: true });
  }

  // Hide overlay elements when entering VR
  scene.addEventListener('enter-vr', () => {
    letterboxTop.style.display = 'none';
    letterboxBottom.style.display = 'none';
  });

  scene.addEventListener('exit-vr', () => {
    letterboxTop.style.display = '';
    letterboxBottom.style.display = '';
  });

  console.log('[VR] ICE Data Explorer VR Experience initialized');
});
