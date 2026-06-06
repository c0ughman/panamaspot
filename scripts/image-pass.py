import re, json, os

D = {'boquete':'/images/boquete/', 'elvalle':'/images/el-valle/'}
D_ROOT = '/images/'

# ── WebP manifest (written by optimize-images.sh) ─────────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = json.load(open(os.path.join(_HERE, 'img-manifest.json')))

def webp_of(basename):
    """Strip up to two extensions and add .webp (handles .jpeg.webp, .HEIC, etc.)."""
    stem = basename
    for _ in range(2):
        root, ext = os.path.splitext(stem)
        if ext: stem = root
        else: break
    return stem + '.webp'

def img_dims(webp_web_path):
    """Return (w, h) from the manifest; (0, 0) if not found."""
    e = DIMS.get(webp_web_path, {})
    return e.get('w', 0), e.get('h', 0)

def make_img(src, alt, w, h, priority=False, extra_style=''):
    dim = f' width="{w}" height="{h}"' if w else ''
    lp  = ' fetchpriority="high" loading="eager"' if priority else ' loading="lazy"'
    st  = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block'
    if extra_style: st += ';' + extra_style
    return f'<img src="{src}" alt="{alt}"{dim}{lp} style="{st}">'

# ── Gallery / inline captions ─────────────────────────────────────────────────
# Keys use the ORIGINAL basenames (jpg/JPG) so ALLOC/THEME references stay unchanged.
CAP_EN = {
 'boquete-volcanbaru.jpg':"Volcán Barú, Panama's highest peak at 3,475 m",
 'boquete-forest.jpg':"Cloud forest in the hills above Boquete",
 'boquete-river2.jpg':"A river running through the Boquete valley",
 'boquete-river.jpg':"A river running through the Boquete valley",
 'boquete-bird.jpg':"Birdlife in the Boquete cloud forest",
 'boquete-losquetzales.JPG':"On the Sendero Los Quetzales",
 'boquete-town2.jpg':"The town of Boquete in the Chiriquí highlands",
 'boquete-bridge.jpg':"A river bridge in Bajo Boquete",
 'boquete-rafting.jpg':"Whitewater rafting on the rivers near Boquete",
 'boquete-market.jpg':"The local market in Boquete",
 'boquete-hills.jpg':"Rolling hills in the Boquete highlands",
 'boquete-clouds.jpg':"Cloud cover rolling over the Boquete highlands",
 'boquete-people.jpg':"Everyday life in Boquete",
 'elvalle-indiadormida.jpg':"The La India Dormida ridge above El Valle",
 'elvalle-elmachowaterfall.jpg':"Chorro El Macho waterfall",
 'elvalle-elmachowaterfall2.jpg':"Chorro El Macho waterfall",
 'elvalle-waterfall.jpg':"A waterfall on the slopes around El Valle",
 'elvalle-panorama.jpg':"Panorama of the El Valle caldera",
 'elvalle-church.jpg':"The church in El Valle de Antón",
 'elvalle-bird.jpg':"Birdlife in the El Valle cloud forest",
 'elvalle-market.JPG':"El Valle's open-air market",
 'elvalle-petroglifo.jpg':"Pre-Columbian petroglyphs at Piedra Pintada",
 'elvalle-flowermarket.jpg':"The flower stalls at El Valle's market",
 'elvalle-town.jpg':"The town of El Valle, inside the caldera",
 'elvalle-bridge.jpg':"A footbridge in El Valle de Antón",
 'elvalle-drums.jpg':"Traditional drums — local culture in El Valle",
 'elvalle-shrine.jpg':"A roadside shrine in El Valle de Antón",
 'elvalle-bird2.jpg':"Birdlife in the El Valle cloud forest",
 'elvalle-bird3.jpg':"A hummingbird in the El Valle highlands",
 'elvalle-bird4.jpg':"Birdlife around El Valle de Antón",
 'elvalle-elmachowaterfall3.jpg':"Chorro El Macho waterfall",
}
CAP_ES = {
 'boquete-volcanbaru.jpg':"El Volcán Barú, el punto más alto de Panamá con 3.475 m",
 'boquete-forest.jpg':"Bosque nuboso en las montañas sobre Boquete",
 'boquete-river2.jpg':"Un río atravesando el valle de Boquete",
 'boquete-river.jpg':"Un río atravesando el valle de Boquete",
 'boquete-bird.jpg':"Aves en el bosque nuboso de Boquete",
 'boquete-losquetzales.JPG':"En el Sendero Los Quetzales",
 'boquete-town2.jpg':"El pueblo de Boquete, en las tierras altas de Chiriquí",
 'boquete-bridge.jpg':"Un puente sobre el río en Bajo Boquete",
 'boquete-rafting.jpg':"Rafting en los ríos cerca de Boquete",
 'boquete-market.jpg':"El mercado local de Boquete",
 'boquete-hills.jpg':"Colinas onduladas en las tierras altas de Boquete",
 'boquete-clouds.jpg':"Nubes pasando sobre las tierras altas de Boquete",
 'boquete-people.jpg':"La vida cotidiana en Boquete",
 'elvalle-indiadormida.jpg':"La silueta de La India Dormida sobre El Valle",
 'elvalle-elmachowaterfall.jpg':"La cascada Chorro El Macho",
 'elvalle-elmachowaterfall2.jpg':"La cascada Chorro El Macho",
 'elvalle-waterfall.jpg':"Una cascada en las laderas alrededor de El Valle",
 'elvalle-panorama.jpg':"Panorámica del cráter de El Valle",
 'elvalle-church.jpg':"La iglesia de El Valle de Antón",
 'elvalle-bird.jpg':"Aves en el bosque nuboso de El Valle",
 'elvalle-market.JPG':"El mercado al aire libre de El Valle",
 'elvalle-petroglifo.jpg':"Petroglifos precolombinos en la Piedra Pintada",
 'elvalle-flowermarket.jpg':"Los puestos de flores del mercado de El Valle",
 'elvalle-town.jpg':"El pueblo de El Valle, dentro del cráter",
 'elvalle-bridge.jpg':"Un puente peatonal en El Valle de Antón",
 'elvalle-drums.jpg':"Tambores tradicionales — cultura local en El Valle",
 'elvalle-shrine.jpg':"Un altar al borde del camino en El Valle de Antón",
 'elvalle-bird2.jpg':"Aves en el bosque nuboso de El Valle",
 'elvalle-bird3.jpg':"Un colibrí en las tierras altas de El Valle",
 'elvalle-bird4.jpg':"Aves alrededor de El Valle de Antón",
 'elvalle-elmachowaterfall3.jpg':"La cascada Chorro El Macho",
}

# ── hero + 5 gallery per (location, article-type) ─────────────────────────────
ALLOC = {
 ('boquete',0):('hikes-boquete.jpg',     ['boquete-volcanbaru.jpg','boquete-forest.jpg','boquete-rafting.jpg','boquete-hills.jpg','boquete-bridge.jpg']),
 ('boquete',1):('things-to-do-boquete.HEIC',['boquete-volcanbaru.jpg','boquete-forest.jpg','boquete-market.jpg','boquete-town2.jpg','boquete-bridge.jpg']),
 ('boquete',2):('tours-boquete.jpeg.webp',['boquete-volcanbaru.jpg','boquete-forest.jpg','boquete-town2.jpg','boquete-bridge.jpg','boquete-market.jpg']),
 ('elvalle',0):('hikes-el-valle.jpg',    ['elvalle-elmachowaterfall.jpg','elvalle-bird.jpg','elvalle-waterfall.jpg','elvalle-petroglifo.jpg','elvalle-town.jpg']),
 ('elvalle',1):('things-to-do-el-valle.jpg',['elvalle-church.jpg','elvalle-market.JPG','elvalle-flowermarket.jpg','elvalle-bird.jpg','elvalle-town.jpg']),
 ('elvalle',2):('tours-el-valle.jpg',    ['elvalle-town.jpg','elvalle-flowermarket.jpg','elvalle-drums.jpg','elvalle-shrine.jpg','elvalle-church.jpg']),
}

# ── "Across the region" bento trio ───────────────────────────────────────────
def E(img,tag_en,h3_en,p_en,tag_es,h3_es,p_es):
    return {'img':img,'en':(tag_en,h3_en,p_en),'es':(tag_es,h3_es,p_es)}

RIVER   = E('boquete-river2.jpg','Rivers','Mountain rivers',"Fast, clear rivers run off the highlands around Boquete — good for rafting and riverside walks.",'Ríos','Ríos de montaña',"Ríos rápidos y cristalinos bajan de las tierras altas de Boquete, ideales para rafting y caminatas junto al agua.")
BIRD_B  = E('boquete-bird.jpg','Wildlife','Cloud-forest birdlife',"Boquete's forests are among Panama's best birding — from hummingbirds to the resplendent quetzal.",'Fauna','Aves del bosque nuboso',"Los bosques de Boquete están entre los mejores de Panamá para observar aves, desde colibríes hasta el quetzal resplandeciente.")
MARKET  = E('boquete-market.jpg','Coffee & market',"Boquete's market","Local produce and the world-famous Geisha coffee grown on the surrounding fincas.",'Café y mercado','El mercado de Boquete',"Productos locales y el famoso café Geisha cultivado en las fincas de los alrededores.")
HILLS   = E('boquete-hills.jpg','Landscape','Highland hills',"Rolling green hills and coffee fincas surround the town on every side.",'Paisaje','Cerros de altura',"Cerros verdes y fincas de café rodean el pueblo por todos lados.")
RAFT    = E('boquete-rafting.jpg','Adventure','Whitewater rafting',"The rivers near Boquete offer some of Panama's best whitewater, from gentle to serious rapids.",'Aventura','Rafting en aguas bravas',"Los ríos cerca de Boquete ofrecen de los mejores rápidos de Panamá, de suaves a exigentes.")

PANO    = E('elvalle-panorama.jpg','The caldera','A town inside a volcano',"El Valle sits on the floor of a huge volcanic caldera, ringed by forested crater walls.",'El cráter','Un pueblo dentro de un volcán',"El Valle se asienta en el fondo de un enorme cráter volcánico, rodeado de paredes boscosas.")
FLOWERS = E('elvalle-flowermarket.jpg','Market','Flowers & crafts',"El Valle's open-air market is known for orchids, plants and local handicrafts.",'Mercado','Flores y artesanías',"El mercado al aire libre de El Valle es famoso por sus orquídeas, plantas y artesanías.")
CHURCH  = E('elvalle-church.jpg','The town','El Valle de Antón',"A laid-back mountain town on the floor of an extinct volcano, two hours from the capital.",'El pueblo','El Valle de Antón',"Un tranquilo pueblo de montaña en el fondo de un volcán extinto, a dos horas de la capital.")
INDIA   = E('elvalle-indiadormida.jpg','La India Dormida','The sleeping woman ridge',"The valley's iconic ridgeline, named for its silhouette of a reclining woman, with a steep trail to the top.",'La India Dormida','La cresta de la mujer dormida',"La cresta más emblemática del valle, llamada así por su silueta de mujer recostada, con un sendero empinado hasta la cima.")
ELMACHO = E('elvalle-elmachowaterfall.jpg','Waterfalls','Chorro El Macho',"El Valle's most famous waterfall, a tall cascade reached on a short walk through forest.",'Cascadas','Chorro El Macho',"La cascada más famosa de El Valle, una caída alta a la que se llega por un corto sendero entre el bosque.")

BENTO = {
 ('boquete',0):[RIVER, BIRD_B, MARKET],
 ('boquete',1):[RIVER, BIRD_B, HILLS],
 ('boquete',2):[RIVER, BIRD_B, RAFT],
 ('elvalle',0):[PANO, FLOWERS, CHURCH],
 ('elvalle',1):[INDIA, PANO, ELMACHO],
 ('elvalle',2):[INDIA, PANO, ELMACHO],
}

# ── Inline image pool + scoring ───────────────────────────────────────────────
ALLIMG = {
 'boquete':['boquete-aerial.jpg','boquete-aerial2.jpg','boquete-bird.jpg','boquete-bridge.jpg',
   'boquete-clouds.jpg','boquete-forest.jpg','boquete-hills.jpg','boquete-losquetzales.JPG',
   'boquete-market.jpg','boquete-people.jpg','boquete-rafting.jpg','boquete-river.jpg',
   'boquete-river2.jpg','boquete-rocks.jpg','boquete-town2.jpg','boquete-volcanbaru.jpg'],
 'elvalle':['elvalle-bird.jpg','elvalle-bird2.jpg','elvalle-bird3.jpg','elvalle-bird4.jpg',
   'elvalle-bridge.jpg','elvalle-church.jpg','elvalle-drums.jpg','elvalle-elmachowaterfall.jpg',
   'elvalle-elmachowaterfall2.jpg','elvalle-elmachowaterfall3.jpg','elvalle-flowermarket.jpg',
   'elvalle-indiadormida.jpg','elvalle-market.JPG','elvalle-panorama.jpg','elvalle-petroglifo.jpg',
   'elvalle-shrine.jpg','elvalle-town.jpg','elvalle-waterfall.jpg'],
}
INLINE_BAN = {'boquete-manmadewaterfall.jpg','boquete-rainbow.png'}
THEME = {
 'boquete-volcanbaru.jpg':'baru volcán volcano summit cumbre peak highest',
 'boquete-bird.jpg':'quetzal wildlife bird fauna nest birding',
 'boquete-market.jpg':'coffee café cafe market finca geisha mercado food cup',
 'boquete-forest.jpg':'pipeline pianista forest cloud bosque nuboso canopy',
 'boquete-losquetzales.JPG':'quetzales sendero trail hike senderismo path',
 'boquete-rafting.jpg':'raft river canyon water rapids adventure',
 'boquete-hills.jpg':'hill highland landscape valley why capital season',
 'boquete-bridge.jpg':'town getting logistic transport bridge llegar puente stay',
 'boquete-river.jpg':'river water waterfall pozos spring río rio thermal',
 'boquete-river2.jpg':'river water waterfall pozos spring río rio thermal lost cascada',
 'boquete-town2.jpg':'town getting stay logistic pueblo life market',
 'boquete-clouds.jpg':'season weather rain cloud condition temporada clima forest',
 'boquete-aerial.jpg':'view panoram overview valley why capital aerial above',
 'boquete-aerial2.jpg':'view panoram overview valley capital aerial above',
 'boquete-people.jpg':'life culture people town community market local',
 'boquete-rocks.jpg':'rock trail canyon gorge river boulder pipeline',
 'elvalle-indiadormida.jpg':'india dormida ridge hike trail sleeping rim',
 'elvalle-elmachowaterfall.jpg':'macho chorro waterfall cascada falls',
 'elvalle-elmachowaterfall2.jpg':'macho chorro waterfall cascada falls',
 'elvalle-elmachowaterfall3.jpg':'macho chorro waterfall cascada falls',
 'elvalle-waterfall.jpg':'waterfall cascada hot spring thermal termal pozos water mud',
 'elvalle-panorama.jpg':'caldera crater cráter view panoram valley overview why',
 'elvalle-bird.jpg':'bird wildlife frog golden fauna rana quetzal',
 'elvalle-bird2.jpg':'bird wildlife fauna birding',
 'elvalle-bird3.jpg':'bird hummingbird wildlife fauna',
 'elvalle-bird4.jpg':'bird wildlife fauna golden',
 'elvalle-market.JPG':'market mercado craft artesan food sunday',
 'elvalle-flowermarket.jpg':'flower flores orchid orquídea market mercado garden plant',
 'elvalle-church.jpg':'church iglesia town pueblo plaza',
 'elvalle-town.jpg':'town pueblo village stay getting life',
 'elvalle-bridge.jpg':'bus getting transport bridge puente llegar',
 'elvalle-petroglifo.jpg':'petroglyph petroglifo history historia piedra pintada rock',
 'elvalle-drums.jpg':'drum culture tambor cultura music tradition',
 'elvalle-shrine.jpg':'shrine culture history altar faith',
}
PREF = {'boquete':['boquete-aerial2.jpg','boquete-clouds.jpg','boquete-river2.jpg','boquete-rocks.jpg',
                   'boquete-people.jpg','boquete-town2.jpg','boquete-aerial.jpg','boquete-river.jpg'],
        'elvalle':['elvalle-panorama.jpg','elvalle-bird2.jpg','elvalle-elmachowaterfall2.jpg',
                   'elvalle-shrine.jpg','elvalle-bird3.jpg','elvalle-market.JPG','elvalle-drums.jpg']}

# CSS injected once per article to ensure <img> fills .imgph + .art-hero-img-full
IMG_CSS = '.art-hero-img-full img,.imgph img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}'

def block_bounds(s, start):
    pos=start; depth=1
    while pos<len(s) and depth>0:
        o=s.find('<div',pos); c=s.find('</div>',pos)
        if c<0: break
        if 0<=o<c: depth+=1; pos=o+4
        else: depth-=1; pos=c+6
    return start,pos

def inline_pick(heading, loc, pool):
    words=set(re.findall(r'[a-záéíóúñ]+', heading.lower()))
    best=None; best_score=-1
    for img in pool:
        kws=set(THEME.get(img,'').split())
        score=len(words & kws)
        if score>best_score:
            best_score=score; best=img
    if best_score>0:
        return best
    for d in PREF[loc]:
        if d in pool: return d
    return pool[0] if pool else None

def process(path):
    es='/es/' in path; lang='es' if es else 'en'
    loc='elvalle' if 'valle' in path else 'boquete'
    fn=path.split('/')[-1]
    t=0 if fn.startswith(('hikes','senderos')) else (1 if fn.startswith(('things','que-hacer')) else 2)
    cap=CAP_ES if es else CAP_EN
    d=D[loc]
    s=open(path,encoding='utf-8').read()
    hero,gal=ALLOC[(loc,t)]

    # ── 0. Inject IMG_CSS once (idempotent) ──────────────────────────────────
    if IMG_CSS not in s:
        s=s.replace('</style>', IMG_CSS+'</style>', 1)

    # ── 0b. Strip previously-inserted inline figures (idempotent) ────────────
    s=re.sub(r'<figure class="fig">.*?</figure>','',s,flags=re.DOTALL)

    # ── Helper: extract H1 text for hero alt ─────────────────────────────────
    h1m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.DOTALL)
    hero_alt=re.sub(r'<[^>]+>','',h1m.group(1)).strip() if h1m else ''

    # ── 1. HERO → <img fetchpriority="high"> ─────────────────────────────────
    hero_webp = webp_of(hero)
    hero_path = D_ROOT + hero_webp
    hw, hh = img_dims(hero_path)
    hero_img_tag = make_img(hero_path, hero_alt, hw, hh, priority=True)
    s=re.sub(
        r'<div class="art-hero-img-full"[^>]*>(?:<img[^>]*>)?</div>',
        f'<div class="art-hero-img-full">{hero_img_tag}</div>',
        s, count=1)

    # ── 2. GALLERY: <div class="imgph photo" style="background-image:...">
    #      → <div class="imgph photo"><img loading=lazy ...></div> ────────────
    m=re.search(r'class="art-gallery-grid">',s)
    if m:
        gs,ge=block_bounds(s,m.end()); grid=s[gs:ge]; idx=[0]
        def rf(fm):
            fig=fm.group(0); k=idx[0]; idx[0]+=1
            if k>=len(gal): return fig
            img_base=gal[k]
            alt_text=cap.get(img_base,'')
            webp_name=webp_of(img_base)
            webp_path=d+webp_name
            iw,ih=img_dims(webp_path)
            itag=make_img(webp_path,alt_text,iw,ih)
            # Replace the whole <div class="imgph photo" ...></div> (with or without bg-image style)
            fig=re.sub(r'<div class="imgph photo"[^>]*>(?:<img[^>]*>)?</div>',
                       f'<div class="imgph photo">{itag}</div>', fig, count=1)
            # Update figcaption
            if alt_text and '<figcaption>' in fig:
                fig=re.sub(r'<figcaption>.*?</figcaption>',f'<figcaption>{alt_text}</figcaption>',fig,flags=re.DOTALL)
            return fig
        grid=re.sub(r'<figure[^>]*>.*?</figure>',rf,grid,flags=re.DOTALL)
        s=s[:gs]+grid+s[ge:]

    # ── 3. BENTO: same replacement inside .home-bento-grid ───────────────────
    m=re.search(r'class="home-bento-grid">',s)
    if m:
        bs,be=block_bounds(s,m.end()); block=s[bs:be]
        trio=BENTO[(loc,t)]
        parts=block.split('<div class="bento-card'); out=[parts[0]]; ci=0
        for chunk in parts[1:]:
            chunk='<div class="bento-card'+chunk
            if ci<len(trio):
                e=trio[ci]; tag,h3,p=e[lang]
                img_base=e['img']
                webp_name=webp_of(img_base)
                webp_path=d+webp_name
                bw,bh=img_dims(webp_path)
                itag=make_img(webp_path,h3,bw,bh)
                chunk=re.sub(r'<div class="imgph photo"[^>]*>(?:<img[^>]*>)?</div>',
                             f'<div class="imgph photo">{itag}</div>', chunk, count=1)
                chunk=re.sub(r'<span class="b-tag">[^<]*</span>',f'<span class="b-tag">{tag}</span>',chunk,count=1)
                chunk=re.sub(r'<h3>.*?</h3>',f'<h3>{h3}</h3>',chunk,count=1,flags=re.DOTALL)
                if '<p>' in chunk:
                    chunk=re.sub(r'<p>.*?</p>',f'<p>{p}</p>',chunk,count=1,flags=re.DOTALL)
                ci+=1
            out.append(chunk)
        s=s[:bs]+''.join(out)+s[be:]

    # ── 4. INLINE figures between sections ───────────────────────────────────
    page_used=set([hero]+gal+[e['img'] for e in BENTO[(loc,t)]])
    pool=[i for i in ALLIMG[loc] if i not in page_used and i not in INLINE_BAN]
    added=0
    for sec in ('s2','s4','s6','s8'):
        mh=re.search(r'<h2 id="'+sec+r'"[^>]*>(.*?)</h2>', s, re.DOTALL)
        if not mh or not pool: continue
        heading=re.sub(r'<[^>]+>','',mh.group(1))
        img_base=inline_pick(heading, loc, pool); pool.remove(img_base)
        alt_text=cap.get(img_base,'')
        webp_name=webp_of(img_base)
        webp_path=d+webp_name
        iw,ih=img_dims(webp_path)
        itag=make_img(webp_path,alt_text,iw,ih)
        caphtml=f'<figcaption><strong>{alt_text}</strong></figcaption>' if alt_text else ''
        fig=f'<figure class="fig"><div class="imgph photo">{itag}</div>{caphtml}</figure>'
        pos=mh.start()
        s=s[:pos]+fig+s[pos:]
        added+=1

    # ── 5. og/twitter/schema image → hero webp (absolute URL) ────────────────
    abs_hero = f'https://panamaspot.com{D_ROOT}{hero_webp}'
    # Replace any absolute panamaspot image URL (old jpg, heic, or webp)
    s=re.sub(r'https://panamaspot\.com/images/[^"\')\s]+', abs_hero, s)

    open(path,'w',encoding='utf-8').write(s)
    print(f"  ✓ {fn:<40} hero={hero_webp:<30} inline+={added}")

FILES=[
 "public/articles/hikes-in-boquete.html","public/articles/things-to-do-in-boquete-panama.html",
 "public/articles/tours-in-boquete-panama.html","public/es/articles/senderos-en-boquete-guia-completa.html",
 "public/es/articles/que-hacer-en-boquete-guia-completa.html","public/es/articles/tours-en-boquete-panama.html",
 "public/articles/hikes-el-valle-de-anton.html","public/articles/things-to-do-el-valle-de-anton.html",
 "public/articles/tours-en-el-valle-de-anton.html","public/es/articles/senderos-el-valle-de-anton.html",
 "public/es/articles/que-hacer-el-valle-de-anton.html","public/es/articles/tours-el-valle-de-anton.html",
]
print("Image pass: heroes→<img fetchpriority=high>, gallery/inline/bento→<img loading=lazy>, WebP…")
for f in FILES: process(f)
print("Done.")
