"""Un bloc du film découpé plan par plan à partir de son cahier (fils humains, transitions, respirations).

Usage : python3 scripts/bloc_plans.py AAAA-MM-JJ BLOC        (ex. : 1944-12-04 B2)
Lit journees/AAAA-MM-JJ/bloc_<BLOC>.json (le cahier) et rythme.json (durées de plan, passage d'un fil, respirations,
parts des registres) ; écrit le fichier nommé par "sortie" dans le cahier (format de aube_plan_par_plan.json, "compact": true),
contrôlé et mis en fiche par scripts/heure_plan_par_plan.py.

Méthode. Le bloc est une suite de passages. Un passage humain suit un fil actif à cette heure (la traite, la cuisine, les
chaudières…) pendant 90 s au plus du fil_max_s du bloc ; tous les 60 à 90 s, une respiration de 10 à 20 s (deux ou trois
plans) le coupe : ciel, nature ou bâtiment, pris dans les fils de transition du cahier ou dans les foyers de la nuit admis
par le cahier (scripts/nuit_plans.py). Un passage « monde » (20 à 60 s) déroule une phrase de nature ou d'architecture.
Le choix entre les deux suit les parts de registres du bloc (rythme.json) : on donne la main à la famille la plus en retard.
Chaque mouvement s'ouvre sur le fil que le cahier désigne ("ouvre"), par son premier détail. Un fil marqué "recit" avance
dans l'ordre de ses détails au fil de sa fenêtre (une fenêtre glissante de trois détails) ; les autres tournent en
prenant les détails les moins employés ; un détail peut porter sa propre fenêtre horaire. Échelles, angles, mouvements,
optiques et mises au point tournent sans se répéter d'un plan au suivant ; pas de drone ni de vue aérienne à l'intérieur ;
la durée suit l'échelle, modulée par une houle lente, bornée par plans_s. Conditions de ciel : ERA5 interpolé d'heure en
heure (clair sous 40 % de nuages) ; astres : ephem. Pas de dialogue (décision du 3/11/2026). Graine fixe."""
import datetime as dt, json, math, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K
import nuit_plans as N
import ephem

E_LARGE = ["TPE", "PE"]
FAM = {"SEUL": "pink", "COL": "red", "NAT": "green", "ARCH": "blue", "LARGE": "yellow", "DIAL": "violet"}
ANGLES_H = {"TPE": ["face", "aerien", "crete", "contre"], "PE": ["face", "aerien", "plongee", "crete", "contre"],
            "PL": ["face", "contre", "plongee", "sol", "travers"], "PM": ["face", "sol", "travers", "plongee", "contre", "subjectif"],
            "PR": ["face", "travers", "contre"], "GP": ["face", "sol", "travers", "zenith", "contre", "reflet"],
            "TGP": ["face", "zenith", "travers", "sol"], "SON": ["face"]}
INTERIEUR_H = re.compile(r"laiterie|stalle|cornadis|mangeoire|\bpis\b|seau|tabouret|flanc|chaudière|chaufferie|manomètre|registre|radiateur|"
                         r"\blit\b|lits|escalier|lobby|combles|caisse|cadran|lampe de poche|fourneau|marmite|buée|cafetière|bouillie|assiettes|"
                         r"tablier|tables|tasses|chariot|pains|plateaux|chaises|bidon|carrelage|cahier|mâchefers|couloir|lucarne|cuisine", re.I)
ETOILES = re.compile(r"étoil|Jupiter|Orion|Arcturus|Spica|Grande Ourse", re.I)
REFLET_H = re.compile(r"vitre|fenêtre|carreau|lucarne|lait|seau|eau|glace|flaque", re.I)
BASE = {"TPE": 9.5, "PE": 8.5, "PL": 7.5, "PM": 6.5, "PR": 6.5, "GP": 6, "TGP": 5.5, "SON": 7}


def sec(tc): h, m, s = map(int, tc.split(":")); return h * 3600 + m * 60 + s
def tc(s): return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"
def famille(reg): return FAM.get(reg.split("_")[0], "green")


def main(jour, bloc):
    dos = os.path.join(K.ROOT, "journees", jour); d = dt.date.fromisoformat(jour)
    C = json.load(open(os.path.join(dos, f"bloc_{bloc}.json"), encoding="utf-8"))
    R = next(b for b in json.load(open(os.path.join(dos, "rythme.json"), encoding="utf-8"))["blocs"] if b["id"] == bloc)
    A = json.load(open(os.path.join(dos, "aube_plan_par_plan.json"), encoding="utf-8"))
    J = json.load(open(os.path.join(dos, "journee.json"), encoding="utf-8"))
    V = json.loads(json.dumps(A["vocabulaire"]))
    for k, v in N.VOCAB_PLUS.items(): V[k].update(v)
    lo, hi, moy = R["plans_s"]; fil_max = R["fil_max_s"]
    nb = [int(x) for x in re.findall(r"\d+", R["respiration"])]; r_ecart, r_duree = (nb[0], nb[1]), (nb[2], nb[3])
    cible = {}
    for k, v in R["parts"].items(): cible[FAM[k.split("_")[0]]] = cible.get(FAM[k.split("_")[0]], 0) + v
    era = {int(x["heure"][:2]): x for x in J["meteo"]["era5_par_heure"]}
    def meteo(t):
        h = t // 3600; f = (t % 3600) / 3600; a, b = era.get(h, {}), era.get(min(23, h + 1), {})
        return {"nuages": a.get("nuages_pct", 0) * (1 - f) + b.get("nuages_pct", 0) * f, "temp_c": a.get("temp_c")}
    o = ephem.Observer(); o.lat, o.lon, o.elevation = str(K.LAT), str(K.LON), 650
    off = K.decalage(d)[0]; rnd = random.Random(19441204 + sum(map(ord, bloc)))
    def astres(s):
        o.date = dt.datetime(d.year, d.month, d.day) + dt.timedelta(seconds=s, hours=-off)
        m, j, a = ephem.Moon(o), ephem.Jupiter(o), ephem.star("Arcturus"); a.compute(o)
        return math.degrees(m.alt), math.degrees(m.az), math.degrees(j.alt), math.degrees(a.alt)

    t0, t1 = sec(C["de"]), sec(C["a"])
    humains = [f for f in C["fils"] if not f.get("transition")]
    transitions = [f for f in C["fils"] if f.get("transition")]
    admis = C.get("respirations", {}).get("foyers", {})
    exclus = tuple(C.get("respirations", {}).get("exclure", {}).get("textes", []))
    foyers = [f[:10] + ([x for x in f[10] if not x[0].startswith(exclus)],) for f in N.FOYERS if f[0] in admis]
    foyers = [f for f in foyers if f[10]]

    def ok_foyer(f, t):
        w = admis[f[0]]
        if w and not sec(w[0]) <= t < sec(w[1]): return False
        clair = meteo(t)["nuages"] < 40; lal, laz, jal, aal = astres(t); cond = f[6]
        if cond == "clair" and not clair: return False
        if cond == "voile" and clair: return False
        if cond == "jupiter" and (jal < 3 or not clair): return False
        if cond == "arcturus" and (aal < 3 or not clair): return False
        if f[0] == "lune" and (lal < 5 or not clair): return False
        return True
    def actif(f, t, marge=20): return sec(f["de"]) <= t and t + marge <= sec(f["a"])
    def det_ok(det, t): return len(det) < 4 or sec(det[3]["de"]) <= t < sec(det[3]["a"])

    plans, util, secs, prev, curseur = [], {}, {}, {"e": None, "mv": None, "o": None}, {}
    duree_fil = {}

    def tourner(det, e_choix, t, interieur, refl, angles):
        tot = sum(secs.values()) or 1
        if secs.get("yellow", 0) / tot > cible.get("yellow", 0) / 100 + 0.01: e_choix = [x for x in e_choix if x not in E_LARGE] or e_choix
        es = [x for x in e_choix if x != prev["e"]] or e_choix; e = rnd.choice(es)
        ang = [x for x in angles[e] if not ((x in ("aerien", "crete") and interieur and e not in E_LARGE) or (x == "reflet" and not refl)
                                             or (x == "subjectif" and not re.search(r"vache|chat|bête", det[0], re.I)))] or ["face"]
        mvs = [x for x in N.MVTS if not (x in ("drone", "grue") and interieur and e not in E_LARGE)]
        mv = "fixe" if e == "SON" else rnd.choice([x for x in mvs if x != prev["mv"]] or mvs)
        if e in ("GP", "TGP") and mv in ("drone", "grue", "vertigo"): mv = rnd.choice(["slider", "fixe", "motion"])
        if e in ("PR", "SON") and mv == "drone": mv = "steadicam" if e == "PR" else "fixe"
        # le texte impose parfois la technique
        if det[0].startswith("Drone"): mv, ang = "drone", ["aerien"]
        elif det[0].startswith("Time-lapse"): mv = "motion"
        elif det[0].startswith("Vue de la crête"): ang = ["crete"]
        if e in E_LARGE and mv == "slider": mv = "drone" if not interieur else "pano"
        a = rnd.choice(ang)
        if mv == "drone" and "aerien" in ang: a = "aerien"
        op = rnd.choice([x for x in N.OPTIQUES[e] if x != prev["o"]] or N.OPTIQUES[e]); pt = rnd.choice(N.POINTS[e])
        houle = 0.5 + 0.5 * math.sin((t - t0) / 600 * math.pi)
        dur = max(lo, min(hi, round(BASE[e] + (houle - 0.5) * 2 + rnd.uniform(-1.5, 1.5))))
        prev.update(e=e, mv=mv, o=op)
        return e, a, mv, op, pt, dur

    def poser(t, fin, dur, e, a, mv, op, pt, r, cat, reg, fr, en, son, src, pct, m, foyer, lieu):
        reste = fin - t
        if 0 < reste - dur < lo: dur = reste if reste <= hi else reste - lo     # pas de reliquat plus court qu'un plan
        dur = min(dur, reste)
        if dur < lo and plans and plans[-1]["d"] + dur <= hi:                    # reliquat trop court : on allonge le plan précédent
            plans[-1]["d"] += dur; secs[famille(plans[-1]["reg"])] = secs.get(famille(plans[-1]["reg"]), 0) + dur; return t + dur
        lal = astres(t)[0]
        plans.append({"tc": tc(t), "d": dur, "seq": C.get("seq", "reveil"), "e": e, "a": a, "mv": mv, "o": op, "p": pt, "r": r, "cat": cat, "reg": reg,
                      "fr": fr, "en": en, "son": son[0] or "ambiance", "son_en": son[1] or "ambience", "src": src, "pct": pct, "m": m,
                      "foyer": foyer, "lieu": lieu, "temp_c": meteo(t)["temp_c"], "lune_alt": round(lal)})
        secs[famille(reg)] = secs.get(famille(reg), 0) + dur; duree_fil[foyer] = duree_fil.get(foyer, 0) + dur
        return t + dur

    def details_fil(f, t, premier):
        D = [x for x in f["details"] if det_ok(x, t)] or f["details"]
        if premier: return [f["details"][0]]
        if f.get("recit"):
            phi = (t - sec(f["de"])) / max(1, sec(f["a"]) - sec(f["de"])); c = phi * (len(f["details"]) - 1)
            # récit : chaque détail est un moment, dans l'ordre ; deux plans au plus par moment ; le récit suit l'horloge
            # (il rattrape l'heure, jamais ne la devance de plus d'un moment et demi) ; s'il est à jour, la phrase s'arrête
            i = max(curseur.get(f["id"], 0), int(c - 3))
            while i < len(f["details"]) and util.get(f["details"][i][0], 0) >= 2: i += 1
            if i >= len(f["details"]) or i > c + 1.5: return []
            curseur[f["id"]] = i
            return [f["details"][i]]
        D = sorted(D, key=lambda x: util.get(x[0], 0))
        return D[:max(2, len(D) // 2 + 1)]

    def phrase_fil(f, t, fin, premier=False, raccord_fin=True):
        """une phrase sur un fil du cahier (humain ou transition), jusqu'à fin"""
        k = 0
        while t < fin:
            pool = details_fil(f, t, premier and k == 0)
            if not pool: break
            if k == 0 and not premier: pool = [x for x in pool if set(x[2]) & set(E_LARGE + ["PL", "PM"])] or pool
            det = rnd.choice(pool); util[det[0]] = util.get(det[0], 0) + 1
            inter = bool(INTERIEUR_H.search(det[0])); refl = bool(REFLET_H.search(det[0]))
            e, a, mv, op, pt, dur = tourner(det, det[2], t, inter, refl, ANGLES_H)
            dernier = t + dur >= fin - lo
            r = "cut"
            if dernier and raccord_fin: r = rnd.choice(["cut", "son_av", "franche", "lumiere", "forme"]) if rnd.random() < 0.6 else "cut"
            elif rnd.random() < 0.1: r = rnd.choice(["mvt", "forme", "lumiere", "son_ap"])
            reg = f.get("reg_large", f["reg"]) if e in E_LARGE else f["reg"]
            cat = f.get("cat") or ("gestes" if not f.get("transition") else "astres" if f["reg"].startswith("NAT") else "lumiere")
            t = poser(t, fin, dur, e, a, mv, op, pt, r, cat, reg, det[0], det[1], f.get("son", ["", ""]), f["src"], f["pct"],
                      f"plan généré (bloc {bloc}) ; " + ("geste attesté transposé" if not f.get("transition") and f["pct"] < 45 else "calculé" if cat == "astres" else "supposé d'après l'usage"),
                      f["id"], f["lieu"])
            k += 1
        return t

    def phrase_foyer(f, t, fin):
        lal, laz, jal, aal = astres(t); clair = meteo(t)["nuages"] < 40
        di = N.DIRS[int((laz + 22.5) // 45) % 8]; di_en = N.DIRS_EN[int((laz + 22.5) // 45) % 8]
        rep = {"lune": f"{round(lal)}° au-dessus de l'horizon, au {di}", "lune_en": f"{round(lal)}° above the horizon, to the {di_en}",
               "reflet": "la lune s'y reflète, à peine tremblée" if lal > 5 and clair else "aucun reflet sous le voile",
               "reflet_en": "the moon reflected in it, barely trembling" if lal > 5 and clair else "no reflection under the veil"}
        k = 0
        while t < fin:
            base = [x for x in f[10] if clair or not ETOILES.search(x[0])] or f[10]
            pool = base if k else ([x for x in base if set(x[2]) & set(E_LARGE + ["PL", "SON"])] or base)
            pool = sorted(pool, key=lambda x: util.get(x[0], 0)); pool = pool[:max(2, len(pool) // 2 + 1)]
            det = rnd.choice(pool); util[det[0]] = util.get(det[0], 0) + 1
            ang_ok, _ = N.compatibles(det, N.ANGLES[det[2][0]] if len(det[2]) == 1 else sum((N.ANGLES[x] for x in det[2]), []), N.MVTS)
            inter = bool(N.INTERIEUR.search(det[0])); refl = bool(N.REFLET.search(det[0])) and f[1] not in ("oiseaux", "betes")
            angles = {x: [a for a in N.ANGLES[x] if a in ang_ok] or ["face"] for x in N.ANGLES}
            e, a, mv, op, pt, dur = tourner(det, det[2], t, inter, refl, angles)
            r = "cut" if rnd.random() < 0.85 else rnd.choice(["forme", "lumiere", "son_ap"])
            reg = f[3] if e in E_LARGE else f[2]
            t = poser(t, fin, dur, e, a, mv, op, pt, r, f[1] if e != "SON" else "sons", reg, det[0].format(**rep), det[1].format(**rep),
                      f[9] if e != "SON" else ("son seul", "sound only"), f[7], f[8],
                      f"plan généré (bloc {bloc}, respiration) ; " + ("calculé" if f[1] == "astres" else "connaissance générale du milieu" if f[8] >= 45 else "usage attesté transposé"),
                      f[0], f[4])
            k += 1
        return t

    dernier_monde = []
    def monde(t, fin, nature_seule=False):
        """respiration ou passage « monde » : un fil de transition ou un foyer de la nuit admis"""
        c = [("fil", f, f["poids"]) for f in transitions if actif(f, t, 0) and f["id"] not in dernier_monde[-2:]]
        c += [("foyer", f, f[5]) for f in foyers if ok_foyer(f, t) and f[0] not in dernier_monde[-2:]]
        if nature_seule: c = [x for x in c if (x[1]["reg"] if x[0] == "fil" else x[1][2]).startswith("NAT")] or c
        # la famille en retard d'abord
        def retard(x):
            reg = x[1]["reg"] if x[0] == "fil" else x[1][2]; fam = famille(reg); tot = sum(secs.values()) or 1
            return cible.get(fam, 0) / 100 - secs.get(fam, 0) / tot
        poids = [w * (1 + max(0, retard(x)) * 8) / (1 + dernier_monde.count(x[1]["id"] if x[0] == "fil" else x[1][0]) * 0.05) for x in c for w in [x[2]]]
        kind, f, _ = rnd.choices(c, poids)[0]
        dernier_monde.append(f["id"] if kind == "fil" else f[0])
        return phrase_fil(f, t, fin, raccord_fin=False) if kind == "fil" else phrase_foyer(f, t, fin)

    bornes = [sec(m["de"]) for m in C["mouvements"]] + [t1]
    vus, dernier_fil, pause = set(), None, {}
    for i, mvt in enumerate(C["mouvements"]):
        t, fin_m = sec(mvt["de"]), bornes[i + 1]
        ferme = next((f for f in C["fils"] if f["id"] == mvt.get("ferme")), None)
        fin_mvt = fin_m
        if ferme: fin_m -= rnd.randint(25, 35)          # la fin du mouvement est réservée au dernier moment du récit
        ouvre = next((f for f in C["fils"] if f["id"] == mvt.get("ouvre")), None)
        if ouvre:
            t = phrase_fil(ouvre, t, min(fin_m, t + rnd.randint(40, 70)), premier=ouvre["id"] not in vus); vus.add(ouvre["id"]); dernier_fil = ouvre["id"]
            t = monde(t, min(fin_m, t + rnd.randint(*r_duree)))
        while t < fin_m:
            tot = sum(secs.values()) or 1
            part_h = (secs.get("pink", 0) + secs.get("red", 0)) / tot; cible_h = (cible.get("pink", 0) + cible.get("red", 0)) / 100
            act = [f for f in humains if actif(f, t) and pause.get(f["id"], 0) <= t and (tot < 900 or secs.get(famille(f["reg"]), 0) / tot <= cible.get(famille(f["reg"]), 0) / 100 + 0.02)]
            if act and (part_h < cible_h or rnd.random() < 0.25):
                cands = act
                def w(f):
                    fam = famille(f["reg"]); r = cible.get(fam, 0) / 100 - secs.get(fam, 0) / tot
                    # partage équitable pondéré : chaque fil reçoit du temps en proportion de son poids
                    return f["poids"] / (60 + duree_fil.get(f["id"], 0)) * (1 + max(0, r) * 3) * (0.6 if f["id"] == dernier_fil and len(act) > 1 else 1)
                f = rnd.choices(cands, [w(x) for x in cands])[0]; dernier_fil = f["id"]
                fin_p = min(fin_m, sec(f["a"]), t + rnd.randint(90, fil_max))
                while t < fin_p:
                    seg = min(fin_p, t + rnd.randint(*r_ecart))
                    tp = phrase_fil(f, t, seg, premier=f["id"] not in vus); vus.add(f["id"])
                    if tp < seg: pause[f["id"]] = tp + 60          # le récit est à jour : le fil se repose une minute
                    t = monde(tp, min(fin_m, tp + rnd.randint(*r_duree)), nature_seule=True) if tp < fin_m else tp
                    if tp < seg: break
            else:
                t = monde(t, min(fin_m, t + rnd.randint(20, 60)))
        if ferme:                                       # derniers moments du récit, dans l'ordre, jusqu'au dernier
            reste = [x for x in ferme["details"][curseur.get(ferme["id"], 0):] if util.get(x[0], 0) == 0][-3:] or ferme["details"][-1:]
            k0 = t
            for j, det in enumerate(reste):
                fin_d = fin_mvt if j == len(reste) - 1 else min(fin_mvt, t + (fin_mvt - k0) // len(reste))
                g = dict(ferme, details=[det], recit=False)
                t = phrase_fil(g, t, fin_d, raccord_fin=(j == len(reste) - 1))

    D = {"_lisezmoi": C["_lisezmoi"] + " Généré par scripts/bloc_plans.py (graine fixe : le même découpage à chaque passage).",
         "titre": C["titre"], "titre_en": C.get("titre_en", ""), "unite_en": C.get("unite_en", "shots"), "plans_s_en": f"{lo}–{hi} s", "compact": True, "bloc": bloc, "vocabulaire": V,
         "parts_obtenues": {k: round(100 * v / (t1 - t0)) for k, v in sorted(secs.items(), key=lambda x: -x[1])}, "parts_cibles": cible,
         "mouvements": [{k: m[k] for k in ("de", "a", "fr", "en")} for m in C["mouvements"]], "plans": plans}
    json.dump(D, open(os.path.join(dos, C["sortie"]), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    tot = sum(p["d"] for p in plans); assert tot == t1 - t0, (tot, t1 - t0)
    print(f"{C['sortie']} : {len(plans)} plans, {tot} s, durée moyenne {tot / len(plans):.1f} s (cible {moy} s), {len({p['fr'] for p in plans})} textes distincts")
    print("parts : " + ", ".join(f"{k} {100 * v / tot:.0f} % (cible {cible.get(k, 0)} %)" for k, v in sorted(secs.items(), key=lambda x: -x[1])))
    fils = {}
    for p in plans: fils[p["foyer"]] = fils.get(p["foyer"], 0) + p["d"]
    print("par fil ou foyer (s) : " + ", ".join(f"{k} {v}" for k, v in sorted(fils.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
