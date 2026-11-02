"""Dossiers « 24 heures » : un fichier par jour, du 1er septembre 1933 au 31 août 1957, pour écrire une journée de
Black Mountain College en scénario (1 minute = 1 page : 00:00 = page 1, 23:59 = page 1440).

Usage : python3 scripts/construire.py <dossier du site public week> [<racine bmc-programmes-aam>]
  - données : version publique du semainier (dépôt RBMIRC/week : data.js, spec/*.js, data_chronos.js,
    data_scenario.js, data_personnes.js, data_syntheses.js), où les extraits longs des livres sont déjà retirés ;
  - météo : meteo/*.csv (scripts/meteo.py) et meteo/mentions_documents.csv (scripts/mentions_meteo.py).
Écrit : jours/AAAA/AAAA-MM-JJ.md et jours/AAAA/README.md, personnes/AAAA-AA.md, lieux/*.md, ambiance/AAAA-AA.md,
ambiance/toutes_annees.md, candidats.md.

Règles : chaque ligne garde sa source et sa part déduite (0 % = écrit tel quel dans un document daté) ; on ne recopie
pas les notes tirées des livres (Duberman, entretiens, témoignages) : titre, référence et page seulement ; les notes
des documents de l'AAM (archives du collège) sont gardées, elles sont courtes."""
import ast, collections, csv, datetime as dt, glob, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOURS = ["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]
NOMS_J = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
MOIS = ["", "janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
DEBUT, FIN = dt.date(1933, 9, 1), dt.date(1957, 8, 31)
LAT, LON = 35.606, -82.375          # Lake Eden ; la Blue Ridge Assembly est à 5 km (écart négligeable pour le soleil)
STATIONS = [("USC00318442", "Swannanoa 2 E", "3 km de Lake Eden"), ("USC00315796", "Montreat", "5 km au nord de Black Mountain"),
            ("USW00013872", "Asheville", "22 km à l'ouest")]
COUCHES = {"aam": "document du collège (AAM)", "dub": "Duberman 1972", "chr": "témoignage ou étude", "scn": "livres (scénario)",
           "spc": "reconstitution"}


def ld(p):
    s = open(p, encoding="utf-8").read()
    m = re.search(r"\]\s*=\s*\{", s)                        # spec/AAAA-AA.js : (window.X ||= {})["an"] = {...}
    i = m.end() - 1 if m and "BMC_SPEC_AN" in s[:m.start()] else s.index("{")
    return json.loads(s[i:s.rstrip().rstrip(";").rindex("}") + 1])


def iso(d): return d.isoformat()
def an_scolaire(d): y = d.year if d.month >= 9 else d.year - 1; return f"{y}-{(y + 1) % 100:02d}"
def date_fr(d): return f"{NOMS_J[d.weekday()]} {d.day}{'er' if d.day == 1 else ''} {MOIS[d.month]} {d.year}"
def hm(m): return f"{m // 60:02d}:{m % 60:02d}"
def mn(h):
    x = re.match(r"(\d{1,2}):(\d{2})", h or ""); return int(x.group(1)) * 60 + int(x.group(2)) if x else None
def court(s, n=150): s = re.sub(r"\s+", " ", s or "").strip(); return s if len(s) <= n else s[:n - 1].rstrip() + "…"
def md(s): return (s or "").replace("|", "/").replace("\n", " ")


# ------------------------------------------------------------------ soleil, lune, heure légale
def decalage(d):
    """heure légale : EST (UTC−5) ; heure de guerre EWT (UTC−4) du 9 février 1942 au 30 septembre 1945."""
    return (-4, "heure de guerre (EWT, UTC−4)") if dt.date(1942, 2, 9) <= d < dt.date(1945, 9, 30) else (-5, "heure normale de l'Est (EST, UTC−5)")


def soleil(d, haut=-0.833):
    n = (d - dt.date(2000, 1, 1)).days
    js = n - LON / 360
    M = (357.5291 + 0.98560028 * js) % 360; r = math.radians
    C = 1.9148 * math.sin(r(M)) + 0.02 * math.sin(r(2 * M)) + 0.0003 * math.sin(r(3 * M))
    lam = (M + C + 180 + 102.9372) % 360
    jt = 2451545.0 + js + 0.0053 * math.sin(r(M)) - 0.0069 * math.sin(r(2 * lam))
    dec = math.asin(math.sin(r(lam)) * math.sin(r(23.4397)))
    cw = (math.sin(r(haut)) - math.sin(r(LAT)) * math.sin(dec)) / (math.cos(r(LAT)) * math.cos(dec))
    if abs(cw) > 1: return None
    w = math.degrees(math.acos(cw)); off = decalage(d)[0] * 60
    loc = lambda j: round(((j - 2451545.0) % 1) * 1440 + 720 + off) % 1440     # JD .0 = midi UTC
    return loc(jt - w / 360), loc(jt + w / 360)


def lune(d):
    jd = (d - dt.date(2000, 1, 1)).days + 2451545.0          # vers midi
    age = ((jd - 2451550.1) / 29.530588853) % 1 * 29.530588853
    ecl = (1 - math.cos(2 * math.pi * age / 29.530588853)) / 2
    nom = ("nouvelle lune" if age < 1.85 or age > 27.68 else "premier croissant" if age < 5.54 else "premier quartier" if age < 9.23
           else "gibbeuse croissante" if age < 12.92 else "pleine lune" if age < 16.61 else "gibbeuse décroissante" if age < 20.30
           else "dernier quartier" if age < 23.99 else "dernier croissant")
    return nom, age, ecl


# ------------------------------------------------------------------ chargement
def charger(week):
    D = ld(os.path.join(week, "data.js"))
    C = ld(os.path.join(week, "data_chronos.js")); Sc = ld(os.path.join(week, "data_scenario.js"))
    P = ld(os.path.join(week, "data_personnes.js")); S = ld(os.path.join(week, "data_syntheses.js"))
    for an, Y in D["spec"].items():
        p = os.path.join(week, "spec", f"{an}.js")
        Y["gabarits"] = ld(p)["gabarits"] if os.path.exists(p) else []
    return D, C, Sc, P, S


def meteo():
    M = {}
    for st, nom, rem in STATIONS:
        p = os.path.join(ROOT, "meteo", f"{st}.csv")
        if os.path.exists(p): M[st] = {r["date"]: r for r in csv.DictReader(open(p, encoding="utf-8"))}
    men = collections.defaultdict(list)
    p = os.path.join(ROOT, "meteo", "mentions_documents.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")): men[r["date_document"]].append(r)
    return M, men


def entree(e, couche):
    ep = e.get("extendedProps", {}); st = e.get("start", "")
    h = st[11:16] if "T" in st else ""; f = (e.get("end") or "")[11:16] if "T" in (e.get("end") or "") else ""
    note = ""
    if couche == "aam": note = ep.get("note", "")
    elif couche == "scn": note = ep.get("note", "")
    src = ep.get("src", ""); inv = ep.get("inv", "")
    return {"h": h, "f": f, "titre": e.get("title", ""), "qui": ep.get("qui", ""), "lieu": ep.get("lieu", ""), "type": ep.get("type", ""),
            "pct": int(float(ep.get("pct") or 0)), "src": src, "url": ep.get("url", ""), "couche": couche, "note": note,
            "noms": [x for x in e.get("resourceIds", []) if not x.startswith("(")], "hors": "hors BMC" in (ep.get("note") or "")}


def jours_de(e):
    a = (e.get("start") or "")[:10]
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a): return []
    a = dt.date.fromisoformat(a); z = e.get("end") or ""
    z = dt.date.fromisoformat(z[:10]) if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", z) else a + dt.timedelta(1)
    if "T" in (e.get("end") or "") or z <= a: z = a + dt.timedelta(1)
    n = (z - a).days
    return [a + dt.timedelta(i) for i in range(n)] if n <= 7 else []


def indexer(D, C, Sc):
    J = collections.defaultdict(list); autour = []
    for couche, L in (("aam", D["events"]), ("dub", D["duberman"]), ("chr", C["grille"]), ("scn", Sc["grille"])):
        for e in L:
            js = jours_de(e)
            for x in js: J[x].append(entree(e, couche))
            if not js: autour.append((e, couche))
    for couche, L in (("dub", D["duberman_panneau"]), ("chr", C["panneau"]), ("scn", Sc["panneau"])):
        for e in L: autour.append((e, couche))
    A = []
    for e, couche in autour:
        a = (e.get("start") or "")[:10]; z = (e.get("fin_periode") or e.get("end") or a)[:10]
        try: a, z = dt.date.fromisoformat(a), dt.date.fromisoformat(z)
        except ValueError: continue
        if (z - a).days <= 62: A.append((a, z, entree(e, couche)))
    # reconstitution : gabarit du trimestre sur chaque jour de ses semaines (comme la page)
    for an, Y in D["spec"].items():
        G = collections.defaultdict(list)
        for g in Y["gabarits"]: G[g["terme"]].append(g)
        for S in Y["semaines"] + Y.get("quotidien", []):
            lun = dt.date.fromisoformat(S["lundi"]); jours = set(S["jours"])
            for g in G[S["terme"]]:
                if g["jour"] == "semaine":
                    cibles = [lun] if iso(lun) in jours else [dt.date.fromisoformat(min(jours))] if jours else []
                else:
                    x = lun + dt.timedelta(JOURS.index(g["jour"])); cibles = [x] if iso(x) in jours else []
                for x in cibles:
                    if iso(x) in (g.get("sauf") or ""): continue
                    J[x].append({"h": g["debut"] if g["jour"] != "semaine" else "", "f": g["fin"] if g["jour"] != "semaine" else "",
                                 "titre": g["activite"], "qui": g["qui"], "lieu": g["lieu"], "type": g["type"], "pct": int(g["part_deduite_pct"]),
                                 "src": "reconstitution " + an + (" — " + g["inventaire"] if g["inventaire"] else ""), "url": (g["url_source"] or "").split(" ")[0],
                                 "couche": "spc", "note": g["note"], "noms": [], "hors": False, "semaine": g["jour"] == "semaine",
                                 "motifs": g["motifs_deduction"], "terme": g["libelle_terme"]})
    return J, A


# ------------------------------------------------------------------ fichiers de contexte
def slug(s): return re.sub(r"[^a-z0-9]+", "_", re.sub(r"[àâä]", "a", re.sub(r"[éèêë]", "e", s.lower()))).strip("_")


def campus(d):
    if d < dt.date(1941, 6, 1):
        return "Blue Ridge Assembly", "blue_ridge_assembly", ("bâtiments loués à la Blue Ridge Association (YMCA), au sud du village de Black Mountain ; "
                                                             "Lee Hall, la grande maison commune" + (" ; chantier du Studies Building à Lake Eden (camps de travail)" if d >= dt.date(1940, 6, 1) else ""))
    return "Lake Eden", "lake_eden_campus", ("propriété du collège à Lake Eden, à 5 km à l'ouest du village" +
                                            (" ; après 1953, le campus bas (salle à manger, Studies Building) est fermé puis loué : plus de repas en commun" if d >= dt.date(1953, 9, 1) else ""))


def ecrire(p, L):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write("\n".join(L).rstrip() + "\n")


def lieux(S):
    motifs = dict((n, m) for n, m in S.get("lieux_motifs", []))
    idx = ["# Lieux", "", "Fiches tirées des synthèses du semainier (`data_syntheses.js`, lectures des livres et des documents, avec "
           "leurs pages). Résumés rédigés par nous ; pour une citation, retourner à la source.", ""]
    for nom, L in S["lieux"].items():
        f = slug(nom); idx.append(f"- [{nom}]({f}.md) — {len(L)} notices")
        T = [f"# {nom}", "", f"Motif de recherche dans les documents : `{motifs.get(nom, '')}`", ""]
        for x in sorted(L, key=lambda x: (x.get("y0") or 0, x.get("y1") or 0)):
            T.append(f"## {x.get('nom', nom)} — {x.get('per', '')}")
            for k, lab in (("desc", "Description"), ("usages", "Usages"), ("amb", "Ambiance")):
                if x.get(k): T.append(f"- **{lab}** : {x[k]}")
            T += [f"- *Source* : {x.get('s', '')}", ""]
        ecrire(os.path.join(ROOT, "lieux", f + ".md"), T)
    ecrire(os.path.join(ROOT, "lieux", "README.md"), idx)


def personnes(P):
    par_an = collections.defaultdict(list)
    for nom, f in P["fiches"].items():
        a, z = f["j"]
        try: a, z = dt.date.fromisoformat(a), dt.date.fromisoformat(z)
        except ValueError: continue
        y = a.year if a.month >= 9 else a.year - 1
        while dt.date(y, 9, 1) <= z:
            par_an[f"{y}-{(y + 1) % 100:02d}"].append((nom, f, a, z)); y += 1
    for an, L in par_an.items():
        T = [f"# Personnes au collège — {an}", "",
             "D'après les fiches du BMC Yearbook (bmcyearbook.org/biographies, Black Mountain College Museum + Arts Center) : "
             "première et dernière date de présence. L'intervalle couvre les vacances ; il ne prouve pas la présence un jour donné.", ""]
        for role in sorted({f["role"] or "—" for _, f, _, _ in L}):
            G = sorted([x for x in L if (x[1]["role"] or "—") == role], key=lambda x: x[0].split()[-1])
            T += [f"## {role} ({len(G)})", "", "| nom | présence | domaine | fiche |", "|---|---|---|---|"]
            T += [f"| {md(n)} | {iso(a)} → {iso(z)} | {md(f.get('dom', ''))} | {f.get('url', '')} |" for n, f, a, z in G]
            T.append("")
        ecrire(os.path.join(ROOT, "personnes", f"{an}.md"), T)
    return par_an


def puce(q): return f"- {'(' + q['per'] + ') ' if q.get('per') else ''}{q['desc']} — *{q['s']}*"


def liste(v):
    if isinstance(v, str) and v.startswith("["):
        try: v = ast.literal_eval(v)
        except (ValueError, SyntaxError): return v
    return " ; ".join(map(str, v)) if isinstance(v, list) else v


def ambiance(S):
    Q = S["quotidien"]; THEMES = collections.defaultdict(list)
    general = [q for q in Q if (q.get("y1") or 0) - (q.get("y0") or 0) > 4]
    T = ["# Ambiance — toutes années", "", "Détails de la vie quotidienne valables sur une longue période (plus de quatre ans), "
         "par thème. Résumés rédigés par nous d'après les livres et les documents ; référence et page pour chaque détail.", ""]
    for q in general: THEMES[q["th"]].append(q)
    for th in sorted(THEMES):
        T += [f"## {th.replace('_', ' ')}", ""] + [puce(q) for q in sorted(THEMES[th], key=lambda q: q.get("y0") or 0)] + [""]
    ecrire(os.path.join(ROOT, "ambiance", "toutes_annees.md"), T)
    for y in range(1933, 1957):
        an = f"{y}-{(y + 1) % 100:02d}"
        L = [q for q in Q if q not in general and (q.get("y0") or 0) <= y + 1 and (q.get("y1") or 0) >= y]
        T = [f"# Ambiance — {an}", "", "Détails de la vie quotidienne datés de cette année ou d'une période courte qui la touche "
             "(voir aussi [toutes_annees.md](toutes_annees.md)) ; puis la chronique de chaque mois (synthèses du semainier).", ""]
        G = collections.defaultdict(list)
        for q in L: G[q["th"]].append(q)
        for th in sorted(G):
            T += [f"## {th.replace('_', ' ')}", ""] + [puce(q) for q in G[th]] + [""]
        T += ["# Chronique mois par mois", ""]
        for m in list(range(9, 13)) + list(range(1, 9)):
            k = f"{y if m >= 9 else y + 1}-{m:02d}"; c = S["chroniques"].get(k)
            if not c: continue
            T += [f"## {MOIS[m]} {k[:4]}", ""]
            for champ, lab in (("session", "Session"), ("situation", "Situation"), ("quotidien", "Vie quotidienne"), ("tensions", "Tensions"), ("lacunes", "Lacunes")):
                v = liste(c.get(champ))
                if v: T.append(f"- **{lab}** : {v}")
            T.append("")
        ecrire(os.path.join(ROOT, "ambiance", f"{an}.md"), T)


# ------------------------------------------------------------------ jour
def periodes_du_jour(D, d):
    out = []
    for p in D["periodes"]:
        try: a = dt.date.fromisoformat(p["debut"]); z = dt.date.fromisoformat(p["fin"] or p["debut"])
        except (ValueError, TypeError): continue
        if a <= d <= z: out.append(p)
    out.sort(key=lambda p: (p.get("spec", False), p.get("pct", 0), "prévu" in p["libelle"] or "planned" in p["libelle"]))
    return out


def jour(d, D, J, A, M, men, par_an, S):
    an = an_scolaire(d); nom_c, slug_c, desc_c = campus(d)
    E = J.get(d, []); per = periodes_du_jour(D, d)
    vac = [p for p in per if re.search(r"(?i)vacation|holiday|recess|vacances", p["libelle"])]
    L = [f"# {date_fr(d).capitalize()} — Black Mountain College", "",
         f"Dossier de travail pour le scénario « 24 heures » (1 minute = 1 page : 00:00 = page 1, 23:59 = page 1440). "
         f"Année scolaire {an} · [ambiance de l'année](../../ambiance/{an}.md) · [personnes de l'année](../../personnes/{an}.md)", ""]
    L.append("**Calendrier** : " + (" ; ".join(f"{p['libelle']} ({p['debut']} → {p['fin'] or '?'}{', ' + str(p['pct']) + ' %' if p.get('pct') else ''})" for p in per[:4]) or "aucune période attestée ce jour-là"))
    if vac: L.append("**Vacances** : " + vac[0]["libelle"])
    L += ["", "## Météo et lumière", ""]
    for st, nom, rem in STATIONS:
        r = M.get(st, {}).get(iso(d))
        if not r or not (r["tmax_c"] or r["pluie_mm"]): continue
        t = []
        if r["tmin_c"] or r["tmax_c"]: t.append(f"min {r['tmin_c']} °C ({r['tmin_f']} °F), max {r['tmax_c']} °C ({r['tmax_f']} °F)")
        if r["pluie_mm"] != "": t.append(f"pluie {r['pluie_mm']} mm" + (f" ({r['pluie_pouces']} in)" if float(r['pluie_mm'] or 0) > 0 else ""))
        if r["neige_mm"] not in ("", "0"): t.append(f"neige tombée {r['neige_mm']} mm")
        if r["neige_au_sol_mm"] not in ("", "0"): t.append(f"neige au sol {r['neige_au_sol_mm']} mm")
        if r["phenomenes"]: t.append("phénomènes : " + r["phenomenes"])
        L.append(f"- **{nom}** ({rem}) : " + ", ".join(t))
    L.append("- *Relevés NOAA GHCN-Daily ; une station coopérative relève souvent le soir : le maximum peut être celui de la veille ; voir meteo/README.md.*")
    s = soleil(d); c = soleil(d, -6); off, lib = decalage(d); nl, age, ecl = lune(d)
    if s:
        L.append(f"- **Soleil** ({lib}) : aube civile {hm(c[0])}, lever {hm(s[0])}, coucher {hm(s[1])}, fin du crépuscule civil {hm(c[1])} ; "
                 f"jour de {(s[1] - s[0]) // 60} h {(s[1] - s[0]) % 60:02d} (horizon théorique : les crêtes de la vallée retardent le lever et avancent le coucher).")
    L.append(f"- **Lune** : {nl} (âge {age:.1f} jours, éclairée à {round(ecl * 100)} %), calcul approché.")
    proches = [r for k in range(-6, 1) for r in men.get(iso(d - dt.timedelta(k)), [])]
    for r in proches[:4]: L.append(f"- Document du {r['date_document']} ({r['inventaire']}) : « {r['phrase']} »")
    L += ["", "## Lieu", "", f"**{nom_c}** — {desc_c}. Fiche : [lieux/{slug_c}.md](../../lieux/{slug_c}.md) ; autres lieux : [lieux/](../../lieux/README.md).", ""]
    lx = collections.Counter(e["lieu"] for e in E if e["lieu"] and e["couche"] != "spc")
    if lx: L.append("Lieux nommés ce jour-là dans les sources : " + ", ".join(f"{k} ({v})" for k, v in lx.most_common(12)) + ".")
    # personnes
    att = collections.Counter(n for e in E if e["couche"] != "spc" for n in e["noms"])
    pres = [(n, f) for n, f, a, z in par_an.get(an, []) if a <= d <= z]
    L += ["", "## Personnes", ""]
    if att: L.append("**Nommées ce jour-là dans les sources** : " + ", ".join(f"{n}" + (f" ({v})" if v > 1 else "") for n, v in att.most_common(60)) + ".")
    if pres:
        L.append(f"**Au collège à cette date d'après les fiches du BMC Yearbook** ({len(pres)} ; intervalle de présence, vacances comprises) :")
        G = collections.defaultdict(list)
        for n, f in pres: G[f["role"] or "—"].append(n)
        for role in sorted(G, key=lambda r: -len(G[r])): L.append(f"- {role} ({len(G[role])}) : " + ", ".join(sorted(G[role], key=lambda x: x.split()[-1])))
    # planning
    hor = sorted([e for e in E if e["h"] and not e.get("semaine")], key=lambda e: (mn(e["h"]), e["pct"]))
    sans = [e for e in E if not e["h"] and not e.get("semaine")]; sem = [e for e in E if e.get("semaine")]
    L += ["", "## Planning minuté (1 minute = 1 page)", ""]
    if sem: L.append("Semaine : " + " ; ".join(f"{e['titre']} ({e['pct']} %)" for e in sem))
    L += ["", "| heure | pages | activité | qui | lieu | part déduite | source |", "|---|---|---|---|---|---|---|"]
    prem = mn(hor[0]["h"]) if hor else 24 * 60
    if prem > 0: L.append(f"| 00:00–{hm(prem)} | 1–{prem} | *Nuit, ou heures sans activité dans les sources* | | | — | |")
    for e in hor:
        a = mn(e["h"]); b = mn(e["f"]) if e["f"] else None
        pg = f"{a + 1}–{b}" if b and b > a else f"{a + 1}"
        cs = "reconstitué " if e["couche"] == "spc" else ""
        src = f"[{md(court(e['src'], 90))}]({e['url']})" if e["url"] else md(court(e["src"], 90))
        L.append(f"| {e['h']}{'–' + e['f'] if e['f'] else ''} | {pg} | {md(e['titre'])}{' *(hors du collège)*' if e['hors'] else ''} | {md(court(e['qui'], 60))} | {md(e['lieu'])} | {cs}{e['pct']} % | {COUCHES[e['couche']]} : {src} |")
    if sans:
        L += ["", "**Dans la journée, sans heure** :", ""]
        for e in sorted(sans, key=lambda e: e["pct"]):
            src = f"[{md(court(e['src'], 90))}]({e['url']})" if e["url"] else md(court(e["src"], 90))
            L.append(f"- {e['titre']}{' *(hors du collège)*' if e['hors'] else ''}" + (f" — {court(e['qui'], 60)}" if e["qui"] else "") + (f" — {e['lieu']}" if e["lieu"] else "")
                     + f" — {e['pct']} % — {COUCHES[e['couche']]} : {src}")
    notes = [e for e in hor + sans if e["note"] and e["couche"] == "aam"]
    if notes:
        L += ["", "**Ce que disent les documents du collège** (notes de lecture, citations courtes) :", ""]
        L += [f"- {e['titre']} : {court(e['note'], 300)}" for e in notes[:25]]
    # autour
    aut = [(a, z, e) for a, z, e in A if a - dt.timedelta(10) <= d <= z + dt.timedelta(10)]
    if aut:
        L += ["", "## Autour de ce jour (dates imprécises ou à quelques jours près)", ""]
        for a, z, e in sorted(aut, key=lambda x: (x[2]["pct"], x[0]))[:20]:
            L.append(f"- {iso(a)}{' → ' + iso(z) if z != a else ''} : {e['titre']} — {e['pct']} % — {COUCHES[e['couche']]} : {court(e['src'], 100)}")
    # ambiance du mois
    c = S["chroniques"].get(f"{d.year}-{d.month:02d}")
    L += ["", "## Ambiance", ""]
    if c:
        for champ, lab in (("session", "Session"), ("quotidien", "Vie quotidienne du mois")):
            if c.get(champ): L.append(f"- **{lab}** : {c[champ]}")
    L.append(f"- Détails par thème (repas, musique, travail, nature, climat et saisons…) : [ambiance/{an}.md](../../ambiance/{an}.md) et [ambiance/toutes_annees.md](../../ambiance/toutes_annees.md).")
    # cours
    cours = {}
    for e in hor + sans:
        if e["type"] in ("cours", "atelier"): cours.setdefault((e["titre"], e["qui"]), e)
    L += ["", "## Progression des cours (à traiter séparément)", "",
          "Place réservée : ce que chaque cours fait ce jour-là (séance, exercice, matériaux). Voir [cours/](../../cours/README.md).", ""]
    L += [f"- {e['h'] or '—'} **{e['titre']}**" + (f" ({court(e['qui'], 50)})" if e["qui"] else "") + " : *à compléter*" for e in cours.values()] or ["- (aucun cours ce jour-là dans les sources)"]
    # sources
    srcs = {}
    for e in E:
        if e["couche"] != "spc": srcs.setdefault(e["src"], e["url"])
    if srcs:
        L += ["", "## Sources du jour", ""] + [f"- {s}" + (f" — {u}" if u else "") for s, u in sorted(srcs.items())]
    info = {"n_att": sum(1 for e in hor if e["couche"] != "spc"), "n_att_h": sum(1 for e in hor if e["couche"] != "spc" and e["pct"] <= 25),
            "n_spc": sum(1 for e in E if e["couche"] == "spc"), "noms": len(att), "pres": len(pres), "vac": bool(vac),
            "pct": round(sum(e["pct"] for e in hor) / len(hor)) if hor else None, "campus": nom_c,
            "meteo": M.get("USC00318442", {}).get(iso(d)) or M.get("USW00013872", {}).get(iso(d))}
    return L, info


def main(week):
    D, C, Sc, P, S = charger(week); M, men = meteo()
    J, A = indexer(D, C, Sc)
    lieux(S); par_an = personnes(P); ambiance(S)
    infos = {}; d = DEBUT
    while d <= FIN:
        L, infos[d] = jour(d, D, J, A, M, men, par_an, S)
        ecrire(os.path.join(ROOT, "jours", str(d.year), f"{iso(d)}.md"), L)
        d += dt.timedelta(1)
    for y in range(DEBUT.year, FIN.year + 1):
        T = [f"# {y} jour par jour", "", "| date | jour | activités attestées à l'heure | reconstituées | personnes nommées | part déduite moyenne | météo (Swannanoa) |", "|---|---|---|---|---|---|---|"]
        for d, i in sorted(infos.items()):
            if d.year != y: continue
            m = i["meteo"]; mt = f"{m['tmin_c']}/{m['tmax_c']} °C, {m['pluie_mm']} mm" if m and m["tmax_c"] else ""
            T.append(f"| [{iso(d)}]({iso(d)}.md) | {NOMS_J[d.weekday()]}{' (vacances)' if i['vac'] else ''} | {i['n_att']} | {i['n_spc']} | {i['noms']} | {'' if i['pct'] is None else str(i['pct']) + ' %'} | {mt} |")
        ecrire(os.path.join(ROOT, "jours", str(y), "README.md"), T)
    # candidats : journées les mieux documentées
    sc = sorted(((i["n_att_h"] * 3 + i["n_att"] + i["noms"] / 2 + (5 if i["meteo"] else 0), d, i) for d, i in infos.items() if not i["vac"]), reverse=True)
    T = ["# Journées candidates", "", "Les jours les mieux documentés pour une « journée type » : nombre d'activités attestées avec une heure "
         "(part déduite de 25 % au plus, compté trois fois), autres activités datées, personnes nommées, météo connue. "
         "Classement indicatif ; une journée composite reste possible (en le disant).", "",
         "| rang | date | jour | campus | attestées à l'heure (≤ 25 %) | attestées | reconstituées | personnes nommées | part déduite moyenne |", "|---|---|---|---|---|---|---|---|---|"]
    for k, (s_, d, i) in enumerate(sc[:60], 1):
        T.append(f"| {k} | [{iso(d)}](jours/{d.year}/{iso(d)}.md) | {NOMS_J[d.weekday()]} | {i['campus']} | {i['n_att_h']} | {i['n_att']} | {i['n_spc']} | {i['noms']} | {i['pct']} % |")
    T += ["", "## La meilleure journée de chaque année scolaire", "", "| année | date | jour | attestées à l'heure | personnes nommées |", "|---|---|---|---|---|"]
    best = {}
    for s_, d, i in sc: best.setdefault(an_scolaire(d), (d, i))
    T += [f"| {an} | [{iso(d)}](jours/{d.year}/{iso(d)}.md) | {NOMS_J[d.weekday()]} | {i['n_att_h']} | {i['noms']} |" for an, (d, i) in sorted(best.items())]
    ecrire(os.path.join(ROOT, "candidats.md"), T)
    print(f"{len(infos)} jours écrits ; {sum(1 for i in infos.values() if i['n_att'])} avec au moins une activité attestée à l'heure")


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
