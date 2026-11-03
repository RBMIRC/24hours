"""Page web « 24 Hours » (anglais) : le séquencier d'une journée en défilement continu, une carte par séquence.

Usage : python3 scripts/page_24h.py AAAA-MM-JJ [dossier de copie, ex. /home/user/week/24h]
Lit journees/AAAA-MM-JJ/sequencier.json et journee.json ; écrit index.html à la racine du dépôt (GitHub Pages :
https://rbmirc.github.io/24hours/) et, si demandé, une copie dans un autre dossier.
Types de séquence et lieux : tables TYPES et LIEUX ci-dessous (couleurs, règles de rattachement)."""
import datetime as dt, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRES = {  # code : (famille, libellé, couleur) — code couleur décidé le 3/11/2026
    "ARCH_NUIT": ("blue", "Buildings at night", "#1d3557"), "ARCH_JOUR": ("blue", "Buildings by day", "#457b9d"), "ARCH_INT": ("blue", "Empty interiors", "#8ab6d6"),
    "NAT_VEG": ("green", "Plants & trees", "#2d6a4f"), "NAT_ANI": ("green", "Animals", "#6a994e"), "NAT_EAU": ("green", "Water, ice & sky up close", "#52b788"), "NAT_SON": ("green", "Sounds of nature", "#95d5b2"),
    "COL_ENS": ("red", "Teaching", "#9d0208"), "COL_REPAS": ("red", "Meals & kitchen", "#e63946"), "COL_SOIREE": ("red", "Evenings, music & dance", "#ef6351"),
    "COL_TRAVAIL": ("red", "Working together", "#6a040f"), "COL_VIE": ("red", "Shared life", "#c1121f"),
    "LARGE_NAT": ("yellow", "Wide view: nature", "#e9c46a"), "LARGE_BAT": ("yellow", "Wide view: buildings", "#d4a017"), "LARGE_FIG": ("yellow", "Figures in the landscape", "#f6e27f"),
    "DIAL": ("violet", "Dialogue", "#5a189a"), "DIAL_ECH": ("violet", "Brief exchanges & announcements", "#9d4edd"),
    "SEUL_LIRE": ("pink", "Alone, reading", "#ffc2d1"), "SEUL_ECRIRE": ("pink", "Alone, writing", "#ff8fab"), "SEUL_TRAV": ("pink", "Alone, working", "#fb6f92"),
}
FAMILLES = [("blue", "Architecture, no one in frame"), ("green", "Nature: animals & plants"), ("red", "Collective scenes: teaching, meals, games…"),
            ("yellow", "Wide views: nature, buildings, figures"), ("violet", "Dialogues"), ("pink", "One person reading, writing, working alone")]
TYPES = [  # (id, libellé, couleur dérivée du code couleur, fils du séquencier)
    ("night", "Night", "#1d3557", {"nuit"}),
    ("light", "Dawn & dusk", "#e9c46a", {"aube"}),
    ("waking", "Waking & lodges", "#c1121f", {"lodges"}),
    ("meal", "Meals & kitchen", "#e63946", {"repas", "cuisine", "magasin"}),
    ("farm", "Farm", "#6a994e", {"ferme"}),
    ("class", "Class", "#9d0208", {"cours", "theatre", "hansgirg", "danse"}),
    ("work", "Work program", "#6a040f", {"chaudieres", "entretien", "atelier", "linge"}),
    ("office", "Mail & office", "#9d4edd", {"courrier", "bureau", "bulletin"}),
    ("evening", "Evening program", "#ef6351", {"cole", "kazin", "disques"}),
    ("journey", "Journeys", "#d4a017", {"wunsch", "dreier"}),
    ("faculty", "Faculty at work", "#fb6f92", {"albers", "lowinsky", "bibliotheque"}),
    ("interlude", "Interlude", "#8ab6d6", {"liaison", "vie"}),
]
NCATS = {"montagnes": "Mountains", "ciel": "Sky & clouds", "astres": "Moon, stars & planets", "lumiere": "Light", "eau": "Lake & water",
         "givre": "Frost, ice & ground", "arbres": "Trees, leaves & wind", "oiseaux": "Birds", "betes": "Animals", "insectes": "Insects & spiders",
         "fumees": "Smoke", "sons": "Sounds"}
NCOUL = {"montagnes": "#d4a017", "ciel": "#52b788", "astres": "#2d6a4f", "lumiere": "#e9c46a", "eau": "#52b788", "givre": "#74c69d",
         "arbres": "#2d6a4f", "oiseaux": "#6a994e", "betes": "#6a994e", "insectes": "#90a955",
         "fumees": "#457b9d", "sons": "#95d5b2"}
LIEUX = [  # (id, libellé, couleur, motif sur le lieu en anglais) — le premier qui convient
    ("offcampus", "Off campus", "#8a8f98", r"brevard|station|road"),
    ("farm", "Farm", "#8a8f98", r"farm|milking|barn"),
    ("dining", "Dining Hall", "#8a8f98", r"dining|kitchen|pantry|porch|mail box"),
    ("roundhouse", "Round House", "#8a8f98", r"round house"),
    ("library", "Library, office & store", "#8a8f98", r"library|office|store"),
    ("studies", "Studies Building", "#8a8f98", r"studies|study|language room|faculty room|physics lab|weaving room"),
    ("northlodge", "North Lodge", "#8a8f98", r"north lodge"),
    ("southlodge", "South Lodge", "#8a8f98", r"south lodge"),
    ("cottages", "Cottages & studios", "#8a8f98", r"cottage|mountain stream|studio"),
    ("shops", "Shops & furnaces", "#8a8f98", r"woodshop|furnace|coal|buildings"),
    ("lake", "Lake & grounds", "#8a8f98", r"lake|campus"),
]


def K_mn(h):
    a, b = h.split(":"); return int(a) * 60 + int(b)


def src_en(s):
    """libellés français courants des références (le reste, titres et pages, est laissé tel quel)."""
    for a, b in (("connaissance générale du milieu", "general knowledge of the environment"), ("connaissance générale", "general knowledge"),
                 ("calcul ephem", "ephem calculation"), ("usage supposé", "assumed custom"), ("plan de liaison", "interlude"), ("calcul ephem", "ephem calculation"),
                 ("formation des aiguilles de glace", "formation of needle ice"), ("phénomène connu", "known phenomenon"), ("géométrie", "geometry"),
                 ("éclairage des cirrus", "lighting of the cirrus"), ("id.", "same sources")):
        s = s.replace(a, b)
    return re.sub(r"\s*\([^)]*[àâçéèêëîïôûùüœ][^)]*\)", "", s)


DEF_REG = {"class": "COL_ENS", "meal": "COL_REPAS", "office": "DIAL_ECH", "waking": "COL_VIE", "night": "ARCH_NUIT", "light": "LARGE_NAT",
           "farm": "NAT_ANI", "work": "COL_TRAVAIL", "evening": "COL_SOIREE", "journey": "LARGE_FIG", "faculty": "SEUL_TRAV", "interlude": "ARCH_JOUR"}
BATI = {"L2", "L3", "L3b", "L6", "L7", "S1", "S2"}


def registre_seq(o):
    return o.get("registre") or DEF_REG.get(type_de(o), "COL_VIE")


def registre_plan(cat, e, mid="", texte=""):
    """plan de nature : vue large → jaune ; bâtiment (fenêtres, fumées de cheminée) → bleu ; sinon vert selon le sujet."""
    large = e in ("TPE", "PE", "PL")
    if mid.startswith("N2"): return "COL_REPAS"                       # gong des repas : appel collectif
    if mid == "L5": return "LARGE_FIG"
    bati = mid in BATI or cat == "fumees" or (not mid and re.search(r"window|chimney|furnace", texte, re.I))
    if large: return "LARGE_BAT" if bati else "LARGE_NAT"
    if bati: return "ARCH_NUIT" if re.search(r"night|dark|lamp|lit ", texte, re.I) else "ARCH_JOUR"
    return {"arbres": "NAT_VEG", "betes": "NAT_ANI", "oiseaux": "NAT_ANI", "insectes": "NAT_ANI", "sons": "NAT_SON"}.get(cat, "NAT_EAU")


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
            "why": o.get("m_en", ""), "src": o["src"], "mo": o["moment"], "r": registre_seq(o)} for o in S]
    heures = []
    era = {x["heure"][:2]: x for x in J["meteo"]["era5_par_heure"]}
    for x in J["lumiere"]["par_heure"]:
        w = era.get(x["heure"][:2], {})
        heures.append({"h": x["heure"], "sun": x["soleil_hauteur"], "moon": x["lune_hauteur"], "light": x["etat"],
                       "temp": w.get("temp_c"), "sky": w.get("temps", ""), "cloud": w.get("nuages_pct"), "wind": w.get("vent_kmh")})
    pn = os.path.join(dos, "plans_nature_montage.json")
    PN = json.load(open(pn, encoding="utf-8")) if os.path.exists(pn) else []
    nature = [{"s": p["sequence"], "h": p["heure"], "pg": p["page"], "d": p["duree_s"], "c": p["cat"], "sc": p["echelle_en"], "x": p["en"],
               "snd": p["son"].split(" / ")[-1] if p["son"] else "", "pct": p["pct"], "src": src_en(p["src"]), "why": p["raison"], "r": registre_plan(p["cat"], p["e"], p["id"], p["en"])} for p in PN]
    # heures découpées plan par plan (à la main, ou générées pour la nuit) : elles remplacent les plans automatiques de leurs fenêtres
    vocab_en = {}
    for fn in sorted(f for f in os.listdir(dos) if f.endswith("_plan_par_plan.json")):
        H = json.load(open(os.path.join(dos, fn), encoding="utf-8")); V = H["vocabulaire"]
        sec = lambda tc: sum(int(v) * k for v, k in zip(tc.split(":"), (3600, 60, 1)))
        wins = [(sec(m["de"]), sec(m["a"])) for m in H["mouvements"]]
        nature = [n for n in nature if not any(a0 <= sec(n["h"]) < a1 for a0, a1 in wins)]
        def porteuse(t):
            m = t // 60
            return next(o["n"] for o in S if K_mn(o["debut"]) <= m < (K_mn(o["fin"]) if o["fin"] != "24:00" else 1440))
        deja = set()
        if H.get("compact"):             # découpage généré (nuit lente) : codes, vocabulaire transmis une fois
            for k, champ in (("e", "echelle"), ("a", "angle"), ("mv", "mouvement"), ("o", "optique"), ("p", "point"), ("r", "raccord")):
                vocab_en.setdefault(k, {}).update({c: v[1] for c, v in V[champ].items()})
            for x in H["plans"]:
                t = sec(x["tc"]); mv = next(m for m in H["mouvements"] if sec(m["de"]) <= t < sec(m["a"]))
                it = {"s": porteuse(t), "h": x["tc"], "d": x["d"], "c": x["cat"], "r": x.get("reg") or registre_plan(x["cat"], x["e"], "", x["en"]), "x": x["en"],
                      "k": [x["e"], x["a"], x["mv"], x["o"], x["p"], x["r"]], "pct": x["pct"], "cp": 1}
                if mv["de"] not in deja: it["mvt"] = mv["en"]; deja.add(mv["de"])
                nature.append(it)
            nature.sort(key=lambda n: n["h"]); continue
        for x in H["plans"]:
            t = sec(x["tc"]); mv = next(m for m in H["mouvements"] if sec(m["de"]) <= t < sec(m["a"]))
            item = {"s": porteuse(t), "h": x["tc"], "pg": t // 60 + 1, "d": x["d"], "c": x["cat"], "sc": V["echelle"][x["e"]][1], "x": x["en"],
                    "snd": x.get("son_en", ""), "pct": x["pct"], "src": src_en(x["src"]), "why": "",
                    "tech": [V["angle"][x["a"]][1], V["mouvement"][x["mv"]][1], V["optique"][x["o"]][1], V["point"][x["p"]][1]], "rc": V["raccord"][x["r"]][1],
                    "r": registre_plan(x["cat"], x["e"], "", x["en"])}
            if mv["de"] not in deja: item["mvt"] = mv["en"]; deja.add(mv["de"])
            nature.append(item)
        nature.sort(key=lambda n: n["h"])
    LU = J["lumiere"]
    noaa = J["meteo"]["noaa"]; mt = noaa.get("Montreat", {}).get(jour) or {}
    pr = os.path.join(dos, "rythme.json")
    blocs = [{"de": b["de"], "a": b["a"], "id": b["id"], "t": b["en"], "tempo": {"lent": "slow", "moyen": "medium", "vif": "brisk", "lent à moyen": "slow to medium"}.get(b["tempo"], b["tempo"]),
              "ps": b["plans_s"], "res": [x["en"] for x in b["reserve"]], "n": b.get("notes_en", "")} for b in json.load(open(pr, encoding="utf-8"))["blocs"]] if os.path.exists(pr) else []
    data = {"blocs": blocs, "voc": vocab_en, "reg": [{"id": k, "fam": f, "label": l, "color": c} for k, (f, l, c) in REGISTRES.items()], "fams": [{"id": f, "label": l} for f, l in FAMILLES],
            "seq": seq, "nature": nature, "ncats": [{"id": k, "label": v, "color": NCOUL[k]} for k, v in NCATS.items()], "hours": heures, "types": [{"id": t, "label": l, "color": c} for t, l, c, _ in TYPES],
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
<meta name="description" content="Monday, December 4, 1944, at Black Mountain College, minute by minute: __N__ sequences and nature shots, 1,440 pages (one page per minute), each with its sources and its deduced share.">
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
.rail button{flex:1;height:22px;border:1px solid var(--line);border-radius:3px;cursor:pointer;font:500 9px Inter,sans-serif;color:var(--ink);background:var(--paper);padding:0}
.hour .skyd{display:inline-block;width:12px;height:12px;border-radius:50%;vertical-align:-1px;margin-right:4px;border:1px solid rgba(255,255,255,.5)}
.rail button:hover{opacity:1;outline:2px solid var(--ink)}
.filters{max-width:980px;margin:0 auto;padding:10px 16px 0;font:500 12px Inter,system-ui,sans-serif}
.filters .row{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:6px 0}
.filters .lab{color:var(--soft);min-width:70px;text-transform:uppercase;letter-spacing:.06em;font-size:11px}
.chip{display:inline-flex;align-items:center;gap:6px;border-radius:999px;padding:3px 10px;font:600 12px Inter,system-ui,sans-serif;border:1.5px solid var(--c);color:var(--ink);background:var(--paper);cursor:pointer;white-space:nowrap}
.chip i{width:9px;height:9px;border-radius:50%;background:var(--c);display:inline-block}
.chip.type{background:var(--paper);border-color:var(--c);color:var(--ink)}
.chip.type i{border-radius:2px}
.chip.reg{background:var(--c);color:var(--fg,#fff);border-color:var(--c)}
.legend-fam{display:grid;grid-template-columns:290px 1fr;gap:6px 10px;align-items:center;margin:5px 0}
.legend-fam .sh{display:flex;flex-wrap:wrap;gap:6px}
@media (max-width:700px){.legend-fam{grid-template-columns:1fr}}
.legend-fam .fl{font:700 11px Inter,sans-serif;cursor:pointer;color:var(--ink)}
.legend-fam .fl i{display:inline-block;width:24px;height:10px;border-radius:3px;margin-right:6px;vertical-align:0;background:var(--c)}
.chip.off{opacity:.35}
.reset{border:0;background:none;color:var(--soft);text-decoration:underline;cursor:pointer;font:inherit}
main{max-width:980px;margin:0 auto;padding:8px 16px 80px}
.hour{position:relative;margin:28px 0 10px;border-radius:12px;padding:14px 16px;color:var(--bg);background:var(--ink);font:500 13px/1.4 Inter,system-ui,sans-serif;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:baseline}
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
.ded{font-weight:700;border-radius:6px;padding:1px 7px;white-space:nowrap;border:1.5px solid var(--ink)}
.ded.attested{background:var(--ink);color:var(--bg)}.ded.transposed{background:var(--paper);color:var(--ink)}.ded.assumed{background:var(--paper);color:var(--soft);border-style:dashed;border-color:var(--soft)}
details{margin-top:6px;font:400 12px/1.45 Inter,system-ui,sans-serif;color:var(--soft)}
summary{cursor:pointer}
.legend{font:500 12px/1.5 Inter,system-ui,sans-serif;color:var(--soft);max-width:760px}
#sentinel{height:60px}
.nat{display:grid;grid-template-columns:96px 1fr;gap:0 16px;margin:4px 0 4px 18px;padding:6px 12px;border-radius:8px;background:color-mix(in srgb,var(--nc) 12%,var(--bg));border:1px dashed color-mix(in srgb,var(--nc) 55%,transparent);font:400 13px/1.4 Inter,system-ui,sans-serif}
.nat .nt{font:700 12px "Courier Prime",monospace;color:var(--soft)}
.nat .nk{display:inline-block;font:700 10px/1 Inter,sans-serif;text-transform:uppercase;letter-spacing:.06em;color:#fff;background:var(--nc);border-radius:4px;padding:3px 6px;margin-right:6px}
.nat .ns{color:var(--soft);font-size:11px}
.nat.hid{display:none}
.nat .tech{display:flex;flex-wrap:wrap;gap:4px;margin-top:4px}
.nat .tech span{font:600 10px/1.2 Inter,sans-serif;border:1px solid color-mix(in srgb,var(--nc) 60%,transparent);border-radius:4px;padding:2px 5px;color:var(--ink);background:var(--paper)}
.nat .tech span.rc{border-style:dashed;color:var(--soft)}
.film{margin:4px 0 8px 18px;padding:8px 10px;border:1px dashed var(--line);border-radius:8px;background:var(--paper);font:500 12px/1.4 Inter,system-ui,sans-serif;color:var(--soft);cursor:pointer}
.film .strip{display:flex;gap:1px;height:22px;margin-top:6px;border-radius:3px;overflow:hidden}
.film .strip i{display:block;height:100%;min-width:2px}
.film ol{margin:8px 0 0;padding-left:0;list-style:none;max-height:420px;overflow:auto;color:var(--ink)}
.film li{display:grid;grid-template-columns:70px 40px 1fr;gap:8px;padding:3px 0;border-top:1px solid var(--line)}
.film li b{font:700 11px "Courier Prime",monospace}
.film li span.k{color:var(--soft);font-size:11px}
.film li i.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}
.bloc{margin:26px 0 8px;padding:12px 16px;border-left:4px solid var(--ink);background:var(--paper);border-radius:6px;font:500 13px/1.5 Inter,system-ui,sans-serif}
.bloc b{display:block;font:700 12px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--soft)}
.bloc .bt{font:600 17px "Source Serif 4",Georgia,serif;color:var(--ink)}
.mvt{margin:14px 0 6px 18px;padding:10px 14px;border-radius:8px;background:var(--ink);color:var(--bg);font:500 13px/1.45 Inter,system-ui,sans-serif}
.mvt b{font:700 12px Inter,sans-serif;letter-spacing:.08em;text-transform:uppercase;display:block;margin-bottom:2px;opacity:.7}
.chip.nat-c{background:var(--paper);border-style:dashed}
@media (max-width:600px){.nat{grid-template-columns:64px 1fr;margin-left:8px}}
footer{max-width:980px;margin:0 auto;padding:30px 16px 60px;font:400 13px/1.6 Inter,system-ui,sans-serif;color:var(--soft)}
@media (max-width:600px){.seq{grid-template-columns:64px 1fr;gap:0 10px}.t{font-size:13px}.hour b{font-size:22px}}
</style>
</head>
<body>
<header class="top">
  <h1>24 Hours at Black Mountain College</h1>
  <p class="sub">Monday, December 4, 1944 · Lake Eden, Black Mountain, North Carolina · a day in real time</p>
  <p class="intro">One page per minute: 1,440 pages from midnight to midnight, cut into <b>__N__ sequences</b>. When several things happen at once, the film cuts between them; each class keeps a quarter of its own time on screen, so that four classes held at the same hour can all be seen. Between the sequences, <b>nature shots</b> (mountains, sky, stars, frost, trees and wind, birds, animals, insects, sounds of the valley) set the rhythm of the cut: each one shows nature at that very minute and borrows a few seconds from the sequence in progress, so the clock never stops. <b>Colors say what the shot shows</b>: blue, architecture with no one in frame; green, nature (animals and plants); red, collective scenes (teaching, meals, evenings, work); yellow, wide views of nature, buildings, and figures; violet, dialogues; pink, one person reading, writing, or working alone; sequence types take their color from the same palette. Every sequence keeps its sources and its <b>deduced share</b>: <span class="ded attested">≤ 10%</span> attested by a dated document, <span class="ded transposed">11–40%</span> an attested custom carried over to this day, <span class="ded assumed">&gt; 40%</span> assumed, to be confirmed.</p>
  <div class="facts" id="facts"></div>
</header>
<div class="bar"><div class="in">
  <span class="clock" id="clock">00:00</span><span class="now" id="now">page 1 · night</span>
  <div class="rail" id="rail" aria-label="Jump to an hour"></div>
</div></div>
<div class="filters">
  <div class="row" style="display:block"><span class="lab">Color code</span><div id="fregs"></div></div>
  <div class="row"><span class="lab">Sequence</span><span id="ftypes"></span></div>
  <div class="row"><span class="lab">Place</span><span id="fplaces"></span></div>
  <div class="row"><span class="lab">Nature</span><span id="fnature"></span> <button class="reset" id="nonat">hide nature shots</button> <button class="reset" id="reset">show all</button></div>
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
const T = Object.fromEntries(D.types.map(x => [x.id, x])), P = Object.fromEntries(D.places.map(x => [x.id, x])), R = Object.fromEntries(D.reg.map(x => [x.id, x]));
const fg = c => { const n = parseInt(c.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255; return (0.299*r + 0.587*g + 0.114*b) > 150 ? "#1f1d1a" : "#ffffff"; };
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
f.insertAdjacentHTML("beforeend", `<span>${D.seq.length} sequences · ${D.nature.length} nature shots</span>${D.nature.some(n => n.mvt) ? `<span><a href="#h07" onclick="jump('07');return false">The dawn hour, shot by shot (7:20–8:20)</a></span>` : ""}${D.nature.some(n => n.cp) ? `<span><a href="#h00" onclick="jump('00');return false">The slow night: ${D.nature.filter(n => n.cp).length} shots of 3–8 s</a></span>` : ""}<span>Waning moon, ${D.moon_pct}% lit</span><span>Montreat: ${D.noaa.min} °C to ${D.noaa.max} °C (${D.noaa.minf}–${D.noaa.maxf} °F), dry</span><span>Eastern War Time (UTC−4)</span>`);
// rail
const rail = document.getElementById("rail");
D.hours.forEach(h => { const b = document.createElement("button"); b.textContent = h.h.slice(0,2); b.title = `${h.h} · ${lightEn[h.light]||h.light}`;
  b.onclick = () => jump(h.h.slice(0,2)); rail.appendChild(b); });
// filters
const on = {t: new Set(D.types.map(x => x.id)), l: new Set(D.places.map(x => x.id))};
const count = (k, id) => D.seq.filter(s => s[k] === id).reduce((a, s) => a + s.m, 0);
function chips(id, list, key, cls) { const el = document.getElementById(id);
  list.forEach(x => { const n = count(key, x.id); if (!n) return; const c = document.createElement("span"); c.className = `chip ${cls}`; c.style.setProperty("--c", x.color);
    c.innerHTML = "<i></i>" + `${esc(x.label)} <small style="opacity:.75">${n}</small>`; c.title = `${n} pages`;
    c.onclick = () => { const s = on[key]; if (s.size === list.length) { s.clear(); s.add(x.id); } else if (s.has(x.id)) { s.delete(x.id); if (!s.size) list.forEach(y => s.add(y.id)); } else s.add(x.id);
      el.querySelectorAll(".chip").forEach((e, i) => {}); refresh(); };
    c.dataset.id = x.id; el.appendChild(c); }); }
chips("ftypes", D.types, "t", "type"); chips("fplaces", D.places, "l", "place");
const onR = new Set(D.reg.map(x => x.id));
(() => { const el = document.getElementById("fregs");
  D.fams.forEach(f => { const regs = D.reg.filter(r => r.fam === f.id), row = document.createElement("div"); row.className = "legend-fam";
    const fl = document.createElement("span"); fl.className = "fl"; fl.style.setProperty("--c", regs[Math.floor(regs.length / 2)].color); fl.innerHTML = `<i></i>${esc(f.label)}`;
    fl.onclick = () => { const all = regs.every(r => onR.has(r.id)) && onR.size === regs.length; onR.clear(); (all ? D.reg : regs).forEach(r => onR.add(r.id)); refresh(); };
    row.appendChild(fl); const sh = document.createElement("span"); sh.className = "sh"; row.appendChild(sh);
    regs.forEach(r => { const n = D.seq.filter(x => x.r === r.id).reduce((a, x) => a + x.m, 0), k = D.nature.filter(x => x.r === r.id).length;
      const c = document.createElement("span"); c.className = "chip reg"; c.style.setProperty("--c", r.color); c.style.setProperty("--fg", fg(r.color)); c.dataset.id = r.id;
      c.innerHTML = `${esc(r.label)} <small style="opacity:.8">${n ? n + " p." : ""}${n && k ? " · " : ""}${k ? k + " shots" : ""}</small>`;
      c.onclick = () => { if (onR.size === D.reg.length) { onR.clear(); onR.add(r.id); } else if (onR.has(r.id)) { onR.delete(r.id); if (!onR.size) D.reg.forEach(y => onR.add(y.id)); } else onR.add(r.id); refresh(); };
      sh.appendChild(c); });
    el.appendChild(row); }); })();
const NC = Object.fromEntries(D.ncats.map(x => [x.id, x])), onN = new Set(D.ncats.map(x => x.id)); let showN = true;
const byS = {}; D.nature.forEach(n => (byS[n.s] ||= []).push(n));
(() => { const el = document.getElementById("fnature");
  D.ncats.forEach(x => { const n = D.nature.filter(y => y.c === x.id).length; if (!n) return; const c = document.createElement("span"); c.className = "chip nat-c"; c.style.setProperty("--c", x.color);
    c.innerHTML = `<i></i>${esc(x.label)} <small style="opacity:.75">${n}</small>`; c.dataset.id = x.id; c.title = `${n} shots`;
    c.onclick = () => { if (onN.size === D.ncats.length) { onN.clear(); onN.add(x.id); } else if (onN.has(x.id)) { onN.delete(x.id); if (!onN.size) D.ncats.forEach(y => onN.add(y.id)); } else onN.add(x.id); showN = true; refresh(); };
    el.appendChild(c); }); })();
document.getElementById("nonat").onclick = () => { showN = !showN; refresh(); };
document.getElementById("reset").onclick = () => { D.types.forEach(x => on.t.add(x.id)); D.places.forEach(x => on.l.add(x.id)); D.ncats.forEach(x => onN.add(x.id)); D.reg.forEach(x => onR.add(x.id)); showN = true; refresh(); };
function refresh() {
  document.querySelectorAll("#ftypes .chip").forEach(c => c.classList.toggle("off", !on.t.has(c.dataset.id)));
  document.querySelectorAll("#fplaces .chip").forEach(c => c.classList.toggle("off", !on.l.has(c.dataset.id)));
  document.querySelectorAll("#fregs .chip").forEach(c => c.classList.toggle("off", !onR.has(c.dataset.id)));
  document.querySelectorAll(".seq").forEach(e => e.classList.toggle("dim", !(on.t.has(e.dataset.t) && on.l.has(e.dataset.l) && onR.has(e.dataset.r))));
  document.querySelectorAll("#fnature .chip").forEach(c => c.classList.toggle("off", !showN || !onN.has(c.dataset.id)));
  document.getElementById("nonat").textContent = showN ? "hide nature shots" : "show nature shots";
  document.querySelectorAll(".nat").forEach(e => e.classList.toggle("hid", !showN || !onN.has(e.dataset.c) || !onR.has(e.dataset.r))); }
function natCard(n) { const c = NC[n.c], rg = R[n.r] || {color: c.color, label: ""};
  const head = n.mvt ? `<div class="mvt nat-m"><b>The dawn hour, shot by shot</b>${esc(n.mvt)}</div>` : "";
  const tech = n.tech ? `<div class="tech">${n.tech.map(t => `<span>${esc(t)}</span>`).join("")}<span class="rc">→ ${esc(n.rc)}</span></div>` : "";
  return head + `<div class="nat" data-c="${n.c}" data-r="${n.r}" style="--nc:${rg.color}" title="${esc(rg.label)}"><div class="nt">${n.h}<br><span class="ns">${n.d} s · p. ${n.pg}</span></div>
    <div><span class="nk" style="color:${fg(rg.color)}">${esc(c.label)}</span><b>${esc(n.sc)}</b> — ${esc(n.x)}${n.snd ? ` <span class="ns">♪ ${esc(n.snd)}</span>` : ""}
    <span class="ns"> · ${n.pct}% deduced · ${esc(n.src)}</span>${tech}</div></div>`; }
// infinite list
const list = document.getElementById("list"); let i = 0, lastHour = null; const BATCH = 25;
function card(s) {
  const t = T[s.t], p = P[s.l], r = R[s.r], cls = s.st === "attested" ? "attested" : s.st === "assumed" ? "assumed" : "transposed";
  return `<article class="seq" id="s${s.n}" data-t="${s.t}" data-l="${s.l}" data-r="${s.r}" data-a="${s.a}" style="--tc:${r.color};--m:${s.m}">
    <div><div class="t">${s.a}<small>${s.m} min · p. ${s.p}</small><small>#${s.n}</small></div><div class="dur"></div></div>
    <div><p class="head">${esc(s.h)}</p>
      <div class="tags"><span class="chip reg" style="--c:${r.color};--fg:${fg(r.color)}">${esc(r.label)}</span>${t.label !== r.label ? `<span class="chip type" style="--c:${t.color}"><i></i>${esc(t.label)}</span>` : ""}<span class="chip" style="--c:#8a8f98">${esc(p.label)}</span></div>
      <p class="x">${esc(s.x)}</p>
      ${s.q && s.q.length ? `<p class="who">${esc(s.q.join(", "))}</p>` : ""}
      <div class="meta"><span class="ded ${cls}">${s.pct}% deduced</span><span>${esc(s.st)}</span><span>${s.a}–${s.b}</span></div>
      <details><summary>Sources</summary>${esc(s.src)}${s.why ? `<br><i>Why this share:</i> ${esc(s.why)}` : ""}</details></div></article>`; }
function hourBand(hh) { const h = D.hours[+hh];
  return `<div class="hour" id="h${hh}"><b>${hh}:00</b><span><i class="skyd" style="background:${sky(h)}"></i>sky</span><span>pages ${+hh*60+1}–${+hh*60+60}</span><span>${lightEn[h.light]||h.light}</span>
    <span>${skyEn[h.sky]||h.sky}, ${h.temp} °C</span><span>sun ${h.sun}°</span><span>moon ${h.moon}°</span>${h.wind!=null?`<span>wind ${h.wind} km/h</span>`:""}</div>`; }
function filmCard(list) {
  const tot = list.reduce((a, x) => a + x.d, 0), head = list.find(x => x.mvt);
  const blocks = list.map(x => `<i style="flex:${x.d};background:${(R[x.r] || {}).color || "#888"}" title="${x.h} · ${esc((D.voc.e || {})[x.k[0]] || "")} · ${esc(x.x)}"></i>`).join("");
  return (head ? `<div class="mvt"><b>The slow night, shot by shot</b>${esc(head.mvt)}</div>` : "") +
    `<div class="film" data-n="${list.length}">${list.length} night shots · ${Math.floor(tot / 60)} min ${String(tot % 60).padStart(2, "0")} s · ${list[0].h}–${list[list.length - 1].h} — click to list them<div class="strip">${blocks}</div></div>`; }
function filmList(el, list) {
  if (el.querySelector("ol")) { el.querySelector("ol").remove(); return; }
  const V = D.voc, ol = document.createElement("ol");
  ol.innerHTML = list.map(x => `<li><b>${x.h}</b><span>${x.d} s</span><span><i class="sw" style="background:${(R[x.r] || {}).color}"></i>${esc(x.x)}<br><span class="k">${[V.e[x.k[0]], V.a[x.k[1]], V.mv[x.k[2]], V.o[x.k[3]], V.p[x.k[4]], "→ " + V.r[x.k[5]]].map(esc).join(" · ")} · ${x.pct}% deduced</span></span></li>`).join("");
  el.appendChild(ol); }
const filmsByS = {}; let nb = 0;
function blocBanner(b) { return `<div class="bloc"><b>Block ${b.id} · ${b.de}–${b.a} · ${esc(b.tempo)} · shots ${b.ps[0]}–${b.ps[1]} s (avg ${b.ps[2]} s)</b><span class="bt">${esc(b.t)}</span>${b.n ? `<br>${esc(b.n)}` : ""}${b.res.length ? `<br>Reserved for later: ${b.res.map(esc).join("; ")}` : ""}</div>`; }
function more(until) {
  let n = 0; while (i < D.seq.length && (n < BATCH || (until && D.seq[i].a.slice(0,2) <= until))) { const s = D.seq[i++], hh = s.a.slice(0,2);
    if (hh !== lastHour) { for (let k = lastHour == null ? 0 : +lastHour + 1; k <= +hh; k++) list.insertAdjacentHTML("beforeend", hourBand(String(k).padStart(2,"0"))); lastHour = hh; }
    while (nb < D.blocs.length && D.blocs[nb].de <= s.a) list.insertAdjacentHTML("beforeend", blocBanner(D.blocs[nb++]));
    list.insertAdjacentHTML("beforeend", card(s));
    const nat = byS[s.n] || [], cp = nat.filter(x => x.cp), dt = nat.filter(x => !x.cp);
    dt.forEach(x => list.insertAdjacentHTML("beforeend", natCard(x)));
    if (cp.length) { list.insertAdjacentHTML("beforeend", filmCard(cp)); const el = list.lastElementChild; el.onclick = e => { if (e.target.closest("ol")) return; filmList(el, cp); }; }
    n++; }
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
