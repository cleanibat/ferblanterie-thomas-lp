#!/usr/bin/env python3
"""Génère le site de La Ferblanterie de Thomas (couvreur zingueur à Portes, Eure).
Usage : python3 build.py   — modifier la config ci-dessous, relancer, pousser sur main (déploiement automatique)."""
import datetime, html, json, os

# ---------- Config ----------
GTM_ID   = ""                                       # ex. "GTM-XXXXXXX" ; vide = snippet commenté
SITE     = "https://laferblanteriedethomas.com/"    # domaine de production (canonical, sitemap, Open Graph)
BRAND    = "La Ferblanterie de Thomas"
OWNER    = "Thomas Ferreira Rolo"
TEL_FR   = "07 78 37 52 91"
TEL_INT  = "+33778375291"
EMAIL    = ""                                       # adresse de contact publique, à confirmer avec Thomas (vide = non affichée)
STREET, CP, CITY = "18 rue Rolette", "27190", "Portes"
GEO      = (49.0316, 0.9472)                        # fiche Google
INSTAGRAM = "https://www.instagram.com/laferblanteriedethomas/"
GMAPS    = "https://www.google.com/maps/search/?api=1&query=La+Ferblanterie+de+Thomas&query_place_id=ChIJVUo5tqwnQW8RNiCrZmFVdOg"
SIREN, SIRET, TVA = "108 468 265", "108 468 265 00013", "FR71108468265"
HOURS_TXT = "Du lundi au vendredi de 7 h 30 à 18 h, le samedi de 7 h 30 à 13 h"
YEAR, TODAY = datetime.date.today().year, datetime.date.today().isoformat()
CONSENT_KEY = "fdt_consent"
CONSENT_DAYS = 182                                  # choix cookies conservé 6 mois (recommandation CNIL)

# Communes à moins de 30 km de Portes (geo.api.gouv.fr). Zone à confirmer avec Thomas.
ZONES = [
    ("Pays de Conches et d'Ouche", ["Portes", "Conches-en-Ouche", "La Bonneville-sur-Iton", "Breteuil", "Mesnils-sur-Iton", "Mesnil-en-Ouche"]),
    ("Évreux et alentours", ["Évreux", "Saint-Sébastien-de-Morsent", "Arnières-sur-Iton", "Gravigny", "Guichainville", "Louviers"]),
    ("Le Neubourg et la Risle", ["Le Neubourg", "Beaumont-le-Roger", "Serquigny", "Brionne", "Bernay"]),
]
CITIES = [c for _, cs in ZONES for c in cs]

e = html.escape

# ---------- Icônes (traits, 24 px) ----------
def ico(d, sw=2):
    return f'<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'

I = dict(
    PHONE='<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>',
    CHECK=ico('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 2.6),
    ARROW=ico('<path d="M5 12h14M13 6l6 6-6 6"/>'),
    DOC=ico('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>'),
    USER=ico('<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>'),
    ROOF=ico('<path d="M2 12 12 4l10 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>'),
    METAL=ico('<path d="M4 20V8l4-4v16M10 20V8l4-4v16M16 20V8l4-4v16"/>'),
    DROP=ico('<path d="M12 3s6 6.6 6 11a6 6 0 0 1-12 0c0-4.4 6-11 6-11z"/>'),
    TILE=ico('<path d="M3 6h18M3 12h18M3 18h18M8 6v6M16 6v6M12 12v6M4 18v0M20 18v0"/>'),
    WIND=ico('<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h7"/>'),
    SEARCH=ico('<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>'),
    CEILING=ico('<path d="M3 4h18"/><path d="M8 8c0 2-2 2-2 4M16 8c0 2 2 2 2 4"/><path d="M12 9v4"/><circle cx="12" cy="16" r="1.5"/>'),
    GUTTER=ico('<path d="M3 7h18v3a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3z"/><path d="M17 13v8"/>'),
    BROOM=ico('<path d="M19 3 11 11"/><path d="M8 10l6 6-2 5-9-9z"/>'),
    PIN=ico('<path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>'),
    STAR=ico('<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>'),
    WALL=ico('<path d="M3 5h18v14H3zM3 10h18M3 15h18M9 5v5M15 10v5M9 15v4"/>'),
    CLOCK=ico('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
)

# ---------- Contenu des pages ----------
NEEDS = ["Rénovation de toiture", "Réparation de fuite", "Gouttières / zinguerie", "Ornementation (épi, girouette…)", "Vérification après tempête", "Autre demande"]

FAQ_COMMON = {
    "prix": ("Combien coûtent les travaux ?",
             "Le prix dépend de la surface, du matériau, de l'accès et de l'état de la toiture. Nous venons voir et vous remettons un devis gratuit, écrit et détaillé."),
    "mairie": ("Faut-il une autorisation de la mairie ?",
               "Une réfection à l'identique n'en demande généralement pas. Un changement de matériau ou de couleur passe par une déclaration préalable, et les abords de monuments historiques par l'avis de l'architecte des Bâtiments de France."),
    "tempete": ("Que faire après une tempête ?",
                "Ne montez pas sur votre toit. Appelez-nous : nous vérifions la couverture, les faîtages et la zinguerie, puis nous remplaçons ce qui a été arraché ou déplacé."),
    "pros": ("Travaillez-vous pour les professionnels ?",
             "Oui. Nous intervenons pour les particuliers comme pour les entreprises, les syndics et les collectivités."),
}

HOME = dict(
    file="index.html", lp="Accueil",
    title="Couvreur zingueur dans l'Eure (27) | La Ferblanterie de Thomas",
    desc="Couvreur zingueur à Portes, près de Conches-en-Ouche et d'Évreux : rénovation de toiture, réparation de fuites, gouttières et ornementation. Devis gratuit.",
    eyebrow="Couvreur zingueur · Portes (27)",
    h1="Couverture et zinguerie <em>dans l'Eure</em>",
    sub="Rénovation de toiture, réparation de fuites, gouttières et ornementation en zinc et cuivre, autour de Conches-en-Ouche, Évreux et Le Neubourg.",
    need="",
    og="img/thomas-toiture-ardoise.jpg",
    hero=("hero-accueil", "ardoises-liteaux-aretier"),
    faq=["prix", "mairie", "tempete",
         ("Intervenez-vous sur les maisons anciennes ?", "Oui. Ardoise, tuile plate, zinc et cuivre : nous travaillons sur le bâti ancien comme sur les maisons récentes, en respectant les matériaux d'origine."),
         "pros"],
)

RENO = dict(
    file="renovation-toiture.html", lp="Rénovation de toiture",
    title="Rénovation de toiture dans l'Eure | La Ferblanterie de Thomas",
    desc="Réfection de toiture en tuile, ardoise, zinc ou bac acier autour de Conches-en-Ouche et Évreux : écran sous-toiture, liteaux, faîtage. Devis gratuit.",
    eyebrow="Rénovation de toiture · Eure (27)",
    h1="Rénovation de toiture <em>tuile, ardoise et zinc</em>",
    sub="Réfection complète ou partielle de votre couverture, autour de Conches-en-Ouche, Évreux et Le Neubourg. Un artisan couvreur zingueur, un devis gratuit et détaillé.",
    need="Rénovation de toiture",
    og="img/ardoises-colombages-lucarnes.jpg",
    hero=("hero-renovation", "hero-renovation-m"),
    signs=[("TILE", "Tuiles ou ardoises abîmées", "Cassées, glissées, poreuses ou couvertes de mousse."),
           ("CEILING", "Traces dans les combles", "Taches, bois humide ou goutte lors des fortes pluies."),
           ("ROOF", "Faîtage et rives fatigués", "Mortier fissuré, tuiles faîtières qui bougent."),
           ("WIND", "Après une tempête", "Éléments arrachés ou déplacés à faire vérifier.")],
    works=[("Le plus demandé", "Réfection complète", "Dépose de l'ancienne couverture, puis toiture neuve sur une base saine.",
            ["Écran sous-toiture et liteaux neufs", "Tuile, ardoise ou bac acier", "Faîtage, rives et raccords"]),
           ("Rénovation partielle", "Remplacement localisé", "Un pan, une zone abîmée ou quelques rangs à reprendre.",
            ["Tuiles et ardoises remplacées", "Raccord avec l'existant", "Fenêtres de toit et cheminées"]),
           ("Annexes et garages", "Bac acier et bardage", "Couverture en bac acier sur voligeage, pignon bardé du même profil.",
            ["Bac acier anthracite", "Bardage de pignon", "Rives et gouttières"])],
    photo="ardoises-liteaux-aretier",
    ba=("bac-acier-avant-tole", "bac-acier-apres-appentis-pignon", "Avant / après", "Une annexe <em>couverte à neuf</em>",
        "Ancienne tôle déposée, voligeage bois, puis bac acier anthracite sur le toit et le pignon."),
    gallery=("Sur nos chantiers", "Ardoise, bois <em>et acier</em>",
             ["ardoises-colombages-lucarnes", "voligeage-isolant-reflechissant", "lucarnes-maison-meuliere", "bac-acier-ossature-pignon", "bac-acier-pose-en-cours"]),
    steps=[("Visite et diagnostic", "Nous montons voir la couverture et vous expliquons ce qui doit être refait."),
           ("Devis détaillé", "Matériaux, surfaces et étapes : tout est écrit, poste par poste."),
           ("Travaux", "Dépose, pose et finitions, puis chantier nettoyé avant de partir.")],
    faq=["prix", "mairie",
         ("Combien de temps dure une rénovation de toiture ?", "Cela dépend de la surface et du matériau. La durée est indiquée sur le devis, et la maison reste hors d'eau chaque soir."),
         ("Peut-on garder les mêmes tuiles ou ardoises ?", "Si elles sont saines, oui : nous les déposons et les reposons. Sinon nous choisissons avec vous un modèle proche de l'existant."),
         "tempete"],
)

FUITE = dict(
    file="reparation-fuite-toiture.html", lp="Réparation de fuite",
    title="Réparation de fuite de toiture dans l'Eure | Ferblanterie de Thomas",
    desc="Fuite de toiture autour de Conches-en-Ouche et Évreux : recherche de l'origine, tuiles, ardoises, faîtage, noues et abergements réparés. Appelez le 07 78 37 52 91.",
    eyebrow="Réparation de fuite · Eure (27)",
    h1="Fuite de toiture : <em>recherche et réparation</em>",
    sub="Nous trouvons d'où vient l'eau et réparons la couverture ou la zinguerie en cause, autour de Conches-en-Ouche, Évreux et Le Neubourg.",
    need="Réparation de fuite",
    og="img/fenetre-de-toit-apres.jpg",
    hero=("hero-fuite", "fenetre-de-toit-apres"),
    signs=[("CEILING", "Tache au plafond", "Auréole, peinture qui cloque ou plâtre qui gonfle."),
           ("DROP", "Gouttes dans les combles", "Bois humide ou isolant mouillé après la pluie."),
           ("TILE", "Tuile cassée ou glissée", "Souvent après un coup de vent ou un hiver rigoureux."),
           ("METAL", "Abergement fissuré", "Autour d'une cheminée ou d'une fenêtre de toit.")],
    works=[("Première étape", "Recherche de l'origine", "L'eau entre rarement à l'endroit où elle apparaît : nous remontons jusqu'à la cause.",
            ["Tuiles, ardoises et faîtage", "Noues et abergements", "Fenêtres de toit et cheminées"]),
           ("Réparation", "Couverture remise en état", "Nous remplaçons ce qui laisse passer l'eau, avec des matériaux proches de l'existant.",
            ["Tuiles et ardoises remplacées", "Faîtage et rives repris", "Noues refaites"]),
           ("Zinguerie", "Raccords étanches", "Les points sensibles sont souvent les jonctions entre la toiture et ce qui la traverse.",
            ["Abergements de cheminée", "Raccords de fenêtre de toit", "Chéneaux et gouttières"])],
    photo="couvertines-solin-angle",
    ba=("fenetre-de-toit-avant", "fenetre-de-toit-apres", "Avant / après", "Une fenêtre de toit <em>et son raccord</em>",
        "Les fenêtres de toit sont un point sensible de la couverture : ici, fenêtre et raccord d'étanchéité remplacés."),
    steps=[("Appel ou formulaire", "Décrivez-nous la fuite : où, depuis quand, par quel temps."),
           ("Recherche de fuite", "Nous inspectons la toiture et vous montrons la cause."),
           ("Réparation", "Devis détaillé, puis réparation de la couverture ou de la zinguerie.")],
    faq=[("Pouvez-vous venir rapidement ?", "Appelez-nous au 07 78 37 52 91 : nous fixons ensemble un passage selon l'urgence et la météo."),
         ("La fuite vient-elle forcément d'une tuile cassée ?", "Non. Elle vient souvent d'un abergement, d'une noue, du faîtage ou d'une gouttière qui déborde. C'est pour cela que nous cherchons d'abord l'origine."),
         ("Mon assurance peut-elle prendre en charge la réparation ?", "Après une tempête, c'est souvent le cas. Nous vous remettons un devis détaillé à transmettre à votre assureur."),
         "tempete", "prix"],
)

GOUTT = dict(
    file="gouttieres-zinguerie.html", lp="Gouttières et zinguerie",
    title="Gouttières et zinguerie dans l'Eure | La Ferblanterie de Thomas",
    desc="Pose et remplacement de gouttières, chéneaux et descentes en zinc, cuivre ou aluminium autour de Conches-en-Ouche et Évreux. Devis gratuit.",
    eyebrow="Gouttières et zinguerie · Eure (27)",
    h1="Gouttières et zinguerie <em>zinc, cuivre, aluminium</em>",
    sub="Gouttières, chéneaux, descentes et habillages façonnés par un ferblantier, autour de Conches-en-Ouche, Évreux et Le Neubourg.",
    need="Gouttières / zinguerie",
    og="img/gouttiere-descente-angle.jpg",
    hero=("hero-gouttieres", "bac-acier-rive-gouttiere"),
    signs=[("GUTTER", "Gouttière qui déborde", "L'eau passe par-dessus et coule le long du mur."),
           ("DROP", "Fuite aux jonctions", "Goutte à goutte aux raccords, aux angles ou aux talons."),
           ("WALL", "Traces sur la façade", "Coulures, mousse ou enduit qui se décolle sous la gouttière."),
           ("METAL", "Gouttière affaissée", "Crochets tordus, pente perdue, eau qui stagne.")],
    works=[("Le plus demandé", "Gouttières et descentes", "Remplacement ou pose neuve, avec la pente et les crochets refaits.",
            ["Zinc, cuivre ou aluminium", "Gouttières pendantes et chéneaux", "Descentes et dauphins"]),
           ("Ferblanterie", "Habillages en zinc", "Les pièces façonnées qui protègent les rives, bandeaux et toits plats.",
            ["Bandeaux et couvertines", "Rives et noues", "Abergements"]),
           ("Ornementation", "Épis, girouettes et crêtes", "Les finitions en zinc ou en cuivre qui signent une toiture.",
            ["Épis de faîtage", "Girouettes", "Crêtes et lucarnes"])],
    photo="gouttiere-descente-angle",
    gallery=("Sur nos chantiers", "Gouttières, descentes <em>et couvertines</em>",
             ["gouttiere-descente-entree", "descente-pied-de-facade", "bac-acier-rive-gouttiere", "couvertines-toiture-terrasse", "couvertine-detail-rive", "girouette-cerf-cuivre"]),
    steps=[("Prise de mesures", "Nous relevons les longueurs, les pentes et les descentes."),
           ("Devis détaillé", "Métal, profil et finitions choisis avec vous."),
           ("Pose", "Dépose de l'ancien, pose et contrôle de l'écoulement.")],
    faq=[("Zinc, cuivre ou aluminium : que choisir ?", "Le zinc est le plus courant sur les maisons de la région. Le cuivre se patine et dure très longtemps. L'aluminium laqué existe en plusieurs couleurs. Nous vous conseillons selon votre maison."),
         ("Faut-il changer toute la gouttière ?", "Pas toujours. Si le métal est sain, une jonction ou quelques crochets suffisent. Si elle est percée en plusieurs points, le remplacement revient moins cher à terme."),
         ("Posez-vous des épis de faîtage ou des girouettes ?", "Oui. L'ornementation fait partie de notre métier de ferblantier : épis, girouettes, crêtes et habillages de lucarnes."),
         "prix", "pros"],
)

PAGES = [HOME, RENO, FUITE, GOUTT]
SERVICES = [  # cartes de l'accueil
    (RENO, "ardoises-colombages-lucarnes", "Rénovation de toiture", "Réfection complète ou partielle en tuile, ardoise, zinc ou bac acier."),
    (FUITE, "fenetre-de-toit-apres", "Réparation de fuite", "Recherche de l'origine, puis réparation de la couverture ou de la zinguerie."),
    (GOUTT, "gouttiere-descente-angle", "Gouttières et zinguerie", "Gouttières, chéneaux, descentes et habillages en zinc, cuivre ou aluminium."),
]
HOME_GALLERY = ["bac-acier-apres-appentis-pignon", "ardoises-liteaux-aretier", "lucarnes-maison-meuliere",
                "couvertines-toiture-terrasse", "bac-acier-pose-en-cours", "couvertines-solin-angle"]

# Photos du site : nom de fichier -> (largeur, hauteur, texte alternatif, légende). Sources : fiche Google,
# Instagram et Drive partagé par Aymeric le 06/11/2026 (métadonnées EXIF retirées).
PHOTOS = {
    "thomas-toiture-ardoise": (505, 828, f"{OWNER.split()[0]} sur une toiture en ardoise en cours de réfection, contre une cheminée en brique", "Réfection d'une couverture en ardoise"),
    "girouette-cerf-cuivre": (900, 1200, "Girouette en cuivre en forme de cerf au sommet d'un pignon", "Girouette en cuivre posée sur un pignon"),
    "ardoises-colombages-lucarnes": (1000, 750, "Maison à colombages avec toiture, lucarnes et bardage en ardoise", "Toiture et bardage en ardoise sur une maison à colombages"),
    "ardoises-liteaux-aretier": (750, 1000, "Ardoises posées sur liteaux le long d'un arêtier, chantier en cours", "Pose d'ardoises sur liteaux, détail d'arêtier"),
    "voligeage-isolant-reflechissant": (750, 1000, "Voligeage bois et isolant réfléchissant posés avant la couverture", "Voligeage et isolant réfléchissant avant couverture"),
    "lucarnes-maison-meuliere": (750, 1000, "Maison en meulière à lucarnes, échafaudage en place pour les travaux de toiture", "Chantier sur une maison en meulière à lucarnes"),
    "bac-acier-avant-tole": (750, 1000, "Annexe couverte d'une ancienne tôle nervurée, avant travaux", "Ancienne couverture en tôle nervurée"),
    "bac-acier-apres-appentis-pignon": (750, 1000, "Annexe couverte de bac acier anthracite, pignon bardé du même bac acier", "Bac acier anthracite, pignon bardé"),
    "bac-acier-pose-en-cours": (750, 1000, "Pose de bac acier anthracite sur voligeage bois, échafaudage en place", "Pose du bac acier sur voligeage"),
    "bac-acier-ossature-pignon": (750, 1000, "Ossature bois du pignon et voligeage prêts à recevoir le bac acier", "Ossature bois du pignon avant bardage"),
    "bac-acier-rive-gouttiere": (750, 1000, "Gouttière et rive en bout de couverture en bac acier anthracite", "Rive et gouttière sur bac acier"),
    "gouttiere-descente-angle": (750, 1000, "Gouttière et descente métalliques à l'angle d'une maison aux volets blancs", "Gouttière et descente à l'angle de la maison"),
    "gouttiere-descente-entree": (750, 1000, "Gouttière et descente métalliques sur une maison de plain-pied", "Gouttière et descente posées"),
    "descente-pied-de-facade": (750, 1000, "Descente d'eaux pluviales métallique fixée en pied de façade", "Descente d'eaux pluviales en pied de façade"),
    "couvertines-toiture-terrasse": (750, 1000, "Couvertines métalliques posées autour d'une toiture terrasse", "Couvertines autour d'une toiture terrasse"),
    "couvertine-detail-rive": (750, 1000, "Détail d'une couvertine métallique en rive de toiture terrasse", "Couvertine en rive de toiture terrasse"),
    "couvertines-solin-angle": (750, 1000, "Couvertines métalliques et solin à l'angle d'une toiture terrasse, contre le mur de la maison", "Couvertines et solin contre le mur"),
    "fenetre-de-toit-avant": (750, 1000, "Ancienne fenêtre de toit avec volet roulant fermé sur une toiture en tuiles, avant travaux", "Ancienne fenêtre de toit"),
    "fenetre-de-toit-apres": (750, 1000, "Fenêtre de toit neuve avec volet roulant solaire et raccord d'étanchéité sur tuiles", "Fenêtre neuve et raccord d'étanchéité"),
}
REASSURANCE = [("DOC", "Devis gratuit", "écrit et détaillé"), ("USER", "Un seul interlocuteur", "l'artisan, du devis à la fin du chantier"),
               ("METAL", "Tous métaux", "zinc, cuivre, acier, aluminium"), ("BROOM", "Chantier nettoyé", "avant notre départ")]

# ---------- Gabarits ----------
def faq_items(keys):
    return [FAQ_COMMON[k] if isinstance(k, str) else k for k in keys]

def consent_default():
    # Mode Consentement v2 : cookies refusés tant que le visiteur n'a pas accepté (choix mémorisé 6 mois).
    return ("<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
            "(function(){var c=null;try{c=JSON.parse(localStorage.getItem('%s')||'null')}catch(e){}"
            "if(c&&(!c.ts||Date.now()-c.ts>%d*864e5))c=null;var g=c&&c.v==='granted'?'granted':'denied';"
            "gtag('consent','default',{ad_storage:g,ad_user_data:g,ad_personalization:g,analytics_storage:g,"
            "functionality_storage:'granted',security_storage:'granted',wait_for_update:500});"
            "})();</script>") % (CONSENT_KEY, CONSENT_DAYS)

def gtm_head():
    s = ("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
         "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
         "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})"
         "(window,document,'script','dataLayer','%s');</script>") % (GTM_ID or "GTM-XXXXXXX")
    return "<!-- Google Tag Manager -->\n" + (s if GTM_ID else "<!-- " + s + " -->")

def gtm_body():
    s = ('<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s" height="0" width="0" '
         'style="display:none;visibility:hidden"></iframe></noscript>') % (GTM_ID or "GTM-XXXXXXX")
    return s if GTM_ID else "<!-- " + s + " -->"

def ld(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>\n' for o in objs if o)

def ld_business():
    o = {"@context": "https://schema.org", "@type": "RoofingContractor", "@id": SITE + "#entreprise", "name": BRAND,
         "url": SITE, "telephone": TEL_INT, "image": SITE + "img/thomas-toiture-ardoise.jpg", "logo": SITE + "img/logo.png",
         "founder": OWNER,
         "address": {"@type": "PostalAddress", "streetAddress": STREET, "postalCode": CP, "addressLocality": CITY, "addressRegion": "Normandie", "addressCountry": "FR"},
         "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
         "areaServed": [{"@type": "AdministrativeArea", "name": "Eure"}] + [{"@type": "City", "name": c} for c in CITIES],
         "openingHoursSpecification": [
             {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:30", "closes": "18:00"},
             {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "07:30", "closes": "13:00"}],
         "sameAs": [INSTAGRAM], "taxID": SIRET.replace(" ", "")}
    if EMAIL: o["email"] = EMAIL
    return o

def url_of(file):
    return SITE if file == "index.html" else SITE + file

def head(title, desc, file, og="img/thomas-toiture-ardoise.jpg", robots="index, follow, max-image-preview:large", extra=""):
    return f"""<!DOCTYPE html>
<html lang="fr-FR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{consent_default()}
{gtm_head()}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url_of(file)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}{og}">
<meta property="og:url" content="{url_of(file)}">
<meta name="theme-color" content="#16130f">
<link rel="icon" type="image/png" href="img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={asset_v('style.css')}">
{extra}</head>
<body>
{gtm_body()}"""

def asset_v(f):  # version dans l'URL : le navigateur recharge le CSS/JS dès qu'il change
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), f)
    return str(int(os.path.getmtime(p))) if os.path.exists(p) else "1"

def header():
    return f"""<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="./" aria-label="{BRAND}, accueil"><img src="img/logo-badge.png" width="91" height="72" alt="Logo {BRAND}"></a>
    <div class="top-cta">
      <a class="btn btn-call" href="tel:{TEL_INT}">{I['PHONE']}<span>{TEL_FR}</span></a>
      <a class="btn btn-main btn-sm top-devis" href="#devis">Devis gratuit</a>
    </div>
  </div>
</header>"""

def cookie_banner():
    return f'''<div class="cookie-banner" id="cookie-banner" role="dialog" aria-labelledby="cookie-title" hidden>
  <div class="cookie-inner">
    <p class="cookie-title" id="cookie-title">Cookies</p>
    <p>Avec votre accord, nous utilisons des cookies Google pour mesurer les demandes de devis et les appels issus de nos annonces. Si vous refusez, aucun de ces cookies n'est déposé et le site fonctionne de la même façon. Votre choix est conservé 6 mois et modifiable via « Gestion des cookies » en bas de page. <a href="confidentialite.html#cookies">En savoir plus</a></p>
    <div class="cookie-actions">
      <button type="button" class="btn cookie-btn" data-consent="denied">Tout refuser</button>
      <button type="button" class="btn cookie-btn" data-consent="granted">Tout accepter</button>
    </div>
  </div>
</div>'''

def footer():
    links = "".join(f'<a href="{p["file"]}">{e(p["lp"])}</a><br>' for p in PAGES[1:])
    mail = f'<a href="mailto:{EMAIL}">{EMAIL}</a><br>' if EMAIL else ""
    return f"""<footer class="foot">
  <div class="wrap foot-in">
    <div><a class="brand" href="./"><img src="img/logo-badge.png" width="122" height="96" alt="" loading="lazy"></a>
      <p>Couvreur zingueur à Portes (27). Couverture, zinguerie et ornementation en zinc et cuivre dans l'Eure.</p></div>
    <div><h3>Contact</h3><p><a href="tel:{TEL_INT}">{TEL_FR}</a><br>{mail}{STREET}<br>{CP} {CITY}<br><span class="muted">{HOURS_TXT}</span></p></div>
    <div><h3>Prestations</h3><p>{links}<a href="{INSTAGRAM}" rel="noopener">Instagram</a></p></div>
  </div>
  <div class="wrap foot-legal">© {YEAR} {BRAND} · <a href="mentions-legales.html">Mentions légales</a> · <a href="confidentialite.html">Confidentialité</a> · <button type="button" class="link-btn" data-consent-open>Gestion des cookies</button></div>
</footer>
<div class="mbar"><a href="tel:{TEL_INT}" class="mbar-call">{I['PHONE']} Appeler</a><a href="#devis" class="mbar-form">Devis gratuit</a></div>
{cookie_banner()}
<script src="main.js?v={asset_v('main.js')}" defer></script>
</body>
</html>"""

ORIGIN_FIELDS = ["gclid", "gbraid", "wbraid", "fbclid", "msclkid", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "referrer", "landing_page"]

def form(p):
    opts = "".join(f'<option{" selected" if n == p["need"] else ""}>{e(n)}</option>' for n in NEEDS)
    placeholder = '' if p["need"] else '<option value="" disabled selected>Choisir…</option>'
    hidden = "".join(f'<input type="hidden" name="{k}" value="">' for k in ORIGIN_FIELDS)
    return f"""<form id="devisForm" class="form" method="POST" action="contact.php">
  <h2>Demandez votre devis gratuit</h2>
  <p class="form-sub">Réponse par téléphone pour fixer une visite.</p>
  <input type="hidden" name="Source" value="{e(p['lp'])}">{hidden}
  <input type="text" name="_honey" tabindex="-1" autocomplete="off" class="hp" aria-hidden="true">
  <div class="row"><label>Nom et prénom<input type="text" name="Nom" required autocomplete="name"></label>
  <label>Téléphone<input type="tel" name="Téléphone" required autocomplete="tel" inputmode="tel"></label></div>
  <div class="row"><label>E-mail<input type="email" name="Email" required autocomplete="email"></label>
  <label>Commune<input type="text" name="Localité" required autocomplete="address-level2" placeholder="Conches, Évreux…"></label></div>
  <label>Votre besoin<select name="Besoin" required>{placeholder}{opts}</select></label>
  <label>Message <span class="opt">(facultatif)</span><textarea name="Message" rows="3" placeholder="Type de toiture (tuile, ardoise, zinc), problème constaté, accès…"></textarea></label>
  <button type="submit" class="btn btn-main btn-block" data-sending="Envoi…">Recevoir mon devis gratuit</button>
  <p class="form-note">Vos coordonnées servent uniquement à répondre à votre demande. <a href="confidentialite.html">Confidentialité</a></p>
</form>"""

def hero(p):
    reas = "".join(f'<li>{I[ic]}<span><b>{e(t)}</b> {e(d)}</span></li>' for ic, t, d in REASSURANCE)
    desk, mob = p["hero"]
    return f"""<section class="hero">
  <picture class="hero-bg"><source media="(max-width:720px)" srcset="img/{mob}.jpg"><img src="img/{desk}.jpg" alt="" fetchpriority="high"></picture>
  <div class="wrap hero-in">
    <div class="hero-txt">
      <p class="eyebrow">{e(p['eyebrow'])}</p>
      <h1>{p['h1']}</h1>
      <p class="lead">{e(p['sub'])}</p>
      <div class="cta"><a href="#devis" class="btn btn-main">{I['ARROW']}Demander un devis gratuit</a><a href="tel:{TEL_INT}" class="btn btn-ghost">{I['PHONE']}<span>{TEL_FR}</span></a></div>
      <ul class="reas">{reas}</ul>
    </div>
    <div class="hero-form" id="devis">{form(p)}</div>
  </div>
</section>"""

def section(eyebrow, h2, inner, lead="", cls="", sid="", center=False):
    a = f' id="{sid}"' if sid else ""
    c = " center" if center else ""
    lead_html = f'<p class="intro">{lead}</p>' if lead else ""
    return f'<section class="sec {cls}"{a}><div class="wrap"><div class="sec-head{c}"><p class="eyebrow">{eyebrow}</p><h2>{h2}</h2>{lead_html}</div>{inner}</div></section>\n'

def tiles(items):
    return '<div class="tiles">' + "".join(f'<div class="tile"><span class="tile-ico">{I[ic]}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>' for ic, t, d in items) + "</div>"

def steps3(items):
    return '<ol class="steps">' + "".join(f'<li><span class="step-n">{n}</span><h3>{e(t)}</h3><p>{e(d)}</p></li>' for n, (t, d) in enumerate(items, 1)) + "</ol>"

def chips(items):
    return '<ul class="chips">' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"

def zone_block():
    cols = "".join(f'<div class="zone"><h3>{e(t)}</h3>{chips(cs)}</div>' for t, cs in ZONES)
    return f'<div class="zones">{cols}</div>'

def faq_block(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"

def cta_band(h2, txt):
    return f"""<section class="band"><div class="wrap band-in"><div><h2>{h2}</h2><p>{e(txt)}</p></div>
<div class="cta"><a href="#devis" class="btn btn-main">{I['ARROW']}Demander un devis gratuit</a><a href="tel:{TEL_INT}" class="btn btn-ghost">{I['PHONE']}<span>{TEL_FR}</span></a></div></div></section>"""

def img(name, pos=""):
    w, h, alt, _ = PHOTOS[name]
    style = f' style="object-position:{pos}"' if pos else ""
    return f'<img src="img/{name}.jpg" width="{w}" height="{h}" alt="{e(alt)}" loading="lazy" decoding="async"{style}>'

def figure(name, cls="photo", pos="", badge=""):
    b = f'<span class="badge">{e(badge)}</span>' if badge else ""
    return f'<figure class="{cls}">{img(name, pos)}{b}<figcaption>{e(PHOTOS[name][3])}</figcaption></figure>'

def gallery(names):
    # les photos paysage occupent deux colonnes
    return '<div class="gallery">' + "".join(figure(n, "photo g-item" + (" wide" if PHOTOS[n][0] > PHOTOS[n][1] else "")) for n in names) + "</div>"

def before_after(before, after):
    return f'<div class="ba">{figure(before, "photo", badge="Avant")}{figure(after, "photo", badge="Après")}</div>'

def page(p, body):
    faq = faq_items(p["faq"])
    ld_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    crumbs = None if p is HOME else {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": p["lp"], "item": url_of(p["file"])}]}
    return head(p["title"], p["desc"], p["file"], og=p["og"], extra=ld(ld_business(), ld_faq, crumbs)) + header() + "\n<main>\n" + hero(p) + "\n" + body + "</main>\n" + footer()

def home():
    p = HOME
    cards = "".join(
        f'<a class="card card-link" href="{s["file"]}">{img(name)}'
        f'<div class="card-body"><h3>{e(t)}</h3><p>{e(d)}</p><span class="more">Voir la prestation {I["ARROW"]}</span></div></a>'
        for s, name, t, d in SERVICES)
    body = section("Nos prestations", "Couverture, fuites <em>et zinguerie</em>", f'<div class="cards cards-3">{cards}</div>'
                   + chips(["Tuile", "Ardoise", "Zinc", "Cuivre", "Bac acier", "Noues et faîtages", "Lucarnes", "Corniches", "Étanchéité"]),
                   lead="Une seule entreprise pour la couverture et tout ce qui est en métal sur votre toit.", sid="prestations")
    body += section("Votre artisan", f"{OWNER.split()[0]}, <em>couvreur zingueur</em>",
                    '<div class="split">' + figure("thomas-toiture-ardoise", pos="50% 30%")
                    + '<div>' + f'<p class="intro">Vous parlez à l\'artisan qui monte sur votre toit, du premier appel à la fin du chantier.</p>'
                    + tiles([("ROOF", "Couverture", "Tuile, ardoise, zinc et bac acier."),
                             ("METAL", "Ferblanterie", "Zinc, cuivre, acier et aluminium façonnés."),
                             ("WALL", "Bâti ancien", "Les matériaux d'origine respectés."),
                             ("USER", "Particuliers et pros", "Maisons, entreprises, collectivités.")])
                    + "</div></div>", cls="sec-alt", sid="artisan")
    body += section("Ornementation", "La signature <em>d'un ferblantier</em>",
                    '<div class="split split-rev">' + figure("girouette-cerf-cuivre", pos="50% 25%")
                    + '<div><p class="intro">Épis de faîtage, girouettes, crêtes, habillages de lucarnes : les finitions en zinc et en cuivre qui donnent du caractère à une toiture.</p>'
                    + chips(["Épis de faîtage", "Girouettes", "Crêtes", "Lucarnes", "Corniches"])
                    + f'<p><a href="{GOUTT["file"]}" class="btn btn-outline">{I["ARROW"]}Zinguerie et ornementation</a></p></div></div>', sid="ornementation")
    body += section("Nos réalisations", "Sur nos <em>chantiers</em>", gallery(HOME_GALLERY),
                    lead="Bac acier, ardoise, couvertines et zinguerie : quelques travaux récents.", cls="sec-alt", sid="realisations")
    body += section("Comment ça se passe", "Votre chantier <em>en 3 étapes</em>",
                    steps3([("Appel ou formulaire", "Décrivez-nous votre toiture et ce qui vous inquiète."),
                            ("Visite et devis gratuit", "Nous venons voir et vous remettons un devis écrit et détaillé."),
                            ("Travaux", "Couverture et zinguerie réalisées, chantier nettoyé avant de partir.")]),
                    cls="sec-dark", sid="methode", center=True)
    body += section("Zone d'intervention", "Couvreur autour de <em>Conches-en-Ouche et Évreux</em>", zone_block(),
                    lead="Depuis Portes, nous intervenons dans ces communes et leurs environs.", cls="sec-alt", sid="zone")
    body += section("Questions fréquentes", "Avant de <em>nous appeler</em>", faq_block(faq_items(p["faq"])), sid="faq", center=True)
    body += cta_band("Un projet de toiture ?", "Décrivez-nous votre toiture : nous vous rappelons pour fixer une visite et établir un devis gratuit.")
    return page(p, body)

def service(p):
    works = "".join(
        f'<article class="card"><span class="tag">{e(tag)}</span><h3>{e(t)}</h3><p>{e(d)}</p><ul class="checks">'
        + "".join(f"<li>{I['CHECK']}{e(x)}</li>" for x in pts) + "</ul></article>" for tag, t, d, pts in p["works"])
    others = "".join(f'<a class="other" href="{s["file"]}">{e(s["lp"])} {I["ARROW"]}</a>' for s in PAGES[1:] if s is not p)
    body = section("Quand nous appeler", "Les signes <em>à surveiller</em>", tiles(p["signs"]), sid="signes")
    body += section("Ce que nous faisons", f"{e(p['lp'])} : <em>nos interventions</em>",
                    '<div class="split split-wide"><div class="cards">' + works + "</div>"
                    + figure(p["photo"]) + "</div>", cls="sec-alt", sid="prestations")
    if p.get("ba"):
        before, after, eyebrow, h2, lead = p["ba"]
        body += section(eyebrow, h2, before_after(before, after), lead=e(lead), sid="avant-apres", center=True)
    if p.get("gallery"):
        eyebrow, h2, names = p["gallery"]
        body += section(eyebrow, h2, gallery(names), cls="sec-alt" if p.get("ba") else "", sid="realisations", center=True)
    body += section("Comment ça se passe", "Votre chantier <em>en 3 étapes</em>", steps3(p["steps"]), cls="sec-dark", sid="methode", center=True)
    body += section("Zone d'intervention", "Dans l'Eure, <em>autour de Portes</em>", zone_block(),
                    lead="Conches-en-Ouche, Évreux, Le Neubourg, Beaumont-le-Roger et les communes voisines.", sid="zone")
    body += section("Questions fréquentes", "Vos questions, <em>nos réponses</em>", faq_block(faq_items(p["faq"])), cls="sec-alt", sid="faq", center=True)
    body += section("Autres prestations", "Nous intervenons aussi pour", f'<div class="others"><a class="other" href="./">Accueil {I["ARROW"]}</a>{others}</div>', center=True)
    body += cta_band("Parlons de votre toiture", "Appelez-nous ou remplissez le formulaire : nous vous rappelons pour fixer une visite.")
    return page(p, body)

def simple(title, desc, file, inner, robots="noindex, follow"):
    # pages sans formulaire : les boutons « Devis gratuit » renvoient au formulaire de l'accueil
    return (head(title, desc, file, robots=robots) + header() + f'\n<main>\n<section class="sec"><div class="wrap narrow legal">{inner}</div></section>\n</main>\n'
            + footer()).replace('href="#devis"', 'href="./#devis"')

def merci():
    inner = f"""<h1>Votre demande est bien envoyée</h1>
<p>Merci. Nous vous rappelons pour fixer une visite et préparer votre devis. Pour une fuite ou une urgence, appelez-nous directement.</p>
<div class="cta"><a href="tel:{TEL_INT}" class="btn btn-main">{I['PHONE']}<span>{TEL_FR}</span></a><a href="./" class="btn btn-outline">Retour à l'accueil</a></div>"""
    return simple("Demande envoyée | " + BRAND, "Votre demande de devis a bien été envoyée.", "merci.html", inner, robots="noindex, nofollow")

def page404():
    inner = f"""<h1>Page introuvable</h1><p>Cette page n'existe pas ou a été déplacée.</p>
<div class="cta"><a href="./" class="btn btn-main">Retour à l'accueil</a><a href="tel:{TEL_INT}" class="btn btn-outline">{I['PHONE']}<span>{TEL_FR}</span></a></div>"""
    # servie à n'importe quelle profondeur d'URL : liens relatifs résolus depuis la racine
    return simple("Page introuvable | " + BRAND, "Page introuvable.", "404.html", inner, robots="noindex, nofollow").replace("<head>\n", '<head>\n<base href="/">\n', 1)

def mentions():
    mail = f', <a href="mailto:{EMAIL}">{EMAIL}</a>' if EMAIL else ""
    inner = f"""<h1>Mentions légales</h1>
<h2>Éditeur du site</h2>
<p>{BRAND}, entreprise individuelle de {OWNER}<br>{STREET}, {CP} {CITY}<br>Téléphone : <a href="tel:{TEL_INT}">{TEL_FR}</a>{mail}<br>
SIREN {SIREN} · SIRET {SIRET} · TVA intracommunautaire {TVA}<br>Activité : travaux de couverture (NAF 43.91B)</p>
<h2>Directeur de la publication</h2><p>{OWNER}</p>
<h2>Hébergement</h2><p>IONOS SARL, 7 place de la Gare, BP 70109, 57200 Sarreguemines Cedex · ionos.fr</p>
<h2>Propriété intellectuelle</h2><p>Les textes, photos et le logo de ce site appartiennent à {BRAND}. Toute reproduction sans autorisation est interdite.</p>
<h2>Données personnelles</h2><p>Voir la <a href="confidentialite.html">politique de confidentialité</a>.</p>"""
    return simple("Mentions légales | " + BRAND, "Mentions légales du site " + BRAND + ".", "mentions-legales.html", inner)

def confidentialite():
    contact = f'<a href="mailto:{EMAIL}">{EMAIL}</a> ou au <a href="tel:{TEL_INT}">{TEL_FR}</a>' if EMAIL else f'au <a href="tel:{TEL_INT}">{TEL_FR}</a> ou par courrier à l\'adresse ci-dessus'
    inner = f"""<h1>Politique de confidentialité</h1>
<h2>Responsable du traitement</h2><p>{BRAND} ({OWNER}), {STREET}, {CP} {CITY}.</p>
<h2>Données collectées</h2><p>Lorsque vous remplissez le formulaire de demande de devis, nous recueillons les informations que vous indiquez : nom, téléphone, e-mail, commune, besoin et message, ainsi que la page d'arrivée et la source de la visite (annonce, moteur de recherche, lien).</p>
<h2>Utilisation</h2><p>Ces données servent uniquement à vous recontacter et à préparer votre devis. Elles ne sont ni vendues ni cédées. Elles sont traitées par {BRAND} et ses prestataires techniques (hébergement, messagerie, gestion des demandes).</p>
<h2>Durée de conservation</h2><p>Trois ans au maximum après notre dernier échange, puis suppression.</p>
<h2 id="cookies">Cookies</h2><p>Avec votre accord, des cookies Google (Google Ads, via Google Tag Manager) mesurent les demandes de devis et les appels issus de nos annonces. Sans accord, aucun de ces cookies n'est déposé. Votre choix est conservé 6 mois et modifiable à tout moment : <button type="button" class="link-btn" data-consent-open>gérer les cookies</button>.</p>
<h2>Vos droits</h2><p>Vous pouvez demander l'accès à vos données, leur rectification ou leur suppression, et vous opposer à leur utilisation, en nous contactant {contact}. Vous pouvez aussi adresser une réclamation à la CNIL (cnil.fr).</p>"""
    return simple("Confidentialité | " + BRAND, "Politique de confidentialité de " + BRAND + ".", "confidentialite.html", inner)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = {"index.html": home(), "merci.html": merci(), "404.html": page404(),
           "mentions-legales.html": mentions(), "confidentialite.html": confidentialite()}
    for p in PAGES[1:]:
        out[p["file"]] = service(p)
    for f, s in out.items():
        open(os.path.join(here, f), "w", encoding="utf-8").write(s)
    open(os.path.join(here, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    urls = "".join(f"<url><loc>{url_of(p['file'])}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    open(os.path.join(here, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print("OK :", ", ".join(out), "+ robots.txt, sitemap.xml")
