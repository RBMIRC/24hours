"""Page web « 24 Hours » (anglais) : le séquencier d'une journée en défilement continu, une carte par séquence.

Usage : python3 scripts/page_24h.py AAAA-MM-JJ [dossier de copie, ex. /home/user/week/24h]
Lit journees/AAAA-MM-JJ/sequencier.json et journee.json ; écrit index.html à la racine du dépôt (GitHub Pages :
https://rbmirc.github.io/24hours/) et, si demandé, une copie dans un autre dossier.
Types de séquence et lieux : tables TYPES et LIEUX ci-dessous (couleurs, règles de rattachement)."""
import datetime as dt, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = [  # (id, libellé, couleur, fils du séquencier)
    ("night", "Night", "#3b4a7a", {"nuit"}),
    ("light", "Dawn & dusk", "#c06c84", {"aube"}),
    ("waking", "Waking & lodges", "#8e6fb3", {"lodges"}),
    ("meal", "Meals & kitchen", "#d08a2e", {"repas", "cuisine", "magasin"}),
    ("farm", "Farm", "#5a8f3c", {"ferme"}),
    ("class", "Class", "#2f7fb8", {"cours", "theatre", "hansgirg", "danse"}),
    ("work", "Work program", "#8a6a4b", {"chaudieres", "entretien", "atelier", "linge"}),
    ("office", "Mail & office", "#4f8a8b", {"courrier", "bureau", "bulletin"}),
    ("evening", "Evening program", "#b5476b", {"cole", "kazin", "disques"}),
    ("journey", "Journeys", "#6b7280", {"wunsch", "dreier"}),
    ("faculty", "Faculty at work", "#9a7b2f", {"albers", "lowinsky", "bibliotheque"}),
    ("interlude", "Interlude", "#9ca3af", {"liaison", "vie"}),
]
LIEUX = [  # (id, libellé, couleur, motif sur le lieu en anglais) — le premier qui convient
    ("offcampus", "Off campus", "#6b7280", r"brevard|station|road"),
    ("farm", "Farm", "#5a8f3c", r"farm|milking|barn"),
    ("dining", "Dining Hall", "#d08a2e", r"dining|kitchen|pantry|porch|mail box"),
    ("roundhouse", "Round House", "#b5476b", r"round house"),
    ("library", "Library, office & store", "#4f8a8b", r"library|office|store"),
    ("studies", "Studies Building", "#2f7fb8", r"studies|study|language room|faculty room|physics lab|weaving room"),
    ("northlodge", "North Lodge", "#8e6fb3", r"north lodge"),
    ("southlodge", "South Lodge", "#7a5aa6", r"south lodge"),
    ("cottages", "Cottages & studios", "#9a7b2f", r"cottage|mountain stream|studio"),
    ("shops", "Shops & furnaces", "#8a6a4b", r"woodshop|furnace|coal|buildings"),
    ("lake", "Lake & grounds", "#3b6f8f", r"lake|campus"),
]


def type_de(o):
    if re.search(r"office", o["lieu_en"], re.I) and o["fil"] == "dreier": return "office"
    return next((t for t, _, _, fils in TYPES if o["fil"] in fils), "interlude")


def lieu_de(o):
    return next((l for l, _, _, rx in LIEUX if re.search(rx, o["lieu_en"], re.I)), "lake")


def main(jour, copie=None):
    dos = os.path.join(ROOT, "journees", jour)
    S = json.load(open(os.path.join(dos, "sequencier.json"), encoding="utf-8"))
    J = json.load(open(os.path.join(dos, "journee.json"), encoding="utf-8"))
    d = dt.date.fromisoformat(jour)
    seq = [{"n": o["n"], "a": o["debut"], "b": o["fin"], "p": o["pages"], "m": o["duree_min"], "h": o["entete_en"], "t": type_de(o),
            "l": lieu_de(o), "pl": o["lieu_en"], "x": o["action_en"], "q": o.get("qui_en", o["qui"]), "pct": o["pct"], "st": o["statut_en"],
            "why": o.get("m_en", ""), "src": o["src"], "mo": o["moment"]} for o in S]
    heures = []
    era = {x["heure"][:2]: x for x in J["meteo"]["era5_par_heure"]}
    for x in J["lumiere"]["par_heure"]:
        w = era.get(x["heure"][:2], {})
        heures.append({"h": x["heure"], "sun": x["soleil_hauteur"], "moon": x["lune_hauteur"], "light": x["etat"],
                       "temp": w.get("temp_c"), "sky": w.get("temps", ""), "cloud": w.get("nuages_pct"), "wind": w.get("vent_kmh")})
    LU = J["lumiere"]
    noaa = J["meteo"]["noaa"]; mt = noaa.get("Montreat", {}).get(jour) or {}
    data = {"seq": seq, "hours": heures, "types": [{"id": t, "label": l, "color": c} for t, l, c, _ in TYPES],
            "places": [{"id": t, "label": l, "color": c} for t, l, c, _ in LIEUX],
            "sun": {k: LU.get(k) for k in ("aube_civile", "lever_soleil", "coucher_soleil", "crepuscule_civil", "lever_lune", "coucher_lune")},
            "moon_pct": LU.get("lune_eclairee_pct"), "noaa": {"min": mt.get("tmin_c"), "max": mt.get("tmax_c"), "minf": mt.get("tmin_f"), "maxf": mt.get("tmax_f")}}
    html = PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    html = html.replace("__N__", str(len(seq)))
    for p in [os.path.join(ROOT, "index.html")] + ([os.path.join(copie, "index.html")] if copie else []):
        os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w", encoding="utf-8").write(html)
        print(p, len(html) // 1024, "Ko")
    open(os.path.join(ROOT, ".nojekyll"), "w").close()


PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>24 Hours at Black Mountain College</title>
<meta name="description" content="Monday, December 4, 1944, at Black Mountain College, minute by minute: __N__ sequences, 1,440 pages (one page per minute), each with its sources and its deduced share.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f3ee;--paper:#fffdf9;--ink:#1f1d1a;--soft:#6b655c;--line:#e3ddd2;--chipbg:#f0ebe2;--att:#2e7d32;--tra:#b7791f;--ass:#b03a2e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15161a;--paper:#1d1f24;--ink:#ecebe7;--soft:#a3a09a;--line:#2e3138;--chipbg:#262930;--att:#66bb6a;--tra:#e0a43a;--ass:#e5675a}}
:root[data-theme="dark"]{--bg:#15161a;--paper:#1d1f24;--ink:#ecebe7;--soft:#a3a09a;--line:#2e3138;--chipbg:#262930;--att:#66bb6a;--tra:#e0a43a;--ass:#e5675a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 "Source Serif 4",Georgia,serif}
a{color:inherit}
header.top{max-width:980px;margin:0 auto;padding:40px 16px 8px}
h1{font:600 clamp(28px,5vw,44px)/1.1 "Source Serif 4",Georgia,serif;margin:0 0 6px}
.sub{font:500 15px/1.4 Inter,system-ui,sans-serif;color:var(--soft);margin:0 0 18px}
.intro{font-size:16px;max-width:760px}
.facts{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0;font:500 13px/1.3 Inter,system-ui,sans-serif}
.facts span{background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:6px 12px}
.bar{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(6px);border-bottom:1px solid var(--line)}
.bar .in{max-width:980px;margin:0 auto;padding:10px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;font:500 13px Inter,system-ui,sans-serif}
.clock{font:700 22px "Courier Prime",monospace;min-width:76px}
.now{color:var(--soft)}
.rail{display:flex;gap:2px;flex:1 1 320px;min-width:240px}
.rail button{flex:1;height:22px;border:0;border-radius:3px;cursor:pointer;font:500 9px Inter,sans-serif;color:#fff;padding:0;opacity:.9}
.rail button:hover{opacity:1;outline:2px solid var(--ink)}
.filters{max-width:980px;margin:0 auto;padding:10px 16px 0;font:500 12px Inter,system-ui,sans-serif}
.filters .row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0}
.filters .lab{color:var(--soft);min-width:70px;text-transform:uppercase;letter-spacing:.06em;font-size:11px}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:3px 10px;font:600 12px Inter,system-ui,sans-serif;border:1.5px solid var(--c);color:var(--ink);background:var(--paper);cursor:pointer;white-space:nowrap}
.chip i{width:9px;height:9px;border-radius:50%;background:var(--c);display:inline-block}
.chip.type{background:var(--c);color:#fff;border-color:var(--c)}
.chip.off{opacity:.35}
.reset{border:0;background:none;color:var(--soft);text-decoration:underline;cursor:pointer;font:inherit}
main{max-width:980px;margin:0 auto;padding:8px 16px 80px}
.hour{position:relative;margin:28px 0 10px;border-radius:12px;padding:14px 16px;color:#fff;font:500 13px/1.4 Inter,system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline}
.hour b{font:700 26px "Courier Prime",monospace;margin-right:6px}
.seq{position:relative;display:grid;grid-template-columns:96px 1fr;gap:0 16px;background:var(--paper);border:1px solid var(--line);border-left:6px solid var(--tc);border-radius:10px;margin:8px 0;padding:12px 14px;min-height:calc(var(--m) * 7px)}
.seq.dim{opacity:.18}
.t{font:700 15px "Courier Prime",monospace}
.t small{display:block;font:500 11px Inter,system-ui,sans-serif;color:var(--soft);margin-top:2px}
.dur{margin-top:8px;width:6px;border-radius:3px;background:var(--tc);height:calc(var(--m) * 5px);max-height:240px;opacity:.55}
.head{font:700 14px/1.3 "Courier Prime",monospace;letter-spacing:.02em;margin:0 0 6px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px}
.tags .chip{cursor:default;font-size:11px;padding:2px 9px}
.x{margin:0 0 6px}
.who{font:500 13px/1.4 Inter,system-ui,sans-serif;color:var(--soft);margin:0 0 6px}
.meta{font:500 12px/1.4 Inter,system-ui,sans-serif;color:var(--soft);display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center}
.ded{font-weight:700;border-radius:6px;padding:1px 7px;color:#fff}
.ded.attested{background:var(--att)}.ded.transposed{background:var(--tra)}.ded.assumed{background:var(--ass)}
details{margin-top:6px;font:400 12px/1.45 Inter,system-ui,sans-serif;color:var(--soft)}
summary{cursor:pointer}
.legend{font:500 12px/1.5 Inter,system-ui,sans-serif;color:var(--soft);max-width:760px}
#sentinel{height:60px}
footer{max-width:980px;margin:0 auto;padding:30px 16px 60px;font:400 13px/1.6 Inter,system-ui,sans-serif;color:var(--soft)}
@media (max-width:600px){.seq{grid-template-columns:64px 1fr;gap:0 10px}.t{font-size:13px}.hour b{font-size:22px}}
</style>
</head>
<body>
<header class="top">
  <h1>24 Hours at Black Mountain College</h1>
  <p class="sub">Monday, December 4, 1944 · Lake Eden, Black Mountain, North Carolina · a day in real time</p>
  <p class="intro">One page per minute: 1,440 pages from midnight to midnight, cut into <b>__N__ sequences</b>. When several things happen at once, the film cuts between them; each class keeps a quarter of its own time on screen, so that four classes held at the same hour can all be seen. Every sequence keeps its sources and its <b>deduced share</b>: <span class="ded attested">≤ 10%</span> attested by a dated document, <span class="ded transposed">11–40%</span> an attested custom carried over to this day, <span class="ded assumed">&gt; 40%</span> assumed, to be confirmed.</p>
  <div class="facts" id="facts"></div>
</header>
<div class="bar"><div class="in">
  <span class="clock" id="clock">00:00</span><span class="now" id="now">page 1 · night</span>
  <div class="rail" id="rail" aria-label="Jump to an hour"></div>
</div></div>
<div class="filters">
  <div class="row"><span class="lab">Sequence</span><span id="ftypes"></span></div>
  <div class="row"><span class="lab">Place</span><span id="fplaces"></span> <button class="reset" id="reset">show all</button></div>
</div>
<main id="list"></main>
<div id="sentinel"></div>
<footer>
  <p class="legend">Sluglines follow screenplay form (INT./EXT. PLACE — NIGHT, DAWN, DAY, DUSK, from the exact times of dawn, sunrise, sunset, and twilight). “(cont.)” marks a return to a sequence already opened. “(enrolled)” marks students who list the class on their BMC Yearbook record for fall 1944.</p>
  <p>Sources: Black Mountain College Community Bulletins and announcements of fall 1944 (Asheville Art Museum, Black Mountain College Collection); Martin Duberman, <i>Black Mountain</i> (1972); David Silver, <i>The Farm at Black Mountain College</i> (2024); Mary Emma Harris interviews; BMC Yearbook (Black Mountain College Museum + Arts Center); weather: NOAA GHCN-Daily and ERA5 reanalysis (Open-Meteo, CC BY 4.0); sun and moon calculated. Summaries are ours; short quotations only.
  Working files, in French: <a href="https://github.com/RBMIRC/24hours">github.com/RBMIRC/24hours</a> · the week-by-week calendar: <a href="https://rbmirc.github.io/week/?lang=en">rbmirc.github.io/week</a>.</p>
</footer>
<script>
const D = __DATA__;
const T = Object.fromEntries(D.types.map(x => [x.id, x])), P = Object.fromEntries(D.places.map(x => [x.id, x]));
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
const fmt = h => { if (!h) return ""; let [H, M] = h.split(":").map(Number); const ap = H >= 12 ? "p.m." : "a.m."; H = H % 12 || 12; return `${H}:${String(M).padStart(2,"0")} ${ap}`; };
const sky = h => { const s = h.sun, c = h.cloud ?? 0;
  if (s < -12) return "#1c2340"; if (s < -6) return "#3a3f6b"; if (s < -0.8) return "#8a5a7a";
  return c >= 80 ? "#7d8796" : s < 15 ? "#c98b5f" : "#4f86b8"; };
const lightEn = {"nuit":"night","nuit astronomique claire":"astronomical twilight","aube ou crépuscule nautique":"nautical twilight","aube ou crépuscule civil":"civil twilight","jour":"daylight"};
const skyEn = {"ciel clair":"clear","plutôt clair":"mainly clear","partiellement nuageux":"partly cloudy","couvert":"overcast","pluie faible":"light rain","pluie":"rain","bruine":"drizzle"};
// facts
const f = document.getElementById("facts");
[["Dawn", D.sun.aube_civile], ["Sunrise", D.sun.lever_soleil], ["Sunset", D.sun.coucher_soleil], ["Dark", D.sun.crepuscule_civil], ["Moonrise", D.sun.lever_lune]]
  .forEach(([k, v]) => v && f.insertAdjacentHTML("beforeend", `<span>${k} ${fmt(v)}</span>`));
f.insertAdjacentHTML("beforeend", `<span>Waning moon, ${D.moon_pct}% lit</span><span>Montreat: ${D.noaa.min} °C to ${D.noaa.max} °C (${D.noaa.minf}–${D.noaa.maxf} °F), dry</span><span>Eastern War Time (UTC−4)</span>`);
// rail
const rail = document.getElementById("rail");
D.hours.forEach(h => { const b = document.createElement("button"); b.textContent = h.h.slice(0,2); b.style.background = sky(h); b.title = `${h.h} · ${lightEn[h.light]||h.light}`;
  b.onclick = () => jump(h.h.slice(0,2)); rail.appendChild(b); });
// filters
const on = {t: new Set(D.types.map(x => x.id)), l: new Set(D.places.map(x => x.id))};
const count = (k, id) => D.seq.filter(s => s[k] === id).reduce((a, s) => a + s.m, 0);
function chips(id, list, key, cls) { const el = document.getElementById(id);
  list.forEach(x => { const n = count(key, x.id); if (!n) return; const c = document.createElement("span"); c.className = `chip ${cls}`; c.style.setProperty("--c", x.color);
    c.innerHTML = (cls === "type" ? "" : "<i></i>") + `${esc(x.label)} <small style="opacity:.75">${n}</small>`; c.title = `${n} pages`;
    c.onclick = () => { const s = on[key]; if (s.size === list.length) { s.clear(); s.add(x.id); } else if (s.has(x.id)) { s.delete(x.id); if (!s.size) list.forEach(y => s.add(y.id)); } else s.add(x.id);
      el.querySelectorAll(".chip").forEach((e, i) => {}); refresh(); };
    c.dataset.id = x.id; el.appendChild(c); }); }
chips("ftypes", D.types, "t", "type"); chips("fplaces", D.places, "l", "place");
document.getElementById("reset").onclick = () => { D.types.forEach(x => on.t.add(x.id)); D.places.forEach(x => on.l.add(x.id)); refresh(); };
function refresh() {
  document.querySelectorAll("#ftypes .chip").forEach(c => c.classList.toggle("off", !on.t.has(c.dataset.id)));
  document.querySelectorAll("#fplaces .chip").forEach(c => c.classList.toggle("off", !on.l.has(c.dataset.id)));
  document.querySelectorAll(".seq").forEach(e => e.classList.toggle("dim", !(on.t.has(e.dataset.t) && on.l.has(e.dataset.l)))); }
// infinite list
const list = document.getElementById("list"); let i = 0, lastHour = null; const BATCH = 25;
function card(s) {
  const t = T[s.t], p = P[s.l], cls = s.st === "attested" ? "attested" : s.st === "assumed" ? "assumed" : "transposed";
  return `<article class="seq" id="s${s.n}" data-t="${s.t}" data-l="${s.l}" data-a="${s.a}" style="--tc:${t.color};--m:${s.m}">
    <div><div class="t">${s.a}<small>${s.m} min · p. ${s.p}</small><small>#${s.n}</small></div><div class="dur"></div></div>
    <div><p class="head">${esc(s.h)}</p>
      <div class="tags"><span class="chip type" style="--c:${t.color}">${esc(t.label)}</span><span class="chip" style="--c:${p.color}"><i></i>${esc(p.label)}</span></div>
      <p class="x">${esc(s.x)}</p>
      ${s.q && s.q.length ? `<p class="who">${esc(s.q.join(", "))}</p>` : ""}
      <div class="meta"><span class="ded ${cls}">${s.pct}% deduced</span><span>${esc(s.st)}</span><span>${s.a}–${s.b}</span></div>
      <details><summary>Sources</summary>${esc(s.src)}${s.why ? `<br><i>Why this share:</i> ${esc(s.why)}` : ""}</details></div></article>`; }
function hourBand(hh) { const h = D.hours[+hh];
  return `<div class="hour" id="h${hh}" style="background:${sky(h)}"><b>${hh}:00</b><span>pages ${+hh*60+1}–${+hh*60+60}</span><span>${lightEn[h.light]||h.light}</span>
    <span>${skyEn[h.sky]||h.sky}, ${h.temp} °C</span><span>sun ${h.sun}°</span><span>moon ${h.moon}°</span>${h.wind!=null?`<span>wind ${h.wind} km/h</span>`:""}</div>`; }
function more(until) {
  let n = 0; while (i < D.seq.length && (n < BATCH || (until && D.seq[i].a.slice(0,2) <= until))) { const s = D.seq[i++], hh = s.a.slice(0,2);
    if (hh !== lastHour) { for (let k = lastHour == null ? 0 : +lastHour + 1; k <= +hh; k++) list.insertAdjacentHTML("beforeend", hourBand(String(k).padStart(2,"0"))); lastHour = hh; }
    list.insertAdjacentHTML("beforeend", card(s)); n++; }
  refresh(); }
new IntersectionObserver(e => { if (e[0].isIntersecting) more(); }, {rootMargin: "1200px"}).observe(document.getElementById("sentinel"));
function jump(hh) { more(hh); const el = document.getElementById("h" + hh); if (el) el.scrollIntoView({behavior: "smooth"}); }
// clock: the sequence at the top of the screen
const clock = document.getElementById("clock"), now = document.getElementById("now");
addEventListener("scroll", () => { const cards = list.querySelectorAll(".seq"); let cur = null;
  for (const c of cards) { if (c.getBoundingClientRect().top > 110) break; cur = c; }
  if (cur) { const s = D.seq[+cur.id.slice(1) - 1], [H, M] = s.a.split(":").map(Number); clock.textContent = s.a; now.textContent = `page ${H*60+M+1} · ${T[s.t].label} · ${P[s.l].label}`; } }, {passive: true});
more();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(*sys.argv[1:3])
