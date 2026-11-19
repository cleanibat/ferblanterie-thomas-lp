# -*- coding: utf-8 -*-
"""Génère les fichiers d'import Google Ads Editor des 4 campagnes Search de La Ferblanterie de Thomas (compte 609-880-3097).
Usage : python3 ads/build_ads.py  →  ads/1-campagnes-google-ads-editor.csv et ads/2-composants-google-ads-editor.csv
Format : tabulations, UTF-16 (format natif de Google Ads Editor). Import : Compte > Importer > À partir d'un fichier.

Une campagne par page zone (même ciblage géographique que la page). Chaque campagne ajoute « zone=<clé> » à ses URL
(suffixe d'URL finale) : les pages services affichent alors la zone de l'annonce.
"""
import csv, io, math, os, sys

SITE = "https://laferblanteriedethomas.com/"
STATUS = "Paused"                       # tout est importé en pause : Aymeric relit et active
BUDGET_MENSUEL = 700                    # hypothèse en attendant le budget réel (même point de départ que La Rénovation de vos rêves)
PHONE = ("+33778375291", "FR")
RENO, FUITE, GOUTT = SITE + "renovation-toiture.html", SITE + "reparation-fuite-toiture.html", SITE + "gouttieres-zinguerie.html"

# Critères géographiques Google (geotargets 2026-10-06), ciblage par département, « Présence » seulement
DEPTS = {"Eure": (9040862, "Eure, Normandy, France"), "Calvados": (9040909, "Calvados, Normandy, France"),
         "Orne": (9040863, "Orne, Normandy, France"), "Eure-et-Loir": (9040865, "Eure-et-Loir, Centre-Val de Loire, France"),
         "Yvelines": (9040873, "Yvelines, Ile-de-France, France"), "Paris": (9040871, "Paris, Ile-de-France, France")}

ZONES = [
  dict(key="eure", name="Eure (27)", page="couvreur-eure.html", depts=["Eure"], share=9, a="Eure", b="à Évreux",
       path="eure", fuite=True,
       cities=["évreux", "conches en ouche", "bernay", "vernon", "louviers", "le neubourg", "verneuil sur avre", "pont audemer"],
       zdesc="Basés à Portes, entre Conches-en-Ouche et Évreux, nous intervenons dans toute l'Eure."),
  dict(key="calvados-orne", name="Calvados et Orne (14-61)", page="couvreur-calvados-orne.html", depts=["Calvados", "Orne"], share=6,
       a="Calvados", b="dans l'Orne", path="calvados-orne", fuite=False,
       cities=["lisieux", "caen", "deauville", "honfleur", "l'aigle", "alençon", "argentan", "pont l'évêque"],
       zdesc="Depuis Portes (27), nous intervenons dans le Calvados et l'Orne, de Lisieux à Alençon."),
  dict(key="eure-et-loir-yvelines", name="Eure-et-Loir et Yvelines (28-78)", page="couvreur-eure-et-loir-yvelines.html",
       depts=["Eure-et-Loir", "Yvelines"], share=5, a="Eure-et-Loir", b="dans les Yvelines", path="yvelines", fuite=False,
       cities=["dreux", "chartres", "mantes la jolie", "houdan", "rambouillet", "versailles", "saint germain en laye"],
       zdesc="Depuis Portes (27), nous intervenons de Dreux à Chartres et de Mantes à Versailles."),
  dict(key="paris", name="Paris (75)", page="couvreur-paris.html", depts=["Paris"], share=3, a="Paris", b="à Paris",
       path="paris", fuite=False, cities=["paris"],
       zdesc="Copropriétés et maisons de ville : nous intervenons dans les 20 arrondissements."),
]
TOTAL_JOUR = math.floor(BUDGET_MENSUEL / 30.4 * 100) / 100          # 23,02 €/jour pour 700 €/mois
SHARES = sum(z["share"] for z in ZONES)

def groups(z):
    a, b, page, c = z["a"], z["b"], SITE + z["page"], z["cities"]
    paris = z["key"] == "paris"
    g = [dict(name="Couvreur zingueur", url=page, path=("couvreur", z["path"]),
              phrase=["couvreur", "couvreur zingueur", "artisan couvreur", "entreprise de couverture", "entreprise couverture toiture",
                      "zingueur", "couvreur ardoise"] + [f"couvreur {v}" for v in c] + [f"couvreur zingueur {v}" for v in c[:3]]
                     + (["toiture zinc paris", "couverture zinc paris", "couvreur zinc"] if paris else
                        [f"couvreur {d.lower()}" for d in z["depts"]]),
              exact=["couvreur zingueur", "artisan couvreur"] + [f"couvreur {v}" for v in c[:3]],
              headlines=[f"Couvreur zingueur {a}", f"Couvreur {b}", "Artisan couvreur zingueur", "Devis gratuit et détaillé",
                         "Rénovation de toiture", "Gouttières et zinguerie", "Zinc, cuivre, ardoise, tuile", "Un seul interlocuteur",
                         "Ornementation zinc et cuivre", "Particuliers et pros", "Chantier nettoyé", "Basé à Portes (27)",
                         "Toiture ardoise et tuile", "Demandez votre devis",
                         "Couverture zinc et ardoise" if paris else "Réparation de fuite"],
              descriptions=["Rénovation de toiture, fuites, gouttières et ornementation en zinc et cuivre.",
                            "Ardoise, tuile, zinc ou aluminium : un artisan couvreur zingueur, du devis à la fin.",
                            "Devis gratuit, écrit et détaillé. Chantier nettoyé avant notre départ.", z["zdesc"]]),
         dict(name="Rénovation de toiture", url=RENO, path=("renovation", "toiture"),
              phrase=["rénovation toiture", "réfection toiture", "refaire toiture", "refaire sa toiture", "rénovation de toiture",
                      "réfection de toiture", "toiture ardoise", "réfection toiture ardoise", "remplacement toiture",
                      "changer toiture", "remplacement velux", "remplacement fenêtre de toit"]
                     + [f"rénovation toiture {v}" for v in c[:4]] + [f"réfection toiture {v}" for v in c[:2]],
              exact=["rénovation toiture", "réfection toiture", "refaire toiture"] + [f"rénovation toiture {c[0]}"],
              headlines=[f"Réfection toiture {a}", f"Couvreur {b}", "Rénovation de toiture", "Réfection totale ou partielle",
                         "Ardoise, tuile et zinc", "Écran sous-toiture neuf", "Liteaux et faîtage refaits", "Velux et raccords étanches",
                         "Devis gratuit et détaillé", "Artisan couvreur zingueur", "Un seul interlocuteur", "Chantier nettoyé",
                         "Aluminium joint debout", "Matériaux d'origine respectés", "Maison hors d'eau chaque soir"],
              descriptions=["Réfection complète ou partielle : écran sous-toiture, liteaux, couverture et faîtage.",
                            "Ardoise, tuile, zinc ou aluminium joint debout, avec des matériaux proches de l'existant.",
                            "Devis gratuit, écrit et détaillé, poste par poste. Maison hors d'eau chaque soir.", z["zdesc"]]),
         dict(name="Gouttières et zinguerie", url=GOUTT, path=("gouttieres", "zinguerie"),
              phrase=["gouttière", "pose gouttière", "remplacement gouttière", "changer gouttière", "gouttière zinc", "gouttière cuivre",
                      "gouttière aluminium", "zinguerie", "zingueur", "ferblantier", "chéneau zinc", "descente eau pluviale",
                      "épi de faîtage", "girouette zinc", "couvertine zinc"] + [f"gouttière {v}" for v in c[:4]] + [f"zingueur {v}" for v in c[:2]],
              exact=["pose gouttière", "remplacement gouttière", "zingueur", "gouttière zinc"],
              headlines=[f"Gouttières {a}", f"Zingueur {b}", "Gouttières zinc et cuivre", "Pose et remplacement", "Chéneaux et descentes",
                         "Zinguerie sur mesure", "Artisan ferblantier", "Habillages et couvertines", "Épis et girouettes",
                         "Gouttières aluminium", "Devis gratuit et détaillé", "Un seul interlocuteur", "Ornementation zinc et cuivre",
                         "Fini les débordements", "Raccords étanches"],
              descriptions=["Gouttières, chéneaux et descentes en zinc, cuivre ou aluminium, posés sur mesure.",
                            "Couvertines, rives, noues et abergements façonnés par un ferblantier.",
                            "Épis de faîtage, girouettes, crêtes : l'ornementation qui signe une toiture.", z["zdesc"]])]
    if z["fuite"]:
        g.append(dict(name="Réparation de fuite", url=FUITE, path=("fuite", "toiture"),
              phrase=["fuite toiture", "réparation fuite toiture", "recherche fuite toiture", "réparation toiture", "réparer toiture",
                      "infiltration toiture", "tuile cassée", "fuite toit", "fuite cheminée toit", "fuite velux",
                      "réparation toit"] + [f"réparation toiture {v}" for v in c[:4]] + [f"fuite toiture {v}" for v in c[:2]],
              exact=["fuite toiture", "réparation fuite toiture", "réparation toiture"],
              headlines=[f"Fuite de toiture {a}", f"Couvreur {b}", "Recherche de fuite toiture", "Réparation de toiture",
                         "Tuiles et ardoises remplacées", "Noues et abergements", "Faîtage repris", "Raccords de cheminée",
                         "Devis gratuit et détaillé", "Artisan couvreur zingueur", "Vérification après tempête", "Devis pour votre assureur",
                         "Un seul interlocuteur", "On trouve l'origine", "Appelez-nous"],
              descriptions=["Nous cherchons d'où vient l'eau, puis réparons la couverture ou la zinguerie en cause.",
                            "Tuiles, ardoises, faîtage, noues, abergements de cheminée et de fenêtre de toit.",
                            "Après une tempête, devis détaillé à transmettre à votre assureur.", z["zdesc"]]))
    return g

NEGATIVES = ["emploi", "recrutement", "salaire", "formation", "cap", "apprenti", "apprentissage", "stage", "alternance", "cours",
             "tuto", "tutoriel", "soi même", "diy", "bricolage", "leroy merlin", "castorama", "brico dépôt", "occasion", "pdf",
             "wikipedia", "définition", "logiciel", "fiche métier", "nettoyage", "démoussage", "hydrofuge", "panneau solaire",
             "photovoltaïque", "isolation", "charpentier", "charpente", "bac acier", "chaume", "plombier", "plomberie",
             "gouttière pvc", "location", "nacelle location", "échafaudage location"]
FAR_NEGATIVES = ["urgence", "urgent", "dépannage", "24h", "nuit", "dimanche"]     # dépannage gardé pour l'Eure

def sitelinks(z):
    page = SITE + z["page"]
    s = [("Rénovation de toiture", "Réfection complète ou partielle", "Ardoise, tuile, zinc", RENO),
         ("Gouttières et zinguerie", "Zinc, cuivre, aluminium", "Chéneaux, descentes, habillages", GOUTT),
         ("Demander un devis", "Devis gratuit et détaillé", "Réponse par téléphone", page + "#devis"),
         ("Nos réalisations", "Quelques chantiers récents", "Couverture et zinguerie", page + "#realisations")]
    if z["fuite"]: s.insert(1, ("Réparation de fuite", "On trouve l'origine de l'eau", "Couverture et zinguerie", FUITE))
    return s
CALLOUTS = ["Devis gratuit", "Un seul interlocuteur", "Zinc, cuivre, ardoise", "Chantier nettoyé", "Particuliers et pros",
            "Basé à Portes (27)", "Ornementation sur mesure"]
SNIPPET = ("Services", ["Rénovation de toiture", "Réparation de fuite", "Gouttières", "Zinguerie", "Ornementation"])

# ---------------- Contrôles des limites Google Ads ----------------
errors = []
def lim(txt, n, what):
    if len(txt) > n: errors.append(f"{what} > {n} caractères ({len(txt)}) : {txt}")
    if "!" in txt: errors.append(f"Point d'exclamation : {txt}")
for z in ZONES:
    for g in groups(z):
        tag = f"{z['key']} / {g['name']}"
        if len(g["headlines"]) != 15 or len(set(g["headlines"])) != 15: errors.append(f"{tag} : il faut 15 titres distincts")
        if len(g["descriptions"]) != 4: errors.append(f"{tag} : il faut 4 descriptions")
        for h in g["headlines"]: lim(h, 30, f"Titre {tag}")
        for d in g["descriptions"]: lim(d, 90, f"Description {tag}")
        for p in g["path"]: lim(p, 15, f"Chemin {tag}")
        for k in g["phrase"] + g["exact"]: lim(k, 80, "Mot-clé")
        if len(set(g["phrase"])) != len(g["phrase"]): errors.append(f"{tag} : mots-clés en double")
    for t, d1, d2, _ in sitelinks(z): lim(t, 25, "Lien annexe"); lim(d1, 35, "Description lien"); lim(d2, 35, "Description lien")
for c in CALLOUTS: lim(c, 25, "Accroche")
for v in SNIPPET[1]: lim(v, 25, "Extrait")
if errors: sys.exit("\n".join(errors))

# ---------------- Fichier 1 : campagnes, zones, groupes, mots-clés, annonces ----------------
H1 = ["Campaign", "Campaign Type", "Networks", "Budget", "Budget type", "Bid Strategy Type", "Languages", "Targeting method",
      "Exclusion method", "Final URL suffix", "Campaign Status", "Location", "Location ID", "Ad Group", "Ad Group Status", "Keyword",
      "Criterion Type", "Status", "Ad type"] + [f"Headline {i}" for i in range(1, 16)] + [f"Description {i}" for i in range(1, 5)] + \
     ["Path 1", "Path 2", "Final URL"]
H2 = ["Campaign", "Sitelink text", "Description line 1", "Description line 2", "Final URL", "Callout text", "Header",
      "Snippet values", "Phone Number", "Country code", "Status"]
rows, rows2, summary = [], [], []
for z in ZONES:
    camp = f"Search - Ferblanterie - {z['name']}"
    budget = math.floor(TOTAL_JOUR * z["share"] / SHARES * 100) / 100
    def row(**kw):
        r = {h: "" for h in H1}; r["Campaign"] = camp
        for k, v in kw.items(): r[k.replace("_", " ")] = v
        rows.append(r)
    row(Campaign_Type="Search", Networks="Google search", Budget=f"{budget:.2f}", Budget_type="Daily",
        Bid_Strategy_Type="Maximize conversions", Languages="fr", Targeting_method="Location of presence",
        Exclusion_method="Location of presence", Final_URL_suffix=f"zone={z['key']}", Campaign_Status=STATUS)
    for d in z["depts"]: row(Location=DEPTS[d][1], Location_ID=str(DEPTS[d][0]))
    negs = NEGATIVES + ([] if z["fuite"] else FAR_NEGATIVES)
    for n in negs: row(Keyword=n, Criterion_Type="Campaign negative")
    gs = groups(z)
    for g in gs:
        row(Ad_Group=g["name"], Ad_Group_Status="Enabled")
        for k in g["phrase"]: row(Ad_Group=g["name"], Keyword=k, Criterion_Type="Phrase", Status="Enabled")
        for k in g["exact"]: row(Ad_Group=g["name"], Keyword=k, Criterion_Type="Exact", Status="Enabled")
        ad = {f"Headline_{i+1}": h for i, h in enumerate(g["headlines"])}
        ad.update({f"Description_{i+1}": d for i, d in enumerate(g["descriptions"])})
        row(**ad, Ad_Group=g["name"], Ad_type="Responsive search ad", Path_1=g["path"][0], Path_2=g["path"][1],
            Final_URL=g["url"], Status="Enabled")
    def row2(**kw):
        r = {h: "" for h in H2}; r["Campaign"] = camp; r["Status"] = "Enabled"
        for k, v in kw.items(): r[k.replace("_", " ")] = v
        rows2.append(r)
    for t, d1, d2, u in sitelinks(z): row2(Sitelink_text=t, Description_line_1=d1, Description_line_2=d2, Final_URL=u)
    for c in CALLOUTS: row2(Callout_text=c)
    snip = SNIPPET[1] if z["fuite"] else [v for v in SNIPPET[1] if v != "Réparation de fuite"]
    row2(Header=SNIPPET[0], Snippet_values=";".join(snip))
    row2(Phone_Number=PHONE[0], Country_code=PHONE[1])
    kw = sum(len(g["phrase"]) + len(g["exact"]) for g in gs)
    summary.append(f"{camp} : {budget:.2f} €/jour, {len(gs)} groupes, {kw} mots-clés, {len(negs)} négatifs, zone={z['key']}")

def write(path, header, data):
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=header, delimiter="\t", lineterminator="\r\n"); w.writeheader(); w.writerows(data)
    open(path, "w", encoding="utf-16", newline="").write(buf.getvalue())
here = os.path.dirname(os.path.abspath(__file__))
write(os.path.join(here, "1-campagnes-google-ads-editor.csv"), H1, rows)
write(os.path.join(here, "2-composants-google-ads-editor.csv"), H2, rows2)
print("\n".join(summary))
print(f"Total {sum(math.floor(TOTAL_JOUR * z['share'] / SHARES * 100) / 100 for z in ZONES):.2f} €/jour ; {len(rows)} + {len(rows2)} lignes ; statut {STATUS}")
