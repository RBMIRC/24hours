"""La nuit lente découpée plan par plan (décision du 3/11/2026) : plans de 3 à 8 secondes, grande variété de points de vue,
de mouvements et de détails.

Usage : python3 scripts/nuit_plans.py AAAA-MM-JJ
Sortie : journees/AAAA-MM-JJ/nuit_plan_par_plan.json (même format que aube_plan_par_plan.json, avec "compact": true),
contrôlé et mis en fiche par scripts/heure_plan_par_plan.py.

Méthode : la nuit est faite de phrases de 5 à 12 plans autour d'un foyer (le ciel, le lac, le givre, un arbre, la ferme,
les animaux, un bâtiment vide, un dortoir) ; dans une phrase, l'échelle progresse (du plan d'ensemble au très gros plan,
retour au large) ; points de vue, mouvements et optiques tournent sans se répéter ; la durée d'un plan va de 3 à 8 s,
modulée par une houle lente (le tempo respire sur une dizaine de minutes). Conditions vérifiées à chaque plan : position
de la lune et des astres (ephem), ciel (ERA5 : clair jusque vers 6 h, voile de nuages hauts le soir), température.
Les animaux et les plantes viennent de la connaissance générale du milieu (décembre, Appalaches du Sud), appuyée sur
nature/seasonal_calendar.json et nature/bmc_ecology_1933_1957.json ; part déduite 40 à 60 %."""
import datetime as dt, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construire as K
import ephem

ROOT = K.ROOT
PLAFOND_DETAIL = 45      # emplois au plus d'un même détail dans la nuit
FENETRES = [("00:00:00", "04:45:00"), ("23:00:00", "24:00:00")]
MOUVEMENTS = [
    ("00:00:00", "01:15:00", "N1. La lune haute — le campus sous une lune aux trois quarts, à l'est puis au sud-est ; givre, silence, dormeurs.",
     "N1. The high moon — the campus under a three-quarter moon, east then southeast; frost, silence, sleepers."),
    ("01:15:00", "02:45:00", "N2. Le gel — le froid descend au fond de la vallée ; le givre pousse, les aiguilles de glace montent, les bêtes se serrent.",
     "N2. The frost — the cold settles into the valley floor; hoarfrost grows, needle ice rises, the animals huddle."),
    ("02:45:00", "03:45:00", "N3. Jupiter — la planète se lève sur la crête de l'est ; Orion bascule vers le sud-ouest ; les chouettes.",
     "N3. Jupiter — the planet rises over the eastern ridge; Orion tilts toward the southwest; the owls."),
    ("03:45:00", "04:45:00", "N4. Avant les lampes — la lune au plus haut, au sud ; les chaudières ; les premiers gestes de la ferme se préparent.",
     "N4. Before the lamps — the moon at its highest, to the south; the furnaces; the first farm chores are getting ready."),
    ("23:00:00", "24:00:00", "N5. Le retour de la nuit — sous le voile, sans étoiles ; la lune levée à 22 h 52, simple lueur ; le sol regèle, les lumières s'éteignent.",
     "N5. Night returns — under the veil, no stars; the moon, risen at 10:52 p.m., only a glow; the ground freezes again, the lights go out."),
]
VOCAB_PLUS = {
    "echelle": {},
    "angle": {"aerien": ["vue aérienne (drone)", "aerial (drone)"], "sous_eau": ["sous l'eau, sous la glace", "underwater, under the ice"],
              "subjectif": ["point de vue d'un animal", "animal point of view"]},
    "mouvement": {"drone": ["vol de drone", "drone flight"], "steadicam": ["steadicam", "steadicam"], "motion": ["motion control (mouvement répétable, lent)", "motion control (slow, repeatable)"],
                  "slider": ["petit travelling macro", "macro slider"], "circulaire": ["travelling circulaire", "orbit"]},
    "optique": {"14": ["grand angle 14 mm", "14 mm ultra-wide"], "135": ["135 mm", "135 mm"], "ana": ["anamorphique 40 mm", "40 mm anamorphic"], "mpe": ["macro à fort grossissement (x5)", "5x high-magnification macro"]},
    "point": {"split": ["dioptre fractionné (deux plans nets)", "split diopter (two planes sharp)"]},
    "raccord": {},
}

# Foyers : (id, catégorie, registre de près, registre en large, lieu, poids, condition, source, part déduite, son fr/en, détails [(fr, en, échelles)])
# condition : "clair" (nuit claire), "voile" (nuit voilée), "jupiter" (après 2 h 50), "arcturus" (après 4 h 15), None
E_LARGE, E_MOY, E_PRES = ["TPE", "PE", "PL"], ["PM", "PR"], ["GP", "TGP"]
FOYERS = [
 ('lune', 'astres', 'NAT_EAU', 'LARGE_NAT', 'le ciel', 3, 'clair', 'calcul ephem ; ERA5 (ciel clair)', 15, ('', ''), [
   ('La lune gibbeuse, à {lune} : sa lumière fait briller le givre comme du sel.', 'The gibbous moon, {lune_en}: its light makes the frost glitter like salt.', ['TPE', 'PE', 'PL']),
   ("Gros plan de la lune aux trois quarts, ses mers grises nettes dans l'air sec.", 'Close-up of the three-quarter moon, its gray maria sharp in the dry air.', ['GP']),
   ('Le halo bleuâtre de la lune sur le givre du toit du North Lodge.', 'The bluish glow of the moon on the frost of the North Lodge roof.', ['PM', 'PL']),
   ('La lune dans une flaque gelée, déformée par les bulles prises dans la glace.', 'The moon in a frozen puddle, distorted by the bubbles trapped in the ice.', ['GP', 'TGP']),
   ('Contre-jour lunaire : la silhouette de la grange et des silos.', 'Moon backlight: the silhouette of the barn and the silos.', ['PE', 'PL']),
   ("Ombres portées par la lune : les poteaux de la clôture s'allongent sur le pâturage blanc.", 'Moon shadows: the fence posts stretch across the white pasture.', ['PL', 'PM']),
   ("La lune entre deux branches nues ; elle glisse d'une branche à l'autre pendant le plan.", 'The moon between two bare branches; it slides from one branch to the next during the shot.', ['PM', 'PL']),
 ]),
 ('orion', 'astres', 'NAT_EAU', 'LARGE_NAT', 'le ciel', 2, 'clair', 'calcul ephem', 15, ('', ''), [
   ('Orion au-dessus de la crête sud : Bételgeuse orange, Rigel bleue, les trois étoiles du baudrier.', 'Orion above the southern ridge: orange Betelgeuse, blue Rigel, the three stars of the belt.', ['TPE', 'PE', 'PL']),
   ("Sirius, basse, scintille et change de couleur près de l'horizon.", 'Sirius, low, twinkles and changes color near the horizon.', ['PL', 'GP']),
   ('Capella très haute, presque au zénith, jaune pâle.', 'Capella very high, almost at the zenith, pale yellow.', ['PL', 'GP']),
   ("Procyon et Pollux au-dessus de l'est, de part et d'autre de la lune.", 'Procyon and Pollux above the east, on either side of the moon.', ['PE', 'PL']),
   ("Le ciel d'hiver entier, d'un horizon à l'autre, la Voie lactée effacée par la lune.", 'The whole winter sky, horizon to horizon, the Milky Way washed out by the moon.', ['TPE']),
   ('Saturne, point jaune fixe, au milieu des étoiles qui scintillent.', 'Saturn, a fixed yellow point among the twinkling stars.', ['GP', 'PL']),
   ('Aldébaran et les Pléiades très haut, presque au zénith.', 'Aldebaran and the Pleiades very high, almost at the zenith.', ['PL', 'PE']),
 ]),
 ('jupiter', 'astres', 'NAT_EAU', 'LARGE_NAT', 'le ciel', 3, 'jupiter', 'calcul ephem (Jupiter se lève vers 2 h 45, magnitude −1,8)', 20, ('', ''), [
   ("Jupiter monte au-dessus de la crête de l'est, la plus brillante des étoiles.", 'Jupiter climbs above the eastern ridge, the brightest star in the sky.', ['TPE', 'PE', 'PL']),
   ('Jupiter se reflète dans le lac noir, un trait tremblé.', 'Jupiter reflected in the black lake, a trembling streak.', ['PL', 'PM']),
   ("Jupiter derrière les aiguilles d'un pin blanc.", 'Jupiter behind the needles of a white pine.', ['PM', 'GP']),
 ]),
 ('arcturus', 'astres', 'NAT_EAU', 'LARGE_NAT', 'le ciel', 1, 'arcturus', "calcul ephem (Arcturus se lève à l'est-nord-est)", 20, ('', ''), [
   ('Arcturus, orangée, se lève au-dessus des Seven Sisters.', 'Orange Arcturus rises above the Seven Sisters.', ['TPE', 'PE', 'PL']),
 ]),
 ('meteore', 'astres', 'NAT_EAU', 'LARGE_NAT', 'le ciel', 1, 'clair', 'connaissance générale (Géminides : maximum vers le 13 décembre, quelques météores dès le début du mois)', 60, ('', ''), [
   ('Un météore traverse le ciel au-dessus du lac, une seconde.', 'A meteor crosses the sky above the lake, for one second.', ['TPE', 'PE']),
 ]),
 ('voile', 'ciel', 'NAT_EAU', 'LARGE_NAT', 'le ciel', 3, 'voile', 'ERA5 (nuages hauts) ; calcul ephem (lune levée à 22 h 52)', 40, ('', ''), [
   ("Pas une étoile : le voile de nuages hauts, à peine éclairé par la lune qui monte à l'est.", 'Not a star: the high veil of cloud, barely lit by the moon climbing in the east.', ['TPE', 'PE', 'PL']),
   ("Une lueur pâle à l'est, derrière la crête : la lune dans le voile.", 'A pale glow to the east, behind the ridge: the moon inside the veil.', ['PE', 'PL']),
   ('La silhouette des Seven Sisters, à peine plus noire que le ciel.', 'The outline of the Seven Sisters, barely darker than the sky.', ['TPE', 'PE']),
 ]),
 ('lac', 'eau', 'NAT_EAU', 'LARGE_NAT', 'le lac', 3, None, 'Lane 1990, p. 132, 136-137 ; Duberman 1972, p. 153-162', 35, ('ruisseau, craquements de glace', 'stream, ice cracking'), [
   ('Le lac noir comme une plaque ; {reflet}.', 'The lake black as a plate; {reflet_en}.', ['TPE', 'PE', 'PL']),
   ('La glace fine qui se forme au bord, en lames ; les roseaux pris dedans.', 'Thin ice forming at the edge in blades; the reeds caught in it.', ['GP', 'TGP', 'PM']),
   ("Sous la glace, l'eau noire bouge encore ; une bulle passe.", 'Under the ice the black water still moves; a bubble drifts past.', ['TGP', 'GP']),
   ("Les fils de brume qui commencent à se lever de l'eau, plus chaude que l'air.", 'Threads of mist beginning to rise from the water, warmer than the air.', ['PL', 'PM']),
   ('La rive opposée, noire, avec les pruches.', 'The far shore, black, with the hemlocks.', ['PE', 'PL']),
   ('Une feuille morte prise dans la glace naissante.', 'A dead leaf caught in the forming ice.', ['TGP', 'GP']),
   ('Le ponton de la salle à manger, ses planches blanches de givre.', 'The dining hall dock, its planks white with frost.', ['PM', 'PL']),
   ("Le barrage : l'eau qui déborde est le seul bruit de la vallée.", 'The dam: the overflowing water is the only sound in the valley.', ['PM', 'PL']),
   ("Un triton vert, actif tout l'hiver, nage lentement sous la glace mince.", 'A green newt, active all winter, swims slowly under the thin ice.', ['TGP', 'GP']),
 ]),
 ('ruisseau', 'eau', 'NAT_EAU', 'LARGE_NAT', 'le ruisseau du bureau', 2, None, 'Lane 1990, p. 138-139 ; nature/seasonal_calendar.json (salamandres actives en décembre)', 40, ('gargouillis', 'gurgling'), [
   ('Le ruisseau du bureau entre les pierres glacées, sous les rhododendrons.', 'The office stream between iced stones, under the rhododendrons.', ['PM', 'GP']),
   ("Une collerette de glace autour d'une pierre ; l'eau passe dessous.", 'A collar of ice around a stone; the water runs beneath it.', ['TGP', 'GP']),
   ('Sous une pierre soulevée, une salamandre à ventre noir, immobile.', 'Under a lifted stone, a black-bellied salamander, motionless.', ['TGP']),
   ('Dans une vasque du ruisseau, une truite de ruisseau tient sa place contre le courant.', 'In a pool of the stream, a brook trout holds its place against the current.', ['GP', 'TGP']),
 ]),
 ('givre', 'givre', 'NAT_EAU', 'LARGE_NAT', 'le pâturage', 3, None, 'NOAA (−8,3 °C à Montreat) ; ERA5', 30, ('', ''), [
   ('Le pâturage blanc sous la lune.', 'The pasture white under the moon.', ['TPE', 'PE', 'PL']),
   ("Le givre qui pousse : des aiguilles se forment sur un brin d'herbe, à vue d'œil.", 'Hoarfrost growing: needles forming on a blade of grass before our eyes.', ['TGP']),
   ("Les cristaux de givre sur le bord d'une feuille de rhododendron roulée.", 'Frost crystals along the edge of a rolled rhododendron leaf.', ['TGP']),
   ('Le pâturage supérieur, sa crête blanche contre le ciel étoilé.', 'The upper pasture, its white crest against the starry sky.', ['PE', 'PL']),
   ('Le givre sur le capot du camion du collège.', 'Frost on the hood of the college truck.', ['GP', 'PM']),
   ('Les traces de pas de la veille, durcies par le gel sur le chemin.', "Yesterday's footprints, hardened by the frost on the path.", ['GP', 'PM']),
   ('Le fil de la clôture, fourré de givre, file vers la ferme.', 'The fence wire, furred with frost, runs off toward the farm.', ['GP', 'PM']),
   ('Une feuille morte de chêne, bordée de cristaux.', 'A dead oak leaf edged with crystals.', ['TGP']),
   ('Une flaque qui gèle : la glace avance du bord vers le centre.', 'A puddle freezing: the ice creeps from the edge toward the center.', ['GP', 'TGP']),
   ("Les aiguilles de glace soulèvent la terre rouge d'une ornière.", 'Needle ice lifting the red earth of a rut.', ['TGP', 'GP']),
 ]),
 ('arbres', 'arbres', 'NAT_VEG', 'LARGE_NAT', 'les bois du lac', 3, None, 'Lane 1990, p. 138-139, 160-166, 194-196 ; nature/bmc_ecology_1933_1957.json (flore de 1944)', 35, ('feuilles sèches, aiguilles', 'dry leaves, needles'), [
   ('Les rhododendrons, feuilles roulées en cigare par le gel, pendantes.', 'The rhododendrons, their leaves rolled into cigars by the frost, hanging down.', ['GP', 'PM']),
   ("Les feuilles sèches d'un hêtre frémissent à une rafale.", 'The dry leaves of a beech shiver in a gust.', ['GP', 'PM']),
   ("Les branches nues d'un chêne blanc, réseau noir sur les étoiles.", 'The bare branches of a white oak, a black web against the stars.', ['PL', 'GP']),
   ('Un érable rouge, ses bourgeons serrés, déjà rouges en décembre.', 'A red maple, its tight buds already red in December.', ['GP', 'TGP']),
   ('Le cornouiller, ses bourgeons de fleurs en petits boutons gris.', 'The dogwood, its flower buds like small gray buttons.', ['TGP', 'GP']),
   ('Les pruches noires le long du ruisseau ; la lune dans leurs branches.', 'The black hemlocks along the stream; the moon in their branches.', ['PL', 'PM']),
   ('Un pin blanc : les aiguilles chuintent dans le vent de nord-ouest.', 'A white pine: the needles hiss in the northwest wind.', ['GP', 'PM']),
   ("Le tronc gris d'un châtaignier mort, dressé sous les étoiles.", 'The gray trunk of a dead chestnut, standing under the stars.', ['PL', 'PM', 'PE']),
   ("Les capsules d'un tulipier en silhouette contre le ciel.", 'The seed heads of a tulip poplar silhouetted against the sky.', ['GP', 'PM']),
 ]),
 ('sousbois', 'arbres', 'NAT_VEG', 'LARGE_NAT', 'le sous-bois', 2, None, 'nature/seasonal_calendar.json (décembre : hamamélis en fleur, fougères de Noël vertes) ; Duberman 1972, p. 169 (galax, laurier)', 45, ('', ''), [
   ("L'hamamélis en fleur en plein décembre : des rubans jaunes, givrés.", 'Witch hazel in bloom in December: yellow ribbons, frosted.', ['TGP', 'GP']),
   ('Une fougère de Noël, restée verte sous le givre.', 'A Christmas fern, still green under the frost.', ['GP', 'TGP']),
   ('Les feuilles mortes sous les arbres, raidies par le gel.', 'Dead leaves under the trees, stiffened by the frost.', ['GP', 'PM']),
   ('Un lichen gris-vert sur une branche tombée.', 'A gray-green lichen on a fallen branch.', ['TGP']),
   ('Les tiges sèches de la friche, chacune gainée de givre.', 'The dry stalks of the old field, each sheathed in frost.', ['GP', 'PM']),
   ("Les feuilles de galax, rouge bronze, au bord de l'allée.", 'Galax leaves, bronze-red, at the edge of the path.', ['GP']),
   ('La mousse sur une pierre, chaque brin poudré de blanc.', 'Moss on a stone, every sprig powdered white.', ['TGP']),
   ('Le laurier des montagnes, vert sombre, luisant sous la lune.', 'Mountain laurel, dark green, gleaming under the moon.', ['PM', 'GP']),
 ]),
 ('chouettes', 'oiseaux', 'NAT_ANI', 'LARGE_NAT', 'les bois', 2, None, 'nature/seasonal_calendar.json (petit-duc, grand-duc, chouette rayée en décembre) ; nature/bmc_ecology_1933_1957.json (petit-duc relevé en 1944)', 50, ('hululements', 'hoots'), [
   ('Un grand-duc sur une branche morte, les aigrettes dressées ; décembre est sa saison des chants.', 'A great horned owl on a dead branch, ear tufts raised; December is its calling season.', ['PM', 'GP']),
   ("La chouette rayée appelle ; l'autre lui répond de l'autre rive.", 'The barred owl calls; another answers from the far shore.', ['PL', 'SON']),
   ('Les yeux jaunes du grand-duc, puis il tourne la tête vers le lac.', "The great horned owl's yellow eyes, then it turns its head toward the lake.", ['TGP', 'GP']),
   ("Une plume de chouette accrochée à l'écorce.", 'An owl feather caught on the bark.', ['TGP']),
   ("Un petit-duc gris, immobile contre l'écorce : on ne le voit que quand il ouvre les yeux.", 'A gray screech owl, still against the bark: you see it only when it opens its eyes.', ['GP', 'TGP']),
   ("Le vol muet d'une chouette qui traverse le clair de lune.", 'The silent flight of an owl crossing the moonlight.', ['PL', 'PM']),
 ]),
 ('mammiferes', 'betes', 'NAT_ANI', 'LARGE_NAT', 'la lisière', 2, None, 'nature/bmc_ecology_1933_1957.json (lynx roux, campagnol, taupe, musaraigne relevés en 1944) ; connaissance générale', 55, ('', ''), [
   ("Un lynx roux traverse la lisière du pâturage, s'arrête, repart.", 'A bobcat crosses the edge of the pasture, stops, moves on.', ['PL', 'PM']),
   ('Un renard roux trotte sur le givre et laisse une ligne de traces.', 'A red fox trots across the frost and leaves a line of tracks.', ['PL', 'PM']),
   ('Les traces du lynx roux sur le givre, rondes, sans griffes.', "The bobcat's tracks on the frost, round, without claw marks.", ['GP', 'TGP']),
   ("Les monticules d'une taupe, durcis par le gel.", "A mole's hills, hardened by the frost.", ['GP', 'PM']),
   ("Un raton laveur au bord du ruisseau, les pattes dans l'eau froide.", 'A raccoon at the edge of the stream, its paws in the cold water.', ['PM', 'GP']),
   ("Un campagnol sort d'un tunnel sous l'herbe gelée et y rentre.", 'A vole comes out of a tunnel under the frozen grass and goes back in.', ['TGP', 'GP']),
   ("Une musaraigne file entre deux touffes, trop vite pour l'objectif.", 'A shrew darts between two tufts, too fast for the lens.', ['TGP']),
   ('Un opossum fouille près de la décharge du collège, les yeux rouges.', 'An opossum noses around the college dump, its eyes red.', ['PM', 'GP']),
   ('Dans une fente de la grange, une chauve-souris en hibernation, couverte de rosée gelée.', 'In a crack in the barn, a hibernating bat covered in frozen dew.', ['TGP']),
 ]),
 ('ferme', 'betes', 'NAT_ANI', 'LARGE_BAT', 'la ferme', 3, None, 'Silver 2024, ch. 6, p. 89-97 (bâtiments et bêtes de 1943-1944)', 35, ('souffles, paille', 'breathing, straw'), [
   ('La grange et les deux silos de tuiles sous la lune.', 'The barn and the two tile silos under the moon.', ['TPE', 'PE', 'PL']),
   ("Les vaches couchées dans l'étable, la buée de leur souffle.", 'The cows lying in the barn, the steam of their breath.', ['PM', 'GP']),
   ('Le bidon de lait vide retourné sur le muret de la laiterie.', 'The empty milk can upturned on the low wall of the milking house.', ['GP']),
   ('La chèvre des Dreier, couchée dans la paille.', "The Dreiers' goat lying in the straw.", ['PM', 'GP']),
   ("L'abreuvoir de la ferme qui gèle par les bords.", 'The farm trough freezing at the edges.', ['GP', 'TGP']),
   ("Le silo vu d'en bas, ses tuiles ocre sous la lune.", 'The silo seen from below, its ochre tiles under the moon.', ['PL', 'PM']),
   ('Les porcs serrés les uns contre les autres dans la paille.', 'The hogs packed tight together in the straw.', ['PM', 'GP']),
   ("Les poules sur leur perchoir, têtes sous l'aile.", 'The hens on their perch, heads under their wings.', ['GP', 'PM']),
   ('Le taureau angus noir, debout dans son enclos, du givre sur le dos.', 'The black Angus bull standing in his pen, frost on his back.', ['PM']),
   ('Les canards du collège serrés au bord du lac, sur une plaque de glace.', 'The college ducks huddled at the lake edge, on a plate of ice.', ['PM', 'GP']),
   ('Lady et Pearl, debout, endormies, une jambe repliée.', 'Lady and Pearl standing asleep, one leg cocked.', ['PM', 'GP']),
 ]),
 ('salle', 'lumiere', 'ARCH_NUIT', 'LARGE_BAT', 'la salle à manger', 2, None, '2017.40.172a-g (véranda, courrier, téléphone, panneaux) ; Horowitz & Danilowitz 2009, p. 122', 35, ('', ''), [
   ('La salle à manger éteinte, sa véranda grillagée au-dessus du lac.', 'The dark dining hall, its screened porch above the lake.', ['TPE', 'PE', 'PL']),
   ('Les chaises de bois retournées sur les tables.', 'The wooden chairs turned upside down on the tables.', ['PM', 'GP']),
   ('La porte de la cuisine, et le seau de déchets pour les porcs.', 'The kitchen door, and the bucket of scraps for the hogs.', ['GP', 'PM']),
   ('La scène de la salle à manger, le rideau tiré : on y jouera Plaute samedi.', 'The dining hall stage, the curtain drawn: Plautus will be played there on Saturday.', ['PM', 'PL']),
   ('Les grands plateaux empilés près du passe-plat.', 'The big trays stacked by the serving hatch.', ['GP']),
   ('Le téléphone mural de la véranda, et la pile de fiches pour noter les appels.', 'The porch wall telephone, and the stack of slips for logging calls.', ['GP', 'TGP']),
   ("Les panneaux d'affichage : les annonces du jour, punaisées.", "The bulletin boards: the day's notices, pinned up.", ['GP']),
   ('La cuisine : les fourneaux qui refroidissent, les casseroles pendues.', 'The kitchen: the stoves cooling, the pans hanging.', ['PM', 'GP']),
   ('La cloche du dîner, immobile, givrée.', 'The dinner bell, still, frosted.', ['GP']),
   ('Les casiers du courrier sur la véranda, vides, une lettre oubliée.', 'The mail boxes on the porch, empty, one forgotten letter.', ['GP', 'PM']),
 ]),
 ('studies', 'lumiere', 'ARCH_NUIT', 'LARGE_BAT', 'le Studies Building', 2, None, 'Díaz 2014, p. 2 ; 2017.40.172a-g (studies)', 35, ('', ''), [
   ('Le Studies Building, blanc sur ses pilotis, sous la lune.', 'The Studies Building, white on its piles, under the moon.', ['TPE', 'PE', 'PL']),
   ('Le long couloir des studies, les portes fermées.', 'The long corridor of studies, the doors closed.', ['PL', 'PM']),
   ('La rampe du Studies Building, une ligne de givre sous la lune.', 'The Studies Building railing, a line of frost under the moon.', ['GP', 'TGP']),
   ("Le hall d'entrée : la boîte aux lettres du Studies Building.", 'The front hall: the Studies Building mail box.', ['GP', 'PM']),
   ('La Language Room vide, le tableau effacé.', 'The empty Language Room, the blackboard wiped clean.', ['PM']),
   ('La Faculty Room, chaises en cercle.', 'The Faculty Room, chairs in a circle.', ['PM']),
   ("Les pilotis du bâtiment dans l'eau gelée.", "The building's piles in the frozen water.", ['GP', 'PM']),
   ('Un study vide : la chaise et le plan de travail du collège, un pull sur le dossier.', 'An empty study: the college chair and writing surface, a sweater on the back.', ['PM', 'GP']),
 ]),
 ('lodges', 'lumiere', 'ARCH_NUIT', 'LARGE_BAT', 'les lodges', 2, None, '2017.40.172a-g (chambres, combles, buanderie)', 35, ('', ''), [
   ('Le North Lodge, son toit blanc de givre, les lucarnes des combles.', 'North Lodge, its roof white with frost, the attic dormers.', ['TPE', 'PE', 'PL']),
   ('La véranda du South Lodge ; dessous, la buanderie et la machine à laver.', 'The South Lodge porch; beneath it, the laundry room and the washing machine.', ['PL', 'PM']),
   ('Le lobby du North Lodge, salon des étudiantes, la cheminée éteinte.', "The North Lodge lobby, the women's sitting room, the fireplace cold.", ['PM', 'PL']),
   ('La salle de repassage du South Lodge, le fer posé sur sa plaque.', 'The South Lodge ironing room, the iron resting on its stand.', ['GP', 'PM']),
   ('La Tea Kitchen : une bouilloire, deux tasses retournées.', 'The Tea Kitchen: a kettle, two cups upside down.', ['GP']),
   ('La boîte des objets trouvés sous la véranda du North Lodge.', 'The lost-and-found box under the North Lodge porch.', ['GP']),
   ('Le lobby du South Lodge : les chaises de la Reading Hour, un livre resté ouvert.', 'The South Lodge lobby: the Reading Hour chairs, a book left open.', ['PM', 'GP']),
 ]),
 ('cottages', 'lumiere', 'ARCH_NUIT', 'LARGE_BAT', 'les cottages', 1, None, '2017.40.172a-g (Stone Cottage, Black Dwarf, Mountain Stream, Meadows Inn fermée)', 40, ('', ''), [
   ('Le Stone Cottage des Hansgirg, un filet de fumée de la cheminée.', "The Hansgirgs' Stone Cottage, a thread of smoke from the chimney.", ['PL', 'PM']),
   ('Black Dwarf Cottage dans les arbres.', 'Black Dwarf Cottage among the trees.', ['PL']),
   ("Mountain Stream, la fenêtre de l'étage où loge Kazin.", 'Mountain Stream, the upstairs window where Kazin lodges.', ['PL', 'PM']),
   ('Le cottage des Jalowetz, dessiné par Kocher, dans les arbres.', "The Jalowetzes' cottage, designed by Kocher, among the trees.", ['PL']),
   ('Meadows Inn, volets fermés depuis le 1er novembre.', 'Meadows Inn, shuttered since November 1.', ['PL', 'PM']),
 ]),
 ('bureau', 'lumiere', 'ARCH_NUIT', 'LARGE_BAT', 'le bureau', 1, None, '2017.40.181.01a-c, 2017.40.182.01a-c (le bulletin ronéotypé)', 40, ('', ''), [
   ('Le bureau : la machine à ronéotyper, un stencil du bulletin n° 11 encore dessus.', 'The office: the mimeograph machine, a stencil of Bulletin No. 11 still on it.', ['GP', 'PM']),
   ("Les piles d'enveloppes adressées aux amis du collège.", 'The stacks of envelopes addressed to the friends of the college.', ['GP', 'TGP']),
   ('Le standard téléphonique du bureau, ses fiches.', 'The office switchboard and its plugs.', ['GP']),
 ]),
 ('chaudiere', 'fumees', 'ARCH_NUIT', 'LARGE_BAT', 'les chaudières', 2, None, '2017.40.177a-g, 2017.40.178a-d, 2017.40.179a-d (chaudières au charbon, équipe des chaudières)', 40, ('ronflement, radiateurs', 'roar, radiators'), [
   ('La porte de la chaudière : la lueur rouge du charbon derrière la grille.', 'The furnace door: the red glow of the coal behind the grate.', ['GP', 'TGP']),
   ('Le tas de charbon, givré sur le dessus, noir dessous.', 'The coal pile, frosted on top, black beneath.', ['PM', 'GP']),
   ('La pelle à charbon plantée dans le tas.', 'The coal shovel stuck in the pile.', ['GP']),
   ('La cendre rouge qui tombe sous la grille.', 'Red ash dropping beneath the grate.', ['TGP', 'GP']),
   ('Un radiateur du lodge qui claque en se dilatant.', 'A lodge radiator ticking as it expands.', ['GP', 'SON']),
   ("La fumée de la cheminée de chaufferie, droite dans l'air calme.", 'Smoke from the boiler-room chimney, straight in the still air.', ['PL', 'PM']),
 ]),
 ('ateliers', 'lumiere', 'ARCH_NUIT', 'LARGE_BAT', "l'atelier de bois", 1, None, 'Silver 2024, ch. 6 (atelier de bois de Molly Gregory)', 40, ('', ''), [
   ("L'atelier de bois : les outils à leur clou, la sciure sur l'établi.", 'The woodshop: the tools on their nails, sawdust on the bench.', ['PM', 'GP']),
   ('Le hangar à machines : le tracteur, la charrue à disques.', 'The machinery shed: the tractor, the disk plow.', ['PL', 'PM']),
 ]),
 ('dortoir_f', 'lodges', 'COL_VIE', 'COL_VIE', 'le North Attic', 2, None, '2017.40.172a-g (huit étudiantes dans le North Attic)', 45, ('souffles, un ressort de lit', 'breathing, a bedspring'), [
   ('Les lits du North Attic sous le toit en pente, huit formes sous les couvertures.', 'The North Attic beds under the sloping roof, eight shapes under the blankets.', ['PL', 'PM']),
   ('Une main qui pend hors du lit.', 'A hand hanging out of a bed.', ['GP']),
   ('Une couverture de laine rayée, une épaule qui bouge.', 'A striped wool blanket, a shoulder that stirs.', ['GP']),
   ('Le clair de lune sur le plancher des combles, en carré.', 'Moonlight on the attic floor, in a square.', ['PM', 'GP']),
   ('Des lettres et un paquet de cigarettes sur une caisse retournée.', 'Letters and a pack of cigarettes on an upturned crate.', ['GP', 'TGP']),
   ('Des chaussures de travail alignées près de la porte, la terre rouge séchée dessus.', 'Work shoes lined up by the door, dried red earth on them.', ['GP']),
   ('Un réveil sur une caisse : il sonnera à 4 h 45.', 'An alarm clock on a crate: it will ring at 4:45.', ['GP', 'TGP']),
   ("Des fougères de givre à l'intérieur d'une lucarne.", 'Frost ferns on the inside of a dormer window.', ['TGP', 'GP']),
 ]),
 ('dortoir_h', 'lodges', 'COL_VIE', 'COL_VIE', 'les combles du South Lodge', 2, None, '2017.40.172a-g (onze étudiants dans les combles)', 45, ('souffles', 'breathing'), [
   ('Les combles du South Lodge : onze lits, une respiration régulière.', 'The South Lodge attics: eleven beds, steady breathing.', ['PL', 'PM']),
   ('Un livre ouvert sur une couverture, la page qui se soulève.', 'A book open on a blanket, its page lifting.', ['GP']),
   ('Une veste de travail pendue à un clou, la poussière de charbon dans les plis.', 'A work jacket hanging on a nail, coal dust in the folds.', ['GP']),
   ('Un dormeur se retourne ; le lit grince.', 'A sleeper turns over; the bed creaks.', ['PM', 'GP']),
   ('La lucarne des combles : la lune, puis plus rien.', 'The attic dormer: the moon, then nothing.', ['GP', 'PM']),
   ('Une cigarette roulée éteinte dans une soucoupe.', 'A hand-rolled cigarette, out, in a saucer.', ['TGP', 'GP']),
 ]),
 ('sons', 'sons', 'NAT_SON', 'NAT_SON', 'la vallée', 1, None, 'connaissance générale', 55, ('', ''), [
   ('Sur noir : le silence, puis un craquement de bois gelé.', 'Over black: silence, then the crack of frozen wood.', ['SON']),
   ('Sur noir : un chien aboie très loin, vers les fermes voisines.', 'Over black: a dog barks far away, toward the neighboring farms.', ['SON']),
   ("Sur noir : la glace du lac qui craque d'une rive à l'autre.", 'Over black: the lake ice cracking from shore to shore.', ['SON']),
   ("Sur noir : le cri bref d'un renard.", 'Over black: the short bark of a fox.', ['SON']),
   ('Sur noir : un train de la Southern siffle dans la vallée de la Swannanoa.', 'Over black: a Southern train whistles in the Swannanoa valley.', ['SON']),
 ]),
]

MVTS = ["fixe"] * 9 + ["pano", "tilt", "trav_lat", "trav_lat", "trav_av", "trav_ar", "zoom_av", "zoom_ar", "grue", "drone", "drone", "steadicam", "steadicam",
        "motion", "motion", "slider", "slider", "circulaire", "portee", "vertigo"]
ANGLES = {"TPE": ["face", "aerien", "crete", "contre"], "PE": ["face", "aerien", "plongee", "crete"], "PL": ["face", "contre", "plongee", "eau", "sol", "reflet"],
          "PM": ["face", "sol", "travers", "plongee", "contre"], "PR": ["face", "travers", "contre"], "GP": ["face", "sol", "travers", "zenith", "contre", "reflet"],
          "TGP": ["sol", "face", "zenith", "sous_eau", "travers"], "SON": ["face"]}
OPTIQUES = {"TPE": ["600", "300", "14", "ana"], "PE": ["300", "35", "18", "ana", "14"], "PL": ["25", "35", "50", "ana", "18"], "PM": ["50", "85", "35", "135"],
            "PR": ["85", "135"], "GP": ["85", "135", "300", "macro"], "TGP": ["macro", "mpe"], "SON": ["50"]}
POINTS = {"TPE": ["infini", "profond"], "PE": ["profond", "infini"], "PL": ["profond", "split", "court"], "PM": ["court", "bascule", "profond", "split"],
          "PR": ["court", "bascule"], "GP": ["court", "bascule", "flou_net"], "TGP": ["court", "flou_net", "bascule"], "SON": ["court"]}
DIRS = ["nord", "nord-est", "est", "sud-est", "sud", "sud-ouest", "ouest", "nord-ouest"]
DIRS_EN = ["north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest"]


import re
INTERIEUR = re.compile(r"cuisine|chaises|plateaux|scène|lobby|couloir|study|Faculty|Language|radiateur|repassage|Tea Kitchen|téléphone|panneaux|casiers|"
                       r"tableau|boîte|bouilloire|lits|combles|couverture|réveil|chaussures|main qui|livre|cigarette|veste|lucarne|plancher|lettres|dormeur|"
                       r"ronéotyper|enveloppes|standard|outils|hangar|étable|perchoir|porte de la chaudière|cendre|pelle|fourneaux", re.I)
EAU = re.compile(r"\beau\b|glace|truite|triton|salamandre|ruisseau|lac\b|flaque|abreuvoir|barrage|pilotis", re.I)
REFLET = re.compile(r"\beau\b|glace|lac\b|flaque|vitre|lucarne|fenêtre|abreuvoir|ponton", re.I)


def compatibles(det, angles, mouvements):
    """angles et mouvements possibles pour ce sujet : pas de drone ni de vue aérienne à l'intérieur, pas de plan sous l'eau
    hors de l'eau, pas de reflet sans eau, glace ou vitre."""
    inter = bool(INTERIEUR.search(det[0])); eau = bool(EAU.search(det[0])); refl = bool(REFLET.search(det[0]))
    a = [x for x in angles if not ((x in ("aerien", "crete") and inter) or (x == "sous_eau" and not eau) or (x == "reflet" and not refl) or (x == "eau" and not eau))]
    m = [x for x in mouvements if not (x in ("drone", "grue") and inter)]
    return a or ["face"], m or ["fixe"]


def sec(tc): h, m, s = map(int, tc.split(":")); return h * 3600 + m * 60 + s
def tc(s): return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def main(jour):
    dos = os.path.join(ROOT, "journees", jour); d = dt.date.fromisoformat(jour)
    A = json.load(open(os.path.join(dos, "aube_plan_par_plan.json"), encoding="utf-8"))
    J = json.load(open(os.path.join(dos, "journee.json"), encoding="utf-8"))
    era = {int(x["heure"][:2]): x for x in J["meteo"]["era5_par_heure"]}
    V = json.loads(json.dumps(A["vocabulaire"]))
    for k, v in VOCAB_PLUS.items(): V[k].update(v)
    o = ephem.Observer(); o.lat, o.lon, o.elevation = str(K.LAT), str(K.LON), 650
    off = K.decalage(d)[0]; rnd = random.Random(19441204)
    def astres(s):
        o.date = dt.datetime(d.year, d.month, d.day) + dt.timedelta(seconds=s, hours=-off)
        m, j, a = ephem.Moon(o), ephem.Jupiter(o), ephem.star("Arcturus"); a.compute(o)
        return math.degrees(m.alt), math.degrees(m.az), math.degrees(j.alt), math.degrees(a.alt)
    def ok(f, s):
        cond = f[6]; h = min(23, s // 3600); w = era.get(h, {})
        clair = (w.get("nuages_pct", 0) < 40)
        lal, laz, jal, aal = astres(s)
        if cond == "clair" and not clair: return False
        if cond == "voile" and clair: return False
        if cond == "jupiter" and (jal < 3 or not clair): return False
        if cond == "arcturus" and (aal < 3 or not clair): return False
        if f[0] == "lune" and lal < 5: return False
        if f[0] in ("orion", "meteore") and not clair: return False
        return True
    plans, dernier_foyer, usage, util = [], [], {}, {}
    for a0, a1 in FENETRES:
        t, fin = sec(a0), sec(a1)
        while t < fin:
            cands = [f for f in FOYERS if ok(f, t) and f[0] not in dernier_foyer[-3:] and not (f[0] == "meteore" and usage.get("meteore", 0) >= 3)]
            poids = [f[5] / (1 + usage.get(f[0], 0) * 0.15) for f in cands]
            f = rnd.choices(cands, poids)[0]; usage[f[0]] = usage.get(f[0], 0) + 1; dernier_foyer.append(f[0])
            n = min(rnd.randint(5, 12), 2 * len(f[10]), 2 if f[0] == "meteore" else 99)
            prev_e = prev_mv = prev_o = None
            for k in range(n):
                if t >= fin: break
                # échelle : ouverture large, détails, fermeture large ; la phrase des sons reste en son seul
                details = f[10]
                if k == 0: pool = [x for x in details if set(x[2]) & set(E_LARGE + ["SON"])] or details
                elif k == n - 1: pool = [x for x in details if set(x[2]) & set(E_LARGE + E_MOY + ["SON"])] or details
                else: pool = details
                pool = [x for x in pool if util.get(x[0], 0) < PLAFOND_DETAIL] or pool
                pool = sorted(pool, key=lambda x: util.get(x[0], 0))[:max(2, len(pool) // 2 + 1)]
                det = rnd.choice(pool); util[det[0]] = util.get(det[0], 0) + 1
                es = [e for e in det[2] if e != prev_e] or det[2]; e = rnd.choice(es)
                ang_ok, mv_ok = compatibles(det, ANGLES[e], MVTS)
                mv = "fixe" if e == "SON" else rnd.choice([m for m in mv_ok if m != prev_mv] or mv_ok)
                if e in ("TGP",) and mv in ("drone", "grue", "vertigo"): mv = rnd.choice(["slider", "fixe", "motion"])
                if e in ("TPE", "PE") and mv in ("slider",): mv = "drone"
                ang = rnd.choice(ang_ok); opt = rnd.choice([x for x in OPTIQUES[e] if x != prev_o] or OPTIQUES[e]); pt = rnd.choice(POINTS[e])
                if mv == "drone" and e in E_LARGE and "aerien" in ang_ok: ang = "aerien"
                houle = 0.5 + 0.5 * math.sin(t / 600 * math.pi)            # le tempo respire sur une vingtaine de minutes
                base = {"TPE": 7, "PE": 6.5, "PL": 6, "PM": 5, "PR": 5, "GP": 4.5, "TGP": 4, "SON": 6}[e]
                dur = max(3, min(8, round(base + (houle - 0.5) * 3 + rnd.uniform(-1, 1))))
                dur = min(dur, fin - t)
                if dur < 3 and plans: plans[-1]["d"] += dur; t += dur; break
                lal, laz, jal, aal = astres(t); w = era.get(min(23, t // 3600), {})
                di = DIRS[int((laz + 22.5) // 45) % 8]; di_en = DIRS_EN[int((laz + 22.5) // 45) % 8]
                rep = {"lune": f"{round(lal)}° au-dessus de l'horizon, au {di}", "lune_en": f"{round(lal)}° above the horizon, to the {di_en}",
                       "reflet": "la lune s'y reflète, à peine tremblée" if lal > 5 and w.get("nuages_pct", 0) < 40 else "aucun reflet sous le voile",
                       "reflet_en": "the moon reflected in it, barely trembling" if lal > 5 and w.get("nuages_pct", 0) < 40 else "no reflection under the veil"}
                fr, en = det[0].format(**rep), det[1].format(**rep)
                reg = f[3] if e in E_LARGE else f[2]
                cat = f[1] if e != "SON" else "sons"
                r = "cut"
                if k == n - 1: r = rnd.choice(["cut", "franche", "son_av", "fondu", "rime"]) if rnd.random() < 0.6 else "cut"
                elif rnd.random() < 0.12: r = rnd.choice(["mvt", "forme", "lumiere", "son_ap"])
                plans.append({"tc": tc(t), "d": dur, "seq": "nuit", "e": e, "a": ang, "mv": mv, "o": opt, "p": pt, "r": r, "cat": cat, "reg": reg,
                              "fr": fr, "en": en, "son": f[9][0] if e != "SON" else "son seul", "son_en": f[9][1] if e != "SON" else "sound only",
                              "src": f[7], "pct": f[8], "m": "plan généré (nuit lente) ; " + ("calculé" if f[1] == "astres" else "connaissance générale du milieu" if f[8] >= 45 else "usage attesté transposé"),
                              "foyer": f[0], "lieu": f[4], "temp_c": w.get("temp_c"), "lune_alt": round(lal)})
                prev_e, prev_mv, prev_o = e, mv, opt; t += dur
    D = {"_lisezmoi": __doc__.split("\n\n")[0].strip() + " Généré par scripts/nuit_plans.py (graine fixe : le même découpage à chaque passage).",
         "titre": "La nuit lente, plan par plan", "compact": True, "vocabulaire": V,
         "mouvements": [{"de": a, "a": b, "fr": fr, "en": en} for a, b, fr, en in MOUVEMENTS], "plans": plans}
    json.dump(D, open(os.path.join(dos, "nuit_plan_par_plan.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    tot = sum(p["d"] for p in plans)
    print(f"{len(plans)} plans, {tot} s ({tot / 3600:.2f} h), durée moyenne {tot / len(plans):.1f} s ; foyers : " + ", ".join(f"{k} {v}" for k, v in sorted(usage.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(sys.argv[1])
