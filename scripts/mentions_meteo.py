"""Mentions du temps qu'il fait dans les documents datés de l'Asheville Art Museum (OCR des fiches).

Usage : python3 scripts/mentions_meteo.py <racine de bmc-programmes-aam>
Lit extraction/<inventaire>.txt (ligne « #ref AAAA-MM-JJ » : date du document) et pages_txt/*/<inventaire>_*.txt ;
écrit meteo/mentions_documents.csv (à relire : une lettre d'un ancien étudiant peut parler du temps ailleurs) : : date du document, inventaire, mot repéré, courte phrase (160 caractères au plus)."""
import csv, os, re, sys, glob

MOTS = r"snow\w*|rain\w*|storm\w*|flood\w*|sleet|ice[ -]?(?:storm|skating|covered)|icy|frozen|freez\w*|fog\w*|thunder\w*|hail|blizzard|" \
       r"zero|below freezing|cold wave|heat wave|hot weather|warm weather|cold weather|weather|sunshine|sunny|drought|frost\w*|thaw\w*|mud\w*|wind\w*"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main(aam):
    refs = {}
    for p in glob.glob(os.path.join(aam, "extraction", "*.txt")):
        for l in open(p, encoding="utf-8"):
            if l.startswith("#ref"): refs[os.path.basename(p)[:-4]] = l.split()[1]; break
    rows = []
    for p in sorted(glob.glob(os.path.join(aam, "pages_txt", "*", "*.txt"))):
        inv = os.path.basename(p).split("_")[0]
        if inv not in refs: continue
        t = re.sub(r"\s+", " ", open(p, encoding="utf-8", errors="replace").read())
        for ph in re.split(r"(?<=[.!?])\s+", t):
            m = next((x for x in re.finditer(r"\b(" + MOTS + r")\b", ph, re.I)
                      if not (x.group(1)[0].isupper() and x.start() > 0)), None)   # « Fogelson », titre « The Snow Falls » : écartés
            if not m or re.search(r"wind(ow|sor|ham)|mudd|rainey|hailed from|snowden", ph, re.I): continue
            s = ph.strip()
            if len(s) > 160:
                i = max(0, m.start() - 70); s = ("… " if i else "") + s[i:i + 150].strip() + " …"
            rows.append((refs[inv], inv, m.group(1).lower(), s))
    rows = sorted(set(rows))
    with open(os.path.join(ROOT, "meteo", "mentions_documents.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["date_document", "inventaire", "mot", "phrase"]); w.writerows(rows)
    print(len(rows), "mentions dans", len({r[1] for r in rows}), "documents")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
