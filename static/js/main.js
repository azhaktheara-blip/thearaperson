(() => {
  'use strict';
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const root = document.documentElement;
  const themeButton = $('.theme-toggle');
  const syncTheme = () => {
    const dark = root.dataset.theme === 'dark';
    themeButton?.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} mode`);
    if (themeButton) themeButton.innerHTML = `<i class="ph ph-${dark ? 'sun' : 'moon'}" aria-hidden="true"></i>`;
    $('meta[name="theme-color"]')?.setAttribute('content', dark ? '#191c18' : '#eeeee8');
  };
  themeButton?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('portfolio-theme', root.dataset.theme); } catch (_) {}
    syncTheme();
  });
  syncTheme();

  // Progressive enhancement: every page and navigation link works without these CDNs.
  let lenis;
  if (!reduced && window.Lenis) {
    lenis = new Lenis({ duration: 1.05, smoothWheel: true, syncTouch: false });
    if (window.gsap) {
      gsap.ticker.add(time => lenis.raf(time * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const raf = time => { lenis.raf(time); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
    if (window.ScrollTrigger) lenis.on('scroll', ScrollTrigger.update);
  }
  $$('a[href^="#"]').forEach(link => link.addEventListener('click', event => {
    const id = link.getAttribute('href');
    const target = id === '#' ? document.body : document.getElementById(id.slice(1));
    if (!target) return;
    event.preventDefault();
    if (lenis) lenis.scrollTo(target);
    else target.scrollIntoView({ behavior: reduced ? 'instant' : 'smooth' });
    if (id !== '#') history.replaceState(null, '', id);
  }));

  const menu = $('.menu-overlay');
  const menuButton = $('.menu-toggle');
  let menuOpen = false, lastFocus;
  const background = $$('.site-header, main, .site-footer');
  const menuItems = () => $$('a,button', menu);
  const closeMenu = () => {
    menuOpen = false;
    menuButton.setAttribute('aria-expanded', 'false');
    menu.inert = true;
    background.forEach(el => { el.inert = false; });
    document.body.classList.remove('menu-is-open');
    lenis?.start();
    if (window.gsap && !reduced) gsap.to(menu, { yPercent: -101, duration: .5, ease: 'power3.inOut', overwrite: true, onComplete: () => { if (!menuOpen) menu.style.visibility = 'hidden'; } });
    else { menu.style.transform = 'translateY(-101%)'; menu.style.visibility = 'hidden'; }
    lastFocus?.focus();
  };
  menuButton?.addEventListener('click', () => {
    if (menuOpen) return closeMenu();
    menuOpen = true;
    lastFocus = document.activeElement;
    menu.inert = false;
    menuButton.setAttribute('aria-expanded', 'true');
    background.forEach(el => { el.inert = true; });
    document.body.classList.add('menu-is-open');
    lenis?.stop();
    menu.style.visibility = 'visible';
    if (window.gsap && !reduced) {
      gsap.fromTo(menu, { yPercent: -101, y: 0 }, { yPercent: 0, duration: .65, ease: 'power3.inOut', overwrite: true });
      gsap.fromTo($$('nav>a', menu), { y: 25, opacity: 0 }, { y: 0, opacity: 1, stagger: .06, duration: .45, delay: .25 });
    } else menu.style.transform = 'translateY(0)';
    $('.menu-close').focus();
  });
  $('.menu-close')?.addEventListener('click', closeMenu);
  document.addEventListener('keydown', event => {
    if (!menuOpen) return;
    if (event.key === 'Escape') closeMenu();
    if (event.key === 'Tab') {
      const items = menuItems(), first = items[0], last = items.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });

  if (window.gsap && window.ScrollTrigger && !reduced) {
    gsap.registerPlugin(ScrollTrigger);
    gsap.from('.hero-title', { y: 35, opacity: 0, duration: .9, ease: 'power3.out' });
    gsap.from('.hero-bottom', { y: 18, opacity: 0, duration: .75, delay: .2 });
    gsap.to('.hero-star', { rotation: 100, scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 } });
    gsap.to('.metal-flower', { rotation: 30, scrollTrigger: { trigger: '.hero-showcase', start: 'top bottom', end: 'bottom top', scrub: 1.5 } });
    $$('.section-heading, .about-copy>h2, .simple-cta>a').forEach(el => gsap.from(el, { y: 25, opacity: 0, duration: .7, scrollTrigger: { trigger: el, start: 'top 92%', once: true } }));
    const media = gsap.matchMedia();
    media.add('(min-width: 992px)', () => {
      const track = $('.work-track'), windowEl = $('.work-window');
      if (track && windowEl && track.scrollWidth > windowEl.clientWidth + 20) {
        // Drive the native overflow container: keyboard, trackpad and no-JS scrolling remain usable.
        gsap.to(windowEl, { scrollLeft: () => track.scrollWidth - windowEl.clientWidth, ease: 'none', scrollTrigger: { trigger: '#work', start: 'top top', end: () => `+=${track.scrollWidth - windowEl.clientWidth}`, pin: true, scrub: .8, invalidateOnRefresh: true } });
      }
      const aside = $('.about-aside');
      if (aside) ScrollTrigger.create({ trigger: aside, start: 'top 35px', endTrigger: '.about-copy', end: 'bottom bottom', pin: true, pinSpacing: false });
      $$('.service-card').forEach((card, index, cards) => {
        if (index < cards.length - 1) ScrollTrigger.create({ trigger: card, start: `top ${80 + index * 12}px`, endTrigger: '.service-stack', end: 'bottom 280px', pin: true, pinSpacing: false });
      });
    });
    window.addEventListener('load', () => ScrollTrigger.refresh());
  }

  if (window.Swiper && $('.gallery-swiper')) new Swiper('.gallery-swiper', {
    slidesPerView: 1, spaceBetween: 24, keyboard: { enabled: true },
    navigation: { nextEl: '.gallery-next', prevEl: '.gallery-prev' },
    pagination: { el: '.swiper-pagination', clickable: true },
    breakpoints: { 992: { slidesPerView: 1.5 } },
    on: { init() { if (window.ScrollTrigger) ScrollTrigger.refresh(); } }
  });
  const dialog = $('.lightbox');
  $$('[data-lightbox]').forEach(button => button.addEventListener('click', () => {
    const img = $('img', dialog);
    img.src = button.dataset.lightbox; img.alt = button.dataset.caption || 'Project image';
    dialog.showModal(); lenis?.stop();
  }));
  $('.lightbox-close')?.addEventListener('click', () => dialog.close());
  dialog?.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog?.addEventListener('close', () => { if (!menuOpen) lenis?.start(); });

  const clock = $('#local-clock');
  const tick = () => { if (clock) clock.textContent = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date()); };
  tick(); if (clock) setInterval(tick, 60000);

  $$('.contact-form').forEach(form => form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const button = $('button[type="submit"]', form), status = $('.form-status', form), original = button.innerHTML;
    if (button.disabled) return;
    $$('[data-error]', form).forEach(el => { el.textContent = ''; });
    $$('[aria-invalid]', form).forEach(el => { el.removeAttribute('aria-invalid'); el.removeAttribute('aria-describedby'); });
    button.disabled = true; button.textContent = 'Sending…'; status.className = 'form-status'; status.textContent = '';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const data = Object.fromEntries(new FormData(form));
      const token = data.csrfmiddlewaretoken; delete data.csrfmiddlewaretoken;
      const response = await fetch(form.action, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token, 'Accept': 'application/json' }, body: JSON.stringify(data), signal: controller.signal });
      const isJSON = response.headers.get('content-type')?.includes('application/json');
      const result = isJSON ? await response.json() : { message: 'The server could not process your message. Please refresh and try again.' };
      if (!response.ok || !result.ok) {
        for (const [name, errors] of Object.entries(result.errors || {})) {
          const field = form.elements.namedItem(name), error = $(`[data-error="${CSS.escape(name)}"]`, form);
          if (field && error) { field.setAttribute('aria-invalid', 'true'); field.setAttribute('aria-describedby', error.id); error.textContent = errors.map(e => e.message).join(' '); }
        }
        throw new Error(result.message || 'Something went wrong. Please try again.');
      }
      status.textContent = result.message; status.classList.add('success'); form.reset();
    } catch (error) {
      status.textContent = error.name === 'AbortError' ? 'The request timed out. Your message may have arrived; please check before retrying.' : error.message === 'Failed to fetch' ? 'Connection interrupted. Please check your connection and try again.' : error.message;
      status.classList.add('error');
    } finally {
      clearTimeout(timeout); button.disabled = false; button.innerHTML = original;
      const invalid = $('[aria-invalid="true"]', form);
      (invalid || status).focus();
    }
  }));
})();
