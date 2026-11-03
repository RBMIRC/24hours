"""Blocs temporels d'une journée (rythme du film) : contrôle et fiche.

Usage : python3 scripts/rythme.py AAAA-MM-JJ
Lit journees/AAAA-MM-JJ/rythme.json ; vérifie que les blocs couvrent 00:00-24:00 sans trou ni chevauchement, que les
durées de plan sont cohérentes (min ≤ moyenne ≤ max) et que les parts de registres font environ 100 % ; écrit
13_rythme.md."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K


def mn(h): a, b = h.split(":"); return int(a) * 60 + int(b)


def main(jour):
    dos = os.path.join(K.ROOT, "journees", jour); R = json.load(open(os.path.join(dos, "rythme.json"), encoding="utf-8")); B = R["blocs"]; err = []
    if B[0]["de"] != "00:00" or B[-1]["a"] != "24:00": err.append("les blocs ne couvrent pas 00:00-24:00")
    for a, b in zip(B, B[1:]):
        if mn(a["a"]) != mn(b["de"]): err.append(f"{a['id']} → {b['id']} : trou ou chevauchement ({a['a']} / {b['de']})")
    for b in B:
        lo, hi, moy = b["plans_s"]
        if not lo <= moy <= hi: err.append(f"{b['id']} : durée moyenne hors de l'intervalle")
        tot = sum(b["parts"].values())
        if not 95 <= tot <= 105: err.append(f"{b['id']} : parts = {tot} %")
    if err: sys.exit("\n".join(err))
    L = [f"# Rythme du film — {K.date_fr(K.dt.date.fromisoformat(jour))}", "", "[Sommaire de la journée](README.md)", "", R["_lisezmoi"], "", "## Règles générales", ""]
    L += [f"- {r['fr']}" for r in R["regles_generales"]]
    L += ["", "## Les blocs", "", "| bloc | heures | durée | tempo | plans (min-max, moyenne) | parts des registres | passage d'un fil | respirations | réservé |", "|---|---|---|---|---|---|---|---|---|"]
    for b in B:
        d = mn(b["a"]) - mn(b["de"]); lo, hi, moy = b["plans_s"]
        res = " ; ".join(f"{x['type']} : {x['fr']}" + (f" ({x['duree_s']} s)" if isinstance(x.get("duree_s"), int) else f" ({x['duree_s'][0]}-{x['duree_s'][1]} s)" if x.get("duree_s") else "") for x in b["reserve"]) or "—"
        L.append(f"| **{b['id']}. {b['fr']}** | {b['de']}-{b['a']} | {d // 60} h {d % 60:02d} | {b['tempo']} | {lo}-{hi} s ({moy} s) | "
                 + ", ".join(f"{k} {v} %" for k, v in b["parts"].items()) + f" | {b['fil_max_s']} s au plus | {b['respiration']} | {K.md(res)} |")
    L += ["", "## Repères et ponts", ""]
    for b in B:
        L.append(f"- **{b['id']}. {b['fr']}** — repères : {', '.join(b['repères'])} ; pont : {b['pont']}" + (f" ; {b['notes_fr']}" if b.get("notes_fr") else ""))
    L += ["", "Nombre de plans attendu (hors cours et dialogues réservés) : " + ", ".join(f"{b['id']} ≈ {round((mn(b['a']) - mn(b['de'])) * 60 / b['plans_s'][2])}" for b in B) + "."]
    K.ecrire(os.path.join(dos, "13_rythme.md"), L)
    print(f"13_rythme.md : {len(B)} blocs, couverture 00:00-24:00 vérifiée")


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
