# Lundi 4 décembre 1944 — la journée du scénario

Structure des éléments dont le scénario a besoin (1 minute = 1 page : 00:00 = page 1, 23:59 = page 1440). Chaque élément a son fichier ; `journee.json` les réunit. Les faits relevés à la main sont dans `donnees_sources.json` ; tout est régénéré par `python3 scripts/journee.py 1944-12-04 <week> <bmc-chronology>`.

| élément | fichier | contenu | état |
|---|---|---|---|
| Météo | [01_meteo.md](01_meteo.md) | relevés NOAA (une semaine avant et après), heure par heure ERA5, phrases des bulletins | rempli |
| Lumière | [02_lumiere.md](02_lumiere.md) | aubes, lever 08:19, coucher 18:20, lune (gibbeuse décroissante, 77 %), heure par heure | rempli |
| Lieux | [03_lieux.md](03_lieux.md) | bâtiments et leur usage cet automne-là, chambres des étudiants, cottages des enseignants, ferme, lac, hors campus | rempli |
| Personnes | [04_personnes.md](04_personnes.md) | 136 personnes, dont 53 à présence attestée ; âge, origine, logement, cours, travail | rempli |
| Cours | [05_cours.md](05_cours.md) | 11 cours ce lundi (heures, pages, inscrits), cours offerts et suivis du trimestre | rempli |
| Routine | [06_routine.md](06_routine.md) | repas, courrier, bureau, magasin, ménage, traite, lait, linge, chaudières | rempli |
| Espace animal et végétal | [07_faune_flore.md](07_faune_flore.md) | bêtes de la ferme, plantes, arbres, animaux sauvages | rempli, en partie supposé |
| Événements | [08_evenements.md](08_evenements.md) | la quinzaine, le courrier du jour, la situation du collège, le monde | rempli |
| Progression des cours | [09_progression_des_cours.md](09_progression_des_cours.md) | place réservée | à faire |
| Séquencier | [10_sequencier.md](10_sequencier.md) | les scènes de 00:00 à 23:59 en temps réel (1 440 pages), avec lieu, lumière, personnages, action, source et part déduite ; `sequencier.csv`, `sequencier.json` (scripts/sequencier.py, à partir de `scenes_cles.json`) | liste faite |
| Plans de nature | [11_plans_nature.md](11_plans_nature.md) | plans de coupe qui rythment le montage (montagnes, ciel, astres, lumière, eau, givre, arbres et vent, oiseaux, bêtes, insectes, fumées, sons), placés minute par minute ; catalogue `plans_nature.json`, `plans_nature_montage.csv/json` (scripts/plans_nature.py) | premier découpage |
| L'heure de l'aube, plan par plan | [12_aube_plan_par_plan.md](12_aube_plan_par_plan.md) | 07:20-08:20, 80 plans de nature écrits à la main en quatre mouvements : échelle, angle, mouvement, optique, mise au point, raccord, son, source et part déduite (`aube_plan_par_plan.json`, scripts/heure_plan_par_plan.py) | fait |
| Scènes écrites | — | dialogues et didascalies, scène par scène | à faire |

## Règles

- Chaque fait porte sa source et sa part déduite (0 % = écrit tel quel dans un document daté qui couvre ce jour).
- Ce qui vient d'une autre date ou d'une autre année le dit, avec une part déduite plus forte ; la connaissance générale (hors sources du collège) est à 30-60 %.
- Dépôt public : résumés et citations courtes ; pas d'extrait long des livres.
