"""Convierte data/INVENTARIOS_2026.xlsx -> data/inventory.json (y crea data/models.json si no existe).
Uso:  python3 scripts/build_data.py   (requiere: pip install openpyxl)
models.json NO se sobreescribe: ahí se agregan fichas técnicas y fotos a mano."""
import json, re, os, unicodedata, openpyxl
ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "data", "INVENTARIOS_2026.xlsx")

COLOR = {"ROJA":"ROJO","NEGRA":"NEGRO","BLANCA":"BLANCO","AMARILLA":"AMARILLO","N/R":"","PINK":"ROSA",
         "ROJA/BLANCO":"ROJO/BLANCO","BLUE CAMUFLAJE":"AZUL CAMUFLAJE","BLUE PINEAPPLE":"AZUL PINEAPPLE",
         "ORANGE PINEAPPLE":"NARANJA PINEAPPLE","HEPOLLEN":"HEPOLLEN"}
BRAND = {"FUNXI":"FUXIN"}
def clean(s): return re.sub(r"\s+"," ",str(s or "")).strip()
def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")

ws = openpyxl.load_workbook(SRC, data_only=True)["Hoja1"]
units, models, seen = [], {}, {}
for r in list(ws.iter_rows(values_only=True))[1:]:
    if not r[0]: continue
    inv = clean(r[0]); brand = BRAND.get(clean(r[2]).upper(), clean(r[2]).upper())
    tipo = clean(r[3]).upper(); color = clean(r[5]).upper(); color = COLOR.get(color, color)
    seen[inv] = seen.get(inv,0)+1
    uid = inv if seen[inv]==1 else f"{inv}-{seen[inv]}"   # inventarios repetidos en el Excel
    mslug = slug(f"{brand} {tipo}")
    m = models.setdefault(mslug, {"slug":mslug,"brand":brand,"name":tipo,"url":clean(r[8]) or None})
    if not m["url"] and r[8]: m["url"]=clean(r[8])
    units.append({"id":uid,"inv":inv,"model":mslug,"year":r[4] if isinstance(r[4],int) else None,
        "color":color,"location":clean(r[1]).replace("FILA-","FILA "),"serie":clean(r[6]),"motor":clean(r[7]),
        "price":r[9] if isinstance(r[9],(int,float)) else None})

json.dump({"models":list(models.values()),"units":units}, open(os.path.join(ROOT,"data","inventory.json"),"w"),
          ensure_ascii=False, indent=1)
mp = os.path.join(ROOT,"data","models.json")
if not os.path.exists(mp):
    json.dump({s:{"photos":[],"specs":{},"description":""} for s in models}, open(mp,"w"), ensure_ascii=False, indent=1)
print(len(units),"unidades,",len(models),"modelos")
