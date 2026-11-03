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
- Plans de nature : catalogue des motifs dans `journees/1944-12-04/plans_nature.json` (catégorie, échelle, texte fr/en, son,
  durée en secondes, conditions de validité — moment, heures, ciel, température, vent —, lieux d'affinité, source, part
  déduite) ; `scripts/plans_nature.py` les place (coupes, respirations, ponts de lumière ; 10 emplois au plus par motif)
  → `11_plans_nature.md`, `plans_nature_montage.csv/json` ; ils prennent quelques secondes à la séquence en cours sans
  décaler l'horloge. Ordre de régénération : journee.py, sequencier.py, plans_nature.py, page_24h.py.
- Heures découpées plan par plan, à la main : `journees/1944-12-04/<nom>_plan_par_plan.json` (vocabulaire des échelles,
  angles, mouvements, optiques, mises au point, raccords ; mouvements de l'heure ; plans avec timecode, durée, codes,
  texte fr/en, son, source, part déduite) ; `scripts/heure_plan_par_plan.py` contrôle (pas de chevauchement, codes connus)
  et écrit `12_<nom>_plan_par_plan.md` ; sur la page, ces plans remplacent les plans automatiques de leur fenêtre.
  Fait : l'aube, 07:20-08:20 (80 plans).
- Code couleur (décision du 3/11/2026), table REGISTRES de `scripts/page_24h.py` : bleu et ses nuances = architecture sans
  personne ; vert = nature, bêtes et végétal ; rouge = scènes collectives (enseignement, repas, soirées, travail, vie commune) ;
  jaune = vues larges (nature, bâtiments, figures dans le paysage) ; violet = dialogues ; rose = une personne seule qui lit,
  écrit, travaille. Chaque scène clé porte son `registre` dans `scenes_cles.json` ; les activités du planning et les plans
  de nature le reçoivent par règle (plan large → jaune ; fenêtres, fumées de cheminée → bleu ; sinon vert selon le sujet).
  Les couleurs des types de séquence en dérivent ; lieux, bandeaux d'heure, barre des heures et part déduite restent neutres.
