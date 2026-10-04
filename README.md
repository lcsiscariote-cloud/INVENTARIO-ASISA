# Catálogo e inventario de motos (sitio estático)

Sin build ni dependencias: se despliega tal cual en Netlify (`publish = "."`).

## Vistas
| Ruta | Quién | Qué hace |
|---|---|---|
| `#/` | Todos | Catálogo por modelo: buscar, filtrar marca/año, colores |
| `#/modelo/<slug>` | Todos | Fotos, colores/años, ficha técnica, enlace al fabricante |
| `#/u/<inventario>` | QR de cada moto | Ficha de esa unidad. En modo Personal muestra serie, motor, ubicación |
| `#/escanear` | Personal | Escáner de QR con la cámara (o captura manual del inventario) |
| `#/qr` | Personal | Etiquetas QR imprimibles (todas o por ubicación) |

## Actualizar datos
- **Inventario**: reemplaza `data/INVENTARIOS_2026.xlsx` y corre `python3 scripts/build_data.py` (`pip install openpyxl`). Regenera `data/inventory.json`.
- **Fichas técnicas / descripción / fotos**: edita `data/models.json` (una entrada por modelo; el `slug` está en `inventory.json`). Nunca se sobreescribe.
- **Fotos**: súbelas a `photos/<slug>.jpg` y se usan solas, o lista varias en `models.json` → `"photos": ["photos/a.jpg", ...]`.
- **Ajustes** (PIN, precio público, WhatsApp): constante `CONFIG` al inicio de `app.js`.

## Nota de seguridad
El modo Personal usa un PIN en el navegador: oculta serie/motor/ubicación a clientes casuales, pero los datos están en `data/inventory.json` y son accesibles a quien los busque. Para protegerlos de verdad, separarlos tras una Netlify Function o activar contraseña en el sitio.
