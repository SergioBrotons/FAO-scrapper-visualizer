# Moteur de Content Marketing & d'Acquisition Vendeurs : Cytria × Désormière & Vanhalst

**Showcase Flagship :** Désormière & Vanhalst (Rive Gauche Genève)  
**URL de Production / Espace Dédié :** `http://localhost:8088/dv/marketing/`  
**Architecture :** White-Label Ready (multi-tenant avec injection du profil `agency_profile.json`)  
**Design & Brandbook :** 100% conforme à la charte officielle D&V (`#00939D`, `#004A4F`, Cormorant Garamond, Plus Jakarta Sans)

---

## 1. Vision Stratégique & Inbound Vendeurs

Pour capter des **mandats exclusifs** auprès des propriétaires genevois, la communication des agences immobilières ne peut plus se limiter aux traditionnelles publications de type catalogue (*« Vendu par nos soins »*).

Le moteur Cytria Content Marketing résout les **interrogations financières, fiscales et patrimoniales réelles** des propriétaires avant même leur prise de contact :
1. **L'Impôt sur les Gains Immobiliers (ICC - LIPP art. 82) :**
   - Barème dégressif de 50% (< 2 ans) à 0% après 25 ans.
   - Simulation immédiate du produit net en mains après déduction des impenses et travaux.
2. **Le Décodeur Casatax 2026 :**
   - Plafond d'exonération officiel (CHF 1'394'928).
   - Recommandation d'optimisation de prix : positionner un bien légèrement sous le plafond fait économiser jusqu'à CHF 20'924 aux acheteurs et déclenche des offres fermes sans négociation.
3. **Baromètres de Marché Hyper-Locaux (OCSTAT + FAO) :**
   - Fusions des statistiques officielles communales (médianes m², taux d'imposition communal en centimes additionnels, volume annuel) avec les transactions notariées réelles.
4. **Benchmark Concurrentiel & Mandats Stagnants :**
   - Surveillance des mandats bloqués depuis plus de 90/120 jours chez les concurrents (Comptoir Immobilier, SPG, Pilet & Renaud, Barnes, Engel & Völkers).
   - Détection des angles de contre-attaque pour proposer un audit d'arbitrage objectif.

---

## 2. Les 4 Modules de l'Interface (`/dv/marketing/`)

La barre de navigation a été optimisée avec **zéro défilement latéral** et 4 onglets concis et ergonomiques :

| Onglet | Fonctionnalités Clés | Livrables & Actions 1-Clic |
|---|---|---|
| **1. Studio Inbound & Simulateur** | Simulateur Net Vendeur LIPP Art. 82, analyseur Casatax, baromètre communal OCSTAT. | Copier l'argumentaire vendeur, imprimer la fiche A4 client, générer le carrousel LinkedIn/Instagram 5 slides. |
| **2. Matrice Funnel, ICP & Idées de Contenu** | Carrefour des 6 sources contrastées, atelier d'alignement ICP (étape de cadrage avec Sandra & Adrien), matrice des 5 lead magnets, et suggestions dynamiques par étape de funnel (TOFU/MOFU/BOFU). | Lecteur modal complet de guides 1'200+ mots avec actes FAO récents, copie Markdown pour CMS/blog et export impression A4. |
| **3. Veille Réseaux & Benchmark Régies** | Surveillance en continu des réseaux sociaux des 96 régies genevoises (données Cytria `geneva_agencies_master.json`), détection des angles morts adverses, radar des mandats bloqués > 120j. | Matrice de contre-attaque éditoriale D&V et opportunités de reprise de mandats par commune. |
| **4. Cockpit Télémétrie Interne** | Suivi des mots-clés Google Search Console à haute intention vendeur, entonnoir de conversion en 5 étapes. | Attribution directe des leads captés et mandats exclusifs signés au contenu. |

---

## 3. Le Carrefour des 6 Sources Contrastées Cytria

Le générateur d'idées et de lead magnets ne produit jamais de contenu abstrait ou générique. Il s'alimente en temps réel auprès de **6 piliers de données réelles et contrastées** :

1. **Actes Notariés FAO (Registre Foncier) :** 8'970 transactions indexées, prix réels enregistrés, historique de mutations et décotes observées.
2. **Fiscalité Cantonale (LIPP Art. 82) :** Barème dégressif sur les gains immobiliers (de 50% à 0% après 25 ans) et exonération de réinvestissement différé.
3. **Seuil Casatax 2026 :** Plafond d'exonération officiel (CHF 1'394'928) permettant un rabais de droits d'enregistrement jusqu'à CHF 21'433 pour l'acquéreur.
4. **Statistiques Publiques OCSTAT :** Médianes officielles au m² PPE, prix médians des villas et centimes additionnels par commune.
5. **Urbanisme & Cadastre SITG (Zone 5) :** Découpage parcellaire, ratios d'utilisation du sol (IUS 0.20-0.40) et valorisation au m² net constructible.
6. **Vélocité du Marché & Veille Réseaux Cytria :** Surveillance des mandats bloqués > 90-120j et analyse des publications récentes des 96 régies genevoises.

---

## 4. Matrice des 5 Lead Magnets Contrastés par ICP

| ICP Cible | Déclencheur Réel & Profil Vendeur | Lead Magnet Déployé (Format & Hook) | Ancrage Cytria | Associé Référent D&V |
|---|---|---|---|---|
| **ICP 1 : Hoiries & Successions** | Indivision successorale (art. 602 CC), tensions familiales, risque de taxation. | **Guide & Attestation :** *« Transmettre ou Vendre en Indivision à Genève : Protocole de Paix Familiale et d'Arbitrage Fiscal »* | Actes notariés successions FAO | Sandra Bleeckx Vanhalst |
| **ICP 2 : Senior Downsizing** | Villa devenue trop grande (>20 ans de détention), transition vers attique standing. | **Dossier d'Arbitrage :** *« Quitter la Villa Familiale pour une Attique sans Pression Fiscale (Art. 82 LIPP - Réinvestissement) »* | Taux 0% à 25 ans + Prix villas Rive Gauche | Sandra Bleeckx Vanhalst |
| **ICP 3 : Grandes Parcelles Zone 5** | Sollicitations agressives de promoteurs à Troinex, Veyrier, Vandœuvres. | **Dossier Foncier :** *« Division de Parcelle vs Vente en Bloc à un Promoteur : Comment Sécuriser votre Plus-Value »* | Cadastre SITG Zone 5 + IUS 0.20-0.40 | Adrien Désormière |
| **ICP 4 : PPE sous Seuil Casatax** | Vente d'un appartement autour de 1.2M - 1.5M avec incertitude sur le pricing. | **Baromètre Stratégique :** *« Le Décodeur Casatax 2026 : Pourquoi Fixer son Prix sous CHF 1'394'928 Déclenche 3x Plus d'Offres »* | Seuil officiel 2026 (rabais max CHF 21'433) | Sandra & Adrien |
| **ICP 5 : Mandats Bloqués Concurrents** | Bien en vente depuis plus de 90-120 jours dans une régie traditionnelle sans offre sérieuse. | **Audit Diagnostic :** *« Pourquoi Votre Bien Ne Se Vend Pas : Les 5 Erreurs Commises par les Régies Traditionnelles »* | Listings stagnants > 120j & décotes de prix | Désormière & Vanhalst |

---

## 5. Endpoints REST API Déployés

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/marketing/agency-profile` | `GET` | Renvoie le profil actif (`?agency=desormiere_vanhalst`) et la liste des profils disponibles. |
| `/api/marketing/fiscal-simulation` | `GET` | Calcule le net vendeur, l'impôt LIPP art. 82 et l'éligibilité Casatax 2026 selon prix, années et travaux. |
| `/api/marketing/competitor-radar` | `GET` | Fournit le benchmark des concurrents et les opportunités de mandats stagnants > 120 jours. |
| `/api/marketing/social-surveillance` | `GET` | Expose la veille des réseaux sociaux (LinkedIn, Instagram, Web) des 96 régies et les opportunités de contre-attaque D&V. |
| `/api/marketing/telemetry-metrics` | `GET` | Renvoie le tableau de bord GSC, l'entonnoir de conversion et le top des contenus convertisseurs. |
| `/api/marketing/quartier-guide` | `GET` | Génère le baromètre officiel OCSTAT et le carrousel 5 slides pour une commune donnée (`?commune=Troinex`). |
| `/api/marketing/funnel-suggestions` | `GET` | Génère les suggestions dynamiques TOFU, MOFU, BOFU croisées avec les données foncières locales. |
| `/api/marketing/full-guide` | `GET` | Produit le guide complet de 1'200+ mots avec chapitres, actes notariés récents FAO et call-to-action personnalisé. |
| `/dv/marketing/` | `GET` | Interface utilisateur complète respectant la charte graphique D&V. |

---

## 6. Tests et Validation Automatisée

Le moteur dispose d'une couverture de tests rigoureuse avec Bun Test :
- `tests/test_content_marketing.test.ts` : 9 tests unitaires et d'intégration validés à 100% (incluant la veille réseaux sociaux et le générateur de guides).
- `tests/test_dv_intelligence.test.ts` : 16 tests D&V validés à 100%.
- `tests/test_surgical_hardening.test.ts` : 18 tests de conformité légale et nLPD validés à 100%.
- **Total : 43 tests réussis (0 échec).**
