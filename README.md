# La Ferblanterie de Thomas – site web

Couvreur zingueur à Portes (27). Site statique généré par `build.py` (accueil + 3 pages services : rénovation de toiture, réparation de fuite, gouttières et zinguerie).
Production : https://laferblanteriedethomas.com/ (IONOS Hébergement Web Plus, contrat 300541272). Aperçu : https://cleanibat.github.io/ferblanterie-thomas-lp/ (le formulaire n'y fonctionne pas, c'est normal).

Déploiement : push sur `main` → `.github/workflows/deploy-ssh.yml` (rsync SSH vers IONOS), actif quand la variable de dépôt `DEPLOY` vaut `on`.

## Reste à faire
1. Adresse e-mail de Thomas : `EMAIL` dans build.py, `$DEST` dans contact.php.
2. ID GTM dans build.py, conteneur importé et publié ; conversions Google Ads.
3. Test de bout en bout du formulaire (`contact.php?test=1`).
4. À confirmer avec Thomas : zone d'intervention (communes à moins de 30 km de Portes), devis gratuit, assurance décennale, logo haute définition, autres photos de chantier.
