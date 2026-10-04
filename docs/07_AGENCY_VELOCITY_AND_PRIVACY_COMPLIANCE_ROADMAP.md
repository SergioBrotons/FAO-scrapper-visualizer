# Module 7 : Cadre Stratégique — Vélocité des Ventes, Corrélation Portails & Conformité LPD

> **Statut :** Document d'Architecture & Roadmap Produit (R&D)  
> **Version :** 1.0 — Octobre 2026  
> **Auteurs :** Équipe d'Architecture Cytria Intelligence

---

## 1. Synthèse Exécutive & Enjeux Métier

L'évaluation des agences immobilières genevoises repose traditionnellement sur deux métriques statiques : le volume brut d'actes passés et les parts de marché territoriales. Bien qu'essentielles, ces données ne capturent pas le dynamisme opérationnel : **à quelle vitesse une agence transforme-t-elle ses mandats en actes authentiques ?**

Ce document structure deux axes majeurs de la roadmap Cytria :
1. **L'Ingénierie de la Vélocité des Ventes (Agency Sales Velocity Framework)** :
   * Mesurer le rythme transactionnel à court terme ($Q_0$ vs $Q_{-1}$, récence du dernier acte, flux de liquidités).
   * Concevoir l'algorithme de corrélation **Portails $\to$ Acte Notarié** pour reconstituer le véritable délai de commercialisation (*Days on Market* — DOM).
2. **Le Blindage Légal & Masquage de Conformité (Privacy & Outworld Compliance Engine)** :
   * Aligner l'application sur la nouvelle Loi fédérale sur la protection des données (**nLPD / FADP**) et les réformes de l'art. 970a CC.
   * Masquer les données nominatives des personnes physiques dans l'interface visuelle tout en conservant les données brutes dans le coffre-fort SQLite privé.
   * Remplacer l'affichage public du PII par des passerelles de redirection vers les registres officiels de l'État (*Deep-Links ORF / SITG*).

---

## 2. Métriques Standards de Vélocité dans l'Industrie Immobilière

Dans l'analyse institutionnelle (Wüest Partner, IAZI/CIFI, SVIT, US National Association of Realtors), la vélocité est la mesure du temps et du débit nécessaire à l'absorption d'un actif.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        STANDARDS DE VÉLOCITÉ IMMOBILIÈRE                               │
├─────────────────────────┬───────────────────────────┬──────────────────────────────────┤
│ Indicateur Standard     │ Définition Théorique      │ Disponibilité en Données Pures   │
├─────────────────────────┼───────────────────────────┼──────────────────────────────────┤
│ 1. Days on Market (DOM) │ Nb de jours entre 1ère    │ NÉCESSITE LE LIEN PORTAILS ➔ FAO │
│                         │ publication et signature  │ (Délai d'absorption réel)        │
├─────────────────────────┼───────────────────────────┼──────────────────────────────────┤
│ 2. Sales Momentum       │ Ratio d'accélération      │ 100% DISPONIBLE EN OPEN DATA     │
│    ($\Delta$ Trimestriel)│ (3 derniers mois vs P-3M) │ (Fréquence des avis FAO)         │
├─────────────────────────┼───────────────────────────┼──────────────────────────────────┤
│ 3. Recency / Inactivity │ Jours écoulés depuis le   │ 100% DISPONIBLE EN OPEN DATA     │
│    (DSLS)               │ dernier acte notarié      │ (Horodatage des publications)    │
├─────────────────────────┼───────────────────────────┼──────────────────────────────────┤
│ 4. Débit par Courtier   │ Actes par négociateur / an│ 100% DISPONIBLE (RC × FAO)       │
│    (Productivity Pace)  │ Efficience par tête       │ (83 agences × 93 courtiers)      │
├─────────────────────────┼───────────────────────────┼──────────────────────────────────┤
│ 5. Décompte d'Absorption│ Taux de rotation du stock │ NÉCESSITE LE SCRAPING CONTINU    │
│    (Inventory Turnover) │ Délistages / Mandats totaux│ DU STOCK ACTIF                   │
└─────────────────────────┴───────────────────────────┴──────────────────────────────────┘
```

---

## 3. Ce Que Nous Pouvons Calculer Immédiatement avec l'Open Data Public

Sans dépendre d'un historique de portails privés, Cytria dispose de **8'970 actes notariés horodatés**. Nous pouvons immédiatement construire un **Indice de Vélocité Cytria (CVI — Cytria Velocity Index)** :

### A. Le Momentum Trimestriel ($\Delta \text{Velocity}$)
Mesure si une agence accélère ou subit un ralentissement dans le closing de ses ventes :

$$\text{Momentum}_{\text{T3M}} = \frac{\text{Volume}(\text{Derniers 90 jours}) - \text{Volume}(\text{J-91 à J-180})}{\text{Volume}(\text{J-91 à J-180}) + \epsilon} \times 100$$

* **Interprétation Métier** :
  * **$\Delta > +20\%$ (Accélération Forte — Vert)** : Agence en plein essor commercial, captant activement les mandats du trimestre.
  * **$-10\% \le \Delta \le +10\%$ (Rythme Stable — Doré)** : Production régulière, régie établie avec flux de fondations ou caisses de pension.
  * **$\Delta < -25\%$ (Ralentissement / Refroidissement — Rouge)** : Tarissement des closings ou perte de négociateurs clés.

### B. La Récence d'Activité (*Days Since Last Sale* — DSLS)
Nombre de jours calendaires écoulés entre la date du jour et le dernier acte notarié attribué à l'enseigne :

$$\text{DSLS} = \text{Date}_{\text{Jour}} - \text{Date}_{\text{Dernier Acte}}$$

* **Grille de Qualification** :
  * **$\le 21$ jours** : *Hyper-Active* (closing hebdomadaire permanent).
  * **22 à 60 jours** : *Activité Normale* (rotation mensuelle standard).
  * **61 à 120 jours** : *En Sommeil* (risque de perte d'emprise sur le quartier).
  * **$> 120$ jours** : *Inactive / Décrochage* (aucun closing enregistré sur le trimestre écoulé).

### C. La Capacité de Closing par Négociateur (*Sales per Broker Pace*)
Rapprochement entre le nombre d'actes conclus sur 12 mois glissants et l'effectif commercial de l'agence (données RC/Annuaires) :

$$\text{Productivité} = \frac{\text{Actes Conclus (12M)}}{\text{Effectif Commercial Recensé}}$$

* Une agence de 3 courtiers signant 24 actes (8 actes/courtier) possède une vélocité commerciale supérieure à une grande enseigne de 25 négociateurs ne signant que 50 actes (2 actes/courtier).

---

## 4. Pin Futur : Moteur de Réconciliation Portails $\to$ Acte Authentique (Le Véritable DOM)

Pour calculer le **délai exact de vente** (*Time to Sell*), nous mettons en réserve le développement de notre moteur de réconciliation prédictive :

```
[ ÉTAPE 1 : CAPTURE DU STOCK ACTIF ]
Annonces en ligne sur Homegate / ImmoScout / Sites Agences
➔ Empreinte : Adresse, Typologie, Étage, Pièces, Prix d'affichage, Date de mise en ligne (T_in)
                         │
                         ▼
[ ÉTAPE 2 : DÉTECTION DU DÉLISTAGE ]
L'annonce disparaît du portail ou passe en "Sous offre" (T_off)
➔ Calcul du Délai d'Affichage = T_off - T_in
                         │
                         ▼
[ ÉTAPE 3 : COLLISION NOTARIÉE (FAO) ]
Sous 30 à 90 jours (délai d'inscription RF), un acte apparaît sur la même parcelle/commune
➔ Rapprochement des caractéristiques physiques (Surface, Étage, Quote-part PPE)
                         │
                         ▼
[ RÉSULTAT DU KPI VÉLOCITÉ ]
• Time to Offer = T_off - T_in (Véritable temps d'acceptation acheteur)
• Transcription Lag = T_fao - T_off (Efficacité notaire / conservation RF)
• Taux de Négociation = (Prix FAO Notarié / Prix Affiché T_in) - 1
```

---

## 5. Conformité LPD & Blindage de la Vie Privée (Outworld Compliancy)

### Le Cadre Juridique Suisse
1. **Loi fédérale sur la protection des données (nLPD / FADP, en vigueur)** :
   * Les données relatives à des **personnes physiques identifiées ou identifiables** constituent des données personnelles protégées.
   * La publication ou l'agrégation non consentie sur des interfaces web (même protégées par mot de passe) de prix de vente associés à des noms de famille de particuliers expose l'exploitant à des injonctions du Préposé fédéral (PFPDT).
2. **Projet de loi cantonal genevois (2026)** :
   * Vise à restreindre la consultation en ligne de la FAO aux seules parties justifiant d'un intérêt digne de protection et à supprimer l'affichage des noms et des prix sur le portail public.
3. **Personnes Morales vs Personnes Physiques** :
   * Les sociétés commerciales (SA, Sàrl, SI, SNC), caisses de pension et entités publiques sont inscrites au Registre du Commerce public (art. 936 CO / ZEFIX) et ne bénéficient pas de la protection nLPD des personnes physiques.

---

### Architecture Cytria : Modèle à Double Écran (Dual-Screen Privacy Architecture)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      CYTRIA PRIVATE VAULT (SOUVERAIN & CHIFFRÉ)                        │
│                           [ data/state/state.sqlite ]                                  │
│  • Conserve 100% des noms bruts : "Vendeur: Dupont Jean, Acheteur: Swiss Life SA"      │
│  • Utilisé pour les calculs internes : Radar Hoiries, Rapprochements ZEFIX, Notariat   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                             FILTRE DE SANITISATION & ANONYMISATION
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   CYTRIA OUTWORLD COMPLIANT UI (INTERFACE VISUELLE)                    │
│                                [ index.html ]                                          │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ CAS 1 : PERSONNE PHYSIQUE (Particulier)                                                │
│ • Vendeur affiché  : "M. J*** D*** (Personne physique)"                                │
│ • Acquéreur affiché: "Particulier / Privé"                                             │
│ • Action légale    : [ 🔗 Vérifier l'identité sur l'avis officiel FAO Genève ↗ ]       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ CAS 2 : PERSONNE MORALE (Société / Institutionnel)                                     │
│ • Vendeur affiché  : "Swiss Prime Site Immobilien AG (CHE-105.856.784)" [Non masqué]   │
│ • Acquéreur affiché: "Fondation Interprofessionnelle de Prévoyance" [Non masqué]      │
│ • Action légale    : [ 🏢 Fiche ZEFIX / Registre du Commerce ↗ ]                       │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Règles d'Anonymisation Automatique dans l'UI :
```typescript
function sanitizePartyName(rawName: string, role: 'SELLER' | 'BUYER'): { displayName: string, isCorporate: boolean } {
  if (!rawName || rawName.trim() === '') {
    return { displayName: 'Non spécifié', isCorporate: false };
  }
  
  // Mots-clés désignant une personne morale (non protégée par la nLPD des particuliers)
  const corporateKeywords = [
    'SA', 'SARL', 'SÀRL', 'SI', 'SNC', 'AG', 'GMBH', 'HOLDING', 'IMMO', 'IMMOBILIER',
    'FONDATION', 'CAISSE', 'PREVOYANCE', 'BANQUE', 'INVESTISSEMENT', 'CAPITAL',
    'COMMUNE', 'VILLE DE', 'ETAT DE', 'ÉTAT DE', 'CONFEDERATION', 'PAROISSE'
  ];
  
  const upper = rawName.toUpperCase();
  const isCorporate = corporateKeywords.some(kw => new RegExp(`\\b${kw}\\b`).test(upper));
  
  if (isCorporate) {
    // Les personnes morales restent transparentes et vérifiables au RC
    return { displayName: rawName, isCorporate: true };
  }
  
  // Personne physique : Masquage nLPD conforme
  // Exemple : "Jean-Marc de la Tour" ➔ "M. J*** D***"
  const tokens = rawName.split(/\s+/).filter(t => t.length > 0);
  const masked = tokens.map((t, idx) => {
    if (idx === 0) return t.charAt(0) + '***';
    return t.charAt(0).toUpperCase() + '***';
  }).join(' ');
  
  return { 
    displayName: `${masked} (Particulier)`, 
    isCorporate: false 
  };
}
```

---

## 6. Passerelles de Redirection vers les Registres d'État

Plutôt que d'afficher des données nominatives sensibles directement dans notre calque, l'application fournit à l'agent un **bouton d'accès direct au registre officiel cantonal**, transférant la consultation sous l'égide des conditions d'utilisation de l'État :

1. **Lien direct avis FAO** :  
   `https://fao.ge.ch/recherche?rubrique=133&date_debut={notice_date}&texte={parcel_number}`
2. **Lien direct extrait cadastral SITG** :  
   `https://ge.ch/sitg/fiche-parcelle?commune={commune}&parcelle={parcel_number}`
3. **Lien direct Registre du Commerce (pour les sociétés)** :  
   `https://www.zefix.admin.ch/fr/search/entity/list?name={corporate_name}`

---

## 7. Plan d'Action & Checklist d'Implémentation

### Phase Vélocité & KPIs Agences
- [x] **V1** : Calculer et afficher sur les fiches des 83 agences :
  * Le volume glissant des 90 derniers jours ($V_{T3M}$).
  * Le delta de dynamique ($\Delta \text{Velocity} = Q_0 \text{ vs } Q_{-1}$).
  * Le nombre de jours depuis la dernière vente enregistrée ($DSLS$).
  * Le débit annuel par négociateur (*Sales per broker pace*).
  * L'indice composite de vélocité Cytria (0-100).
- [x] **V2** : Créer le tri de la League Table : *"Trier par Vélocité & Dynamisme Récents"* et *"Trier par Récence Dernier Acte (DSLS)"*, plus cadran 4-KPIs dans le volet d'inspection.

### Phase Conformité & Masquage nLPD
- [x] **C1** : Intégrer la fonction de détection `isCorporateEntity` dans [`map_builder.py`](file:///c:/Users/sbrot/DEV/Cytria_FAO_Scrapper_Intelligence_AGY/src/fao_transactions/visualization/map_builder.py).
- [x] **C2** : Masquer les noms de personnes physiques dans les volets de détails et bandeaux comparatifs (`M. J*** D*** (Personne physique)`).
- [x] **C3** : Conserver l'affichage en clair uniquement pour les sociétés répertoriées au RC / ZEFIX avec badge `🏢 Personne Morale (RC)`.
- [x] **C4** : Ajouter le lien officiel sortant *"Consulter l'avis officiel au Registre Foncier (fao.ge.ch ↗)"* et *"Fiche Parcelle & Droits Réels SITG"* dans la fiche détaillée de chaque transaction.
- [x] **C5** : Mécanisme de déverrouillage souverain intégré :
  * Paramètre d'URL direct (`?vault=cytria` ou `?key=cytria`) pour accès interne immédiat.
  * Bouton interactif dans la barre supérieure (`🔒 nLPD Conforme` $\leftrightarrow$ `🔓 Mode Souverain Actif`).
  * Modal de saisie du code maître (`cytria`) avec rétention de session (`sessionStorage`).
  * Bouton individuel de révélation inline (`👁️ Révéler`) par transaction.

### Phase Courtiers LinkedIn
- [ ] **L1** : Auditer les annuaires des 83 agences et réactiver individuellement les URLs LinkedIn au fur et à mesure de leur vérification manuelle (actuellement neutralisées et grisées).
