# Registre des Risques Résiduels & Points d'Attention
**Projet :** Cytria Real Estate Intelligence (Genève)  
**Date :** 4 Octobre 2026  
**Document :** `docs/hardening/SECURITY_AND_DATA_RISKS.md`  

Ce document répertorie **exclusivement les risques non résolus**, les limitations inhérentes aux sources de données officielles genevoises, et les points requérant un arbitrage métier ou une validation humaine.

---

## 1. Risques Résiduels Techniques & Données

### RISK-01 : Défi Anti-Bot (CAPTCHA / Cloudflare) sur le Portail FAO
- **Description :** Le portail de la Feuille d'Avis Officielle (`fao.ge.ch`) déploie périodiquement des défis JavaScript ou CAPTCHA Cloudflare lors des requêtes automatisées en masse.
- **État Actuel :** Le code lève désormais une exception explicite `AntiBotChallengeException` (`src/fao_transactions/collector/browser.py`) au lieu d'échouer silencieusement ou d'enregistrer des pages blanches.
- **Risque Résiduel :** L'automatisation complète en arrière-plan sans surveillance humaine (cron sans écran) peut être bloquée en cas de déclenchement du challenge de sécurité cantonal.
- **Action / Recommandation :** Maintenir le mode interactif ou semi-automatisé (`launch_fao_scraper.bat` avec navigateur visible) pour permettre à l'opérateur de résoudre le défi lors de la première initialisation de session.

### RISK-02 : Écart entre Date de l'Acte Notarié et Date de Publication FAO (CASATAX)
- **Description :** L'éligibilité au barème CASATAX est légalement rattachée à la date de signature de l'acte authentique chez le notaire (ou date d'inscription au Registre Foncier). Or, la FAO ne publie que la date de parution de l'avis officiel (généralement 15 à 45 jours après la signature notariale).
- **Impact :** Pour les transactions intervenues aux limites des exercices légaux (notamment fin février / début mars), un acte signé le 27 février 2026 sous l'ancien plafond (CHF 1'374'396) peut être publié en avril 2026 sous le nouveau plafond (CHF 1'394'928).
- **Atténuation Appliquée :** Les rapports CMA indiquent désormais l'éligibilité CASATAX comme un *indicateur de seuil de prix* indicatif.
- **Action Requise :** L'utilisateur final (courtier ou notaire) doit vérifier l'instrumentum notarié pour les cas frontières situés entre 1'374'396 CHF et 1'394'928 CHF au 1er trimestre 2026.

### RISK-03 : Quotas et Disponibilité de l'API SITG (Open Data Cadastre)
- **Description :** L'enrichissement géocadastral et les requêtes altimétriques/zonages s'appuient sur les services cartographiques du Système d'Information du Territoire à Genève (SITG).
- **Risque Résiduel :** En cas d'indisponibilité du serveur cantonal ou de modifications des couches WFS/REST (classes de zonage 5, 4A, 4B), l'enrichissement en temps réel peut être temporairement ralenti.
- **Atténuation :** La base SQLite locale met en cache les centroïdes LV95/WGS84 et les correspondances parcellaires déjà résolues.

---

## 2. Risques Juridiques et Décisions Requérant une Révision Humaine

### RISK-04 : Délimitation Juridique entre Analyse Comparative de Marché (CMA) et Expertise Hypothécaire Bancaire
- **Contexte Légal :** En droit suisse, une valorisation automatisée basée sur des comparables de transactions notariées constitue une Analyse Comparative de Marché (CMA) à visée d'aide à la négociation commerciale. Elle ne remplace pas une expertise vénale formelle (norme SXI / OES) exigée par les établissements bancaires (BCGE, UBS, Raiffeisen) pour l'octroi d'un prêt hypothécaire.
- **Statut :** **REQUIRES HUMAN REVIEW / DÉCISION MÉTIER**
- **Recommandation :** Veiller à ce que les courtiers partenaires n'utilisent pas les exports PDF/HTML en tant que "rapport d'expertise bancaire agréé", mais strictement en tant qu'"Analyse Comparative de Marché fondée sur les avis de mutations foncières".

### RISK-05 : Attribution des Ventes d'Agences Non Rapprocheables à 100%
- **Contexte :** 2'183 ventes d'agences sont réconciliées dans la table `agency_sold_properties`. Certaines annonces de portails (ex. portails immobiliers suisses) omettent le numéro de parcelle officiel ou arrondissent le prix d'affichage de quelques milliers de francs par rapport à l'acte notarié authentique (négociation finale).
- **Risque Résiduel :** Un très faible pourcentage de ventes d'agences indépendantes ne peut être réconcilié automatiquement sans arbitrage subjectif.
- **Recommandation :** Conserver la colonne `reconciliation_level` (`CONFIRMED_FAO`, `HIGH_PROBABILITY`, `UNMATCHED`) et ne jamais forcer de fausse réconciliation sans confirmation documentaire.
