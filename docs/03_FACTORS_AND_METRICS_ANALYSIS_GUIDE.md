# Module 3 : Guide Analytique des Facteurs de Données
## Décryptage Métier & Valeur Commerciale de Chaque Indicateur du Projet (FAO × SITG)

---

## 📊 Tableau Synthétique des Facteurs & Valeur Métier

| Catégorie | Facteur Clé | Source Donnée | Impact Stratégique pour l'Agence | Potentiel de Revenu |
| :--- | :--- | :--- | :--- | :--- |
| **Légal / Source** | `source_category` | FAO (LaCC vs LDTR) | Distingue les ventes libres des appartements protégés avec prix réels déclarés. | ★★★★☆ |
| **Transaction** | `transaction_type` | FAO (Vente / Succession / Partage) | Déclencheur fondamental : isole les successions avant mise sur le marché. | ★★★★★ |
| **Acteurs** | `seller` & `buyer` | FAO (Noms des parties) | Détecte les hoiries, investisseurs institutionnels et acheteurs réguliers. | ★★★★★ |
| **Prix** | `price_chf` | FAO (LDTR / Extraits) | Établit la vérité des prix notariés opposables aux prix d'affichage portails. | ★★★★★ |
| **Scoring** | `mandate_score` | Algorithme CYTRIA | Priorise les 5% de dossiers ayant la plus forte probabilité de mise en vente. | ★★★★★ |
| **Urbanisme** | `zone_code` (Zone 5) | SITG (`SIT_ZONE_AMENAG`) | Isole les villas à potentiel de valorisation résidentielle et densification. | ★★★★★ |
| **Potentiel** | `dev_score` | Algorithme CYTRIA | Détecte les parcelles pour montage d'opérations d'assemblage promoteurs. | ★★★★★ |
| **Planification** | `plq_number` | SITG (`RDPPF_PLQ`) | Accès direct aux droits à bâtir officiels pour calculer la surcharge foncière. | ★★★★☆ |
| **Bâtiment** | `building_period` | SITG (`CAD_BATIMENT_HORSOL`) | Cible les passoires énergétiques des années 1960–1975 nécessitant arbitrage. | ★★★★☆ |
| **Permis** | `permit_number` | SITG (`CAD_BATI_PROJET`) | Anticipe l'arrivée de programmes neufs sur le secteur (concurrence directe). | ★★★☆☆ |

---

## 🔍 Analyse Détaillée Facteur par Facteur

---

### 1. `source_category` (Catégorie Légale de la Source)
- **Définition** : Identifie le fondement légal de la publication dans la FAO : soit `Registre_Foncier` (application de l'art. 157 LaCC), soit `LDTR_Appartement` (application de l'art. 39 LDTR).
- **Méthode d'extraction** : Classifié par regex dans `pdf_parser.py` selon les sections officielles de la FAO.
- **Signification Métier pour l'Agence** :
  - `LDTR_Appartement` : **Une mine d'or statistique.** À Genève, la LDTR oblige à publier le **montant exact de la transaction en francs suisses**. Cela permet à l'agence de cartographier la véritable cote au m² de la PPE par quartier, sans le biais des annonces surévaluées.
  - `Registre_Foncier` : Concerne les biens-fonds, villas et immeubles. Le prix n'est pas systématiquement publié s'il s'agit d'une mutation à titre gratuit (succession, donation), ce qui indique une transmission patrimoniale imminente.

---

### 2. `transaction_type` (Nature de la Mutation)
- **Définition** : La nature juridique du transfert de propriété : `Vente`, `Héritage / Succession`, `Partage successoral`, `Donation`, `Cession de droits`.
- **Méthode d'extraction** : Détection lexicale dans le bloc d'avis (`"dévolu par succession"`, `"par suite de partage"`, `"vente immobilière"`).
- **Signification Métier pour l'Agence** :
  - **`Héritage / Partage`** : C'est le signal d'alarme le plus rentable pour un courtier. Un héritage n'est pas un choix d'investissement, c'est un événement de vie. Les héritiers ont souvent besoin de vendre dans les 6 à 18 mois pour payer les soultes ou les impôts successoraux.
  - **`Vente`** : Permet de mettre à jour la base des nouveaux acquéreurs (nouveaux résidents à fort pouvoir d'achat).
  - **`Donation`** : Signal d'un démembrement ou d'une restructuration familiale ; opportunité de conseil fiscal et patrimonial.

---

### 3. `seller` & `buyer` (Aliénateur & Acquéreur)
- **Définition** : Identité des personnes physiques ou morales cédant ou recevant le bien.
- **Méthode d'extraction** : Parsing syntaxique des clauses `"Anc. : Nom Prénom"` et `"Nouv. : Nom Prénom"`.
- **Signification Métier pour l'Agence** :
  - **Détection des Hoiries** : Si l'acheteur ou le vendeur contient `"Hoirie de Feu..."`, `"Consorts..."`, ou plus de 3 noms de famille différents pour un même bien, il s'agit d'une indivision.
  - **Détection des Promoteurs & Marchands de Biens** : Si l'acquéreur est une SA/Sàrl (ex: `"Capvest Real Estate SA"`, `"Comptoir Investissements"`, `"Swissroc Development"`), cela indique un rachat foncier stratégique. L'agence peut immédiatement étudier les parcelles voisines pour monter un contre-projet ou un assemblage.
  - **Fichier de Vendeurs Qualifiés** : Conserver l'identité des aliénateurs permet de savoir qui détient désormais d'importantes liquidités à réinvestir (*cash out* à réallouer en PPE de rendement).

---

### 4. `price_raw` & `price_chf` (Prix Déclaré)
- **Définition** : Montant financier de la transaction consigné dans l'acte notarié.
- **Méthode d'extraction** : Extraction regex des montants numériques (`"CHF 3'450'000.-"` $\rightarrow$ `3450000.0`).
- **Signification Métier pour l'Agence** :
  - **L'arme absolue de négociation** : Élimine le "bruit" des portails. Le courtier peut montrer au propriétaire d'un appartement qu'un lot strictement identique au 3e étage s'est vendu CHF 1'450'000 il y a 4 mois, justifiant une estimation rigoureuse.
  - **Calcul de la décote de négociation** : En comparant le dernier prix affiché en ligne avec le prix notarié final, l'agence calcule le taux de décote moyen par commune (généralement 4.5% à 7% à Genève).

---

### 5. `is_hoirie` & `mandate_score` (Indicateurs d'Opportunité Vendeur)
- **Définition** :
  - `is_hoirie` (Booléen) : Vrai si la transaction implique une indivision successorale.
  - `mandate_score` (0 à 100) : Score algorithmique CYTRIA combinant le type de transaction, le nombre d'héritiers, l'ancienneté du bâtiment et la typologie du bien.
- **Signification Métier pour l'Agence** :
  - **Filtrage Haute Priorité** : Un courtier indépendant ne peut pas prospecter 6'000 parcelles par an. Le `mandate_score` lui permet de concentrer son énergie commerciale sur les **50 dossiers les plus rentables du canton chaque mois**.
  - **Score $\ge 85$** : Villa individuelle issue d'une succession sans lien avec une régie désignée. Taux de conversion de premier contact estimé à **12%** contre 0.5% pour un boîtage anonyme.

---

### 6. `zone_code` & `zone_name` (Affectation Foncier SITG)
- **Définition** : Classement de la parcelle selon la loi générale sur les zones d'aménagement (Zone 1, 2, 3, 4, 5 ou Zone de développement).
- **Méthode d'extraction** : Intersection spatiale GIS entre les coordonnées centroïdes du bien et la couche SITG `SIT_ZONE_AMENAG`.
- **Signification Métier pour l'Agence** :
  - **`Zone 5 (Villas)`** : C'est le territoire roi du courtage genevois (Cologny, Vandœuvres, Conches, Veyrier, Troinex). Les honoraires moyens oscillent entre CHF 60'000 et CHF 250'000 par transaction.
  - **`Zone de Développement`** : Soumise à la LGZD. L'acquéreur promoteur doit respecter les prix de sortie contrôlés par l'État, ce qui plafonne le prix du terrain mais garantit un écoulement rapide des logements.

---

### 7. `surface_m2` & `surface_official_m2` (Emprise Parcellaire)
- **Définition** : Contenance cadastrale exacte de la parcelle en mètres carrés.
- **Méthode d'extraction** : Croisement officiel avec `CAD_PARCELLE_MENSU`.
- **Signification Métier pour l'Agence** :
  - **Le Seuil Critique des $1'200\text{ m}^2$ en Zone 5** : En dessous de $1'000\text{ m}^2$, une villa en Zone 5 reste un logement individuel. Au-delà de $1'200 - 1'500\text{ m}^2$, la parcelle devient éligible à l'art. 59 LCI : elle peut être scindée ou accueillir un projet de 2 à 4 villas contiguës.
  - La valeur du terrain ne se calcule plus "à la villa" mais **au potentiel constructible brut (m² de plancher)**, ce qui justifie une valorisation supérieure auprès d'un promoteur.

---

### 8. `building_period` & `building_year` (Époque & Année de Construction)
- **Définition** : Année d'érection du bâtiment principal selon le registre fédéral des bâtiments (RegBL / SITG `CAD_BATIMENT_HORSOL`).
- **Méthode d'extraction** : Jointure spatiale avec le centroïde du bâtiment principal.
- **Signification Métier pour l'Agence** :
  - **Bâtiments 1960–1980 (Passoires Thermiques & Rénovations Lourdes)** : Les propriétaires de villas construites entre 1960 et 1980 ont aujourd'hui entre 75 et 90 ans. Ces biens souffrent d'une obsolescence technique (chaudières mazout, isolation inexistante, amiante potentiel). Les coûts de rénovation (CHF 400'000 à CHF 1M) incitent très fortement les occupants seniors à vendre pour acheter un appartement moderne de plain-pied.

---

### 9. `plq_number`, `plq_name` & `plq_status` (Plan Localisé de Quartier)
- **Définition** : Présence d'un PLQ adopté ou en cours sur la parcelle (`RDPPF_PLQ`).
- **Méthode d'extraction** : Requête spatiale STRtree géométrique sur le cadastre SITG.
- **Signification Métier pour l'Agence** :
  - **Accélérateur de Valeur Foncier** : Une parcelle couverte par un PLQ adopté ne souffre plus d'incertitude juridique sur les gabarits autorisés. Le promoteur peut déposer son permis de construire immédiatement.
  - Le courtier peut télécharger directement le **plan et le règlement du PLQ** depuis l'application pour monter une plaquette d'investissement "clé en main".

---

### 10. `permit_number`, `permit_destination` & `permit_height` (Permis de Construire)
- **Définition** : Demandes d'autorisations préalables (APA) ou définitives (DD) déposées sur la parcelle (`CAD_BATI_PROJET`).
- **Méthode d'extraction** : Stratification spatiale des polygones de bâtiments projetés.
- **Signification Métier pour l'Agence** :
  - **Veille Concurrentielle Amont** : Détecte si un propriétaire a déjà mandaté un architecte pour valoriser sa parcelle.
  - **Détection des Ventes sous Condition de Permis** : Les promoteurs signent souvent une promesse de vente sous condition suspensive de l'obtention du permis de construire. Le suivi de l'avancement du permis permet au courtier de savoir exactement quand l'opération deviendra définitive.
