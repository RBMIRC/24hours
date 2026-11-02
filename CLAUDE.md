# 24 heures — consignes

Matériaux pour écrire une journée du Black Mountain College en scénario (1 minute = 1 page). Lire `README.md`.

- Écrire en français ; ne pas traduire une source déjà en anglais.
- Toute ligne garde sa source et sa part déduite (0 % = attesté par un document daté) ; ce qui est supposé le dit.
- Source qui fait foi en cas de conflit : document daté attesté > Duberman corrigé > spéculation.
- Dépôt public : pas d'extrait long d'un livre ; résumés avec référence et page ; citations courtes seulement.
- Les fichiers de `jours/`, `lieux/`, `personnes/`, `ambiance/`, `meteo/` et `candidats.md` sont produits par
  `scripts/` : corriger la source (RBMIRC/bmc-chronology) ou le script, puis régénérer, plutôt que de les modifier à la main.
- `cours/` est réservé à la progression des cours (travail séparé, écrit à la main).
- Journée retenue : lundi 4 décembre 1944 (`journees/1944-12-04/`). Les faits relevés à la main vont dans
  `donnees_sources.json` (chacun avec source, part déduite et motif) ; les fichiers 01-09, `README.md` et `journee.json`
  sont produits par `scripts/journee.py`. Les scènes s'écriront ensuite à partir de ces éléments.
- Séquencier : les scènes clés s'écrivent dans `journees/1944-12-04/scenes_cles.json` (fenêtre horaire, lieu, personnages,
  action, source, part déduite, motif, « remplace » = motif des activités du planning qu'elles englobent) ;
  `scripts/sequencier.py` en tire `10_sequencier.md`, `sequencier.csv`, `sequencier.json` (1 440 minutes, sans trou).
- Décision du 2/11/2026 : 1 page = 1 minute, 1 440 pages ; chaque cours ne garde à l'écran que 25 % de sa propre durée
  (`QUOTA_COURS` dans `scripts/sequencier.py`), pour montrer plusieurs cours ou activités dans le même temps réel (montage
  alterné) ; quand les cours simultanés ne remplissent pas le temps, le reste va aux autres activités.
- Page en ligne, en anglais : `index.html` (GitHub Pages, https://rbmirc.github.io/24hours/, copie dans RBMIRC/week/24h/),
  produite par `scripts/page_24h.py` à partir de `sequencier.json` ; les textes anglais des scènes clés sont dans
  `scenes_cles.json` (`t_en`, `lieu_en`, `m_en`) ; types de séquence et lieux : tables TYPES et LIEUX du script.
