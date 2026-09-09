#!/usr/bin/env python3
"""
evbike-page-fix.py — factual and editorial repair of
public/es/articles/tours-en-bicicleta-el-valle-de-anton.html

The page presented itself as an impartial comparison while being written for
one of the four operators it compared, carried a product-safety allegation
about the other three, invented a coffee origin, and got six checkable prices
and schedules wrong — including E-Valley's own, which it quoted at $65 for a
"private guided tour" that does not exist in any of E-Valley's material.

The brief from the client: stay neutral in method, let the tilt come from the
facts. So:

  - every operator keeps its name, but only E-Valley gets numbers, because
    E-Valley is the only one whose prices, hours, kit, minimum age and routes
    are published first-party (evalleybikes.net and the funnel page). The
    competitors' figures were never sourced and are removed rather than guessed;
  - a transparency note says plainly that PanamaSpot works with E-Valley and
    explains why the numbers are asymmetric;
  - the recycled-construction-helmet line is gone;
  - Geisha is gone entirely — it is a Chiriquí varietal grown at 1,400-1,900 m
    and El Valle sits at 600. This page is about El Valle;
  - Piedra Pintada $1 (was "free"), hot springs $10 (was ~$5), Mariposario $5
    and closed Tuesdays (was $3-5, closure unmentioned), Albrook bus $4.25 from
    ~6:30 a.m. every 30 min (was "$4-5 from 6 AM every 30-40 min") — all now
    agree with the pages on this site that cover those places directly;
  - the blue morpho is no longer called endemic to El Valle;
  - the group-size contradiction (5 per guide in one section, 10 in two others)
    and the duration contradiction (2.5-3 h vs 3.5-4 h) are resolved.

Every replacement below is asserted, so a silent miss fails the run.

    python3 scripts/evbike-page-fix.py
"""
import pathlib, sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "public/es/articles/tours-en-bicicleta-el-valle-de-anton.html"

BUS = "/es/articles/bus-albrook-el-valle-de-anton-horarios-precios"

EDITS = [

# ── intro: no Geisha, and the butterflies are not endemic ────────────────────
("intro",
 "El Valle de Antón es uno de los pocos lugares del mundo donde puedes pedalear "
 "dentro de un cráter volcánico extinto, pasar por un mariposario endémico, probar "
 "café Geisha recién preparado y estar de vuelta en tu cabaña antes del almuerzo.",

 "El Valle de Antón es uno de los pocos lugares del mundo donde puedes pedalear "
 "dentro de un cráter volcánico extinto, parar en una cascada de 35 metros y en un "
 "petroglifo precolombino, y estar de vuelta en tu hospedaje antes del almuerzo."),

# ── transparency note, right after the intro ────────────────────────────────
("disclosure",
 "Si ya tienes claro que quieres ir, salta directo a la tabla comparativa. Si aún "
 "dudas, empieza por el principio.</p>",

 "Si ya tienes claro que quieres ir, salta directo a la tabla comparativa. Si aún "
 "dudas, empieza por el principio.</p>\n\n"
 '<div class="callout"><span class="label">Transparencia</span> PanamaSpot trabaja '
 "comercialmente con E-Valley Bikes, uno de los operadores que aparece en esta guía. "
 "Los datos de E-Valley salen de sus propios materiales publicados. De los demás "
 "operadores solo publicamos lo que se puede verificar de forma independiente —qué "
 "modalidad ofrecen y dónde están— porque no publican tarifas ni horarios de forma "
 "estable. Esa es la razón de que las cifras de esta página estén repartidas de forma "
 "desigual. Confirma precios y condiciones con cada operador antes de reservar.</div>"),

# ── §02 self-guided rental: real tiers, and the audio guide ─────────────────
("s2-rental",
 "Recoges la bici, te dan un casco, un candado y quizás una botella de agua, y sales "
 "a explorar por tu cuenta. No hay itinerario fijo ni horario de regreso más allá del "
 "límite de tiempo contratado (normalmente 3 horas). Es la opción más barata —desde "
 "$15 USD por bicicleta de montaña convencional hasta $30–35 USD por e-bike— y la más "
 "flexible.",

 "Recoges la bici, te dan casco y candado, y sales a explorar por tu cuenta. No hay "
 "itinerario fijo ni horario de regreso más allá del bloque de tiempo que contrates. "
 "Es la opción más barata y la más flexible. E-Valley Bikes publica sus tarifas por "
 "bloque: $30 por bici por 2 horas, $40 por 4 horas y $50 por el día completo."),

# ── §02 the honest downside of going unguided — the audio guide closes it ───
("s2-downside",
 "La desventaja real: sin guía, es fácil pasar por alto La Piedra Pintada (un "
 "petroglifo precolombino que está literalmente al borde del camino pero sin "
 "señalización clara), no saber qué café probar ni dónde, y perderte el contexto "
 "geológico que hace que el paisaje tenga sentido. El valle no es grande, pero tampoco "
 "está señalizado como un parque temático.",

 "La desventaja real: sin nadie que te lo cuente, es fácil pasar por alto La Piedra "
 "Pintada —un petroglifo precolombino que está prácticamente al borde del camino pero "
 "con acceso poco señalizado— y perderte el contexto geológico que hace que el paisaje "
 "tenga sentido. El valle no es grande, pero tampoco está señalizado como un parque "
 "temático. La audioguía GPS que E-Valley incluye con el alquiler cubre buena parte de "
 "ese hueco: va narrando cada parada a medida que llegas, sin depender de un grupo."),

# ── §02 guided tours: drop the unsourced competitor price band ──────────────
("s2-guided",
 "Incluye guía bilingüe, equipo de seguridad, paradas predeterminadas y, según el "
 "operador, degustación de café, entrada al mariposario y refrigerios. Los grupos "
 "suelen ser de 5 a 12 personas. El precio oscila entre $40 y $65 USD por persona. "
 "Ideal para viajeros",

 "Incluye guía, equipo de seguridad y paradas predeterminadas; según el operador, "
 "también entradas a alguna atracción y refrigerios. El precio, el tamaño del grupo y "
 "lo que entra en cada salida varían por operador y por temporada, y ninguno los "
 "publica de forma estable: pídelos por escrito antes de pagar. Ideal para viajeros"),

# ── §03 the comparison table: like for like, no invented figures ────────────
("s3-table",
 """<tr>
<td>Go Panama Bike Tours</td>
<td>Tour guiado grupal (bici convencional o e-bike)</td>
<td>~3 h</td>
<td>$40–$55 / persona</td>
<td><span class="pill good">Primer viaje al valle</span></td>
</tr>
<tr>
<td>Civitatis / Go Panama</td>
<td>Tour guiado con café Geisha + mariposario</td>
<td>2,5–3 h</td>
<td>~$55 / persona</td>
<td><span class="pill good">Turista con poco tiempo</span></td>
</tr>
<tr>
<td>E-Valley Bikes</td>
<td>Alquiler de e-bike + tour guiado privado</td>
<td>Hasta 3 h</td>
<td>$30 alquiler / $65 tour privado</td>
<td><span class="pill good">Flexibilidad + comodidad</span></td>
</tr>
<tr>
<td>Espacio Eklektiko</td>
<td>Alquiler de bici + scooter eléctrico + tours de cascadas</td>
<td>Variable</td>
<td>Consultar directo</td>
<td><span class="pill mid">Viajero independiente</span></td>
</tr>""",

 """<tr>
<td>E-Valley Bikes</td>
<td>Alquiler de e-bike autoguiado, con audioguía GPS</td>
<td>2 h · 4 h · día completo</td>
<td>$30 · $40 · $50 por bici</td>
<td><span class="pill good">Ir a tu propio ritmo</span></td>
</tr>
<tr>
<td>Go Panama Bike Tours</td>
<td>Tour guiado en grupo, con guía bilingüe</td>
<td>Según la salida</td>
<td>Consultar con el operador</td>
<td><span class="pill good">Preferir ir con guía</span></td>
</tr>
<tr>
<td>Espacio Eklektiko</td>
<td>Alquiler de bicis y scooters eléctricos + tours de cascadas</td>
<td>Variable</td>
<td>Consultar con el operador</td>
<td><span class="pill mid">Improvisar sobre la marcha</span></td>
</tr>"""),

("s3-table-head",
 "<tr><th>Operador</th><th>Modalidad</th><th>Duración</th><th>Precio aprox.</th><th>Perfil ideal</th></tr>",
 "<tr><th>Operador</th><th>Modalidad</th><th>Duración</th><th>Tarifas publicadas</th><th>A quién le encaja</th></tr>"),

# ── §03 Go Panama: name and modality stay, unsourced specifics go ───────────
("s3-gopanama",
 "<p><strong>Go Panama Bike Tours</strong> opera desde un local junto al mercado de "
 "frutas de El Valle y es el operador con más presencia en plataformas como Booking.com "
 "y Civitatis. Sus tours grupales salen los fines de semana a las 10:00 AM y duran "
 "aproximadamente 3 horas. Los grupos son de hasta 5 personas por guía, lo que es "
 "razonable. Incluyen bicicleta, casco, agua, degustación de café y guía bilingüe. No "
 "incluyen transporte desde Ciudad de Panamá (eso cuesta extra si lo contratas con "
 "ellos) ni almuerzo.</p>",

 "<p><strong>Go Panama Bike Tours</strong> opera junto al mercado y se vende tanto "
 "directamente como a través de plataformas de reserva como Civitatis y Booking.com. "
 "Su formato es el tour guiado en grupo, con guía bilingüe y paradas fijas. Los "
 "horarios de salida, el tamaño máximo del grupo y lo que incluye cada salida cambian "
 "según la temporada y no están publicados de forma estable, así que confírmalos con "
 "ellos antes de reservar. El transporte desde Ciudad de Panamá y el almuerzo van "
 "aparte.</p>"),

# ── §03 E-Valley: what their own materials actually say ────────────────────
("s3-evalley",
 "<p><strong>E-Valley Bikes</strong> es el operador local especializado en bicicletas "
 "eléctricas. Tienen dos formatos: alquiler libre desde $30 por e-bike (con casco, "
 "candado y audio guía incluidos) y tour privado guiado desde $65 por persona. La "
 "ventaja diferencial es que pueden entregar las bicis directamente en tu hotel dentro "
 "del valle, y el tour privado se adapta a tu horario en lugar de salir en horario "
 "fijo. Para grupos de 2 a 4 personas, el tour privado en e-bike de E-Valley Bikes "
 "resulta comparable en precio al tour grupal de otros operadores, con mucha más "
 "flexibilidad.</p>",

 "<p><strong>E-Valley Bikes</strong> es el operador local especializado en bicicletas "
 "eléctricas. Está sobre la Avenida Principal, diagonal al mercado, y abre de lunes a "
 "domingo de 8:00 a.m. a 5:00 p.m. Su formato es el alquiler autoguiado: $30 por bici "
 "por 2 horas, $40 por 4 horas y $50 por el día completo, con casco, candado y una "
 "audioguía GPS que va narrando cada parada. Entregan cinco rutas ya trazadas en el "
 "mapa —Circuito completo, Níspero y Mariposario, Ruta con trillos, Curvas del Valle y "
 "La Silla, y Hotel Campestre—; la más larga, el Circuito completo, son 19,7 km y unos "
 "93 minutos de pedaleo por Calle Millonarios, Cariguana, Chorro El Macho, La Piedra "
 "Pintada y el mercado. Edad mínima 7 años y cancelación gratuita hasta 24 horas "
 "antes.</p>"),

# ── §03 Eklektiko: stop writing them off ──────────────────────────────────
("s3-eklektiko",
 "que funciona más como punto de encuentro para viajeros independientes. No tienen "
 "itinerario fijo de tour en bicicleta publicado; la oferta varía. Si buscas algo "
 "espontáneo y estás dispuesto a preguntar en persona, puede ser una buena opción. Si "
 "necesitas reservar con antelación desde Ciudad de Panamá, mejor ir con uno de los "
 "operadores anteriores.",

 "que funciona como punto de encuentro para viajeros independientes. No publican "
 "itinerario fijo de tour en bicicleta ni tarifas en línea; la oferta varía. Si vas a "
 "improvisar sobre la marcha, pregunta en persona. Si necesitas dejarlo cerrado antes "
 "de salir de Ciudad de Panamá, escríbeles primero para confirmar disponibilidad."),

# ── §04 inclusions: no Geisha, guide language, add the audio guide ─────────
("s4-guide-li",
 "<li><strong>Guía bilingüe:</strong> en los tours guiados. El nivel de inglés y el "
 "conocimiento del guía varía significativamente entre operadores y entre días.</li>",
 "<li><strong>Guía bilingüe:</strong> en los tours guiados. Pregunta en qué idioma va "
 "la salida concreta que reservas.</li>"),

("s4-geisha-li",
 "<li><strong>Degustación de café Geisha:</strong> en los tours de Go Panama / "
 "Civitatis. En E-Valley Bikes depende del formato del tour.</li>\n",
 "<li><strong>Audioguía GPS:</strong> en el alquiler de E-Valley Bikes. Es la "
 "diferencia práctica entre pedalear sin más y entender lo que estás viendo.</li>\n"),

("s4-mariposario-li",
 "<li><strong>Entrada al mariposario:</strong> incluida en algunos tours de Go Panama. "
 "Verifica antes de reservar.</li>",
 "<li><strong>Entradas a las atracciones:</strong> el Mariposario, el Zoo El Níspero y "
 "las aguas termales cobran aparte. Ningún alquiler las incluye; en los tours guiados, "
 "pregunta antes de reservar si alguna va incluida.</li>"),

# ── §04 what is not included: the two prices that were wrong ───────────────
("s4-bus-li",
 "<li><strong>Transporte desde Ciudad de Panamá:</strong> los buses a El Valle salen de "
 "la Terminal de Albrook y cuestan $4–5 USD por trayecto. El trayecto dura unas 2 "
 "horas. Si contratas transporte con el operador, añade $25–40 USD por persona.</li>",
 "<li><strong>Transporte desde Ciudad de Panamá:</strong> el bus desde la Terminal de "
 f'Albrook cuesta <a href="{BUS}">$4.25 por trayecto</a>, solo en efectivo, y tarda '
 "entre 1 h 45 min y 2 h 30 min. Si contratas transporte privado con un operador, "
 "cuenta bastante más.</li>"),

("s4-termales-li",
 "<li><strong>Actividades opcionales en ruta:</strong> las aguas termales del valle "
 "tienen entrada separada (~$5 USD). No están incluidas en ningún tour estándar.</li>",
 "<li><strong>Actividades opcionales en ruta:</strong> las aguas termales tienen "
 "entrada aparte —$10 al balneario con piscinas— y no están incluidas en ningún tour "
 "estándar.</li>"),

# ── §04 budget callout: no invented competitor headline price ──────────────
("s4-callout",
 "Un tour guiado de 3 horas que cuesta $55 en papel puede terminar costando $75–85 si "
 "añades propina, almuerzo y transporte desde Ciudad de Panamá. Planifica con ese "
 "margen.",
 "El precio del tour o del alquiler es sólo una parte. Súmale el bus desde Ciudad de "
 "Panamá ($8.50 ida y vuelta), el almuerzo ($8–20), las entradas que quieras hacer "
 "($1 la Piedra Pintada, $5 el Mariposario, $10 las aguas termales) y la propina si "
 "vas con guía. Un día completo en bici sale realista entre $50 y $90 por persona "
 "saliendo de la capital."),

# ── §05 minimum age: E-Valley publishes 7+; nobody else publishes anything ──
("s5-edad",
 "<p>Go Panama Bike Tours establece una edad mínima de 12 años. E-Valley Bikes no tiene "
 "restricción de edad publicada, pero sí requieren que el participante sepa montar "
 "bicicleta convencional antes de subirse a una e-bike.",
 "<p>E-Valley Bikes fija la edad mínima en 7 años y pide que quien monte sepa manejar "
 "una bicicleta convencional antes de subirse a una eléctrica. Los operadores de tour "
 "guiado aplican sus propios mínimos y no los publican: pregúntalos al reservar."),

# ── §06 the route: anchor the distance to a real published track ───────────
("s6-circuito",
 "<p>El circuito estándar de los tours en bicicleta de El Valle cubre entre 8 y 14 km "
 "dependiendo del operador y de si incluye desvíos a miradores. Estos son los puntos "
 "principales, en el orden en que suelen aparecer en los recorridos:</p>",
 "<p>El circuito estándar de El Valle cubre entre 8 y 20 km según hasta dónde subas. "
 "Como referencia concreta y verificable: el Circuito completo que E-Valley Bikes "
 "entrega marcado en su mapa son 19,7 km y unos 93 minutos de pedaleo sin contar "
 "paradas. Estos son los puntos principales, en el orden en que suelen aparecer:</p>"),

# ── §06 Piedra Pintada: it costs $1, it is not free ────────────────────────
("s6-piedra",
 "Un petroglifo precolombino de unos 3 metros de alto, ubicado a unos 2 km del centro "
 "del pueblo por la carretera hacia La Mesa. La entrada es libre. Sin guía, es fácil "
 "pasarlo de largo porque el acceso está señalizado de forma discreta. Con guía, suele "
 "ser una de las paradas más interesantes del recorrido, especialmente si explica el "
 "contexto histórico de los pueblos que habitaron el cráter antes de la llegada "
 "española.",

 "Un petroglifo precolombino de unos 3 metros de alto, a unos 2 km del centro del "
 "pueblo por la carretera hacia La Mesa. La entrada cuesta $1 por persona. El acceso "
 "está señalizado de forma discreta y es fácil pasarlo de largo: si vas por tu cuenta, "
 "lleva la ubicación marcada antes de salir. Es una de las paradas más interesantes del "
 "recorrido si alguien te explica el contexto de los pueblos que habitaron el cráter "
 "antes de la llegada española."),

# ── §06 Mariposario: not endemic, $5, and it shuts on Tuesdays ─────────────
("s6-mariposario",
 "Santuario de mariposas endémicas de El Valle, incluyendo la famosa mariposa azul "
 "morpho. La entrada ronda los $3–5 USD (incluida en algunos tours, no en todos). El "
 "mejor momento para verlas activas es entre las 9 y las 11 de la mañana, cuando el sol "
 "calienta las alas. Si tu tour sale a las 10 AM, llegarás al mariposario alrededor de "
 "las 11, que sigue siendo buen momento.",

 "Invernadero de mariposas tropicales en vuelo libre, entre ellas la morfo azul. La "
 "entrada cuesta $5 y <strong>cierra los martes, sin excepción</strong>: si tu "
 "recorrido cae en martes, cambia esta parada por el Zoo El Níspero, que abre todos los "
 "días. El mejor momento para verlas activas es entre las 9 y las 11 de la mañana, "
 "cuando el sol calienta las alas."),

# ── §06 the Geisha block goes entirely ─────────────────────────────────────
("s6-geisha",
 "<h3>Degustación de café Geisha</h3>\n"
 "<p>El café Geisha panameño es uno de los más cotizados del mundo, y El Valle tiene "
 "productores locales que ofrecen degustaciones. Go Panama Bike Tours incluye esta "
 "parada como parte del recorrido estándar. La degustación suele ser de una taza de "
 "café preparado en método pour-over o chemex, con explicación del proceso de cultivo "
 "en las alturas del cráter. No es una cata de barista profesional, pero es genuina y "
 "el café es bueno.</p>\n\n",
 ""),

# ── §06 hot springs: $10 ───────────────────────────────────────────────────
("s6-termales",
 "Si vas por tu cuenta en alquiler libre, es una parada fácil de añadir al circuito. "
 "Entrada aproximada: $5 USD.",
 "Si vas por tu cuenta en alquiler libre es una parada fácil de añadir al circuito. La "
 "entrada al balneario con piscinas cuesta $10."),

# ── §06 route callout: no café, and the time budget matches §01 ────────────
("s6-callout",
 "El circuito completo —mercado, La Piedra Pintada, mariposario, café, mirador y aguas "
 "termales— cubre unos 12–14 km y requiere entre 3,5 y 4 horas con paradas. Ningún tour "
 "estándar cubre todo esto en 3 horas; tendrás que elegir o contratar un tour "
 "extendido.",
 "El circuito completo —mercado, La Piedra Pintada, mariposario, mirador y aguas "
 "termales— ronda los 20 km y requiere entre 3,5 y 4 horas con paradas. No cabe en un "
 "bloque de 2 horas: si quieres hacerlo entero, contrata 4 horas o el día completo."),

# ── §07 booking window: only what each operator actually publishes ─────────
("s7-reserva",
 "<p>Go Panama Bike Tours acepta reservas hasta el día anterior si quedan plazas. "
 "E-Valley Bikes permite reservar con 24 horas de antelación para tours privados y "
 "acepta walk-ins para alquiler libre según disponibilidad. En temporada alta "
 "(enero–abril y Semana Santa), reserva con al menos una semana de antelación para "
 "tours privados.</p>",
 "<p>E-Valley Bikes acepta walk-ins para el alquiler según disponibilidad y cancela "
 "gratis hasta 24 horas antes, así que reservar temprano no te ata a nada. Los "
 "operadores de tour guiado trabajan con salidas programadas y plazas limitadas: en "
 "temporada alta (enero–abril y Semana Santa) reserva con al menos una semana de "
 "antelación y confirma por escrito la política de cancelación.</p>"),

# ── §08 safety kit: the disparagement goes ────────────────────────────────
("s8-helmets",
 "<p>Todos los operadores incluyen casco. La calidad varía: algunos tienen cascos de "
 "ciclismo modernos con buen ajuste; otros, cascos de construcción reciclados que "
 "cumplen la función mínima. Si tienes tu propio casco, llévatelo. E-Valley Bikes "
 "incluye además guantes, rodilleras y coderas en sus tours guiados, lo que es inusual "
 "para El Valle y marca una diferencia real en los tramos con grava.</p>",
 "<p>Todos los operadores incluyen casco. Si viajas con el tuyo, llévatelo: el ajuste "
 "propio siempre es mejor que el de un casco de flota. E-Valley Bikes entrega además "
 "candado y canasta delantera con cada bici, lo que resuelve el problema de dónde dejar "
 "la mochila y la bici cuando paras a caminar hasta una cascada.</p>"),

# ── §08 getting there: the bus facts, matching our own Albrook guide ───────
("s8-bus",
 "<p>Los buses salen de la Terminal de Albrook cada 30–40 minutos desde las 6 AM. El "
 "trayecto dura entre 1 hora 45 minutos y 2 horas 30 minutos dependiendo del tráfico. "
 "El precio es de $4–5 USD. El bus te deja en el centro del pueblo, a menos de 200 "
 "metros del punto de salida de los principales operadores.",
 "<p>Los buses salen de la Terminal de Albrook aproximadamente cada 30 minutos y el "
 "primero sale sobre las 6:30 a.m. El trayecto dura entre 1 hora 45 minutos y 2 horas "
 "30 minutos según el tráfico, y el pasaje cuesta $4.25, solo en efectivo. Compra el "
 "tiquete en la boletería B-22 y aborda en la Plataforma 48: son dos puntos distintos "
 f'dentro de la terminal, y lo explicamos paso a paso en la <a href="{BUS}">guía del '
 "bus Albrook–El Valle</a>. El bus te deja en el centro del pueblo, sobre la Avenida "
 "Principal, a pocos minutos a pie de los puntos de alquiler."),

# ── §08 group size: resolve the 5-vs-10 contradiction ─────────────────────
("s8-grupos",
 "<p>El tamaño del grupo importa más de lo que parece. Un tour de 10 personas con un "
 "guía mediocre puede ser frustrante: largas esperas en cada parada, dificultad para "
 "escuchar las explicaciones, ritmo dictado por el más lento. Un tour de 4 personas con "
 "un buen guía es otra experiencia. Si el operador no especifica el tamaño máximo del "
 "grupo, pregunta antes de reservar. Los tours privados —disponibles con E-Valley Bikes "
 "y con Go Panama bajo petición— eliminan este problema por completo y suelen merecer "
 "el pequeño sobreprecio.</p>",
 "<p>El tamaño del grupo importa más de lo que parece: en una salida grande hay esperas "
 "en cada parada, cuesta escuchar las explicaciones y el ritmo lo marca el más lento. "
 "Si vas con un operador de tour guiado y no publica el tamaño máximo del grupo, "
 "pregúntalo antes de reservar. El alquiler autoguiado elimina el problema por "
 "definición —paras donde quieres y el tiempo que quieres— y es la razón principal por "
 "la que mucha gente que ya conoce el valle acaba prefiriéndolo.</p>"),

# ── dek / meta description: stop promising everyone's prices ───────────────
("dek",
 "Guía completa de tours en bicicleta el valle de antón: precios reales, qué incluye "
 "cada operador, dificultad, rutas y cuándo reservar. Sin letra pequeña.",
 "Guía de tours en bicicleta en El Valle de Antón: alquiler autoguiado o tour con guía, "
 "tarifas publicadas, dificultad real del terreno, rutas y cuándo reservar."),
]


def main():
    s = PAGE.read_text(encoding="utf-8")
    misses = []
    for name, old, new in EDITS:
        n = s.count(old)
        if n == 0:
            misses.append(name)
            print(f"  !! MISS  {name}")
            continue
        s = s.replace(old, new)
        print(f"  ok  {name}" + (f"  (×{n})" if n > 1 else ""))
    PAGE.write_text(s, encoding="utf-8")

    for word in ("Geisha", "cascos de construcción", "entrada es libre"):
        left = s.count(word)
        print(f"  {'!!' if left else 'ok'}  '{word}' remaining: {left}")
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
