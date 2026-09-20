# Module 2 : Glossaire Juridique, Cadastral & Foncier Genevois
## Dictionnaire Exhaustif de Référence pour Professionnels de l'Immobilier

---

## 🏛 1. Institutions, Publications & Sources Officielles

### FAO (Feuille d'Avis Officielle de la République et Canton de Genève)
Journal officiel cantonal fondé au XVIIIe siècle, publié par la Chancellerie d'État. C'est l'organe légal dans lequel sont obligatoirement publiées les mutations immobilières (ventes, successions, donations), les enquêtes publiques de permis de construire, les avis de faillite et les avis successoraux.
- *Lien métier* : La source primaire de vérité du projet CYTRIA.

### Registre Foncier (RF / Grundbuch)
Service étatique rattaché au Département des institutions et du numérique (DIN). Il a la charge d'enregistrer tous les droits réels relatifs aux immeubles : propriété, servitudes, charges foncières, hypothèques (cédule hypothécaire). 
- Le principe de la foi publique du registre foncier (art. 9 ZGB / CC) garantit que toute personne inscrite est présumée propriétaire légitime.

### Notariat Latin Genevois
Genève applique le système du notariat de type latin. Le notaire est un officier public indépendant, délégataire de la puissance publique. Tout transfert immobilier (vente d'immeuble, constitution de PPE, démembrement) nécessite obligatoirement un acte notarié authentique (art. 216 CO).

### SITG (Système d'Information du Territoire à Genève)
Système d'information géographique (SIG) cantonal réunissant les données foncières, topographiques, géologiques, réglementaires et environnementales de l'État de Genève, des 45 communes genevoises et des régies publiques (SIG, TPG).
- *Lien technique* : Les couches vectorielles utilisées par le pipeline (`CAD_PARCELLE_MENSU`, `CAD_BATIMENT_HORSOL`, `RDPPF_PLQ`, `SIT_ZONE_AMENAG`) proviennent de l'API ArcGIS REST du SITG.

---

## 📜 2. Lois Cantonales & Fédérales Clés

### LaCC (Loi d'application du Code civil suisse et d'autres lois fédérales en matière de droit civil - art. 157)
Base légale cantonale genevoise qui impose la publication hebdomadaire dans la FAO des acquisitions d'immeubles inscrites au Registre Foncier.
- **Article 157** : Stipule que la publication doit mentionner la commune, la désignation cadastrale, la nature de l'immeuble, le nom de l'aliénateur (vendeur) et de l'acquéreur (acheteur).

### LDTR (Loi sur les démolitions, transformations et rénovations d'immeubles d'habitation)
Loi d'ordre public genevoise très stricte protégeant le parc de logements locatifs.
- **Article 39 LDTR (Aliénation d'appartements)** : Toute vente d'un appartement loué ou ayant été loué au cours des trois dernières années est soumise à une autorisation d'aliénation préalable délivrée par le département. Les transactions sous LDTR sont publiées dans la FAO avec mention explicite du **prix exact en francs suisses**, créant un observatoire transparent des prix de la PPE.

### LGZD (Loi générale sur les zones de développement)
Loi régissant les terrains déclassés en "Zone de développement". À Genève, ces zones imposent des plafonds de prix de vente des terrains et des logements neufs (contrôle étatique des prix pendant 10 ans pour le logement d'utilité publique - LUP, ou le logement locatif - HM).
- *Lien métier* : Les parcelles situées en zone de développement sont soumises à un contrôle étatique, mais offrent des volumes colossaux pour les promoteurs.

### LDFR (Loi fédérale sur le droit foncier rural)
Loi fédérale protégeant les terres et entreprises agricoles. L'acquisition d'une parcelle agricole (située hors zone à bâtir, en zone agricole) nécessite d'être "exploitant à titre personnel" ou de bénéficier d'une dérogation de la Commission foncière agricole. Empêche la spéculation foncière sur les domaines viticoles et agricoles du Mandement et de la Champagne.

### LCI (Loi sur les constructions et les installations diverses)
Régit l'ensemble des règles de bâtir à Genève (hauteurs, gabarits, distances aux limites, coefficient d'utilisation du sol).
- **Article 59 al. 4 LCI (Densification en Zone 5)** : Permet, sous certaines conditions strictes de qualité architecturale et d'intégration paysagère, de construire des gabarits plus denses (villas contiguës ou petits immeubles) sur des parcelles individuelles de villas traditionnelles.

---

## 📐 3. Typologies Foncières & Entités Cadastrales

### Bien-fonds (BF)
Immeuble traditionnel au sens de l'art. 655 CC : une parcelle de terrain nettement délimitée dans l'espace avec tout ce qui y est incorporé (bâtiments, arbres, sources).

### PPE (Propriété Par Étage)
Forme particulière de copropriété (art. 712a ss CC) conférant au copropriétaire le droit exclusif d'utiliser et d'aménager des parties déterminées d'un bâtiment (appartement, cave, place de parking intérieure).
- Chaque lot de PPE possède son propre feuillet au Registre Foncier et son numéro de lot (ex: `6089-104`).

### DDP (Droit Distinct et Permanent de superficie - art. 675 / 779 CC)
Droit réel conférant à son titulaire la faculté d'avoir ou de maintenir une construction sur le fonds d'autrui pour une durée minimale de 30 ans et maximale de 100 ans.
- Très fréquent à Genève sur les terrains appartenant à la Ville de Genève, à l'État ou à des fondations d'utilité publique (ex: FIPOI pour les organisations internationales).

### Copropriété Ordinaire (COP)
Propriété collective où chaque copropriétaire détient une quote-part idéale du bien sans jouissance exclusive garantie d'une partie précise (souvent utilisé pour des parcelles de voirie privée, des allées communes ou des cours).

### EGRID (Eidgenössischer Grundstücksidentifikator)
Identifiant fédéral unique d'immeuble attribué à chaque parcelle en Suisse (format: `CH` suivi de 12 caractères alphanumériques). Il permet d'interroger directement les registres nationaux et les bases de données géodésiques fédérales.

---

## 🗺 4. Aménagement du Territoire & Régimes de Zones (Genève)

| Zone d'Affectation | Dénomination | Densité & Gabarit Type | Opportunité Agence |
| :--- | :--- | :--- | :--- |
| **Zone 1** | Cité & Hyper-Centre Ancien | Bâtiments d'époque continus, 6 à 8 niveaux | Arbitrages d'immeubles de rapport, appartements de maître, penthouses de luxe. |
| **Zone 2** | Urbaine Dense | Immeubles locatifs et PPE urbains, 5 à 7 niveaux | Transactions de blocs PPE, surélévations de toitures. |
| **Zone 3** | Moyenne Densité | Quartiers résidentiels mixtes (Champel, Petit-Saconnex) | Rénovation d'appartements familiaux, vente en bloc. |
| **Zone 4** | Périphérique / Transition | Faubourgs et couronnes urbaines | Opérations de densification urbaine, commerces de proximité. |
| **Zone 5** | Résidentielle / Villas | Maisons individuelles, $IUS \approx 0.20$ à $0.25$ | **Le cœur du courtage résidentiel haut de gamme** et potentiel d'assemblage densification. |
| **Zone Agricole** | Zone Foraine protégée | Inconstructible sauf affectation agricole | Domaines de maître avec statut patrimonial hors LDFR. |

### PLQ (Plan Localisé de Quartier)
Instrument d'urbanisme d'échelle locale définissant l'implantation exacte des constructions, les hauteurs, les accès et les espaces publics d'un secteur à développer.
- Un terrain soumis à un PLQ adopté prend instantanément une **surcharge de valeur foncière**, car les droits à bâtir y sont garantis.

### Droits de Préemption Communaux & Cantonaux
Prérogative légale permettant à la commune ou au canton de se substituer à l'acquéreur privé au prix convenu dans l'acte notarié :
- Droit de préemption en zone de développement (LGZD).
- Droit de préemption communal pour la création d'équipements publics ou de logements d'utilité publique.
- Droit de préemption dans les périmètres du PAV (Praille Acacias Vernets).

---

## 👨‍👩‍👧‍👦 5. Vocabulaire Successoral & Notarié

### Hoirie (Erbengemeinschaft)
Communauté héréditaire formée de plein droit par tous les héritiers d'un défunt dès l'ouverture de la succession (art. 602 CC). Les membres de l'hoirie sont propriétaires en main commune (*Gesamteigentum*) : **aucune décision de vente ou de gestion ne peut être prise sans l'unanimité absolue de tous les héritiers**.
- *Valeur métier* : L'exigence de l'unanimité crée fréquemment des blocages qui nécessitent l'intervention d'un courtier expérimenté capable de jouer le rôle de médiateur neutre.

### Partage Successoral
Acte juridique par lequel les héritiers mettent fin à l'indivision de l'hoirie en attribuant les biens de la succession à l'un d'entre eux ou en décidant de vendre le bien à un tiers pour se partager le produit net de la vente.

### Aliénateur
Terme juridique désignant la personne physique ou morale qui transfère la propriété de l'immeuble (le vendeur, le donateur, le cédant).

### Acquéreur
La personne physique ou morale qui reçoit la propriété de l'immeuble (l'acheteur, le donataire, l'héritier).

### Démembrement de Propriété (Usufruit & Nue-Propriété)
Séparation des prérogatives de la propriété (art. 745 CC) :
- **Nue-propriété** : Droit de disposer de la chose (vendre le fond).
- **Usufruit** : Droit d'utiliser la chose et d'en percevoir les fruits (habiter ou percevoir les loyers).
- Très fréquent dans les donations intrafamiliales : les parents donnent la nue-propriété aux enfants tout en conservant l'usufruit jusqu'à leur décès.

---

## 🏗 6. Autorisations de Construire & Codes Procédures (SAD / SAPA)

- **APA (Autorisation Préalable d'Aménager / de Construire)** : Décision préalable de principe de l'État sur la faisabilité d'un projet d'envergure. Très bon indicateur qu'un terrain est en cours de développement.
- **DD (Demande Définitive)** : Procédure ordinaire complète avec publication dans la FAO pour l'obtention du permis de construire exécutoire.
- **M (Procédure Accélérée)** : Procédure allégée pour transformations intérieures, extensions mineures ou piscines ne modifiant pas l'aspect extérieur de manière prépondérante.
- **SAD / SAPA** : Système d'Affichage des Données de l'urbanisme genevois permettant de consulter les plans, coupes, avis d'experts et oppositions d'un dossier de permis.
