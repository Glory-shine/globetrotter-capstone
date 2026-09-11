"""Seeds the destinations table with real Bafoussam places on first startup
(idempotent — skipped if the table already has rows).

Sourcing notes
--------------
Names, locations, and descriptions are grounded in public references about
Bafoussam (Wikipedia, Wikivoyage, ORTOC — the West Cameroon regional
tourism office — and Wikimedia Commons' "Category:Bafoussam" photo
archive). Coordinates are careful estimates placing each site within its
correct part of the city (verified against Bafoussam's known center at
~5.478°N, 10.418°E and its three communes — Bafoussam I, II/Baleng,
III/Bamougoum) rather than surveyed GPS fixes; treat them as
demo-appropriate, not survey-grade.

Entry fees and activity prices are realistic estimates for a city where
most small sites don't publish an official price list — calibrated
against the one documented public tariff (shared taxi fares, see
app/fare.py) and typical regional museum/heritage-site pricing.

Photos are hotlinked directly from Wikimedia Commons via `Special:FilePath`
(https://commons.wikimedia.org/wiki/Category:Bafoussam and
.../Category:Chefferie_de_Bafoussam) rather than downloaded/redistributed —
the browser fetches them straight from Commons, and virtually everything
in that category is contributor-licensed for reuse.
"""

from urllib.parse import quote

from app.database import SessionLocal
from app.models import Destination


def commons(filename: str, width: int = 1000) -> str:
    """Build a Wikimedia Commons hotlink URL for a real photo, resized via
    Commons' own thumbnail service."""
    encoded = quote(filename.replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width={width}"


CENTRE_VILLE = "Bafoussam I (Centre-ville)"
BALENG = "Bafoussam II (Baleng)"
BAMOUGOUM = "Bafoussam III (Bamougoum)"

MOCK_DESTINATIONS = [
    dict(
        id="dest-001", name="Chefferie Supérieure de Bafoussam", country=CENTRE_VILLE,
        category="Chefferie", tags=["chefferie", "culture", "histoire"],
        avg_cost_per_day=2000,
        description="Résidence du chef supérieur des Bafoussam, ce palais royal bâti selon la tradition "
                     "bamiléké porte plus de huit siècles d'histoire de la dynastie, depuis le fondateur "
                     "Fo Njouvoum jusqu'au roi actuel.",
        best_season="Toute l'année (fermé lors des cérémonies privées)",
        latitude=5.4740, longitude=10.4130, rating=4.7, price_range_xaf="2 000 - 5 000 FCFA",
        media_main=commons("Case sacrée chefferie bafoussam.jpg"),
        media_secondary=[commons("Maison sacré chefferie bafoussam.jpg")],
        activities=[
            {"name": "Visite guidée du palais royal", "price": "2 000 FCFA"},
            {"name": "Visite avec accès à la forêt sacrée", "price": "5 000 FCFA"},
        ],
        anecdote=(
            "On raconte que le trône du roi ne doit jamais être touché par une personne étrangère à la cour sous peine de malédiction — même les photographes gardent leurs distances !"
        ),
    ),
    dict(
        id="dest-002", name="Musée de la Chefferie Bafoussam", country=CENTRE_VILLE,
        category="Musée", tags=["culture", "histoire"],
        avg_cost_per_day=1000,
        description="Installé dans l'enceinte royale, ce musée retrace l'histoire de la dynastie Bafoussam "
                     "depuis les années 1400 à travers objets royaux, tenues cérémonielles et récits des "
                     "migrations bamiléké.",
        best_season="Toute l'année",
        latitude=5.4742, longitude=10.4132, rating=4.6, price_range_xaf="1 000 FCFA",
        media_main=commons("Musée - Chefferie Bafoussam.jpg"),
        activities=[
            {"name": "Visite guidée du musée", "price": "1 000 FCFA"},
            {"name": "Guide privé (français/anglais)", "price": "3 000 FCFA"},
        ],
        anecdote=(
            "Certains objets exposés ici auraient plus de 400 ans et n'ont changé de gardien qu'une poignée de fois depuis leur fabrication, toujours transmis de notable en notable."
        ),
    ),
    dict(
        id="dest-003", name="Musée des Calebasses", country=CENTRE_VILLE,
        category="Musée", tags=["culture", "artisanat"],
        avg_cost_per_day=1000,
        description="Une collection originale de calebasses sculptées et décorées, objets emblématiques de "
                     "l'art décoratif bamiléké utilisés lors des grandes cérémonies traditionnelles.",
        best_season="Toute l'année",
        latitude=5.4745, longitude=10.4125, rating=4.3, price_range_xaf="1 000 FCFA",
        media_main=commons("Musée des calebasses.jpg"),
        media_secondary=[commons("Musée des calebasses 2.jpg")],
        activities=[{"name": "Visite libre", "price": "1 000 FCFA"}],
        anecdote=(
            "Chez les Bamiléké, offrir une calebasse sculptée à un futur époux était autrefois un signe d'engagement plus solennel qu'une bague — on ne la brisait jamais, même en cas de dispute."
        ),
    ),
    dict(
        id="dest-004", name="Forêt Sacrée de la Chefferie", country=CENTRE_VILLE,
        category="Nature", tags=["nature", "chefferie", "religieux"],
        avg_cost_per_day=1500,
        description="Espace boisé considéré comme sacré au sein du domaine royal, où se déroulent certains "
                     "rites traditionnels bamiléké à l'abri des regards profanes.",
        best_season="Saison sèche (Novembre - Mars)",
        latitude=5.4735, longitude=10.4120, rating=4.2, price_range_xaf="1 500 FCFA (avec guide)",
        media_main=commons("Foret sacrée chefferie Bafoussam.jpg"),
        activities=[{"name": "Visite accompagnée", "price": "1 500 FCFA"}],
        anecdote=(
            "Il est dit que seuls les initiés connaissent le chemin exact à travers la forêt sacrée — les autres, même nés à Bafoussam, s'y perdraient volontairement par respect."
        ),
    ),
    dict(
        id="dest-005", name="Marché A (Grand Marché de Bafoussam)", country=CENTRE_VILLE,
        category="Marché", tags=["marche", "artisanat", "famille", "gratuit"],
        avg_cost_per_day=0,
        description="Le plus grand marché de Bafoussam, cœur battant du commerce de la ville : vivres, "
                     "tissus, artisanat et vie urbaine bamiléké au quotidien.",
        best_season="Toute l'année, tous les jours",
        latitude=5.4770, longitude=10.4200, rating=4.4, price_range_xaf="Entrée gratuite",
        media_main=commons("Entrée principale Marché A (1).jpg"),
        media_secondary=[commons("Entrée principale marché - Bafoussam.jpg")],
        activities=[{"name": "Visite libre du marché", "price": "Gratuit"}],
        anecdote=(
            "Le Marché A ne ferme presque jamais : certaines vendeuses de vivres y tiennent le même emplacement depuis plus de trente ans, transmis de mère en fille."
        ),
    ),
    dict(
        id="dest-006", name="Marché B", country=CENTRE_VILLE,
        category="Marché", tags=["marche", "artisanat", "gratuit"],
        avg_cost_per_day=0,
        description="Second grand marché de la ville, plus artisanal, réputé pour ses étals de vivres "
                     "frais et ses ateliers de couturiers et de forgerons.",
        best_season="Toute l'année",
        latitude=5.4805, longitude=10.4230, rating=4.1, price_range_xaf="Entrée gratuite",
        media_main=commons("Marché B, Bafoussam.jpg"),
        activities=[{"name": "Visite libre du marché", "price": "Gratuit"}],
        anecdote=(
            "Au Marché B, les forgerons artisanaux façonnent encore certains outils agricoles à la main, exactement comme leurs grands-parents le faisaient avant l'arrivée de l'acier importé."
        ),
    ),
    dict(
        id="dest-007", name="Chutes de la Metché", country=BAMOUGOUM,
        category="Nature", tags=["nature", "aventure", "panorama"],
        avg_cost_per_day=1500,
        description="Chute d'eau nichée dans un écrin de verdure aux abords de Bamougoum, un site prisé "
                     "pour la randonnée et les baignades en saison sèche.",
        best_season="Saison sèche (Novembre - Mars)",
        latitude=5.4150, longitude=10.3950, rating=4.6, price_range_xaf="1 500 FCFA",
        media_main=commons("Les chutes de la metché.jpg"),
        activities=[
            {"name": "Randonnée guidée jusqu'aux chutes", "price": "1 500 FCFA"},
            {"name": "Accès à la zone de baignade", "price": "1 000 FCFA"},
        ],
        anecdote=(
            "Les habitants racontent que l'eau des Chutes de la Metché ne tarit jamais, même durant les pires sécheresses — un signe, disent certains, que l'esprit du lieu veille sur la ville."
        ),
    ),
    dict(
        id="dest-008", name="Monument Wanko", country=CENTRE_VILLE,
        category="Monument", tags=["histoire", "gratuit", "panorama"],
        avg_cost_per_day=0,
        description="Monument emblématique érigé au cœur d'un carrefour animé de Bafoussam, devenu un "
                     "repère incontournable pour se situer en ville.",
        best_season="Toute l'année",
        latitude=5.4760, longitude=10.4190, rating=4.0, price_range_xaf="Accès libre",
        media_main=commons("Monument Wanko.jpg"),
        media_secondary=[commons("Monument Wanko1.jpg")],
        activities=[],
        anecdote=(
            "Le rond-point du Monument Wanko est devenu si célèbre comme point de repère que les chauffeurs de taxi l'utilisent pour donner des indications, même pour des destinations situées à l'autre bout de la ville."
        ),
    ),
    dict(
        id="dest-009", name="Gare Routière de Bafoussam (Ndiangdam)", country=CENTRE_VILLE,
        category="Transport", tags=["gratuit", "famille"],
        avg_cost_per_day=0,
        description="Principale gare routière de la ville, point de départ des agences de voyage vers "
                     "Yaoundé, Douala, Foumban et les autres villes de l'Ouest.",
        best_season="Toute l'année",
        latitude=5.4700, longitude=10.4250, rating=3.9, price_range_xaf="Accès libre",
        media_main=commons("Gare routière bafoussam- ndiangdam.jpg"),
        activities=[],
        anecdote=(
            "À la gare routière, il n'est pas rare de voir un même bus attendre patiemment que le dernier siège se remplisse avant de partir — parfois plusieurs heures, coca et arachides à l'appui."
        ),
    ),
    dict(
        id="dest-010", name="Stade Lécfo'o de la Chefferie", country=CENTRE_VILLE,
        category="Sport", tags=["sport", "famille"],
        avg_cost_per_day=500,
        description="Stade omnisports situé dans le domaine de la chefferie, utilisé pour les compétitions "
                     "locales de football et les grands rassemblements populaires.",
        best_season="Toute l'année",
        latitude=5.4750, longitude=10.4140, rating=4.0, price_range_xaf="500 - 2 000 FCFA selon événement",
        media_main=commons("Stade LECFO'O de la chefferie Bafoussam (2).jpg"),
        activities=[{"name": "Billet match local", "price": "500 FCFA"}],
        anecdote=(
            "Lors des grands matchs, le Stade Lécfo'o peut faire trembler tout le quartier chefferie sous les chants et les tambours des supporters — on l'entend parfois depuis le centre-ville."
        ),
    ),
    dict(
        id="dest-011", name="Paroisse du Sacré-Cœur de Ndiendam", country=CENTRE_VILLE,
        category="Religieux", tags=["religieux", "gratuit"],
        avg_cost_per_day=0,
        description="Église paroissiale au cœur du quartier Ndiendam, un lieu de culte et de vie "
                     "communautaire important pour les catholiques de Bafoussam.",
        best_season="Toute l'année, messes le dimanche",
        latitude=5.4680, longitude=10.4210, rating=4.3, price_range_xaf="Accès libre",
        media_main=commons("Garden sacred heart Parish Ndiendam Bafoussam.jpg"),
        activities=[],
        anecdote=(
            "La paroisse de Ndiendam est réputée pour ses chorales : certains habitants viennent de quartiers voisins uniquement pour assister à la messe chantée du dimanche."
        ),
    ),
    dict(
        id="dest-012", name="Festival Ngou-Ngoung", country=CENTRE_VILLE,
        category="Culture", tags=["culture", "chefferie", "famille"],
        avg_cost_per_day=2000,
        description="Grand rassemblement de danses initiatiques et traditionnelles bamiléké, organisé dans "
                     "l'enceinte de la chefferie et rythmé par les tam-tams de paix.",
        best_season="Décembre - Janvier (période des fêtes traditionnelles)",
        latitude=5.4740, longitude=10.4130, rating=4.8, price_range_xaf="2 000 - 5 000 FCFA",
        media_main=commons("Danse Traditionnelle Ngou-Ngoung.jpg"),
        media_secondary=[commons("Festival Ngou-Ngoung.jpg"), commons("Danse Initiatique Bamiliké 6.jpg")],
        activities=[
            {"name": "Entrée festival (place debout)", "price": "2 000 FCFA"},
            {"name": "Place assise en tribune", "price": "5 000 FCFA"},
        ],
        anecdote=(
            "Pendant le festival Ngou-Ngoung, les danseurs initiés portent des masques qu'aucun étranger n'est autorisé à toucher — la tradition veut que seul le sculpteur qui les a créés en connaisse le vrai visage."
        ),
    ),
    # ---- Hôtels, restaurants et institutions -----------------------------
    # Noms et adresses réels (Petit Futé, Wikipédia, Wikivoyage, annuaires
    # locaux) ; coordonnées estimées dans le bon quartier de la ville, comme
    # pour le reste du catalogue. Pour Zingana, Altitel et Sare, les photos
    # sont de vraies photos de l'établissement (façade, chambres/suites,
    # restaurant) récupérées depuis leur fiche Tripadvisor. Pour les
    # établissements sans photo dédiée trouvée, on utilise la photo la plus
    # proche et véridique disponible sous licence libre dans la catégorie
    # Commons "Bafoussam" (bâtiment de la ville ou plat camerounais réel),
    # plutôt qu'une image générique/inventée.
    dict(
        id="dest-013", name="Hôtel Zingana", country=CENTRE_VILLE,
        category="Hôtel", tags=["famille"],
        avg_cost_per_day=25000,
        description="Hôtel du centre-ville reprenant avec élégance des éléments de l'architecture "
                     "bamiléké dans sa décoration, apprécié pour son confort et son accueil soigné.",
        best_season="Toute l'année",
        latitude=5.4718, longitude=10.4148, rating=4.2, price_range_xaf="25 000 - 45 000 FCFA / nuit",
        media_main="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0f/39/52/31/hotel-zingana.jpg?w=900&h=500&s=1",
        media_secondary=[
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0f/39/51/0e/hotel-zingana.jpg?w=900&h=500&s=1",
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0f/39/53/c4/hotel-zingana.jpg?w=900&h=500&s=1",
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0f/39/55/c8/bar-restaurant-ouvert.jpg?w=900&h=500&s=1",
        ],
        activities=[{"name": "Nuitée chambre standard", "price": "25 000 FCFA"}, {"name": "Nuitée suite", "price": "45 000 FCFA"}],
        anecdote=(
            "Le décor de l'hôtel Zingana reprend les motifs géométriques du tissu ndop, comme un clin d'œil permanent à la royauté bamiléké."
        ),
    ),
    dict(
        id="dest-014", name="Hôtel Altitel", country=CENTRE_VILLE,
        category="Hôtel", tags=["famille"],
        avg_cost_per_day=18000,
        description="Établissement bien situé en centre-ville, réputé pour ses chambres propres et "
                     "confortables et son bon rapport qualité-prix, apprécié des voyageurs d'affaires.",
        best_season="Toute l'année",
        latitude=5.4702, longitude=10.4172, rating=4.0, price_range_xaf="18 000 - 30 000 FCFA / nuit",
        media_main="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/1c/6a/0c/a4/facade-principale.jpg?w=900&h=600&s=1",
        media_secondary=[
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-s/02/c3/12/31/hotel-altitel.jpg?w=600&h=400&s=1",
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-s/02/c3/11/99/hotel-altitel.jpg?w=600&h=400&s=1",
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-s/02/c3/14/4f/hotel-altitel.jpg?w=600&h=400&s=1",
        ],
        activities=[{"name": "Nuitée chambre standard", "price": "18 000 FCFA"}],
        anecdote=(
            "Sa position centrale en fait une base idéale : la plupart des lieux du centre-ville de Bafoussam se rejoignent à pied ou en quelques minutes de moto-taxi."
        ),
    ),
    dict(
        id="dest-015", name="Résidence Sare Hôtel", country=CENTRE_VILLE,
        category="Hôtel", tags=["famille"],
        avg_cost_per_day=20000,
        description="Un établissement calme et reposant, souvent cité comme une étape agréable après "
                     "une longue route, avec un service attentionné.",
        best_season="Toute l'année",
        latitude=5.4740, longitude=10.4085, rating=4.1, price_range_xaf="20 000 - 35 000 FCFA / nuit",
        media_main="https://dynamic-media-cdn.tripadvisor.com/media/photo-o/06/e4/e3/2b/getlstd-property-photo.jpg?w=900&h=500&s=1",
        activities=[{"name": "Nuitée chambre standard", "price": "20 000 FCFA"}],
        anecdote=(
            "Beaucoup de voyageurs en direction de Foumban ou de Dschang choisissent d'y faire étape avant de reprendre la route le lendemain."
        ),
    ),
    dict(
        id="dest-016", name="La Terrasse", country=CENTRE_VILLE,
        category="Restaurant", tags=["famille"],
        avg_cost_per_day=3500,
        description="Petit bijou d'authenticité au cœur de Bafoussam, face au marché : cuisine "
                     "camerounaise familiale servie dans une ambiance conviviale.",
        best_season="Toute l'année",
        latitude=5.4772, longitude=10.4195, rating=4.4, price_range_xaf="2 000 - 5 000 FCFA",
        media_main=commons("Ndolé camerounais.JPG"),
        activities=[{"name": "Plat du jour", "price": "3 500 FCFA"}],
        anecdote=(
            "Sa position juste en face du grand marché en fait une pause idéale entre deux emplettes — la ndolé y est l'un des plats les plus commandés."
        ),
    ),
    dict(
        id="dest-017", name="Restaurant Le Buffet Saint-Paul", country=CENTRE_VILLE,
        category="Restaurant", tags=["famille"],
        avg_cost_per_day=2500,
        description="Adresse pratique près de la gare routière, idéale pour les voyageurs pressés : "
                     "formule buffet et plats locaux servis rapidement.",
        best_season="Toute l'année",
        latitude=5.4703, longitude=10.4242, rating=3.9, price_range_xaf="1 500 - 3 500 FCFA",
        media_main=commons("Poulet DG.JPG"),
        activities=[{"name": "Formule buffet", "price": "2 500 FCFA"}],
        anecdote=(
            "Beaucoup de voyageurs s'y arrêtent juste avant de prendre leur bus à la gare routière voisine de Ndiangdam, à quelques pas de là."
        ),
    ),
    dict(
        id="dest-018", name="Restaurant La Miséricorde", country=CENTRE_VILLE,
        category="Restaurant", tags=["famille"],
        avg_cost_per_day=3000,
        description="Situé au cœur du quartier Kankop, un véritable havre de paix pour les amateurs de "
                     "bonne cuisine : poulet braisé, poulet DG, poisson grillé et options végétariennes.",
        best_season="Toute l'année",
        latitude=5.4830, longitude=10.4080, rating=4.3, price_range_xaf="2 000 - 4 500 FCFA",
        media_main=commons("Le ndolè, plat mythique camerounais..jpg"),
        activities=[{"name": "Plat signature (poulet DG)", "price": "4 000 FCFA"}],
        anecdote=(
            "L'ambiance chaleureuse et le décor mêlant éléments traditionnels et style contemporain en font une adresse prisée pour les repas de famille et les occasions spéciales."
        ),
    ),
    dict(
        id="dest-019", name="Hôtel de Ville de Bafoussam", country=CENTRE_VILLE,
        category="Institution", tags=["histoire", "gratuit"],
        avg_cost_per_day=0,
        description="Siège de la Communauté Urbaine de Bafoussam, sur la place centrale de la ville : "
                     "un repère administratif et un point de rencontre populaire du centre-ville.",
        best_season="Toute l'année (jours ouvrés)",
        latitude=5.4762, longitude=10.4160, rating=4.0, price_range_xaf="Accès libre à l'esplanade",
        media_main=commons("Hôtel de ville de Bafoussam.jpg"),
        media_secondary=[commons("Place de l'hôtel de ville de Bafoussam.jpg")],
        activities=[],
        anecdote=(
            "La place de l'Hôtel de Ville sert régulièrement de point de rassemblement pour les grands événements officiels et populaires de la ville."
        ),
    ),
    dict(
        id="dest-020", name="Institut Catholique de Bafoussam (ICAB)", country=BALENG,
        category="Institution", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement d'enseignement supérieur du diocèse de Bafoussam, créé en 2015, "
                     "proposant des filières industrielles, technologiques, économiques et commerciales.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.4650, longitude=10.4380, rating=4.1, price_range_xaf="Accès libre au campus",
        media_main=commons("Direction générale PMUC à Bafoussam.jpg"),
        activities=[],
        anecdote=(
            "Fondé en juin 2015 par le diocèse de Bafoussam, l'ICAB est l'un des jeunes établissements supérieurs qui font de la ville un pôle universitaire montant de l'Ouest-Cameroun."
        ),
    ),
    dict(
        id="dest-021", name="Aéroport de Bafoussam-Bamougoum (BFX)", country=BAMOUGOUM,
        category="Institution", tags=["gratuit"],
        avg_cost_per_day=0,
        description="Aéroport desservant Bafoussam, construit à Bamougoum sur 450 hectares, avec une "
                     "piste de 2 500 m — point d'arrivée aérien de la ville, relié à Douala par Camair-Co.",
        best_season="Toute l'année",
        latitude=5.536667, longitude=10.354444, rating=3.7, price_range_xaf="Accès libre au hall public",
        media_main=commons("Vue aérienne de la ville de Bafoussam (9).jpg"),
        activities=[],
        anecdote=(
            "Sa piste de 2 500 m peut accueillir des appareils jusqu'à 60 tonnes — de quoi voir un jour Bafoussam se connecter directement à davantage de villes du pays."
        ),
    ),

    # ---- Enrichissement depuis la carte touristique officielle de l'Ouest
    # (brochure "Carte touristique Ouest 2021-2022", CamScanner) — nouveaux
    # lieux concernant explicitement Bafoussam et ses communes (Bafoussam
    # I/II-Baleng/III-Bamougoum), avec photos réelles recadrées depuis la
    # brochure elle-même et hébergées localement sous /destinations/.
    dict(
        id="dest-022", name="Chefferie Bamougoum", country=BAMOUGOUM,
        category="Chefferie", tags=["chefferie", "histoire", "culture"],
        avg_cost_per_day=1000,
        description="Chefferie importante de la commune de Bamougoum, dotée d'un musée qui retrace "
                     "l'histoire du groupement et de son peuple, au sud-ouest du centre de Bafoussam.",
        best_season="Toute l'année",
        latitude=5.4450, longitude=10.3850, rating=4.0, price_range_xaf="1 000 - 2 000 FCFA (visite guidée)",
        media_main="/destinations/chefferie-bamougoum.jpg",
        activities=[{"name": "Visite guidée + musée", "price": "1 500 FCFA"}],
        anecdote=(
            "La légende raconte que le groupement Bamougoum est né du partage des terres entre quatre frères de même père — l'un d'eux prenant la part qui allait devenir la chefferie de Bamougoum."
        ),
    ),
    dict(
        id="dest-023", name="Chefferie Baleng", country=BALENG,
        category="Chefferie", tags=["chefferie", "histoire", "nature"],
        avg_cost_per_day=1000,
        description="Doyenne des chefferies de la région, installée avec sa forêt sacrée dans les hauts "
                     "plateaux au nord de Bafoussam. Elle forme, avec le lac Baleng voisin, un circuit "
                     "touristique complet à ne pas manquer.",
        best_season="Toute l'année",
        latitude=5.5100, longitude=10.4300, rating=4.2, price_range_xaf="1 000 - 2 000 FCFA (visite guidée)",
        media_main="/destinations/chefferie-baleng.jpg",
        activities=[{"name": "Visite guidée de la chefferie", "price": "1 500 FCFA"}],
        anecdote=(
            "Fondée par Fôo Fondoup, la chefferie Baleng fut transférée deux fois avant de s'installer à son emplacement actuel — la lignée en est aujourd'hui à son 97ᵉ chef, Fôo Tchountchoua Njitack Ngompé Pelé."
        ),
    ),
    dict(
        id="dest-024", name="Lac Takouche de Baleng", country=BALENG,
        category="Nature", tags=["nature", "panorama", "aventure"],
        avg_cost_per_day=500,
        description="Lac de cratère niché parmi les collines de Baleng, réputé pour ses hippopotames et "
                     "sa nature intacte — l'un des sites les plus photogéniques des environs de Bafoussam.",
        best_season="Saison sèche (novembre à mars)",
        latitude=5.5050, longitude=10.4400, rating=4.4, price_range_xaf="500 FCFA (accès + guide local)",
        media_main="/destinations/lac-takouche-baleng.jpg",
        activities=[{"name": "Randonnée + observation", "price": "500 FCFA"}],
        anecdote=(
            "Le lac Takouché abrite encore aujourd'hui une population d'hippopotames — une rareté pour un plan d'eau aussi proche du centre-ville de Bafoussam."
        ),
    ),
    dict(
        id="dest-025", name="Parc des Loisirs de Bafoussam", country=CENTRE_VILLE,
        category="Culture", tags=["famille", "gratuit"],
        avg_cost_per_day=1000,
        description="Espace vert aménagé au cœur de la ville, entre pavillons de détente et allées "
                     "ombragées — un lieu de promenade familiale apprécié des habitants de Bafoussam.",
        best_season="Toute l'année",
        latitude=5.4820, longitude=10.4230, rating=3.9, price_range_xaf="Accès libre, activités payantes",
        media_main="/destinations/parc-loisirs-bafoussam.jpg",
        activities=[{"name": "Entrée + balade", "price": "Gratuit"}],
        anecdote=(
            "C'est l'un des rares grands espaces verts ouverts au public en plein centre-ville, prisé le week-end pour les sorties en famille."
        ),
    ),
    dict(
        id="dest-026", name="Grottes de Doumelong", country=BAMOUGOUM,
        category="Nature", tags=["religieux", "aventure", "histoire"],
        avg_cost_per_day=500,
        description="Ensemble de grands rochers naturels transformé en sanctuaire, à environ 800 m de la "
                     "chefferie de Bamougoum — un lieu de recueillement toujours fréquenté aujourd'hui.",
        best_season="Toute l'année",
        latitude=5.4470, longitude=10.3830, rating=4.0, price_range_xaf="500 FCFA (guide local recommandé)",
        media_main="/destinations/grottes-doumelong.jpg",
        activities=[{"name": "Visite accompagnée", "price": "500 FCFA"}],
        anecdote=(
            "Le site accueille encore des croyants en quête de recueillement, dans un décor de rochers géants abrité par une petite forêt galerie."
        ),
    ),
    dict(
        id="dest-027", name='Marché de vivres « Casablanca »', country=CENTRE_VILLE,
        category="Marché", tags=["marche", "famille"],
        avg_cost_per_day=1500,
        description="Marché populaire de produits vivriers en plein centre de Bafoussam, connu sous le "
                     "surnom de « Casablanca » — légumes, tubercules et produits frais s'y négocient "
                     "chaque jour dans une ambiance animée.",
        best_season="Toute l'année",
        latitude=5.4790, longitude=10.4210, rating=4.1, price_range_xaf="Prix négociés au kilo",
        media_main="/destinations/marche-casablanca.jpg",
        activities=[{"name": "Panier de produits frais", "price": "dès 1 000 FCFA"}],
        anecdote=(
            "Son surnom « Casablanca » vient de l'effervescence permanente du lieu — l'un des points de ravitaillement en vivres les plus fréquentés de la ville."
        ),
    ),

    # ---- Établissements de santé et pharmacies -----------------------
    # Source : répertoire "Établissements de Santé & Pharmacies — Bafoussam"
    # fourni par l'utilisateur (notes, catégories et descriptions reprises du
    # document). Ce répertoire ne contient aucune photo réelle exploitable (les
    # vignettes "Vue 1/2/3" sont des emplacements vides, jamais remplis) : les
    # photos ci-dessous sont donc de vraies photos (non générées) piochées sur
    # Unsplash — représentatives de la catégorie de l'établissement plutôt que
    # des photos de l'établissement précis, faute de mieux, plutôt que de
    # laisser ces 43 lieux sans aucune image.
    dict(
        id="dest-028", name="Hôpital Régional De Bafoussam", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Établissement hospitalier public majeur de référence dans la région de l'Ouest, ouvert en continu. Services d'urgences, chirurgie, réanimation et soins spécialisés.",
        best_season="Toute l'année",
        latitude=5.474, longitude=10.413, rating=3.8, price_range_xaf="Consultation sur place (Hôpital public)",
        media_main="https://images.unsplash.com/photo-1479839672679-a46483c0e7c8?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-029", name="CHR de Bafoussam", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Centre Hospitalier Régional récent doté de structures de prise en charge modernes, d'un plateau technique de pointe et d'un service d'urgence 24h/24. Situé à Njingah.",
        best_season="Toute l'année",
        latitude=5.49, longitude=10.43, rating=4.4, price_range_xaf="Consultation sur place (Centre Hospitalier Régional)",
        media_main="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-030", name="Hôpital Régional De Bafoussam (Annexe)", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Annexe de la structure hospitalière régionale publique. Services de médecine générale, consultations externes et urgences 24h/24.",
        best_season="Toute l'année",
        latitude=5.475, longitude=10.414, rating=3.5, price_range_xaf="Consultation sur place (Hôpital public)",
        media_main="https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-031", name="Bafoussam Baptist Hospital", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Hôpital confessionnel très fréquenté pour la qualité de son accueil et de ses soins. Assistance médicale 24h/24, pédiatrie, ophtalmologie et chirurgie.",
        best_season="Toute l'année",
        latitude=5.485, longitude=10.43, rating=4.6, price_range_xaf="Consultation sur place (Hôpital confessionnel)",
        media_main="https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-032", name="Hôpital protestant", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Centre hospitalier confessionnel reconnu dans la ville. Consultations, soins continus 24h/24, maternité et accompagnement médical complet.",
        best_season="Toute l'année",
        latitude=5.47, longitude=10.41, rating=4.3, price_range_xaf="Consultation sur place (Hôpital confessionnel)",
        media_main="https://images.unsplash.com/photo-1481026469463-66327c86e544?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-033", name="Clinique Acodess Bafoussam", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Clinique privée offrant diverses prestations de soins de santé : médecine générale, urgences et petite chirurgie disponible 24h/24.",
        best_season="Toute l'année",
        latitude=5.465, longitude=10.42, rating=4.0, price_range_xaf="Consultation sur place (Clinique privée)",
        media_main="https://images.unsplash.com/photo-1626315869436-d6781ba69d6e?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-034", name="Clinique De L'Ouest", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Établissement privé assurant le suivi médical et les urgences. Ouvert 24h/24 avec des consultations spécialisées et des soins généraux.",
        best_season="Toute l'année",
        latitude=5.46, longitude=10.415, rating=4.7, price_range_xaf="Consultation sur place (Clinique privée)",
        media_main="https://images.unsplash.com/photo-1517120026326-d87759a7b63b?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-035", name="Clinique de la Solidarité", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Clinique de proximité offrant des prestations de soins généraux, service de permanence 24h/24, soins infirmiers et petite chirurgie.",
        best_season="Toute l'année",
        latitude=5.482, longitude=10.405, rating=3.0, price_range_xaf="Consultation sur place (Clinique privée)",
        media_main="https://images.unsplash.com/photo-1490351267196-b7a67e26e41b?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-036", name="Hôpital des Sœurs de Tyo Village", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Structure de santé confessionnelle située vers le quartier Tyo. Soins de santé continus 24h/24, maternité et médecine générale.",
        best_season="Toute l'année",
        latitude=5.455, longitude=10.445, rating=4.0, price_range_xaf="Consultation sur place (Hôpital confessionnel)",
        media_main="https://images.unsplash.com/photo-1586773860383-dab5f3bc1bcc?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-037", name="Centre Médico-Chirurgical SOS Ouest Santé", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Centre médico-chirurgical offrant une prise en charge rapide des urgences, blocs opératoires et suivi spécialisé. Situé sur la route de Bamenda.",
        best_season="Toute l'année",
        latitude=5.495, longitude=10.4, rating=4.4, price_range_xaf="Consultation sur place (Centre médico-chirurgical)",
        media_main="https://images.unsplash.com/photo-1533042789716-e9a9c97cf4ee?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-038", name="Centre de Santé ACS Santé Ngom Passam", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Centre de santé local assurant le suivi de médecine générale, vaccinations et soins primaires. Ouvert 24h/24 au quartier Ngom Passam.",
        best_season="Toute l'année",
        latitude=5.46, longitude=10.45, rating=5.0, price_range_xaf="Consultation sur place (Centre de santé)",
        media_main="https://images.unsplash.com/photo-1587351021355-a479a299d2f9?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-039", name="Centre de Santé des Recasés de Ngouache", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Centre de santé communautaire implanté au quartier Ngouache. Soins de santé primaires et consultations de proximité dans le secteur de Bafoussam 3e.",
        best_season="Toute l'année",
        latitude=5.45, longitude=10.39, rating=5.0, price_range_xaf="Consultation sur place (Centre médical)",
        media_main="https://images.unsplash.com/photo-1578991624414-276ef23a534f?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-040", name="Dynastie Santé+ | Oasis Médicale Royale", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Structure médicale privée proposant divers services de santé, accueil et permanence 24h/24, consultations et soins personnalisés à Tougang Ville.",
        best_season="Toute l'année",
        latitude=5.49, longitude=10.445, rating=4.9, price_range_xaf="Consultation sur place (Centre médical)",
        media_main="https://images.unsplash.com/photo-1596541223130-5d31a73fb6c6?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-041", name="Centre de Santé Émergence", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Centre de santé de proximité offrant des soins généraux, consultations externes et permanence médicale 24h/24 dans le secteur de Bafoussam II.",
        best_season="Toute l'année",
        latitude=5.5, longitude=10.425, rating=4.5, price_range_xaf="Consultation sur place (Centre de santé)",
        media_main="https://images.unsplash.com/photo-1597807037496-c56a1d8bc29a?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-042", name="Centre Medical Unicare", country=CENTRE_VILLE,
        category="Hôpital", tags=[],
        avg_cost_per_day=0,
        description="Centre médical privé situé en zone urbaine au Carrefour Madelon à Banengo. Soins et consultations de santé 24h/24.",
        best_season="Toute l'année",
        latitude=5.468, longitude=10.408, rating=4.2, price_range_xaf="Consultation sur place (Centre médical)",
        media_main="https://images.unsplash.com/photo-1479839672679-a46483c0e7c8?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-043", name="Centre de Santé la Modestie", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Établissement de soins de santé de proximité situé à l'entrée du stade. Permanence médicale 24h/24 et soins infirmiers.",
        best_season="Toute l'année",
        latitude=5.477, longitude=10.428, rating=4.1, price_range_xaf="Consultation sur place (Centre de santé)",
        media_main="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-044", name="Centre de Santé de Djeleng", country=CENTRE_VILLE,
        category="Hôpital", tags=['gratuit'],
        avg_cost_per_day=0,
        description="Centre de santé public assurant des soins de première nécessité, suivi de maternité et médecine de quartier. Situé à Djeleng, rue des Grandes Endémies.",
        best_season="Toute l'année",
        latitude=5.46, longitude=10.46, rating=3.9, price_range_xaf="Consultation sur place (Centre de santé public)",
        media_main="https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),

    # ---- Pharmacies -------------------------------------------------------
    dict(
        id="dest-045", name="Pharmacie La Salvia", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Pharmacie idéalement située pour le ravitaillement en médicaments. Ouverte tous les jours, y compris le dimanche, de 7h à 19h sur la route de Bamenda.",
        best_season="Toute l'année",
        latitude=5.498, longitude=10.398, rating=4.3, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1576602976047-174e57a47881?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-046", name="Pharmacie Du Benin", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Officine fournissant un large choix de produits pharmaceutiques et parapharmaceutiques. Ouverte du lundi au samedi de 7h30 à 20h au quartier Bénin.",
        best_season="Toute l'année",
        latitude=5.472, longitude=10.405, rating=4.4, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1642055514517-7b52288890ec?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-047", name="Pharmacie Binam", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Pharmacie centrale de la ville de Bafoussam. Ouverte du lundi au samedi de 7h30 à 20h. Approvisionnement régulier en médicaments essentiels.",
        best_season="Toute l'année",
        latitude=5.4778, longitude=10.4176, rating=3.7, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1471864190281-a93a3070b6de?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-048", name="Pharmacie Noubissi", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Officine pharmaceutique assurant la vente de produits médicaux et conseils parapharmaceutiques. Ouverte du lundi au samedi de 7h30 à 21h en centre-ville.",
        best_season="Toute l'année",
        latitude=5.479, longitude=10.419, rating=3.9, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1512069772995-ec65ed45afd6?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-049", name="Pharmacie du Marché 'B'", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Pharmacie de proximité implantée près des zones commerçantes. Ouverte du lundi au samedi de 7h30 à 20h, au 76 route Bafoussam-Bamenda.",
        best_season="Toute l'année",
        latitude=5.485, longitude=10.41, rating=3.9, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-050", name="Pharmacie de la Mifi", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Officine servant la population locale avec un éventail complet de produits de santé et d'hygiène. Ouverte du lundi au samedi de 7h30 à 20h près du secteur commercial.",
        best_season="Toute l'année",
        latitude=5.476, longitude=10.421, rating=4.3, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1603706580932-6befcf7d8521?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-051", name="Pharmacie Moyo Pierre", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Pharmacie reconnue pour la dispensation de médicaments et le conseil de proximité. Ouverte du lundi au samedi de 7h30 à 20h.",
        best_season="Toute l'année",
        latitude=5.473, longitude=10.416, rating=5.0, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-052", name="Pharmacie Les Merveilles", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Officine de quartier proposant un suivi et des conseils santé personnalisés. Ouverte du lundi au samedi de 7h30 à 20h.",
        best_season="Toute l'année",
        latitude=5.47, longitude=10.423, rating=4.5, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1607619056574-7b8d3ee536b2?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-053", name="Pharmacie des Martyrs", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Pharmacie établie au quartier des Martyrs. Vente de produits pharmaceutiques et produits de soin, ouverte du lundi au samedi de 7h30 à 20h.",
        best_season="Toute l'année",
        latitude=5.465, longitude=10.435, rating=4.5, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1622230208995-0f26eba75875?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-054", name="Pharmacie Du Secours", country=CENTRE_VILLE,
        category="Pharmacie", tags=[],
        avg_cost_per_day=0,
        description="Officine délivrant soins et ordonnances médicales. Ouverte du lundi au samedi de 7h30 à 20h sur l'avenue Pachong Adolf.",
        best_season="Toute l'année",
        latitude=5.481, longitude=10.414, rating=3.9, price_range_xaf="Prix des médicaments variables",
        media_main="https://images.unsplash.com/photo-1562243061-204550d8a2c9?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),

    # ---- Éducation de base (maternelles et primaires) ---------------------
    dict(
        id="dest-055", name="École Publique de Camp-Fon", country=CENTRE_VILLE,
        category="École", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement public de référence situé dans le quartier historique de Camp-Fon (Bafoussam I). Enseignement primaire gratuit et inclusif, accueillant les enfants de la communauté locale.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.483, longitude=10.416, rating=4.0, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1536337005238-94b997371b40?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-056", name="Groupe Scolaire Bilingue Privé Laïc ANGRA", country=CENTRE_VILLE,
        category="École", tags=["famille"],
        avg_cost_per_day=0,
        description="Complexe éducatif privé intégrant maternelle et primaire, connu pour son programme bilingue français/anglais rigoureux, avec un accent sur la discipline et l'éveil précoce aux technologies.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.47, longitude=10.428, rating=4.2, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1521493959102-bdd6677fdd81?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-057", name="La Centrale Bilingue School (Groupe Scolaire J-BOS)", country=CENTRE_VILLE,
        category="École", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement laïc moderne offrant un encadrement bilingue complet, avec des infrastructures adaptées à l'épanouissement des jeunes élèves pour une transition réussie vers le secondaire.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.475, longitude=10.432, rating=4.1, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1473649085228-583485e6e4d7?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-058", name="Groupe Scolaire Bilingue Privé Laïc La Mailizette", country=CENTRE_VILLE,
        category="École", tags=["famille"],
        avg_cost_per_day=0,
        description="École privée laïque reconnue pour ses excellents résultats aux examens officiels du CEP et du First School Leaving Certificate, avec un cadre sécurisé et des activités parascolaires variées.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.468, longitude=10.42, rating=4.3, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1632215861513-130b66fe97f4?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-059", name="École Maternelle et Primaire Catholique Sacré-Cœur", country=CENTRE_VILLE,
        category="École", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement confessionnel sous la tutelle du Secrétariat à l'Éducation Catholique du diocèse de Bafoussam, alliant excellence académique et éducation aux valeurs.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.479, longitude=10.423, rating=4.4, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1567057419565-4349c49d8a04?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),

    # ---- Enseignement secondaire (lycées et collèges) ----------------------
    dict(
        id="dest-060", name="Lycée Classique de Bafoussam", country=CENTRE_VILLE,
        category="Lycée", tags=["famille"],
        avg_cost_per_day=0,
        description="L'un des plus anciens et prestigieux établissements d'enseignement secondaire général de l'Ouest. Forme plusieurs milliers d'élèves de la 6ème à la Terminale, séries littéraires et scientifiques.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.4805, longitude=10.411, rating=4.5, price_range_xaf="Frais de scolarité variables",
        media_main=commons("Lycée classique de bafoussam.jpg"),
        media_secondary=[commons("Entrée secondaire Lycée Classique de Bafoussam (8).jpg"), commons("Voie longeant le Lycée Classique de Bafoussam.jpg")],
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-061", name="Lycée Technique de Bafoussam", country=CENTRE_VILLE,
        category="Lycée", tags=["famille"],
        avg_cost_per_day=0,
        description="Centre majeur de la formation technique et industrielle de la ville, préparant aux spécialités du génie civil, électrique, mécanique et sciences de gestion. Ateliers et laboratoires spécialisés.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.465, longitude=10.408, rating=4.2, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1548102245-c79dbcfa9f92?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-062", name="Collège Évangélique Bilingue de Bafoussam", country=CENTRE_VILLE,
        category="Lycée", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement privé confessionnel protestant reconnu pour la rigueur de son encadrement bilingue, menant aux examens du BEPC, GCE, Probatoire et Baccalauréat.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.49, longitude=10.42, rating=4.3, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/flagged/photo-1579133311477-9121405c78dd?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-063", name="Collège Privé Catholique Sacré-Cœur", country=CENTRE_VILLE,
        category="Lycée", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement secondaire confessionnel catholique réputé pour sa discipline stricte, ses excellents résultats scolaires et son infrastructure moderne (laboratoires, terrains de sport, informatique).",
        best_season="Toute l'année (période scolaire)",
        latitude=5.478, longitude=10.424, rating=4.4, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1582307811683-75b18a39ab71?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-064", name="Collège Polyvalent Bilingue Martin Luther King", country=CENTRE_VILLE,
        category="Lycée", tags=["famille"],
        avg_cost_per_day=0,
        description="Établissement privé laïc proposant une formation polyvalente intégrant enseignement général et filières commerciales/techniques, avec une pédagogie orientée compétences.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.472, longitude=10.435, rating=4.0, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1547226706-af7e2c20bcea?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-065", name="Collège de la Réunification Tankou", country=CENTRE_VILLE,
        category="Lycée", tags=["famille"],
        avg_cost_per_day=0,
        description="Membre du groupe d'enseignement Tankou, ce collège offre un cadre structuré avec des sections francophone et anglophone et des équipements didactiques complets.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.46, longitude=10.402, rating=4.1, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1627423896085-e3e694d88e40?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),

    # ---- Enseignement supérieur (universités et instituts) -----------------
    dict(
        id="dest-066", name="Université de Dschang — Campus de Bafoussam", country=CENTRE_VILLE,
        category="Université", tags=[],
        avg_cost_per_day=0,
        description="Antenne universitaire publique de l'Université de Dschang à Bafoussam, abritant notamment des filières de l'IUT-FV (Institut Universitaire de Technologie Fotso Victor) et des formations professionnalisantes.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.455, longitude=10.415, rating=4.2, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1583373834259-46cc92173cb7?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-067", name="Institut Supérieur de Bafoussam (ISB)", country=CENTRE_VILLE,
        category="Université", tags=[],
        avg_cost_per_day=0,
        description="Fondé en 2011 et agréé par le MINESUP, institut privé majeur formant en BTS, Licence Professionnelle et Master, dans les sciences médicales, médico-sanitaires, la gestion et les technologies d'ingénierie.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.468, longitude=10.407, rating=4.3, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1576495199011-eb94736d05d6?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-068", name="Groupe Tankou Enseignement Supérieur (GTES)", country=CENTRE_VILLE,
        category="Université", tags=[],
        avg_cost_per_day=0,
        description="Institut privé d'enseignement supérieur proposant des cycles de BTS, Licences et Masters professionnels en gestion d'entreprise, commerce international, génie informatique et réseaux/télécoms.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.461, longitude=10.403, rating=4.0, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1581362072978-14998d01fdaa?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-069", name="Institut Supérieur des Sciences et Technologies Nanfah (ISSTN)", country=CENTRE_VILLE,
        category="Université", tags=[],
        avg_cost_per_day=0,
        description="Établissement supérieur privé spécialisé dans la formation technique, les sciences industrielles, les filières biologiques et médicales ainsi que la gestion, avec un accent sur l'insertion professionnelle.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.472, longitude=10.44, rating=4.1, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1591123120675-6f7f1aae0e5b?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
    dict(
        id="dest-070", name="Institut Supérieur Mony Keng (IMK)", country=CENTRE_VILLE,
        category="Université", tags=[],
        avg_cost_per_day=0,
        description="Institut supérieur privé offrant des formations professionnelles universitaires (BTS, Bachelor, Master), préparant aux métiers du management, de la communication et des nouvelles technologies.",
        best_season="Toute l'année (période scolaire)",
        latitude=5.485, longitude=10.418, rating=4.0, price_range_xaf="Frais de scolarité variables",
        media_main="https://images.unsplash.com/photo-1559135197-8a45ea74d367?auto=format&fit=crop&w=1000&q=80",
        activities=[],
        anecdote="",
    ),
]


def seed_destinations() -> None:
    """Inserts every destination from MOCK_DESTINATIONS that isn't already in
    the database, and refreshes any existing row whose fields have drifted
    from the current catalog (e.g. a corrected photo URL).

    This used to bail out entirely as soon as a single destination existed
    ("if anything is seeded, do nothing"). On a fresh install that's fine,
    but on an upgrade — a Postgres volume that already has data from an
    earlier version of this catalog — it meant newly added destinations
    (and fixes to existing ones, like broken/missing photos) would never
    reach a database that already had *some* rows in it. Admin-added
    destinations are untouched either way, since their ids never match an
    entry in MOCK_DESTINATIONS.
    """
    db = SessionLocal()
    try:
        existing = {d.id: d for d in db.query(Destination).all()}
        changed = False
        for row in MOCK_DESTINATIONS:
            current = existing.get(row["id"])
            if current is None:
                db.add(Destination(**row))
                changed = True
                continue
            for key, value in row.items():
                if getattr(current, key) != value:
                    setattr(current, key, value)
                    changed = True
        if changed:
            db.commit()
    finally:
        db.close()
