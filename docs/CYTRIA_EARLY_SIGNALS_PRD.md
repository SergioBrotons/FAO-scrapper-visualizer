# Cytria EarlySignals — Product Requirements & Architecture Blueprint
**Pre-Market Intelligence & Assisted Decision-Making for Geneva Real Estate**

---

## 1. Vision & Commercial Proposition

**Cytria EarlySignals** transforms raw cantonal notices (FAO, SITG, Land Register) into an actionable, decision-support operating system for independent real estate agencies, land developers, and private wealth advisers in Geneva.

Rather than positioning the product as a generic "property scraper" or promising "guaranteed seller leads", **Cytria EarlySignals** provides:
1. **Verified Administrative Facts**: Strictly segregated from statistical derivations and probabilistic signals.
2. **Pre-Market Advisory Timing**: Detecting ownership and territorial events 6 to 18 months before properties appear on public listing portals.
3. **Ethical & Compliant Engagement**: Equipping brokers with rigorous, data-backed patrimonial valuation briefs rather than unsolicited cold-calling.
4. **Local Valuation Evidence**: Opposable contiguous notarial transaction benchmarks to anchor price expectations at the right level from day one.

---

## 2. The 3-Tier Data Lineage Model

To maintain uncompromised professional credibility with notaries, banks, and property owners, every data point inside Cytria EarlySignals is labeled according to its legal and technical lineage:

| Level | Classification | Definition & Examples |
| :--- | :--- | :--- |
| **Level 1** | **Fait Public Officiel** | Directly sourced from cantonal registries with zero inference: Publication date, EGRID, parcel number, official zoning, cadastral footprint, published transaction amount. |
| **Level 2** | **Indice Dérivé Calculé** | Algorithmic calculations with transparent methodology: Price per m² based on SITG cadastral envelope, contiguous distance weighting, time decay. |
| **Level 3** | **Signal d'Aide à la Décision** | Commercial hypotheses and propensity indicators: Succession co-ownership friction (CC 602/604), densification potential under Art. 59 LCI, building vintage energy friction. |

---

## 3. The Core Feature: The Opportunity Card (Fiche d'Opportunité Conseil)

Replacing passive dots on a map with an actionable work queue. Each detected signal generates an **Opportunity Card**:

### Anatomy of an Opportunity Card
1. **Territorial Anchor**:
   * Address / Street & Number
   * Parcel Number & Federal EGRID
   * Cadastral Zoning (Zone 5, Zone 2, Zone de Développement)
   * Plot Surface (m²) & Building Footprint (SITG `CAD_BATIMENT_HORSOL`)
2. **Administrative Event Detected**:
   * Event Type: Devolution / Inheritance (Hoirie), Division parcellaire, Autorisation Préalable d'Implanter (APA), Enquête publique.
   * Official Publication Date & Source Gazette (FAO Rubrique 133 / SAD).
3. **Decision Propensity Indicators**:
   * Multi-heir indivision status (CC 602).
   * Building age & energy upgrade constraints (LEn).
   * Densification ratio (IUS / IBUS).
4. **Contiguous Market Benchmark (CMA Evidence)**:
   * Nearest notarized deeds recorded within 250m.
   * Contiguous parcel sale reference (e.g. sale at #16 to benchmark #18).
   * Real effective price/m² certified at land registry.
5. **Recommended Broker Action & Advisory Assets**:
   * *Status*: Période de réserve (J+0 à J+30) vs Fenêtre de conseil technique (J+30 à J+180).
   * *Action*: Generate contiguous valuation brief.
   * *Asset 1*: Pre-filled neighbor advisory letter (`Courrier Riverain Circonstancié`).
   * *Asset 2*: One-click export to CRM task (RealForce / HubSpot / SweepBright).

---

## 4. Workflows for Independent Agencies

### A. The Weekly Territory Radar
Every Monday at 08:30:
1. Cytria executes its differential scan across FAO notices and SITG FeatureServer layers.
2. Filters by the agency's primary micro-markets (e.g. Cologny, Chêne-Bougeries, Vandœuvres, Carouge).
3. Produces a prioritized queue of 5 to 10 explainable advisory opportunities for the agency's designated brokers.

### B. The Contiguous Proof Listing Pitch
When meeting a prospective seller:
1. The broker inputs the target parcel.
2. Cytria isolates identical micro-zone transactions and highlights direct neighbor deeds.
3. Outputs a clean, 2-page institutional memo neutralizing speculative asking prices and justifying an exclusive mandate at the real market price.

### C. The Local Authority Content Engine
The agency leverages aggregate quarterly insights to publish high-value, differentiated content:
* Micro-neighborhood transaction whitepapers.
* Succession and co-ownership tax guidance.
* Zone 5 villa densification analyses.
