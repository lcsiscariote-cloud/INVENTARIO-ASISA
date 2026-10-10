"""data/urls_imagenes*.csv (+ data/photo_map.json) -> data/photos.json  {slug_inventario: [{color, urls:[...]}]}
Uso: python3 scripts/import_photos.py   y luego   python3 scripts/build_site.py"""
import csv, json, os, glob, collections
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
rows = [r for f in sorted(glob.glob(os.path.join(R, "data", "urls_imagenes*.csv"))) for r in csv.DictReader(open(f, encoding="utf-8-sig"))]
pm = json.load(open(os.path.join(R, "data", "photo_map.json")))
inv = {m["slug"] for m in json.load(open(os.path.join(R, "data", "inventory.json")))["models"]}
out, seen, sinmapa = {}, set(), collections.Counter()
for r in sorted(rows, key=lambda r: (r["modelo_slug"], r["color"], r["archivo"])):
    m = pm.get(r["modelo_slug"])
    if not m: sinmapa[r["modelo"]] += 1; continue
    if r["sha256"] in seen: continue
    seen.add(r["sha256"])
    color = "" if m.get("ref") else m.get("aliases", {}).get(r["color"], r["color"])  # ref: foto de referencia, vale para cualquier color
    for slug in m["to"]:
        assert slug in inv, f"slug inexistente: {slug}"
        sets = out.setdefault(slug, [])
        s = next((x for x in sets if x["color"] == color), None) or sets.append({"color": color, "urls": [], **({"ref": True} if m.get("ref") else {})}) or sets[-1]
        s["urls"].append(r["url"])
json.dump(out, open(os.path.join(R, "data", "photos.json"), "w"), ensure_ascii=False, indent=1)
print(len(out), "modelos del inventario con fotos;", sum(len(s["urls"]) for v in out.values() for s in v), "fotos")
for k, v in sinmapa.items(): print("SIN MAPEAR (no está en inventario.json):", k, v, "fotos")
