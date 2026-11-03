# 24 heures au Black Mountain College

Page en ligne (anglais) : https://rbmirc.github.io/24hours/ (copie : https://rbmirc.github.io/week/24h/) — `index.html`, produite par `scripts/page_24h.py`.

Matériaux pour écrire **une journée type** du Black Mountain College (1933-1957) en **scénario de film, 1 minute = 1 page**
(une journée entière = 1 440 pages : 00:00 = page 1, 07:30 = page 451, 12:00 = page 721, 23:59 = page 1440).

Tout vient des sources, avec la référence et la **part déduite** de chaque ligne (0 % = écrit tel quel dans un document
daté ; davantage pour ce qui est tiré d'un livre, d'une lecture automatique ou reconstitué). Données tirées du semainier
(https://rbmirc.github.io/week, dépôt de travail RBMIRC/bmc-chronology) et des relevés météo de la NOAA.

## Contenu

Audit et plan de travail pour le découpage plan par plan : [`AUDIT_ET_WORKFLOW.md`](AUDIT_ET_WORKFLOW.md).

| dossier | contenu |
|---|---|
| [`journees/1944-12-04/`](journees/1944-12-04/README.md) | **la journée retenue, lundi 4 décembre 1944** : un fichier par élément (météo, lumière, lieux, personnes, cours, routine, espace animal et végétal, événements, progression des cours), `journee.json` le **séquencier** (`10_sequencier.md` : 315 séquences en temps réel) et les **plans de nature** (`11_plans_nature.md` : 499 plans de coupe) |
| [`candidats.md`](candidats.md) | les journées les mieux documentées (pour choisir la journée type) et la meilleure de chaque année |
| [`jours/`](jours/) | un dossier par jour, du 1er septembre 1933 au 31 août 1957 (8 766 jours) ; `jours/AAAA/README.md` : tableau de l'année |
| [`meteo/`](meteo/README.md) | relevés quotidiens (Swannanoa 2 E à 3 km de Lake Eden, Montreat, Asheville) ; mentions du temps dans les bulletins |
| [`lieux/`](lieux/README.md) | les lieux (Blue Ridge Assembly, Lee Hall, Lake Eden, salle à manger, Studies Building, lodges, ferme…) : description, usages, ambiance |
| [`personnes/`](personnes/) | qui est au collège chaque année (fiches du BMC Yearbook : rôle, dates de présence, lien vers la notice) |
| [`ambiance/`](ambiance/) | détails de la vie quotidienne par thème (repas, musique, travail, nature, climat, fêtes…) et chronique mois par mois |
| [`cours/`](cours/README.md) | **réservé** : la progression des cours, traitée séparément |
| [`scripts/`](scripts/) | les scripts qui produisent tout cela |

## Un dossier de jour

1. **Calendrier** : trimestre ou session, vacances.
2. **Météo et lumière** : températures (°C et °F), pluie, neige, phénomènes (brouillard, orage…) ; aube, lever et coucher
   du soleil, crépuscule, à l'heure légale du jour (heure de guerre EWT du 9 février 1942 au 30 septembre 1945) ; phase de
   la lune ; phrases des bulletins des jours suivants qui parlent du temps.
3. **Lieu** : campus du jour et lieux nommés par les sources.
4. **Personnes** : nommées ce jour-là ; présentes au collège d'après les fiches (par rôle).
5. **Planning minuté** : chaque activité avec son heure, ses **pages**, qui, où, sa part déduite et sa source (document
   du collège, Duberman, témoignage, livre, reconstitution) ; puis ce qui est daté sans heure, et les notes courtes des
   documents du collège.
6. **Autour de ce jour** : ce que les sources datent au mois ou à quelques jours près.
7. **Ambiance** : la vie quotidienne du mois et les renvois vers `ambiance/`.
8. **Progression des cours** : la liste des cours du jour, *à compléter* (traitée séparément).
9. **Sources du jour**, avec les liens vers les fiches du musée.

## Régénérer

```
python3 scripts/meteo.py <dossier des .csv.gz de la NOAA>
python3 scripts/mentions_meteo.py <bmc-chronology>/bmc-programmes-aam
python3 scripts/construire.py <clone de RBMIRC/week>
python3 scripts/journee.py 1944-12-04 <clone de RBMIRC/week> <clone de RBMIRC/bmc-chronology>
python3 scripts/sequencier.py 1944-12-04 <clone de RBMIRC/week>
python3 scripts/plans_nature.py 1944-12-04
python3 scripts/page_24h.py 1944-12-04 <clone de RBMIRC/week>/24h
```

`journee.py` lit `journees/AAAA-MM-JJ/donnees_sources.json` (faits relevés à la main, avec source et part déduite) et
`era5_horaire.json` (météo heure par heure, Open-Meteo / ERA5, CC BY 4.0) ; il demande la bibliothèque `ephem`.

Droits : ce dépôt est public. Il ne contient aucun extrait long des livres : seulement nos résumés, avec la
référence et la page ; les citations courtes viennent des documents du collège (Asheville Art Museum). Les relevés de
la NOAA sont du domaine public. Voir [`SOURCES.md`](SOURCES.md).
