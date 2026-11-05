/* Site search for the guides. Loads /search-index.json (built by scripts/build-static.mjs) on first use.
   The panel grows out of the "Search guides" pill, in the same frosted glass, with nothing dimmed behind it.
   Results stay in the language of the page you are on. */
(function () {
  "use strict";
  var es = (document.documentElement.lang || "").indexOf("es") === 0;
  var L = es
    ? { ph: "Buscar guías", none: "No hay guías para esa búsqueda.", all: "Ver todas las guías", hint: "Busque un lugar o una actividad: cascadas, café, Bocas…", close: "Cerrar", err: "No se pudo cargar la búsqueda. Inténtelo de nuevo.", home: "/es#cat-regions", guide: "Guía" }
    : { ph: "Search guides", none: "No guides match that search.", all: "See all guides", hint: "Try a place or an activity: waterfalls, coffee, Bocas…", close: "Close", err: "Search could not load. Please try again.", home: "/#cat-regions", guide: "Guide" };
  var SPRING = "linear(0, 0.02 1.1%, 0.083 2.4%, 0.311 5.7%, 0.63 10.4%, 0.85 14.6%, 0.96 17.9%, 1.03 21.3%, 1.06 24.4%, 1.07 27.5%, 1.06 31.5%, 1.02 39.5%, 1 45%, 0.995 52%, 1)";
  var hasSpring = window.CSS && CSS.supports && CSS.supports("transition-timing-function", SPRING);
  var EASE = hasSpring ? SPRING : "cubic-bezier(.22,1.15,.36,1)";
  var calm = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var GLASS = { bg: "rgba(255,255,255,.62)", blur: "blur(30px) saturate(1.7)", shadow: "0 18px 60px rgba(5,24,63,.2), inset 0 0 0 1px rgba(255,255,255,.5)" };
  var PILL = { bg: "rgba(255,255,255,.18)", blur: "blur(7px) saturate(1.15)", shadow: "0 2px 8px rgba(0,0,0,.15), inset 0 0 0 1px rgba(255,255,255,0)" };
  var CSSTEXT = ".ps-s{position:fixed;inset:0;z-index:1000;display:none}.ps-s.on{display:block}" +
    ".ps-b{position:fixed;overflow:hidden;border-radius:26px;background:" + GLASS.bg + ";-webkit-backdrop-filter:" + GLASS.blur + ";backdrop-filter:" + GLASS.blur + ";box-shadow:" + GLASS.shadow + ";font-family:var(--sans,system-ui,sans-serif);color:var(--ink,#161b26);transition:height .42s " + EASE + "}" +
    ".ps-in{display:flex;flex-direction:column;min-height:0}" +
    ".ps-r{display:flex;align-items:center;gap:11px;padding:13px 14px 13px 18px;flex:none}.ps-r svg{flex:none;color:var(--ink,#161b26);opacity:.65}" +
    ".ps-i{flex:1;min-width:0;border:0;outline:0;background:none;color:inherit;font:500 17px/1.3 var(--sans,system-ui,sans-serif);-webkit-appearance:none;appearance:none}.ps-i::placeholder{color:rgba(22,27,38,.55)}.ps-i::-webkit-search-cancel-button{display:none}" +
    ".ps-x{border:0;background:rgba(255,255,255,.55);border-radius:999px;padding:6px 12px;font:600 12.5px/1.2 var(--sans,system-ui,sans-serif);color:var(--ink,#161b26);cursor:pointer}" +
    ".ps-res{overflow-y:auto;overscroll-behavior:contain;scrollbar-width:thin;border-top:1px solid rgba(22,27,38,.09)}.ps-res:empty{display:none}" +
    ".ps-l{list-style:none;margin:0;padding:7px}.ps-l:empty{display:none}" +
    ".ps-l a{display:grid;grid-template-columns:56px minmax(0,1fr);gap:13px;align-items:center;padding:8px;border-radius:17px;color:inherit;text-decoration:none;transition:background .16s ease}" +
    ".ps-l a[aria-selected=true]{background:rgba(255,255,255,.62);box-shadow:0 1px 4px rgba(5,24,63,.07)}.ps-l a:hover{background:rgba(255,255,255,.5)}" +
    ".ps-th{display:block;width:56px;height:56px;border-radius:13px;overflow:hidden;background:rgba(5,24,63,.08)}.ps-th img{display:block;width:100%;height:100%;object-fit:cover}" +
    ".ps-tx{display:grid;gap:2px;min-width:0}.ps-g{display:inline-flex;align-items:center;gap:6px;font:600 12px/1.2 var(--sans,system-ui,sans-serif);color:rgba(22,27,38,.68)}.ps-g i{width:6px;height:6px;border-radius:50%;background:var(--red,#da121a);flex:none}" +
    ".ps-t{font:700 15.5px/1.28 var(--sans,system-ui,sans-serif);color:var(--navy,#05183f);letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".ps-d{font:400 13px/1.35 var(--sans,system-ui,sans-serif);color:rgba(22,27,38,.68);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}" +
    ".ps-b mark{background:rgba(218,18,26,.15);color:inherit;border-radius:4px;padding:0 1px;font-weight:inherit}.ps-t mark{color:#a50d14}" +
    "@media(max-width:640px){.ps-t{white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}}" +
    ".ps-res.more{-webkit-mask-image:linear-gradient(#000 calc(100% - 26px),transparent);mask-image:linear-gradient(#000 calc(100% - 26px),transparent)}" +
    ".ps-m{padding:15px 20px 18px;font-size:14px;line-height:1.4;color:rgba(22,27,38,.72)}.ps-m a{color:inherit}" +
    "@keyframes ps-up{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}.ps-l.fresh li{animation:ps-up .34s cubic-bezier(.2,.8,.2,1) both}";
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
    host.innerHTML = '<div class="ps-b"><div class="ps-in"><div class="ps-r"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input class="ps-i" type="search" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="search" placeholder="' + L.ph + '" aria-label="' + L.ph + '"><button class="ps-x" type="button">' + L.close + '</button></div><div class="ps-res"><ul class="ps-l" role="listbox"></ul><div class="ps-m"></div></div></div></div>';
    document.body.appendChild(host);
    panel = host.querySelector(".ps-b"); inner = host.querySelector(".ps-in"); input = host.querySelector(".ps-i"); res = host.querySelector(".ps-res"); list = host.querySelector(".ps-l"); msg = host.querySelector(".ps-m");
    host.addEventListener("mousedown", function (e) { if (e.target === host) hide(); });
    host.querySelector(".ps-x").addEventListener("click", hide);
    input.addEventListener("input", render);
    res.addEventListener("scroll", edge, { passive: true });
    input.addEventListener("keydown", function (e) {
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
  function place() {
    var vw = document.documentElement.clientWidth, o = origin(), w, left;
    if (vw <= 640) { w = vw - 24; left = 12; } else { w = Math.min(640, vw - 32); left = o.el ? Math.max(16, Math.min(o.left + o.width - w, vw - w - 16)) : (vw - w) / 2; }
    panel.style.left = left + "px"; panel.style.top = Math.max(12, o.top - 3) + "px"; panel.style.width = w + "px";
    return o;
  }
  function frame(o, glass) {
    var g = glass ? GLASS : PILL;
    return { left: o.left + "px", top: o.top + "px", width: o.width + "px", height: o.height + "px", borderRadius: glass ? "26px" : o.height / 2 + "px", backgroundColor: g.bg, backdropFilter: g.blur, webkitBackdropFilter: g.blur, boxShadow: g.shadow };
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
    if (o.el) o.el.style.visibility = "hidden";
    panel.style.transition = "none";
    anim = panel.animate([frame(o, false), frame(end, true)], { duration: 560, easing: EASE });
    inner.animate([{ opacity: 0, offset: 0 }, { opacity: 0, offset: .14 }, { opacity: 1, offset: .5 }, { opacity: 1, offset: 1 }], { duration: 560, easing: "ease-out" });
    anim.onfinish = function () { panel.style.transition = ""; };
  }
  function hide() {
    if (!isOpen) return; isOpen = false;
    var o = origin(), r = panel.getBoundingClientRect();
    var done = function () { host.classList.remove("on"); if (o.el) o.el.style.visibility = ""; input.value = ""; list.innerHTML = ""; if (trigger && trigger.focus) trigger.focus({ preventScroll: true }); };
    if (calm) { done(); return; }
    if (anim) anim.cancel();
    panel.style.transition = "none";
    inner.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 120, easing: "ease-out", fill: "forwards" }).onfinish = function (e) { e.target.cancel(); };
    anim = panel.animate([frame({ left: r.left, top: r.top, width: r.width, height: r.height }, true), o.el ? frame(o, false) : Object.assign(frame(o, false), { opacity: 0 })], { duration: 300, easing: "cubic-bezier(.32,.72,0,1)" });
    anim.onfinish = function () { panel.style.transition = ""; done(); };
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-search]");
    if (a) { e.preventDefault(); show(a); }
  });
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); show(); }
    else if (e.key === "Escape" && isOpen) hide();
  });
})();
