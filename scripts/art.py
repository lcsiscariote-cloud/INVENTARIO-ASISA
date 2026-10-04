"""Ilustraciones vectoriales por categoría. El color de la carrocería se pasa como {c}."""
D, M, L = "#1b2026", "#3a434c", "#c9d0d7"

def wheel(cx, cy, r, knob=False):
    t = "".join(f'<rect x="{cx-3}" y="{cy-r-3}" width="6" height="8" rx="2" fill="{D}" transform="rotate({a} {cx} {cy})"/>' for a in range(0, 360, 22)) if knob else ""
    return (f'<g>{t}<circle cx="{cx}" cy="{cy}" r="{r}" fill="{D}"/><circle cx="{cx}" cy="{cy}" r="{r*0.64:.0f}" fill="{L}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.52:.0f}" fill="#8e98a3"/><circle cx="{cx}" cy="{cy}" r="{r*0.2:.0f}" fill="{D}"/>'
            f'<g stroke="{L}" stroke-width="3">' + "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx+r*0.5:.0f}" y2="{cy}" transform="rotate({a} {cx} {cy})"/>' for a in range(0, 360, 60)) + '</g></g>')

def gloss(d): return f'<path d="{d}" fill="#fff" opacity=".22"/>'

ART = {}
ART["deportiva"] = wheel(92,168,44)+wheel(312,168,44)+f'''
<line x1="296" y1="100" x2="312" y2="168" stroke="#9aa3ad" stroke-width="8" stroke-linecap="round"/>
<path d="M92 168 L210 150" stroke="{M}" stroke-width="10" stroke-linecap="round"/>
<rect x="150" y="116" width="78" height="44" rx="8" fill="{M}"/><path d="M140 160 C110 168 80 166 56 160" stroke="#9aa3ad" stroke-width="9" fill="none" stroke-linecap="round"/>
<path d="M46 122 C62 100 112 94 150 90 L206 84 C226 62 266 52 296 64 L340 96 C346 103 340 110 330 110 L282 110 C262 114 248 134 230 152 L122 152 C78 152 50 142 46 122Z" fill="{{c}}"/>
{gloss("M70 112 C100 100 140 98 180 94 L200 90 C150 100 100 106 70 112Z")}
<path d="M268 62 L298 46 L304 70Z" fill="#dfe8f0" opacity=".85"/><path d="M104 100 C130 94 170 92 204 88 L208 102 L112 110Z" fill="{D}"/>
<ellipse cx="326" cy="95" rx="9" ry="5" fill="#fff"/><path d="M282 60 L296 52" stroke="{D}" stroke-width="6" stroke-linecap="round"/>'''

ART["motocicleta"] = wheel(92,168,42)+wheel(312,168,42)+f'''
<path d="M296 98 L312 168" stroke="#9aa3ad" stroke-width="8" stroke-linecap="round"/><path d="M92 168 L196 150" stroke="{M}" stroke-width="10" stroke-linecap="round"/>
<rect x="148" y="112" width="82" height="48" rx="10" fill="{M}"/><path d="M150 156 C110 170 80 168 54 160" stroke="#9aa3ad" stroke-width="10" fill="none" stroke-linecap="round"/>
<path d="M170 96 C190 70 240 70 262 92 L250 112 L168 112Z" fill="{{c}}"/>{gloss("M185 88 C205 76 232 76 248 88 C228 84 205 86 185 94Z")}
<path d="M84 104 C110 96 156 96 182 104 L176 116 L90 118Z" fill="{D}"/>
<path d="M258 94 L296 98 M280 66 L296 62 L300 98" stroke="{D}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<ellipse cx="310" cy="96" rx="12" ry="14" fill="#fff"/><ellipse cx="310" cy="96" rx="12" ry="14" fill="none" stroke="{D}" stroke-width="4"/>
<path d="M300 126 L330 126 L330 140 L304 140Z" fill="{{c}}"/>'''

ART["motoneta"] = wheel(104,174,34)+wheel(300,174,34)+f'''
<path d="M300 174 L286 70" stroke="#9aa3ad" stroke-width="8" stroke-linecap="round"/>
<path d="M60 112 C76 90 140 88 176 96 L186 150 L218 168 L244 160 L246 108 C250 80 270 62 296 66 L330 74 C346 82 346 100 338 118 L318 164 L290 166 L256 188 L130 188 C100 190 76 160 60 112Z" fill="{{c}}"/>
{gloss("M70 104 C100 92 140 92 170 98 C130 96 96 100 70 112Z")}
<path d="M82 86 C110 78 160 80 190 86 L194 100 L84 104Z" fill="{D}"/><rect x="190" y="150" width="62" height="14" rx="6" fill="{M}"/>
<path d="M272 62 L300 50 L306 70Z" fill="#dfe8f0" opacity=".85"/><path d="M286 56 L304 48" stroke="{D}" stroke-width="7" stroke-linecap="round"/>
<ellipse cx="338" cy="92" rx="8" ry="11" fill="#fff"/><rect x="60" y="112" width="26" height="12" rx="5" fill="#d33"/>'''

ART["cuatrimoto"] = wheel(86,168,46,True)+wheel(318,168,46,True)+f'''
<path d="M86 168 L318 168" stroke="{M}" stroke-width="12" stroke-linecap="round"/>
<path d="M44 118 C60 96 120 96 150 104 L250 104 C272 100 292 90 330 100 L350 126 C340 150 300 150 260 146 L96 150 C58 150 44 140 44 118Z" fill="{{c}}"/>
{gloss("M60 112 C90 102 130 102 170 108 C130 108 90 110 60 118Z")}
<rect x="104" y="80" width="116" height="26" rx="12" fill="{D}"/><rect x="146" y="120" width="86" height="34" rx="8" fill="{M}"/>
<path d="M262 96 L280 54 M246 54 L296 50" stroke="{D}" stroke-width="8" fill="none" stroke-linecap="round"/>
<path d="M300 100 C320 90 344 98 352 112 L330 116Z" fill="{{c}}"/><ellipse cx="344" cy="108" rx="9" ry="6" fill="#fff"/>'''

ART["cross"] = wheel(86,166,48,True)+wheel(314,166,48,True)+f'''
<path d="M300 70 L316 166" stroke="#9aa3ad" stroke-width="9" stroke-linecap="round"/><path d="M86 166 L196 150" stroke="{M}" stroke-width="10" stroke-linecap="round"/>
<rect x="156" y="118" width="70" height="40" rx="8" fill="{M}"/>
<path d="M280 100 C290 60 320 48 346 58 C340 64 322 70 310 98Z" fill="{{c}}"/>
<path d="M60 96 C90 86 150 92 200 96 L250 70 C262 66 276 74 280 88 L266 124 L196 126 L120 114 C80 112 60 108 60 96Z" fill="{{c}}"/>
{gloss("M70 94 C100 88 140 92 180 96 C130 94 100 96 70 100Z")}
<path d="M74 88 C110 80 170 84 224 90 L228 100 L84 98Z" fill="{D}"/>
<path d="M248 62 L292 52 M262 54 L254 40 M286 52 L296 38" stroke="{D}" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M150 150 C110 176 70 170 40 150" stroke="#9aa3ad" stroke-width="9" fill="none" stroke-linecap="round"/>'''

ART["electrico"] = wheel(88,166,48)+wheel(312,166,48)+f'''
<g stroke="{{c}}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" fill="none">
<path d="M88 166 L150 100 L260 100 L312 166 M150 100 L190 166 L88 166 M190 166 L260 100"/></g>
<path d="M260 100 L276 60" stroke="{D}" stroke-width="8" stroke-linecap="round"/><path d="M262 58 L296 54" stroke="{D}" stroke-width="8" stroke-linecap="round"/>
<path d="M130 92 L176 92" stroke="{D}" stroke-width="12" stroke-linecap="round"/>
<rect x="168" y="106" width="74" height="22" rx="6" fill="{D}"/><rect x="176" y="112" width="40" height="10" rx="3" fill="#35c46b"/>
<circle cx="190" cy="166" r="12" fill="{M}"/>'''

ART["carga"] = wheel(80,176,32)+wheel(300,176,32)+wheel(130,176,32)+f'''
<path d="M40 70 L200 70 L204 160 L40 160Z" fill="{{c}}"/><path d="M40 70 L200 70 L200 84 L40 84Z" fill="#fff" opacity=".25"/>
<path d="M200 84 L250 84 C262 84 270 92 274 104 L290 150 L204 160Z" fill="{M}"/><path d="M212 92 L246 92 L256 118 L212 118Z" fill="#dfe8f0" opacity=".85"/>
<path d="M270 100 L300 90 L320 150 L300 176" stroke="#9aa3ad" stroke-width="8" fill="none" stroke-linecap="round"/>
<path d="M290 80 L322 76" stroke="{D}" stroke-width="7" stroke-linecap="round"/><ellipse cx="318" cy="132" rx="9" ry="7" fill="#fff"/>'''

NAMES = {"deportiva":"Deportivas","motocicleta":"Motocicletas","motoneta":"Motonetas","cuatrimoto":"Cuatrimotos y UTV","cross":"Cross y minimotos","electrico":"Eléctricos","carga":"Motocarros y carga"}

def svg(cat, color="#e31e24", cls="art"):
    body = ART[cat].replace("{c}", color)
    return (f'<svg class="{cls}" viewBox="0 0 400 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">'
            f'<ellipse cx="200" cy="214" rx="165" ry="9" fill="#000" opacity=".16"/>{body}</svg>')

def categorize(brand, name):
    n = name.upper()
    if any(k in n for k in ("ELECTRIC",)): return "electrico"
    if any(k in n for k in ("MOTOCARRO","RAMPANTE","APE ","CARGO","DZ200Q1")): return "carga"
    if "MONETA" in n or "SCALA" in n: return "motoneta"
    if "DEPORTIVA" in n or "NINJA 160" in n: return "deportiva"
    if any(k in n for k in ("MINICROSS","POCKET","CROSSTAR","CROSS PRO","R8 MINI","CROSS ")): return "cross"
    if n.startswith("Q") or "ATV" in n or "UTV" in n or "CUATRI" in n or "AMAROK" in n or "AMAX" in n or "GO KART" in n: return "cuatrimoto"
    return "motocicleta"
