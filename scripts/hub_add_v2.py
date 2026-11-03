#!/usr/bin/env python3
"""Add the V2 guides to their destination hubs: a row in the matching themed group and an entry in
the numbered "Every … guide" index (the hub's count is updated). Skips any guide the hub already links.
Edits the hub HTML in place (build-hub.py output has hand edits since, so the hubs are not rebuilt).

    python3 scripts/hub_add_v2.py
"""
import re, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUB = ROOT / "public"

# hub -> [(group heading, href, short name, one-line description, index title, index category)]
ADD = {
 "articles/boquete": [
  ("Trails and the volcano", "/articles/el-pianista-trail-boquete", "El Pianista Trail", "The trailhead, the climb, and whether you need a guide.", "El Pianista Trail", "Hiking"),
  ("Trails and the volcano", "/articles/pipeline-trail-boquete-quetzal-hike", "The Pipeline Trail", "The quetzal hike: access, distance and the best hours to look.", "Pipeline Trail Quetzal Hike", "Hiking"),
  ("Trails and the volcano", "/articles/volcan-baru-national-park-entry-facts-active", "Volcán Barú National Park", "Entry rules, safety and whether the volcano is active.", "Volcán Barú National Park", "Volcano"),
  ("Coffee, cloud forest and birds", "/articles/geisha-coffee-boquete-where-to-taste", "Geisha Coffee", "Where to taste it, what tastings cost and how to book.", "Geisha Coffee: Where to Taste It", "Coffee"),
  ("Planning: when to come, where to sleep", "/articles/where-to-eat-in-boquete", "Where to Eat", "Restaurants near the centre, what to order and which need a car.", "Where to Eat in Boquete", "Food"),
  ("Planning: when to come, where to sleep", "/articles/boquete-with-kids-family-guide", "Boquete With Kids", "Easy trails, gentle bike routes and rainy-day ideas.", "Boquete with Kids", "Family"),
  ("Planning: when to come, where to sleep", "/articles/boquete-flower-and-coffee-fair-visitor-guide", "The Flower and Coffee Fair", "January dates, venues and getting around during the fair.", "Flower and Coffee Fair", "Events"),
  ("Planning: when to come, where to sleep", "/articles/boquete-to-bocas-del-toro-shuttle-bus-timing", "On to Bocas del Toro", "Shuttle or bus, the boat leg and realistic travel time.", "Boquete to Bocas del Toro", "Getting there"),
 ],
 "articles/el-valle-de-anton": [
  ("Trails and summits", "/articles/hiking-in-panama-best-trails", "Hiking in Panama", "The best trails in the country, starting from the crater.", "Hiking in Panama: Best Trails", "Hiking"),
  ("Trails and summits", "/articles/piedra-pintada-painted-rock-el-valle-de-anton", "Piedra Pintada", "The painted rock, how to reach it and what is nearby.", "Piedra Pintada: The Painted Rock", "Culture"),
  ("Trails and summits", "/articles/birding-el-valle-de-anton-trails-lodges-season", "Birding in El Valle", "Trails, the Canopy Lodge, guided tours and the best months.", "Birding in El Valle de Antón", "Birding"),
  ("Waterfalls and hot water", "/articles/chorro-las-mozas-swimming-falls-el-valle", "Chorro Las Mozas", "The swimming falls: trail time from town and the pools.", "Chorro Las Mozas", "Waterfalls"),
  ("Waterfalls and hot water", "/articles/el-valle-de-anton-hot-springs-prices-hours-getting-there", "The Hot Springs", "Entry prices, hours and how to reach the pools.", "El Valle Hot Springs", "Hot springs"),
  ("Waterfalls and hot water", "/articles/best-waterfalls-in-panama-where-to-see-several", "Panama's Best Waterfalls", "Using El Valle as the base to see several in one day.", "Best Waterfalls in Panama", "Waterfalls"),
  ("Planning the visit", "/articles/where-to-eat-el-valle-de-anton", "Where to Eat", "The restaurants worth it, the Sunday market and what to order.", "Where to Eat in El Valle de Antón", "Food"),
 ],
 "es/articles/boquete": [
  ("Senderos y el volcán", "/es/articles/sendero-el-pianista-boquete-ruta-dificultad", "Sendero El Pianista", "Distancia, desnivel, tiempo y cómo llegar al inicio.", "Sendero El Pianista", "Senderismo"),
  ("Senderos y el volcán", "/es/articles/cascadas-perdidas-boquete-ruta-precio", "Cascadas Perdidas", "Cómo llegar, cuánto se camina, entrada y qué llevar.", "Cascadas Perdidas de Boquete", "Senderismo"),
  ("Senderos y el volcán", "/es/articles/bajo-mono-boquete-circuito-y-senderos", "Bajo Mono", "El circuito junto al río y los senderos que salen de ahí.", "Bajo Mono: circuito y senderos", "Senderismo"),
  ("Senderos y el volcán", "/es/articles/miradores-de-boquete-vistas-sin-subir-baru", "Miradores de Boquete", "Vistas al Barú y al valle sin la subida nocturna.", "Miradores de Boquete", "Vistas"),
  ("Café y bosque nuboso", "/es/articles/tour-de-cafe-boquete-fincas-precios-reservar", "Tour de café", "Fincas, duración, qué incluye el precio y cómo reservar.", "Tour de café en Boquete", "Café"),
  ("Café y bosque nuboso", "/es/articles/sendero-los-quetzales-quetzal-boquete", "Sendero Los Quetzales", "La ruta, el horario para ver el quetzal y dónde mirar.", "Sendero Los Quetzales", "Senderismo"),
  ("Agua caliente, río y cómo llegar", "/es/articles/canopy-en-boquete-tree-trek-y-opciones", "Canopy en Boquete", "Tree Trek, tirolesa y alternativas, con precios.", "Canopy en Boquete", "Aventura"),
  ("Planificar: cuándo venir y cuánto cuesta", "/es/articles/donde-dormir-en-boquete-hoteles-cabanas-hospedaje", "Dónde dormir", "Hoteles, cabañas y hospedaje por zona del pueblo.", "Dónde dormir en Boquete", "Dormir"),
  ("Planificar: cuándo venir y cuánto cuesta", "/es/articles/restaurantes-y-cafeterias-en-boquete", "Dónde comer y tomar café", "Desayuno, almuerzo y café por zona del pueblo.", "Restaurantes y cafeterías en Boquete", "Comer"),
  ("Planificar: cuándo venir y cuánto cuesta", "/es/articles/lugares-turisticos-chiriqui", "Lugares turísticos de Chiriquí", "Qué ver en la provincia y en qué orden, desde Boquete.", "Lugares turísticos de Chiriquí", "Provincia"),
 ],
 "es/articles/el-valle-de-anton": [
  ("Senderos y cumbres", "/es/articles/cerro-gaital-cara-iguana-rutas-dificultad", "Cerro Gaital y Cara Iguana", "Rutas, tiempos y dificultad de las dos subidas más duras.", "Cerro Gaital y Cara Iguana", "Senderismo"),
  ("Senderos y cumbres", "/es/articles/cerro-la-silla-sendero-amanecer-el-valle", "Cerro La Silla", "El sendero del amanecer: salida, tiempos y qué llevar.", "Cerro La Silla", "Senderismo"),
  ("Senderos y cumbres", "/es/articles/miradores-el-valle-de-anton", "Miradores del cráter", "Cerro La Cruz y las vistas, a pie o en e-bike.", "Miradores de El Valle de Antón", "Vistas"),
  ("Senderos y cumbres", "/es/articles/senderismo-en-panama-mejores-senderos-ciudad", "Senderismo en Panamá", "Los senderos cerca de la capital, con El Valle primero.", "Senderismo en Panamá", "Senderismo"),
  ("Cascadas y agua caliente", "/es/articles/cascadas-el-valle-de-anton-como-llegar", "Todas las cascadas", "Cuáles son, cuánto se camina y cuál conviene con niños.", "Cascadas de El Valle de Antón", "Cascadas"),
  ("Cascadas y agua caliente", "/es/articles/cascadas-en-panama-mejores-como-llegar", "Cascadas de Panamá", "Las más visitadas del país y cuál elegir según tu tiempo.", "Cascadas en Panamá", "Cascadas"),
  ("Familia, animales y aventura", "/es/articles/el-valle-de-anton-con-ninos-familia", "El Valle con niños", "Mariposario, zoológico, pozas cortas y rutas en e-bike.", "El Valle de Antón con niños", "Familia"),
  ("Familia, animales y aventura", "/es/articles/avistamiento-de-aves-el-valle-de-anton", "Avistamiento de aves", "Dónde ver aves, especies clave, mejor hora y tours.", "Avistamiento de aves", "Aves"),
  ("Planificar: llegar, precios y horarios", "/es/articles/el-valle-de-anton-en-un-dia-itinerario", "El Valle en un día", "Itinerario desde la capital: bus, bici, cascadas y comida.", "El Valle de Antón en un día", "Planificar"),
  ("Planificar: llegar, precios y horarios", "/es/articles/fin-de-semana-el-valle-de-anton-2-dias", "Fin de semana en El Valle", "Plan de dos días con el mercado del domingo.", "Fin de semana en El Valle", "Planificar"),
  ("Planificar: llegar, precios y horarios", "/es/articles/lugares-turisticos-de-cocle", "Lugares turísticos de Coclé", "El Valle, El Chorro, El Caño, Penonomé y playas.", "Lugares turísticos de Coclé", "Provincia"),
 ],
 "articles/panama-city": [
  ("The old quarter", "/articles/where-to-stay-in-panama-city", "Where to Stay", "Casco Viejo, San Francisco and Punta Pacífica compared, with hotels.", "Where to Stay in Panama City", "Planning"),
  ("The canal and the causeway", "/articles/panama-canal-boat-tours", "Canal Boat Tours", "Partial vs full transit, the days they run and prices.", "Panama Canal Boat Tours", "The canal"),
  ("Getting out of the city", "/articles/contadora-ferry-from-panama-city", "The Contadora Ferry", "Schedule, tickets and where it leaves from.", "Contadora Ferry", "Day trips"),
  ("Getting out of the city", "/articles/san-blas-tours-from-panama-city", "San Blas Tours", "Day trips and overnight trips compared, with prices.", "San Blas Tours from Panama City", "Day trips"),
 ],
 "es/articles/panama-city": [
  ("El casco antiguo", "/es/articles/hoteles-en-casco-viejo", "Hoteles en el Casco Viejo", "Boutique, de lujo y económicos, comparados con precios.", "Hoteles en el Casco Viejo", "Casco Viejo"),
  ("Salir de la ciudad", "/es/articles/san-blas-guna-yala-guia-tours-islas", "Islas de San Blas", "Playas, cómo llegar y tours de uno o varios días.", "Islas de San Blas (Guna Yala)", "Escapadas"),
 ],
 "articles/bocas-del-toro": [
  ("Getting there and getting around", "/articles/boquete-to-bocas-del-toro-shuttle-bus-timing", "From Boquete", "Shuttle or bus, the boat leg and the real travel time.", "Boquete to Bocas del Toro", "Getting there"),
  ("Getting there and getting around", "/articles/which-bocas-del-toro-island-to-stay-on", "Where to Stay", "Isla Colón, Carenero and Bastimentos compared by budget.", "Where to Stay in Bocas del Toro", "Planning"),
 ],
}


def main():
    for hub, rows in ADD.items():
        f = PUB / (hub + ".html")
        s = f.read_text(encoding="utf-8")
        added = 0
        for group, href, name, desc, idx_title, cat in rows:
            if f'href="{href}"' in s:
                print("  already linked:", hub, href); continue
            # group row
            m = re.search(r'<h2>' + re.escape(html.escape(group, quote=False)) + r'</h2>.*?</ul>', s, re.S)
            assert m, (hub, group)
            li = (f'<li><a href="{href}"><span class="n">{html.escape(name, quote=False)}</span><span class="d">{html.escape(desc, quote=False)}</span>'
                  f'<span class="ar" aria-hidden="true">&rarr;</span></a></li>\n')
            pos = m.end() - len("</ul>")
            s = s[:pos] + li + s[pos:]
            # index row
            ol = re.search(r'<ol class="hub-idx">(.*?)</ol>', s, re.S)
            n = len(re.findall(r"<li>", ol.group(1))) + 1
            row = (f'<li><a href="{href}"><span class="num">{n:02d}</span><span class="ttl">{html.escape(idx_title, quote=False)}</span>'
                   f'<span class="cat">{html.escape(cat, quote=False)}</span><span class="ar" aria-hidden="true">&rarr;</span></a></li>\n')
            s = s[:ol.end() - len("</ol>")] + row + s[ol.end() - len("</ol>"):]
            added += 1
        ol = re.search(r'<ol class="hub-idx">(.*?)</ol>', s, re.S)
        n = len(re.findall(r"<li>", ol.group(1)))
        s = re.sub(r'<span class="hub-count">\d+ (guides|guías)</span>', lambda m: f'<span class="hub-count">{n} {m.group(1)}</span>', s)
        f.write_text(s, encoding="utf-8")
        print(f"{hub}: +{added} guides, index now {n}")


if __name__ == "__main__":
    main()
