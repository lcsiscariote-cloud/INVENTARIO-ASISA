"""Genera el sitio público (HTML estático, SEO + datos estructurados) desde data/*.json.
Uso: python3 scripts/build_site.py   (después de scripts/build_data.py si cambió el Excel)"""
import json, os, re, glob, html, shutil
from datetime import date
import art
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
B = json.load(open(P("data", "business.json")))
DB = json.load(open(P("data", "inventory.json")))
MODELS = json.load(open(P("data", "models.json")))
E = lambda s: html.escape(str(s if s is not None else ""), quote=True)
SITE = B["siteUrl"].rstrip("/")
NAME, CITY = B["name"], f'{B["city"]}, Gto.'
HEX = {"ROJO":"#d92635","AZUL":"#1f5fbf","NEGRO":"#22272d","BLANCO":"#eef1f4","VERDE":"#2e9a4d","NARANJA":"#f28c1b","AMARILLO":"#f4c20d","ROSA":"#ee7fb0","GRIS":"#8a9099","AZUL CIELO":"#6cc0ee","HEPOLLEN":"#c9b458"}
def hexof(c):
    c = (c or "").upper()
    return HEX.get(c) or next((v for k, v in HEX.items() if k in c), "#8a9099")
money = lambda n: "$" + f"{int(n):,}" + " MXN"
def nice(n):
    n = re.sub(r"^\d{4}\s+", "", n).replace("NARANAJA", "NARANJA")
    return n
by_model = {}
for u in DB["units"]: by_model.setdefault(u["model"], []).append(u)
CAT_SING = {"deportiva":"Motocicleta deportiva","motocicleta":"Motocicleta","motoneta":"Motoneta","cuatrimoto":"Cuatrimoto / vehículo todo terreno","cross":"Moto cross o minimoto","electrico":"Vehículo eléctrico","carga":"Motocarro / vehículo de carga"}
CAT_SLUG = {"deportiva":"deportivas","motocicleta":"motocicletas","motoneta":"motonetas","cuatrimoto":"cuatrimotos","cross":"cross-y-minimotos","electrico":"electricos","carga":"motocarros-y-carga"}
CAT_BLURB = {
 "deportiva":"Motos deportivas de carenado completo para ciudad y carretera.",
 "motocicleta":"Motocicletas de trabajo, choppers y uso diario.",
 "motoneta":"Motonetas automáticas, prácticas para moverte por la ciudad.",
 "cuatrimoto":"Cuatrimotos, UTV y karts para trabajo, campo y diversión.",
 "cross":"Motos cross, minimotos y mini pistas para todas las edades.",
 "electrico":"Bicicletas y triciclos eléctricos para moverte sin gasolina.",
 "carga":"Motocarros y vehículos de carga para tu negocio."}
ms = []
for m in DB["models"]:
    us = by_model.get(m["slug"], [])
    if not us: continue
    prices = [u["price"] for u in us if u["price"]]
    cat = art.categorize(m["brand"], m["name"])
    photos = sorted(glob.glob(P("photos", m["slug"] + ".*")) + glob.glob(P("photos", m["slug"] + "-*.*")))
    photos = [os.path.basename(x) for x in photos if not x.endswith(".gitkeep")] + [os.path.basename(p) for p in MODELS.get(m["slug"], {}).get("photos", [])]
    opts = {}
    for u in us: opts.setdefault((u["color"], u["year"], u["price"]), []).append(u["id"])
    ms.append(dict(m, title=nice(m["name"]), cat=cat, pmin=min(prices) if prices else None, pmax=max(prices) if prices else None,
        colors=sorted({u["color"] for u in us if u["color"]}), years=sorted({u["year"] for u in us if u["year"]}, reverse=True),
        photos=photos, opts=opts, info=MODELS.get(m["slug"], {})))
ms.sort(key=lambda m: (m["brand"], m["title"]))
BRANDS = sorted({m["brand"] for m in ms}); CATS = [c for c in art.NAMES if any(m["cat"] == c for m in ms)]
cnt = lambda f: sum(1 for m in ms if f(m))
def wa(text=""):
    n = re.sub(r"\D", "", B.get("whatsapp", ""))
    return f"https://wa.me/{n}?text=" + re.sub(r"\s", "%20", text) if n else ""
MAPS = B.get("mapsUrl") or "https://www.google.com/maps/search/?api=1&query=" + re.sub(r"\s", "+", f'{NAME} {B["city"]} {B["region"]}')

def visual(m, cls="art"):
    if m["photos"]: return f'<img class="photo" src="/photos/{E(m["photos"][0])}" alt="{E(m["brand"]+" "+m["title"])} en {E(CITY)}" loading="lazy">'
    return art.svg(m["cat"], hexof(m["colors"][0] if m["colors"] else ""), cls)

def head(title, desc, path, extra="", og=True, robots="index,follow"):
    url = SITE + path; desc = desc.replace("Gto..", "Gto."); title = title.replace("Gto..", "Gto.")
    return f'''<!doctype html>
<html lang="es-MX"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><meta name="robots" content="{robots}">
<link rel="canonical" href="{E(url)}"><meta name="theme-color" content="#0b1b3b"><link rel="icon" href="/logo.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:locale" content="es_MX"><meta property="og:site_name" content="{E(NAME)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{E(url)}">
<meta property="og:image" content="{SITE}/og.png"><meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="MX-GUA"><meta name="geo.placename" content="{E(B["city"])}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,700;0,800;1,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/site.css">{extra}</head><body>'''
def ld(o): return '<script type="application/ld+json">' + json.dumps(o, ensure_ascii=False).replace("</", "<\\/") + "</script>"

def header():
    cta = f'<a class="btn btn-red sm" href="{E(wa("Hola, quiero información de una moto"))}" rel="noopener">WhatsApp</a>' if wa() else f'<a class="btn btn-red sm" href="{E(MAPS)}" rel="noopener" target="_blank">Cómo llegar</a>'
    return f'''<a class="skip" href="#main">Saltar al contenido</a>
<header class="top"><div class="wrap bar"><a href="/" class="logo" aria-label="{E(NAME)} - Inicio"><img src="/logo.svg" alt="{E(NAME)}" width="150" height="38"></a>
<nav aria-label="Principal"><a href="/#catalogo">Catálogo</a><a href="/#categorias">Categorías</a><a href="/#preguntas">Preguntas</a><a href="/#visitanos">Ubicación</a></nav>{cta}</div></header>'''
def footer():
    contact = "".join(f"<li>{x}</li>" for x in [E(B["address"]) if B["address"] else "", f'<a href="tel:{E(B["phone"])}">{E(B["phone"])}</a>' if B["phone"] else "", E(B["hours"]) if B["hours"] else ""] if x)
    return f'''<footer class="foot"><div class="wrap fgrid"><div><img src="/logo.svg" alt="{E(NAME)}" width="150" height="38" class="flogo"><p>{E(NAME)} · Motos, cuatrimotos y motonetas en {E(CITY)}</p></div>
<div><h4>Categorías</h4><ul>{"".join(f'<li><a href="/categoria/{CAT_SLUG[c]}/">{E(art.NAMES[c])}</a></li>' for c in CATS)}</ul></div>
<div><h4>Marcas</h4><ul>{"".join(f'<li><a href="/#catalogo" data-brand="{E(b)}">{E(b.title())}</a></li>' for b in BRANDS)}</ul></div>
<div><h4>Contacto</h4><ul>{contact}<li><a href="{E(MAPS)}" target="_blank" rel="noopener">Cómo llegar</a></li></ul></div></div>
<p class="legal wrap">Los modelos mostrados corresponden al inventario actual y pueden variar. Precios en MXN sujetos a cambio sin previo aviso. Imágenes ilustrativas.</p></footer>
<script src="/js/site.js" defer></script></body></html>'''

def card(m):
    pr = f'<div class="price"><small>Desde</small> {money(m["pmin"])}</div>' if m["pmin"] else '<div class="price ask">Consultar precio</div>'
    sw = "".join(f'<i title="{E(c)}" style="background:{hexof(c)}"></i>' for c in m["colors"])
    hay = " ".join([m["brand"], m["title"], art.NAMES[m["cat"]], *m["colors"], *map(str, m["years"])]).lower()
    return f'''<a class="card" href="/moto/{m["slug"]}/" data-cat="{m["cat"]}" data-brand="{E(m["brand"])}" data-price="{m["pmin"] or 0}" data-name="{E(m["title"])}" data-q="{E(hay)}">
<div class="stage">{visual(m)}<span class="badge">{E(art.NAMES[m["cat"]])}</span></div>
<div class="cb"><div class="brand">{E(m["brand"])}</div><h3>{E(m["title"])}</h3><div class="sw">{sw}</div>{pr}<span class="more">Ver detalle →</span></div></a>'''

FAQ_PRICE = lambda c: (lambda ps: f'desde {money(min(ps))}' if ps else "")( [m["pmin"] for m in ms if m["cat"] == c and m["pmin"]])
def faqs():
    brands = ", ".join(b.title() for b in BRANDS)
    f = [(f"¿Dónde comprar motos y cuatrimotos en {B['city']}, Guanajuato?",
          f"En {NAME}, en {CITY}. En este sitio puedes consultar el catálogo con modelos, colores y precios, y visitarnos para ver las unidades en piso."),
         ("¿Qué marcas de motos manejan?", f"Actualmente manejamos las marcas {brands}."),
         ("¿Qué tipos de vehículos ofrecen?", "Motocicletas, deportivas, motonetas, cuatrimotos y UTV, motos cross y minimotos, bicicletas y triciclos eléctricos, y motocarros de carga: " + ", ".join(art.NAMES[c] for c in CATS) + ".")]
    if FAQ_PRICE("motoneta"): f.append((f"¿Cuánto cuesta una motoneta en {B['city']}?", f"En nuestro catálogo actual las motonetas van {FAQ_PRICE('motoneta')}. El precio exacto depende del modelo, color y año."))
    if FAQ_PRICE("cuatrimoto"): f.append((f"¿Cuánto cuesta una cuatrimoto en {B['city']}?", f"Las cuatrimotos de nuestro catálogo van {FAQ_PRICE('cuatrimoto')}, según cilindrada y modelo."))
    f.append(("¿Cómo sé si un modelo está disponible?", "Los modelos del catálogo corresponden a nuestro inventario actual. Te recomendamos confirmar disponibilidad de color y año antes de visitarnos."))
    return f

def home():
    n_models, n_units = len(ms), len(DB["units"])
    chips = '<button class="chip on" data-f="cat" data-v="">Todas</button>' + "".join(f'<button class="chip" data-f="cat" data-v="{c}">{E(art.NAMES[c])} <small>{cnt(lambda m: m["cat"] == c)}</small></button>' for c in CATS)
    bchips = '<button class="chip on" data-f="brand" data-v="">Todas las marcas</button>' + "".join(f'<button class="chip" data-f="brand" data-v="{E(b)}">{E(b.title())} <small>{cnt(lambda m: m["brand"] == b)}</small></button>' for b in BRANDS)
    tiles = "".join(f'<a class="tile" href="/categoria/{CAT_SLUG[c]}/"><div class="tart">{art.svg(c, ["#e31e24","#1d4fa3"][i % 2])}</div><h3>{E(art.NAMES[c])}</h3><p>{cnt(lambda m: m["cat"] == c)} modelos</p></a>' for i, c in enumerate(CATS))
    show = [("deportiva", "#f2f5f9"), ("cuatrimoto", "#f4c20d"), ("motoneta", "#2a6ad4"), ("cross", "#f2f5f9")]
    hero_art = "".join(f'<div class="slide" style="animation-delay:{-2-i*5}s">{art.svg(c, col)}</div>' for i, (c, col) in enumerate(show) if c in CATS)
    cta = (f'<a class="btn btn-red" href="{E(wa("Hola, quiero información de una moto"))}" rel="noopener">Cotizar por WhatsApp</a>' if wa() else "") + '<a class="btn btn-light" href="#catalogo">Ver catálogo</a>'
    faq = faqs()
    d = f'''<main id="main"><section class="hero"><div class="speed"></div><div class="wrap hgrid"><div class="htext">
<p class="eyebrow"><span></span> {E(NAME)} · {E(CITY)}</p>
<h1>Motos, cuatrimotos y motonetas en <em>{E(B["city"])}</em>, Gto.</h1>
<p class="lead">Explora nuestro catálogo, compara modelos y colores, y encuentra la moto ideal para trabajar, rodar o divertirte. Visítanos y pruébala.</p>
<div class="ctas">{cta}</div>
<ul class="stats"><li><b>{n_models}</b><span>Modelos</span></li><li><b>{len(BRANDS)}</b><span>Marcas</span></li><li><b>{len(CATS)}</b><span>Categorías</span></li></ul></div>
<div class="hart" aria-hidden="true">{hero_art}</div></div></section>
<section class="wrap sec" id="categorias"><div class="sh"><p class="kicker">Explora por tipo</p><h2>¿Qué estás buscando?</h2></div><div class="tiles">{tiles}</div></section>
<section class="band"><div class="wrap vals">
<div><span class="ic">📱</span><h3>Escanea y conoce</h3><p>Cada unidad en piso tiene su código QR: escanéalo y ve modelo, color y ficha técnica al instante.</p></div>
<div><span class="ic">🏍️</span><h3>{len(BRANDS)} marcas, un solo lugar</h3><p>{E(", ".join(b.title() for b in BRANDS))}.</p></div>
<div><span class="ic">📍</span><h3>Visítanos en {E(B["city"])}</h3><p>Ven a ver las unidades en piso y resuelve tus dudas con nuestro equipo.</p></div></div></section>
<section class="wrap sec" id="catalogo"><div class="sh"><p class="kicker">Catálogo completo</p><h2>Nuestras motos disponibles</h2></div>
<div class="chips" role="group" aria-label="Categoría">{chips}</div><div class="chips" role="group" aria-label="Marca">{bchips}</div>
<div class="tools"><input id="q" type="search" placeholder="Buscar modelo, marca o color…" aria-label="Buscar"><select id="sort" aria-label="Ordenar"><option value="">Ordenar: Destacados</option><option value="asc">Precio: menor a mayor</option><option value="desc">Precio: mayor a menor</option><option value="name">Nombre A–Z</option></select></div>
<p class="count" id="count" aria-live="polite">{n_models} modelos</p><div class="grid" id="grid">{"".join(card(m) for m in ms)}</div><p class="empty" id="empty" hidden>No encontramos modelos con esos filtros.</p></section>
<section class="wrap sec" id="preguntas"><div class="sh"><p class="kicker">Preguntas frecuentes</p><h2>Lo que más nos preguntan</h2></div>
<div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}</div></section>
<section class="band dark" id="visitanos"><div class="wrap loc"><div><p class="kicker light">Visítanos</p><h2>{E(NAME)} en {E(CITY)}</h2>
<p>{E(B["address"]) if B["address"] else "Ven a conocer las unidades en piso y resuelve tus dudas con nuestro equipo."}</p>{f'<p><b>Horario:</b> {E(B["hours"])}</p>' if B["hours"] else ""}{f'<p><b>Teléfono:</b> <a href="tel:{E(B["phone"])}">{E(B["phone"])}</a></p>' if B["phone"] else ""}</div>
<div class="ctas"><a class="btn btn-red" href="{E(MAPS)}" target="_blank" rel="noopener">Cómo llegar</a>{f'<a class="btn btn-light" href="{E(wa("Hola, quiero información"))}" rel="noopener">Escribir por WhatsApp</a>' if wa() else ""}</div></div></section></main>'''
    dealer = {"@context": "https://schema.org", "@type": "MotorcycleDealer", "@id": SITE + "/#dealer", "name": NAME, "url": SITE + "/", "logo": SITE + "/logo.svg", "image": SITE + "/og.png",
        "description": f"Venta de motos, cuatrimotos, motonetas y vehículos eléctricos en {CITY}",
        "address": {"@type": "PostalAddress", "addressLocality": B["city"], "addressRegion": B["region"], "addressCountry": B["country"], **({"streetAddress": B["address"]} if B["address"] else {})},
        "areaServed": [{"@type": "City", "name": B["city"]}], "brand": [{"@type": "Brand", "name": b.title()} for b in BRANDS],
        **({"telephone": B["phone"]} if B["phone"] else {}), **({"openingHours": B["hours"]} if B["hours"] else {}), "hasMap": MAPS}
    items = {"@context": "https://schema.org", "@type": "ItemList", "name": f"Catálogo de motos {NAME}", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f'{SITE}/moto/{m["slug"]}/', "name": f'{m["brand"].title()} {m["title"]}'} for i, m in enumerate(ms)]}
    fq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    title = f"Motos, cuatrimotos y motonetas en {CITY} | {NAME}"
    desc = f"Catálogo de {n_models} modelos de motos, cuatrimotos, motonetas y eléctricos en {CITY}. Marcas {', '.join(b.title() for b in BRANDS)}. Precios, colores y fotos."
    return head(title, desc, "/", ld(dealer) + ld(items) + ld(fq)) + header() + d + footer()

def model_page(m):
    name = f'{m["brand"].title()} {m["title"]}'
    opts = "".join(f'<button class="opt{" on" if i == 0 else ""}" data-hex="{hexof(c)}" data-year="{y or ""}" data-price="{p or ""}" data-ids="{E(",".join(ids))}" data-color="{E(c)}"><i style="background:{hexof(c)}"></i>{E(c or "—")}{f" · {y}" if y else ""}</button>'
                   for i, ((c, y, p), ids) in enumerate(m["opts"].items()))
    first = next(iter(m["opts"]))
    specs = {"Marca": m["brand"].title(), "Tipo": CAT_SING[m["cat"]], "Colores": ", ".join(c.title() for c in m["colors"]) or "Consultar", "Año modelo": ", ".join(map(str, m["years"])) or "Consultar", **m["info"].get("specs", {})}
    desc_txt = m["info"].get("description") or f'{name} es {("una " if m["cat"] in ("motocicleta","deportiva","motoneta","cuatrimoto") else "un ")}{CAT_SING[m["cat"]].lower()} disponible en {NAME}, {CITY}'.rstrip(".") + "." + (f' Colores: {", ".join(c.lower() for c in m["colors"])}.' if m["colors"] else "") + (f' Precio desde {money(m["pmin"])}.' if m["pmin"] else "")
    gallery = f'<div class="stage big" id="stage" data-cat="{m["cat"]}">{visual(m, "art")}</div>' + ("".join(f'<img class="th" src="/photos/{E(p)}" alt="" loading="lazy">' for p in m["photos"][1:]))
    related = [r for r in ms if r["cat"] == m["cat"] and r["slug"] != m["slug"]][:4] or [r for r in ms if r["slug"] != m["slug"]][:4]
    price = f'<span id="price">{money(first[2])}</span>' if first[2] else '<span id="price">Consultar precio</span>'
    ctas = (f'<a class="btn btn-red" href="{E(wa(f"Hola, me interesa la {name}"))}" rel="noopener">Cotizar por WhatsApp</a>' if wa() else f'<a class="btn btn-red" href="{E(MAPS)}" target="_blank" rel="noopener">Cómo llegar a la tienda</a>') + (f'<a class="btn btn-light" href="{E(m["url"])}" target="_blank" rel="noopener nofollow">Sitio del fabricante</a>' if m.get("url") else "")
    body = f'''<main id="main"><div class="wrap"><nav class="crumbs" aria-label="Migas de pan"><a href="/">Inicio</a> › <a href="/categoria/{CAT_SLUG[m["cat"]]}/">{E(art.NAMES[m["cat"]])}</a> › <span>{E(name)}</span></nav>
<article class="mgrid" data-slug="{m["slug"]}"><div class="gal">{gallery}</div>
<div class="info"><p class="brand">{E(m["brand"])}</p><h1>{E(m["title"])} <small>en {E(CITY)}</small></h1>
<div class="pricebox"><small>Precio</small><b>{price}</b><span class="note">Sujeto a disponibilidad</span></div>
<div class="staffbar" id="staffbar" hidden><a id="staffLink" href="/staff/">Abrir ficha de inventario (personal) →</a></div>
<h2 class="h3">Color y año</h2><div class="opts" role="group" aria-label="Color y año">{opts}</div>
<p class="desc">{E(desc_txt)}</p><div class="ctas">{ctas}</div></div></article>
<section class="spec"><h2>Ficha técnica</h2><table>{"".join(f"<tr><th>{E(k)}</th><td>{E(v)}</td></tr>" for k, v in specs.items())}</table>{"" if m["info"].get("specs") else '<p class="soon">Ficha técnica completa próximamente.</p>'}</section>
<section class="sec"><div class="sh"><h2>También te puede interesar</h2></div><div class="grid">{"".join(card(r) for r in related)}</div></section></div></main>'''
    prod = {"@context": "https://schema.org", "@type": "Product", "name": name, "brand": {"@type": "Brand", "name": m["brand"].title()}, "category": CAT_SING[m["cat"]], "description": desc_txt,
        "url": f'{SITE}/moto/{m["slug"]}/', **({"color": ", ".join(m["colors"])} if m["colors"] else {}),
        **({"image": [f'{SITE}/photos/{p}' for p in m["photos"]]} if m["photos"] else {"image": SITE + "/og.png"}),
        **({"offers": {"@type": "AggregateOffer", "priceCurrency": "MXN", "lowPrice": m["pmin"], "highPrice": m["pmax"], "offerCount": len(m["opts"]), "availability": "https://schema.org/InStock",
            "seller": {"@id": SITE + "/#dealer"}}} if m["pmin"] else {})}
    bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate([("Inicio", SITE + "/"), (art.NAMES[m["cat"]], f'{SITE}/categoria/{CAT_SLUG[m["cat"]]}/'), (name, f'{SITE}/moto/{m["slug"]}/')])]}
    t = f'{name} en {CITY} | Precio y colores | {NAME}'
    d = f'{name}: {CAT_SING[m["cat"]].lower()} en {CITY}.' + (f' Desde {money(m["pmin"])}.' if m["pmin"] else "") + (f' Colores: {", ".join(c.lower() for c in m["colors"])}.' if m["colors"] else "") + f' Cotiza en {NAME}.'
    return head(t, d[:300], f'/moto/{m["slug"]}/', ld(prod) + ld(bc)) + header() + body + footer()

def cat_page(c):
    lst = [m for m in ms if m["cat"] == c]; pr = [m["pmin"] for m in lst if m["pmin"]]
    body = f'''<main id="main"><div class="wrap"><nav class="crumbs"><a href="/">Inicio</a> › <span>{E(art.NAMES[c])}</span></nav>
<header class="chead"><div><h1>{E(art.NAMES[c])} en {E(CITY)}</h1><p>{E(CAT_BLURB[c])} {len(lst)} modelos disponibles{f", desde {money(min(pr))}" if pr else ""}.</p></div><div class="tart">{art.svg(c, "#e31e24")}</div></header>
<div class="grid">{"".join(card(m) for m in lst)}</div></div></main>'''
    items = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f'{SITE}/moto/{m["slug"]}/', "name": f'{m["brand"].title()} {m["title"]}'} for i, m in enumerate(lst)]}
    t = f'{art.NAMES[c]} en {CITY} | Modelos y precios | {NAME}'
    return head(t, f'{art.NAMES[c]} en {CITY}: {len(lst)} modelos{f", desde {money(min(pr))}" if pr else ""}. {CAT_BLURB[c]}', f"/categoria/{CAT_SLUG[c]}/", ld(items)) + header() + body + footer()

def write(path, s):
    full = P(path.lstrip("/")); os.makedirs(os.path.dirname(full), exist_ok=True); open(full, "w").write(s)
shutil.rmtree(P("moto"), ignore_errors=True); shutil.rmtree(P("categoria"), ignore_errors=True)
write("index.html", home())
for m in ms: write(f'moto/{m["slug"]}/index.html', model_page(m))
for c in CATS: write(f"categoria/{CAT_SLUG[c]}/index.html", cat_page(c))
today = date.today().isoformat()
urls = ["/"] + [f"/categoria/{CAT_SLUG[c]}/" for c in CATS] + [f'/moto/{m["slug"]}/' for m in ms]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
bots = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot"]
write("robots.txt", "User-agent: *\nAllow: /\nDisallow: /staff/\nDisallow: /data/\n\n" + "".join(f"User-agent: {b}\nAllow: /\nDisallow: /staff/\n\n" for b in bots) + f"Sitemap: {SITE}/sitemap.xml\n")
ll = [f"# {NAME}", "", f"> Tienda de motos, cuatrimotos, motonetas y vehículos eléctricos en {CITY}. Marcas: {', '.join(b.title() for b in BRANDS)}.", ""]
if B["address"]: ll.append(f"Dirección: {B['address']}")
if B["phone"]: ll.append(f"Teléfono: {B['phone']}")
ll += [f"Sitio: {SITE}/", ""]
for c in CATS:
    ll += [f"## {art.NAMES[c]}", ""] + [f'- [{m["brand"].title()} {m["title"]}]({SITE}/moto/{m["slug"]}/)' + (f' — desde {money(m["pmin"])}' if m["pmin"] else "") + (f'; colores: {", ".join(x.lower() for x in m["colors"])}' if m["colors"] else "") for m in ms if m["cat"] == c] + [""]
write("llms.txt", "\n".join(ll))
print(len(ms), "modelos;", len(CATS), "categorías;", len(urls), "URLs")
