/**
 * ICE Data Explorer - Wow Factor Features JavaScript
 * Handles: Animated counters, scrollytelling, sound design, sharing, themes
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('[WOW] DOMContentLoaded - initializing features');
    try {
        initAnimatedCounters();
        console.log('[WOW] Animated counters initialized');
    } catch(e) { console.error('[WOW] Counter error:', e); }

    try {
        initScrollytelling();
        console.log('[WOW] Scrollytelling initialized');
    } catch(e) { console.error('[WOW] Scrollytelling error:', e); }

    try {
        initThemeToggle();
        console.log('[WOW] Theme toggle initialized');
    } catch(e) { console.error('[WOW] Theme error:', e); }

    try {
        initSoundDesign();
        console.log('[WOW] Sound design initialized');
    } catch(e) { console.error('[WOW] Sound error:', e); }

    try {
        initShareCards();
        console.log('[WOW] Share cards initialized');
    } catch(e) { console.error('[WOW] Share cards error:', e); }
});

// ============================================
// 1. ANIMATED COUNTER INTRO
// ============================================

function initAnimatedCounters() {
    // Observe stat cards for animation trigger
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const card = entry.target;
                card.classList.add('animate-in');

                // Animate the counter value
                const valueEl = card.querySelector('.stat-value');
                if (valueEl) {
                    animateCounter(valueEl);
                }

                observer.unobserve(card);
            }
        });
    }, { threshold: 0.2 });

    // Re-run when new content is loaded (Dash callback)
    const watchForStatCards = () => {
        document.querySelectorAll('.stat-card:not(.observed)').forEach(card => {
            card.classList.add('observed');
            observer.observe(card);
        });
    };

    // Initial run and mutation observer for Dash updates
    watchForStatCards();

    const mutationObserver = new MutationObserver(watchForStatCards);
    mutationObserver.observe(document.body, { childList: true, subtree: true });
}

function animateCounter(element) {
    const text = element.textContent;
    const match = text.match(/[\d,]+\.?\d*/);

    if (!match) return;

    const numStr = match[0].replace(/,/g, '');
    const targetNum = parseFloat(numStr);
    const prefix = text.substring(0, text.indexOf(match[0]));
    const suffix = text.substring(text.indexOf(match[0]) + match[0].length);
    const hasDecimal = numStr.includes('.');
    const decimalPlaces = hasDecimal ? numStr.split('.')[1].length : 0;

    let current = 0;
    const duration = 1500;
    const startTime = performance.now();

    element.classList.add('counting');

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        current = targetNum * easeOut;

        let displayNum;
        if (hasDecimal) {
            displayNum = current.toFixed(decimalPlaces);
        } else {
            displayNum = Math.floor(current).toLocaleString();
        }

        element.textContent = prefix + displayNum + suffix;

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = text; // Restore original formatting
            element.classList.remove('counting');
        }
    }

    requestAnimationFrame(update);
}

// ============================================
// 6. SCROLLYTELLING MODE
// ============================================

let scrollytellingEnabled = false;

function initScrollytelling() {
    console.log('[WOW] initScrollytelling starting...');

    // Create toggle button if it doesn't exist
    if (!document.querySelector('.scrollytelling-toggle')) {
        console.log('[WOW] Creating toggle button...');
        const toggle = document.createElement('button');
        toggle.className = 'scrollytelling-toggle';
        toggle.innerHTML = '📖 Story Mode';
        toggle.onclick = toggleScrollytelling;
        document.body.appendChild(toggle);
        console.log('[WOW] Toggle button appended to body');
    } else {
        console.log('[WOW] Toggle button already exists');
    }

    // Create progress bar
    if (!document.querySelector('.scroll-progress')) {
        const progress = document.createElement('div');
        progress.className = 'scroll-progress';
        progress.style.width = '0%';
        document.body.appendChild(progress);
        console.log('[WOW] Progress bar created');
    }

    // Update progress on scroll
    window.addEventListener('scroll', updateScrollProgress);

    // Observe story sections
    observeStorySections();
    console.log('[WOW] initScrollytelling complete');
}

function toggleScrollytelling() {
    scrollytellingEnabled = !scrollytellingEnabled;
    const toggle = document.querySelector('.scrollytelling-toggle');

    if (scrollytellingEnabled) {
        toggle.innerHTML = '✕ Exit Story';
        toggle.style.background = 'var(--danger)';
        document.body.classList.add('scrollytelling-active');

        // Smooth scroll to first section
        const firstSection = document.querySelector('.story-section');
        if (firstSection) {
            firstSection.scrollIntoView({ behavior: 'smooth' });
        }
    } else {
        toggle.innerHTML = '📖 Story Mode';
        toggle.style.background = 'var(--accent)';
        document.body.classList.remove('scrollytelling-active');
    }
}

function updateScrollProgress() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = (scrollTop / docHeight) * 100;

    const progressBar = document.querySelector('.scroll-progress');
    if (progressBar) {
        progressBar.style.width = progress + '%';
    }
}

// Intersection observer for story sections (reused)
let storyObserver = null;

function observeStorySections() {
    // Create observer once
    if (!storyObserver) {
        storyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');

                    // Play ambient sound if enabled
                    if (window.soundEnabled) {
                        const sectionType = entry.target.dataset.sectionType;
                        playAmbientSound(sectionType);
                    }
                }
            });
        }, { threshold: 0.3 });
    }

    // Watch for new story sections (handles Dash dynamic content)
    const watchForStorySections = () => {
        const sections = document.querySelectorAll('.story-section:not(.story-observed)');
        if (sections.length > 0) {
            console.log('[WOW] Found', sections.length, 'new story sections');
        }
        sections.forEach(section => {
            section.classList.add('story-observed');
            storyObserver.observe(section);
        });
    };

    // Initial run
    watchForStorySections();

    // MutationObserver for Dash dynamic content updates
    const mutationObserver = new MutationObserver(watchForStorySections);
    mutationObserver.observe(document.body, { childList: true, subtree: true });
}

// ============================================
// 7. SOUND DESIGN
// ============================================

window.soundEnabled = false;
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

function initSoundDesign() {
    // Create sound toggle button
    if (!document.querySelector('.sound-toggle')) {
        const toggle = document.createElement('button');
        toggle.className = 'sound-toggle muted';
        toggle.innerHTML = '<span class="sound-icon">🔇</span>';
        toggle.onclick = toggleSound;
        toggle.title = 'Toggle sound effects';
        document.body.appendChild(toggle);
    }
}

function toggleSound() {
    window.soundEnabled = !window.soundEnabled;
    const toggle = document.querySelector('.sound-toggle');

    if (window.soundEnabled) {
        toggle.classList.remove('muted');
        toggle.querySelector('.sound-icon').textContent = '🔊';
        audioContext.resume();
        playTone(440, 0.1, 'sine'); // Feedback tone
    } else {
        toggle.classList.add('muted');
        toggle.querySelector('.sound-icon').textContent = '🔇';
    }
}

function playTone(frequency, duration, type = 'sine') {
    if (!window.soundEnabled) return;

    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);

    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration);
}

function playAmbientSound(type) {
    if (!window.soundEnabled) return;

    switch(type) {
        case 'deaths':
            // Low, somber tone
            playTone(110, 2, 'sine');
            setTimeout(() => playTone(98, 1.5, 'sine'), 500);
            break;
        case 'budget':
            // Rising tone for money
            playTone(330, 0.3, 'triangle');
            setTimeout(() => playTone(440, 0.3, 'triangle'), 150);
            setTimeout(() => playTone(550, 0.4, 'triangle'), 300);
            break;
        case 'detention':
            // Confined, metallic sound
            playTone(220, 0.5, 'sawtooth');
            break;
        default:
            // Subtle notification
            playTone(523, 0.15, 'sine');
    }
}

// Expose for Dash callbacks
window.playDataSound = playAmbientSound;

// ============================================
// 8. SHAREABLE DATA CARDS
// ============================================

function initShareCards() {
    // Add share buttons to stat cards on hover
    const addShareButtons = () => {
        document.querySelectorAll('.stat-card:not(.share-enabled)').forEach(card => {
            card.classList.add('share-enabled', 'share-card-container');

            const shareBtn = document.createElement('button');
            shareBtn.className = 'share-button';
            shareBtn.innerHTML = '↗';
            shareBtn.onclick = (e) => {
                e.stopPropagation();
                showShareModal(card);
            };

            card.appendChild(shareBtn);
        });
    };

    addShareButtons();

    // Watch for new cards
    const observer = new MutationObserver(addShareButtons);
    observer.observe(document.body, { childList: true, subtree: true });
}

function showShareModal(card) {
    const value = card.querySelector('.stat-value')?.textContent || '';
    const label = card.querySelector('.stat-label')?.textContent || '';
    const subtext = card.querySelector('.stat-subtext')?.textContent || '';

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'share-modal';
    modal.innerHTML = `
        <div class="share-modal-content">
            <h3 style="margin-bottom: 20px; color: var(--text);">Share This Statistic</h3>
            <div class="share-preview">
                <div class="share-preview-stat">${value}</div>
                <div class="share-preview-label">${label}</div>
                <div class="share-preview-source">Source: ICE Data Explorer | ice-data.info</div>
            </div>
            <div class="share-buttons">
                <button class="share-btn twitter" onclick="shareToTwitter('${value}', '${label}')">
                    𝕏 Twitter
                </button>
                <button class="share-btn copy" onclick="copyToClipboard('${value} - ${label}\\n\\nSource: ICE Data Explorer')">
                    📋 Copy
                </button>
                <button class="share-btn download" onclick="downloadCard(this)">
                    📥 Download
                </button>
            </div>
            <button onclick="closeShareModal()" style="margin-top: 20px; background: transparent; border: 1px solid var(--grid); color: var(--text-muted); padding: 8px 20px; border-radius: 6px; cursor: pointer;">
                Close
            </button>
        </div>
    `;

    document.body.appendChild(modal);

    // Animate in
    requestAnimationFrame(() => {
        modal.classList.add('active');
    });

    // Close on backdrop click
    modal.onclick = (e) => {
        if (e.target === modal) closeShareModal();
    };
}

function closeShareModal() {
    const modal = document.querySelector('.share-modal');
    if (modal) {
        modal.classList.remove('active');
        setTimeout(() => modal.remove(), 300);
    }
}

function shareToTwitter(value, label) {
    const text = encodeURIComponent(`${value} - ${label}\n\nData from ICE Data Explorer`);
    window.open(`https://twitter.com/intent/tweet?text=${text}`, '_blank');
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '✓ Copied!';
        setTimeout(() => btn.innerHTML = originalText, 2000);
    });
}

function downloadCard(btn) {
    const preview = btn.closest('.share-modal-content').querySelector('.share-preview');

    // Use html2canvas if available, otherwise show instructions
    if (typeof html2canvas !== 'undefined') {
        html2canvas(preview).then(canvas => {
            const link = document.createElement('a');
            link.download = 'ice-data-stat.png';
            link.href = canvas.toDataURL();
            link.click();
        });
    } else {
        alert('Take a screenshot of the preview above to save the image.');
    }
}

// ============================================
// 10. THEME TOGGLE
// ============================================

function initThemeToggle() {
    // Create theme toggle container
    if (!document.querySelector('.theme-toggle-container')) {
        const container = document.createElement('div');
        container.className = 'theme-toggle-container';
        container.innerHTML = `
            <button class="theme-btn active" data-theme="dark" title="Dark Mode">🌙</button>
            <button class="theme-btn" data-theme="light" title="Light Mode">☀️</button>
            <button class="theme-btn" data-theme="reality" title="Reality Mode">👁</button>
        `;
        document.body.appendChild(container);

        // Add click handlers
        container.querySelectorAll('.theme-btn').forEach(btn => {
            btn.onclick = () => setTheme(btn.dataset.theme);
        });
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('iceDataTheme') || 'dark';
    setTheme(savedTheme);
}

function setTheme(theme) {
    // Remove all theme classes
    document.body.classList.remove('theme-dark', 'theme-light', 'theme-reality');

    // Add new theme class
    if (theme !== 'dark') {
        document.body.classList.add('theme-' + theme);
    }

    // Update active button
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === theme);
    });

    // Play sound feedback
    if (window.soundEnabled) {
        if (theme === 'reality') {
            playTone(220, 0.5, 'sine');
        } else {
            playTone(440, 0.15, 'sine');
        }
    }

    // Save preference
    localStorage.setItem('iceDataTheme', theme);
}

// ============================================
// UTILITY: Flight Tracker Animation
// ============================================

function animateFlightPaths() {
    const paths = document.querySelectorAll('.flight-path');
    paths.forEach((path, index) => {
        path.style.animationDelay = (index * 0.5) + 's';
    });
}

// ============================================
// UTILITY: Intersection Observer for Charts
// ============================================

function initChartAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('chart-visible');

                // Trigger sound for certain chart types
                if (window.soundEnabled) {
                    const chartType = entry.target.dataset.chartType;
                    if (chartType === 'deaths') {
                        playAmbientSound('deaths');
                    }
                }
            }
        });
    }, { threshold: 0.2 });

    document.querySelectorAll('.js-plotly-plot').forEach(chart => {
        observer.observe(chart);
    });
}

// Re-initialize on Dash page updates
if (typeof window.dash_clientside === 'undefined') {
    window.dash_clientside = {};
}

window.dash_clientside.wow_features = {
    init: function() {
        setTimeout(() => {
            initAnimatedCounters();
            initChartAnimations();
            animateFlightPaths();
            initVisualMetaphors();
        }, 100);
        return window.dash_clientside.no_update;
    }
};

// ============================================
// VISUAL METAPHOR SYSTEM
// Project Watchtower - Investigative Visualization
// ============================================

function initVisualMetaphors() {
    initRedactionReveals();
    initFlashlightEffect();
    initSonarPings();
    initParticleFlows();
    initMemorialScroll();
    initWaffleCharts();
}

// ============================================
// 1. REDACTION REVEAL SYSTEM
// Reveals hidden/suppressed information on interaction
// ============================================

function initRedactionReveals() {
    // Handle individual redaction bars
    document.querySelectorAll('.redaction-bar:not(.initialized)').forEach(bar => {
        bar.classList.add('initialized');

        bar.addEventListener('click', function() {
            this.classList.toggle('revealed');

            // Play reveal sound
            if (window.soundEnabled) {
                playRevealSound();
            }

            // Track reveal for analytics
            trackReveal(this.dataset.revealId);
        });
    });

    // Handle redaction overlays (full document reveal)
    document.querySelectorAll('.redaction-overlay:not(.initialized)').forEach(overlay => {
        overlay.classList.add('initialized');
        const container = overlay.parentElement;

        container.addEventListener('click', function() {
            overlay.classList.add('revealing');

            if (window.soundEnabled) {
                playRevealSound();
            }
        });
    });

    // Landing page lens reveal effect
    initLensReveal();
}

function initLensReveal() {
    const lensContainers = document.querySelectorAll('.lens-reveal-container');

    lensContainers.forEach(container => {
        const overlay = container.querySelector('.lens-overlay');
        if (!overlay) return;

        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 100;
            const y = ((e.clientY - rect.top) / rect.height) * 100;

            overlay.style.setProperty('--lens-x', `${x}%`);
            overlay.style.setProperty('--lens-y', `${y}%`);
        });

        container.addEventListener('mouseleave', () => {
            overlay.style.setProperty('--lens-x', '50%');
            overlay.style.setProperty('--lens-y', '50%');
        });
    });
}

function playRevealSound() {
    // Typewriter-style reveal sound
    playTone(800, 0.05, 'square');
    setTimeout(() => playTone(1000, 0.05, 'square'), 50);
    setTimeout(() => playTone(1200, 0.08, 'sine'), 100);
}

function trackReveal(revealId) {
    // Track which data points users are revealing
    if (window.gtag) {
        gtag('event', 'data_reveal', {
            'reveal_id': revealId
        });
    }
}

// ============================================
// 2. FLASHLIGHT/BLUR WALL EFFECT
// Cursor-based transparency for archive reveals
// ============================================

function initFlashlightEffect() {
    const containers = document.querySelectorAll('.flashlight-container:not(.initialized)');

    containers.forEach(container => {
        container.classList.add('initialized');
        const mask = container.querySelector('.flashlight-mask');

        if (!mask) {
            // Create mask if it doesn't exist
            const newMask = document.createElement('div');
            newMask.className = 'flashlight-mask';
            container.appendChild(newMask);
        }

        container.addEventListener('mousemove', (e) => {
            const rect = container.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const maskEl = container.querySelector('.flashlight-mask');
            maskEl.style.setProperty('--mouse-x', `${x}px`);
            maskEl.style.setProperty('--mouse-y', `${y}px`);
        });
    });

    // Blur wall items - focus on hover
    document.querySelectorAll('.blur-wall-item:not(.initialized)').forEach(item => {
        item.classList.add('initialized');

        item.addEventListener('mouseenter', function() {
            // Unfocus siblings
            this.parentElement.querySelectorAll('.blur-wall-item').forEach(sibling => {
                if (sibling !== this) {
                    sibling.classList.add('unfocused');
                }
            });
            this.classList.add('focused');
        });

        item.addEventListener('mouseleave', function() {
            this.parentElement.querySelectorAll('.blur-wall-item').forEach(sibling => {
                sibling.classList.remove('unfocused', 'focused');
            });
        });
    });
}

// ============================================
// 3. SONAR PING EFFECT
// For showing surveillance activity
// ============================================

function initSonarPings() {
    const pingNodes = document.querySelectorAll('.sonar-node:not(.initialized)');

    pingNodes.forEach(node => {
        node.classList.add('initialized');
        createSonarPings(node);
    });
}

function createSonarPings(node) {
    const interval = parseInt(node.dataset.pingInterval) || 2000;
    const maxPings = parseInt(node.dataset.maxPings) || 3;

    setInterval(() => {
        if (document.hidden) return; // Don't animate if tab not visible

        const ping = document.createElement('div');
        ping.className = 'sonar-ping';
        node.appendChild(ping);

        // Remove ping after animation completes
        setTimeout(() => ping.remove(), 2000);

        // Limit concurrent pings
        const pings = node.querySelectorAll('.sonar-ping');
        if (pings.length > maxPings) {
            pings[0].remove();
        }
    }, interval);
}

// Add sonar effect to map markers dynamically
function addSonarToMarker(markerElement, intensity = 'normal') {
    markerElement.classList.add('sonar-node');

    const intervals = {
        'high': 1000,
        'normal': 2000,
        'low': 4000
    };

    markerElement.dataset.pingInterval = intervals[intensity] || 2000;
    createSonarPings(markerElement);
}

// ============================================
// 4. PARTICLE FLOW SYSTEM
// For deportation/logistics visualizations
// ============================================

function initParticleFlows() {
    const flowContainers = document.querySelectorAll('.particle-flow-container:not(.initialized)');

    flowContainers.forEach(container => {
        container.classList.add('initialized');
        startParticleFlow(container);
    });
}

function startParticleFlow(container) {
    const pathElement = container.querySelector('.flow-path');
    if (!pathElement) return;

    const particleCount = parseInt(container.dataset.particleCount) || 20;
    const duration = parseInt(container.dataset.flowDuration) || 3000;
    const color = container.dataset.particleColor || 'var(--accent)';

    for (let i = 0; i < particleCount; i++) {
        createFlowParticle(container, pathElement, duration, color, i * (duration / particleCount));
    }
}

function createFlowParticle(container, pathElement, duration, color, delay) {
    const particle = document.createElement('div');
    particle.className = 'flow-particle';
    particle.style.cssText = `
        position: absolute;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: ${color};
        box-shadow: 0 0 8px ${color};
        offset-path: path('${pathElement.getAttribute('d')}');
        offset-rotate: 0deg;
        animation: particle-move ${duration}ms linear infinite;
        animation-delay: ${delay}ms;
    `;

    container.appendChild(particle);
}

// Create animated flow between two points (for map)
function createFlowLine(container, startX, startY, endX, endY, options = {}) {
    const {
        color = 'var(--accent)',
        particleCount = 10,
        duration = 2000,
        curve = 0.3
    } = options;

    // Calculate control point for bezier curve
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2 - (Math.abs(endX - startX) * curve);

    const pathD = `M ${startX} ${startY} Q ${midX} ${midY} ${endX} ${endY}`;

    // Create SVG path
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.cssText = 'position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;';

    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', pathD);
    path.setAttribute('class', 'flow-line');
    path.setAttribute('stroke', color);

    svg.appendChild(path);
    container.appendChild(svg);

    // Create particles along path
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle-trail';
        particle.style.cssText = `
            offset-path: path('${pathD}');
            --particle-duration: ${duration}ms;
            animation-delay: ${i * (duration / particleCount)}ms;
            background: ${color};
        `;
        container.appendChild(particle);
    }
}

// ============================================
// 5. INFINITE SCROLL MEMORIAL
// For deaths in custody visualization
// ============================================

function initMemorialScroll() {
    const memorialContainer = document.querySelector('.memorial-container');
    if (!memorialContainer) return;

    const entries = memorialContainer.querySelectorAll('.memorial-entry');
    const counter = document.querySelector('.memorial-counter-number');
    let visibleCount = 0;

    const observer = new IntersectionObserver((observedEntries) => {
        observedEntries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                visibleCount++;

                // Update counter
                if (counter) {
                    counter.textContent = visibleCount.toLocaleString();
                }

                // Known names pause effect
                if (entry.target.classList.contains('known-name')) {
                    // Subtle pause effect - slow scroll
                    document.body.style.scrollBehavior = 'auto';
                    setTimeout(() => {
                        document.body.style.scrollBehavior = 'smooth';
                    }, 500);

                    // Play somber tone
                    if (window.soundEnabled) {
                        playMemorialTone();
                    }
                }

                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.5,
        rootMargin: '0px 0px -20% 0px'
    });

    entries.forEach(entry => observer.observe(entry));
}

function playMemorialTone() {
    // Low, somber tone for each death
    const audioCtx = window.audioContext || new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(110, audioCtx.currentTime); // Low A

    gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.5);

    oscillator.start(audioCtx.currentTime);
    oscillator.stop(audioCtx.currentTime + 1.5);
}

// ============================================
// 6. WAFFLE CHART REVEAL
// For demographic myth-busting
// ============================================

function initWaffleCharts() {
    const waffleContainers = document.querySelectorAll('.waffle-container:not(.initialized)');

    waffleContainers.forEach(container => {
        container.classList.add('initialized');

        const revealBtn = container.querySelector('.waffle-reveal-btn');
        const grid = container.querySelector('.waffle-grid');

        if (revealBtn && grid) {
            revealBtn.addEventListener('click', () => {
                revealWaffleChart(grid);
                revealBtn.disabled = true;
                revealBtn.textContent = 'Reality Revealed';
            });
        }
    });
}

function revealWaffleChart(grid, options = {}) {
    const {
        revealPercentage = 73, // Default: 73% have no criminal conviction
        revealClass = 'no-conviction',
        otherClass = 'conviction',
        staggerDelay = 5
    } = options;

    const cells = Array.from(grid.querySelectorAll('.waffle-cell'));
    const revealCount = Math.floor(cells.length * (revealPercentage / 100));

    // Shuffle cells for random reveal pattern
    const shuffled = cells.sort(() => Math.random() - 0.5);

    // Reveal cells with staggered animation
    shuffled.forEach((cell, index) => {
        setTimeout(() => {
            cell.classList.add('revealed');

            if (index < revealCount) {
                cell.classList.add(revealClass);
            } else {
                cell.classList.add(otherClass);
            }

            // Play subtle tick sound
            if (window.soundEnabled && index % 10 === 0) {
                playTone(600 + (index % 100) * 2, 0.02, 'sine');
            }
        }, index * staggerDelay);
    });

    // Final reveal sound
    setTimeout(() => {
        if (window.soundEnabled) {
            playTone(880, 0.3, 'sine');
        }
    }, cells.length * staggerDelay + 200);
}

// ============================================
// 7. SLOT MACHINE ANIMATION
// For lobbying ROI visualization
// ============================================

function initSlotMachine(container) {
    const input = container.querySelector('.slot-input');
    const output = container.querySelector('.slot-output');
    const roi = container.querySelector('.slot-roi');
    const leverBtn = container.querySelector('.slot-lever-btn');

    if (!leverBtn) return;

    leverBtn.addEventListener('click', () => {
        spinSlotMachine(container, input, output, roi);
    });
}

function spinSlotMachine(container, inputEl, outputEl, roiEl) {
    const lobbyingSpend = parseFloat(inputEl.dataset.value) || 1000000;
    const contractAward = parseFloat(outputEl.dataset.value) || 50000000;
    const roiValue = ((contractAward / lobbyingSpend) * 100).toFixed(0);

    // Start spinning
    inputEl.classList.add('spinning');
    outputEl.classList.add('spinning');

    // Play slot machine sounds
    if (window.soundEnabled) {
        playSlotSound();
    }

    // Reveal input
    setTimeout(() => {
        inputEl.classList.remove('spinning');
        inputEl.textContent = '$' + lobbyingSpend.toLocaleString();
    }, 1000);

    // Reveal output (bigger number, more dramatic)
    setTimeout(() => {
        outputEl.classList.remove('spinning');
        animateSlotValue(outputEl, contractAward);
    }, 2000);

    // Reveal ROI with neon effect
    setTimeout(() => {
        roiEl.textContent = roiValue + '%';
        roiEl.classList.add('revealed');

        if (window.soundEnabled) {
            // Jackpot sound
            playTone(523, 0.2, 'sine');
            setTimeout(() => playTone(659, 0.2, 'sine'), 100);
            setTimeout(() => playTone(784, 0.3, 'sine'), 200);
        }
    }, 3000);
}

function animateSlotValue(element, targetValue) {
    let current = 0;
    const duration = 1000;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);

        current = targetValue * easeOut;
        element.textContent = '$' + Math.floor(current).toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

function playSlotSound() {
    // Slot machine spinning sound
    let freq = 200;
    const interval = setInterval(() => {
        playTone(freq, 0.05, 'square');
        freq += 20;
        if (freq > 600) {
            clearInterval(interval);
        }
    }, 50);
}

// ============================================
// 8. DISCREPANCY SPLIT VIEW
// For contested data visualization
// ============================================

function createDiscrepancySplit(container, officialData, independentData) {
    container.innerHTML = `
        <div class="discrepancy-split">
            <div class="discrepancy-side discrepancy-official">
                <div class="discrepancy-label">🏛️ Official Government Figure</div>
                <div class="discrepancy-value" data-value="${officialData.value}">${officialData.display}</div>
                <div class="discrepancy-source">${officialData.source}</div>
                <div class="discrepancy-divider">VS</div>
            </div>
            <div class="discrepancy-side discrepancy-independent">
                <div class="discrepancy-label">✅ Independent Verification</div>
                <div class="discrepancy-value" data-value="${independentData.value}">${independentData.display}</div>
                <div class="discrepancy-source">${independentData.source}</div>
            </div>
            <div class="discrepancy-explanation">
                <strong>Why the difference?</strong> ${independentData.explanation || 'Methodological differences between official and independent counts.'}
            </div>
        </div>
    `;

    // Animate values
    const values = container.querySelectorAll('.discrepancy-value');
    values.forEach(el => animateCounter(el));
}

// ============================================
// EXPORT FOR DASH CALLBACKS
// ============================================

window.WatchtowerVisuals = {
    initRedactionReveals,
    initFlashlightEffect,
    initSonarPings,
    addSonarToMarker,
    createFlowLine,
    revealWaffleChart,
    initSlotMachine,
    createDiscrepancySplit,
    playRevealSound,
    playMemorialTone
};
