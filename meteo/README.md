# Météo, 1933-1957

Relevés quotidiens NOAA GHCN-Daily (domaine public), un fichier par station, produits par `scripts/meteo.py` :

| fichier | station | distance | remarques |
|---|---|---|---|
| `USC00318442.csv` | Swannanoa 2 E, 683 m | 3 km de Lake Eden, 5 km de la Blue Ridge Assembly | la plus proche ; même vallée de la Swannanoa |
| `USC00315796.csv` | Montreat, 793 m | 5 km au nord de Black Mountain | série partielle |
| `USW00013872.csv` | Asheville, 682 m | 22 km à l'ouest | série complète, seule à noter les phénomènes |

Colonnes : `tmin_c`, `tmax_c`, `tmin_f`, `tmax_f`, `pluie_mm`, `pluie_pouces`, `neige_mm` (tombée), `neige_au_sol_mm`,
`phenomenes` (brouillard, orage, pluie, neige, brume ou fumée, grésil, verglas, bruine…), `heure_releve` (heure du
relevé, HHMM, quand elle est donnée).

À savoir :
- une station coopérative relève une fois par jour, souvent le soir ou le matin : le maximum (ou la pluie) noté à une date
  peut appartenir en partie à la veille ;
- une valeur dont le contrôle qualité a échoué est écartée ;
- Lake Eden est au fond d'une vallée : matins plus frais et brouillards plus fréquents qu'à Asheville.

`mentions_documents.csv` (`scripts/mentions_meteo.py`) : phrases des documents datés du collège qui parlent du temps
(neige, pluie, boue, orage, froid…), avec la date du document. À relire : une lettre d'ancien étudiant, citée dans un
bulletin, peut parler du temps qu'il fait ailleurs.

Heure légale (pour le soleil, dans les dossiers de jour) : heure normale de l'Est (UTC−5) ; heure de guerre (EWT, UTC−4)
du 9 février 1942 au 30 septembre 1945. Une heure d'été locale avant ou après la guerre n'est pas documentée ici.
