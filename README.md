# Assisa Motors · catálogo e inventario (sitio estático)

Se despliega tal cual en Netlify (`publish = "."`, sin build). Las páginas se **pre-generan** como HTML real para que Google y los asistentes de IA (ChatGPT, Claude, Perplexity…) puedan leer el catálogo.

## Estructura
| Ruta | Para qué |
|---|---|
| `/` | Portada pública: catálogo, categorías, preguntas frecuentes, ubicación |
| `/moto/<slug>/` | Una página por modelo (colores, precio, ficha). El QR de cada unidad apunta aquí con `?u=<inventario>` |
| `/categoria/<tipo>/` | Una página por categoría (motonetas, cuatrimotos…) |
| `/staff/` | App de personal: PIN, escáner QR, etiquetas, serie/motor/ubicación (`noindex`) |
| `sitemap.xml`, `robots.txt`, `llms.txt` | SEO y descubrimiento por IA |

## Flujo de actualización
1. **Inventario**: reemplaza `data/INVENTARIOS_2026.xlsx` → `python3 scripts/build_data.py` (`pip install openpyxl`).
2. **Datos del negocio** (dirección, teléfono, WhatsApp, horario, URL del sitio, link de Google Maps, financieras y plazos `financiers`/`termMin`/`termMax`): edita `data/business.json`.
3. **Fichas técnicas / descripción**: `data/models.json` (nunca se sobreescribe).
4. **Fotos**: guarda `photos/<slug>.jpg` (y `<slug>-2.jpg`, …). Reemplazan la ilustración solas.
5. **Regenera el sitio**: `python3 scripts/build_site.py` y sube los cambios.

## SEO local (León, Gto.)
Incluye JSON-LD (`MotorcycleDealer`, `Product`, `FAQPage`, `ItemList`, `BreadcrumbList`), `sitemap.xml`, `robots.txt` que permite a los bots de IA y `llms.txt`.
Para aparecer de verdad: llena `data/business.json`, crea/verifica tu **Perfil de Negocio en Google** con el mismo nombre, dirección y teléfono, y registra el sitio en **Google Search Console** enviando `sitemap.xml`. Si cambias de dominio, actualiza `siteUrl`.

## Seguridad
El PIN de `/staff/` (constante `CONFIG` en `staff/app.js`) es solo una barrera ligera en el navegador. Serie, motor y ubicación están en `data/inventory.json`, que es público. Para protegerlos de verdad, moverlos tras una Netlify Function.

## Fotos
Las fotos viven en ImageKit y se enlazan por URL:
1. `data/urls_imagenes.csv` — lista de fotos (modelo, color, URL) exportada del chat de WhatsApp.
2. `data/photo_map.json` — une cada `modelo_slug` del CSV con el/los modelos del inventario (y renombra colores con `aliases`).
3. `python3 scripts/import_photos.py` → genera `data/photos.json` (fotos por modelo y color; avisa de lo que no encontró).
4. `python3 scripts/build_site.py` → regenera el sitio. En la ficha, al elegir un color cambia la galería; si ese color no tiene fotos se muestra la ilustración con "Foto de este color próximamente".

Alternativa manual: `photos/<slug>.jpg` en el repo, o URLs en `data/models.json` → `"photos": [...]`.
