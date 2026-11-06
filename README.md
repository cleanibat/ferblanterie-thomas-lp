# La Ferblanterie de Thomas – Landing pages Google Ads

Site statique. Chaque push sur `main` déploie automatiquement (workflow dans `.github/workflows/`, garder celui de l'hébergeur utilisé).
Aperçu : https://cleanibat.github.io/ferblanterie-thomas-lp/

## Checklist de lancement
1. E-mail de réception des leads dans `contact.php` (formulaire HTML classique, aucun service tiers ; l'aperçu GitHub Pages n'envoie rien, c'est normal).
2. ID GTM dans la config du site, conteneur importé et publié (`gtm_container.py`).
3. Conversions Google Ads créées et importées dans GTM.
4. Domaine final dans canonical, `_next`, sitemap.
5. Test de bout en bout du formulaire.
