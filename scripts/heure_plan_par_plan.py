"""Découpage plan par plan d'une heure de plans de nature (écrit à la main) : contrôle et fiche.

Usage : python3 scripts/heure_plan_par_plan.py journees/AAAA-MM-JJ/<fichier>.json [sortie.md]
Contrôles : timecodes croissants, aucun plan qui empiète sur le suivant, codes du vocabulaire connus.
Fiche : les mouvements, puis chaque plan (timecode, page, durée, échelle, angle, mouvement, optique, mise au point, raccord,
description, son, source, part déduite), puis la variété des techniques (décomptes par code)."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K


def sec(tc): h, m, s = map(int, tc.split(":")); return h * 3600 + m * 60 + s


def main(p, sortie=None):
    D = json.load(open(p, encoding="utf-8")); V = D["vocabulaire"]; P = D["plans"]; err = []
    for a, b in zip(P, P[1:]):
        if sec(a["tc"]) + a["d"] > sec(b["tc"]): err.append(f"{a['tc']} (+{a['d']} s) empiète sur {b['tc']}")
        if sec(b["tc"]) <= sec(a["tc"]): err.append(f"timecode non croissant : {b['tc']}")
    for x in P:
        for k, champ in (("e", "echelle"), ("a", "angle"), ("mv", "mouvement"), ("o", "optique"), ("p", "point"), ("r", "raccord")):
            if x[k] not in V[champ]: err.append(f"{x['tc']} : code inconnu {champ}={x[k]}")
    if err: sys.exit("\n".join(err))
    tot = sum(x["d"] for x in P)
    L = [f"# L'heure de l'aube, plan par plan — {P[0]['tc'][:5]} à {D['mouvements'][-1]['a'][:5]}", "", "[Sommaire de la journée](README.md) · [plans de nature](11_plans_nature.md)", "",
         D["_lisezmoi"], "", f"**{len(P)} plans**, {tot // 60} min {tot % 60:02d} s de nature dans l'heure ; plans les plus courts {min(x['d'] for x in P)} s, le plus long {max(x['d'] for x in P)} s.", ""]
    for champ, k in (("echelle", "e"), ("angle", "a"), ("mouvement", "mv"), ("optique", "o"), ("point", "p"), ("raccord", "r")):
        c = collections.Counter(x[k] for x in P)
        L.append(f"- **{champ.capitalize()}** : " + ", ".join(f"{V[champ][code][0]} {n}" for code, n in c.most_common()))
    cat = collections.Counter(x["cat"] for x in P)
    L += ["- **Sujets** : " + ", ".join(f"{k} {v}" for k, v in cat.most_common()), ""]
    for mvt in D["mouvements"]:
        ps = [x for x in P if sec(mvt["de"]) <= sec(x["tc"]) < sec(mvt["a"])]
        L += ["", f"## {mvt['fr']}", "", f"{len(ps)} plans, {sum(x['d'] for x in ps)} s.", "",
              "| tc | page | durée | échelle | angle | mouvement | optique | point | plan | son | raccord | part déduite | source |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for x in ps:
            L.append(f"| {x['tc']} | {sec(x['tc']) // 60 + 1} | {x['d']} s | {V['echelle'][x['e']][0]} | {V['angle'][x['a']][0]} | {V['mouvement'][x['mv']][0]} | "
                     f"{V['optique'][x['o']][0]} | {V['point'][x['p']][0]} | {K.md(x['fr'])} | {K.md(x['son'])} | {V['raccord'][x['r']][0]} | {x['pct']} %"
                     + (f" ({K.md(x['m'])})" if x["m"] else "") + f" | {K.md(x['src'])} |")
    sortie = sortie or os.path.join(os.path.dirname(p), "12_" + os.path.basename(p).replace(".json", ".md"))
    K.ecrire(sortie, L)
    print(f"{sortie} : {len(P)} plans, {tot} s ; " + ", ".join(f"{k} {v}" for k, v in cat.most_common()))


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(*sys.argv[1:3])
