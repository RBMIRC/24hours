"""Éléments d'une journée choisie pour le scénario : météo, lumière, lieux, personnes, cours, routine, faune et flore,
événements. Un fichier par élément (Markdown) et un fichier journee.json qui les réunit.

Usage : python3 scripts/journee.py AAAA-MM-JJ <clone de RBMIRC/week> <clone de RBMIRC/bmc-chronology>
Entrées :
  - journees/AAAA-MM-JJ/donnees_sources.json : faits relevés à la main (source, part déduite, motif) ;
  - journees/AAAA-MM-JJ/era5_horaire.json : météo heure par heure (Open-Meteo, réanalyse ERA5), téléchargée une fois ;
  - le semainier public (planning du jour, personnes), meteo/*.csv (NOAA), et dans bmc-chronology :
    chronos/009_personnes_cours_suivis.csv (cours suivis, BMC Yearbook), fiches.json (fiches du musée),
    extraction/2017.40.172a-g.txt (cours offerts en 1944-45).
Sortie : journees/AAAA-MM-JJ/README.md, 01_meteo.md … 09_progression_des_cours.md, journee.json."""
import collections, csv, datetime as dt, json, math, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K
import ephem

ROOT = K.ROOT
WMO = {0: "ciel clair", 1: "plutôt clair", 2: "partiellement nuageux", 3: "couvert", 45: "brouillard", 48: "brouillard givrant",
       51: "bruine légère", 53: "bruine", 55: "bruine forte", 61: "pluie faible", 63: "pluie", 65: "forte pluie", 71: "neige faible",
       73: "neige", 75: "forte neige", 80: "averses", 95: "orage"}
DIR = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]


def pages(h, f=""):
    a = K.mn(h); b = K.mn(f) if f else None
    if a is None: return ""
    return f"{a + 1}–{b}" if b and b > a else f"{a + 1}"


def norm(n):
    n = re.sub(r"\(.*?\)", "", n); n = n.replace("Jr.", "").replace(",", " ")
    t = [w for w in re.sub(r"[^A-Za-zÀ-ÿ' -]", " ", n).lower().split() if len(w) > 1 and w not in ("jr", "mrs", "mr", "dr")]
    return [re.sub(r"^mac", "mc", w) for w in t]


def proche(a, b):
    """même mot à une lettre près (Zabriskie / Zabriske), ou préfixe de quatre lettres (Eleanor / Eleanore)."""
    if a == b or (len(a) >= 4 and len(b) >= 4 and (a.startswith(b) or b.startswith(a))): return True
    if abs(len(a) - len(b)) > 1 or min(len(a), len(b)) < 5: return False
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]: i += 1
    return a[i + 1:] == b[i:] or a[i:] == b[i + 1:] or a[i + 1:] == b[i + 1:]


class Noms:
    """rapproche « Ati Gropius », « Beate "Ati" Gropius », « Mrs Fritz Hansgirg » (même nom de famille + un prénom commun)."""
    def __init__(self, fiches):
        self.F = fiches; self.par_nom = collections.defaultdict(list)
        for n in fiches: self.par_nom[norm(n)[-1] if norm(n) else n].append(n)
    def trouver(self, n):
        t = norm(n)
        if not t: return None
        if n in self.F: return n
        cands = self.par_nom.get(t[-1], []) or [c for k, v in self.par_nom.items() if proche(k, t[-1]) for c in v]
        if len(cands) == 1 and len(t) == 1: return cands[0]
        for c in cands:
            tc = norm(c)
            if any(proche(x, y) for x in t[:-1] for y in tc[:-1]): return c
        return cands[0] if len(cands) == 1 and not re.match(r"(?i)mrs?\b", n) else None


def age(naiss, d):
    try: b = dt.date.fromisoformat(naiss)
    except (ValueError, TypeError): return None
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


def lumiere(d):
    o = ephem.Observer(); o.lat, o.lon, o.elevation = str(K.LAT), str(K.LON), 650
    off, lib = K.decalage(d)
    loc = lambda e: (ephem.Date(e).datetime() + dt.timedelta(hours=off)).strftime("%H:%M")
    debut = ephem.Date(dt.datetime(d.year, d.month, d.day) - dt.timedelta(hours=off))
    R = {"heure_legale": lib}
    for nom, hz in (("astronomique", "-18"), ("nautique", "-12"), ("civile", "-6"), ("soleil", "-0:34")):
        o.horizon = hz; o.date = debut
        try:
            R["aube_" + nom] = loc(o.next_rising(ephem.Sun(), use_center=(nom != "soleil")))
            R["crepuscule_" + nom] = loc(o.next_setting(ephem.Sun(), use_center=(nom != "soleil")))
        except ephem.CircumpolarError: pass
    R["lever_soleil"], R["coucher_soleil"] = R.pop("aube_soleil"), R.pop("crepuscule_soleil")
    o.horizon = "0"; o.date = debut; tr = o.next_transit(ephem.Sun()); o.date = tr; s = ephem.Sun(o)
    R["midi_solaire"] = loc(tr); R["hauteur_max_soleil"] = round(math.degrees(s.alt), 1)
    o.date = debut; o.horizon = "0"
    m = ephem.Moon()
    try: R["lever_lune"] = loc(o.next_rising(m)); o.date = debut; R["coucher_lune"] = loc(o.next_setting(m))
    except ephem.CircumpolarError: pass
    o.date = debut + 0.5; m.compute(o)
    R["lune_eclairee_pct"] = round(m.phase); R["lune_phase"] = K.lune(d)[0]
    par_h = []
    for h in range(24):
        o.date = ephem.Date(debut + h / 24); s = ephem.Sun(o); m = ephem.Moon(o)
        a = math.degrees(s.alt)
        etat = "nuit" if a < -18 else "nuit astronomique claire" if a < -12 else "aube ou crépuscule nautique" if a < -6 else "aube ou crépuscule civil" if a < -0.83 else "jour"
        par_h.append({"heure": f"{h:02d}:00", "page": h * 60 + 1, "soleil_hauteur": round(a, 1), "soleil_azimut": round(math.degrees(s.az)),
                      "lune_hauteur": round(math.degrees(m.alt), 1), "etat": etat})
    R["par_heure"] = par_h
    return R


def meteo_horaire(p, d):
    if not os.path.exists(p): return []
    E = json.load(open(p, encoding="utf-8")); H = E["hourly"]; off = K.decalage(d)[0]; out = []
    for i, t in enumerate(H["time"]):
        loc = dt.datetime.fromisoformat(t) + dt.timedelta(hours=off)
        if loc.date() != d: continue
        g = lambda k: H.get(k, [None] * len(H["time"]))[i]
        out.append({"heure": loc.strftime("%H:%M"), "page": loc.hour * 60 + 1, "temp_c": g("temperature_2m"), "ressenti_c": g("apparent_temperature"),
                    "humidite_pct": g("relative_humidity_2m"), "nuages_pct": g("cloud_cover"), "nuages_bas_pct": g("cloud_cover_low"),
                    "vent_kmh": g("wind_speed_10m"), "vent_dir": DIR[round((g("wind_direction_10m") or 0) / 22.5) % 16], "rafales_kmh": g("wind_gusts_10m"),
                    "pluie_mm": g("precipitation"), "neige_cm": g("snowfall"), "temps": WMO.get(g("weather_code"), str(g("weather_code"))),
                    "sol_0_7cm_c": g("soil_temperature_0_to_7cm"), "pression_hpa": g("surface_pressure")})
    return out


def ref(f, U):
    if f.get("inv"):
        invs = [x.strip() for x in f["inv"].split(";")]
        return " ; ".join(f"[{i}]({U.get(i, {}).get('url', '')})" if U.get(i, {}).get("url") else i for i in invs)
    return f.get("src", "")


def puce(f, U):
    return f"- {f['t']} — *{ref(f, U)}* — {f.get('pct', 0)} %" + (f" ({f['m']})" if f.get("m") else "")


def main(jour, week, chrono):
    d = dt.date.fromisoformat(jour); dos = os.path.join(ROOT, "journees", jour)
    S = json.load(open(os.path.join(dos, "donnees_sources.json"), encoding="utf-8"))
    D, C, Sc, P, Sy = K.charger(week); M, men = K.meteo(); J, A = K.indexer(D, C, Sc)
    U = {f["accession"]: f for f in json.load(open(os.path.join(chrono, "bmc-programmes-aam", "fiches.json"), encoding="utf-8"))}
    F = P["fiches"]; N = Noms(F); E = J.get(d, [])
    an = K.an_scolaire(d); y0 = int(an[:4])
    saison = {9: "automne", 10: "automne", 11: "automne", 12: "automne", 1: "hiver", 2: "hiver", 3: "hiver", 4: "printemps", 5: "printemps", 6: "printemps", 7: "été", 8: "été"}[d.month]
    trim = f"{saison} {d.year if d.month != 12 or saison != 'hiver' else d.year + 1}"
    OUT = {"date": jour, "jour": K.date_fr(d), "annee_scolaire": an, "trimestre_fiches": trim}
    tete = lambda titre: [f"# {titre} — {K.date_fr(d)}", "", f"[Sommaire de la journée](README.md) · dossier du jour : [jours/{d.year}/{jour}.md](../../jours/{d.year}/{jour}.md)", ""]

    # ---------------- 01 météo
    st = []
    for code, nom, rem in K.STATIONS:
        rows = [M.get(code, {}).get(K.iso(d + dt.timedelta(k))) for k in range(-7, 7)]
        st.append((nom, rem, [(K.iso(d + dt.timedelta(k)), r) for k, r in zip(range(-7, 7), rows)]))
    era = meteo_horaire(os.path.join(dos, "era5_horaire.json"), d)
    OUT["meteo"] = {"noaa": {nom: {k: r for k, r in rows if r} for nom, rem, rows in st}, "era5_par_heure": era,
                    "documents": [r for k in range(-7, 8) for r in men.get(K.iso(d + dt.timedelta(k)), [])]}
    L = tete("Météo")
    L += ["## En bref", ""]
    if era:
        tmin = min(e["temp_c"] for e in era); tmax = max(e["temp_c"] for e in era)
        L.append(f"- Réanalyse ERA5 (maille de 25 km, plus douce que le fond de la vallée) : de {tmin} °C à {tmax} °C ; "
                 + " ; ".join(f"{e['heure']} {e['temps']}" for e in era if e["heure"] in ("06:00", "09:00", "12:00", "15:00", "18:00", "21:00")) + ".")
    for nom, rem, rows in st:
        r = dict(rows).get(jour)
        if r and r["tmax_c"]: L.append(f"- {nom} ({rem}) : min {r['tmin_c']} °C ({r['tmin_f']} °F), max {r['tmax_c']} °C ({r['tmax_f']} °F), pluie {r['pluie_mm']} mm" + (f", {r['phenomenes']}" if r["phenomenes"] else ""))
    L += ["", "## Ce que disent les documents du collège", ""]
    L += [f"- {r['date_document']} ({r['inventaire']}) : « {r['phrase']} »" for r in OUT["meteo"]["documents"]] or ["- rien"]
    L += ["", "## Relevés quotidiens NOAA, une semaine avant et après", "",
          "| date | " + " | ".join(n for n, _, _ in st) + " |", "|---|" + "---|" * len(st)]
    for i in range(14):
        k = st[0][2][i][0]; cells = []
        for nom, rem, rows in st:
            r = rows[i][1]
            cells.append(f"{r['tmin_c']}/{r['tmax_c']} °C, {r['pluie_mm']} mm" + (f", {r['phenomenes']}" if r["phenomenes"] else "") if r and r["tmax_c"] else "—")
        L.append(f"| {'**' + k + '**' if k == jour else k} | " + " | ".join(cells) + " |")
    L += ["", "Min/max en °C, pluie en mm. NOAA GHCN-Daily (domaine public) ; une station coopérative relève une fois par jour (souvent le soir) : le maximum peut appartenir à la veille.", ""]
    if era:
        L += ["## Heure par heure (réanalyse ERA5, heure légale du jour)", "",
              "| heure | page | temps | °C | ressenti | humidité | nuages (bas) | vent | pluie | sol 0-7 cm |", "|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {e['heure']} | {e['page']} | {e['temps']} | {e['temp_c']} | {e['ressenti_c']} | {e['humidite_pct']} % | {e['nuages_pct']} % ({e['nuages_bas_pct']} %) | {e['vent_kmh']} km/h {e['vent_dir']} | {e['pluie_mm']} mm | {e['sol_0_7cm_c']} °C |" for e in era]
        L += ["", "Source : Open-Meteo (open-meteo.com), réanalyse ERA5 du Copernicus Climate Change Service (licence CC BY 4.0), point 35,61 N, 82,37 W. "
              "Une réanalyse de 1944 est un modèle nourri de peu d'observations : part déduite **40 %** pour l'heure par heure (nuages, vent), "
              "à croiser avec les relevés NOAA du jour (0 %) et les bulletins. Le fond de la vallée est plus froid la nuit que la maille du modèle."]
    K.ecrire(os.path.join(dos, "01_meteo.md"), L)

    # ---------------- 02 lumière
    lu = lumiere(d); OUT["lumiere"] = lu
    L = tete("Lumière : soleil et lune")
    L += [f"Heure légale : **{lu['heure_legale']}**. Horizon théorique ; à Lake Eden les crêtes retardent le soleil visible le matin et l'avancent le soir.", "",
          "| moment | heure | page |", "|---|---|---|"]
    for k, lab in (("aube_astronomique", "aube astronomique (fin de la nuit noire)"), ("aube_nautique", "aube nautique"), ("aube_civile", "aube civile (on y voit dehors)"),
                   ("lever_soleil", "lever du soleil"), ("midi_solaire", f"midi solaire (soleil à {lu['hauteur_max_soleil']}°)"), ("coucher_soleil", "coucher du soleil"),
                   ("crepuscule_civil", "fin du crépuscule civil"), ("crepuscule_nautique", "fin du crépuscule nautique"), ("crepuscule_astronomique", "nuit noire"),
                   ("lever_lune", "lever de la lune"), ("coucher_lune", "coucher de la lune")):
        if lu.get(k): L.append(f"| {lab} | {lu[k]} | {pages(lu[k])} |")
    L += ["", f"Lune : {lu['lune_phase']}, éclairée à {lu['lune_eclairee_pct']} %.", "", "## Heure par heure", "",
          "| heure | page | soleil (hauteur, azimut) | lune (hauteur) | lumière |", "|---|---|---|---|---|"]
    L += [f"| {x['heure']} | {x['page']} | {x['soleil_hauteur']}°, {x['soleil_azimut']}° | {x['lune_hauteur']}° | {x['etat']} |" for x in lu["par_heure"]]
    L += ["", "Calcul : bibliothèque ephem (PyEphem), position de Lake Eden (35,606 N, 82,375 W, 650 m) ; précision de l'ordre de la minute ; 0 % de déduction pour le calcul, "
          "mais la lumière réelle dépend des nuages (voir 01_meteo.md)."]
    K.ecrire(os.path.join(dos, "02_lumiere.md"), L)

    # ---------------- 04 personnes
    suivis = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(chrono, "bmc-programmes-aam", "chronos", "009_personnes_cours_suivis.csv"), encoding="utf-8")):
        if r["trimestre"] == trim: suivis[r["etudiant"]].append(r)
    loge = {}
    for bat, ch in S["logements_etudiants"].items():
        if bat.startswith("_"): continue
        for piece, v in ch.items():
            for n in (v if isinstance(v, list) else [piece]):
                loge[n] = f"{bat}, {piece}" if isinstance(v, list) else f"study n° {v}"
    nommes = collections.Counter(n for e in E if e["couche"] == "aam" and not e["hors"] for n in e["noms"])
    cites = collections.Counter(n for e in E if e["couche"] in ("dub", "chr", "scn") for n in e["noms"])
    pers = {}
    def ajouter(nom_src, statut, pct, extra=None):
        k = N.trouver(nom_src) or nom_src
        p = pers.setdefault(k, {"nom": k, "noms_dans_les_sources": [], "presence": [], "pct_presence": 90})
        if nom_src not in p["noms_dans_les_sources"]: p["noms_dans_les_sources"].append(nom_src)
        p["presence"].append(statut); p["pct_presence"] = min(p["pct_presence"], pct)
        if extra:
            for kx, vx in extra.items():
                p[kx] = p[kx] + " ; " + vx if kx == "logement" and p.get(kx) and vx not in p[kx] else p.get(kx) if kx == "logement" and p.get(kx) else vx
    for n, c in nommes.items(): ajouter(n, f"nommé(e) dans les sources du jour ({c} fois)", 0)
    for n, l in loge.items(): ajouter(n, f"logement de la rentrée (30 septembre) : {l}", 10, {"logement": l})
    for n, rs in suivis.items(): ajouter(n, f"cours suivis à l'{trim} (BMC Yearbook)", 5, {"cours_suivis": [f"{r['cours']} ({r['enseignant']})" for r in rs]})
    for n, f in F.items():
        try: a, z = dt.date.fromisoformat(f["j"][0]), dt.date.fromisoformat(f["j"][1])
        except ValueError: continue
        if a <= d <= z: ajouter(n, f"intervalle de présence de la fiche : {f['j'][0]} → {f['j'][1]}", 30)
    OUT["cites_ailleurs"] = {n: c for n, c in cites.items() if (N.trouver(n) or n) not in pers}
    for p in pers.values():
        f = F.get(p["nom"], {})
        p.update({"role": f.get("role", ""), "domaine": f.get("dom", ""), "naissance": f.get("vie", ["", "", ""])[0], "origine": f.get("vie", ["", "", ""])[2],
                  "age": age(f.get("vie", [""])[0], d), "fiche": f.get("url", ""), "relations": f.get("rel", "")})
        if p["age"] is not None and p["age"] < 14 and "Student" in p["role"]: p["age"] = f"{p['age']} (date de naissance douteuse : {p['naissance']})"
        if f.get("j"):
            try:
                if dt.date.fromisoformat(f["j"][1]) < d: p["presence"].append(f"attention : la fiche dit départ le {f['j'][1]}"); p["pct_presence"] = max(p["pct_presence"], 40)
            except ValueError: pass
        cles = set(p["noms_dans_les_sources"] + [p["nom"]])
        tn = norm(p["nom"])
        if len(tn) >= 2: cles.add(f"{tn[0].capitalize()} {tn[-1].capitalize()}")
        p["travail"] = [t["t"] for t in S["travail"] + S["routine_complements"] if any(x in t["t"] for x in cles)]
    enseigne = collections.defaultdict(list)
    for e in E:
        if e["type"] in ("cours", "atelier") and e["couche"] == "aam":
            for q in e["noms"]: enseigne[N.trouver(q) or q].append(f"{e['h']} {e['titre']}")
    for k, v in enseigne.items():
        if k in pers: pers[k]["enseigne_ce_jour"] = v
    OUT["personnes"] = sorted(pers.values(), key=lambda p: (p["pct_presence"], p["role"], p["nom"].split()[-1]))
    L = tete("Personnes")
    L += ["Une ligne par personne. **Présence** : 0 % = nommée dans un document du jour ; 5 % = cours suivis ce trimestre-là (fiche d'étudiant) ; "
          "10 % = chambre attribuée à la rentrée du 30 septembre ; 30 % = seulement dans l'intervalle de présence de sa fiche (BMC Yearbook), vacances comprises. "
          "Âge au jour dit, d'après la date de naissance de la fiche.", ""]
    for titre, cond in (("Présence attestée (0-10 %)", lambda p: p["pct_presence"] <= 10), ("Présence probable (30 % et plus)", lambda p: p["pct_presence"] > 10)):
        G = [p for p in OUT["personnes"] if cond(p)]
        L += [f"## {titre} — {len(G)}", "", "| nom | rôle | âge | origine | logement | ce jour-là | cours suivis ce trimestre | travail | présence | fiche |", "|---|---|---|---|---|---|---|---|---|---|"]
        for p in sorted(G, key=lambda p: (p["role"] or "~", p["nom"].split()[-1])):
            L.append(f"| {K.md(p['nom'])} | {K.md(p['role'])} | {p['age'] if p['age'] is not None else ''} | {K.md(p['origine'])} | {K.md(p.get('logement', ''))} | "
                     f"{K.md(' ; '.join(p.get('enseigne_ce_jour', [])))} | {K.md(' ; '.join(p.get('cours_suivis', [])))} | {K.md(' ; '.join(K.court(t, 70) for t in p.get('travail', [])))} | {p['pct_presence']} % | {p['fiche']} |")
        L.append("")
    if OUT["cites_ailleurs"]:
        L += ["## Cités ce jour-là par les livres, pas forcément sur place", "", ", ".join(OUT["cites_ailleurs"]) + ".", ""]
    L += ["## Absences et allées et venues connues", ""]
    L += [f"- {f['t']} — *{ref(f, U)}* — {f['pct']} %" for f in S["evenements_semaine"] if re.search(r"rentre|part |quitte|Brevard|Chapel Hill|Washington", f["t"])]
    L += ["", "## Travail et responsabilités", ""] + [puce(f, U) for f in S["travail"]]
    K.ecrire(os.path.join(dos, "04_personnes.md"), L)

    # ---------------- 05 cours
    offerts = []
    for l in open(os.path.join(chrono, "bmc-programmes-aam", "extraction", "2017.40.172a-g.txt"), encoding="utf-8"):
        p = l.rstrip("\n").split("|")
        if p[0] == "C" and len(p) == 6 and "horaire" not in p[1]: offerts.append({"periode": p[1], "cours": p[2], "enseignant": p[3], "horaire": p[4], "note": p[5]})
    du_jour = [e for e in E if e["type"] in ("cours", "atelier")]
    def inscrits(titre, qui):
        tw = {w for w in re.findall(r"[a-z]{4,}", titre.lower())} - {"with", "theory", "practice", "laboratory", "class", "tutorial"}
        nq = (norm(qui)[-1:] or [""])[0]
        out = []
        for n, rs in suivis.items():
            for r in rs:
                cw = set(re.findall(r"[a-z]{4,}", r["cours"].lower()))
                if (tw & cw) and (not nq or nq in r["enseignant"].lower() or not r["enseignant"]): out.append(n); break
        return sorted(set(out))
    OUT["cours"] = []
    for e in du_jour:
        OUT["cours"].append({"heure": e["h"], "fin": e["f"], "pages": pages(e["h"], e["f"]), "titre": e["titre"], "enseignant": e["qui"], "lieu": e["lieu"],
                             "pct": e["pct"], "source": e["src"], "inscrits_bmc_yearbook": inscrits(e["titre"], e["qui"]), "progression": None})
    L = tete("Cours")
    L += ["## Les cours de ce lundi", "", "Grille de l'automne 1944 (bulletin du 23 octobre, 2017.40.176a-h ; part déduite 25 % : la grille ne nomme pas les enseignants) "
          "et ajouts des bulletins. **Inscrits** : étudiants qui ont ce cours dans leur fiche du BMC Yearbook pour l'" + trim + " (titre rapproché automatiquement : à relire).", ""]
    for c in sorted(OUT["cours"], key=lambda c: K.mn(c["heure"]) or 9999):
        L += [f"### {c['heure'] or '—'}{'–' + c['fin'] if c['fin'] else ''} · {c['titre']} — {c['enseignant'] or 'enseignant non nommé'}",
              f"- pages {c['pages']} ; lieu : {c['lieu'] or 'non donné'} ; part déduite {c['pct']} % ; source : {c['source']}",
              f"- inscrits ({len(c['inscrits_bmc_yearbook'])}) : " + (", ".join(c["inscrits_bmc_yearbook"]) or "aucun rapproché"),
              "- progression : *à compléter (09_progression_des_cours.md)*", ""]
    L += ["## Tous les cours offerts en 1944-45 (annonce du 30 septembre)", "", "| période | cours | enseignant | horaire (heures par semaine) | note |", "|---|---|---|---|---|"]
    L += [f"| {K.md(o['periode'])} | {K.md(o['cours'])} | {K.md(o['enseignant'])} | {K.md(o['horaire'])} | {K.md(o['note'])} |" for o in offerts]
    L += ["", f"Source : [2017.40.172a-g]({U.get('2017.40.172a-g', {}).get('url', '')}) ; F, W, S = trimestres d'automne, d'hiver, de printemps ; B/A = débutants/avancés.", "",
          f"## Tous les cours suivis à l'{trim} (fiches d'étudiants)", "", "| étudiant | cours (enseignant) |", "|---|---|"]
    for n, rs in sorted(suivis.items()):
        L.append(f"| {K.md(n)} | " + K.md(" ; ".join(r["cours"] + " (" + r["enseignant"] + ")" for r in rs)) + " |")
    OUT["cours_offerts"] = offerts; OUT["cours_suivis"] = {n: [{"cours": r["cours"], "enseignant": r["enseignant"]} for r in rs] for n, rs in suivis.items()}
    K.ecrire(os.path.join(dos, "05_cours.md"), L)

    # ---------------- 06 routine (et planning complet)
    routine = [e for e in E if e["type"] in ("social", "autre", "travail") and not e.get("semaine") and e["couche"] in ("aam", "spc")]
    R = [{"h": e["h"], "f": e["f"], "t": e["titre"], "qui": e["qui"], "lieu": e["lieu"], "pct": e["pct"], "src": e["src"], "couche": e["couche"]} for e in routine]
    R += [{"h": f["h"], "f": f["f"], "t": f["t"], "qui": "", "lieu": "", "pct": f["pct"], "src": ref(f, U) + (f" ({f['m']})" if f.get("m") else ""), "couche": "relevé"} for f in S["routine_complements"]]
    R.sort(key=lambda x: (K.mn(x["h"]) if x["h"] else 9999, x["pct"]))
    OUT["routine"] = R
    L = tete("Routine de la journée")
    L += ["Repas, courrier, bureau, magasin, ménage, traite, lait, linge : ce qui revient chaque jour. Part déduite : 10 % pour l'horaire quotidien de la session "
          "(bulletin du 30 septembre 1944), davantage pour ce qui est transposé d'une autre période.", "",
          "| heure | pages | quoi | qui, où | part déduite | source |", "|---|---|---|---|---|---|"]
    for x in R:
        if not x["h"]: continue
        L.append(f"| {x['h']}{'–' + x['f'] if x['f'] else ''} | {pages(x['h'], x['f'])} | {K.md(x['t'])} | {K.md(', '.join(v for v in (x['qui'], x['lieu']) if v))} | {x['pct']} % | {K.md(K.court(x['src'], 110))} |")
    L += ["", "## Sans heure", ""] + [f"- {x['t']} — {x['pct']} % — {x['src']}" for x in R if not x["h"]]
    L += ["", "## Le planning complet du jour", "", "Toutes les activités, cours compris, avec leurs pages : voir le dossier du jour "
          f"[jours/{d.year}/{jour}.md](../../jours/{d.year}/{jour}.md)."]
    K.ecrire(os.path.join(dos, "06_routine.md"), L)

    # ---------------- 03 lieux
    lx = collections.Counter(e["lieu"] for e in E if e["lieu"] and e["couche"] != "spc")
    occ = collections.defaultdict(list)
    for n, l in loge.items(): occ[l.split(",")[0]].append(n)
    OUT["lieux"] = {"campus": K.campus(d)[0], "faits": S["lieux"], "lieux_du_jour": dict(lx), "logements": S["logements_etudiants"]}
    L = tete("Lieux")
    L += [f"Campus : **{K.campus(d)[0]}** — {K.campus(d)[2]}.", "", "Lieux nommés par les sources du jour : " + ", ".join(f"{k} ({v})" for k, v in lx.most_common()) + ".", ""]
    for g in S["lieux"]:
        L += [f"## {g['nom']}", ""] + [puce(f, U) for f in g["faits"]]
        if g["id"] == "north_lodge":
            L += ["", "Chambres (rentrée du 30 septembre, 10 %) :", ""] + [f"- {piece} : {', '.join(v)}" for piece, v in S["logements_etudiants"]["North Lodge"].items()]
        if g["id"] == "south_lodge":
            L += ["", "Combles des hommes (10 %) :", ""] + [f"- {piece} : {', '.join(v)}" for piece, v in S["logements_etudiants"]["South Lodge"].items()]
        if g["id"] == "studies_building":
            L += ["", "Studies attribués à la rentrée (10 %) : " + ", ".join(f"{n} ({v})" for n, v in S["logements_etudiants"]["Studies (n°)"].items())]
        L.append("")
    L += ["Fiches générales des lieux (toutes années) : [lieux/](../../lieux/README.md)."]
    K.ecrire(os.path.join(dos, "03_lieux.md"), L)

    # ---------------- 07 faune et flore
    OUT["faune_flore"] = {"elevage": S["elevage"], "vegetal_et_sauvage": S["vegetal_et_sauvage"]}
    L = tete("Espace animal et végétal")
    L += ["## Les bêtes de la ferme", ""] + [puce(f, U) for f in S["elevage"]]
    L += ["", "Moments de la journée où l'on voit les bêtes : traite à 5 h et 17 h, lait à 7 h 30 et 18 h 15 (voir 06_routine.md) ; équipe de ferme du lundi l'après-midi.", "",
          "## Plantes, arbres, animaux sauvages", ""] + [puce(f, U) for f in S["vegetal_et_sauvage"]]
    L += ["", "La part déduite élevée (60 %) signale ce qui vient de la connaissance générale du milieu et non des sources du collège : à confirmer avant d'écrire la scène."]
    K.ecrire(os.path.join(dos, "07_faune_flore.md"), L)

    # ---------------- 08 événements
    OUT["evenements"] = {"semaine": S["evenements_semaine"], "courrier": S["courrier_du_jour"], "monde": S["monde"], "situation": S["situation"],
                         "autour": [{"debut": K.iso(a), "fin": K.iso(z), "titre": e["titre"], "pct": e["pct"], "source": e["src"]} for a, z, e in A if a - dt.timedelta(15) <= d <= z + dt.timedelta(15)]}
    L = tete("Événements, courrier, contexte")
    L += ["## La quinzaine (du 20 novembre au 14 décembre)", "", "| date | ce qui arrive | source | part déduite |", "|---|---|---|---|"]
    L += [f"| {'**' + f['d'] + '**' if f['d'] == jour else f['d']} | {K.md(f['t'])} | {ref(f, U)} | {f['pct']} % |" for f in sorted(S["evenements_semaine"], key=lambda f: f["d"])]
    L += ["", "## Le courrier lu dans le bulletin du jour", ""] + [puce(f, U) for f in S["courrier_du_jour"]]
    L += ["", "## Situation du collège", ""] + [puce(f, U) for f in S["situation"]]
    L += ["", "## Le monde", ""] + [puce(f, U) for f in S["monde"]]
    if OUT["evenements"]["autour"]:
        L += ["", "## Dates imprécises qui touchent ces jours-là (livres, témoignages)", ""] + [f"- {x['debut']} → {x['fin']} : {x['titre']} — {x['pct']} % — {K.court(x['source'], 100)}" for x in OUT["evenements"]["autour"]]
    K.ecrire(os.path.join(dos, "08_evenements.md"), L)

    # ---------------- 09 progression (réservé)
    L = tete("Progression des cours — réservé")
    L += ["À traiter séparément : pour chaque cours du jour, où en est-on de la matière (séance, exercice, lecture, œuvre), d'après les fiches d'étudiants, "
          "les catalogues, les témoignages et les synthèses de cours du semainier. Un paragraphe par cours, avec source et part déduite.", ""]
    for c in sorted(OUT["cours"], key=lambda c: K.mn(c["heure"]) or 9999):
        L += [f"## {c['heure']} · {c['titre']} — {c['enseignant']}", "", "- Séance du jour : *à compléter*", "- Où en est le trimestre (semaine 10 sur 11) : *à compléter*",
              "- Exercice, matériaux, œuvre : *à compléter*", "- Sources : *à compléter*", ""]
    K.ecrire(os.path.join(dos, "09_progression_des_cours.md"), L)

    # ---------------- README + JSON
    n0 = sum(1 for p in OUT["personnes"] if p["pct_presence"] <= 10)
    L = [f"# {K.date_fr(d).capitalize()} — la journée du scénario", "",
         "Structure des éléments dont le scénario a besoin (1 minute = 1 page : 00:00 = page 1, 23:59 = page 1440). Chaque élément a son fichier ; "
         "`journee.json` les réunit. Les faits relevés à la main sont dans `donnees_sources.json` ; tout est régénéré par "
         f"`python3 scripts/journee.py {jour} <week> <bmc-chronology>`.", "",
         "| élément | fichier | contenu | état |", "|---|---|---|---|",
         f"| Météo | [01_meteo.md](01_meteo.md) | relevés NOAA (une semaine avant et après), heure par heure ERA5, phrases des bulletins | rempli |",
         f"| Lumière | [02_lumiere.md](02_lumiere.md) | aubes, lever {lu['lever_soleil']}, coucher {lu['coucher_soleil']}, lune ({lu['lune_phase']}, {lu['lune_eclairee_pct']} %), heure par heure | rempli |",
         f"| Lieux | [03_lieux.md](03_lieux.md) | bâtiments et leur usage cet automne-là, chambres des étudiants, cottages des enseignants, ferme, lac, hors campus | rempli |",
         f"| Personnes | [04_personnes.md](04_personnes.md) | {len(OUT['personnes'])} personnes, dont {n0} à présence attestée ; âge, origine, logement, cours, travail | rempli |",
         f"| Cours | [05_cours.md](05_cours.md) | {len(OUT['cours'])} cours ce lundi (heures, pages, inscrits), cours offerts et suivis du trimestre | rempli |",
         "| Routine | [06_routine.md](06_routine.md) | repas, courrier, bureau, magasin, ménage, traite, lait, linge, chaudières | rempli |",
         "| Espace animal et végétal | [07_faune_flore.md](07_faune_flore.md) | bêtes de la ferme, plantes, arbres, animaux sauvages | rempli, en partie supposé |",
         "| Événements | [08_evenements.md](08_evenements.md) | la quinzaine, le courrier du jour, la situation du collège, le monde | rempli |",
         "| Progression des cours | [09_progression_des_cours.md](09_progression_des_cours.md) | place réservée | à faire |",
         "| Séquencier | [10_sequencier.md](10_sequencier.md) | les scènes de 00:00 à 23:59 en temps réel (1 440 pages), avec lieu, lumière, personnages, action, source et part déduite ; `sequencier.csv`, `sequencier.json` (scripts/sequencier.py, à partir de `scenes_cles.json`) | liste faite |",
         "| Plans de nature | [11_plans_nature.md](11_plans_nature.md) | plans de coupe qui rythment le montage (montagnes, ciel, astres, lumière, eau, givre, arbres et vent, oiseaux, bêtes, insectes, fumées, sons), placés minute par minute ; catalogue `plans_nature.json`, `plans_nature_montage.csv/json` (scripts/plans_nature.py) | premier découpage |",
         "| Scènes écrites | — | dialogues et didascalies, scène par scène | à faire |", "",
         "## Règles", "",
         "- Chaque fait porte sa source et sa part déduite (0 % = écrit tel quel dans un document daté qui couvre ce jour).",
         "- Ce qui vient d'une autre date ou d'une autre année le dit, avec une part déduite plus forte ; la connaissance générale (hors sources du collège) est à 30-60 %.",
         "- Dépôt public : résumés et citations courtes ; pas d'extrait long des livres.", ""]
    K.ecrire(os.path.join(dos, "README.md"), L)
    json.dump(OUT, open(os.path.join(dos, "journee.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{dos} : {len(OUT['personnes'])} personnes, {len(OUT['cours'])} cours, {len(R)} lignes de routine, météo {len(era)} heures")


if __name__ == "__main__":
    if len(sys.argv) < 4: sys.exit(__doc__)
    main(*sys.argv[1:4])
