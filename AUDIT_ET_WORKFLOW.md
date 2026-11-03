# Audit et workflow — vers un découpage plan par plan, séquence après séquence

Lundi 4 décembre 1944, Lake Eden. Audit du 3 novembre 2026. But : un découpage très poussé et très cinématographique,
plan par plan, séquence après séquence, fondé autant que possible sur des faits avérés. Les cours ne sont pas développés
ici : ils restent des emplacements (25 % de leur durée à l'écran) et seront traités à part (`cours/`).

---

## 1. Résumé

- La structure tient : 1 440 pages sans trou, 315 séquences, un code couleur, 499 plans de nature placés, une heure
  (l'aube) découpée plan par plan.
- Mais hors cours, le film repose encore trop sur la supposition : **424 pages sur 1 165 (36 %) ont une part déduite
  de plus de 40 %**, et seulement **107 pages (9 %) sont attestées** à 10 % ou moins. **21 des 51 scènes clés hors cours
  sont à 50 % ou plus.**
- Une séquence n'est aujourd'hui qu'**une ligne d'action, répétée** à chaque retour du montage alterné (« (suite) »
  jusqu'à 12 fois pour le dîner de Brevard, 10 fois pour l'équipe de ferme ou le charbon). Il n'y a pas encore de
  découpage des séquences humaines.
- La nuit (00:00-04:45, 285 pages) tourne en boucle sur cinq fils sans événement.
- Plusieurs sources riches ne sont pas encore exploitées (bulletins d'octobre et novembre lus en partie, Duberman
  ch. 7-8, entretiens de Mary Emma Harris avec des étudiants de l'automne 1944, journal de Kazin, photographies,
  cartes, presse locale, horaires de train), et quelques erreurs ou approximations sont à corriger (§ 3.4).

Verdict : passer d'un **séquencier de situations** à un **découpage de séquences réelles**. Il faut d'abord élargir et
vérifier la base de faits, puis construire le monde physique et les emplois du temps individuels, et enfin découper
plan par plan, heure par heure, avec des contrôles automatiques à chaque étape.

---

## 2. État des lieux (chiffres)

| élément | état |
|---|---|
| Séquences | 315 : 88 de cours (275 pages), 227 hors cours (1 165 pages) |
| Part déduite hors cours | ≤ 10 % : 107 pages · 11-40 % : 634 pages · > 40 % : 424 pages |
| Scènes clés hors cours | 51, dont 3 à 10 % ou moins, 21 à 50 % ou plus |
| Pages par fil hors cours | nuit 270, ferme 177, Wunsch 129, chaudières 97, cuisine 79, lodges 68, repas 67, aube 37, atelier 35, Albers 34, Kazin 31, disques 24, bibliothèque 23, Cole 23, bureau 18, magasin 11, Dreier 10, Lowinsky 8, linge 6, entretien 6, bulletin 4, courrier 4 |
| Sources des scènes clés | surtout trois documents : 2017.40.172a-g (18 renvois), 2017.40.182.01a-c (13), Silver 2024 (11) ; Lane 1990 seulement 3 fois |
| Faits relevés à la main (`donnees_sources.json`) | 79 : 28 sur les lieux, 8 sur le travail, 9 de routine, 8 sur l'élevage, 7 sur les plantes et la faune, 19 événements de la quinzaine |
| Plans de nature automatiques | 499 : ≤ 25 % : 68 · 30-45 % : 242 · ≥ 50 % : 189 (connaissance générale) |
| Heure de l'aube plan par plan | 80 plans : ≤ 25 % : 2 · 30-45 % : 60 · ≥ 50 % : 18 |

---

## 3. Audit détaillé

### 3.1 Ce qui est solide

- **Le cadre du jour** : bulletin du 4 décembre (2017.40.182.01a-c) et ceux qui l'entourent (181.01, 184), annonces de
  rentrée (172a-g : chambres, studies, logements des enseignants, repas, courrier, téléphone, linge, bibliothèque,
  magasin, consignes), grille de l'automne (176a-h).
- **Les heures** : repas, courrier, bureau, magasin (session 1944-45) ; causerie de Cole à 19 h 15 ; Wunsch à Brevard.
- **La lumière et le ciel** : soleil, lune, planètes et étoiles calculés ; relevés NOAA ; réanalyse ERA5 heure par
  heure avec ses couches de nuages.
- **La ferme** : Silver 2024 (effectifs de 1943, bâtiments, traite à 5 h et 17 h, lait à 7 h 30 et 18 h 15, équipe du
  lundi, Penley).
- **Les personnes** : 136 avec âge, origine, logement, cours suivis, présence.

### 3.2 Ce qui manque pour un découpage cinématographique

1. **Pas de découpage des séquences humaines** : ni plans, ni axes, ni entrées et sorties de champ, ni accessoires.
2. **Pas d'emploi du temps individuel** : rien n'empêche un personnage d'être à deux endroits à la fois
   (Jagna Braunthal à la traite, en Calculus et dans le dortoir…). Aucun contrôle d'ubiquité.
3. **Pas de plan du campus** : distances, chemins, temps de marche, orientation des bâtiments et des fenêtres (utile
   pour la lumière), position du lac, de la ferme, des cottages.
4. **Pas de bible des décors** : intérieurs (mobilier, éclairage, chauffage, matériaux), états du jour (radiateurs,
   givre aux vitres, poussière de charbon).
5. **Pas de bible des costumes, accessoires et sons** : ce que l'on porte en décembre 1944 au collège, objets du jour,
   sons attestés.
6. **Pas de politique de la parole** : que fait-on dire aux personnages, avec quelles garanties.
7. **Horizon réel non calculé** : 8 h 19 et 18 h 20 sont des heures théoriques ; les crêtes de la vallée décalent le
   soleil visible, et différemment selon le lieu (ferme, lodges, lac).

### 3.3 La nuit

- 00:00-04:45 : cinq fils (campus, dortoir des femmes, combles des hommes, Studies Building, ferme) alternés toutes les
  12 minutes, sans événement daté ; puis chaudières, traite, cuisine.
- Il faut soit trouver des faits de nuit (chargement des chaudières, veille incendie, horaires de la cuisine, rondes,
  insomnies racontées dans des souvenirs), soit **assumer une nuit lente** de plans de nature et d'architecture
  (bleu, vert, jaune), en le disant. C'est un choix à trancher (§ 6).

### 3.4 Erreurs, incohérences et points douteux à corriger

| n° | point | ce qu'on a | à faire |
|---|---|---|---|
| 1 | Ciel de l'après-midi | « couvert » partout | ERA5 : 0 % de nuages bas ou moyens, 97-100 % de **nuages hauts** à partir de 7 h ; c'est un voile de cirrostratus, avec un soleil laiteux et des ombres douces (ce qui explique 11,7 °C à Montreat) ; réécrire les motifs C2, C6, M8, T9, W6, les bandeaux d'heure (« overcast ») et les scènes |
| 2 | Appel des repas | gong de rail (Lane 1990, p. 8, souvenir des années 1941-1956) | le bulletin de l'automne 1944 parle de « the dinner bell » (2017.40.173a-c) : prendre la cloche comme attestée, le gong comme variante |
| 3 | Heure des disques | « tenue ce soir-là supposée » (30 %) | 2017.40.176a-h : disques « on Mondays, Wednesdays, Thursdays, Fr[idays] » sous la surveillance de Kazin, Sue Burton et Joan Keiser : le lundi est attesté ; ramener la part déduite à 10-15 % |
| 4 | Présence de Kazin le 4 | Reading Hour et disques avec Kazin | il part pour Washington le 23 novembre (181.01) et parle à la communauté le 11 décembre (184) ; sa présence le 4 n'est pas prouvée : chercher (journal de Kazin, Duberman) ; sinon Sue Burton et Joan Keiser seules aux disques, Reading Hour à 50 % |
| 5 | Cole à Meadows Inn | logé dans le petit appartement de Meadows Inn | Meadows Inn « closed temporarily after November 1 » (172a-g) : vérifier où il loge fin novembre et début décembre |
| 6 | Ensemble de 8 h 30 à 11 h | grille (25 %) | durée anormale (cours d'une demi-heure par semaine dans la liste) : relire le scan de la grille 176a-h |
| 7 | Edwin Woldin | né en 1935 d'après sa fiche (9 ans) | étudiant à l'automne 1944 : date fausse dans la fiche ; chercher la vraie (entretien Harris : « Edwin Judd Woldin, 1944-1946 ») |
| 8 | Bêtes | effectifs de la fin de l'été 1943 | chercher les effectifs de 1944 (documents de ferme cités par Silver, inventaires, bulletins) ; Lady, Pearl, Derek, les taureaux, la chèvre : présents en décembre 1944 ? |
| 9 | Train de Dreier | « train du matin », heure supposée | horaire de la Southern Railway à Black Mountain en décembre 1944 (Official Guide of the Railways) ; savoir qui va le chercher, avec quoi |
| 10 | Brevard | « une soixantaine de kilomètres », départ à 17 h | distance et route réelles en 1944 (environ 70 km par Asheville), moyen de transport (essence rationnée), heure du dîner mensuel ; Wunsch « las et déprimé » d'après sa lettre du 7 décembre (Duberman) : à intégrer au personnage |
| 11 | Décor de Thanksgiving | « peut-être encore en place » (30 %) | vérifier (bulletins suivants, photos) ; sinon le retirer |
| 12 | Chambres | attribution du 30 septembre | changements en cours de trimestre (départs, arrivées : Sam Brown, Betty Kelley…) : croiser avec les bulletins d'octobre et novembre |
| 13 | Penley | ivre, labourant la nuit (souvenir de Zabriskie, 1944-45) | en décembre, sol gelé : pas de labour ; garder le personnage, pas la scène |
| 14 | Station de Swannanoa 2 E | relevés absents ces jours-là | chercher le Climatological Data de Caroline du Nord, décembre 1944 (coopérateurs) ; sinon le signaler dans la fiche météo |
| 15 | Oiseaux et insectes | connaissance générale (50-65 %) | chercher des relevés datés : Christmas Bird Count de la région d'Asheville en décembre 1944, flores et faunes régionales ; remplacer ce qui ne se confirme pas |
| 16 | Annonces du petit-déjeuner | contenu supposé | s'appuyer sur la règle (172a-g) et le calendrier du bulletin du jour ; marquer chaque annonce comme reconstruite |

### 3.5 Sources non exploitées ou exploitées en partie

**Dans le corpus (RBMIRC/bmc-chronology)**

1. **Bulletins d'octobre et novembre 1944** (2017.40.173a-c à 180a-d) : lus seulement pour quelques thèmes. On y
   trouve encore :
   - la cloche du dîner ;
   - l'organisation des pompiers (sirène, raccords de tuyaux, équipe chimique) ;
   - la visite de deux éditeurs de *Life* qui photographient le campus et les gens ;
   - le tabac roulé, les visiteurs ;
   - les consignes du programme de travail (relevés d'heures des équipes) ;
   - la vie des lodges, les soirées du samedi.
2. **Duberman, ch. 7-8** : 25 entrées de septembre 1944 à janvier 1945 dans le semainier, dont :
   - le journal de Kazin du 7 novembre 1944 (l'automne qui s'attarde, l'herbe près de la salle à manger) ;
   - la lettre de Wunsch du 7 décembre (lassitude, dépression) ;
   - Lowinsky et l'intégration à la rentrée ;
   - Miller sur les manières (9 octobre) ;
   - les réunions de la faculté.
3. **Entretiens de Mary Emma Harris**, avec des gens présents à l'automne 1944 :
   - Peggy Bennett (4 faits : salle à manger et ferme, cours avec Kazin et Hansgirg) ;
   - Max Paul (3 : chef des pompiers, exercice d'incendie) ;
   - Edwin Judd Woldin (6) ;
   - Nancy Smith (4) ;
   - Kazin (3).

   Ce sont des souvenirs, avec des citations courtes utilisables.
4. **Silver 2024**, documents de ferme de 1944 : tableau complet de l'équipe de Janet Heling, comptes de production
   (`ferme_silver.json`, 135 documents).
5. **Lane 1990** : les pages de 1944-45 (environ p. 120-170) ne sont exploitées que par fragments ; relecture
   systématique pour les détails sensibles (repas, froid, bruits, lumière, habits).
6. **Images des bulletins** (scans du musée) : mise en page, papier ronéotypé (accessoire du jour).

**Hors corpus, à chercher ou à acquérir**

7. ***Alfred Kazin's Journals*** (éd. Richard M. Cook, Yale, 2011) : entrées de novembre et décembre 1944 à Lake
   Eden. Source de premier ordre pour l'atmosphère, à lire et à citer brièvement.
8. **Photographies** :
   - la séance de *Life* de novembre 1944 (archives de *Life*) ;
   - Josef Breitenbach (été 1944) ;
   - le fonds du Black Mountain College Museum + Arts Center ;
   - les Western Regional Archives (State Archives of North Carolina, Asheville), qui gardent les papiers du collège.

   On en tirera visages, habits, intérieurs, mobilier, état des bâtiments.
9. **Cartes** :
   - cartes topographiques historiques de l'USGS, quadrangle de Black Mountain des années 1930-1940 (TopoView,
     domaine public) : relief, routes, voie ferrée, bâtiments ;
   - modèle numérique de terrain (USGS 3DEP) pour calculer l'horizon réel ;
   - plans du campus (BMC Museum).
10. **Météo** : Local Climatological Data d'Asheville et Climatological Data de Caroline du Nord, décembre 1944
    (NOAA/NCEI, nébulosité, insolation, vent) ; bulletin météo de l'*Asheville Citizen* du 4 et du 5 décembre 1944.
11. **Presse** : *Asheville Citizen* et *Asheville Times* du 2 au 6 décembre 1944. On y cherchera :
    - les nouvelles de la guerre lues ou entendues ce jour-là ;
    - les programmes de radio (WWNC, WISE) et les films à l'affiche ;
    - un éventuel compte rendu de la pièce du 2 décembre au Plaza Theatre.
12. **Chemin de fer** : *Official Guide of the Railways*, décembre 1944 (Southern Railway, ligne Salisbury-Asheville par
    Black Mountain).
13. **Nature** : Christmas Bird Count (National Audubon Society, résultats historiques) ; flore de la Caroline du Nord ;
    état des châtaigniers, pruches, rhododendrons à Lake Eden.

---

## 4. Principes du découpage (à tenir sur toute la journée)

1. **Hiérarchie des sources** : document daté qui couvre ce jour > document de la session ou de la semaine > Duberman
   corrigé > témoignage (Harris, Lane, Kazin) > étude > connaissance générale > supposition. Chaque plan porte sa source
   et sa part déduite.
2. **Parole** : trois sortes de répliques, toujours marquées :
   - **attestée** : citation courte d'un document du collège, d'une lettre ou d'un entretien ;
   - **paraphrasée** : le sens vient d'une source, les mots sont à nous ;
   - **inventée** : nécessaire au jeu, sans prétendre au document ; part déduite élevée.

   Jamais de fausse citation entre guillemets.
3. **Temps réel** : 1 page = 1 minute ; les plans de nature et d'architecture sont pris dans la minute en cours ;
   aucune ellipse.
4. **Pas d'ubiquité** : un personnage n'est qu'à un endroit à la fois ; les déplacements prennent le temps réel du
   plan du campus.
5. **Lumière juste** : chaque plan extérieur doit être compatible avec l'état du soleil et de la lune, l'horizon réel et
   le voile ; chaque intérieur, avec son éclairage (électricité, lampes) et ses fenêtres.
6. **Cours** : emplacements titrés et minutés (25 % de leur durée), sans contenu, jusqu'au travail sur la progression.
7. **Droits** : dépôt public, résumés et citations courtes seulement.

---

## 5. Workflow, point par point

Chaque étape donne : ce qu'on fait · les sources · le fichier produit · le contrôle · le critère de fin.

### Phase A — Corriger et fiabiliser la base

- **A1. Requalifier le ciel.**
  - Ajouter à `journee.json` les couches de nuages ERA5 (bas, moyen, haut) heure par heure.
  - Remplacer « couvert » par « voile de nuages hauts » partout où c'est le cas : catalogue des plans de nature,
    bandeaux, scènes.
  - Prévoir halos, soleil laiteux, ombres douces, rose des cirrus.
  - *Sortie* : `journee.json`, `plans_nature.json`, `scenes_cles.json`.
  - *Contrôle* : aucun motif « ciel couvert bas » valide ce jour-là.
- **A2. Horizon réel.**
  - Télécharger le modèle de terrain (USGS 3DEP ou SRTM) autour de Lake Eden.
  - Calculer, pour six points (lac, ferme, North Lodge, South Lodge, Studies Building, pâturage supérieur), l'heure où le
    soleil apparaît et disparaît derrière les crêtes, et celle de la lune.
  - *Sortie* : `meteo/horizon_lake_eden.csv`, section dans `02_lumiere.md`.
  - *Contrôle* : comparer avec le lever théorique de 8 h 19.
- **A3. Météo officielle.**
  - Chercher le Local Climatological Data d'Asheville et le Climatological Data de Caroline du Nord de décembre 1944,
    et le bulletin météo de l'*Asheville Citizen*.
  - Croiser avec NOAA et ERA5.
  - *Sortie* : `meteo/1944-12_sources_officielles.md`.
- **A4. Corriger les points du § 3.4** un par un : cloche, disques du lundi, présence de Kazin, logement de Cole,
  Ensemble, Woldin, Thanksgiving, Penley, chambres.
  - *Sortie* : `donnees_sources.json` et `scenes_cles.json` corrigés, avec le motif de chaque correction.
  - *Contrôle* : la liste du § 3.4 est soldée, chaque ligne avec sa résolution.
- **A5. Régénérer** dans l'ordre : `journee.py`, `sequencier.py`, `plans_nature.py`, `heure_plan_par_plan.py`,
  `page_24h.py`.
  - *Contrôle* : 1 440 pages, aucune erreur, page testée.

### Phase B — Élargir la base de faits

- **B1. Lire intégralement les bulletins 173a-c à 185.01a-g**, avec les annonces et les rapports de travail.
  - Pour chaque fait, noter : date, inventaire, citation courte, thème (lieu, objet, son, consigne, personne, travail,
    nature), part déduite pour le 4 décembre.
  - *Sortie* : `journees/1944-12-04/faits_bulletins_automne_1944.json`, versé dans `donnees_sources.json`.
  - *Critère* : chaque bulletin relu en entier, liste des faits par bulletin.
- **B2. Duberman, ch. 7-8** : les 25 entrées de septembre 1944 à janvier 1945, et leurs notes.
  - On y prend :
    - l'état de chacun (fatigue de Wunsch, combat de Lowinsky pour l'intégration, autorité d'Albers et de Dreier) ;
    - les tensions de la faculté ;
    - le journal de Kazin.
  - *Sortie* : `personnes_du_jour/etats.md` (une ligne par personne : ce qu'elle porte en elle ce jour-là, source).
- **B3. Entretiens de Mary Emma Harris** : relever tous les faits de l'automne 1944 chez Bennett, Paul, Woldin,
  Nancy Smith, Kazin, et chez tous les autres interviewés présents ce trimestre-là.
  - Garder les citations courtes et le contexte.
  - *Sortie* : `journees/1944-12-04/souvenirs_harris.json`.
- **B4. Ferme 1944.**
  - Documents de Silver (équipes, production, bêtes, travaux de décembre : ensilage, fumier, bois, traite, vêlages).
  - *Sortie* : `journees/1944-12-04/ferme_1944.json`.
  - *Critère* : effectifs probables de décembre 1944, avec leur part déduite.
- **B5. Lane 1990**, pages de 1944-45 : relevé systématique des détails sensoriels (froid, habits, nourriture, bruits,
  odeurs, lumière).
  - *Sortie* : `ambiance/lane_1944-45.md` (résumés et pages).
- **B6. Sources extérieures** :
  - *Asheville Citizen* du 2 au 6 décembre 1944 ;
  - *Official Guide of the Railways* de décembre 1944 ;
  - Christmas Bird Count ;
  - photographies de *Life* (novembre 1944) et de Breitenbach ;
  - cartes de l'USGS ;
  - Western Regional Archives ;
  - BMC Museum + Arts Center.

  Ouvrir une fiche par source : ce qu'elle apporte, où elle est, droits, état de la recherche.
  - *Sortie* : `SOURCES_A_TROUVER.md`.
  - *Critère* : chaque source trouvée, ou déclarée introuvable.
- **B7. Journal de Kazin** (édition de 2011) : entrées de novembre et décembre 1944.
  - *Sortie* : résumés et citations courtes dans `souvenirs_kazin.json`.

### Phase C — Le monde physique

- **C1. Plan du campus en décembre 1944.**
  - Bâtiments, chemins, routes, ponton, barrage, ferme, cottages, orientation, distances, temps de marche.
  - Sources : carte de l'USGS, descriptions (Duberman p. 153-162, Harris 2005, Lane), photos.
  - *Sortie* : `lieux/plan_lake_eden_1944.md` et un plan SVG.
  - *Contrôle* : chaque lieu nommé dans les scènes figure sur le plan.
- **C2. Bible des décors**, une fiche par lieu filmé :
  - liste des lieux : salle à manger et sa véranda, cuisine, office, North Lodge (lobby, chambres, combles), South Lodge
    (lobby, combles, infirmerie, lingerie, Tea Kitchen), Studies Building (study type, Faculty Room, Language Room, hall),
    bibliothèque, bureau, magasin, laiterie, grange, enclos, atelier de bois, Stone Cottage, Mountain Stream, Black Dwarf,
    cottage des Lowinsky, chaudières ;
  - pour chaque lieu : matériaux, mobilier, éclairage, chauffage, fenêtres et orientation, sons, odeurs, état ce jour-là,
    sources et part déduite.
  - *Sortie* : `lieux/decors_1944/<lieu>.md`.
- **C3. Accessoires** :
  - liste : ronéo et stencils du bulletin, enveloppes, carnets de rationnement, fiches de téléphone, téléphone de la
    véranda, casiers du courrier, bidons et seaux de lait, charbon, pelles, brouettes, tracteur Farmall H, camion du
    collège, livres de la bibliothèque, électrophone et disques, cigarettes roulées, lampes de poche, extincteur et sirène ;
  - pour chacun : source, état, à qui il est.
  - *Sortie* : `lieux/accessoires_1944.md`.
- **C4. Costumes** : décembre 1944, rationnement, froid, travail à la ferme ; d'après les photos (*Life*, Breitenbach,
  archives) et les souvenirs.
  - *Sortie* : `personnes_du_jour/costumes.md`, une ligne par personnage principal.
- **C5. Bible sonore**.
  - Sons attestés :
    - cloche du dîner, sirène des pompiers ;
    - téléphone de la véranda ;
    - chorale (Judas Maccabée, répétition du lendemain) ;
    - disques (lesquels ? chercher la discothèque du collège) ;
    - piano, train, bêtes de la ferme, ruisseau, barrage.
  - Sons plausibles : à marquer.
  - Sons absents : ce qu'il ne faut pas entendre en 1944.
  - *Sortie* : `lieux/sons_1944.md`.
- **C6. Lumière intérieure** : électricité (installée par Gisela Kronenberg et Bas Allen, d'après Silver), lampes,
  ampoules (distribuées par Annette Stone, Bas Allen, Mac Wood), feu des cheminées.
  - *Sortie* : section de la bible des décors.

### Phase D — Les personnages

- **D1. Fiche par personnage principal**, une trentaine :
  - liste : Braunthal, Gropius, Heling, Schmitt, Woldin, Swackhamer, Forberg, McLaughlin, Osbourne, Kelley, Bauer,
    Bennett, Paul, Jane Stone, Ann MacKinnon, Albers, Anni Albers, Dreier, Wunsch, Jalowetz, Lowinsky, Miller, les
    Hansgirg, Zabriskie, Kazin, Mary Gregory, Cole, Nell Rice, Annette Stone, Bas Allen, Mac Wood, Penley ;
  - contenu : âge, origine, logement, apparence (photos), voix et accent (réfugiés allemands et autrichiens,
    personnel local), travail, relations, état du moment (B2), sources.
  - *Sortie* : `personnes_du_jour/<nom>.md`.
- **D2. Emploi du temps individuel, minute par minute**, pour chaque personnage principal : où il est, ce qu'il fait,
  d'après les sources (cours à l'emplacement réservé, équipes, repas, chambres).
  - *Sortie* : `personnes_du_jour/emplois_du_temps.json`.
  - *Contrôle automatique* (script) :
    - personne n'est à deux endroits en même temps ;
    - les trajets tiennent dans le temps de marche du plan C1 ;
    - chaque présence a sa source.
- **D3. Registre des paroles** : tout ce qui a été dit ou écrit par chacun en ces jours-là.
  - Liste : citations du bulletin, lettres (Duncan Dwight, Malek, Martin), causerie de Cole (titres), propos de Miller,
    discours de rentrée, entretiens.
  - Règles de réplique (§ 4.2).
  - *Sortie* : `personnes_du_jour/paroles.json`.

### Phase E — Restructurer le séquencier

- **E1. Des séquences réelles plutôt que des situations.**
  - Pour chaque séquence hors cours, fixer :
    - début et fin réels, enjeu ;
    - action concrète, en trois à six temps ;
    - personnages exacts (D2), lieu exact (C1, C2) ;
    - sources et part déduite.
  - Supprimer les retours « (suite) » sans évolution : chaque retour doit montrer un temps nouveau de l'action.
  - *Sortie* : `scenes_cles.json` réécrit (champ `temps` : liste des temps de l'action, chacun avec sa source).
- **E2. La nuit** : soit des faits (chaudières, veille, cuisine, ferme, insomnies), soit une nuit lente assumée, faite
  de plans de nature et d'architecture.
  - *Sortie* : décision écrite dans `CLAUDE.md`, puis découpage de 00:00 à 04:45.
- **E3. Règles du montage alterné** : continuité des personnages (D2), raccords de regard et de son entre lieux voisins,
  durée minimale d'un retour (au moins un temps d'action nouveau).
- **E4. Les cours** restent des emplacements (titre, salle, enseignant, inscrits, 25 %), marqués « à traiter ».

### Phase F — Découpage plan par plan, séquence après séquence

- **F1. Format du découpage des séquences humaines**, qui étend celui de l'aube.
  - Champs de chaque plan :
    - n°, timecode, durée ;
    - échelle, angle, mouvement, optique, point ;
    - lumière (source, direction, qualité) ;
    - personnages dans le champ, entrées et sorties ;
    - action ;
    - réplique (texte, type attestée, paraphrasée ou inventée, source) ;
    - son (dans le champ, hors champ, off) ;
    - accessoires, costumes ;
    - raccord ;
    - registre (code couleur), source, part déduite, motif.
  - *Sortie* : `journees/1944-12-04/sequences/<hh>h_<séquence>.json`.
  - *Script* : extension de `heure_plan_par_plan.py`.
- **F2. Ordre de travail**, des heures les mieux attestées aux moins attestées :
  1. 07:20-08:30 (l'aube est faite ; ajouter lait, petit-déjeuner, annonces, chambres) ;
  2. 18:00-20:30 (dîner, cloche, annonce, disques, causerie de Cole, Reading Hour) ;
  3. 10:30-11:30 (levée et arrivée du courrier, lettres, téléphone, retour de Dreier) ;
  4. 12:30-16:00 (déjeuner, magasin, bureau, après-midi de travail : ferme, charbon, chaudières, atelier) ;
  5. 04:45-07:20 (traite, cuisine, chaudières, aube) ;
  6. 16:00-18:00 (traite du soir, cuisine, bibliothèque, départ de Wunsch) ;
  7. 20:30-24:00 (eukinétique, Brevard, retour de Wunsch, lodges, lever de lune) ;
  8. 00:00-04:45 (la nuit, selon E2).
- **F3. Plans de nature et d'architecture** dans chaque séquence : reprendre les plans automatiques et les écrire à la
  main, comme pour l'aube (variété d'échelles, de mouvements et de raccords ; rimes d'une heure à l'autre).
- **F4. Contrôles automatiques** à chaque heure découpée :
  - timecodes croissants, sans chevauchement ; 3 600 secondes par heure ;
  - personnages conformes à D2 ;
  - lumière conforme au calcul et à l'horizon réel ; météo conforme à l'heure ;
  - chaque plan avec source et part déduite, chaque inventaire existant ;
  - aucune citation sans source.
- **F5. Cible par heure** : 60 à 150 plans selon l'heure ; part déduite moyenne hors cours d'au plus 30 % ; au moins une
  source datée par séquence.

### Phase G — Vérification

- **G1. Vérification automatique** des plans à 25 % ou moins : le fait cité doit se retrouver dans le texte de la source
  (comme `verifier_sources.py`).
- **G2. Relecture humaine** : liste des doutes, scène par scène ; corrections tracées.
- **G3. Traduction anglaise** de tout ce qui est nouveau (textes `_en`), relue, pour la page.

### Phase H — Publication

- **H1. Page en ligne** :
  - pour chaque heure découpée, vue « plan par plan » complète (tous les champs de F1) ;
  - code couleur, filtres par personnage, lieu, registre, type de plan ;
  - minuteur qui suit la lecture.
- **H2. Export scénario** : format Fountain, puis PDF, d'une page par minute (1 440 pages), avec en-têtes de scène et
  numéros de plan ; les plans de cours restent des pages réservées.
- **H3. Historique** : un commit par heure découpée, avec le bilan des parts déduites.

---

## 6. Décisions

Prises le 3 novembre 2026 :

1. **Nuit** : nuit lente assumée, très découpée (plans de 3 à 8 s, variété de points de vue, de mouvements, de détails).
2. **Répliques, cours, dialogues** : plus tard ; on définit les blocs temporels et leur fréquence (rythme du film), sans les
   développer.
3. **Animaux et plantes** : connaissance générale (Amérique du Nord, Caroline du Nord, Appalaches, saison, jour et nuit),
   appuyée sur Black Mountain Ecologies (`nature/`).
4. **Sources extérieures** : l'auteur s'en charge ; elles restent en attente (§ 3.5, points 7 à 13 ; phase B6-B7).
5. **Caméra** : d'aujourd'hui, omnisciente, virtuose, mais dans les standards du découpage.

Questions telles qu'elles étaient posées :

1. **La nuit** : chercher des faits de nuit, ou assumer une nuit lente de plans de nature et d'architecture ?
2. **La parole** : jusqu'où inventer des répliques (marquées « inventée ») ? Ou se limiter aux paroles attestées et
   paraphrasées ?
3. **La connaissance générale** (oiseaux, insectes, mammifères) : la garder à 50-65 % en attendant des relevés datés, ou
   la retirer ?
4. **Les sources à acquérir** : journal de Kazin, presse d'Asheville, *Official Guide*, photos de *Life* : qui les
   cherche, et comment ?
5. **Le langage de caméra** : toute la grammaire moderne (zoom, vertigo, macro), ou une grammaire « 1944 » (optiques et
   mouvements de l'époque) ?

---

## 7. Indicateurs de suivi

| indicateur | aujourd'hui | cible |
|---|---|---|
| Pages hors cours à plus de 40 % de part déduite | 424 (36 %) | moins de 15 % |
| Pages hors cours attestées (≤ 10 %) | 107 (9 %) | plus de 30 % |
| Scènes clés hors cours à 50 % ou plus | 21 sur 51 | moins de 8 |
| Heures découpées plan par plan | 1 (nature seule) | 24 (hors contenu des cours) |
| Retours « (suite) » sans action nouvelle | tous | aucun |
| Contrôle d'ubiquité | absent | 0 conflit |
| Lever et coucher sur l'horizon réel | non | oui, pour six points |
| Points du § 3.4 résolus | 0 sur 16 | 16 sur 16 |
