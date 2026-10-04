(() => {
  // ---- Burbuja de contacto ----
  const fb = document.getElementById("fabBtn"), fm = document.getElementById("fabMenu");
  if (fb && fm) {
    const set = open => { fm.hidden = !open; fb.setAttribute("aria-expanded", open); };
    fb.onclick = e => { e.stopPropagation(); set(fm.hidden); };
    document.addEventListener("click", e => { if (!fm.hidden && !fm.contains(e.target)) set(false); });
    document.addEventListener("keydown", e => { if (e.key === "Escape") set(false); });
  }
  const $ = (s, e = document) => e.querySelector(s), $$ = (s, e = document) => [...e.querySelectorAll(s)];
  const money = n => n ? "$" + Number(n).toLocaleString("es-MX") + " MXN" : "Consultar precio";
  // ---- Catálogo: filtros ----
  const grid = $("#grid");
  if (grid) {
    const st = { cat: "", brand: "", q: "", sort: "" }, cards = $$(".card", grid), plural = n => n + (n === 1 ? " modelo" : " modelos");
    const draw = () => {
      const words = st.q.toLowerCase().split(/\s+/).filter(Boolean);
      let shown = cards.filter(c => (!st.cat || c.dataset.cat === st.cat) && (!st.brand || c.dataset.brand === st.brand) && words.every(w => c.dataset.q.includes(w)));
      cards.forEach(c => c.hidden = !shown.includes(c));
      const key = { asc: c => +c.dataset.price || 9e9, desc: c => -(+c.dataset.price), name: null }[st.sort];
      shown.sort((a, b) => st.sort === "name" ? a.dataset.name.localeCompare(b.dataset.name) : key ? key(a) - key(b) : 0).forEach((c, i) => c.style.order = st.sort ? i : 0);
      if (!st.sort) cards.forEach(c => c.style.order = 0);
      $("#count").textContent = plural(shown.length); $("#empty").hidden = shown.length > 0;
    };
    $$(".chip[data-f]").forEach(b => b.onclick = () => { st[b.dataset.f] = b.dataset.v; $$(`.chip[data-f="${b.dataset.f}"]`).forEach(x => x.classList.toggle("on", x === b)); draw(); });
    $("#q").oninput = e => { st.q = e.target.value; draw(); }; $("#sort").onchange = e => { st.sort = e.target.value; draw(); };
    $$("a[data-brand]").forEach(a => a.onclick = () => { const b = $(`.chip[data-f="brand"][data-v="${a.dataset.brand}"]`); b && b.click(); });
  }
  // ---- Ficha de modelo: color/año ----
  const art = $("#stage"), opts = $$(".opt");
  if (opts.length) {
    const body = $(".gal svg");
    const select = o => {
      opts.forEach(x => x.classList.toggle("on", x === o));
      if (body) $$("[data-base]", body).forEach(p => p.setAttribute(p.dataset.base, o.dataset.hex));
      $("#price").textContent = money(o.dataset.price);
    };
    // marca los elementos que llevan el color de la carrocería (el color inicial es el de la 1ª opción)
    if (body) { const first = opts[0].dataset.hex.toLowerCase(); $$("[fill],[stroke]", body).forEach(p => ["fill", "stroke"].forEach(a => { if ((p.getAttribute(a) || "").toLowerCase() === first) p.dataset.base = a; })); }
    opts.forEach(o => o.onclick = () => select(o));
    const u = new URLSearchParams(location.search).get("u");
    if (u) { const o = opts.find(x => x.dataset.ids.split(",").includes(u)); if (o) select(o); }
    try { if (sessionStorage.getItem("staff") === "1" && u) { const l = $("#staffLink"); l.href = "/staff/#/u/" + encodeURIComponent(u); $("#staffbar").hidden = false; } } catch (e) { }
  }
})();
