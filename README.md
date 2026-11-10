# La Ferblanterie de Thomas – site web

Couvreur zingueur à Portes (27). Site statique généré par `build.py` : accueil, 3 pages services (rénovation de toiture, réparation de fuite, gouttières et zinguerie) et 4 pages zones.

## Pages zones et campagnes Google Ads
Une page par zone, une campagne Google Ads par page (même ciblage géographique) :

| Page | Départements | Suffixe d'URL finale de la campagne |
|---|---|---|
| couvreur-eure.html | 27 | `zone=eure` |
| couvreur-calvados-orne.html | 14, 61 | `zone=calvados-orne` |
| couvreur-eure-et-loir-yvelines.html | 28, 78 | `zone=eure-et-loir-yvelines` |
| couvreur-paris.html | 75 | `zone=paris` |

Avec ce suffixe, les pages services affichent la zone de la campagne (hero, bloc zone, liens). Sans paramètre, elles affichent « Eure et départements voisins ». Les annonces génériques (couvreur, toiture) renvoient vers la page zone, les annonces par service vers la page service.
Production : https://laferblanteriedethomas.com/ (IONOS Hébergement Web Plus, contrat 300541272). Aperçu : https://cleanibat.github.io/ferblanterie-thomas-lp/ (le formulaire n'y fonctionne pas, c'est normal).

Déploiement : push sur `main` → `.github/workflows/deploy-ssh.yml` (rsync SSH vers IONOS), actif quand la variable de dépôt `DEPLOY` vaut `on`.

## Reste à faire
1. Adresse e-mail de Thomas : `EMAIL` dans build.py, `$DEST` dans contact.php.
2. ID GTM dans build.py, conteneur importé et publié ; conversions Google Ads.
3. Test de bout en bout du formulaire (`contact.php?test=1`).
4. À confirmer avec Thomas : déplacements lointains (Paris, Caen, Alençon, Chartres) et montant minimum de chantier, devis gratuit, assurance décennale, logo haute définition, autres photos de chantier.
