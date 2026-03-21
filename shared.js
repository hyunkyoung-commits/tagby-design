/* ============================================================
   shared.js — 모든 페이지 공통 JavaScript
   ============================================================ */

/* togglePortfolioCategory: 햄버거 메뉴 포트폴리오 아코디언 */
function togglePortfolioCategory(btn) {
  var sub = btn.parentElement.querySelector('.category-sub');
  var arrow = btn.querySelector('.category-arrow');
  if (!sub) return;
  var isOpen = sub.classList.contains('flex');
  sub.classList.toggle('hidden', isOpen);
  sub.classList.toggle('flex', !isOpen);
  if (arrow) arrow.style.transform = isOpen ? '' : 'rotate(180deg)';
}

window.addEventListener('load', function () {

  /* ── Scroll-to-Top ── */
  var scrollToTopBtn = document.getElementById('scrollToTop');
  if (scrollToTopBtn) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 300) {
        scrollToTopBtn.classList.add('visible');
      } else {
        scrollToTopBtn.classList.remove('visible');
      }
    });
    scrollToTopBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ── Mobile Menu (Hamburger) ── */
  var hamburger    = document.getElementById('hamburger');
  var mobileMenu   = document.getElementById('mobileMenu');
  var mobileOverlay = document.getElementById('mobileOverlay');

  if (hamburger && mobileMenu && mobileOverlay) {
    hamburger.addEventListener('click', function () {
      hamburger.classList.toggle('active');
      mobileMenu.classList.toggle('active');
      mobileOverlay.classList.toggle('active');
      document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });

    mobileOverlay.addEventListener('click', function () {
      hamburger.classList.remove('active');
      mobileMenu.classList.remove('active');
      mobileOverlay.classList.remove('active');
      document.body.style.overflow = '';
    });

    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        mobileOverlay.classList.remove('active');
        document.body.style.overflow = '';
      });
    });
  }

  /* ── Dropdown (shared timer) ── */
  (function () {
    var allDropdowns = Array.from(document.querySelectorAll('.dropdown'));
    var hideTimer;
    var activeMenu = null;

    function closeAll() {
      allDropdowns.forEach(function (d) {
        var m = d.querySelector('.dropdown-menu');
        if (m) { m.style.display = 'none'; m.style.opacity = '0'; }
      });
      activeMenu = null;
    }

    function showMenu(dropdown) {
      clearTimeout(hideTimer);
      if (activeMenu && activeMenu !== dropdown) {
        var prev = activeMenu.querySelector('.dropdown-menu');
        if (prev) { prev.style.display = 'none'; prev.style.opacity = '0'; }
      }
      activeMenu = dropdown;
      var menu = dropdown.querySelector('.dropdown-menu');
      if (menu) {
        menu.style.display = 'block';
        menu.style.opacity = '1';
        menu.style.transform = 'translateY(0)';
      }
    }

    function scheduleHide() {
      hideTimer = setTimeout(closeAll, 300);
    }

    allDropdowns.forEach(function (dropdown) {
      var menu = dropdown.querySelector('.dropdown-menu');
      if (!menu) return;
      dropdown.addEventListener('mouseenter', function () { showMenu(dropdown); });
      dropdown.addEventListener('mouseleave', scheduleHide);
      menu.addEventListener('mouseenter', function () { showMenu(dropdown); });
      menu.addEventListener('mouseleave', scheduleHide);
    });
  })();

  /* ── GSAP Scroll Animation ── */
  (function () {
    if (!window.gsap || !window.ScrollTrigger) {
      console.warn('GSAP not loaded, content visible by default');
      return;
    }
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    try {
      gsap.registerPlugin(ScrollTrigger);

      document.querySelectorAll('.reveal-item').forEach(function (el) {
        el.classList.add('gsap-enabled');
      });

      ScrollTrigger.batch('.reveal-item', {
        interval: 0.1,
        batchMax: 8,
        onEnter: function (batch) {
          gsap.to(batch, {
            opacity: 1,
            y: 0,
            stagger: { each: 0.08 },
            duration: 0.9,
            ease: 'power1.out'
          });
        },
        start: 'top 80%'
      });

      ScrollTrigger.refresh();
    } catch (e) {
      console.error('GSAP animation error:', e);
      document.querySelectorAll('.reveal-item').forEach(function (el) {
        el.classList.remove('gsap-enabled');
      });
    }
  })();

});
