// ===== Configuración (edítala aquí) =====
const CONFIG = {
  STAFF_PIN: "1234",          // CÁMBIALO. Protección ligera del lado del cliente (ver README)
  SHOW_PRICE_PUBLIC: true,    // ¿clientes externos ven el precio?
  WHATSAPP: "",               // ej. "5215512345678" -> activa botón "Preguntar por WhatsApp"
};
// ========================================
const $ = (s, el = document) => el.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const money = n => n == null ? "Consultar" : "$" + n.toLocaleString("es-MX");
const COLORS = { ROJO: "#d02030", AZUL: "#1f5fbf", NEGRO: "#1a1a1a", BLANCO: "#f4f4f4", VERDE: "#2e9a4d", NARANJA: "#f28c1b", AMARILLO: "#f4c20d", ROSA: "#ee7fb0", GRIS: "#8a9099", "AZUL CIELO": "#6cc0ee" };
const dot = c => `<span class="dot" title="${esc(c)}" style="background:${COLORS[c] || COLORS[c.split(/[ /]/)[0]] || "#999"}"></span>`;
let staff = sessionStorage.getItem("staff") === "1", DB, MODELS = {};
document.body.classList.toggle("staff", staff);

const unitsOf = slug => DB.units.filter(u => u.model === slug);
const modelBy = slug => DB.models.find(m => m.slug === slug);
const photosOf = m => { const p = (MODELS[m.slug] || {}).photos || []; return p.length ? p : [`photos/${m.slug}.jpg`]; };
function ph(m, i = 0) {
  return `<div class="ph" style="position:relative">${esc(m.brand.slice(0, 1) + m.brand.slice(1, 2).toLowerCase())}<img src="${esc(photosOf(m)[i])}" alt="${esc(m.name)}" style="position:absolute;inset:0" onerror="this.remove()"></div>`;
}
function setNav(k) { document.querySelectorAll("nav a").forEach(a => a.classList.toggle("on", a.dataset.nav === k)); }

// ---------- Vistas ----------
function viewCatalog() {
  setNav("catalog");
  const brands = [...new Set(DB.models.map(m => m.brand))].sort();
  const years = [...new Set(DB.units.map(u => u.year).filter(Boolean))].sort().reverse();
  let brand = "";
  $("#app").innerHTML = `
  ${staff ? "" : `<section class="hero"><h1>Encuentra tu próxima moto</h1><p>Motonetas, deportivas, cuatrimotos, minicross y más. Consulta modelos, colores y precios.</p>
    <div class="stats"><div><b>${DB.models.length}</b><span>Modelos</span></div><div><b>${brands.length}</b><span>Marcas</span></div><div><b>${DB.units.length}</b><span>Unidades</span></div></div></section>`}
  <div class="brandbar" id="bb"><button class="chip on" data-b="">Todas</button>${brands.map(b => `<button class="chip" data-b="${esc(b)}">${esc(b)} <small>${DB.models.filter(m => m.brand === b).length}</small></button>`).join("")}</div>
  <div class="filters">
    <input id="q" type="search" placeholder="Buscar modelo, marca o color…" autocomplete="off">
    <select id="fy"><option value="">Todos los años</option>${years.map(y => `<option>${y}</option>`).join("")}</select>
    ${staff ? `<select id="fl"><option value="">Toda ubicación</option>${[...new Set(DB.units.map(u => u.location))].sort().map(l => `<option>${esc(l)}</option>`).join("")}</select>` : `<span></span>`}
  </div>
  <p class="count" id="count"></p><div class="grid" id="grid"></div>`;
  const draw = () => {
    const q = $("#q").value.toLowerCase().trim(), fb = brand, fy = $("#fy").value, fl = $("#fl")?.value || "";
    const list = DB.models.filter(m => {
      if (fb && m.brand !== fb) return false;
      const us = unitsOf(m.slug).filter(u => (!fy || String(u.year) === fy) && (!fl || u.location === fl));
      if (!us.length) return false;
      const hay = (m.brand + " " + m.name + " " + us.map(u => u.color).join(" ")).toLowerCase();
      return !q || q.split(/\s+/).every(w => hay.includes(w));
    });
    $("#count").textContent = `${list.length} ${list.length === 1 ? "modelo" : "modelos"}`;
    $("#grid").innerHTML = list.map(m => {
      const us = unitsOf(m.slug), prices = us.map(u => u.price).filter(Boolean), colors = [...new Set(us.map(u => u.color).filter(Boolean))];
      return `<a class="card" href="#/modelo/${m.slug}">${ph(m)}<div class="b"><div class="brand">${esc(m.brand)}</div><div class="name">${esc(m.name)}</div>
      ${CONFIG.SHOW_PRICE_PUBLIC || staff ? `<div class="price">${prices.length ? "Desde " + money(Math.min(...prices)) : "Precio a consultar"}</div>` : ""}
      <div class="dots">${colors.map(dot).join("")}</div>${staff ? `<div class="price">${us.length} en piso</div>` : ""}</div></a>`;
    }).join("") || `<p class="empty">Sin resultados.</p>`;
  };
  ["input", "change"].forEach(e => $(".filters").addEventListener(e, draw));
  $("#bb").onclick = e => { const c = e.target.closest("[data-b]"); if (!c) return; brand = c.dataset.b; document.querySelectorAll("#bb .chip").forEach(x => x.classList.toggle("on", x === c)); draw(); };
  draw();
}

function viewModel(slug, unitId) {
  const m = modelBy(slug); if (!m) return viewCatalog();
  setNav(""); const us = unitsOf(slug), info = MODELS[slug] || {}, specs = info.specs || {};
  const sel = unitId && us.find(u => u.id === unitId);
  const photos = photosOf(m);
  $("#app").innerHTML = `<a class="back" href="#/">← Catálogo</a>
  <div class="detail"><div class="gallery"><div id="main">${ph(m)}</div>
    ${photos.length > 1 ? `<div class="thumbs">${photos.map((p, i) => `<img src="${esc(p)}" data-i="${i}" alt="">`).join("")}</div>` : ""}</div>
  <div><div class="brand">${esc(m.brand)}</div><h2 style="margin:0 0 6px">${esc(m.name)}</h2>
    ${info.description ? `<p>${esc(info.description)}</p>` : ""}
    ${sel ? `<div class="panel"><span class="tag ${staff ? "staff" : ""}">${staff ? "Unidad escaneada" : "Unidad seleccionada"}</span><table>
      <tr><td>Color</td><td>${dot(sel.color)} ${esc(sel.color || "—")}</td></tr><tr><td>Año</td><td>${sel.year ?? "—"}</td></tr>
      ${CONFIG.SHOW_PRICE_PUBLIC || staff ? `<tr><td>Precio</td><td><b>${money(sel.price)}</b></td></tr>` : ""}
      ${staff ? `<tr><td>Inventario</td><td>${esc(sel.inv)}</td></tr><tr><td>Ubicación</td><td>${esc(sel.location)}</td></tr><tr><td>Serie</td><td>${esc(sel.serie)}</td></tr><tr><td>Motor</td><td>${esc(sel.motor)}</td></tr>` : ""}</table></div>` : ""}
    <div class="panel"><h3>Colores y años disponibles</h3><div class="chips">${us.map(u => `<button class="chip ${sel && sel.id === u.id ? "on" : ""}" data-u="${esc(u.id)}">${dot(u.color)} ${esc(u.color || "—")} ${u.year ?? ""}</button>`).join("")}</div>
      <p class="hint">Toca una opción para ver el detalle.</p></div>
    <div class="panel"><h3>Ficha técnica</h3>${Object.keys(specs).length ? `<table>${Object.entries(specs).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join("")}</table>` : `<p class="empty">Próximamente.</p>`}</div>
    <div class="row no-print">${m.url ? `<a class="btn ghost" target="_blank" rel="noopener" href="${esc(m.url)}">Sitio del fabricante</a>` : ""}
      ${CONFIG.WHATSAPP ? `<a class="btn" target="_blank" rel="noopener" href="https://wa.me/${CONFIG.WHATSAPP}?text=${encodeURIComponent("Hola, me interesa la " + m.brand + " " + m.name)}">Preguntar por WhatsApp</a>` : ""}</div>
  </div></div>`;
  $("#app").onclick = e => {
    const t = e.target.closest("[data-i]"); if (t) $("#main").innerHTML = ph(m, +t.dataset.i);
    const c = e.target.closest("[data-u]"); if (c) openUnitModal(slug, c.dataset.u);
  };
}

function openUnitModal(slug, id) {
  const m = modelBy(slug), u = DB.units.find(x => x.id === id);
  const md = $("#modal"); md.hidden = false;
  md.innerHTML = `<div class="sheet"><h3>${esc(m.brand)} ${esc(m.name)}</h3><table>
    <tr><td>Color</td><td>${dot(u.color)} ${esc(u.color || "—")}</td></tr><tr><td>Año</td><td>${u.year ?? "—"}</td></tr>
    ${CONFIG.SHOW_PRICE_PUBLIC || staff ? `<tr><td>Precio</td><td><b>${money(u.price)}</b></td></tr>` : ""}
    ${staff ? `<tr><td>Inventario</td><td>${esc(u.inv)}</td></tr><tr><td>Ubicación</td><td>${esc(u.location)}</td></tr><tr><td>Serie</td><td>${esc(u.serie)}</td></tr><tr><td>Motor</td><td>${esc(u.motor)}</td></tr>` : ""}</table>
    <div class="row"><button class="ghost" id="mx">Cerrar</button></div></div>`;
  $("#mx").onclick = () => md.hidden = true; md.onclick = e => { if (e.target === md) md.hidden = true; };
}

let scanner;
function stopScanner() { if (scanner) { scanner.stop().catch(() => { }); scanner = null; } }
function viewScan() {
  setNav("escanear");
  if (!staff) return askPin(viewScan);
  $("#app").innerHTML = `<h2>Escanear QR</h2><div id="reader"></div><p class="hint" style="text-align:center">Apunta a la etiqueta de la moto. Si no hay cámara, escribe el inventario:</p>
  <div class="row" style="max-width:420px;margin:auto"><input id="manual" placeholder="Ej. 1600-226"><button id="go" style="flex:0 0 auto">Buscar</button></div>`;
  const go = txt => {
    const mt = txt.match(/#\/u\/([^\s/]+)/); const id = decodeURIComponent(mt ? mt[1] : txt.trim());
    const u = DB.units.find(x => x.id.toLowerCase() === id.toLowerCase() || x.inv.toLowerCase() === id.toLowerCase());
    if (!u) return alert("No encontré esa unidad: " + id);
    stopScanner(); location.hash = "#/u/" + encodeURIComponent(u.id);
  };
  $("#go").onclick = () => go($("#manual").value);
  const start = () => { scanner = new Html5Qrcode("reader"); scanner.start({ facingMode: "environment" }, { fps: 10, qrbox: 240 }, go).catch(() => $("#reader").innerHTML = `<p class="empty">No se pudo abrir la cámara (permiso o HTTPS).</p>`); };
  window.Html5Qrcode ? start() : addEventListener("load", start, { once: true });
}

function viewLabels() {
  setNav("qr"); if (!staff) return askPin(viewLabels);
  $("#app").innerHTML = `<div class="no-print"><h2>Etiquetas QR</h2><p class="hint">Cada QR abre la ficha de esa unidad. Imprime y pega en la moto.</p>
  <div class="row" style="max-width:420px"><select id="lf"><option value="">Todas las unidades</option>${[...new Set(DB.units.map(u => u.location))].sort().map(l => `<option>${esc(l)}</option>`).join("")}</select><button id="pr">Imprimir</button></div></div><div class="labels" id="labels"></div>`;
  const draw = () => {
    const f = $("#lf").value, base = location.origin + location.pathname.replace(/index\.html$/, "");
    $("#labels").innerHTML = DB.units.filter(u => !f || u.location === f).map(u => {
      const qr = qrcode(0, "M"); qr.addData(base + "#/u/" + encodeURIComponent(u.id)); qr.make();
      return `<div class="label">${qr.createSvgTag({ scalable: true })}<div><b>${esc(u.inv)}</b></div><div>${esc(modelBy(u.model).name)} · ${esc(u.color)}</div></div>`;
    }).join("");
  };
  $("#lf").onchange = draw; $("#pr").onclick = () => print();
  window.qrcode ? draw() : addEventListener("load", draw, { once: true });
}

// ---------- Modo personal ----------
function askPin(then) {
  const md = $("#modal"); md.hidden = false;
  md.innerHTML = `<div class="sheet"><h3>Modo personal</h3><input id="pin" type="password" inputmode="numeric" placeholder="PIN" autofocus>
  <div class="row"><button class="ghost" id="pc">Cancelar</button><button id="pk">Entrar</button></div></div>`;
  const ok = () => { if ($("#pin").value === CONFIG.STAFF_PIN) { staff = true; sessionStorage.setItem("staff", "1"); document.body.classList.add("staff"); md.hidden = true; route(); } else { $("#pin").value = ""; $("#pin").placeholder = "PIN incorrecto"; } };
  $("#pk").onclick = ok; $("#pin").onkeydown = e => e.key === "Enter" && ok();
  $("#pc").onclick = () => { md.hidden = true; location.hash = "#/"; };
}
$("#staffBtn").onclick = () => {
  if (staff) { staff = false; sessionStorage.removeItem("staff"); document.body.classList.remove("staff"); route(); } else askPin();
};

// ---------- Router ----------
function route() {
  stopScanner(); $("#modal").hidden = true; window.scrollTo(0, 0);
  const [, a, b] = location.hash.split("/");
  if (a === "modelo") viewModel(b);
  else if (a === "u") { const u = DB.units.find(x => x.id === decodeURIComponent(b || "")); u ? viewModel(u.model, u.id) : viewCatalog(); }
  else if (a === "escanear") viewScan();
  else if (a === "qr") viewLabels();
  else viewCatalog();
}
addEventListener("hashchange", route);
Promise.all([fetch("data/inventory.json").then(r => r.json()), fetch("data/models.json").then(r => r.json()).catch(() => ({}))])
  .then(([d, m]) => { DB = d; MODELS = m; route(); })
  .catch(() => $("#app").innerHTML = `<p class="empty">No se pudo cargar el inventario.</p>`);
