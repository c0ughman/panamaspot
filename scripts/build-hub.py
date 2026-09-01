#!/usr/bin/env python3
"""build-hub.py — generate a destination hub page from the shared article shell.

A hub is not an article: it has no prose body, no TOC and no FAQ. It reuses the
article shell (head + inlined CSS + header + footer) so it inherits the site
design and the analytics injection in build-static.mjs, then replaces <main>
with a curated index of every guide in one destination cluster.

Config lives in HUBS below. Add a dict, re-run, done.
Usage: python3 scripts/build-hub.py [slug ...]
"""
import re, sys, json, html as H
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELL_EN = ROOT / "public/articles/things-to-do-el-valle-de-anton.html"
SHELL_ES = ROOT / "public/es/articles/que-hacer-el-valle-de-anton.html"

IMG = "/images/el-valle/"
BQIMG = "/images/boquete/"
PCIMG_HERO  = "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=2400"
PCIMG_ITIN  = "https://images.pexels.com/photos/17477516/pexels-photo-17477516.jpeg?auto=compress&cs=tinysrgb&w=1200"
PCIMG_CASCO = "https://images.pexels.com/photos/18049699/pexels-photo-18049699.jpeg?auto=compress&cs=tinysrgb&w=1200"
PCIMG_CANAL = "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Panama_Canal_Gatun_Locks.jpg/1280px-Panama_Canal_Gatun_Locks.jpg"
PCIMG_DAY   = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Calle_en_Isla_Taboga_-_Panam%C3%A1.jpg/1280px-Calle_en_Isla_Taboga_-_Panam%C3%A1.jpg"

HUBS = {
 "el-valle-de-anton": dict(
  out="public/articles/el-valle-de-anton.html",
  lang="en", alt_lang="es", alt_url="/es/articles/el-valle-de-anton",
  name="El Valle de Antón",
  title="El Valle de Antón: Complete Travel Guide 2026",
  desc="Everything we know about El Valle de Antón — the town inside a volcanic crater two hours from Panama City. Trails, waterfalls, hot springs, tours and how to plan the trip.",
  hero=IMG+"elvalle-crater-hero.webp",
  hero_alt="Families on the grass below the forested crater walls that ring El Valle de Antón",
  eyebrow="Destination guide",
  dek="A town of 7,000 people living inside the caldera of a volcano that last erupted around 200,000 years ago. Two hours from Panama City, 600 metres up, and about ten degrees cooler than the coast.",
  pills=["2 hrs from Panama City","600 m elevation","Coclé Province"],
  intro=[
   "El Valle de Antón sits on the flat floor of a collapsed volcanic crater roughly five kilometres across — one of only a handful of inhabited calderas anywhere in the world. The walls you can see from the main street are the rim.",
   "That geography is the whole reason to come. The altitude gives it a permanently mild climate, the crater walls hold cloud forest full of birds and orchids, and the streams coming off them produce waterfalls and thermal springs within walking distance of town. It is the easiest genuine mountain escape from Panama City, and most people do it as a day trip when it deserves two."],
  facts=[("Getting there","Bus from Albrook terminal, roughly 2½ hrs. Driving is 2 hrs on the Panamericana, exit at Las Uvas."),
         ("When to go","December to April is dry season. Green season brings fuller waterfalls and afternoon rain."),
         ("How long","A day trip works. Two nights lets you hike in the morning when the crater rim is clear."),
         ("Getting around","The town is flat and compact — bikes beat cars here. Trailheads are 10–25 min from the centre.")],
  start=[("/articles/things-to-do-el-valle-de-anton","Things to Do in El Valle de Antón","The full survey — every attraction, what it costs, and which ones are worth your time.",IMG+"elvalle-church.webp"),
         ("/articles/el-valle-day-trip-from-panama-city","El Valle as a Day Trip from Panama City","Timings, transport and a realistic itinerary for doing it in one day without rushing.",IMG+"elvalle-town.webp"),
         ("/articles/hikes-el-valle-de-anton","Best Hikes in El Valle","Every trail in the crater, ranked by difficulty, with times and trailhead directions.",IMG+"elvalle-bridge.webp")],
  groups=[
   dict(t="Trails and summits", img=IMG+"elvalle-indiadormida.webp",
        alt="The India Dormida ridge, the sleeping-figure skyline that forms the crater's northern wall",
        blurb="The crater rim is the reason to bring boots. Two of these are half-day efforts; the third is a genuine climb.",
        items=[("/articles/india-dormida-hike-el-valle-de-anton","India Dormida Hike","The signature ridge walk — the 'sleeping Indian' skyline seen from town."),
               ("/articles/cerro-gaital-cara-iguana-hike-el-valle","Cerro Gaital &amp; Cara Iguana","The harder pair. Cloud forest, exposed scrambling and the best views in the crater."),
               ("/articles/hikes-el-valle-de-anton","Every Trail, Compared","All the crater hikes side by side with times, gradients and trailheads.")]),
   dict(t="Waterfalls and hot water", img=IMG+"elvalle-elmachowaterfall.webp",
        alt="Chorro El Macho falling down a rock face into dense forest",
        blurb="Runoff from the crater walls produces both the waterfalls and the thermal springs — two of El Valle's three most-visited sites.",
        items=[("/articles/chorro-el-macho-waterfall-el-valle-de-anton","Chorro El Macho","The 35-metre waterfall on the town's western edge, plus the canopy line above it."),
               ("/articles/el-valle-de-anton-waterfalls","All the Waterfalls","Chorro El Macho, Las Mozas and the smaller ones people miss.")]),
   dict(t="Slow days, markets and family", img=IMG+"elvalle-flowermarket.webp",
        alt="Flowers and potted plants for sale under the roof of the El Valle market",
        blurb="What to do when you are not hiking — and what works with children in tow.",
        items=[("/articles/el-valle-de-anton-with-kids","El Valle With Kids","The zoo, the butterfly house and the orchid garden, plus which trails small legs can manage."),
               ("/articles/tours-en-el-valle-de-anton","Tours, Bikes and Prices","Guided options, e-bike rental and what each one actually costs in 2026.")])],
  cta=dict(img=IMG+"evbike-bike-crater.webp", eyebrow="E-Valley Bikes · El Valle",
           h="See the whole crater by bike.",
           p="Self-guided e-bike tours from $30 — helmet, GPS audio guide and lock included. Ride the volcano floor at your own pace.",
           btn="See the bike tours", href="/funnels/evalley_elvalle",
           micro="Four routes · Beginner &amp; family friendly · Cancel free up to 24h"),
  index=[("/articles/things-to-do-el-valle-de-anton","Things to Do in El Valle de Antón","Overview"),
         ("/articles/el-valle-day-trip-from-panama-city","El Valle Day Trip from Panama City","Planning"),
         ("/articles/hikes-el-valle-de-anton","Best Hikes El Valle de Antón","Hiking"),
         ("/articles/india-dormida-hike-el-valle-de-anton","India Dormida Hike: Trail Guide","Hiking"),
         ("/articles/cerro-gaital-cara-iguana-hike-el-valle","Cerro Gaital &amp; Cara Iguana","Hiking"),
         ("/articles/chorro-el-macho-waterfall-el-valle-de-anton","Chorro El Macho Waterfall","Waterfalls"),
         ("/articles/el-valle-de-anton-waterfalls","El Valle de Antón Waterfalls","Waterfalls"),
         ("/articles/el-valle-de-anton-with-kids","El Valle de Antón With Kids","Family"),
         ("/articles/tours-en-el-valle-de-anton","Tours in El Valle de Antón","Tours")],
 ),
 "boquete": dict(
  out="public/articles/boquete.html",
  lang="en", alt_lang="es", alt_url="/es/articles/boquete",
  name="Boquete", region="Chiriquí", lat=8.7799, lon=-82.4419,
  title="Boquete, Panama: Complete Travel Guide 2026",
  desc="Everything we know about Boquete — the cloud-forest town in Chiriquí highlands. Coffee farms, Volcán Barú, hot springs, waterfall hikes and how to plan the trip.",
  hero=BQIMG+"boquete-hills.webp",
  hero_alt="Cloud settling over the forested ridges that surround Boquete in the Chiriquí highlands",
  eyebrow="Destination guide",
  dek="A coffee town at 1,200 metres in the Chiriquí highlands, an hour from the Costa Rican border. Cool, wet, green, and the base for the only hike in Panama that shows you two oceans at once.",
  pills=["1,200 m elevation","Chiriquí Province","7 hrs from Panama City"],
  intro=[
   "Boquete sits in a river valley on the eastern flank of Volcán Barú, Panama's highest point and its only volcano of consequence. The altitude does the same thing here that it does in El Valle, only more so — it is genuinely cool, often wet, and the cloud forest starts more or less where the town ends.",
   "It is Panama's coffee country and its best-known highland destination, which means two quite different crowds: people here to hike Barú and the waterfall trails, and a large, long-established community of foreign residents. The guides below are written for the first group, though the practical detail serves both."],
  facts=[("Getting there","Fly to David (45 min from Panama City) then 45 min by road. Overland is 7 hrs by bus."),
         ("When to go","December to April is driest. The <em>bajareque</em> — fine wind-driven mist — can arrive any month."),
         ("How long","Three days covers the coffee, a waterfall hike and the hot springs. Barú needs a fourth."),
         ("Getting around","Town is walkable; trailheads and farms are not. Bikes, taxis or a rental car.")],
  start=[("/articles/things-to-do-in-boquete-panama","Things to Do in Boquete","The full survey — every hike, farm, spring and viewpoint, and which are worth the trip.",BQIMG+"boquete-town2.webp"),
         ("/articles/boquete-travel-guide","Boquete in Three Days","A tested itinerary that fits the coffee, a waterfall hike and Barú without rushing.",BQIMG+"boquete-clouds.webp"),
         ("/articles/volcan-baru-hike-sunrise-summit-guide","Climbing Volcán Barú","The overnight summit hike — the one place you can see the Pacific and Caribbean together.",BQIMG+"boquete-volcanbaru.webp")],
  groups=[
   dict(t="Trails and the volcano", img=BQIMG+"boquete-bridge.webp",
        alt="A footbridge on a forest trail in the hills above Boquete",
        blurb="Boquete's hiking runs from an easy waterfall circuit to an overnight slog up a 3,475-metre volcano.",
        items=[("/articles/volcan-baru-hike-sunrise-summit-guide","Volcán Barú Summit","The overnight climb, the sunrise, and an honest account of how hard it is."),
               ("/articles/lost-waterfalls-boquete-hiking-guide","The Lost Waterfalls","Three waterfalls on one short, steep, very wet trail."),
               ("/articles/hikes-in-boquete","Every Trail, Compared","All the Boquete hikes with times, gradients and what the weather does to them.")]),
   dict(t="Coffee, cloud forest and birds", img=BQIMG+"boquete-losquetzales.webp",
        alt="Moss-covered cloud forest along the Los Quetzales trail near Boquete",
        blurb="The two things Boquete is genuinely world-class at — specialty coffee and the resplendent quetzal — happen within a few kilometres of each other.",
        items=[("/articles/boquete-coffee-farm-tour","Coffee Farm Tours","Which estate to pick, what a tour actually covers, and what the Geisha fuss is about."),
               ("/articles/finca-lerida-los-quetzales-trail-birdwatching-boquete","Finca Lérida &amp; Los Quetzales","The birding trail, quetzal season, and when you realistically see one.")]),
   dict(t="Hot water, rivers and tours", img=BQIMG+"boquete-river2.webp",
        alt="The Caldera river running over rocks below Boquete",
        blurb="What to do on the days you are not climbing anything.",
        items=[("/articles/caldera-hot-springs-boquete","Caldera Hot Springs","The thermal pools down the valley — fees, temperatures and the road in."),
               ("/articles/tours-in-boquete-panama","Tours, Bikes and Prices","Guided options and rentals, with what each one costs in 2026.")])],
  cta=dict(img=BQIMG+"boquete-ebike-hero.webp", eyebrow="E-Valley Bikes · Boquete",
           h="Ride the coffee roads.",
           p="Self-guided e-bike tours through the Boquete valley — helmet, GPS audio guide and lock included. The climbs are the point, and the motor makes them possible.",
           btn="See the Boquete rides", href="/funnels/evalley_boquete",
           micro="Multiple routes · Beginner &amp; family friendly · Cancel free up to 24h"),
  index=[("/articles/things-to-do-in-boquete-panama","Things to Do in Boquete, Panama","Overview"),
         ("/articles/boquete-travel-guide","Boquete Travel Guide: 3-Day Itinerary","Planning"),
         ("/articles/hikes-in-boquete","Best Hikes in Boquete","Hiking"),
         ("/articles/volcan-baru-hike-sunrise-summit-guide","Volcán Barú Sunrise Summit Hike","Hiking"),
         ("/articles/lost-waterfalls-boquete-hiking-guide","Lost Waterfalls Hiking Guide","Hiking"),
         ("/articles/caldera-hot-springs-boquete","Caldera Hot Springs Boquete","Hot springs"),
         ("/articles/boquete-coffee-farm-tour","Boquete Coffee Farm Tours","Coffee"),
         ("/articles/finca-lerida-los-quetzales-trail-birdwatching-boquete","Finca Lérida &amp; Los Quetzales Trail","Birding"),
         ("/articles/tours-in-boquete-panama","Tours in Boquete, Panama","Tours")],
 ),

 "panama-city": dict(
  out="public/articles/panama-city.html",
  lang="en", alt_lang="es", alt_url="/es/articles/panama-city",
  name="Panama City", region="Panamá", lat=8.9824, lon=-79.5199,
  title="Panama City: Complete Travel Guide 2026",
  desc="Everything we know about Panama City — the old quarter, the canal, the causeway and the day trips out. What to see, how long it takes and what it costs.",
  hero=PCIMG_HERO,
  hero_alt="The Panama City skyline seen across the bay from the old quarter",
  eyebrow="Destination guide",
  dek="A capital with a glass skyline on one side of the bay and a 350-year-old walled quarter on the other, joined by the canal that put both of them there.",
  pills=["Pacific coast","UNESCO old quarter","Hub for every region"],
  intro=[
   "Panama City is the only capital in the Americas with a rainforest inside its city limits and a working interoceanic canal at the end of a metro line. Most visitors give it two days on the way somewhere else, which is roughly half what it takes.",
   "The city divides cleanly for planning: Casco Viejo, the restored colonial quarter where most of the eating and drinking happens; the canal and the causeway, which are the engineering; and everything reachable in under three hours, which is where the rest of this site begins."],
  facts=[("Getting there","Tocumen (PTY) is the main hub; Albrook (PAC) handles domestic flights. Metro Line 2 reaches Tocumen."),
         ("When to go","December to April is dry. The canal and the museums work in any weather."),
         ("How long","Two days for the city itself. Three if you want the canal without rushing it."),
         ("Getting around","The metro is quick, cheap and safe. Uber works well. Driving in Casco is not worth it.")],
  start=[("/articles/panama-city-itinerary-3-days","Panama City in Three Days","A tested itinerary covering the old quarter, the canal and the causeway.",PCIMG_ITIN),
         ("/articles/casco-viejo-panama-walking-guide","Casco Viejo Walking Guide","The old quarter on foot — the route, the plazas and where to stop.",PCIMG_CASCO),
         ("/articles/panama-canal-tour-miraflores-locks-visitor-guide","The Canal at Miraflores","When ships actually transit, what the ticket covers, and how to time a visit.",PCIMG_CANAL)],
  groups=[
   dict(t="The old quarter", img=PCIMG_CASCO,
        alt="Restored colonial facades and balconies in Casco Viejo, Panama City",
        blurb="Casco Viejo is the reason the city is on the UNESCO list, and the one part of it built for walking.",
        items=[("/articles/casco-viejo-panama-walking-guide","The Walking Guide","A route through the plazas, churches and ruins, with the detours worth taking."),
               ("/articles/panama-city-itinerary-3-days","Fitting It Into Three Days","How the old quarter slots into a short city stay.")]),
   dict(t="The canal and the causeway", img=PCIMG_CANAL,
        alt="A ship passing through the lock chambers of the Panama Canal",
        blurb="The engineering half of the city — and the half most people get the timing wrong on.",
        items=[("/articles/panama-canal-tour-miraflores-locks-visitor-guide","Miraflores Locks","Transit times, ticket tiers and which viewing deck is worth it."),
               ("/articles/amador-causeway-biomuseo-guide","Amador Causeway &amp; Biomuseo","The four islands built from canal spoil, and Gehry's museum at the entrance.")]),
   dict(t="Getting out of the city", img=PCIMG_DAY,
        alt="A street on Isla Taboga, a short ferry ride from Panama City",
        blurb="Almost everything else on this site is a day trip or a short flight from here.",
        items=[("/articles/day-trips-from-panama-city","Seven Day Trips, Ranked","Taboga, El Valle, the canal expansion and four more, with real travel times."),
               ("/articles/el-valle-day-trip-from-panama-city","El Valle in a Day","The crater town two hours west — the most-taken day trip of the lot.")])],
  cta=None,
  index=[("/articles/panama-city-itinerary-3-days","Panama City in 3 Days: The Perfect Itinerary","Planning"),
         ("/articles/casco-viejo-panama-walking-guide","Casco Viejo: The Complete Walking Guide","Old quarter"),
         ("/articles/panama-canal-tour-miraflores-locks-visitor-guide","Panama Canal: Miraflores Locks Visitor Guide","The canal"),
         ("/articles/amador-causeway-biomuseo-guide","Amador Causeway &amp; Biomuseo","Half-day"),
         ("/articles/day-trips-from-panama-city","Best Day Trips From Panama City","Day trips")],
 ),

 "es-el-valle-de-anton": dict(
  out="public/es/articles/el-valle-de-anton.html",
  lang="es", alt_lang="en", alt_url="/articles/el-valle-de-anton",
  name="El Valle de Antón", region="Coclé", lat=8.6003, lon=-80.1264,
  title="El Valle de Antón: Guía Completa 2026",
  desc="Todo lo que sabemos de El Valle de Antón — el pueblo dentro del cráter de un volcán, a dos horas de la capital. Senderos, cascadas, aguas termales, tours y cómo organizar el viaje.",
  hero=IMG+"elvalle-crater-hero.webp",
  hero_alt="Familias en el pasto bajo las paredes boscosas del cráter de El Valle de Antón",
  eyebrow="Guía de destino",
  dek="Un pueblo de 7,000 habitantes dentro de la caldera de un volcán que hizo erupción hace unos 200,000 años. A dos horas de la capital, 600 metros de altura y unos diez grados más fresco que la costa.",
  pills=["2 h desde la capital","600 m de altura","Provincia de Coclé"],
  intro=[
   "El Valle de Antón está sobre el piso plano de un cráter volcánico de unos cinco kilómetros de ancho — una de las pocas calderas habitadas del mundo. Las paredes que se ven desde la calle principal son el borde del cráter.",
   "Esa geografía es toda la razón para venir. La altura mantiene el clima fresco todo el año, las paredes guardan bosque nuboso lleno de aves y orquídeas, y las quebradas que bajan de ellas forman cascadas y pozos termales a distancia caminable del pueblo. Es la escapada de montaña más fácil desde la ciudad, y casi todos la hacen en un día cuando merece dos."],
  facts=[("Cómo llegar","Bus desde la terminal de Albrook, unas 2½ h. En carro son 2 h por la Panamericana, salida en Las Uvas."),
         ("Cuándo ir","De diciembre a abril es temporada seca. En temporada verde las cascadas llevan más agua y llueve por la tarde."),
         ("Cuánto quedarse","Un día alcanza. Dos noches permiten caminar temprano, cuando el borde del cráter está despejado."),
         ("Cómo moverse","El pueblo es plano y compacto — aquí la bicicleta gana. Los senderos quedan a 10–25 min del centro.")],
  start=[("/es/articles/que-hacer-el-valle-de-anton","Qué hacer en El Valle de Antón","El panorama completo — cada atracción, cuánto cuesta y cuáles valen la pena.",IMG+"elvalle-church.webp"),
         ("/es/articles/el-valle-de-anton-desde-ciudad-de-panama","El Valle desde Ciudad de Panamá","Horarios, transporte y un itinerario realista para hacerlo en un día sin correr.",IMG+"elvalle-town.webp"),
         ("/es/articles/senderos-el-valle-de-anton","Los mejores senderos","Todas las rutas del cráter por dificultad, con tiempos e indicaciones de acceso.",IMG+"elvalle-bridge.webp")],
  groups=[
   dict(t="Senderos y cumbres", img=IMG+"elvalle-indiadormida.webp",
        alt="La cresta de La India Dormida, el perfil que forma la pared norte del cráter",
        blurb="El borde del cráter es la razón para traer botas. Dos de estas son medio día; la tercera es una subida de verdad.",
        items=[("/es/articles/sendero-india-dormida-el-valle-de-anton","Sendero La India Dormida","La caminata insignia — el perfil de la mujer dormida que se ve desde el pueblo."),
               ("/es/articles/senderos-el-valle-de-anton","Todos los senderos","Las rutas del cráter comparadas: tiempos, desniveles y accesos.")]),
   dict(t="Cascadas y agua caliente", img=IMG+"elvalle-elmachowaterfall.webp",
        alt="El Chorro El Macho cayendo por la roca entre bosque denso",
        blurb="El agua que baja de las paredes del cráter alimenta tanto las cascadas como los pozos termales — dos de los tres sitios más visitados.",
        items=[("/es/articles/cascada-chorro-el-macho-el-valle-de-anton","Cascada Chorro El Macho","La caída de 35 metros al oeste del pueblo, y el canopy que pasa por encima."),
               ("/es/articles/aguas-termales-el-valle-de-anton","Aguas termales","Los pozos de barro y agua caliente: precios, horarios y qué esperar.")]),
   dict(t="Familia, animales y aventura", img=IMG+"elvalle-flowermarket.webp",
        alt="Plantas y flores a la venta bajo el techo del mercado de El Valle",
        blurb="Qué hacer los días que no se camina — y qué funciona con niños.",
        items=[("/es/articles/zoologico-el-nispero-el-valle-de-anton","Zoológico El Níspero","La rana dorada, el mariposario y qué tanto rinde con niños pequeños."),
               ("/es/articles/canopy-el-valle-de-anton-cabalgatas-aventura","Canopy y cabalgatas","Tirolesa sobre el bosque, caballos y las demás opciones de aventura."),
               ("/es/articles/tours-el-valle-de-anton","Tours y precios","Las opciones guiadas y cuánto cuesta cada una en 2026.")])],
  cta=dict(img=IMG+"evbike-bike-crater.webp", eyebrow="E-Valley Bikes · El Valle",
           h="Recorre el cráter completo en bici.",
           p="Tours autoguiados en e-bike desde $30 — casco, audioguía con GPS y candado incluidos. El piso del volcán a tu ritmo.",
           btn="Ver los tours en bici", href="/funnels/evalley_elvalle",
           micro="Cuatro rutas · Aptas para principiantes y familias · Cancelación gratis hasta 24 h antes"),
  index=[("/es/articles/que-hacer-el-valle-de-anton","Qué Hacer en El Valle de Antón","General"),
         ("/es/articles/el-valle-de-anton-desde-ciudad-de-panama","El Valle de Antón desde Ciudad de Panamá","Cómo llegar"),
         ("/es/articles/senderos-el-valle-de-anton","Senderos El Valle de Antón","Senderismo"),
         ("/es/articles/sendero-india-dormida-el-valle-de-anton","Sendero La India Dormida","Senderismo"),
         ("/es/articles/cascada-chorro-el-macho-el-valle-de-anton","Cascada Chorro El Macho","Cascadas"),
         ("/es/articles/aguas-termales-el-valle-de-anton","Aguas Termales El Valle de Antón","Termales"),
         ("/es/articles/zoologico-el-nispero-el-valle-de-anton","Zoológico El Níspero","Familia"),
         ("/es/articles/canopy-el-valle-de-anton-cabalgatas-aventura","Canopy y Cabalgatas","Aventura"),
         ("/es/articles/tours-el-valle-de-anton","Tours en El Valle de Antón","Tours")],
  ui=dict(start_eyebrow="Por dónde empezar", start_h="Si solo lees tres",
          start_dek="Las tres guías que responden casi todo lo que la gente pregunta antes de un primer viaje.",
          card_cta="Leer la guía", lib_eyebrow="La biblioteca completa",
          lib_count="guías", lang_badge="EN",
          lang_t="Also in English", lang_d="La biblioteca en inglés cubre temas distintos — guías propias, no traducciones.",
          lang_btn="Read in English"),
 ),

 "es-boquete": dict(
  out="public/es/articles/boquete.html",
  lang="es", alt_lang="en", alt_url="/articles/boquete",
  name="Boquete", region="Chiriquí", lat=8.7799, lon=-82.4419,
  title="Boquete, Panamá: Guía Completa 2026",
  desc="Todo lo que sabemos de Boquete — el pueblo cafetero de las tierras altas de Chiriquí. Fincas de café, Volcán Barú, aguas termales, senderos y cómo organizar el viaje.",
  hero=BQIMG+"boquete-hills.webp",
  hero_alt="Nubes bajando sobre las lomas boscosas que rodean Boquete, en las tierras altas de Chiriquí",
  eyebrow="Guía de destino",
  dek="Un pueblo cafetero a 1,200 metros en las tierras altas de Chiriquí, a una hora de la frontera con Costa Rica. Fresco, húmedo, verde, y la base de la única caminata en Panamá que muestra dos océanos a la vez.",
  pills=["1,200 m de altura","Provincia de Chiriquí","7 h desde la capital"],
  intro=[
   "Boquete está en un valle sobre el flanco este del Volcán Barú, el punto más alto de Panamá. La altura hace aquí lo mismo que en El Valle, pero más: es genuinamente fresco, llueve seguido y el bosque nuboso empieza más o menos donde termina el pueblo.",
   "Es la zona cafetera del país y su destino de montaña más conocido, lo que atrae a dos públicos distintos: quienes vienen a subir el Barú y hacer los senderos de cascadas, y una comunidad grande y establecida de residentes extranjeros. Estas guías están escritas para los primeros, aunque el detalle práctico sirve a ambos."],
  facts=[("Cómo llegar","Vuelo a David (45 min desde la capital) y 45 min por carretera. Por tierra son 7 h en bus."),
         ("Cuándo ir","De diciembre a abril es lo más seco. El <em>bajareque</em> — llovizna fina con viento — puede caer cualquier mes."),
         ("Cuánto quedarse","Tres días cubren el café, un sendero de cascadas y las termales. El Barú pide un cuarto."),
         ("Cómo moverse","El pueblo se camina; las fincas y los senderos no. Bici, taxi o carro alquilado.")],
  start=[("/es/articles/que-hacer-en-boquete-guia-completa","Qué hacer en Boquete","El panorama completo — senderos, fincas, termales y miradores.",BQIMG+"boquete-town2.webp"),
         ("/es/articles/boquete-panama-guia-completa-itinerario","Boquete en tres días","Un itinerario probado que cubre el café, un sendero y el Barú sin correr.",BQIMG+"boquete-clouds.webp"),
         ("/es/articles/volcan-baru-como-subir-cima-panama","Subir el Volcán Barú","La caminata nocturna a la cima — el único punto donde se ven los dos océanos.",BQIMG+"boquete-volcanbaru.webp")],
  groups=[
   dict(t="Senderos y el volcán", img=BQIMG+"boquete-bridge.webp",
        alt="Un puente peatonal en un sendero de bosque sobre Boquete",
        blurb="El senderismo en Boquete va de un circuito fácil de cascadas a una subida nocturna de 3,475 metros.",
        items=[("/es/articles/volcan-baru-como-subir-cima-panama","Volcán Barú","La subida nocturna, el amanecer y qué tan dura es en realidad."),
               ("/es/articles/senderos-en-boquete-guia-completa","Todos los senderos","Rutas y cascadas con tiempos, desniveles y qué les hace el clima.")]),
   dict(t="Café y bosque nuboso", img=BQIMG+"boquete-losquetzales.webp",
        alt="Bosque nuboso cubierto de musgo en el sendero Los Quetzales, cerca de Boquete",
        blurb="Lo que Boquete hace mejor que casi cualquier lugar: café de especialidad y quetzales, a pocos kilómetros uno del otro.",
        items=[("/es/articles/tours-en-boquete-panama","Tours de café y precios","Qué finca elegir, qué incluye un tour y de qué va tanto ruido con el Geisha."),
               ("/es/articles/que-hacer-en-boquete-guia-completa","Qué más hacer","Miradores, jardines y el resto del pueblo.")]),
   dict(t="Agua caliente, río y cómo llegar", img=BQIMG+"boquete-river2.webp",
        alt="El río Caldera corriendo sobre las piedras bajo Boquete",
        blurb="Los días que no se sube nada — y cómo llegar aquí sin carro propio.",
        items=[("/es/articles/aguas-termales-caldera-boquete","Aguas Termales de Caldera","Los pozos termales valle abajo: precios, temperaturas y el camino de entrada."),
               ("/es/articles/rafting-boquete-rio-chiriqui","Rafting en el Río Chiriquí","Los rápidos, las temporadas y qué nivel se necesita."),
               ("/es/articles/como-llegar-a-boquete-sin-carro","Cómo llegar sin carro","Buses, vuelos y conexiones desde la capital y David."),
               ("/es/articles/alquiler-de-bicicletas-boquete","Alquiler de bicicletas","E-bikes desde $35 y las rutas que sí valen la pena.")])],
  cta=dict(img=BQIMG+"boquete-ebike-hero.webp", eyebrow="E-Valley Bikes · Boquete",
           h="Recorre los caminos del café.",
           p="Tours autoguiados en e-bike por el valle de Boquete — casco, audioguía con GPS y candado incluidos. Las subidas son el punto, y el motor las hace posibles.",
           btn="Ver las rutas de Boquete", href="/funnels/evalley_boquete",
           micro="Varias rutas · Aptas para principiantes y familias · Cancelación gratis hasta 24 h antes"),
  index=[("/es/articles/que-hacer-en-boquete-guia-completa","Qué Hacer en Boquete","General"),
         ("/es/articles/boquete-panama-guia-completa-itinerario","Boquete Panamá: Itinerario de 3 Días","Planificación"),
         ("/es/articles/senderos-en-boquete-guia-completa","Senderos en Boquete","Senderismo"),
         ("/es/articles/volcan-baru-como-subir-cima-panama","Volcán Barú: Subir a la Cima","Senderismo"),
         ("/es/articles/aguas-termales-caldera-boquete","Aguas Termales de Caldera","Termales"),
         ("/es/articles/rafting-boquete-rio-chiriqui","Rafting en Boquete: Río Chiriquí","Aventura"),
         ("/es/articles/tours-en-boquete-panama","Tours en Boquete: Café, Bici y Precios","Tours"),
         ("/es/articles/alquiler-de-bicicletas-boquete","Alquiler de Bicicletas en Boquete","Bicicletas"),
         ("/es/articles/como-llegar-a-boquete-sin-carro","Cómo Llegar a Boquete Sin Carro","Cómo llegar")],
  ui=dict(start_eyebrow="Por dónde empezar", start_h="Si solo lees tres",
          start_dek="Las tres guías que responden casi todo lo que la gente pregunta antes de un primer viaje.",
          card_cta="Leer la guía", lib_eyebrow="La biblioteca completa",
          lib_count="guías", lang_badge="EN",
          lang_t="Also in English", lang_d="La biblioteca en inglés cubre temas distintos — guías propias, no traducciones.",
          lang_btn="Read in English"),
 ),

 "es-panama-city": dict(
  out="public/es/articles/panama-city.html",
  lang="es", alt_lang="en", alt_url="/articles/panama-city",
  name="Ciudad de Panamá", region="Panamá", lat=8.9824, lon=-79.5199,
  title="Ciudad de Panamá: Guía Completa 2026",
  desc="Todo lo que sabemos de Ciudad de Panamá — el Casco Viejo, el Canal, la Cinta Costera y las escapadas de un día. Qué ver, cuánto toma y cuánto cuesta.",
  hero=PCIMG_HERO,
  hero_alt="El skyline de Ciudad de Panamá visto desde el otro lado de la bahía",
  eyebrow="Guía de destino",
  dek="Una capital con rascacielos de vidrio a un lado de la bahía y un casco amurallado de 350 años al otro, unidos por el canal que puso a los dos ahí.",
  pills=["Costa pacífica","Casco Antiguo UNESCO","Punto de partida del país"],
  intro=[
   "Ciudad de Panamá es la única capital de América con selva dentro de sus límites y un canal interoceánico al final de una línea de metro. La mayoría le da dos días de paso hacia otro lado, más o menos la mitad de lo que pide.",
   "Para organizarse, la ciudad se divide sola: el Casco Viejo, donde está casi todo lo de comer y beber; el canal y la Calzada de Amador, que es la ingeniería; y todo lo que queda a menos de tres horas, que es donde empieza el resto de este sitio."],
  facts=[("Cómo llegar","Tocumen (PTY) es el aeropuerto principal; Albrook (PAC) maneja los vuelos internos. La Línea 2 del metro llega a Tocumen."),
         ("Cuándo ir","De diciembre a abril es seco. El canal y los museos funcionan con cualquier clima."),
         ("Cuánto quedarse","Dos días para la ciudad. Tres si se quiere el canal sin apuro."),
         ("Cómo moverse","El metro es rápido, barato y seguro. Uber funciona bien. Manejar en el Casco no vale la pena.")],
  start=[("/es/articles/que-hacer-en-ciudad-de-panama","Qué hacer en Ciudad de Panamá","El panorama completo — qué ver, cuánto toma y qué se puede saltar.",PCIMG_ITIN),
         ("/es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse","Casco Viejo: comer, beber y dormir","Dónde comer bien en el casco, desde fondas hasta lo caro, y dónde quedarse.",PCIMG_CASCO),
         ("/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo","Cinta Costera y Panamá Viejo","El malecón, el mercado de mariscos y las ruinas de la ciudad original.",PCIMG_CANAL)],
  groups=[
   dict(t="El casco antiguo", img=PCIMG_CASCO,
        alt="Fachadas coloniales restauradas y balcones en el Casco Viejo",
        blurb="El Casco Viejo es la razón por la que la ciudad está en la lista de la UNESCO, y la única parte hecha para caminar.",
        items=[("/es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse","Dónde comer, beber y dormir","Restaurantes por rango de precio, bares de azotea y dónde alojarse."),
               ("/es/articles/que-hacer-en-ciudad-de-panama","Qué hacer en la ciudad","Cómo encaja el casco en una visita corta.")]),
   dict(t="El canal y la costa", img=PCIMG_CANAL,
        alt="Un barco pasando por las esclusas del Canal de Panamá",
        blurb="La mitad ingeniera de la ciudad — y la que más gente calcula mal en cuanto a horarios.",
        items=[("/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo","Cinta Costera y Mercado de Mariscos","El malecón, el ceviche y las ruinas de Panamá Viejo en una sola salida.")]),
   dict(t="Salir de la ciudad", img=PCIMG_DAY,
        alt="Una calle en Isla Taboga, a un viaje corto en ferry de la capital",
        blurb="Casi todo lo demás en este sitio es una escapada de un día o un vuelo corto desde aquí.",
        items=[("/es/articles/el-valle-de-anton-desde-ciudad-de-panama","El Valle de Antón en un día","El pueblo del cráter a dos horas — la escapada más hecha de todas."),
               ("/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama","Cómo llegar a Bocas del Toro","Vuelo, bus y lancha comparados, con tiempos reales.")])],
  cta=None,
  index=[("/es/articles/que-hacer-en-ciudad-de-panama","Qué Hacer en Ciudad de Panamá","General"),
         ("/es/articles/casco-viejo-restaurantes-donde-comer-beber-hospedarse","Casco Viejo: Dónde Comer, Beber y Dormir","Casco Viejo"),
         ("/es/articles/cinta-costera-panama-mercado-mariscos-panama-viejo","Cinta Costera, Mercado de Mariscos y Panamá Viejo","Costa"),
         ("/es/articles/como-llegar-a-bocas-del-toro-desde-ciudad-de-panama","Cómo Llegar a Bocas del Toro","Escapadas")],
  ui=dict(start_eyebrow="Por dónde empezar", start_h="Si solo lees tres",
          start_dek="Las tres guías que responden casi todo lo que la gente pregunta antes de un primer viaje.",
          card_cta="Leer la guía", lib_eyebrow="La biblioteca completa",
          lib_count="guías", lang_badge="EN",
          lang_t="Also in English", lang_d="La biblioteca en inglés cubre temas distintos — guías propias, no traducciones.",
          lang_btn="Read in English"),
 ),

}

HUB_CSS = """
<style id="ps-hub-styles">
main.hub{--hub-gap:clamp(64px,7.5vw,104px)}
.hub-wrap{max-width:var(--maxw);margin:0 auto;padding:0 clamp(18px,4vw,40px)}
.hub-narrow{max-width:74ch}
.hub-sec{padding:var(--hub-gap,80px) 0}
.hub-eyebrow{font-family:var(--mono);font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--terra);margin:0 0 14px}
.hub-h2{font-family:var(--serif);font-size:clamp(1.9rem,4vw,2.9rem);line-height:1.08;color:var(--navy);margin:0 0 14px;font-weight:400}
.hub-lead{font-family:var(--sans);font-size:1.07rem;line-height:1.72;color:var(--ink-soft);margin:0 0 1.1em}
.hub-rule{height:1px;background:var(--border-light);border:0;margin:0}

/* hero */
.hub-hero{position:relative;min-height:clamp(520px,72vh,760px);display:flex;align-items:flex-end;overflow:hidden}
.hub-hero-img{position:absolute;inset:0}
.hub-hero-img img{width:100%;height:100%;object-fit:cover;display:block}
.hub-hero-scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(7,35,87,.14) 0%,rgba(7,35,87,.30) 42%,rgba(7,35,87,.82) 100%)}
.hub-hero-body{position:relative;padding:clamp(96px,14vh,150px) 0 clamp(48px,7vw,76px);color:#fff;width:100%}
.hub-hero-body .hub-eyebrow{color:#ffd9d5}
.hub-hero h1{font-family:var(--serif);font-weight:400;font-size:clamp(2.8rem,7.4vw,5.4rem);line-height:.98;margin:0 0 18px;color:#fff;letter-spacing:-.015em}
.hub-hero-dek{font-family:var(--sans);font-size:clamp(1.02rem,1.6vw,1.2rem);line-height:1.62;max-width:58ch;color:rgba(255,255,255,.93);margin:0 0 30px}
.hub-pills{display:flex;flex-wrap:wrap;gap:8px}
.hub-pill{font-family:var(--mono);font-size:.7rem;letter-spacing:.07em;text-transform:uppercase;color:#fff;border:1px solid rgba(255,255,255,.42);border-radius:999px;padding:6px 13px;backdrop-filter:blur(6px);background:rgba(255,255,255,.10)}

/* orientation */
.hub-orient{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:clamp(34px,5.5vw,80px);align-items:start}
.hub-facts{border-top:2px solid var(--navy);padding-top:20px}
.hub-fact{padding:15px 0;border-bottom:1px solid var(--border-light)}
.hub-fact:last-child{border-bottom:0}
.hub-fact dt{font-family:var(--mono);font-size:.68rem;letter-spacing:.13em;text-transform:uppercase;color:var(--terra);margin-bottom:6px}
.hub-fact dd{margin:0;font-family:var(--sans);font-size:.94rem;line-height:1.6;color:var(--ink-soft)}

/* start-here cards */
.hub-start{display:grid;grid-template-columns:repeat(auto-fit,minmax(272px,1fr));gap:clamp(18px,2.4vw,30px);margin-top:38px}
.hub-card{display:flex;flex-direction:column;text-decoration:none;background:#fff;border:1px solid var(--border-light);border-radius:3px;overflow:hidden;transition:border-color .22s,transform .22s,box-shadow .22s}
.hub-card:hover{border-color:var(--navy);transform:translateY(-3px);box-shadow:0 14px 34px -20px rgba(7,35,87,.42)}
.hub-card-img{aspect-ratio:16/10;overflow:hidden;background:var(--cream)}
.hub-card-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s ease}
.hub-card:hover .hub-card-img img{transform:scale(1.04)}
.hub-card-body{padding:20px 22px 24px;display:flex;flex-direction:column;gap:9px;flex:1}
.hub-card h3{font-family:var(--serif);font-weight:400;font-size:1.42rem;line-height:1.16;color:var(--navy);margin:0}
.hub-card p{font-family:var(--sans);font-size:.92rem;line-height:1.6;color:var(--ink-mute);margin:0;flex:1}
.hub-card-go{font-family:var(--mono);font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--terra);display:flex;align-items:center;gap:7px}

/* themed groups */
.hub-group{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:clamp(28px,4.6vw,68px);align-items:center;padding:clamp(48px,6vw,76px) 0;border-bottom:1px solid var(--border-light)}
.hub-group:first-of-type{padding-top:0}
.hub-group:last-of-type{border-bottom:0;padding-bottom:0}
.hub-group:nth-child(even) .hub-group-media{order:2}
.hub-group-media{aspect-ratio:4/3;overflow:hidden;border-radius:3px;background:var(--cream)}
.hub-group-media img{width:100%;height:100%;object-fit:cover;display:block}
.hub-group h2{font-family:var(--serif);font-weight:400;font-size:clamp(1.65rem,3vw,2.3rem);line-height:1.1;color:var(--navy);margin:0 0 12px}
.hub-group-blurb{font-family:var(--sans);font-size:1rem;line-height:1.65;color:var(--ink-soft);margin:0 0 22px;max-width:56ch}
.hub-list{list-style:none;margin:0;padding:0;border-top:1px solid var(--border-light)}
.hub-list li{border-bottom:1px solid var(--border-light)}
.hub-list a{display:flex;gap:16px;align-items:baseline;padding:15px 18px 15px 2px;text-decoration:none;transition:padding .22s,background .22s}
.hub-list a:hover{padding-left:13px;padding-right:16px;background:var(--cream)}
.hub-list .n{font-family:var(--serif);font-size:1.12rem;color:var(--navy);line-height:1.3;flex:1}
.hub-list a:hover .n{color:var(--terra)}
.hub-list .d{font-family:var(--sans);font-size:.88rem;color:var(--ink-mute);line-height:1.5;flex:1.25;display:none}
.hub-list .ar{font-family:var(--mono);color:var(--terra);font-size:.95rem;opacity:0;flex:none;width:12px;text-align:right;transition:opacity .2s,transform .2s}
.hub-list a:hover .ar{opacity:1;transform:translateX(3px)}
@media(min-width:880px){.hub-list .d{display:block}}

/* full index */
.hub-index-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;flex-wrap:wrap;margin-bottom:34px}
.hub-count{font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute)}
.hub-idx{list-style:none;margin:0;padding:0;border-top:2px solid var(--navy)}
.hub-idx li{border-bottom:1px solid var(--border-light)}
.hub-idx a{display:grid;grid-template-columns:auto 1fr auto auto;gap:14px;align-items:center;padding:16px 18px 16px 4px;text-decoration:none;transition:background .2s,padding .2s}
.hub-idx a:hover{background:var(--cream);padding-left:12px;padding-right:16px}
.hub-idx .num{font-family:var(--mono);font-size:.72rem;color:var(--ink-mute);min-width:2ch}
.hub-idx .ttl{font-family:var(--serif);font-size:1.16rem;color:var(--navy);line-height:1.25}
.hub-idx a:hover .ttl{color:var(--terra)}
.hub-idx .cat{font-family:var(--mono);font-size:.64rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-mute);border:1px solid var(--border-light);border-radius:999px;padding:3px 10px;white-space:nowrap}
.hub-idx .ar{font-family:var(--mono);color:var(--terra);opacity:0;flex:none;width:12px;text-align:right;transition:opacity .2s,transform .2s}
.hub-idx a:hover .ar{opacity:1;transform:translateX(3px)}
.hub-lang{margin-top:clamp(44px,5vw,64px);display:flex;gap:22px;align-items:center;flex-wrap:wrap;
  padding:26px 28px;background:#fff;border:1px solid var(--border-light);border-left:3px solid var(--terra);border-radius:3px}
.hub-lang-badge{font-family:var(--mono);font-size:.72rem;font-weight:500;letter-spacing:.1em;color:#fff;background:var(--navy);
  width:42px;height:42px;display:grid;place-items:center;border-radius:2px;flex:none}
.hub-lang-txt{flex:1;min-width:220px}
.hub-lang-t{margin:0 0 4px;font-family:var(--serif);font-size:1.22rem;line-height:1.25;color:var(--navy)}
.hub-lang-d{margin:0;font-family:var(--sans);font-size:.9rem;line-height:1.55;color:var(--ink-mute)}
.hub-lang-btn{font-family:var(--mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--navy);
  text-decoration:none;border:1px solid var(--navy);border-radius:2px;padding:11px 20px;white-space:nowrap;
  display:inline-flex;align-items:center;gap:9px;transition:background .2s,color .2s}
.hub-lang-btn:hover{background:var(--navy);color:#fff}
.hub-lang-btn .ar{transition:transform .2s}
.hub-lang-btn:hover .ar{transform:translateX(3px)}

@media(max-width:860px){
  .hub-orient,.hub-group{grid-template-columns:1fr}
  .hub-group:nth-child(even) .hub-group-media{order:0}
  .hub-idx a{grid-template-columns:auto 1fr;row-gap:6px}
  .hub-idx .cat{grid-column:2;justify-self:start}
  .hub-idx .ar{display:none}
}
</style>
"""


def build_main(c):
    """Compose the hub <main>. Header markup is lifted from the shell so nav
    and language toggle stay in sync with the rest of the site."""
    P = []
    A = P.append
    A('<main class="hub">')

    # ── hero ──────────────────────────────────────────────────────────────
    A('<section class="hub-hero">')
    A(f'<div class="hub-hero-img"><img src="{c["hero"]}" alt="{c["hero_alt"]}" '
      'loading="eager" fetchpriority="high" decoding="async"></div>')
    A('<div class="hub-hero-scrim"></div>')
    A('<div class="hub-hero-body"><div class="hub-wrap">')
    A(f'<p class="hub-eyebrow">{c["eyebrow"]}</p>')
    A(f'<h1>{c["name"]}</h1>')
    A(f'<p class="hub-hero-dek">{c["dek"]}</p>')
    A('<div class="hub-pills">' + ''.join(f'<span class="hub-pill">{p}</span>' for p in c["pills"]) + '</div>')
    A('</div></div></section>')

    # ── orientation + facts ───────────────────────────────────────────────
    A('<section class="hub-sec"><div class="hub-wrap"><div class="hub-orient">')
    A('<div>' + ''.join(f'<p class="hub-lead">{p}</p>' for p in c["intro"]) + '</div>')
    A('<dl class="hub-facts">')
    for k, v in c["facts"]:
        A(f'<div class="hub-fact"><dt>{k}</dt><dd>{v}</dd></div>')
    A('</dl></div></div></section>')

    # ── start here ────────────────────────────────────────────────────────
    A('<hr class="hub-rule"><section class="hub-sec"><div class="hub-wrap">')
    T = c.get("ui", {})
    A(f'<p class="hub-eyebrow">{T.get("start_eyebrow","Start here")}</p>')
    A(f'<h2 class="hub-h2">{T.get("start_h","If you only read three")}</h2>')
    A(f'<p class="hub-lead hub-narrow">{T.get("start_dek","The three guides that answer most of what people ask before a first trip.")}</p>')
    A('<div class="hub-start">')
    for href, t, d, img in c["start"]:
        A(f'<a class="hub-card" href="{href}">'
          f'<div class="hub-card-img"><img src="{img}" alt="" loading="lazy" decoding="async"></div>'
          f'<div class="hub-card-body"><h3>{t}</h3><p>{d}</p>'
          f'<span class="hub-card-go">{T.get("card_cta","Read the guide")} <span aria-hidden="true">&rarr;</span></span>'
          '</div></a>')
    A('</div></div></section>')

    # ── themed groups ─────────────────────────────────────────────────────
    A('<hr class="hub-rule"><section class="hub-sec"><div class="hub-wrap">')
    for g in c["groups"]:
        A('<div class="hub-group">')
        A(f'<div class="hub-group-media"><img src="{g["img"]}" alt="{g["alt"]}" loading="lazy" decoding="async"></div>')
        A('<div>')
        A(f'<h2>{g["t"]}</h2>')
        A(f'<p class="hub-group-blurb">{g["blurb"]}</p>')
        A('<ul class="hub-list">')
        for href, n, d in g["items"]:
            A(f'<li><a href="{href}"><span class="n">{n}</span><span class="d">{d}</span>'
              '<span class="ar" aria-hidden="true">&rarr;</span></a></li>')
        A('</ul></div></div>')
    A('</div></section>')

    # ── client CTA (only where we have a client in that destination) ──────
    cta = c.get("cta")
    if cta:
     A('<div class="hub-wrap" style="margin:clamp(20px,4vw,44px) auto">')
     A('<div class="evb-cta" style="--evb-accent:#ea450e;--evb-accent-d:#c2370a;--evb-shadow:rgba(234,69,14,.30);'
       '--evb-ink:#2F280B;--evb-ink-soft:#5a4d38;--evb-muted:#8b7e6b;--evb-cream:#f7f5ee;--evb-line:#e8e1d2;--evb-gold:#e7b75a">'
       '<div class="evb-banner">')
     A(f'<div class="evb-banner-img" style="background-image:url(\'{cta["img"]}\')"></div>')
     A('<div class="evb-banner-body">')
     A(f'<span class="evb-eyebrow">{cta["eyebrow"]}</span>')
     A(f'<h3>{cta["h"]}</h3><p>{cta["p"]}</p>')
     A(f'<a class="evb-btn" href="{cta["href"]}"><span>{cta["btn"]}</span>'
       '<span class="evb-ar" aria-hidden="true">&rarr;</span></a>')
     A(f'<div class="evb-micro">{cta["micro"]}</div>')
     A('</div></div></div></div>')

    # ── complete index ────────────────────────────────────────────────────
    A('<hr class="hub-rule"><section class="hub-sec"><div class="hub-wrap">')
    A('<div class="hub-index-head"><div>')
    A(f'<p class="hub-eyebrow">{T.get("lib_eyebrow","The full library")}</p>')
    A(f'<h2 class="hub-h2">{T.get("lib_h", "Every " + c["name"] + " guide")}</h2></div>')
    A(f'<span class="hub-count">{len(c["index"])} {T.get("lib_count","guides")}</span>')
    A('</div><ol class="hub-idx">')
    for i, (href, t, cat) in enumerate(c["index"], 1):
        A(f'<li><a href="{href}"><span class="num">{i:02d}</span><span class="ttl">{t}</span>'
          f'<span class="cat">{cat}</span><span class="ar" aria-hidden="true">&rarr;</span></a></li>')
    A('</ol>')
    A('<aside class="hub-lang">'
      f'<span class="hub-lang-badge">{T.get("lang_badge","ES")}</span>'
      '<div class="hub-lang-txt">'
      f'<p class="hub-lang-t">{T.get("lang_t","Tambi&eacute;n en espa&ntilde;ol")}</p>'
      f'<p class="hub-lang-d">{T.get("lang_d","The Spanish library covers different ground &mdash; separate guides, not translations.")}</p>'
      '</div>'
      f'<a class="hub-lang-btn" href="{c["alt_url"]}">{T.get("lang_btn","Ver en espa&ntilde;ol")} <span class="ar" aria-hidden="true">&rarr;</span></a>'
      '</aside>')
    A('</div></section>')
    A('</main>')
    return '\n'.join(P)


def jsonld(c, base="https://panamaspot.com"):
    url = base + "/" + c["out"].replace("public/", "").replace(".html", "")
    items = [{"@type": "ListItem", "position": i, "url": base + h, "name": H.unescape(t)}
             for i, (h, t, _) in enumerate(c["index"], 1)]
    blocks = [
      {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
        {"@type": "ListItem", "position": 2, "name": c["name"]}]},
      {"@context": "https://schema.org", "@type": "CollectionPage",
       "@id": url + "#collection", "url": url, "name": H.unescape(c["title"]),
       "description": c["desc"], "inLanguage": "es-PA" if c["lang"] == "es" else "en-US",
       "isPartOf": {"@id": base + "/#website"},
       "about": {"@id": url + "#destination"},
       "primaryImageOfPage": {"@type": "ImageObject", "url": c["hero"] if c["hero"].startswith("http") else base + c["hero"]},
       "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": items}},
      {"@context": "https://schema.org", "@type": "TouristDestination",
       "@id": url + "#destination", "name": c["name"],
       "description": c["desc"], "url": url,
       "address": {"@type": "PostalAddress", "addressRegion": c.get("region","Coclé"), "addressCountry": "PA"},
       "geo": {"@type": "GeoCoordinates", "latitude": c.get("lat",8.6003), "longitude": c.get("lon",-80.1264)}},
    ]
    return '\n'.join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + '</script>'
                     for b in blocks)


def build(slug):
    c = HUBS[slug]
    slug_path = c["out"].replace("public/", "").replace(".html", "")
    shell = (SHELL_ES if c["lang"] == "es" else SHELL_EN).read_text(encoding="utf8")
    url = "https://panamaspot.com/" + slug_path

    head = shell[:shell.index("</head>")]
    footer = shell[shell.index("<footer"):shell.index("</footer>") + len("</footer>")]
    tail = shell[shell.index("</footer>") + len("</footer>"):]
    header = shell[shell.index("<header"):shell.index("</header>") + len("</header>")]
    # the toggle is inherited from the shell article; point it at this hub's pair
    en_url = url if c["lang"] == "en" else c["alt_url"]
    es_url = c["alt_url"] if c["lang"] == "en" else "/" + slug_path
    header = re.sub(r'(<a[^>]*hreflang="en"[^>]*href=")[^"]*(")',
                    lambda m: m.group(1) + en_url + m.group(2), header)
    header = re.sub(r'(<a[^>]*href=")[^"]*("[^>]*hreflang="en")',
                    lambda m: m.group(1) + en_url + m.group(2), header)
    header = re.sub(r'(<a[^>]*hreflang="es"[^>]*href=")[^"]*(")',
                    lambda m: m.group(1) + es_url + m.group(2), header)
    header = re.sub(r'(<a[^>]*href=")[^"]*("[^>]*hreflang="es")',
                    lambda m: m.group(1) + es_url + m.group(2), header)

    # strip the shell's article-specific structured data, keep Organization + WebSite
    blocks = re.findall(r'<script type="application/ld\+json">.*?</script>', head, re.S)
    for b in blocks:
        if '"Organization"' in b or '"WebSite"' in b:
            continue
        head = head.replace(b, "")

    def setmeta(h, key, val, attr="name"):
        pat = re.compile(rf'(<meta [^>]*{attr}="{re.escape(key)}"[^>]*>)')
        new = f'<meta {attr}="{key}" content="{H.escape(val, quote=True)}"/>'
        return pat.sub(new, h) if pat.search(h) else h.replace("</title>", "</title>" + new, 1)

    head = re.sub(r"<title>.*?</title>", f"<title>{c['title']}</title>", head, flags=re.S)
    for k, v in [("description", c["desc"])]:
        head = setmeta(head, k, v)
    hero_abs = c["hero"] if c["hero"].startswith("http") else "https://panamaspot.com" + c["hero"]
    for k, v in [("og:title", c["title"]), ("og:description", c["desc"]), ("og:url", url),
                 ("og:type", "website"), ("og:locale", "es_PA" if c["lang"] == "es" else "en_US"),
                 ("og:image", hero_abs)]:
        head = setmeta(head, k, v, "property")
    for k, v in [("twitter:title", c["title"]), ("twitter:description", c["desc"]),
                 ("twitter:image", hero_abs)]:
        head = setmeta(head, k, v)
    head = re.sub(r'<link[^>]+rel="canonical"[^>]*>', f'<link href="{url}" rel="canonical"/>', head)
    en_href = url if c["lang"] == "en" else "https://panamaspot.com" + c["alt_url"]
    es_href = ("https://panamaspot.com" + c["alt_url"]) if c["lang"] == "en" else url
    head = re.sub(r'<link[^>]+hreflang="en"[^>]*>', f'<link href="{en_href}" hreflang="en" rel="alternate"/>', head)
    head = re.sub(r'<link[^>]+hreflang="es"[^>]*>', f'<link href="{es_href}" hreflang="es" rel="alternate"/>', head)
    head = re.sub(r'<link[^>]+hreflang="x-default"[^>]*>',
                  f'<link href="{en_href}" hreflang="x-default" rel="alternate"/>', head)
    # article-only meta that must not survive onto a collection page
    head = re.sub(r'<meta [^>]*property="article:[^"]*"[^>]*>', "", head)

    head += jsonld(c) + HUB_CSS + "</head>"
    body_open = re.search(r"<body[^>]*>", shell).group(0)
    main = build_main(c).replace("<main class=\"hub\">", "<main class=\"hub\">" + header, 1)
    out = head + body_open + main + footer + tail
    dest = ROOT / c["out"]
    dest.write_text(out, encoding="utf8")
    print(f"  wrote {c['out']}  ({len(out)//1024} KB)")


if __name__ == "__main__":
    for s in (sys.argv[1:] or list(HUBS.keys())):
        build(s)
