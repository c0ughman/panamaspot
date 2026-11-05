/* Site search for the guides. Loads /search-index.json (built by scripts/build-static.mjs) on first use.
   The panel grows out of the "Search guides" pill and glides to the centre, in dark frosted glass with white text and nothing dimmed behind it.
   Results stay in the language of the page you are on. */
(function () {
  "use strict";
  var es = (document.documentElement.lang || "").indexOf("es") === 0;
  var L = es
    ? { ph: "Buscar guías", none: "No hay guías para esa búsqueda.", all: "Ver todas las guías", hint: "Busque un lugar o una actividad: cascadas, café, Bocas…", close: "Cerrar", err: "No se pudo cargar la búsqueda. Inténtelo de nuevo.", home: "/es#cat-regions", guide: "Guía" }
    : { ph: "Search guides", none: "No guides match that search.", all: "See all guides", hint: "Try a place or an activity: waterfalls, coffee, Bocas…", close: "Close", err: "Search could not load. Please try again.", home: "/#cat-regions", guide: "Guide" };
  var SPRING = "linear(0, 0.07 2.2%, 0.26 6.3%, 0.55 12.5%, 0.79 19.5%, 0.93 27%, 0.99 35%, 1.008 43%, 1.006 53%, 1)";
  var hasSpring = window.CSS && CSS.supports && CSS.supports("transition-timing-function", SPRING);
  var EASE = hasSpring ? SPRING : "cubic-bezier(.2,.9,.25,1)";
  var calm = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var GLASS = { bg: "rgba(255,255,255,.18)", blur: "blur(26px) saturate(1.15)", shadow: "0 2px 8px rgba(0,0,0,.15), 0 22px 60px rgba(0,0,0,.12)" };
  var PILL = { bg: "rgba(255,255,255,.18)", blur: "blur(7px) saturate(1.15)", shadow: "0 2px 8px rgba(0,0,0,.15), 0 0 0 rgba(0,0,0,0)" };
  var CSSTEXT = ".ps-s{position:fixed;inset:0;z-index:1000;display:none}.ps-s.on{display:block}" +
    ".ps-b{position:fixed;overflow:hidden;border-radius:26px;background:" + GLASS.bg + ";-webkit-backdrop-filter:" + GLASS.blur + ";backdrop-filter:" + GLASS.blur + ";box-shadow:" + GLASS.shadow + ";font-family:var(--sans,system-ui,sans-serif);color:#fff;transition:height .42s " + EASE + "}" +
    ".ps-in{display:flex;flex-direction:column;min-height:0}" +
    ".ps-r{display:flex;align-items:center;gap:11px;padding:13px 14px 13px 18px;flex:none}.ps-r svg{flex:none;color:#fff;opacity:.75}" +
    ".ps-i{caret-color:#ff4a4f;flex:1;min-width:0;border:0;outline:0;background:none;color:inherit;font:500 17px/1.3 var(--sans,system-ui,sans-serif);-webkit-appearance:none;appearance:none}.ps-i::placeholder{color:rgba(255,255,255,.62)}.ps-i::-webkit-search-cancel-button{display:none}" +
    ".ps-x{border:0;background:rgba(255,255,255,.16);border-radius:999px;padding:6px 12px;font:600 12.5px/1.2 var(--sans,system-ui,sans-serif);color:#fff;cursor:pointer}" +
    ".ps-res{overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin;border-top:1px solid rgba(255,255,255,.13)}.ps-res:empty{display:none}" +
    ".ps-l{list-style:none;margin:0;padding:7px}.ps-l:empty{display:none}" +
    ".ps-l a{display:grid;grid-template-columns:56px minmax(0,1fr);gap:13px;align-items:center;padding:8px;border-radius:17px;color:inherit;text-decoration:none;transition:background .16s ease}" +
    ".ps-l a:hover{background:rgba(255,255,255,.09)}.ps-l a[aria-selected=true]{background:rgba(255,255,255,.17)}" +
    ".ps-th{display:block;width:56px;height:56px;border-radius:13px;overflow:hidden;background:rgba(255,255,255,.1)}.ps-th img{display:block;width:100%;height:100%;object-fit:cover}" +
    ".ps-tx{display:grid;gap:2px;min-width:0}.ps-g{display:inline-flex;align-items:center;gap:6px;font:600 12px/1.2 var(--sans,system-ui,sans-serif);color:rgba(255,255,255,.74)}.ps-g i{width:6px;height:6px;border-radius:50%;background:#ff4a4f;flex:none}" +
    ".ps-t{font:700 15.5px/1.28 var(--sans,system-ui,sans-serif);color:#fff;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".ps-d{font:400 13px/1.35 var(--sans,system-ui,sans-serif);color:rgba(255,255,255,.72);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".ps-b mark{background:rgba(255,74,79,.42);color:#fff;border-radius:4px;padding:0 1px;font-weight:inherit}" +
    "@media(max-width:640px){.ps-t{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}}" +
    ".ps-res.more{-webkit-mask-image:linear-gradient(#000 calc(100% - 26px),transparent);mask-image:linear-gradient(#000 calc(100% - 26px),transparent)}" +
    ".ps-m{padding:15px 20px 18px;font-size:14px;line-height:1.4;color:rgba(255,255,255,.8)}.ps-m a{color:#fff}" +
    ".ps-b,.ps-b *{text-shadow:none}" +
    ".ps-pill{position:absolute;left:0;top:0;margin:0;background:none!important;box-shadow:none!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;color:#fff;pointer-events:none;opacity:0;white-space:nowrap;z-index:2}" +
    ".ps-tint{position:absolute;inset:0;pointer-events:none}.ps-r,.ps-res{position:relative;z-index:1}" +
    "@keyframes ps-up{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}.ps-l.fresh li{animation:ps-up .34s cubic-bezier(.2,.8,.2,1) both}";
  var hidden = null, raf = 0, lastShade = 0, lastGrad = "";
  /* Brightness 0-1 of a photo at a screen point, from a 48x48 copy of it. Unknown -> 0 (treated as dark). */
  var grids = new Map(), cv = document.createElement("canvas"); cv.width = cv.height = 48;
  function brightAt(img, x, y) {
    var key = img.currentSrc || img.src, g = grids.get(key);
    if (g === undefined) {
      g = null;
      try {
        if (img.complete && img.naturalWidth) {
          var cx = cv.getContext("2d", { willReadFrequently: true }); cx.clearRect(0, 0, 48, 48); cx.drawImage(img, 0, 0, 48, 48);
          var d = cx.getImageData(0, 0, 48, 48).data; g = new Float32Array(2304);
          for (var i = 0; i < 2304; i++) g[i] = (0.2126 * d[i * 4] + 0.7152 * d[i * 4 + 1] + 0.0722 * d[i * 4 + 2]) / 255;
          grids.set(key, g);
        }
      } catch (e) { grids.set(key, null); }
    }
    if (!g) return 0;
    var r = img.getBoundingClientRect(), sc = Math.max(r.width / img.naturalWidth, r.height / img.naturalHeight), dw = img.naturalWidth * sc, dh = img.naturalHeight * sc;
    var pos = getComputedStyle(img).objectPosition.split(" ").map(function (v) { return parseFloat(v) / 100; });
    var ox = r.left + (r.width - dw) * (isNaN(pos[0]) ? .5 : pos[0]), oy = r.top + (r.height - dh) * (isNaN(pos[1]) ? .5 : pos[1]);
    var gx = Math.min(47, Math.max(0, Math.floor((x - ox) / dw * 48))), gy = Math.min(47, Math.max(0, Math.floor((y - oy) / dh * 48)));
    return g[gy * 48 + gx];
  }
  /* Is the page behind this point light (white page, beige box) rather than a photo or a dark block? */
  function lightAt(x, y) {
    var under = document.elementsFromPoint(x, y);
    for (var i = 0; i < under.length; i++) {
      var el = under[i];
      if (host.contains(el)) continue;
      var img = el.tagName === "IMG" ? el : null, box = img ? null : el.closest("header.hero, .hero, .home-hero, .hub-hero, .art-hero-section, figure, .ph, .gal, .stamp, .ev-ph");
      if (box) img = box.querySelector("img");
      if (img || box || el.tagName === "VIDEO") return img ? brightAt(img, x, y) > .72 : false;
      for (var a = el; a && a.nodeType === 1; a = a.parentElement) {
        var c = getComputedStyle(a).backgroundColor.match(/[\d.]+/g);
        if (c && (c.length < 4 || +c[3] > .5)) return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255 > .55;
      }
      return true;
    }
    return true;
  }
  /* One soft shade instead of strips: measure how much of each 20px band sits over a light area,
     blur that over about 160px, and ease it in over time, so the edge is a long gentle fade. */
  var MAXA = .34, target = [], eased = [];
  function measure() {
    var r = panel.getBoundingClientRect(), n = Math.ceil(r.height / 20) + 1, raw = [];
    for (var i = 0; i < n; i++) {
      var vy = Math.min(r.bottom - 2, r.top + i * 20), v = 0;
      [.15, .38, .62, .85].forEach(function (f) { if (lightAt(r.left + r.width * f, vy)) v += .25; });
      raw.push(v);
    }
    target = raw.map(function (_, i) {   /* gaussian blur, sigma 4 bands */
      var sum = 0, w = 0;
      for (var k = -10; k <= 10; k++) { var j = Math.min(n - 1, Math.max(0, i + k)), g = Math.exp(-k * k / 32); sum += raw[j] * g; w += g; }
      return sum / w;
    });
  }
  function shade(now) {
    if (!isOpen) return;
    raf = requestAnimationFrame(shade);
    if (now - lastShade > 120) { lastShade = now; measure(); }
    if (!target.length) return;
    var moved = false;
    for (var i = 0; i < target.length; i++) {
      var cur = eased[i] === undefined ? target[i] : eased[i], nx = cur + (target[i] - cur) * .12;
      if (Math.abs(nx - cur) > .002) moved = true;
      eased[i] = nx;
    }
    eased.length = target.length;
    if (!moved && lastGrad) return;
    var stops = eased.map(function (v, i) { return "rgba(24,30,42," + (MAXA * v * v * (3 - 2 * v)).toFixed(3) + ") " + i * 20 + "px"; });
    var g = "linear-gradient(to bottom, " + stops.join(", ") + ")";
    if (g !== lastGrad) { panel.querySelector(".ps-tint").style.backgroundImage = g; lastGrad = g; }
  }

  var host, panel, inner, input, res, list, msg, data = null, loading = null, sel = -1, trigger = null, isOpen = false, anim = null, shown = 0;

  function norm(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function near(a, b) {
    var max = a.length >= 8 ? 2 : 1;
    if (a.length < 5 || Math.abs(a.length - b.length) > max) return false;
    var p = [], j; for (j = 0; j <= b.length; j++) p[j] = j;
    for (var i = 1; i <= a.length; i++) { var c = [i], m = i; for (j = 1; j <= b.length; j++) { c[j] = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); if (c[j] < m) m = c[j]; } if (m > max) return false; p = c; }
    return p[b.length] <= max;
  }
  function tokens(q) { return norm(q).split(/[^a-z0-9]+/).filter(function (t) { return t.length > 1; }); }
  function score(d, toks, fuzzy) {
    var total = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], s = 0;
      if (d._tw.indexOf(t) >= 0) s += 12; else if (d._t.indexOf(t) >= 0) s += 8;
      if (d._r.indexOf(t) >= 0) s += 5;
      if (d._h.indexOf(t) >= 0) s += 3;
      if (d._d.indexOf(t) >= 0) s += 2;
      if (!s && fuzzy && d._all.some(function (w) { return near(t, w); })) s = 2;
      if (!s) return 0;
      total += s;
    }
    return total;
  }
  function run(toks) {
    if (!toks.length) return [];
    var f = function (fz) { return data.map(function (d) { return [score(d, toks, fz), d]; }).filter(function (x) { return x[0] > 0; }).sort(function (a, b) { return b[0] - a[0]; }).slice(0, 10).map(function (x) { return x[1]; }); };
    var r = f(false);
    return r.length ? r : f(true);
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  /* Wrap what was typed in <mark>, matching "cafe" to "café", and the nearest word when it was a typo. */
  function mark(text, toks) {
    var flat = "", map = [], i;
    for (i = 0; i < text.length; i++) { var n = norm(text[i]); for (var k = 0; k < n.length; k++) { flat += n[k]; map.push(i); } }
    var hit = [];
    toks.forEach(function (t) {
      var from = 0, at, any = false;
      while ((at = flat.indexOf(t, from)) >= 0) { hit.push([map[at], map[at + t.length - 1] + 1]); from = at + t.length; any = true; }
      if (!any) { var re = /[a-z0-9]+/g, m; while ((m = re.exec(flat))) if (near(t, m[0])) hit.push([map[m.index], map[m.index + m[0].length - 1] + 1]); }
    });
    if (!hit.length) return esc(text);
    hit.sort(function (a, b) { return a[0] - b[0]; });
    var out = "", pos = 0;
    hit.forEach(function (h) { if (h[1] <= pos) return; var s = Math.max(h[0], pos); out += esc(text.slice(pos, s)) + "<mark>" + esc(text.slice(s, h[1])) + "</mark>"; pos = h[1]; });
    return out + esc(text.slice(pos));
  }
  function select(n) {
    var a = list.querySelectorAll("a"); if (!a.length) { sel = -1; return; }
    if (sel >= 0 && a[sel]) a[sel].removeAttribute("aria-selected");
    sel = (n + a.length) % a.length; a[sel].setAttribute("aria-selected", "true"); a[sel].scrollIntoView({ block: "nearest" });
  }
  function fit() {
    var row = panel.querySelector(".ps-r").offsetHeight, top = parseFloat(panel.style.top) || 12;
    var vh = window.visualViewport ? visualViewport.height : innerHeight;
    res.style.maxHeight = Math.max(120, Math.min(vh - top - 16, 620) - row) + "px";
    panel.style.height = inner.offsetHeight + "px";
    edge();
  }
  function edge() { res.classList.toggle("more", res.scrollHeight - res.scrollTop - res.clientHeight > 4); }
  function render() {
    var q = input.value.trim(), first = shown === 0;
    sel = -1; list.innerHTML = ""; list.classList.remove("fresh");
    if (!q) { msg.textContent = L.hint; msg.style.display = "block"; shown = 0; fit(); return; }
    if (!data) { fit(); return; }
    var toks = tokens(q), r = run(toks);
    shown = r.length;
    if (!r.length) { msg.innerHTML = esc(L.none) + ' <a href="' + L.home + '">' + esc(L.all) + "</a>"; msg.style.display = "block"; fit(); return; }
    msg.style.display = "none";
    list.innerHTML = r.map(function (d, i) {
      return '<li style="animation-delay:' + i * 22 + 'ms"><a role="option" href="' + esc(d.u) + '"><span class="ps-th">' + (d.i ? '<img alt="" width="56" height="56" decoding="async" src="' + esc(d.i) + '" onerror="this.remove()">' : "") + '</span><span class="ps-tx"><span class="ps-g"><i></i>' + esc(d.r || L.guide) + '</span><span class="ps-t">' + mark(d.t, toks) + '</span><span class="ps-d">' + mark(d.d, toks) + "</span></span></a></li>";
    }).join("");
    if (first && !calm) list.classList.add("fresh");
    select(0); fit();
  }
  function load() {
    if (data || loading) return loading;
    loading = fetch("/search-index.json").then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (all) {
      var lang = es ? "es" : "en";
      data = all.filter(function (d) { return d.l === lang; }).map(function (d) {
        d._t = norm(d.t); d._tw = d._t.split(/[^a-z0-9]+/); d._r = norm(d.r); d._h = norm(d.h); d._d = norm(d.d);
        d._all = (d._t + " " + d._r + " " + d._h).split(/[^a-z0-9]+/);
        return d;
      });
      if (isOpen) render();
    }).catch(function () { loading = null; if (isOpen) { msg.textContent = L.err; msg.style.display = "block"; fit(); } });
    return loading;
  }
  function build() {
    var st = document.createElement("style"); st.textContent = CSSTEXT; document.head.appendChild(st);
    host = document.createElement("div"); host.className = "ps-s"; host.setAttribute("role", "dialog"); host.setAttribute("aria-modal", "true"); host.setAttribute("aria-label", L.ph);
    host.innerHTML = '<div class="ps-b"><div class="ps-in"><div class="ps-tint" aria-hidden="true"></div><div class="ps-r"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input class="ps-i" type="search" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="search" placeholder="' + L.ph + '" aria-label="' + L.ph + '"><button class="ps-x" type="button">' + L.close + '</button></div><div class="ps-res"><ul class="ps-l" role="listbox"></ul><div class="ps-m"></div></div></div></div>';
    document.body.appendChild(host);
    panel = host.querySelector(".ps-b"); inner = host.querySelector(".ps-in"); input = host.querySelector(".ps-i"); res = host.querySelector(".ps-res"); list = host.querySelector(".ps-l"); msg = host.querySelector(".ps-m");
    host.addEventListener("mousedown", function (e) { if (e.target === host) hide(); });
    host.querySelector(".ps-x").addEventListener("click", hide);
    input.addEventListener("input", render);
    res.addEventListener("scroll", edge, { passive: true });
    input.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); hide(); return; }  /* stop the browser clearing the box first */
      if (e.key === "ArrowDown") { e.preventDefault(); select(sel + 1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); select(sel - 1); }
      else if (e.key === "Enter") { var a = list.querySelectorAll("a"); if (a.length) { e.preventDefault(); location.href = a[Math.max(sel, 0)].getAttribute("href"); } }
    });
    addEventListener("resize", function () { if (isOpen) { place(); fit(); } });
    if (window.visualViewport) visualViewport.addEventListener("resize", function () { if (isOpen) fit(); });
  }
  /* Where the pill is now. If it has scrolled away (the shortcut still works), start from a small pill at the top. */
  function origin() {
    var el = trigger && trigger.getBoundingClientRect ? trigger : document.querySelector("[data-search]");
    var r = el && el.getBoundingClientRect();
    if (r && r.width > 0 && r.bottom > 0 && r.top < innerHeight) return { left: r.left, top: r.top, width: r.width, height: r.height, el: el };
    return { left: innerWidth / 2 - 95, top: 16, width: 190, height: 40, el: null };
  }
  /* The panel always lands in the middle of the screen; the pill stays hidden while it is open. */
  function place() {
    var vw = document.documentElement.clientWidth, vh = window.innerHeight, o = origin(), w = vw <= 640 ? vw - 24 : Math.min(660, vw - 32);
    panel.style.left = (vw - w) / 2 + "px"; panel.style.top = (vw <= 640 ? 16 : Math.round(vh * .14)) + "px"; panel.style.width = w + "px";
    return o;
  }
  function frame(o, glass) {
    var g = glass ? GLASS : PILL;
    return { left: o.left + "px", top: o.top + "px", width: o.width + "px", height: o.height + "px", borderRadius: glass ? "26px" : o.height / 2 + "px", backgroundColor: g.bg, backdropFilter: g.blur, webkitBackdropFilter: g.blur, boxShadow: g.shadow };
  }
  var byKey = false;
  /* Put the pill's own icon and label inside the panel, at the pill's size, so the two can cross-fade. */
  function pillCopy(el) {
    var c = panel.querySelector(".ps-pill");
    if (!c) { c = document.createElement("span"); c.className = "search ps-pill"; c.setAttribute("aria-hidden", "true"); panel.appendChild(c); }
    if (el) {
      c.innerHTML = el.innerHTML;
      var r = el.getBoundingClientRect(); c.style.width = r.width + "px"; c.style.height = r.height + "px"; c.style.font = getComputedStyle(el).font;
    }
    return el ? c : null;
  }
  function show(from) {
    if (!host) build();
    if (isOpen) { input.focus(); input.select(); return; }
    trigger = from || null; isOpen = true;
    if (anim) anim.cancel();
    host.classList.add("on");
    var o = place(); input.value = input.value || ""; shown = 0; render();
    input.focus({ preventScroll: true }); load();
    var end = { left: parseFloat(panel.style.left), top: parseFloat(panel.style.top), width: parseFloat(panel.style.width), height: inner.offsetHeight };
    if (calm) { panel.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160 }); return; }
    if (o.el) { o.el.style.visibility = "hidden"; hidden = o.el; }
    cancelAnimationFrame(raf); lastShade = 0; target = []; eased = []; lastGrad = ""; raf = requestAnimationFrame(shade);
    panel.style.transition = "none";
    anim = panel.animate([frame(o, false), frame(end, true)], { duration: 560, easing: EASE });
    inner.animate([{ opacity: 0, offset: 0 }, { opacity: 0, offset: .12 }, { opacity: 1, offset: .46 }, { opacity: 1, offset: 1 }], { duration: 560, easing: "ease-out" });
    var pc = pillCopy(o.el);
    if (pc) pc.animate([{ opacity: 1 }, { opacity: 0, offset: .24 }, { opacity: 0 }], { duration: 560, easing: "ease-out" });
    anim.onfinish = function () { panel.style.transition = ""; };
  }
  /* Closing mirrors opening: in one continuous move the results fade out while the pill's own label
     fades in early, so the glass is never empty, and it lands exactly on the pill. */
  function hide() {
    if (!isOpen) return; isOpen = false;
    var o = origin(), r = panel.getBoundingClientRect(), fades = [];
    var done = function () {
      host.classList.remove("on"); fades.forEach(function (f) { f.cancel(); });
      input.value = ""; list.innerHTML = ""; shown = 0;
      if (trigger && trigger.focus) trigger.focus({ preventScroll: true, focusVisible: byKey });
    };
    var back = function () { if (hidden) { hidden.style.visibility = ""; hidden = null; } };
    if (calm) { back(); done(); return; }
    if (anim) anim.cancel();
    panel.style.transition = "none";
    var D = 440;
    fades.push(inner.animate([{ opacity: 1 }, { opacity: 0, offset: .24 }, { opacity: 0 }], { duration: D, easing: "ease-out", fill: "forwards" }));
    var pc = pillCopy(o.el);
    if (pc) fades.push(pc.animate([{ opacity: 0 }, { opacity: 1, offset: .3 }, { opacity: 1 }], { duration: D, easing: "ease-out", fill: "forwards" }));
    var end = o.el ? frame(o, false) : Object.assign(frame(o, false), { opacity: 0 });
    anim = panel.animate([frame({ left: r.left, top: r.top, width: r.width, height: r.height }, true), end], { duration: D, easing: "cubic-bezier(.32,.72,0,1)" });
    anim.onfinish = function () { panel.style.transition = ""; back(); done(); };
  }
  document.addEventListener("click", function (e) {
    var lang = e.target.closest && e.target.closest(".lang a:not(.on)");
    if (lang && !e.metaKey && !e.ctrlKey && !e.shiftKey && !calm) {
      var wrap = lang.parentElement, on = wrap.querySelector("a.on");
      if (on) {
        e.preventDefault();
        var w = wrap.getBoundingClientRect(), a = on.getBoundingClientRect(), b = lang.getBoundingClientRect();
        var knob = document.createElement("i");
        knob.style.cssText = "position:absolute;z-index:0;border-radius:999px;background:rgba(255,255,255,.92);pointer-events:none;left:" + (a.left - w.left) + "px;top:" + (a.top - w.top) + "px;width:" + a.width + "px;height:" + a.height + "px";
        wrap.style.position = "relative"; wrap.insertBefore(knob, wrap.firstChild);
        [on, lang].forEach(function (x) { x.style.position = "relative"; x.style.zIndex = "1"; x.style.transition = "color .28s ease"; });
        on.classList.remove("on"); on.style.background = "none"; lang.style.color = "var(--navy, #05183f)";
        knob.animate([{ transform: "translateX(0)", width: a.width + "px" }, { transform: "translateX(" + (b.left - a.left) + "px)", width: b.width + "px" }], { duration: 340, easing: EASE, fill: "forwards" });
        var href = lang.href;
        setTimeout(function () { location.href = href; }, 360);
        return;
      }
    }
    var a = e.target.closest && e.target.closest("[data-search]");
    if (a) { e.preventDefault(); byKey = e.detail === 0; show(a); }
  });
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); byKey = true; show(); }
    else if (e.key === "Escape" && isOpen) hide();
  });
})();
