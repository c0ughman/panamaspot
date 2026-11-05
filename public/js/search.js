/* Site search for the guides. Loads /search-index.json (built by scripts/build-static.mjs) on first use.
   Results stay in the language of the page you are on. */
(function () {
  "use strict";
  var es = (document.documentElement.lang || "").indexOf("es") === 0;
  var L = es
    ? { ph: "Buscar guías", none: "No hay guías para esa búsqueda.", all: "Ver todas las guías", hint: "Busque un lugar o una actividad: cascadas, café, Bocas…", close: "Cerrar", err: "No se pudo cargar la búsqueda. Inténtelo de nuevo.", home: "/es#cat-regions" }
    : { ph: "Search guides", none: "No guides match that search.", all: "See all guides", hint: "Try a place or an activity: waterfalls, coffee, Bocas…", close: "Close", err: "Search could not load. Please try again.", home: "/#cat-regions" };
  var CSS = ".ps-s{position:fixed;inset:0;z-index:1000;display:none;background:rgba(10,20,35,.55);padding:min(12vh,96px) 16px 16px}.ps-s.on{display:block}" +
    ".ps-b{max-width:640px;margin:0 auto;background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 24px 70px rgba(0,0,0,.35);display:flex;flex-direction:column;max-height:100%;font-family:var(--sans,system-ui,sans-serif);color:#141b2b}" +
    ".ps-r{display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid #e8e8e4}.ps-r svg{flex:none;color:#6b7280}" +
    ".ps-i{flex:1;min-width:0;border:0;outline:0;font:500 17px/1.3 inherit;font-family:inherit;background:none;color:inherit}" +
    ".ps-x{border:0;background:#f3f3f0;border-radius:999px;padding:6px 12px;font:600 13px/1.2 inherit;font-family:inherit;color:#444;cursor:pointer}" +
    ".ps-l{list-style:none;margin:0;padding:6px;overflow-y:auto}.ps-l a{display:block;padding:11px 12px;border-radius:12px;color:inherit;text-decoration:none}" +
    ".ps-l a[aria-selected=true],.ps-l a:hover{background:#f5f5f1}.ps-t{display:block;font-weight:600;font-size:15.5px;line-height:1.3}.ps-d{display:block;margin-top:3px;font-size:13.5px;line-height:1.4;color:#6b7280;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}.ps-g{display:inline-block;margin-right:6px;font-size:12px;font-weight:600;color:#c8102e}" +
    ".ps-m{padding:18px;font-size:14.5px;color:#6b7280}.ps-m a{color:inherit}@media(max-width:560px){.ps-s{padding:12px}}";
  var box, input, list, msg, data = null, loading = null, sel = -1, last = null;

  function norm(s) { return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase(); }
  function close1(a, b) {
    var max = a.length >= 8 ? 2 : 1;
    if (a.length < 5 || Math.abs(a.length - b.length) > max) return false;
    var p = []; for (var j = 0; j <= b.length; j++) p[j] = j;
    for (var i = 1; i <= a.length; i++) { var c = [i], m = i; for (j = 1; j <= b.length; j++) { c[j] = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)); if (c[j] < m) m = c[j]; } if (m > max) return false; p = c; }
    return p[b.length] <= max;
  }
  function score(d, toks, fuzzy) {
    var total = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], s = 0;
      if (d._tw.indexOf(t) >= 0) s += 12;
      else if (d._t.indexOf(t) >= 0) s += 8;
      if (d._r.indexOf(t) >= 0) s += 5;
      if (d._h.indexOf(t) >= 0) s += 3;
      if (d._d.indexOf(t) >= 0) s += 2;
      if (!s && fuzzy) { if (d._all.some(function (w) { return close1(t, w); })) s = 2; }
      if (!s) return 0;
      total += s;
    }
    return total;
  }
  function run(q) {
    var toks = norm(q).split(/[^a-z0-9]+/).filter(function (t) { return t.length > 1; });
    if (!toks.length) return [];
    var f = function (fz) { return data.map(function (d) { return [score(d, toks, fz), d]; }).filter(function (x) { return x[0] > 0; }).sort(function (a, b) { return b[0] - a[0]; }).slice(0, 12).map(function (x) { return x[1]; }); };
    var r = f(false);
    return r.length ? r : f(true);
  }
  function esc(s) { var e = document.createElement("span"); e.textContent = s; return e.innerHTML; }
  function render() {
    var q = input.value.trim(); sel = -1; list.innerHTML = "";
    if (!q) { msg.textContent = L.hint; msg.style.display = "block"; return; }
    if (!data) return;
    var r = run(q);
    if (!r.length) { msg.innerHTML = esc(L.none) + ' <a href="' + L.home + '">' + esc(L.all) + "</a>"; msg.style.display = "block"; return; }
    msg.style.display = "none";
    list.innerHTML = r.map(function (d) { return '<li><a role="option" href="' + d.u + '"><span class="ps-t">' + esc(d.t) + '</span><span class="ps-d">' + (d.r ? '<span class="ps-g">' + esc(d.r) + "</span>" : "") + esc(d.d) + "</span></a></li>"; }).join("");
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
      render();
    }).catch(function () { loading = null; msg.textContent = L.err; msg.style.display = "block"; });
    return loading;
  }
  function move(n) {
    var a = list.querySelectorAll("a"); if (!a.length) return;
    if (sel >= 0) a[sel].removeAttribute("aria-selected");
    sel = (sel + n + a.length) % a.length; a[sel].setAttribute("aria-selected", "true"); a[sel].scrollIntoView({ block: "nearest" });
  }
  function build() {
    var st = document.createElement("style"); st.textContent = CSS; document.head.appendChild(st);
    box = document.createElement("div"); box.className = "ps-s"; box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true"); box.setAttribute("aria-label", L.ph);
    box.innerHTML = '<div class="ps-b"><div class="ps-r"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input class="ps-i" type="search" autocomplete="off" enterkeyhint="search" placeholder="' + L.ph + '" aria-label="' + L.ph + '"><button class="ps-x" type="button">' + L.close + '</button></div><ul class="ps-l" role="listbox"></ul><div class="ps-m"></div></div>';
    document.body.appendChild(box);
    input = box.querySelector(".ps-i"); list = box.querySelector(".ps-l"); msg = box.querySelector(".ps-m");
    box.addEventListener("click", function (e) { if (e.target === box) hide(); });
    box.querySelector(".ps-x").addEventListener("click", hide);
    input.addEventListener("input", render);
    input.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
      else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
      else if (e.key === "Enter") { var a = list.querySelectorAll("a"); if (a.length) { e.preventDefault(); location.href = a[Math.max(sel, 0)].getAttribute("href"); } }
    });
  }
  function show(from) {
    if (!box) build();
    last = from || document.activeElement; box.classList.add("on"); document.documentElement.style.overflow = "hidden"; input.focus(); render(); load();
  }
  function hide() { box.classList.remove("on"); document.documentElement.style.overflow = ""; if (last && last.focus) last.focus(); }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("[data-search]");
    if (a) { e.preventDefault(); show(a); }
  });
  document.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); show(); }
    else if (e.key === "Escape" && box && box.classList.contains("on")) hide();
  });
})();
