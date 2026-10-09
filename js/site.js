(() => {
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
  // ---- Ficha de modelo: color/año + galería ----
  const opts = $$(".opt");
  if (opts.length) {
    const G = JSON.parse(($("#galdata") || { textContent: "[]" }).textContent), stage = $("#stage"), pmain = $("#pmain"), thumbs = $("#thumbs"), artw = $(".artwrap"), note = $("#gnote");
    const ik = (u, w) => /imagekit\.io/.test(u) ? u + (u.includes("?") ? "&" : "?") + "tr=w-" + w + ",f-auto,q-80" : u;
    let cur = [], k = 0;
    const show = i => {
      k = i; const u = cur[i];
      pmain.innerHTML = '<div class="pimg"><img class="pbg" alt="" aria-hidden="true" src="' + ik(u, 48) + '"><img class="photo" decoding="async" alt="' + (pmain.dataset.alt || "") + '" src="' + ik(u, 900) + '"></div>';
      $$(".thb", thumbs).forEach((t, n) => t.classList.toggle("on", n === i));
    };
    const select = o => {
      opts.forEach(x => x.classList.toggle("on", x === o));
      $("#price").textContent = money(o.dataset.price);
      const urls = G[+o.dataset.i] || [];
      cur = urls; pmain.dataset.alt = (document.querySelector("h1").firstChild.textContent.trim() + " " + (o.dataset.color || "").toLowerCase()).trim();
      if (urls.length) {
        artw.hidden = true; pmain.hidden = false; note.hidden = true;
        thumbs.innerHTML = urls.length > 1 ? urls.map((u, n) => '<button class="thb" data-k="' + n + '"><img alt="" loading="lazy" src="' + ik(u, 160) + '"></button>').join("") : "";
        show(0);
      } else {
        pmain.hidden = true; artw.hidden = false; note.hidden = false; thumbs.innerHTML = "";
        $$("[data-base]", artw).forEach(p => p.setAttribute(p.dataset.base, o.dataset.hex));
      }
    };
    // marca los elementos que llevan el color de la carrocería de la ilustración (color de la opción inicial)
    const sel0 = opts.find(x => x.classList.contains("on")) || opts[0], first = sel0.dataset.hex.toLowerCase();
    $$("[fill],[stroke]", artw).forEach(p => ["fill", "stroke"].forEach(a => { if ((p.getAttribute(a) || "").toLowerCase() === first) p.dataset.base = a; }));
    cur = G[+sel0.dataset.i] || []; pmain.dataset.alt = (document.querySelector("h1").firstChild.textContent.trim() + " " + (sel0.dataset.color || "").toLowerCase()).trim();
    thumbs.addEventListener("click", e => { const t = e.target.closest(".thb"); if (t) show(+t.dataset.k); });
    $$(".thb", thumbs).forEach((t, n) => t.classList.toggle("on", n === 0));
    opts.forEach(o => o.onclick = () => select(o));
    // ampliar foto
    const lb = document.createElement("div"); lb.className = "lb"; lb.hidden = true; lb.innerHTML = '<button class="lb-x" aria-label="Cerrar">×</button><button class="lb-p" aria-label="Anterior">‹</button><img alt=""><button class="lb-n" aria-label="Siguiente">›</button>'; document.body.appendChild(lb);
    const lbi = $("img", lb), go = d => { if (!cur.length) return; k = (k + d + cur.length) % cur.length; lbi.src = ik(cur[k], 1600); lbi.alt = pmain.dataset.alt; show(k); };
    pmain.onclick = () => { if (!cur.length) return; lbi.src = ik(cur[k], 1600); lbi.alt = pmain.dataset.alt; lb.hidden = false; };
    $(".lb-x", lb).onclick = () => lb.hidden = true; $(".lb-p", lb).onclick = () => go(-1); $(".lb-n", lb).onclick = () => go(1);
    lb.addEventListener("click", e => { if (e.target === lb) lb.hidden = true; });
    document.addEventListener("keydown", e => { if (lb.hidden) return; if (e.key === "Escape") lb.hidden = true; if (e.key === "ArrowLeft") go(-1); if (e.key === "ArrowRight") go(1); });
    const u = new URLSearchParams(location.search).get("u");
    if (u) { const o = opts.find(x => x.dataset.ids.split(",").includes(u)); if (o) select(o); }
    try { if (sessionStorage.getItem("staff") === "1" && u) { const l = $("#staffLink"); l.href = "/staff/#/u/" + encodeURIComponent(u); $("#staffbar").hidden = false; } } catch (e) { }
  }
})();
