"""Séquencier d'une journée en temps réel : les 1 440 minutes (1 minute = 1 page) découpées en scènes, sans trou.

Usage : python3 scripts/sequencier.py AAAA-MM-JJ <clone de RBMIRC/week>
Entrées : journees/AAAA-MM-JJ/scenes_cles.json (scènes écrites à la main, avec source et part déduite),
journees/AAAA-MM-JJ/journee.json (scripts/journee.py : lumière, météo, cours et inscrits) et le planning du jour
(semainier public). Sorties : 10_sequencier.md, sequencier.csv, sequencier.json.

Méthode (chaque cours ne garde à l'écran que 25 % de sa durée, QUOTA_COURS : quatre cours simultanés tiennent ensemble dans le temps réel) :
  1. activités = scènes clés + activités du planning (documents du collège, reconstitution) qu'aucune scène clé ne
     remplace ; heure de fin manquante : 45 min pour un repas, 60 pour une causerie, 30 sinon ; salle d'un cours non
     donnée : celle du même enseignant à l'hiver 1945 (+10 %) ;
  2. la journée est coupée à chaque début et fin d'activité ; dans chaque tranche, le temps est partagé entre les
     activités en cours selon leur poids (scène clé 3, document du collège 2, cours 1,5, reconstitution 0,6), puis
     découpé en scènes de 4 minutes au plus le jour et 12 la nuit, en alternant (montage parallèle) ;
  3. minutes sans activité : plans de liaison choisis selon l'heure (part déduite 55 %).
Chaque scène garde la part déduite de son activité (la plus forte si elle en réunit plusieurs) et ses sources."""
import collections, csv, datetime as dt, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K

ROOT = K.ROOT
POIDS = {"cle": 3.0, "aam": 2.0, "cours": 1.5, "spc": 0.6}
MOMENT_EN = {"NUIT": "NIGHT", "AUBE": "DAWN", "JOUR": "DAY", "CRÉPUSCULE": "DUSK"}
QUOTA_COURS = 0.25        # part du temps de cours gardée à l'écran (décision du 2/11/2026)
COURS_FILS = {"theatre", "hansgirg", "danse"}      # scènes clés qui sont des cours


def mn(h): return K.mn(h)
def hm(m): return K.hm(min(m, 1439)) if m < 1440 else "24:00"


def main(jour, week):
    d = dt.date.fromisoformat(jour); dos = os.path.join(ROOT, "journees", jour)
    SC = json.load(open(os.path.join(dos, "scenes_cles.json"), encoding="utf-8"))
    JJ = json.load(open(os.path.join(dos, "journee.json"), encoding="utf-8"))
    D, C, Sc, P, Sy = K.charger(week); J, A = K.indexer(D, C, Sc); E = J.get(d, [])
    lum = {x["heure"][:2]: x for x in JJ["lumiere"]["par_heure"]}
    met = {x["heure"][:2]: x for x in JJ["meteo"]["era5_par_heure"]}
    inscrits = {(c["heure"], c["titre"]): c["inscrits_bmc_yearbook"] for c in JJ["cours"]}
    salles = SC["salles_hiver_1945"]
    EN = K.ld(os.path.join(week, "data_en.js")).get("revu", {}) if os.path.exists(os.path.join(week, "data_en.js")) else {}
    SALLES_EN = dict(SC.get("salles_hiver_1945_en", {}), **{"Studies Building (salle non donnée)": "Studies Building (room not given)"})

    acts = []
    for k, s in enumerate(SC["scenes"]):
        acts.append({"id": f"K{k + 1}", "a": mn(s["h"]), "b": mn(s["f"]) + (1 if s["f"] == "23:59" else 0), "titre": s["t"], "lieu": s["lieu"], "ie": s["ie"],
                     "qui": s["qui"], "src": s["src"], "pct": s["pct"], "m": s.get("m", ""), "fil": s["fil"], "poids": POIDS["cle"], "type": "scène clé",
                     "titre_en": s.get("t_en", s["t"]), "lieu_en": s.get("lieu_en", s["lieu"]), "m_en": s.get("m_en", ""), "registre": s.get("registre", "")})
    cles = [(a, s) for a, s in zip(acts, SC["scenes"]) if s.get("remplace")]
    for e in E:
        if not e["h"] or e.get("semaine") or e["couche"] not in ("aam", "spc") or e["hors"]: continue
        a = mn(e["h"]); b = mn(e["f"]) if e["f"] else None
        if b is None or b <= a: b = a + (45 if e["type"] == "social" else 60 if e["type"] == "conference" else 30)
        if any(re.search(s["remplace"], e["titre"], re.I) and x["a"] < b and a < x["b"] for x, s in cles): continue
        lieu, pct, note = e["lieu"], e["pct"], ""
        if not lieu and e["type"] in ("cours", "atelier"):
            for cle, salle in salles.items():
                if cle.startswith("_"): continue
                if all(re.search(p, e["qui"] + " " + e["titre"], re.I) for p in cle.split("|")):
                    lieu, pct, note = salle, min(90, pct + 10), "salle du même cours à l'hiver 1945 (+10)"; break
        cours = e["type"] in ("cours", "atelier")
        qui = [q.strip() for q in re.split(r";", e["qui"]) if q.strip()]
        lieu_f = lieu or ("Studies Building (salle non donnée)" if cours else "")
        en_extra = {"titre_en": EN.get(e["titre"], e["titre"]), "lieu_en": SALLES_EN.get(lieu_f, EN.get(lieu_f, lieu_f)),
                    "m_en": "room of the same class in winter 1945 (+10)" if note else ""}
        ins = inscrits.get((e["h"], e["titre"]), [])
        acts.append({"id": f"P{len(acts)}", "a": a, "b": min(b, 1440), "titre": e["titre"], "lieu": lieu or ("Studies Building (salle non donnée)" if cours else ""),
                     "ie": "EXT" if re.search(r"porch|véranda|ferme|lac", lieu or "", re.I) else "INT", "qui": qui, "inscrits": ins, "src": e["src"], "pct": pct, "m": note,
                     "fil": "cours" if cours else "repas" if e["type"] == "social" else "vie", "poids": POIDS["cours"] if cours else POIDS["aam"] if e["couche"] == "aam" else POIDS["spc"], **en_extra,
                     "type": ("cours" if cours else "activité") + (" (reconstitution)" if e["couche"] == "spc" else " (document du collège)")})

    # tranches ; chaque cours ne garde à l'écran que QUOTA_COURS de sa durée : plusieurs cours ou activités tiennent dans le même temps
    def cours_(x): return x["type"].startswith("cours") or x["fil"] in COURS_FILS
    def partager(act, L):
        if not act or L <= 0: return []
        act = sorted(act, key=lambda x: (-x["poids"], x["pct"], x["a"]))[:max(1, L // 2)]   # deux minutes au moins par plan
        tot = sum(x["poids"] for x in act)
        part = [max(2 if L >= 2 else 1, int(L * x["poids"] / tot)) for x in act]
        while sum(part) > L: part[part.index(max(part))] -= 1
        k = 0
        while sum(part) < L: part[k % len(part)] += 1; k += 1
        return list(zip(act, part))
    union = set()
    for x in acts:
        if cours_(x): union |= set(range(x["a"], x["b"]))
    cuts = sorted({0, 1440} | {x["a"] for x in acts} | {x["b"] for x in acts})
    pieces = []; report = collections.defaultdict(float)
    for t0, t1 in zip(cuts, cuts[1:]):
        if t1 <= t0: continue
        act = [x for x in acts if x["a"] < t1 and t0 < x["b"]]
        nuit = t0 < 7 * 60 or t0 >= 23 * 60
        L = t1 - t0
        if not act:
            pieces.append((t0, t1, None)); continue
        co = [x for x in act if cours_(x)]; au = [x for x in act if not cours_(x)]
        if co:
            # chaque cours garde QUOTA_COURS de sa propre durée : quatre cours en même temps se partagent tout le temps
            m = {}
            for x in co:
                v = max(0, round(QUOTA_COURS * L + report[x["id"]])); m[x["id"]] = v; report[x["id"]] += QUOTA_COURS * L - v
            while sum(m.values()) > L:
                k = max(m, key=m.get); m[k] -= 1; report[k] += 1
            parts = [(x, m[x["id"]]) for x in co if m[x["id"]]]
            c = sum(m.values())
            parts += partager(au, L - c) if au else [(None, L - c)] if L - c else []
        else:
            parts = partager(au, L)
        maxi = 12 if nuit else 4
        files = [(x, collections.deque([maxi] * (p // maxi) + ([p % maxi] if p % maxi else []))) for x, p in parts if p]
        t = t0
        while any(f for _, f in files):
            for x, f in files:
                if f: n = f.popleft(); pieces.append((t, t + n, x)); t += n
    # liaisons et fusion des morceaux contigus d'une même activité
    scenes = []
    for t0, t1, x in pieces:
        if scenes and scenes[-1]["x"] is x and scenes[-1]["b"] == t0 and (x is not None):
            scenes[-1]["b"] = t1; continue
        if x is None:
            t = t0
            while t < t1:
                n = min(t1 - t, 12 if t < 420 or t >= 1380 else 5); scenes.append({"a": t, "b": t + n, "x": None}); t += n
        else: scenes.append({"a": t0, "b": t1, "x": x})
    vus = collections.Counter(); out = []
    pool = SC["liaison"]; k_l = collections.Counter()
    for i, s in enumerate(scenes, 1):
        h = f"{s['a'] // 60:02d}"; l = lum.get(h, {}); w = met.get(h, {})
        etat = l.get("etat", "")
        LU = JJ["lumiere"]; t_ = lambda k: mn(LU[k])
        moment = ("NUIT" if s["a"] < t_("aube_nautique") else "AUBE" if s["a"] < t_("lever_soleil") else "JOUR" if s["a"] < t_("coucher_soleil")
                  else "CRÉPUSCULE" if s["a"] < t_("crepuscule_nautique") else "NUIT")
        meteo = f"{w.get('temps', '')}, {w.get('temp_c', '')} °C" if w else ""
        x = s["x"]
        if x is None:
            per = "nuit" if s["a"] < 420 or s["a"] >= 1260 else "matin" if s["a"] < 540 else "jour" if s["a"] < 1020 else "soir"
            txt = pool[per][k_l[per] % len(pool[per])]; k_l[per] += 1
            rec = {"lieu": "Le campus", "ie": "EXT", "qui": [], "action": txt + f" ({meteo} ; lumière : {etat})", "src": "plan de liaison (02_lumiere.md, 01_meteo.md, 03_lieux.md)",
                   "pct": 55, "m": "aucune activité attestée à cette minute", "fil": "liaison", "type": "liaison",
                   "lieu_en": "The campus", "action_en": f"Interlude on the campus ({meteo}; light: {etat})", "m_en": "no attested activity at this minute"}
        else:
            vus[x["id"]] += 1
            qui = list(x["qui"]) + [n + " (inscrit)" for n in x.get("inscrits", [])[:6]]
            ici = f" — {hm(s['a'])} : {w.get('temp_c', '')} °C, {w.get('temps', '')}, lune à {l.get('lune_hauteur', '')}°" if x["fil"] in ("nuit", "ferme", "chaudieres", "aube", "wunsch", "lodges") and w else ""
            rec = {"lieu": x["lieu"] or "lieu non donné", "ie": x["ie"], "qui": qui, "action": ("(suite) " if vus[x["id"]] > 1 else "") + x["titre"] + ici,
                   "src": x["src"], "pct": x["pct"], "m": x["m"], "fil": x["fil"], "type": x["type"],
                   "lieu_en": x.get("lieu_en") or x["lieu"] or "place not given", "m_en": x.get("m_en", ""),
                   "action_en": ("(cont.) " if vus[x["id"]] > 1 else "") + x.get("titre_en", x["titre"]), "qui_en": [q.replace(" (inscrit)", " (enrolled)") for q in qui],
                   "registre": x.get("registre", "")}
        rec["cours"] = bool(x and cours_(x))
        statut = "attesté" if rec["pct"] <= 10 else "usage attesté, transposé" if rec["pct"] <= 40 else "supposé"
        out.append({"n": i, "debut": hm(s["a"]), "fin": hm(s["b"]), "pages": f"{s['a'] + 1}–{s['b']}", "duree_min": s["b"] - s["a"],
                    "entete": f"{rec['ie']}. {rec['lieu'].upper()} — {moment}", "lumiere": etat, "meteo": meteo, "statut": statut, **rec,
                    "entete_en": f"{rec['ie']}. {rec['lieu_en'].upper()} — {MOMENT_EN[moment]}", "moment": moment,
                    "statut_en": {"attesté": "attested", "usage attesté, transposé": "attested custom, transposed", "supposé": "assumed"}[statut],
                    "temp_c": w.get("temp_c"), "temps_en": w.get("temps", ""), "lune_hauteur": l.get("lune_hauteur"), "soleil_hauteur": l.get("soleil_hauteur")})
    assert sum(o["duree_min"] for o in out) == 1440, sum(o["duree_min"] for o in out)

    # sorties
    with open(os.path.join(dos, "sequencier.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["n", "debut", "fin", "pages", "duree_min", "entete", "lieu", "personnages", "action", "fil", "type", "statut", "part_deduite_pct", "motif", "sources", "lumiere", "meteo"])
        for o in out: w.writerow([o["n"], o["debut"], o["fin"], o["pages"], o["duree_min"], o["entete"], o["lieu"], "; ".join(o["qui"]), o["action"], o["fil"], o["type"], o["statut"], o["pct"], o["m"], o["src"], o["lumiere"], o["meteo"]])
    json.dump(out, open(os.path.join(dos, "sequencier.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    st = collections.Counter(o["statut"] for o in out); mins = collections.Counter()
    for o in out: mins[o["statut"]] += o["duree_min"]
    fils = collections.Counter()
    for o in out: fils[o["fil"]] += o["duree_min"]
    L = [f"# Séquencier — {K.date_fr(d)}", "", f"[Sommaire de la journée](README.md)", "",
         f"**{len(out)} scènes** pour 1 440 pages (1 minute = 1 page), en temps réel de 00:00 à 23:59, sans trou. Quand plusieurs choses se passent "
         "en même temps, le montage alterne (montage parallèle) ; « (suite) » marque le retour à une scène déjà ouverte.", "",
         "| statut | scènes | pages |", "|---|---|---|"]
    L += [f"| {k} | {st[k]} | {mins[k]} |" for k in ("attesté", "usage attesté, transposé", "supposé")]
    pc = sum(o["duree_min"] for o in out if o.get("cours"))
    ecran = collections.Counter()
    for sc in scenes:
        if sc["x"] is not None and cours_(sc["x"]): ecran[sc["x"]["id"]] += sc["b"] - sc["a"]
    co_all = sorted([x for x in acts if cours_(x)], key=lambda x: x["a"])
    duree = sum(x["b"] - x["a"] for x in co_all)
    L += ["", f"**Cours** : chacun garde {round(QUOTA_COURS * 100)} % de sa durée à l'écran ; {len(co_all)} cours, {duree} minutes de cours cumulées "
          f"(plusieurs en même temps), {pc} pages de cours à l'écran ({round(100 * pc / max(1, duree))} %).", "",
          "| cours | heures | durée | à l'écran |", "|---|---|---|---|"]
    L += [f"| {K.md(K.court(x['titre'], 70))} | {hm(x['a'])}–{hm(x['b'])} | {x['b'] - x['a']} min | {ecran[x['id']]} pages ({round(100 * ecran[x['id']] / max(1, x['b'] - x['a']))} %) |" for x in co_all]
    L += ["", "Fils (pages par fil) : " + ", ".join(f"{k} {v}" for k, v in fils.most_common()) + ".", "",
          "Statut : **attesté** = part déduite de 10 % au plus (document daté qui couvre ce jour) ; **usage attesté, transposé** = 11 à 40 % "
          "(usage de la session ou d'un autre jour, salle d'un autre trimestre, heure supposée) ; **supposé** = plus de 40 % (scène de liaison ou "
          "conjecture, à confirmer). Personnages « (inscrit) » : étudiants qui ont ce cours dans leur fiche ce trimestre-là. Méthode : `scripts/sequencier.py`.", ""]
    heure = None
    for o in out:
        if o["debut"][:2] != heure:
            heure = o["debut"][:2]; l = lum.get(heure, {}); w = met.get(heure, {})
            L += ["", f"## {heure} h — pages {int(heure) * 60 + 1}–{int(heure) * 60 + 60} · {l.get('etat', '')} · {w.get('temps', '')}, {w.get('temp_c', '')} °C", "",
                  "| n° | heure | pages | scène | personnages | action | part déduite | source |", "|---|---|---|---|---|---|---|---|"]
        L.append(f"| {o['n']} | {o['debut']}–{o['fin']} | {o['pages']} | {K.md(o['entete'])} | {K.md(K.court(', '.join(o['qui']), 120))} | {K.md(K.court(o['action'], 220))} | "
                 f"{o['pct']} % ({o['statut']}) | {K.md(K.court(o['src'], 90))} |")
    K.ecrire(os.path.join(dos, "10_sequencier.md"), L)
    print(f"{len(out)} scènes ; " + ", ".join(f"{k} {st[k]} ({mins[k]} pages)" for k in st))


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(*sys.argv[1:3])
