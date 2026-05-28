/* Vanilla replacements for the React client components stripped out of
   the static HTML. Each block feature-detects its targets so unused
   pages cost nothing. Loaded with `defer`, so the DOM is ready. */
(function () {
  "use strict";

  // ── ReadingProgress ────────────────────────────────────────────────────
  // <div class="read-progress"> at the top of article pages. Width tracks
  // scroll-depth percentage.
  (function readingProgress() {
    const bar = document.querySelector(".read-progress");
    if (!bar) return;
    const root = document.documentElement;
    const update = () => {
      const pct = (root.scrollTop / (root.scrollHeight - root.clientHeight)) * 100;
      bar.style.width = (isFinite(pct) ? pct : 0) + "%";
    };
    update();
    window.addEventListener("scroll", update, { passive: true });
  })();

  // ── NewsletterForm ─────────────────────────────────────────────────────
  // <form class="nl-form"> — swap button text to "Thanks ✓" on submit.
  // No backend wired up here; keep this as a no-op submission.
  (function newsletterForm() {
    document.querySelectorAll("form.nl-form").forEach((form) => {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        const btn = form.querySelector("button[type=submit]");
        if (btn) btn.textContent = "Thanks ✓";
      });
    });
  })();

  // ── FaqItem ────────────────────────────────────────────────────────────
  // <div class="faq-item"><button class="faq-q">…</button><div class="faq-a">…</div></div>
  (function faqItems() {
    document.querySelectorAll(".faq-item").forEach((item) => {
      const btn = item.querySelector(".faq-q");
      if (!btn) return;
      btn.addEventListener("click", () => {
        const open = item.classList.toggle("open");
        btn.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
  })();

  // ── ArticleToc ─────────────────────────────────────────────────────────
  // <aside class="toc"><ul><li><a href="#anchor">…</a></li>…</ul></aside>
  // Smooth-scrolls on click and highlights the nearest section above the
  // 200px threshold (matches the React version).
  (function articleToc() {
    const toc = document.querySelector(".toc");
    if (!toc) return;
    const links = Array.from(toc.querySelectorAll('a[href^="#"]'));
    if (!links.length) return;

    const targets = links
      .map((a) => {
        const id = a.getAttribute("href").slice(1);
        const el = document.getElementById(id);
        return el ? { id, el, link: a } : null;
      })
      .filter(Boolean);

    const setActive = (id) => {
      links.forEach((a) => {
        a.classList.toggle("active", a.getAttribute("href") === "#" + id);
      });
    };

    const onScroll = () => {
      let cur = null;
      for (const t of targets) {
        if (t.el.getBoundingClientRect().top < 200) cur = t.id;
      }
      if (cur) setActive(cur);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    links.forEach((a) => {
      a.addEventListener("click", (e) => {
        const id = a.getAttribute("href").slice(1);
        const el = document.getElementById(id);
        if (!el) return;
        e.preventDefault();
        const y = el.getBoundingClientRect().top + window.pageYOffset - 80;
        window.scrollTo({ top: y, behavior: "smooth" });
      });
    });
  })();

  // ── HeroParallax (home hero) ───────────────────────────────────────────
  // <section class="home-hero"> with an inner <div class="header-wrapper">.
  // backgroundPosition shifts with scroll; .has-background flips at 10vh.
  (function heroParallax() {
    const section = document.querySelector(".home-hero");
    if (!section) return;
    const wrapper = section.querySelector(".header-wrapper");
    const onScroll = () => {
      const y = window.scrollY;
      section.style.backgroundPosition = "center " + y * 0.4 + "px";
      if (wrapper) {
        const threshold = window.innerHeight * 0.1;
        wrapper.classList.toggle("has-background", y > threshold);
      }
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  })();

  // ── ArticleHero ────────────────────────────────────────────────────────
  // <section class="art-hero-section">
  //   <div class="art-hero-img-full" …></div>
  //   <div class="art-header-bar"> … </div>
  // The image translates downward at 40% of scroll; the header bar gains
  // .scrolled past the midpoint of the hero.
  (function articleHero() {
    const section = document.querySelector(".art-hero-section");
    if (!section) return;
    const img = section.querySelector(".art-hero-img-full");
    const bar = section.querySelector(".art-header-bar");
    const onScroll = () => {
      const heroH = section.offsetHeight || window.innerHeight * 0.4;
      if (bar) bar.classList.toggle("scrolled", window.scrollY >= heroH * 0.5);
      if (img) img.style.transform = "translateY(" + window.scrollY * 0.4 + "px)";
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  })();

  // ── CategoryRow ────────────────────────────────────────────────────────
  // <div class="cat-row-wrap">
  //   <button class="cat-arrow prev">…</button>
  //   <div class="cat-row"> .cat-card * N </div>
  //   <button class="cat-arrow next">…</button>
  // Arrows scroll one card (+14px gap) at a time, smoothly.
  (function categoryRows() {
    document.querySelectorAll(".cat-row-wrap").forEach((wrap) => {
      const row = wrap.querySelector(".cat-row");
      if (!row) return;
      const scroll = (dir) => {
        const card = row.querySelector(".cat-card");
        const step = card ? card.offsetWidth + 14 : row.clientWidth;
        row.scrollBy({ left: dir * step, behavior: "smooth" });
      };
      const prev = wrap.querySelector(".cat-arrow.prev");
      const next = wrap.querySelector(".cat-arrow.next");
      if (prev) prev.addEventListener("click", () => scroll(-1));
      if (next) next.addEventListener("click", () => scroll(1));
    });
  })();
})();
