"""Relevés météo quotidiens 1933-1957 autour du collège (NOAA, GHCN-Daily, domaine public).

Usage : python3 scripts/meteo.py <dossier des fichiers .csv.gz téléchargés>
Téléchargement : https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/<STATION>.csv.gz
Écrit meteo/<station>.csv : une ligne par jour, unités converties (°C et °F, mm et pouces), phénomènes en français.
Valeurs GHCN : TMAX/TMIN en dixièmes de °C, PRCP en dixièmes de mm, SNOW/SNWD en mm ; une valeur dont le
contrôle qualité (QFLAG) a échoué est écartée."""
import csv, gzip, os, sys, collections

STATIONS = {
    "USC00318442": ("Swannanoa 2 E", "35.6000 N, 82.3667 W, 683 m", "à environ 3 km de Lake Eden et 5 km de la Blue Ridge Assembly (même vallée de la Swannanoa)"),
    "USC00315796": ("Montreat", "35.6500 N, 82.3167 W, 793 m", "à 5 km au nord de Black Mountain ; relevés partiels"),
    "USW00013872": ("Asheville (ville)", "35.5953 N, 82.5567 W, 682 m", "à 22 km à l'ouest ; série complète, avec les phénomènes (brouillard, orage, pluie, neige)"),
}
PHEN = {"WT01": "brouillard", "WT03": "orage", "WT04": "grésil", "WT05": "grêle", "WT06": "verglas", "WT07": "poussière",
        "WT08": "brume ou fumée", "WT09": "neige soufflée", "WT14": "bruine", "WT16": "pluie", "WT18": "neige"}
DEBUT, FIN = "19330801", "19571231"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(src):
    for st, (nom, coord, rem) in STATIONS.items():
        J = collections.defaultdict(dict)
        with gzip.open(os.path.join(src, st + ".csv.gz"), "rt") as f:
            for r in csv.reader(f):
                _, d, el, v, mf, qf, sf, ot = (r + [""] * 8)[:8]
                if not (DEBUT <= d <= FIN) or qf.strip(): continue
                if el in ("TMAX", "TMIN", "PRCP", "SNOW", "SNWD", "TOBS"): J[d][el] = int(v)
                elif el in PHEN and v == "1": J[d].setdefault("ph", []).append(PHEN[el])
                if el in ("TMAX", "PRCP") and ot: J[d]["heure_releve"] = ot
        out = os.path.join(ROOT, "meteo", f"{st}.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "tmin_c", "tmax_c", "tmin_f", "tmax_f", "pluie_mm", "pluie_pouces", "neige_mm", "neige_au_sol_mm", "phenomenes", "heure_releve"])
            for d in sorted(J):
                x = J[d]; c = lambda k: round(x[k] / 10, 1) if k in x else ""
                fa = lambda k: round(x[k] / 10 * 9 / 5 + 32) if k in x else ""
                w.writerow([f"{d[:4]}-{d[4:6]}-{d[6:]}", c("TMIN"), c("TMAX"), fa("TMIN"), fa("TMAX"), c("PRCP"),
                            round(x["PRCP"] / 254, 2) if "PRCP" in x else "", x.get("SNOW", ""), x.get("SNWD", ""),
                            ", ".join(x.get("ph", [])), x.get("heure_releve", "")])
        print(f"{out} : {len(J)} jours ({nom})")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
