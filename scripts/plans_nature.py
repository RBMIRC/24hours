"""Plans de nature : découpage des plans de coupe (montagnes, ciel, astres, lumière, eau, givre, arbres et vent,
oiseaux, bêtes, insectes, fumées, sons) qui rythment le montage d'une journée.

Usage : python3 scripts/plans_nature.py AAAA-MM-JJ
Entrées : journees/AAAA-MM-JJ/plans_nature.json (catalogue des motifs, avec conditions, source et part déduite),
sequencier.json et journee.json (lumière, météo heure par heure).
Sorties : 11_plans_nature.md, plans_nature_montage.csv, plans_nature_montage.json.

Le temps reste réel : un plan de nature montre la nature à la minute même ; il est pris sur la séquence en cours
(quelques secondes de cette séquence), sans décaler l'horloge.
Règles de placement :
  - à chaque coupe entre deux séquences qui changent de lieu ou de type : 1 plan (2 la nuit) ;
  - aux bascules de lumière (aube nautique, lever du soleil, coucher, fin du crépuscule nautique) : un pont de 3 plans ;
  - dans une séquence longue : 1 plan toutes les 5 minutes (la nuit : 2 plans toutes les 4 minutes) ;
  - motif choisi parmi ceux qui sont valides à cette minute (moment, fenêtre horaire, ciel, température, vent), en
    préférant l'affinité avec le lieu de la séquence, une échelle et une catégorie différentes du plan précédent,
    et le motif le moins employé ; un même motif ne revient pas avant 25 minutes ni plus de 10 fois (sinon le plan est sauté)."""
import collections, csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K
from page_24h import lieu_de, type_de

ROOT = K.ROOT
PLAFOND = 10      # emplois au plus par motif dans la journée
ECART = 25        # minutes au moins entre deux emplois d'un même motif


def main(jour):
    dos = os.path.join(ROOT, "journees", jour)
    C = json.load(open(os.path.join(dos, "plans_nature.json"), encoding="utf-8"))
    S = json.load(open(os.path.join(dos, "sequencier.json"), encoding="utf-8"))
    J = json.load(open(os.path.join(dos, "journee.json"), encoding="utf-8"))
    era = {int(x["heure"][:2]): x for x in J["meteo"]["era5_par_heure"]}
    LU = J["lumiere"]; t_ = lambda k: K.mn(LU[k])
    def moment(t):
        return ("NUIT" if t < t_("aube_nautique") else "AUBE" if t < t_("lever_soleil") else "JOUR" if t < t_("coucher_soleil")
                else "CRÉPUSCULE" if t < t_("crepuscule_nautique") else "NUIT")
    def valide(m, t):
        w = era.get(t // 60, {}); cl, te, vt = w.get("nuages_pct", 50), w.get("temp_c", 0), w.get("vent_kmh", 0)
        if moment(t) not in m["mo"]: return False
        if m.get("h") and not (K.mn(m["h"][0]) <= t <= K.mn(m["h"][1])): return False
        if m.get("ciel") == "clair" and cl >= 40: return False
        if m.get("ciel") == "couvert" and cl < 60: return False
        if m.get("tmax") is not None and te > m["tmax"]: return False
        if m.get("tmin") is not None and te < m["tmin"]: return False
        if m.get("vent") and vt < m["vent"]: return False
        return True
    usage = collections.Counter(); dernier = {}; prec = {"e": "", "cat": ""}
    def choisir(t, lieu):
        cands = [m for m in C["motifs"] if valide(m, t) and t - dernier.get(m["id"], -999) >= ECART and usage[m["id"]] < PLAFOND]
        if not cands: return None             # plutôt sauter le plan que répéter un motif
        def score(m):
            return ((3 if lieu in m["lieux"] else 1 if not m["lieux"] else 0) + (1 if m["e"] != prec["e"] else 0)
                    + (1 if m["cat"] != prec["cat"] else 0) - 2 * usage[m["id"]] - m["pct"] / 100, m["id"])
        m = max(cands, key=score)
        usage[m["id"]] += 1; dernier[m["id"]] = t; prec.update(e=m["e"], cat=m["cat"])
        return m
    bascules = {t_("aube_nautique"): "aube", t_("lever_soleil"): "lever du soleil", t_("coucher_soleil"): "coucher du soleil", t_("crepuscule_nautique"): "nuit noire"}
    coupes = []                         # (minute, nombre de plans, séquence porteuse, raison)
    deb = lambda o: K.mn(o["debut"]); fin = lambda o: K.mn(o["fin"]) if o["fin"] != "24:00" else 1440
    for i, o in enumerate(S):
        a, b = deb(o), fin(o); nuit = moment(a) == "NUIT"
        if i:
            p = S[i - 1]
            if lieu_de(p) != lieu_de(o) or type_de(p) != type_de(o):
                coupes.append((a, 2 if nuit else 1, o, "coupe : changement de lieu ou de type"))
        pas = 4 if nuit else 5
        for t in range(a + pas, b - 1, pas):
            coupes.append((t, 2 if nuit else 1, o, "respiration dans une séquence longue"))
        for tb, nom in bascules.items():
            if a <= tb < b: coupes.append((tb, 3, o, f"pont de lumière : {nom}"))
    coupes.sort(key=lambda c: (c[0], -c[1]))
    plans, vu = [], set()
    for t, n, o, raison in coupes:
        if (t, raison[:4]) in vu: continue
        vu.add((t, raison[:4])); sec = 0
        for k in range(n):
            m = choisir(t, lieu_de(o))
            if not m: break
            w = era.get(t // 60, {})
            plans.append({"n": len(plans) + 1, "heure": f"{t // 60:02d}:{t % 60:02d}:{sec:02d}", "minute": t, "page": t + 1, "duree_s": m["d"],
                          "sequence": o["n"], "sequence_titre": o["entete"], "raison": raison, "id": m["id"], "cat": m["cat"],
                          "cat_fr": C["categories"][m["cat"]][0], "cat_en": C["categories"][m["cat"]][1], "e": m["e"],
                          "echelle": C["echelles"][m["e"]][0], "echelle_en": C["echelles"][m["e"]][1], "fr": m["fr"], "en": m["en"], "son": m["son"],
                          "moment": moment(t), "ciel": w.get("temps", ""), "temp_c": w.get("temp_c"), "vent_kmh": w.get("vent_kmh"),
                          "src": m["src"], "pct": m["pct"], "m": m["m"]})
            sec += m["d"]
    with open(os.path.join(dos, "plans_nature_montage.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); cols = ["n", "heure", "page", "duree_s", "sequence", "raison", "id", "cat_fr", "echelle", "fr", "son", "moment", "ciel", "temp_c", "vent_kmh", "pct", "m", "src"]
        w.writerow(cols); [w.writerow([p[c] for c in cols]) for p in plans]
    json.dump(plans, open(os.path.join(dos, "plans_nature_montage.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cat = collections.Counter(p["cat_fr"] for p in plans); ech = collections.Counter(p["echelle"] for p in plans)
    tot = sum(p["duree_s"] for p in plans)
    L = [f"# Plans de nature — {K.date_fr(K.dt.date.fromisoformat(jour))}", "", "[Sommaire de la journée](README.md) · [séquencier](10_sequencier.md)", "",
         f"**{len(plans)} plans de nature**, {tot // 60} min {tot % 60:02d} s au total, tirés de {len(usage)} motifs du catalogue "
         "(`plans_nature.json`). Ils rythment le montage sans décaler l'horloge : chacun montre la nature à la minute même et prend "
         "quelques secondes à la séquence en cours.", "",
         "Par catégorie : " + ", ".join(f"{k} {v}" for k, v in cat.most_common()) + ".", "",
         "Par échelle : " + ", ".join(f"{k} {v}" for k, v in ech.most_common()) + ".", "",
         "Part déduite : 10-25 % calculé (astres, lumière) ou relevé (gel) ; 30-45 % attesté à Lake Eden dans les années 1940 et transposé ; "
         "50-65 % connaissance générale du milieu, à confirmer.", ""]
    heure = None
    for p in plans:
        h = p["heure"][:2]
        if h != heure:
            heure = h; L += ["", f"## {h} h", "", "| n° | heure | page | séquence | échelle | plan | son | durée | conditions | part déduite | source |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        L.append(f"| {p['n']} | {p['heure']} | {p['page']} | {p['sequence']} | {p['echelle']} | **{p['cat_fr']}** — {K.md(p['fr'])} | {K.md(p['son'])} | {p['duree_s']} s | "
                 f"{p['moment'].lower()}, {p['ciel']}, {p['temp_c']} °C | {p['pct']} % | {K.md(K.court(p['src'], 80))} |")
    K.ecrire(os.path.join(dos, "11_plans_nature.md"), L)
    print(f"{len(plans)} plans de nature ({tot // 60} min) ; " + ", ".join(f"{k} {v}" for k, v in cat.most_common()))


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
