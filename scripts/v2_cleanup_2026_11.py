"""One-off cleanup of the 54 V2 guides, 2026-11-05. Prices come only from evalleybikes.net.
  1. E-Valley prices and kit in article text and FAQ schema, cited to evalleybikes.net
  2. no links between languages in text or source lists (the EN/ES switch stays)
  3. no skipped heading levels: step titles and footer columns
  4. "Every guide" footer lists every guide of the page's own language
"""
import html, json, re
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "public"
ALL = sorted(P.glob("articles/*.html")) + sorted(P.glob("es/articles/*.html"))
V2 = [f for f in ALL if '<header class="hero">' in f.read_text(errors="ignore")]
key = lambda f: str(f.relative_to(P))[:-5]
EV = {"elv-r": "el-valle/rentals", "elv-t": "el-valle/tours", "bq-r": "boquete/rentals", "bq-t": "boquete/tours"}
EVT = {"es": {"elv-r": "Alquiler de e-bikes en El Valle", "elv-t": "Tours guiados en El Valle", "bq-r": "Alquiler de e-bikes en Boquete", "bq-t": "Tours guiados en Boquete"},
       "en": {"bq-t": "Guided e-bike tours in Boquete"}}
cite = lambda n: f'<sup class="cite"><a href="#src-{n}">[{n}]</a></sup>'


def src_li(n, lang, k):
    return (f'<li id="src-{n}"><span class="src-n">{n}</span><div><a href="https://evalleybikes.net/{lang}/{EV[k]}" rel="sponsored noopener" target="_blank">'
            f'E-Valley Bikes - {EVT[lang][k]}</a><span class="src-domain">evalleybikes.net</span></div></li>')


class Page:
    def __init__(s, rel):
        s.f = P / (rel + ".html"); s.h = s.f.read_text(); s.lang = "es" if rel.startswith("es/") else "en"; s.rel = rel

    def rep(s, a, b):
        if a not in s.h: raise SystemExit(f"{s.rel}: not found: {a[:70]}")
        s.h = s.h.replace(a, b)

    def sub(s, pat, b):
        s.h, n = re.subn(pat, lambda m: b, s.h, flags=re.S)
        if not n: raise SystemExit(f"{s.rel}: no match: {pat[:70]}")

    def set_src(s, n, k):
        s.sub(rf'<li id="src-{n}">.*?</li>', src_li(n, s.lang, k))

    def drop_src(s, n):
        s.sub(rf'<li id="src-{n}">.*?</li>', ""); s._count(-1)

    def add_src(s, k):
        n = max(int(x) for x in re.findall(r'<li id="src-(\d+)">', s.h)) + 1
        i = s.h.index("</ol>", s.h.index('class="src-list"'))
        s.h = s.h[:i] + src_li(n, s.lang, k) + s.h[i:]; s._count(1)
        return n

    def _count(s, d):
        s.h = re.sub(r'(<a href="#sources">)(\d+)( (?:sources|fuentes))', lambda m: f"{m[1]}{int(m[2]) + d}{m[3]}", s.h)

    def save(s):
        s.f.write_text(s.h)


def prices():
    p = Page("articles/boquete-with-kids-family-guide")
    p.rep("<td>2-4 h</td><td>$35-85</td>", "<td>2.5-3 h</td><td>$75-115</td>")
    p.rep(" is listed for ages 18 to 99 at $48 per adult.", " is listed for ages 18 to 99.")
    p.rep("Guided e-bike tours run from about $35 to $85 per person, the higher end for a 4-hour tour with a two-person minimum." + cite(10) + cite(11),
          "E-Valley Bikes lists private guided tours in Boquete at $75-85 per person for groups of 2 or more, or $100-115 for one person." + cite(10))
    p.set_src(10, "bq-t"); p.drop_src(11); p.save()

    p = Page("es/articles/cascadas-perdidas-boquete-ruta-precio")
    p.rep("tour privado de e-bike y café, desde $85, que incluye", "tour privado de e-bike y café que incluye"); p.save()

    p = Page("es/articles/canopy-en-boquete-tree-trek-y-opciones")
    p.rep("casco, guantes, mochila, agua, candado y rutas en Komoot", "casco, gafas, guantes, mochila, agua, poncho de lluvia y rutas en Komoot")
    n = p.add_src("bq-r")
    p.rep("desde $35, por períodos de 2 a 8 horas." + cite(21), "desde $35, por períodos de 2 a 8 horas." + cite(n)); p.save()

    p = Page("es/articles/el-valle-de-anton-con-ninos-familia")
    p.rep("<td>Desde $30</td>", "<td>Desde $35</td>")
    p.sub(r"E-Valley Bikes ofrece tours autoguiados en e-bike desde \$30\. Incluyen.*?pagaría desde \$120\.",
          "E-Valley Bikes alquila e-bikes por persona a $35 por 2 horas, $45 por 4 horas y $55 por 8 horas. Incluye casco, gafas, guantes, mochila, botella de agua y poncho de lluvia, y las rutas se descargan en la app Komoot. También tiene bicicletas para niños. La tienda está sobre la Avenida Principal, diagonal al mercado." + cite(14) + " Una familia de cuatro con cuatro e-bikes pagaría desde $140 por 2 horas.")
    p.rep("E-Valley Bikes ofrece tours autoguiados desde $30, con casco, audioguía, candado y canasta incluidos.",
          "E-Valley Bikes alquila e-bikes desde $35 por 2 horas, con casco, gafas, guantes, mochila, agua y poncho de lluvia incluidos, y tiene bicicletas para niños.")
    p.set_src(14, "elv-r"); p.save()

    p = Page("es/articles/el-valle-de-anton-en-un-dia-itinerario")
    p.rep("<b>$30–50</b><span class=\"s\">alquiler de 2 h a día completo", "<b>$35–55</b><span class=\"s\">alquiler de 2 a 8 horas")
    p.rep("<td>$60–64</td>", "<td>$65–69</td>")
    p.rep("<td>desde $84</td><td>5–6 h</td><td>Guía, equipo, refrigerios, entrada a la Piedra Pintada y almuerzo aparte</td>", "<td>desde $80</td><td>5–6 h</td><td>Guía y equipo; almuerzo aparte</td>")
    p.rep("$30 por 2 horas, $40 por 4 horas y $50 por el día completo, e incluye casco, candado y audioguía GPS.", "$35 por 2 horas, $45 por 4 horas y $55 por 8 horas, por persona, e incluye casco, gafas, guantes, mochila, agua y poncho de lluvia.")
    p.sub(r"El tour guiado de 3 horas aparece desde \$70 por persona.*?desde \$140 por 4 horas\." + re.escape(cite(14)),
          "También publica dos tours guiados de 2.5 a 3 horas. El Panoramic recorre el fondo del cráter, los miradores y el mercado, por $75 para una persona o $66 por persona en grupos de 2 o más. El Adventure va al Chorro El Macho y a la Piedra Pintada, por $85 para una persona o $75 por persona en grupo." + cite(14))
    p.rep("<td>$30 por bici</td>", "<td>$35 por persona</td>"); p.rep("<td>$40 por bici</td>", "<td>$45 por persona</td>")
    p.rep("<td>Alquiler día completo</td><td>$50 por bici</td><td>Todo el día</td>", "<td>Alquiler de 8 horas</td><td>$55 por persona</td><td>8 h</td>")
    p.rep("Casco, candado, audioguía GPS", "Casco, mochila, agua y poncho")
    p.sub(r"<tr><td>Tour guiado</td><td>desde \$70 por persona</td>.*?</tr>", "<tr><td>Tour Panoramic</td><td>$75, o $66 por persona en grupo</td><td>2.5–3 h</td><td>Guía y equipo; miradores y mercado</td><td>La mañana con guía, con salida a las 8:00 a. m.</td></tr>")
    p.sub(r"<tr><td>Tour privado</td><td>desde \$100</td>.*?</tr>", "<tr><td>Tour Adventure</td><td>$85, o $75 por persona en grupo</td><td>2.5–3 h</td><td>Guía y equipo; Chorro El Macho y Piedra Pintada</td><td>La mañana con guía, con salida a las 8:30 a. m.</td></tr>")
    p.sub(r"<tr><td>E-bike y canopy</td><td>desde \$140</td>.*?</tr>\s*", "")
    p.rep("Un alquiler de 4 horas por $40", "Un alquiler de 4 horas por $45")
    p.set_src(12, "elv-r"); p.set_src(14, "elv-t"); p.save()

    p = Page("es/articles/fin-de-semana-el-valle-de-anton-2-dias")
    p.rep("$3–5 / $30–40", "$3–5 / $35–45")
    p.rep("$30 por 2 horas, $40 por 4 horas y $50 por el día completo", "$35 por 2 horas, $45 por 4 horas y $55 por 8 horas")
    p.rep("$30 por 2 horas, $40 por 4 horas y $50 por el día", "$35 por 2 horas, $45 por 4 horas y $55 por 8 horas")
    n = p.add_src("elv-t")
    p.rep("en diagonal al mercado." + cite(14), "en diagonal al mercado." + cite(13))
    p.rep("El operador ofrece además un recorrido guiado de hasta 3 horas por la Piedra Pintada, el Cerro Cara Iguana y el mercado, de dificultad baja, por unos $65 por persona.",
          "El operador ofrece además dos tours guiados de 2.5 a 3 horas. El Panoramic pasa por los miradores del cráter y el mercado, por $75 para una persona o $66 por persona en grupos de 2 o más. El Adventure va al Chorro El Macho y a la Piedra Pintada, por $85 o $75 por persona en grupo." + cite(n))
    p.rep("súmele entre $30 y $50", "súmele entre $35 y $55"); p.rep("Más $30–50 si alquila", "Más $35–55 si alquila")
    p.rep("Una bicicleta convencional cuesta $10–15 al día. El tour guiado de hasta 3 horas ronda los $65 por persona.", "Una bicicleta convencional cuesta allí $20 por 2 horas. Los tours guiados de 2.5 a 3 horas cuestan desde $66 por persona en grupo.")
    p.set_src(13, "elv-r"); p.save()

    p = Page("es/articles/miradores-de-boquete-vistas-sin-subir-baru")
    p.rep("El alquiler libre de e-bike en Boquete empieza en $35." + cite(12) + " En reventa en línea, a noviembre de 2026, figura a $35 por 2 horas y $45 por 4 horas, con impuestos incluidos. El precio cubre la bicicleta, el casco, el agua y una bolsa, pero no las entradas ni el transporte al punto de salida.",
          "E-Valley Bikes alquila e-bikes en Boquete por persona a $35 por 2 horas, $45 por 4 horas y $55 por 8 horas. El precio cubre la bicicleta, el casco, las gafas, los guantes, la mochila, el agua y el poncho de lluvia, pero no las entradas.")
    p.rep("Si prefiere ir con guía, hay un tour de 2 horas en e-bike desde $55." + cite(18) + " Ese tour para 10 minutos en Los Ladrillos, 15 en la cascada de San Ramón y 30 en un café de especialidad." + cite(19),
          "Si prefiere ir con guía, E-Valley Bikes tiene tours privados de 2.5 a 3 horas desde $75 por persona en grupos de 2 o más, o $100 para una persona." + cite(18))
    p.rep("y unos $45 por cuatro", "y $45 por cuatro")
    p.rep("Un tour guiado de 2 horas en e-bike cuesta desde $55.", "Un tour guiado de 2.5 a 3 horas cuesta desde $75 por persona en grupo.")
    p.rep("<strong>desde $55</strong>por persona</span><span><strong>2 h</strong>", "<strong>desde $75</strong>por persona en grupo</span><span><strong>2.5-3 h</strong>")
    p.set_src(17, "bq-r"); p.set_src(18, "bq-t"); p.drop_src(19); p.save()

    p = Page("es/articles/miradores-el-valle-de-anton")
    p.rep('<b>$30-50</b><span class="s">De 2 horas a día completo', '<b>$35-55</b><span class="s">De 2 a 8 horas')
    p.rep("<strong>$30</strong>por 2 horas", "<strong>$35</strong>por 2 horas")
    p.rep("<strong>$65</strong>e-bike guiado por persona", "<strong>$66</strong>e-bike guiado, por persona en grupo")
    p.sub(r"E-Valley Bikes publica alquileres de \$30.*?confirme el precio en el local antes de salir\.",
          "E-Valley Bikes publica alquileres de $35 por 2 horas, $45 por 4 horas y $55 por 8 horas, con casco, gafas, guantes, mochila, agua y poncho de lluvia incluidos." + cite(18))
    p.rep("E-Valley Bikes tiene un tour guiado en e-bike de $65 por persona por los puntos más destacados del valle." + cite(18),
          "E-Valley Bikes tiene un tour Panoramic en e-bike por el fondo del cráter, por $75 para una persona o $66 por persona en grupos de 2 o más." + cite(19))
    p.rep("el alquiler cuesta $30 por 2 horas o $50 por día completo", "el alquiler cuesta $35 por 2 horas o $55 por 8 horas")
    p.set_src(18, "elv-r"); p.set_src(19, "elv-t"); p.save()

    p = Page("es/articles/sendero-el-pianista-boquete-ruta-dificultad")
    p.rep("En Boquete las e-bikes se alquilan desde $35 al día, con casco, guantes, gafas, mochila con botella de agua, candado y rutas cargadas en la app Komoot." + cite(14) + " E-Valley Bikes, en la Av. A Este 0413 de Bajo Boquete, publica alquileres desde $35 por persona, de 2 a 8 horas." + cite(15),
          "E-Valley Bikes, en la Av. A Este 0413 de Bajo Boquete, alquila e-bikes por persona a $35 por 2 horas, $45 por 4 horas y $55 por 8 horas, con casco, guantes, gafas, mochila con botella de agua, poncho de lluvia y rutas para descargar en la app Komoot." + cite(15))
    p.rep("deje la bici con candado, fuera del camino", "deje la bici fuera del camino")
    p.set_src(15, "bq-r"); p.drop_src(14); p.save()

    p = Page("es/articles/sendero-los-quetzales-quetzal-boquete")
    p.rep("Desde $35/día.", "Desde $35."); p.save()


def h1(f):
    x = f.read_text(errors="ignore"); m = re.search(r"<h1[^>]*>(.*?)</h1>", x, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else f.stem


def twins():
    t = {}
    for f in ALL:
        for tag in re.findall(r"<link\b[^>]*hreflang=[^>]*>", f.read_text(errors="ignore")):
            l = re.search(r'hreflang="([^"]+)"', tag)[1]; u = re.search(r'href="https://panamaspot\.com/([^"]*)"', tag)
            if u and l in ("en", "es") and u[1] != key(f): t.setdefault(key(f), {})[l] = u[1]
    return t


def crosslinks():
    t = twins()
    for f in V2:
        h = f.read_text(); me = key(f); es = me.startswith("es/")
        pre = "articles/" if es else "es/articles/"; other = "en" if not es else "es"
        def fix(m):
            target = m[1]; tw = t.get(target, {}).get("en" if not es else "es")
            if tw and tw != me and (P / (tw + ".html")).exists():
                return f'<a href="https://panamaspot.com/{tw}" rel="noopener" target="_blank">PanamaSpot - {html.escape(h1(P / (tw + ".html")), quote=False)}</a>'
            return f"<span>{m[2]}</span>"
        i = h.find('class="src-list"')
        if i >= 0:
            j = h.index("</ol>", i)
            seg = re.sub(rf'<a href="https://panamaspot\.com/({pre}[^"]+)"[^>]*>(.*?)</a>', fix, h[i:j], flags=re.S)
            h = h[:i] + seg + h[j:]
        f.write_text(h)
    p = Page("articles/diving-in-panama")
    p.sub(r' Readers who prefer Spanish can use our <a href="/es/articles/isla-coiba-buceo-parque-nacional">.*?</a>\.', ""); p.save()
    p = Page("articles/volcan-baru-national-park-entry-facts-active")
    p.sub(r"<li><strong>Reading in Spanish:</strong>.*?</li>\s*", ""); p.save()
    p = Page("es/articles/isla-coiba-buceo-parque-nacional")
    p.sub(r"<p>Si quiere una versión en inglés para compartir.*?</p>\s*", ""); p.save()
    p = Page("es/articles/tour-de-cafe-boquete-fincas-precios-reservar")
    p.sub(r"<p>Si lee inglés, la <a.*?</p>\s*", ""); p.save()
    p = Page("es/articles/restaurantes-y-cafeterias-en-boquete")
    p.rep('<a href="/articles/boquete-coffee-farm-tour">comparativa de tours', '<a href="/es/articles/tour-de-cafe-boquete-fincas-precios-reservar">comparativa de tours')
    p.sub(r'Para comparar las fincas una por una, con duración y si incluyen Geisha, está la <a href="/articles/boquete-coffee-farm-tour">.*?</a> \(en inglés\)\. La guía en español de ', "La guía en español de ")
    p.save()


def headings():
    for f in V2:
        h = f.read_text()
        # a step title sits one level under its section: h3 under an h2, h4 under an h3
        b = h.find("<body")
        def walk(seg):
            res = []; pos = 0; prev = 0; group = None
            for m in re.finditer(r'<div class="steps">|<h([1-6])\b([^>]*)>|</h([1-6])>', seg):
                if m[0] == '<div class="steps">':
                    group = "h3" if prev == 2 else None; continue
                if m[3]:
                    if m[3] == "4" and stack and stack[-1] == "x":
                        res.append(seg[pos:m.start()] + "</h3>"); pos = m.end(); stack.pop()
                    elif stack: stack.pop()
                    continue
                lvl = int(m[1])
                is_step = lvl == 4 and seg[max(0, m.start() - 60):m.start()].rfind('<span class="n">') >= 0
                if is_step and prev == 2 or is_step and group == "h3":
                    group = "h3"; res.append(seg[pos:m.start()] + "<h3" + m[2] + ">"); pos = m.end(); stack.append("x"); continue
                stack.append("o")
                if not is_step: prev = lvl
            res.append(seg[pos:]); return "".join(res)
        stack = []
        h = h[:b] + walk(h[b:])
        h = h.replace(".step h4 {", ".step h4, .steps .step h3 {").replace(".step h4 small {", ".step h4 small, .steps .step h3 small {")
        h = h.replace(".f-grid h5", ".f-grid h4").replace(".f-grid { display: grid; grid-template-columns: repeat(6, 1fr);", ".f-grid { display: grid; grid-template-columns: repeat(7, 1fr);")
        f.write_text(h)


EN_LABEL = {"best-time-to-visit-boquete": "Best time to visit", "boquete-bike-rental": "E-bike rental", "boquete-cycling-routes": "Cycling routes", "boquete-flower-and-coffee-fair-visitor-guide": "Flower and Coffee Fair", "boquete-to-bocas-del-toro-shuttle-bus-timing": "Boquete to Bocas", "boquete-travel-guide": "Boquete in 3 days", "boquete-with-kids-family-guide": "Boquete with kids", "caldera-hot-springs-boquete": "Caldera Hot Springs", "el-pianista-trail-boquete": "El Pianista Trail", "finca-lerida-los-quetzales-trail-birdwatching-boquete": "Finca Lérida and Los Quetzales", "geisha-coffee-boquete-where-to-taste": "Geisha coffee", "pipeline-trail-boquete-quetzal-hike": "Pipeline Trail", "tours-in-boquete-panama": "Tours", "volcan-baru-national-park-entry-facts-active": "Volcán Barú National Park", "where-to-eat-in-boquete": "Where to eat",
            "birding-el-valle-de-anton-trails-lodges-season": "Birding", "cerro-gaital-cara-iguana-hike-el-valle": "Cerro Gaital and Cara Iguana", "chorro-las-mozas-swimming-falls-el-valle": "Chorro Las Mozas", "el-valle-de-anton-hot-springs-prices-hours-getting-there": "Hot springs", "el-valle-de-anton-itinerary-one-day": "El Valle in one day", "piedra-pintada-painted-rock-el-valle-de-anton": "Piedra Pintada", "tours-en-el-valle-de-anton": "Tours", "where-to-eat-el-valle-de-anton": "Where to eat",
            "where-to-stay-in-panama-city": "Where to stay", "panama-canal-boat-tours": "Canal boat tours",
            "contadora-ferry-from-panama-city": "Contadora ferry", "diving-in-panama": "Diving in Panama", "panama-all-inclusive-resorts": "All-inclusive resorts", "panama-surf-camps": "Surf camps", "playa-venao-panama": "Playa Venao", "san-blas-tours-from-panama-city": "San Blas tours",
            "best-waterfalls-in-panama-where-to-see-several": "Waterfalls in Panama", "hiking-in-panama-best-trails": "Hiking in Panama",
            "buying-property-in-panama-as-a-foreigner": "Buying property", "healthcare-in-panama-for-foreigners": "Healthcare for foreigners", "panama-residency-visas": "Residency visas", "retiring-in-panama": "Retiring in Panama", "stem-cell-therapy-in-panama": "Stem cell therapy"}
EN_GROUP = {"where-to-stay-in-panama-city": "Panama City", "panama-canal-boat-tours": "Panama City", "contadora-ferry-from-panama-city": "Islands and sea", "diving-in-panama": "Islands and sea", "panama-all-inclusive-resorts": "Islands and sea", "panama-surf-camps": "Islands and sea", "playa-venao-panama": "Islands and sea", "san-blas-tours-from-panama-city": "Islands and sea", "best-waterfalls-in-panama-where-to-see-several": "Plan your trip", "hiking-in-panama-best-trails": "Plan your trip"}
LIVING = ["buying-property-in-panama-as-a-foreigner", "panama-residency-visas", "retiring-in-panama", "healthcare-in-panama-for-foreigners", "stem-cell-therapy-in-panama"]
ES_LABEL = {"cerro-la-silla-sendero-amanecer-el-valle": "Cerro La Silla", "boquete": "Guía de Boquete", "el-valle-de-anton": "Guía de El Valle", "panama-city": "Guía de Ciudad de Panamá", "aguas-termales-caldera-boquete": "Aguas termales de Caldera", "aguas-termales-el-valle-de-anton": "Pozos termales", "alquiler-de-bicicletas-boquete": "Alquiler de e-bikes", "avistamiento-de-aves-el-valle-de-anton": "Avistamiento de aves", "bajo-mono-boquete-circuito-y-senderos": "Bajo Mono", "boquete-panama-guia-completa-itinerario": "Itinerario de Boquete", "bus-albrook-el-valle-de-anton-horarios-precios": "Bus desde Albrook", "canopy-el-valle-de-anton-cabalgatas-aventura": "Canopy y cabalgatas", "canopy-en-boquete-tree-trek-y-opciones": "Canopy", "cascada-chorro-el-macho-el-valle-de-anton": "Chorro El Macho", "cascadas-el-valle-de-anton-como-llegar": "Cascadas", "cascadas-perdidas-boquete-ruta-precio": "Cascadas Perdidas", "casco-viejo-restaurantes-donde-comer-beber-hospedarse": "Casco Viejo", "cerro-gaital-cara-iguana-rutas-dificultad": "Cerro Gaital y Cara Iguana", "chorro-las-mozas-pozas-el-valle-de-anton": "Chorro Las Mozas", "cinta-costera-panama-mercado-mariscos-panama-viejo": "Cinta Costera y Panamá Viejo", "como-llegar-a-bocas-del-toro-desde-ciudad-de-panama": "Cómo llegar a Bocas", "como-llegar-a-boquete-sin-carro": "Cómo llegar sin carro", "cuanto-cuesta-boquete-presupuesto-semana": "Cuánto cuesta", "donde-comer-en-el-valle-de-anton": "Dónde comer", "donde-dormir-el-valle-de-anton": "Dónde dormir", "donde-dormir-en-boquete-hoteles-cabanas-hospedaje": "Dónde dormir", "el-valle-de-anton-con-ninos-familia": "El Valle con niños", "el-valle-de-anton-desde-ciudad-de-panama": "Desde Ciudad de Panamá", "el-valle-de-anton-en-un-dia-itinerario": "El Valle en un día", "el-volcan-baru-esta-activo": "¿Está activo el Volcán Barú?", "feria-de-las-flores-y-del-cafe-boquete": "Feria de las Flores y del Café", "fin-de-semana-el-valle-de-anton-2-dias": "Fin de semana", "hoteles-en-casco-viejo": "Hoteles en el Casco Viejo", "isla-coiba-buceo-parque-nacional": "Buceo y Coiba", "mariposario-el-valle-de-anton": "Mariposario y serpentario", "mercado-el-valle-de-anton": "Mercado", "mi-jardin-es-su-jardin-boquete": "Mi Jardín es Su Jardín", "miradores-de-boquete-vistas-sin-subir-baru": "Miradores", "miradores-el-valle-de-anton": "Miradores", "piedra-pintada-el-valle-de-anton": "Piedra Pintada", "precios-horarios-el-valle-de-anton": "Precios y horarios", "que-hacer-el-valle-de-anton": "Qué hacer", "que-hacer-en-boquete-guia-completa": "Qué hacer", "que-hacer-en-ciudad-de-panama": "Qué hacer", "rafting-boquete-rio-chiriqui": "Rafting", "restaurantes-y-cafeterias-en-boquete": "Restaurantes y cafeterías", "san-blas-guna-yala-guia-tours-islas": "San Blas", "senderismo-en-panama-mejores-senderos-ciudad": "Senderismo en Panamá", "sendero-el-pianista-boquete-ruta-dificultad": "Sendero El Pianista", "sendero-india-dormida-el-valle-de-anton": "La India Dormida", "sendero-los-quetzales-quetzal-boquete": "Sendero Los Quetzales", "senderos-el-valle-de-anton": "Senderos", "senderos-en-boquete-guia-completa": "Senderos", "tour-de-cafe-boquete-fincas-precios-reservar": "Tour de café", "tours-el-valle-de-anton": "Tours", "tours-en-bicicleta-el-valle-de-anton": "Tours en bicicleta", "tours-en-boquete-panama": "Tours", "volcan-baru-como-subir-cima-panama": "Subir al Volcán Barú", "zoologico-el-nispero-el-valle-de-anton": "Zoológico El Níspero", "cascadas-en-panama-mejores-como-llegar": "Cascadas en Panamá", "lugares-turisticos-chiriqui": "Lugares turísticos de Chiriquí", "lugares-turisticos-de-cocle": "Lugares turísticos de Coclé", "boquete-con-ninos-guia-familiar": "Boquete con niños"}


def crumb(x):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', x, re.S):
        try: d = json.loads(m[1])
        except ValueError: continue
        for g in (d.get("@graph", [d]) if isinstance(d, dict) else d):
            if isinstance(g, dict) and g.get("@type") == "BreadcrumbList":
                n = [i.get("name") for i in g.get("itemListElement", [])]
                return n[1] if len(n) > 2 else ""
    return ""


def grid(cols, base):
    out = []
    for name, items in cols:
        li = "".join(f'<li><a href="{base}{s}">{html.escape(l, quote=False)}</a></li>' for s, l in items)
        out.append(f"<div><h4>{name}</h4><ul>{li}</ul></div>")
    return "".join(out)


def directory():
    def block_end(h, i):
        depth = 0
        for m in re.finditer(r"<div\b|</div>", h[i:]):
            depth += 1 if m[0] != "</div>" else -1
            if depth == 0: return i + m.end()
    sample = (P / "articles/geisha-coffee-boquete-where-to-taste.html").read_text()
    i = sample.index('<div class="wrap f-dir">'); blk = sample[i:block_end(sample, i)]
    cols = {}; order = []; seen = set()
    for name, ul in re.findall(r"<h[45]>(.*?)</h[45]><ul>(.*?)</ul>", blk, re.S):
        items = [(s, html.unescape(l)) for s, l in re.findall(r'href="/articles/([^"]+)">(.*?)</a>', ul)]
        cols[name] = items; order.append(name); seen.update(s for s, _ in items)
    for f in sorted(P.glob("articles/*.html")):
        s = f.stem
        if s in seen or s in LIVING: continue
        if s not in EN_LABEL: raise SystemExit("no EN label: " + s)
        g = EN_GROUP.get(s) or {"Boquete": "Boquete", "El Valle de Antón": "El Valle de Antón"}.get(crumb(f.read_text(errors="ignore")))
        if not g: raise SystemExit("no EN group: " + s)
        cols[g].append((s, EN_LABEL[s]))
    cols["Living in Panama"] = [(s, EN_LABEL[s]) for s in LIVING]; order.append("Living in Panama")
    en = grid([(n, cols[n]) for n in order], "/articles/")
    ES_G = {"Boquete": "Boquete", "El Valle de Antón": "El Valle de Antón", "Ciudad de Panamá": "Ciudad de Panamá"}
    es = {k: [] for k in ("Ciudad de Panamá", "Bocas del Toro", "Boquete", "El Valle de Antón", "Islas y mar", "Por todo Panamá")}
    over = {"boquete": "Boquete", "el-valle-de-anton": "El Valle de Antón", "panama-city": "Ciudad de Panamá", "hoteles-en-casco-viejo": "Ciudad de Panamá", "como-llegar-a-bocas-del-toro-desde-ciudad-de-panama": "Bocas del Toro", "isla-coiba-buceo-parque-nacional": "Islas y mar", "san-blas-guna-yala-guia-tours-islas": "Islas y mar", "cascadas-en-panama-mejores-como-llegar": "Por todo Panamá", "senderismo-en-panama-mejores-senderos-ciudad": "Por todo Panamá"}
    hubs = {"boquete", "el-valle-de-anton", "panama-city"}
    for f in sorted(P.glob("es/articles/*.html")):
        s = f.stem
        if s not in ES_LABEL: raise SystemExit("no ES label: " + s)
        g = over.get(s) or ES_G.get(crumb(f.read_text(errors="ignore")))
        if not g: raise SystemExit("no ES group: " + s)
        (es[g].insert(0, (s, ES_LABEL[s])) if s in hubs else es[g].append((s, ES_LABEL[s])))
    es_html = grid([(k, v) for k, v in es.items() if v], "/es/articles/")
    for f in V2:
        h = f.read_text(); i = h.index('<div class="wrap f-dir">'); j = block_end(h, i)
        if key(f).startswith("es/"):
            new = f'<div class="wrap f-dir"><div class="f-dir-hd"><h3>Todas las guías</h3><span>Guías en español</span></div><div class="f-grid">{es_html}</div></div>'
        else:
            new = f'<div class="wrap f-dir"><div class="f-dir-hd"><h3>Every guide</h3><span>Guides in English</span></div><div class="f-grid">{en}</div></div>'
        f.write_text(h[:i] + new + h[j:])


# prices(), crosslinks() and headings() are one-shot and already applied; directory() can be re-run.
directory(); print("done")
