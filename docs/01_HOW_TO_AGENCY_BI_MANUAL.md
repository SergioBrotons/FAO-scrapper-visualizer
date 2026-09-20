# Module 1 : Manuel Pratique d'Intelligence d'Affaires Immobilières
## Guide d'Utilisation Métier pour Agences, Courtiers & Développeurs Fonciers (Genève)

---

## 🧭 Introduction : Pourquoi ce Système Change la Règle du Jeu à Genève

Dans le canton de Genève, le courtage immobilier traditionnel souffre d'un handicap structurel : **le manque de transparence**.
- Les portails immobiliers publics (Homegate, ImmoScout24, Immobilier.ch) ne publient que des **prix de mise en vente** (qui intègrent souvent une surcote de 5 à 15% ou des baisses masquées).
- Dès qu'un bien est visible en ligne, il est déjà sous contrat avec une agence concurrente.
- Les transactions notariées réelles sont consignées au Registre Foncier et publiées dans la **Feuille d'Avis Officielle (FAO)**, mais sous forme d'avis juridiques complexes, non géolocalisés et difficiles à décrypter à l'œil nu.

Ce système transforme ces avis bruts en **Business Intelligence active** grâce à la fusion avec le **SITG (Système d'Information du Territoire à Genève)**. Il dote l'agence d'une longueur d'avance en transformant chaque publication légale en opportunité de mandat, d'assemblage foncier ou d'arbitrage.

---

## 📅 La Routine Matinale du Courtier d'Élite (Workflow Quotidien)

| Horaire | Action dans l'Outil | Objectif Commercial |
| :--- | :--- | :--- |
| **08h30** | Ouvrir le système en mode **`MANDATES` (Radar Mandats)** | Filtrer les publications FAO de la veille avec un score $\ge 70$. |
| **08h45** | Isoler les **Hoiries & Successions** récentes | Identifier les héritiers d'un bien situé sur son secteur d'attribution. |
| **09h15** | Ouvrir le mode **`DEVELOPMENT` (Radar Développeurs)** | Repérer les mutations en **Zone 5** sur des parcelles $> 1'200\text{ m}^2$ ou sous **PLQ**. |
| **10h00** | Lancer les courriers d'approche ou appels qualifiés | Contacter les parties prenantes avec un dossier d'estimation préalable. |
| **14h00** | Préparation de rendez-vous vendeur en mode **`MARKET`** | Extraire les transactions réelles notariées de la rue pour fixer le juste prix. |

---

## 🎯 Workflow 1 : La Chasse aux Mandats Successoraux (Radar Hoiries & Partages)

### Le Constat Métier
En Suisse, la transmission successorale est le **déclencheur n°1 de vente immobilière non planifiée**. 
Lorsqu'un propriétaire décède, le bien passe en **hoirie** (propriété commune entre plusieurs héritiers : enfants, conjoint survivant, neveux). Dans 82% des cas à Genève :
- Les héritiers ne souhaitent ou ne peuvent pas habiter ensemble le bien.
- L'un des héritiers a besoin de liquidités pour racheter les parts ou régler les droits de succession.
- Le bien nécessite d'importants travaux de rénovation énergétique (bâtiments des années 1960–1980).
- **Conséquence inéluctable : le bien sera vendu.**

### Comment utiliser l'outil :
1. Cliquez sur le mode **`MANDATES`** dans la barre supérieure.
2. Cochez le filtre **`Hoiries & Successions uniquement`**.
3. Observez la liste triée par **`Mandate Propensity Score`** (0 à 100) :
   - **Score $\ge 85$ (Ultra-Chaud)** : Mutation portant sur un bien-fonds individuel (villa) où l'acquéreur est expressément noté comme *"Hoirie de Feu X"* ou *"Partage successoral"*, avec une maison construite avant 1985.
   - **Score $70 - 84$ (Chaud)** : Cession de parts de PPE entre membres d'une même famille ou acquisition suite à dévolution légale.
4. Cliquez sur le marqueur sur la carte :
   - Le système affiche l'adresse exacte, la parcelle cadastrale SITG, la surface de la parcelle, l'année de construction du bâtiment et les noms des héritiers requérants.
5. **Action Immédiate** :
   - Générer une fiche de synthèse cadastrale.
   - Envoyer le **Courrier d'Approche Successorale Neutre & Conseil** (voir [Module 4](file:///c:/Users/AI-Mini-PC/DEV/Real-state-agencies-intelligence/docs/FAO_BI_GUIDE/04_STRATEGIC_PLAYBOOK_SCRIPTS_FAQ.md)).

---

## 🏗 Workflow 2 : L'Assemblage Foncier & Surcharge Développeur (Radar Zone 5 & PLQ)

### Le Constat Métier
À Genève, le sol constructible est une denrée rarissime. La loi sur les constructions (LCI) et la politique cantonale favorisent la **densification de la Zone 5** (villas) et la mise en œuvre des **Plans Localisés de Quartier (PLQ)**.
Un courtier qui vend une villa traditionnelle touche 2 à 3% sur 3 millions de CHF (~CHF 75'000).
Un courtier qui vend une **parcelle à un promoteur pour créer 6 logements PPE** valorise le terrain sur sa valeur résiduelle constructible et génère un double mandat :
1. Honoraires sur la vente du terrain au promoteur (~CHF 120'000).
2. Contrat d'exclusivité de pilotage commercial pour la vente des 6 appartements neufs (~CHF 180'000).
**Total : CHF 300'000 de commissions sur une seule opportunité.**

### Comment utiliser l'outil :
1. Cliquez sur le mode **`DEVELOPMENT`**.
2. Activez le sous-filtre :
   - **`Densification Zone 5`** : Identifie les mutations de villas sur parcelles $> 1'200\text{ m}^2$ (seuil critique pour division parcellaire ou projet de villas contiguës/habitat groupé selon l'art. 59 LCI).
   - **`Périmètre PLQ / Zone de Dév.`** : Affiche les parcelles situées à l'intérieur d'un Plan Localisé de Quartier adopté ou en voie d'adoption (ex: Bernex, Chêne-Bourg, Grand-Saconnex).
   - **`Permis de Construire Actifs`** : Détecte les parcelles ayant fait l'objet d'une demande de permis (APA - Autorisation Préalable ou DD - Définitive) issue du flux `CAD_BATI_PROJET`.
3. Cliquez sur la parcelle pour inspecter :
   - Le lien direct vers le **Plan SITG officiel**.
   - Le lien vers le **règlement du PLQ** (gabarits autorisés, surface brute de plancher constructible).
   - L'historique des mutations récentes sur les parcelles voisines.
4. **Action Commerciale** :
   - Vérifier si les parcelles adjacentes appartiennent à des propriétaires âgés (effet d'assemblage parcellaire).
   - Proposer une étude de faisabilité préliminaire à un promoteur partenaire (Capvest, Swissroc, m3, EDIFEA, Comptoir Promotion).

---

## ⚖️ Workflow 3 : L'Avis de Valeur Imparable (Calibration Prix Notariés vs Portails)

### Le Constat Métier
Le principal obstacle du courtier lors d'un "pitch" vendeur est le **prix d'affichage fantaisiste** :
- Le vendeur consulte les portails (Homegate, ImmoScout) et voit que son voisin affiche sa villa à CHF 4.2M.
- En réalité, cette villa est en ligne depuis 9 mois, a subi deux baisses de prix secrètes, et finira par se vendre chez le notaire à CHF 3.5M.
- Si le courtier accepte le mandat au prix espéré par le vendeur (CHF 4.2M), le mandat "brûle", le bien ne se vend pas, et l'agence perd de l'argent en marketing.

### Comment utiliser l'outil :
1. Ouvrez le mode **`MARKET`**.
2. Zoomez sur la rue ou le micro-quartier du bien à estimer (ex: *Chemin de Planta, Cologny* ou *Avenue Eugène-Pittard, Champel*).
3. Consultez l'historique des **prix réels notariés publiés dans la FAO** :
   - Filtrer par nature : `Appartement PPE`, `Bien-fonds (Villa)`, `Immeuble de rapport`.
   - Comparer le prix payé ($CHF/m^2$ habitable ou de terrain) sur les 24 derniers mois.
4. Présentez au vendeur la **vérité officielle du Registre Foncier** :
   > *"Monsieur le Vendeur, voici l'extrait officiel des 5 dernières ventes notariées dans votre rue exacte au cours des 18 derniers mois. Le prix moyen effectif signé chez le notaire est de CHF 14'200/m², et non de CHF 17'000/m² comme l'espérait l'annonce du voisin qui ne trouve pas preneur depuis un an. Si nous positionnons votre bien à CHF 14'800/m² avec notre stratégie de mise en valeur, nous déclencherons 3 offres en moins de 45 jours."*
5. **Résultat** : Crédibilité technique absolue, mandat exclusif signé au juste prix de marché.

---

## 📍 Workflow 4 : Le Farming Territorial & Détection d'Angles Morts

### Le Constat Métier
Un bon courtier ne s'éparpille pas sur tout le canton ; il **domine un territoire** (un quartier, une commune, un plateau résidentiel).
Pour dominer un secteur, il doit connaître :
- Le taux de rotation annuel des parcelles.
- L'âge moyen des propriétaires.
- Les investisseurs institutionnels détenant des immeubles en copropriété.

### Comment utiliser l'outil :
1. Dans le sélecteur de commune, choisissez votre territoire prioritaire (ex: *Vandœuvres*, *Collonge-Bellerive*, *Carouge*).
2. Utilisez l'outil de mesure pour analyser le volume annuel des transactions :
   - Nombre total de mutations notariées par an.
   - Volume total en millions de CHF.
   - Répartition PPE vs Villas individuelles.
3. Comparez avec le module **`Cartographie des Agences`** :
   - Identifiez quelles agences concurrentes ont leur siège ou leur rayon d'action officiel sur ce périmètre.
   - Si une commune comme *Hermance* ou *Russin* génère 25 ventes par an mais qu'aucune agence n'y détient plus de 15% de part de marché, il s'agit d'un **angle mort stratégique** idéal pour une offensive de prospection ciblée.

---

## 🏆 Workflow 5 : Veille Concurrentielle & Contre-Attribution

### Comment utiliser l'outil :
1. Ouvrez le panneau **`Agences & League Table`**.
2. Filtrez par agence concurrente (ex: *BARNES*, *Cardis Sotheby's*, *SPG One*, *Naef*).
3. Visualisez son **rayon territorial d'intervention** et les parcelles qu'elle a historiquement négociées.
4. Croisez avec le module Multi-Portails :
   - Repérez les biens qu'un concurrent a en mandat depuis plus de 90 jours (signe d'usure du mandat).
   - Préparez un dossier de reprise de mandat dès l'expiration de la clause d'exclusivité du concurrent.
