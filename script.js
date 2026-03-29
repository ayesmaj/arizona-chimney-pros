'use strict';

/* ===== HEADER SCROLL ===== */
const header = document.querySelector('.header');
if (header) {
  const update = () => {
    header.classList.toggle('scrolled', window.scrollY > 30);
  };
  update();
  window.addEventListener('scroll', update, { passive: true });
}

/* ===== MOBILE NAV ===== */
const navToggle = document.getElementById('navToggle');
const navList   = document.getElementById('navList');
if (navToggle && navList) {
  navToggle.addEventListener('click', () => {
    const open = navList.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(open));
  });
  navList.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      navList.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
  document.addEventListener('click', e => {
    if (!header?.contains(e.target)) {
      navList.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

/* ===== ACTIVE NAV LINK ===== */
const currentPage = location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav__link').forEach(link => {
  const href = link.getAttribute('href');
  if (href === currentPage || (href === 'index.html' && currentPage === '')) {
    link.classList.add('active');
  }
});

/* ===== FAQ ===== */
document.querySelectorAll('.faq-item__q').forEach(btn => {
  btn.addEventListener('click', () => {
    const item     = btn.closest('.faq-item');
    const isOpen   = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

/* ===== BEFORE/AFTER SLIDER ===== */
document.querySelectorAll('.ba-slider').forEach(slider => {
  const after  = slider.querySelector('.ba-after');
  const handle = slider.querySelector('.ba-handle');
  const line   = slider.querySelector('.ba-line');
  if (!after) return;

  let dragging = false;
  let pct = 50;

  const setPos = (x) => {
    const rect = slider.getBoundingClientRect();
    pct = Math.min(100, Math.max(0, ((x - rect.left) / rect.width) * 100));
    after.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
    if (handle) handle.style.left = `${pct}%`;
    if (line)   line.style.left   = `${pct}%`;
  };

  // Init
  after.style.clipPath = 'inset(0 50% 0 0)';

  // Mouse
  slider.addEventListener('mousedown', e => { dragging = true; setPos(e.clientX); });
  window.addEventListener('mousemove', e => { if (dragging) setPos(e.clientX); });
  window.addEventListener('mouseup',   () => { dragging = false; });

  // Touch
  slider.addEventListener('touchstart', e => { dragging = true; setPos(e.touches[0].clientX); }, { passive: true });
  window.addEventListener('touchmove',  e => { if (dragging) setPos(e.touches[0].clientX); }, { passive: true });
  window.addEventListener('touchend',   () => { dragging = false; });
});

/* ===== SCROLL ANIMATIONS ===== */
const animObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      animObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.anim').forEach(el => animObserver.observe(el));

/* ===== COUNTER ANIMATION ===== */
const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    const el   = entry.target;
    const text = el.textContent.trim();
    const num  = text.match(/[\d,]+/);
    if (!num) return;
    const target = parseInt(num[0].replace(/,/g, ''), 10);
    const suffix = text.replace(num[0], '');
    const dur  = 1400;
    const start = performance.now();
    const tick = now => {
      const t = Math.min((now - start) / dur, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(target * ease).toLocaleString() + suffix;
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    counterObserver.unobserve(el);
  });
}, { threshold: 0.5 });

document.querySelectorAll('.why-stat__number').forEach(el => counterObserver.observe(el));

/* ===== EMBER PARTICLES ===== */
const emberContainer = document.querySelector('.hero__embers');
if (emberContainer) {
  const count = 22;
  for (let i = 0; i < count; i++) {
    const e = document.createElement('div');
    e.className = 'ember';
    const size = Math.random() * 4 + 2;
    const x    = Math.random() * 100;
    const dur  = Math.random() * 8 + 6;
    const del  = Math.random() * 10;
    const drift= (Math.random() - .5) * 100;
    const col  = Math.random() > .5 ? '#FF6A1A' : '#C9A86A';
    Object.assign(e.style, {
      width:  size + 'px',
      height: size + 'px',
      left:   x + '%',
      bottom: '-20px',
      background: col,
      boxShadow:  `0 0 ${size * 2}px ${col}`,
      animationDuration:  dur + 's',
      animationDelay:     del + 's',
      '--drift':          drift + 'px',
    });
    emberContainer.appendChild(e);
  }
}

/* ===== CONTACT FORM ===== */
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = contactForm.querySelector('.form-submit');
    const orig = btn.textContent;
    btn.textContent = 'Sending…';
    btn.disabled = true;
    await new Promise(r => setTimeout(r, 1200));
    const success = contactForm.querySelector('.form-success');
    contactForm.querySelector('.form-fields').style.display = 'none';
    if (success) success.style.display = 'block';
  });
}

/* ===== SMOOTH SCROLL FOR HASH LINKS ===== */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

/* ═══════════════════════════════════════════════
   INTERACTIVE FIREPLACE EXPLORER
═══════════════════════════════════════════════ */
(function () {
  const explorer = document.getElementById('explorer');
  if (!explorer) return;

  const fpImg   = document.getElementById('fpImg');
  const fpLabel = document.getElementById('fpLabel');
  const fpDesc  = document.getElementById('fpDesc');
  const cats    = explorer.querySelectorAll('.fp-cat');

  // Preload all images for instant switching
  const allImgs = explorer.querySelectorAll('.fp-style[data-img]');
  allImgs.forEach(btn => {
    const pre = new Image();
    pre.src = btn.dataset.img;
  });

  // Swap main image with smooth fade
  function swapImage(src, label, desc) {
    fpImg.classList.add('fp-fade');
    fpDesc.classList.add('fp-fade-text');
    setTimeout(() => {
      fpImg.src = src;
      fpLabel.textContent = label;
      fpImg.classList.remove('fp-fade');
      fpDesc.textContent = desc;
      fpDesc.classList.remove('fp-fade-text');
    }, 320);
  }

  // Subtle parallax on mouse move over display frame
  const frame = document.getElementById('fpFrame');
  if (frame) {
    frame.addEventListener('mousemove', e => {
      const rect = frame.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width  - 0.5) * 8;
      const y = ((e.clientY - rect.top)  / rect.height - 0.5) * 8;
      fpImg.style.transform = `scale(1.05) translate(${x}px, ${y}px)`;
    });
    frame.addEventListener('mouseleave', () => {
      fpImg.style.transform = '';
    });
  }

  // Category click — open/close accordion + load default style
  cats.forEach(cat => {
    const header  = cat.querySelector('.fp-cat__header');
    const styles  = cat.querySelectorAll('.fp-style');

    header.addEventListener('click', () => {
      const isActive = cat.classList.contains('fp-cat--active');

      // Close all
      cats.forEach(c => c.classList.remove('fp-cat--active'));
      explorer.querySelectorAll('.fp-style').forEach(s => s.classList.remove('fp-style--active'));

      if (!isActive) {
        cat.classList.add('fp-cat--active');
        // Activate first style of this category
        if (styles.length) {
          styles[0].classList.add('fp-style--active');
          swapImage(styles[0].dataset.img, styles[0].dataset.label, styles[0].dataset.desc);
        }
      }
    });

    // Style pill click
    styles.forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        // Make sure this category is open
        cats.forEach(c => c.classList.remove('fp-cat--active'));
        explorer.querySelectorAll('.fp-style').forEach(s => s.classList.remove('fp-style--active'));
        cat.classList.add('fp-cat--active');
        btn.classList.add('fp-style--active');
        swapImage(btn.dataset.img, btn.dataset.label, btn.dataset.desc);
      });
    });
  });
})();
