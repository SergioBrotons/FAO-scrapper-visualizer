# Module 1 : Manuel Pratique d'Intelligence d'Affaires Immobilières
## Guide d'Utilisation Métier pour Agences, Courtiers & Développeurs Fonciers (Genève)

---

## 1. Introduction : Pourquoi ce Système Change la Règle du Jeu à Genève

Dans le canton de Genève, le courtage immobilier traditionnel souffre d'un handicap structurel : **le manque de transparence**.
- Les portails immobiliers publics (Homegate, ImmoScout24, Immobilier.ch) ne publient que des **prix de mise en vente** (qui intègrent souvent une surcote de 5 à 15% ou des baisses masquées).
- Dès qu'un bien est visible en ligne, il est déjà sous contrat avec une agence concurrente.
- Les transactions notariées réelles sont consignées au Registre Foncier et publiées dans la **Feuille d'Avis Officielle (FAO)**, mais sous forme d'avis juridiques complexes, non géolocalisés et difficiles à décrypter à l'œil nu.

Ce système transforme ces avis bruts en **Business Intelligence active** grâce à la fusion avec le **SITG (Système d'Information du Territoire à Genève)**. Il dote l'agence d'une longueur d'avance en transformant chaque publication légale en opportunité de mandat, d'assemblage foncier ou d'arbitrage.

---

## 2. La Routine Matinale du Courtier d'Élite (Workflow Quotidien)

| Horaire | Action dans l'Outil | Objectif Commercial |
| :--- | :--- | :--- |
| **08h30** | Ouvrir le système en mode **CYTRIA SOURCING — Mandats Vendeurs B2C** | Filtrer les publications FAO de la veille avec un score >= 70. |
| **08h45** | Isoler les **Hoiries & Successions** récentes | Identifier les héritiers d'un bien situé sur son secteur d'attribution. |
| **09h15** | Ouvrir le mode **CYTRIA SOURCING — Radar Promotion B2B** | Repérer les mutations en **Zone 5** sur des parcelles > 1'200 m² ou sous **PLQ**. |
| **10h00** | Lancer les courriers d'approche ou appels qualifiés | Contacter les parties prenantes avec un dossier d'estimation préalable. |
| **14h00** | Préparation de rendez-vous vendeur en mode **CYTRIA MARKET** | Lancer le simulateur CMA pour extraire les ventes notariées de la rue et du quartier. |

---

## 3. Workflow 1 : La Chasse aux Mandats Successoraux (Radar Hoiries & Partages)

### Le Constat Métier
En Suisse, la transmission successorale est le **déclencheur n°1 de vente immobilière non planifiée**. 
Lorsqu'un propriétaire décède, le bien passe en **hoirie** (propriété commune entre plusieurs héritiers : enfants, conjoint survivant, neveux). Dans 82% des cas à Genève :
- Les héritiers ne souhaitent ou ne peuvent pas habiter ensemble le bien.
- L'un des héritiers a besoin de liquidités pour racheter les parts ou régler les droits de succession.
- Le bien nécessite d'importants travaux de rénovation énergétique (bâtiments des années 1960–1980).
- **Conséquence inéluctable : le bien sera vendu.**

### Comment utiliser l'outil :
1. Cliquez sur le mode **CYTRIA SOURCING** puis sélectionnez **Mandats Vendeurs (B2C)**.
2. Cochez le filtre **Hoiries & Successions uniquement**.
3. Observez la liste triée par **Mandate Propensity Score** (0 à 100) :
   - **Score >= 85 (Ultra-Chaud)** : Mutation portant sur un bien-fonds individuel (villa) où l'acquéreur est expressément noté comme *"Hoirie de Feu X"* ou *"Partage successoral"*, avec une maison construite avant 1985.
   - **Score 70 - 84 (Chaud)** : Cession de parts de PPE entre membres d'une même famille ou acquisition suite à dévolution légale.
4. Cliquez sur le marqueur sur la carte :
   - Le système affiche l'adresse exacte, la parcelle cadastrale SITG, la surface de la parcelle, l'année de construction du bâtiment et les noms des héritiers requérants.
5. **Action Immédiate** :
   - Générer une fiche de synthèse cadastrale.
   - Envoyer le **Courrier d'Approche Successorale Neutre & Conseil** (voir Module 4).

---

## 4. Workflow 2 : L'Assemblage Foncier & Surcharge Développeur (Radar Zone 5 & PLQ)

### Le Constat Métier
À Genève, le sol constructible est une denrée rarissime. La loi sur les constructions (LCI) et la politique cantonale favorisent la **densification de la Zone 5** (villas) et la mise en œuvre des **Plans Localisés de Quartier (PLQ)**.
Un courtier qui vend une villa traditionnelle touche 2 à 3% sur 3 millions de CHF (~CHF 75'000).
Un courtier qui vend une **parcelle à un promoteur pour créer 6 logements PPE** valorise le terrain sur sa valeur résiduelle constructible et génère un double mandat :
1. Honoraires sur la vente du terrain au promoteur (~CHF 120'000).
2. Contrat d'exclusivité de pilotage commercial pour la vente des 6 appartements neufs (~CHF 180'000).
**Total : CHF 300'000 de commissions sur une seule opportunité.**

### Comment utiliser l'outil :
1. Cliquez sur le mode **CYTRIA SOURCING** puis sélectionnez **Radar Promotion (B2B)**.
2. Activez le sous-filtre :
   - **Densification Zone 5** : Identifie les mutations de villas sur parcelles > 1'200 m² (seuil critique pour division parcellaire ou projet de villas contiguës/habitat groupé selon l'art. 59 LCI).
   - **Périmètre PLQ / Zone de Dév.** : Affiche les parcelles situées à l'intérieur d'un Plan Localisé de Quartier adopté ou en voie d'adoption (ex: Bernex, Chêne-Bourg, Grand-Saconnex).
   - **Permis de Construire Actifs** : Détecte les parcelles ayant fait l'objet d'une demande de permis (APA - Autorisation Préalable ou DD - Définitive) issue du flux `CAD_BATI_PROJET`.
3. Cliquez sur la parcelle pour inspecter :
   - Le lien direct vers le **Plan SITG officiel**.
   - Le lien vers le **règlement du PLQ** (gabarits autorisés, surface brute de plancher constructible).
   - L'historique des mutations récentes sur les parcelles voisines.
4. **Action Commerciale** :
   - Vérifier si les parcelles adjacentes appartiennent à des propriétaires âgés (effet d'assemblage parcellaire).
   - Proposer une étude de faisabilité préliminaire à un promoteur partenaire (Capvest, Swissroc, m3, EDIFEA, Comptoir Promotion).

---

## 5. Workflow 3 : L'Avis de Valeur Imparable & Simulateur Micro-Quartier (CMA)

### Le Constat Métier
Le principal obstacle du courtier lors d'un "pitch" vendeur est le **prix d'affichage fantaisiste** :
- Le vendeur consulte les portails (Homegate, ImmoScout) et voit que son voisin affiche sa villa à CHF 4.2M.
- En réalité, cette villa est en ligne depuis 9 mois, a subi deux baisses de prix secrètes, et finira par se vendre chez le notaire à CHF 3.5M.
- Si le courtier accepte le mandat au prix espéré par le vendeur (CHF 4.2M), le mandat "brûle", le bien ne se vend pas, et l'agence perd de l'argent en marketing.

### Outils Opérationnels Disponibles dans CYTRIA MARKET :

#### A. Macro-Zonage Rive Gauche vs Rive Droite
- **Rive Gauche (70.8% des transactions)** : Polarise les communes à très haute valeur foncière (Cologny, Vandoeuvres, Collonge-Bellerive, Chêne-Bougeries) et les quartiers centraux les plus prisés (Champel, Florissant, Eaux-Vives). Prix médians PPE : CHF 13'500 – 18'000+/m².
- **Rive Droite (29.2% des transactions)** : Polarise le secteur international (Nations, Pregny-Chambésy, Grand-Saconnex), les pôles d'emploi aéroportuaires et les communes de Meyrin/Vernier. Prix médians PPE : CHF 10'500 – 13'500/m².
- **Usage** : Filtrer d'un clic pour recadrer l'univers de référence et calibrer la dynamique fiscale et d'attractivité territoriale.

#### B. Calque Prix / m² (Zones Iso-Valeur Notariées)
Activez le calque pour visualiser instantanément la segmentation officielle en 4 catégories :
- **Prestige (> 18'000 CHF/m²)** : Cologny, Conches, Vieille-Ville haute, quais Eaux-Vives.
- **Haut Standing (14'000 – 18'000 CHF/m²)** : Champel, Florissant, Malagnou, Chêne-Bougeries, Vésenaz.
- **Cœur de Marché (11'000 – 14'000 CHF/m²)** : Chêne-Bourg, Carouge, Servette, Petit-Saconnex, Plainpalais.
- **Entrée / Accessible (< 11'000 CHF/m²)** : Vernier, Meyrin, Onex, Lancy, Thônex périphérique.

#### C. Simulateur d'Avis de Valeur & Comparables (CMA)
> **Accès Direct Applicatif** : [Lancer le Simulateur CMA dans l'application Web](http://localhost:8080/index.html#cma) (ou `index.html?tool=cma&address=Chemin+du+Saut-du-Loup+18&surface=95&typology=PPE`)

Le moteur CMA permet d'évaluer n'importe quel immeuble ou appartement en croisant les actes notariés réels :
1. **Saisie du Bien Cible** : Entrez l'adresse (ex: *Chemin du Saut-du-Loup 18, 1225 Chêne-Bourg*), la surface habitable (ex: 95 m²) et la typologie.
2. **Détection des Ventes Directes & Contiguës** :
   - Le système identifie automatiquement les ventes conclues sur la même adresse ou les numéros voisins (ex: *Chemin du Saut-du-Loup 16*, vendu pour CHF 1'620'000 le 26 février 2026, ou mutations parcellaires au n° 22).
3. **Sélection du Rayon ou Périmètre Quartier** :
   - *100 m* : Périmètre immédiat / copropriété contiguë.
   - *250 m* : Voisinage direct (rayon recommandé pour les PPE urbaines).
   - *500 m* : Micro-quartier élargi.
   - *1'000 m* : Commune entière.
4. **Calcul Statistique Tri-Niveaux** :
   - Fourchette Basse (25e percentile).
   - Valeur Vénale Médiane Recommandée (médiane notariée FAO).
   - Fourchette Haute (75e percentile).
5. **Restitution Client** :
   - Bouton **Copier le Rapport d'Estimation** : Génère un mémo textuel prêt à insérer dans le dossier d'estimation.
   - Bouton **Tracer sur la Carte & Voir** : Dessine le cercle de prospection et met en lumière les transactions comparables.

---

## 6. Workflow 4 : Le Farming Territorial & Détection d'Angles Morts

### Le Constat Métier
Un bon courtier ne s'éparpille pas sur tout le canton ; il **domine un territoire** (un quartier, une commune, un plateau résidentiel).
Pour dominer un secteur, il doit connaître :
- Le taux de rotation annuel des parcelles.
- La part respective des successions et des ventes institutionnelles.
- L'emprise des agences concurrentes sur ce territoire précis.

### Comment utiliser l'outil :
1. Dans le sélecteur de commune, choisissez votre territoire prioritaire (ex: *Vandœuvres*, *Collonge-Bellerive*, *Carouge*).
2. Utilisez l'outil de mesure pour analyser le volume annuel des transactions :
   - Nombre total de mutations notariées par an.
   - Volume total en millions de CHF.
   - Répartition PPE vs Villas individuelles.
3. Comparez avec le module **CYTRIA AGENCY BI** :
   - Identifiez quelles agences concurrentes détiennent les mandats actifs sur ce périmètre.
   - Si une commune génère 25 ventes par an mais qu'aucune agence n'y détient plus de 15% de part de marché, il s'agit d'un **angle mort stratégique** idéal pour une offensive de prospection ciblée.

---

## 7. Workflow 5 : Veille Concurrentielle & Benchmark de Parts de Marché

### Comment utiliser l'outil :
1. Ouvrez le module **CYTRIA AGENCY BI** puis cliquez sur **Benchmark & Parts de Marché**.
2. Consultez la cartographie certifiée des **83 agences officielles du canton de Genève** (données Zefix / RC Genève, connectées dynamiquement à la base d'intelligence).
3. Analysez le portefeuille sous mandat et le **taux de conciliation notarié** (mandats délistés confirmés par une publication FAO ultérieure).
4. Croisez avec les données de délais de parution :
   - Repérez les biens en mandat depuis plus de 90 jours sans offre.
   - Préparez un dossier d'estimation comparative (CMA) pour solliciter le propriétaire lors de l'expiration de l'exclusivité du confrère.

---

## 8. Workflow 6 : CYTRIA EARLYSIGNALS — Détection Pré-Marché, Campagne Riverains & Connexion CRM

### Le Constat Métier
La meilleure façon de remporter un mandat exclusif à Genève n'est pas de participer à une mise en concurrence avec 4 confrères lorsque le bien est déjà sur les portails. C'est d'intervenir **avant le marché**, dès qu'une mutation successorale ou un arbitrage foncier se produit au Registre Foncier, avec une approche consultative ultra-qualifiée.

### Les 4 Piliers Opérationnels d'EarlySignals :

#### A. Le 4e Onglet Maître Produit & Sous-Barre Dédiée
- **Accès** : Cliquez sur l'onglet `EARLYSIGNALS` dans la barre supérieure.
- **Filtres Rapides** :
  - *Tous les signaux* : Vue panoramique des 4'346 opportunités qualifiées.
  - *Hoiries & Successions (CC 602)* : Isole les transmissions familiales.
  - *Densification & PLQ (Art. 59)* : Isole les parcelles à potentiel de bâtir additionnel.
  - *Arbitrage Foncier* : Filtre les terrains et immeubles sous-optimisés.
- **HUD Dynamique** : Affiche les métriques clés en temps réel (*Signaux Pré-Marché*, *Hoiries CC 602*, *Densif. Art. 59*, *Score >= 70*).

#### B. Le Dashboard Macro Radar (`#earlySignalsRadarModal`)
- **Accès** : Cliquez sur `Radar Pré-Marché (Table) ↗` dans la sous-barre ou dans la barre latérale.
- **Usage** :
  - Parcourez l'ensemble des opportunités cantonales classées par score décisionnel décroissant.
  - Utilisez le champ de recherche pour filtrer instantanément par commune, rue ou numéro de parcelle.
  - Consultez en un coup d'œil le lignage 3 tiers : Fait Public (date FAO), Indice Dérivé (distance et prix de la vente contiguë) et Signal Décisionnel.
  - Déclenchez directement les actions : `Carte`, `Fiche` (dossier d'aide à la décision 3-tiers), `Campagne` ou `➔ CRM`.

#### C. Le Générateur de Campagne Riverains en Lot (`#batchCampaignModal`)
- **Accès** : Cliquez sur `Campagne Riverains en Lot ↗` depuis la sous-barre, la table Radar ou la fiche conseil.
- **Usage** :
  - L'outil scanne automatiquement toutes les parcelles riveraines dans un rayon de 150 m à 600 m autour de l'acte notarié de référence.
  - Cochez ou décochez les riverains cibles dans la liste de gauche (avec affichage de la distance exacte au mètre près).
  - Prévisualisez en direct dans le panneau de droite la lettre personnalisée adressée aux ayants droit, mentionnant l'impact de la transaction contiguë.
  - Exportez en un clic : `Copier Tous les Courriers (Pack)` pour publipostage ou `Télécharger Pack Campagne (.json)`.

#### D. Le Connecteur CRM Webhook Direct (`#crmSettingsModal`)
- **Accès** : Cliquez sur `Connecteur CRM Webhook ⚙`.
- **Usage** :
  - Renseignez l'URL de votre endpoint Webhook (HubSpot, Salesforce, Whise, Apimo, Zapier, Make) et vos clés d'autorisation éventuelles.
  - Sauvegardez dans votre navigateur local.
  - Dès qu'une opportunité est qualifiée, cliquez sur `Transmettre au CRM (Webhook Direct ➔)` depuis le tiroir latéral ou le Radar pour créer la fiche prospect et la tâche commerciale sans quitter la carte.

