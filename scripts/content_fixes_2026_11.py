"""Hand-reviewed corrections to old-guide text (user approved 2026-11-05). One-shot: stops if an expected text is missing.
Only claims naming E-Valley Bikes that its own site contradicts (evalleybikes.net, read 2026-11-05):
rental $35/$45/$55 per 2/4/8 h per person; El Valle tours $75 or $66 (Panoramic), $85 or $75 (Adventure);
kit helmet, goggles, gloves, backpack, water, rain poncho, Komoot routes; no lock, audio guide, basket or free cancellation
listed; open Mon-Sun 8-17. Other companies' prices are not touched. Applies to visible text and FAQ schema alike.
"""
import re, sys
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "public"
KE = "a helmet, gloves, backpack, water and rain poncho"
KS = "casco, gafas, guantes, mochila, agua y poncho de lluvia"
E = {
"articles/boquete-bike-rental": [
 ("helmet, cable lock, backpack", "helmet, backpack"),
 (" — the cable lock is included for exactly this purpose.", "."),
 ("They operate Monday and Wednesday through Sunday, 8:00 am to 5:00 pm (closed Tuesdays as of the latest available information — confirm before arriving).", "They are open Monday to Sunday, 8:00 am to 5:00 pm."),
],
"articles/boquete-travel-guide": [("Their tours include helmets, a route audio guide, and a lock — useful when you stop for a tasting.", f"Their rentals include {KE}, plus routes to download in the Komoot app.")],
"articles/cerro-gaital-cara-iguana-hike-el-valle": [("rents electric bikes from $30/day with helmet and lock included", "rents electric bikes from $35 for 2 hours with helmet and gear included"), ("($30/day)", "($35 for 2 hours)")],
"articles/chorro-el-macho-waterfall-el-valle-de-anton": [
 ("From $30/bike", "From $35"),
 ("rents electric bikes from $30 per bike with a helmet, audio guide, and lock included — the audio guide covers the main sites along the route, which makes it a surprisingly good value for solo travelers or couples who want context without a group tour.", f"rents electric bikes from $35 for 2 hours with {KE} included, plus routes to download in the Komoot app, which makes it a good value for solo travelers or couples who want to set their own pace."),
],
"articles/day-trips-from-panama-city": [("offers e-bike rentals from $30 per bike", "offers e-bike rentals from $35 for 2 hours"), ("Helmets, a lock, and an audio route guide are included.", "A helmet, gloves, backpack, water and rain poncho are included."), ("Add $30 for an e-bike rental", "Add $35–$55 for an e-bike rental")],
"articles/el-valle-day-trip-from-panama-city": [("Rentals include a helmet, audio guide, and lock.", "Rentals include a helmet, gloves, a backpack, water and a rain poncho.")],
"articles/el-valle-de-anton-itinerary-one-day": [("rents e-bikes from $30 per bike with a helmet, lock, and audio guide included", f"rents e-bikes from $35 for 2 hours with {KE} included"), ("from around $30/day with E-Valley Bikes", "from $35 for 2 hours with E-Valley Bikes"), ("includes helmet + lock", "includes helmet and gear")],
"articles/el-valle-de-anton-vs-boquete": [("Rentals start around $30 per bike with helmet and audio guide included", "Rentals start at $35 for 2 hours with helmet and gear included")],
"articles/el-valle-de-anton-waterfalls": [("rents electric bikes from $30 per bike, with helmets and a lock included", "rents electric bikes from $35 for 2 hours, with a helmet and gear included"), ("rents electric bikes from $30 per bike, which makes", "rents electric bikes from $35 for 2 hours, which makes")],
"articles/el-valle-de-anton-with-kids": [("bikes and seats, making", "bikes, making"), ("bikes and seats for younger riders", "bikes for younger riders")],
"articles/india-dormida-hike-el-valle-de-anton": [("ride to the trailhead, lock up, hike", "ride to the trailhead, hike"), ("From $30/bike", "From $35"), ("you can lock up at the trailhead, do the hike", "you can ride to the trailhead, do the hike"), ("rents electric bikes with helmets, locks, and a route audio guide included, starting at $30 per bike", f"rents electric bikes with {KE} included, starting at $35 for 2 hours")],
"articles/where-to-stay-in-el-valle-de-anton": [("located near the tourist information center on the east side of Avenida Principal, rents electric bikes from $30 per day", "located on Avenida Principal, diagonally across from the market, rents electric bikes from $35 for 2 hours")],
"articles/tours-en-el-valle-de-anton": [
 ("Solo riders pay slightly more.", "One rider alone pays $75–$85."),
 ("$65 per person", "$66–$75 per person"),
 ("$65 pp (2+ people)", "$66–$75 pp (2+ people)"),
 ("~$30–$40/hr", "$35 for 2 h, $45 for 4 h, $55 for 8 h"),
 ("($65 pp)", "($66–$75 pp)"),
 ("$110–$130", "$110–$140"),
 ("$150–$180", "$150–$190"),
 ("are $65 pp for two or more, with the solo rate higher", "are $66–$75 pp for two or more, with the solo rate at $75–$85"),
],
"es/articles/aguas-termales-el-valle-de-anton": [("Desde $30/día (alquiler)", "Desde $35 (alquiler)"), ("desde $30 por día con casco, guía de audio y candado incluidos", f"desde $35 por 2 horas con {KS} incluidos")],
"es/articles/bus-albrook-el-valle-de-anton-horarios-precios": [("desde $30 por bicicleta, con casco y guía de audio incluidos", "desde $35 por 2 horas, con casco y equipo incluidos"), ("con E-Valley Bikes desde $30", "con E-Valley Bikes desde $35")],
"es/articles/canopy-el-valle-de-anton-cabalgatas-aventura": [("desde $30 por bicicleta, con casco, guía de audio y candado incluidos", f"desde $35 por 2 horas, con {KS} incluidos"), ("e-bike medio día $30", "e-bike medio día $45"), ("~$160 USD", "~$175 USD")],
"es/articles/cascada-chorro-el-macho-el-valle-de-anton": [("desde $30 por día con casco, candado y audioguía incluidos", f"desde $35 por 2 horas con {KS} incluidos"), ("e-bikes desde $30/día con casco y audioguía incluidos", "e-bikes desde $35 por 2 horas con casco y equipo incluidos"), ("Desde $30/día", "Desde $35")],
"es/articles/chorro-las-mozas-pozas-el-valle-de-anton": [("Desde $30/día", "Desde $35"), ("alquiler por día desde $30, con casco y guía de audio incluidos", "alquiler desde $35 por 2 horas, con casco y equipo incluidos")],
"es/articles/como-llegar-a-boquete-sin-carro": [("con casco, guía de audio y candado incluidos", f"con {KS} incluidos")],
"es/articles/cuanto-cuesta-boquete-presupuesto-semana": [("con guía incluido, por alrededor de $35–45 por persona", "con guía incluido, desde $75 por persona en grupos de 2 o más"), ("cuesta alrededor de $30/día", "cuesta desde $35 por 2 horas")],
"es/articles/donde-dormir-el-valle-de-anton": [("desde $30 por bicicleta, con casco y candado incluidos", "desde $35 por 2 horas, con casco y equipo incluidos")],
"es/articles/el-valle-de-anton-desde-ciudad-de-panama": [("desde aproximadamente $30 por bicicleta", "desde $35 por 2 horas"), ("desde aproximadamente $30 por día", "desde $35 por 2 horas")],
"es/articles/mariposario-el-valle-de-anton": [("(desde $30 por bici)", "(desde $35 por 2 horas)")],
"es/articles/mercado-el-valle-de-anton": [("desde $30 por bicicleta, con casco y guía de audio incluidos", "desde $35 por 2 horas, con casco y equipo incluidos")],
"es/articles/mi-jardin-es-su-jardin-boquete": [("Desde $30/día", "Desde $35"), ("ofrecen alquiler por día con casco y guía de audio incluidos", "ofrecen alquiler desde 2 horas con casco y equipo incluidos"), ("($30–35/día)", "(desde $35)"), ("incluyen casco, candado y guía de audio, y permiten", "incluyen casco y equipo, y permiten")],
"es/articles/piedra-pintada-el-valle-de-anton": [("con casco y candado desde $30", "con casco y equipo desde $35")],
"es/articles/precios-horarios-el-valle-de-anton": [("desde $30 por bicicleta con casco, guía de audio y candado incluidos", f"desde $35 por 2 horas con {KS} incluidos")],
"es/articles/que-hacer-el-valle-de-anton": [("El tour guiado cuesta $65 por persona e incluye", "El tour guiado cuesta desde $66 por persona en grupo e incluye"), ("($65 p/p)", "(desde $66 p/p)")],
"es/articles/senderos-el-valle-de-anton": [("$65/persona", "Desde $66/persona"), ("tours en bicicleta eléctrica desde $65", "tours en bicicleta eléctrica desde $66")],
"es/articles/sendero-india-dormida-el-valle-de-anton": [("Desde $30/día (alquiler)", "Desde $35 (alquiler)"), ("desde $30 por bici al día, con casco y guía de audio incluidos", "desde $35 por 2 horas, con casco y equipo incluidos")],
"es/articles/zoologico-el-nispero-el-valle-de-anton": [("desde $30 por bici, con casco, candado y guía de audio incluidos", f"desde $35 por 2 horas, con {KS} incluidos")],
"es/articles/tours-el-valle-de-anton": [
 ("$65/persona", "$66–$75/persona"), ("$85/persona", "$75–$85/persona"),
 ("<td>$20–$50</td><td>1 h–1 día</td><td>Casco, candado, rutas sugeridas</td>", f"<td>$35–$55</td><td>2–8 h</td><td>Casco, mochila, agua, poncho, rutas</td>"),
 ("(frente a $60 para grupos de 2+)", "(frente a $66 para grupos de 2+)"),
 (" Aquí también está ubicado E-Valley Bikes, lo que facilita reservar el tour de e-bike directamente desde el hotel.", ""),
 ("3 horas, $65 con E-Valley Bikes", "3 horas, desde $66 con E-Valley Bikes"),
 ("clásico de $65 incluye", "clásico, desde $66, incluye"),
],
"es/articles/tours-en-bicicleta-el-valle-de-anton": [
 ("te dan casco y candado", "te dan casco y equipo"),
 ("La audioguía GPS que E-Valley incluye con el alquiler cubre buena parte de ese hueco: va narrando cada parada a medida que llegas, sin depender de un grupo.", "Las rutas de E-Valley en la app Komoot ayudan a orientarse, pero el contexto corre por tu cuenta."),
 ("Alquiler de e-bike autoguiado, con audioguía GPS", "Alquiler de e-bike autoguiado, con rutas en Komoot"),
 ("2 h · 4 h · día completo", "2 h · 4 h · 8 h"), ("$30 · $40 · $50 por bici", "$35 · $45 · $55 por persona"),
 ("$30 por bici por 2 horas, $40 por 4 horas y $50 por el día completo, con casco, candado y una audioguía GPS que va narrando cada parada.", f"$35 por 2 horas, $45 por 4 horas y $55 por 8 horas, con {KS}. También ofrece tours guiados de 2.5 a 3 horas, desde $66 por persona en grupo."),
 ("$30 por bici por 2 horas, $40 por 4 horas y $50 por el día completo, con casco, candado y audioguía GPS incluidos.", f"$35 por 2 horas, $45 por 4 horas y $55 por 8 horas, con {KS} incluidos."),
 ("$30 por bici por 2 horas, $40 por 4 horas y $50 por el día completo, con casco, candado y audioguía GPS. Los tours guiados no publican tarifa fija: hay que consultarla.", f"$35 por 2 horas, $45 por 4 horas y $55 por 8 horas, con {KS}. Sus tours guiados cuestan desde $66 por persona en grupo."),
 ("$30 por bici por 2 horas, $40 por 4 horas y $50 por el día completo", "$35 por 2 horas, $45 por 4 horas y $55 por 8 horas"),
 ("según disponibilidad y cancela gratis hasta 24 horas antes, así que reservar temprano no te ata a nada.", "según disponibilidad."),
 ("según disponibilidad y cancela gratis hasta 24 horas antes, así que reservar temprano no te compromete a nada.", "según disponibilidad."),
 ("E-Valley Bikes entrega además candado y canasta delantera con cada bici, lo que resuelve el problema de dónde dejar la mochila y la bici cuando paras a caminar hasta una cascada.", "E-Valley Bikes entrega además gafas, guantes, mochila, agua y poncho de lluvia con cada bici."),
 ("decides el ritmo, las paradas y el recorrido, y en el caso de E-Valley la audioguía GPS te va dando el contexto en cada punto.", "decides el ritmo, las paradas y el recorrido."),
 ("casco, candado, canasta delantera y una audioguía GPS que va narrando cada parada.", f"{KS}."),
 ("<b>$30</b><p>", "<b>$35</b><p>"), ("<li>$30: Alquiler", "<li>$35: Alquiler"),
],
# Feria de las Flores is a January fair, not a weekly market
"articles/panama-city-to-boquete": [("The Tuesday market (Feria de las Flores y del Café) is", "The Tuesday market is")],
"articles/volcan-baru-hike-sunrise-summit-guide": [("The Saturday farmers' market (Feria de las Flores y del Café) runs", "The Saturday farmers' market runs"), ],
}
problems = []; n = 0; touched = 0
out = {}
for rel, edits in E.items():
    f = P / (rel + ".html"); h = f.read_text(); before = h
    for a, b in edits:
        cands = [a, a.replace("'", "&#x27;"), a.replace("'", "&#39;"), a.replace("'", "’")]
        hit = next((c for c in cands if c in h), None)
        if hit is None:
            problems.append(f"{rel}: not found: {a[:80]}"); continue
        n += h.count(hit); h = h.replace(hit, b)
    if h != before: out[f] = h
if "--dry" in sys.argv or problems:
    print("\n".join(problems) or "all found"); print(f"{n} replacements on {len(out)} pages (nothing written)")
    sys.exit(1 if problems else 0)
for f, h in out.items(): f.write_text(h)
print(f"{n} replacements on {len(out)} pages")
