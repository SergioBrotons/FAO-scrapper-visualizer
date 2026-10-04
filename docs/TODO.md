# Cytria — Backlog & Roadmap des Tâches (TODO)

> Dernière mise à jour : 02 Octobre 2026  
> Statut global : Système de synchronisation Fast-Lane opérationnel (8'970 actes préservés, 8'548 cartographiés).

---

## 📌 Priorité Haute : Fiabilisation des Données Courtiers & Profils LinkedIn

### Constat & Diagnostic
* **Agences Immobilières (83 agences)** : Données 100% fiabilisées et réconciliées avec le Registre du Commerce de Genève (RC) et le registre fédéral **ZEFIX** (raison sociale, UID CHE, sièges, dirigeants, mandats).
* **Courtiers & Négociateurs (93 profils)** : La couverture des courtiers et les slugs de profils LinkedIn individuels comportent des approximations et des liens non garantis.

### Mesure Immédiate Prise (UI)
* **Mise en retrait visuelle (Grisage)** :
  * Les liens directs vers les profils LinkedIn des courtiers individuels ont été neutralisés et grisés avec la mention : `🔒 LinkedIn : En cours de vérification`.
  * L'onglet **Courtiers & Négociateurs** dans la League Table affiche le badge `EN COURS DE FIABILISATION`.
  * Un bandeau d'avertissement informe l'utilisateur que seules les données agences certifiées font foi pour le moment.

### Actions à Mener (TODO Checklist)
- [ ] **1. Extraction des Annuaires d'Équipes Officiels** :
  * Scraper ou auditer les pages officielles *"Notre Équipe"* / *"Team"* des 83 agences genevoises pour consolider la liste exacte des négociateurs en poste.
- [ ] **2. Vérification des Profils LinkedIn Individuels** :
  * Valider manuellement ou via recherche ciblée (Google Search / LinkedIn Search) les URLs exactes des courtiers confirmés rattachés à leur agence genevoise.
  * Éliminer les homonymes ou profils inactifs.
- [ ] **3. Structure de Données & Statut de Validation** :
  * Ajouter un champ booléen `linkedin_verified: bool` et `last_verified_at: string` dans `geneva_brokers_master.json`.
  * Ne réactiver le bouton bleu cliquable que pour les profils ayant `linkedin_verified === true`.

---

## 📌 Phase 3 : Scraper Ciblé d'Enrichissement Légal (Audit FAO Sélectif)

- [ ] **1. Repositionnement du Scraper Playwright** :
  * Transformer le scraper de masse en scanner de précision sur les dossiers à haute valeur :
    * Ventes > 5'000'000 CHF.
    * Opportunités de falaise CASATAX (prix juste sous le seuil d'exonération).
    * Parcelles Zone 5 > 1'200 m² à fort potentiel de densification.
- [ ] **2. Extraction des Identités Légales des Parties** :
  * Récupérer le texte intégral du bordereau notarié sur `fao.ge.ch`.
  * Extraire le nom légal des vendeurs et acquéreurs pour alimenter le **Radar Développeurs** et le **Radar Hoiries & Successions**.

---

## 📌 Maintenance & Infrastructure

- [x] Remplacement des chemins virtuels obsolètes par `.venv` généré via `uv` avec l'ensemble des 44 dépendances.
- [x] Intégration de la recompilation automatique de la carte interactive (`index.html`) dès l'achèvement de chaque cycle Fast-Lane ou Agency BI.
- [x] Ajout de la barre de pied de page fixe `.scan-footer` dans le modal de synchronisation garantissant la visibilité permanente des boutons de fermeture et de rechargement.
