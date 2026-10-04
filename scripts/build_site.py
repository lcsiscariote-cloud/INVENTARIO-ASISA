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
    photos = [os.path.basename(x) for x in photos if not x.endswith(".gitkeep")] + list(MODELS.get(m["slug"], {}).get("photos", []))
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

TEL = re.sub(r"[^\d+]", "", B.get("phone", ""))
FIN = B.get("financiers", []); T0, T1 = B.get("termMin", 6), B.get("termMax", 24)
FIN_TXT = " y ".join([", ".join(FIN[:-1]), FIN[-1]]) if len(FIN) > 1 else (FIN[0] if FIN else "")
FIN_DISC = "Sujeto a análisis y aprobación de la financiera. El monto autorizado depende de tu historial crediticio. " + (FIN_TXT + " son empresas independientes de " + NAME + "." if FIN else "")
IC = {"wrench": '<path d="M14.7 6.3a4 4 0 0 0-5 5L3 18l3 3 6.7-6.7a4 4 0 0 0 5-5l-2.7 2.7-2.3-.7-.7-2.3z"/>',
      "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/>',
      "shield": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
      "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
      "qr": '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><path d="M14 14h3v3h-3zM20 14v7M14 20h3"/>',
      "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
      "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
      "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
      "moto": '<circle cx="5.5" cy="16" r="3.5"/><circle cx="18.5" cy="16" r="3.5"/><path d="M5.5 16 9 9h5l4.5 7M14 9l-1-3h-3"/>'}
icon = lambda n: f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{IC[n]}</svg>'
SERV = [("wrench", "Reparación de motos", "Diagnóstico y reparación de motocicletas, motonetas y cuatrimotos en nuestro taller."),
        ("gear", "Refacciones", "Venta de refacciones y accesorios para mantener tu unidad en las mejores condiciones."),
        ("shield", "Trabajo con aseguradoras", "Atendemos unidades de aseguradoras: reparación de siniestros y refacciones. Pregunta por tu compañía.")]
def term_bar():
    pts = "".join(f'<li style="left:{(t-T0)/(T1-T0)*100:.0f}%"><i></i><b>{t}</b><span>meses</span></li>' for t in sorted({T0, 12, 18, T1}) if T0 <= t <= T1)
    return f'<div class="terms" aria-label="Plazos de {T0} a {T1} meses"><div class="track"></div><ul>{pts}</ul></div>'

def purl(p, w=None):
    """URL de foto: archivo local (photos/) o URL externa (p. ej. ImageKit, con redimensionado y WebP automáticos)."""
    if p.startswith("http"):
        return p + (("&" if "?" in p else "?") + f"tr=w-{w},f-auto,q-80") if w and "imagekit.io" in p else p
    return "/photos/" + os.path.basename(p)

def visual(m, cls="art"):
    if m["photos"]: return f'<img class="photo" src="{E(purl(m["photos"][0], 600))}" alt="{E(m["brand"]+" "+m["title"])} en {E(CITY)}" loading="lazy">'
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
<nav aria-label="Principal"><a href="/#catalogo">Catálogo</a><a href="/financiamiento/">Financiamiento</a><a href="/servicios/">Taller y refacciones</a><a href="/#visitanos">Ubicación</a></nav>{cta}</div></header>'''
WA_ICO = '<svg class="gi" viewBox="0 0 24 24" aria-hidden="true"><path fill="#fff" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 2a8 8 0 1 1-4.2 14.8l-.4-.2-2.7.7.7-2.6-.2-.4A8 8 0 0 1 12 4z"/><path fill="#fff" d="M8.7 7.6c.3-.5.8-.5 1.1-.1l.8 1.4c.2.4.1.8-.2 1.1l-.5.5c.6 1.2 1.6 2.2 2.8 2.8l.5-.5c.3-.3.7-.4 1.1-.2l1.4.8c.4.3.4.8 0 1.2-.7.9-1.6 1.2-2.5 1-2.9-.8-5-3-5.8-5.8-.2-.9.1-1.8.3-2.2z"/></svg>'
MAP_ICO = '<svg class="gi" viewBox="0 0 24 24" aria-hidden="true"><path fill="#ea4335" d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7z"/><path fill="#fbbc04" d="M12 2a7 7 0 0 0-5.6 2.8L12 11z"/><path fill="#34a853" d="M17.6 4.8A7 7 0 0 1 19 9c0 1.4-.5 3-1.2 4.5L12 11z"/><path fill="#4285f4" d="M5 9c0 1.4.5 3 1.2 4.5L12 11 6.4 4.8A7 7 0 0 0 5 9z"/><circle cx="12" cy="9" r="2.6" fill="#fff"/></svg>'

def dock():
    items = [f'<a class="g-map" href="{E(MAPS)}" target="_blank" rel="noopener" aria-label="Cómo llegar en Google Maps" title="Cómo llegar">{MAP_ICO}<span>Cómo llegar</span></a>',
             (f'<a class="g-wa" href="{E(wa("Hola, quiero información de una moto"))}" rel="noopener" aria-label="Escribir por WhatsApp" title="WhatsApp">{WA_ICO}<span>WhatsApp</span></a>' if wa() else ""),
             (f'<a class="g-tel" href="tel:{TEL}" aria-label="Llamar por teléfono" title="Llamar">{icon("phone")}<span>Llamar</span></a>' if B.get("phone") else "")]
    return '<nav class="gbar" aria-label="Contacto rápido">' + "".join(items) + "</nav>"

def footer():
    contact = "".join(f"<li>{x}</li>" for x in [E(B["address"]) if B["address"] else "", f'<a href="tel:{TEL}">{E(B["phone"])}</a>' if B["phone"] else "", E(B["hours"]) if B["hours"] else ""] if x)
    return f'''<footer class="foot"><div class="wrap fgrid"><div><img src="/logo.svg" alt="{E(NAME)}" width="150" height="38" class="flogo"><p>{E(NAME)} · Motos, cuatrimotos y motonetas en {E(CITY)}</p></div>
<div><h4>Categorías</h4><ul>{"".join(f'<li><a href="/categoria/{CAT_SLUG[c]}/">{E(art.NAMES[c])}</a></li>' for c in CATS)}</ul></div>
<div><h4>Servicios</h4><ul><li><a href="/financiamiento/">Financiamiento</a></li><li><a href="/servicios/">Reparación de motos</a></li><li><a href="/servicios/#refacciones">Refacciones</a></li><li><a href="/servicios/#aseguradoras">Aseguradoras</a></li></ul></div>
<div><h4>Marcas</h4><ul>{"".join(f'<li><a href="/#catalogo" data-brand="{E(b)}">{E(b.title())}</a></li>' for b in BRANDS)}</ul></div>
<div><h4>Contacto</h4><ul>{contact}<li><a href="{E(MAPS)}" target="_blank" rel="noopener">Cómo llegar</a></li></ul></div></div>
<p class="legal wrap">Los modelos mostrados corresponden al inventario actual y pueden variar. Precios en MXN sujetos a cambio sin previo aviso. Imágenes ilustrativas.</p></footer>
{dock()}<script src="/js/site.js" defer></script></body></html>'''

def card(m):
    pr = f'<div class="price"><small>Desde</small> {money(m["pmin"])}</div>' if m["pmin"] else '<div class="price ask">Consultar precio</div>'
    sw = "".join(f'<i title="{E(c)}" style="background:{hexof(c)}"></i>' for c in m["colors"])
    hay = " ".join([m["brand"], m["title"], art.NAMES[m["cat"]], *m["colors"], *map(str, m["years"])]).lower()
    return f'''<a class="card" href="/moto/{m["slug"]}/" data-cat="{m["cat"]}" data-brand="{E(m["brand"])}" data-price="{m["pmin"] or 0}" data-name="{E(m["title"])}" data-q="{E(hay)}">
<div class="stage">{visual(m)}<span class="badge">{E(art.NAMES[m["cat"]])}</span></div>
<div class="cb"><div class="brand">{E(m["brand"])}</div><h3>{E(m["title"])}</h3><div class="sw">{sw}</div>{pr}{f'<span class="fin">Financiamiento {T0}–{T1} meses</span>' if FIN else ""}<span class="more">Ver detalle →</span></div></a>'''

FAQ_PRICE = lambda c: (lambda ps: f'desde {money(min(ps))}' if ps else "")( [m["pmin"] for m in ms if m["cat"] == c and m["pmin"]])
def faqs():
    brands = ", ".join(b.title() for b in BRANDS)
    f = [(f"¿Dónde comprar motos y cuatrimotos en {B['city']}, Guanajuato?",
          f"En {NAME}, en {CITY}. En este sitio puedes consultar el catálogo con modelos, colores y precios, y visitarnos para ver las unidades en piso."),
         ("¿Qué marcas de motos manejan?", f"Actualmente manejamos las marcas {brands}."),
         ("¿Qué tipos de vehículos ofrecen?", "Motocicletas, deportivas, motonetas, cuatrimotos y UTV, motos cross y minimotos, bicicletas y triciclos eléctricos, y motocarros de carga: " + ", ".join(art.NAMES[c] for c in CATS) + ".")]
    if FAQ_PRICE("motoneta"): f.append((f"¿Cuánto cuesta una motoneta en {B['city']}?", f"En nuestro catálogo actual las motonetas van {FAQ_PRICE('motoneta')}. El precio exacto depende del modelo, color y año."))
    if FAQ_PRICE("cuatrimoto"): f.append((f"¿Cuánto cuesta una cuatrimoto en {B['city']}?", f"Las cuatrimotos de nuestro catálogo van {FAQ_PRICE('cuatrimoto')}, según cilindrada y modelo."))
    if FIN: f += [(f"¿Tienen financiamiento para motos en {B['city']}?", f"Sí. Trabajamos con financieras como {FIN_TXT}. Acude a la sucursal y realizamos el análisis para saber cuánto crédito te autorizan según tu historial crediticio. Los plazos van de {T0} a {T1} meses, con abono a capital. {FIN_DISC}"),
        ("¿Con qué empresas de financiamiento trabajan?", f"Con {FIN_TXT}."), (f"¿A cuántos meses puedo pagar mi moto?", f"Los plazos de pago son de {T0} hasta {T1} meses, con abono a capital, sujetos a la aprobación de la financiera.")]
    f += [(f"¿Hacen reparación de motos en {B['city']}?", f"Sí, {NAME} cuenta con servicio de reparación de motos, motonetas y cuatrimotos, además de venta de refacciones."),
          ("¿Trabajan con aseguradoras?", "Sí, trabajamos con compañías aseguradoras en la reparación de unidades y el suministro de refacciones. Consúltanos para confirmar tu aseguradora."),
          ("¿Venden refacciones para motos?", "Sí, manejamos refacciones para motocicletas, motonetas y cuatrimotos. Pregunta por la pieza que necesitas.")]
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

    fin_band = f'''<section class="finband" id="financiamiento"><div class="wrap fgrid2"><div><p class="kicker light">Financiamiento</p><h2>Estrena tu moto a {T0}–{T1} meses</h2>
<p>Financia con <b>{E(FIN_TXT)}</b>. Acude a la sucursal y hacemos el análisis de cuánto crédito te autorizan según tu historial crediticio. Plazos con abono a capital.</p>
<div class="ctas"><a class="btn btn-light" href="/financiamiento/">Cómo funciona</a>{f'<a class="btn btn-red" href="{E(wa("Hola, quiero información de financiamiento"))}" rel="noopener">Pregunta por WhatsApp</a>' if wa() else ""}</div></div>
<div class="fcard">{term_bar()}<div class="pills">{"".join(f"<span>{E(x)}</span>" for x in FIN)}</div><small>{E(FIN_DISC)}</small></div></div></section>''' if FIN else ""
    serv = f'''<section class="wrap sec" id="servicios"><div class="sh"><p class="kicker">Más que una tienda</p><h2>Taller, refacciones y aseguradoras</h2></div>
<div class="servs">{"".join(f'<div class="sv">{icon(i)}<h3>{E(t)}</h3><p>{E(d)}</p></div>' for i, t, d in SERV)}</div><p style="margin-top:18px"><a class="btn btn-light" href="/servicios/">Ver servicios del taller</a></p></section>'''
    d = f'''<main id="main"><section class="hero"><div class="speed"></div><div class="wrap hgrid"><div class="htext">
<p class="eyebrow"><span></span> {E(NAME)} · {E(CITY)}</p>
<h1>Motos, cuatrimotos y motonetas en <em>{E(B["city"])}</em>, Gto.</h1>
<p class="lead">Catálogo de motos con financiamiento a {T0}–{T1} meses, taller de reparación, refacciones y atención a aseguradoras. Visítanos en {E(B["city"])}.</p>
<div class="ctas">{cta}</div>
<ul class="trust"><li>{icon("card")} Financiamiento {T0}–{T1} meses</li><li>{icon("wrench")} Taller y refacciones</li><li>{icon("shield")} Trabajamos con aseguradoras</li></ul>
<ul class="stats"><li><b>{n_models}</b><span>Modelos</span></li><li><b>{len(BRANDS)}</b><span>Marcas</span></li><li><b>{len(CATS)}</b><span>Categorías</span></li></ul></div>
<div class="hart" aria-hidden="true">{hero_art}</div></div></section>
{fin_band}<section class="wrap sec" id="categorias"><div class="sh"><p class="kicker">Explora por tipo</p><h2>¿Qué estás buscando?</h2></div><div class="tiles">{tiles}</div></section>
<section class="band"><div class="wrap vals">
<div><span class="ic">{icon("qr")}</span><h3>Escanea y conoce</h3><p>Cada unidad en piso tiene su código QR: escanéalo y ve modelo, color y ficha técnica al instante.</p></div>
<div><span class="ic">{icon("moto")}</span><h3>{len(BRANDS)} marcas, un solo lugar</h3><p>{E(", ".join(b.title() for b in BRANDS))}.</p></div>
<div><span class="ic">{icon("pin")}</span><h3>Visítanos en {E(B["city"])}</h3><p>Ven a ver las unidades en piso y resuelve tus dudas con nuestro equipo.</p></div></div></section>
<section class="wrap sec" id="catalogo"><div class="sh"><p class="kicker">Catálogo completo</p><h2>Nuestras motos disponibles</h2></div>
<div class="chips" role="group" aria-label="Categoría">{chips}</div><div class="chips" role="group" aria-label="Marca">{bchips}</div>
<div class="tools"><input id="q" type="search" placeholder="Buscar modelo, marca o color…" aria-label="Buscar"><select id="sort" aria-label="Ordenar"><option value="">Ordenar: Destacados</option><option value="asc">Precio: menor a mayor</option><option value="desc">Precio: mayor a menor</option><option value="name">Nombre A–Z</option></select></div>
<p class="count" id="count" aria-live="polite">{n_models} modelos</p><div class="grid" id="grid">{"".join(card(m) for m in ms)}</div><p class="empty" id="empty" hidden>No encontramos modelos con esos filtros.</p></section>
{serv}<section class="wrap sec" id="preguntas"><div class="sh"><p class="kicker">Preguntas frecuentes</p><h2>Lo que más nos preguntan</h2></div>
<div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)}</div></section>
<section class="band dark" id="visitanos"><div class="wrap loc"><div><p class="kicker light">Visítanos</p><h2>{E(NAME)} en {E(CITY)}</h2>
<p>{E(B["address"]) if B["address"] else "Ven a conocer las unidades en piso y resuelve tus dudas con nuestro equipo."}</p>{f'<p><b>Horario:</b> {E(B["hours"])}</p>' if B["hours"] else ""}{f'<p><b>Teléfono:</b> <a href="tel:{TEL}">{E(B["phone"])}</a></p>' if B["phone"] else ""}</div>
<div class="ctas">{f'<a class="btn btn-light" href="tel:{TEL}">Llamar</a>' if B["phone"] else ""}<a class="btn btn-red" href="{E(MAPS)}" target="_blank" rel="noopener">Cómo llegar</a>{f'<a class="btn btn-light" href="{E(wa("Hola, quiero información"))}" rel="noopener">Escribir por WhatsApp</a>' if wa() else ""}</div></div></section></main>'''
    dealer = {"@context": "https://schema.org", "@type": "MotorcycleDealer", "@id": SITE + "/#dealer", "name": NAME, "url": SITE + "/", "logo": SITE + "/logo.svg", "image": SITE + "/og.png",
        "description": f"Venta de motos, cuatrimotos, motonetas y vehículos eléctricos en {CITY}",
        "address": {"@type": "PostalAddress", "addressLocality": B["city"], "addressRegion": B["region"], "addressCountry": B["country"], **({"streetAddress": B.get("streetAddress") or B["address"]} if B["address"] else {}), **({"postalCode": B["postalCode"]} if B.get("postalCode") else {})},
        "areaServed": [{"@type": "City", "name": B["city"]}], "brand": [{"@type": "Brand", "name": b.title()} for b in BRANDS],
        **({"telephone": TEL} if B["phone"] else {}), **({"openingHours": B["hours"]} if B["hours"] else {}), "hasMap": MAPS,
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Servicios", "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "areaServed": B["city"]}} for n in ["Reparación de motocicletas", "Venta de refacciones para motocicletas", "Reparación y refacciones para aseguradoras"] + ([f"Financiamiento de motocicletas con {FIN_TXT}"] if FIN else [])]}}
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
    gallery = f'<div class="stage big" id="stage" data-cat="{m["cat"]}">{visual(m, "art")}</div>' + ("".join(f'<img class="th" src="{E(purl(p, 200))}" alt="" loading="lazy">' for p in m["photos"][1:]))
    related = [r for r in ms if r["cat"] == m["cat"] and r["slug"] != m["slug"]][:4] or [r for r in ms if r["slug"] != m["slug"]][:4]
    price = f'<span id="price">{money(first[2])}</span>' if first[2] else '<span id="price">Consultar precio</span>'
    ctas = (f'<a class="btn btn-red" href="{E(wa(f"Hola, me interesa la {name}"))}" rel="noopener">Cotizar por WhatsApp</a>' if wa() else f'<a class="btn btn-red" href="{E(MAPS)}" target="_blank" rel="noopener">Cómo llegar a la tienda</a>') + (f'<a class="btn btn-light" href="{E(m["url"])}" target="_blank" rel="noopener nofollow">Sitio del fabricante</a>' if m.get("url") else "")
    body = f'''<main id="main"><div class="wrap"><nav class="crumbs" aria-label="Migas de pan"><a href="/">Inicio</a> › <a href="/categoria/{CAT_SLUG[m["cat"]]}/">{E(art.NAMES[m["cat"]])}</a> › <span>{E(name)}</span></nav>
<article class="mgrid" data-slug="{m["slug"]}"><div class="gal">{gallery}</div>
<div class="info"><p class="brand">{E(m["brand"])}</p><h1>{E(m["title"])} <small>en {E(CITY)}</small></h1>
<div class="pricebox"><small>Precio</small><b>{price}</b><span class="note">Sujeto a disponibilidad</span></div>
<div class="staffbar" id="staffbar" hidden><a id="staffLink" href="/staff/">Abrir ficha de inventario (personal) →</a></div>
{f'<div class="fincall">{icon("card")}<div><b>Financia tu {E(m["title"])}</b><span>De {T0} a {T1} meses con {E(FIN_TXT)}. <a href="/financiamiento/">Ver cómo</a></span></div></div>' if FIN else ""}<h2 class="h3">Color y año</h2><div class="opts" role="group" aria-label="Color y año">{opts}</div>
<p class="desc">{E(desc_txt)}</p><div class="ctas">{ctas}</div></div></article>
<section class="spec"><h2>Ficha técnica</h2><table>{"".join(f"<tr><th>{E(k)}</th><td>{E(v)}</td></tr>" for k, v in specs.items())}</table>{"" if m["info"].get("specs") else '<p class="soon">Ficha técnica completa próximamente.</p>'}</section>
<section class="sec"><div class="sh"><h2>También te puede interesar</h2></div><div class="grid">{"".join(card(r) for r in related)}</div></section></div></main>'''
    prod = {"@context": "https://schema.org", "@type": "Product", "name": name, "brand": {"@type": "Brand", "name": m["brand"].title()}, "category": CAT_SING[m["cat"]], "description": desc_txt,
        "url": f'{SITE}/moto/{m["slug"]}/', **({"color": ", ".join(m["colors"])} if m["colors"] else {}),
        **({"image": [p if p.startswith("http") else f'{SITE}{purl(p)}' for p in m["photos"]]} if m["photos"] else {"image": SITE + "/og.png"}),
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


def fin_page():
    steps = [("Elige tu moto", "Revisa el catálogo y escanea el QR en piso para ver modelo, color y precio."), ("Visita la sucursal", "Acude con tu identificación; hacemos contigo el análisis de crédito."),
             ("Análisis de crédito", "Con tu historial crediticio se determina cuánto crédito te autorizan."), (f"Elige tu plazo", f"De {T0} a {T1} meses, con abono a capital, según lo autorizado.")]
    body = f'''<main id="main"><div class="wrap"><nav class="crumbs"><a href="/">Inicio</a> › <span>Financiamiento</span></nav>
<header class="chead"><div><h1>Financiamiento de motos en {E(CITY)}</h1><p>Financia tu moto con <b>{E(FIN_TXT)}</b>, a plazos de {T0} a {T1} meses con abono a capital. El análisis se hace en sucursal según tu historial crediticio.</p>
<div class="ctas"><a class="btn btn-red" href="{E(wa("Hola, quiero información de financiamiento") or MAPS)}" rel="noopener">{"Pregunta por WhatsApp" if wa() else "Cómo llegar a la sucursal"}</a></div></div><div class="fcard">{term_bar()}<div class="pills">{"".join(f"<span>{E(x)}</span>" for x in FIN)}</div></div></header>
<section class="sec"><div class="sh"><h2>Así de fácil</h2></div><ol class="steps">{"".join(f"<li><b>{i+1}</b><h3>{E(t)}</h3><p>{E(d)}</p></li>" for i, (t, d) in enumerate(steps))}</ol></section>
<section class="spec"><h2>Lo que debes saber</h2><ul class="check"><li>Plazos de <b>{T0} a {T1} meses</b> con abono a capital.</li><li>El monto de crédito autorizado depende de tu <b>historial crediticio</b>.</li><li>El análisis se realiza al acudir a la <b>sucursal</b>.</li><li>Financieras: <b>{E(FIN_TXT)}</b>.</li></ul><p class="soon">{E(FIN_DISC)}</p></section>
<section class="sec"><div class="sh"><h2>Motos para financiar</h2></div><div class="grid">{"".join(card(m) for m in sorted([x for x in ms if x["pmin"]], key=lambda x: x["pmin"])[:8])}</div><p style="margin-top:18px"><a class="btn btn-light" href="/#catalogo">Ver todo el catálogo</a></p></section></div></main>'''
    fq = [(q, a) for q, a in faqs() if "financ" in q.lower() or "meses" in q.lower() or "empresas" in q.lower()]
    jl = ld({"@context": "https://schema.org", "@type": "Service", "name": f"Financiamiento de motocicletas en {B['city']}", "serviceType": "Financiamiento", "provider": {"@id": SITE + "/#dealer"}, "areaServed": B["city"],
             "description": f"Financiamiento con {FIN_TXT}, plazos de {T0} a {T1} meses con abono a capital; análisis de crédito en sucursal."}) + ld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]})
    return head(f"Financiamiento de motos en {CITY} | {FIN_TXT} | {NAME}", f"Financia tu moto con {FIN_TXT} a {T0}–{T1} meses con abono a capital. Análisis de crédito en sucursal en {CITY}.", "/financiamiento/", jl) + header() + body + footer()

def serv_page():
    blocks = [("taller", "wrench", "Reparación de motos", f"Servicio de taller para motocicletas, motonetas y cuatrimotos en {CITY}: diagnóstico, mantenimiento y reparación."),
              ("refacciones", "gear", "Refacciones", "Refacciones y accesorios para motocicletas, motonetas y cuatrimotos. Pregunta por la pieza que necesitas."),
              ("aseguradoras", "shield", "Trabajo con aseguradoras", "Trabajamos con compañías aseguradoras en la reparación de unidades y el suministro de refacciones. Consúltanos para confirmar tu aseguradora.")]
    body = f'''<main id="main"><div class="wrap"><nav class="crumbs"><a href="/">Inicio</a> › <span>Taller y refacciones</span></nav>
<header class="chead"><div><h1>Reparación de motos y refacciones en {E(CITY)}</h1><p>En {E(NAME)} no solo vendemos motos: también las reparamos, surtimos refacciones y trabajamos con aseguradoras.</p>
<div class="ctas"><a class="btn btn-red" href="{E(wa("Hola, necesito servicio para mi moto") or MAPS)}" rel="noopener">{"Agenda por WhatsApp" if wa() else "Cómo llegar al taller"}</a></div></div><div class="tart">{art.svg("motocicleta", "#1d4fa3")}</div></header>
<div class="servs big">{"".join(f'<section class="sv" id="{i}">{icon(ic)}<h2>{E(t)}</h2><p>{E(d)}</p></section>' for i, ic, t, d in blocks)}</div>
<section class="sec"><div class="sh"><h2>¿Necesitas cambiar de moto?</h2></div><p>Conoce el catálogo y los planes de <a href="/financiamiento/"><b>financiamiento a {T0}–{T1} meses</b></a>.</p><p><a class="btn btn-light" href="/#catalogo">Ver catálogo</a></p></section></div></main>'''
    jl = ld({"@context": "https://schema.org", "@type": "AutoRepair", "name": f"{NAME} · Taller y refacciones", "url": SITE + "/servicios/", "parentOrganization": {"@id": SITE + "/#dealer"},
             "address": {"@type": "PostalAddress", "addressLocality": B["city"], "addressRegion": B["region"], "addressCountry": B["country"]}, "areaServed": B["city"],
             "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t}} for _, _, t, _ in blocks]})
    return head(f"Reparación de motos y refacciones en {CITY} | {NAME}", f"Taller de reparación de motos, venta de refacciones y trabajo con aseguradoras en {CITY}. {NAME}.", "/servicios/", jl) + header() + body + footer()

def write(path, s):
    full = P(path.lstrip("/")); os.makedirs(os.path.dirname(full), exist_ok=True); open(full, "w").write(s.replace("Gto..", "Gto."))
shutil.rmtree(P("moto"), ignore_errors=True); shutil.rmtree(P("categoria"), ignore_errors=True)
write("index.html", home())
if FIN: write("financiamiento/index.html", fin_page())
write("servicios/index.html", serv_page())
for m in ms: write(f'moto/{m["slug"]}/index.html', model_page(m))
for c in CATS: write(f"categoria/{CAT_SLUG[c]}/index.html", cat_page(c))
today = date.today().isoformat()
urls = ["/", "/servicios/"] + (["/financiamiento/"] if FIN else []) + [f"/categoria/{CAT_SLUG[c]}/" for c in CATS] + [f'/moto/{m["slug"]}/' for m in ms]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
bots = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-User", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot"]
write("robots.txt", "User-agent: *\nAllow: /\nDisallow: /staff/\nDisallow: /data/\n\n" + "".join(f"User-agent: {b}\nAllow: /\nDisallow: /staff/\n\n" for b in bots) + f"Sitemap: {SITE}/sitemap.xml\n")
ll = [f"# {NAME}", "", f"> Tienda de motos, cuatrimotos, motonetas y vehículos eléctricos en {CITY}. Marcas: {', '.join(b.title() for b in BRANDS)}.", ""]
if B["address"]: ll.append(f"Dirección: {B['address']}")
if B["phone"]: ll.append(f"Teléfono: {B['phone']}")
ll += [f"Sitio: {SITE}/", ""]
ll += ["## Servicios", "", f"- Reparación de motos, motonetas y cuatrimotos: {SITE}/servicios/", "- Venta de refacciones: " + SITE + "/servicios/#refacciones", "- Trabajo con aseguradoras (reparación y refacciones): " + SITE + "/servicios/#aseguradoras"]
if FIN: ll += [f"- Financiamiento con {FIN_TXT}, plazos de {T0} a {T1} meses con abono a capital; el análisis de crédito se hace en sucursal según historial crediticio: {SITE}/financiamiento/"]
ll += [""]
for c in CATS:
    ll += [f"## {art.NAMES[c]}", ""] + [f'- [{m["brand"].title()} {m["title"]}]({SITE}/moto/{m["slug"]}/)' + (f' — desde {money(m["pmin"])}' if m["pmin"] else "") + (f'; colores: {", ".join(x.lower() for x in m["colors"])}' if m["colors"] else "") for m in ms if m["cat"] == c] + [""]
write("llms.txt", "\n".join(ll))
print(len(ms), "modelos;", len(CATS), "categorías;", len(urls), "URLs")
