# Reverse engineering of the Désormière & Vanhalst property-estimation process

**Reference case:** 3-room PPE apartment, Chemin du Saut-du-Loup 18, Chêne-Bourg  
**Source document:** Estimation dated 21 August 2025  
**Purpose:** Reconstruct the operating process, data sources, formulas, judgement points and evidence needed to reproduce the estimate in a traceable DigitalCoa.ch tool.

## 1. Executive conclusion

The estimation is a hybrid deliverable combining five functions:

1. a property fact file;
2. a qualitative visit report;
3. a comparable-market analysis;
4. an adjusted price calculation;
5. a brokerage proposal.

The calculation on page 11 is arithmetically coherent, but the final value depends heavily on four professional assumptions that are not yet formalised:

- retained base price: CHF 11,000 per weighted m²;
- depreciation: 5%;
- garden value: CHF 1,000 per m²;
- parking value: CHF 50,000.

The future system should not attempt to replace Sandra's judgement. It should collect and verify evidence, calculate reproducibly, expose uncertainty, detect inconsistencies and require Sandra to approve or override each material assumption.

## 2. Report architecture

| Pages | Module | Case-specific? | Primary function |
|---|---|---:|---|
| 1 | Cover | Yes | Client and assignment identity |
| 2 | Property designation | Yes | Authoritative property record |
| 3 | Cadastre and location | Yes | Spatial evidence |
| 4 | Characteristics and location | Yes | Visit findings and expert assessment |
| 5-6 | Photographs | Yes | Condition and feature evidence |
| 7 | Plans | Yes | Layout, lot and dependencies |
| 8 | Current listings | Yes | Asking-price comparables |
| 9 | New-development benchmark | Yes | Normalised local comparables |
| 10 | Market indicators | Partly | Wider market context |
| 11 | Valuation | Yes | Calculation and price recommendation |
| 12 | Advice | Yes | Tax and sale-timing guidance |
| 13-15 | Agency, testimonials, fees, contact | Mostly no | Conversion to mandate |

## 3. Source taxonomy and provenance rules

Every datum should be stored with one of the following source classes.

| Class | Meaning | Example | Required evidence |
|---|---|---|---|
| Official record | Issued by a public authority | Parcel, building number, planning zone | Source URL/document, retrieval date |
| Legal/PPE document | Governs the lot or co-ownership | PPE quota, easement, garden-use right | Document name, page, date |
| Owner declaration | Supplied by the seller | Renovation history, equipment | Owner identity and confirmation date |
| Visit observation | Observed by the agent | Condition, nuisance, light | Agent, date, note/photo |
| Market listing | Advertised supply | Properstar listing | Portal, URL, capture date, listing ID |
| Transaction evidence | Completed or officially published sale | FAO sale notice | Publication/date/reference |
| Commercial market model | Third-party estimate/index | RealAdvisor | Provider, model date, limitations |
| Agency rule | Reusable D&V convention | 50% loggia weighting | Rule version and approval |
| Expert judgement | Case-specific decision | CHF 11,000/m² retained | Sandra's rationale and approval |
| Calculated field | Deterministic transformation | Weighted area | Formula and input versions |

The interface should display these classes visually. A manual judgement must never appear as an official fact.

## 4. Full field-level reverse engineering

### 4.1 Assignment and owner

| Field | Value in case | Likely source | Processing | Confirmation needed |
|---|---|---|---|---|
| Owner name | Sergio Brotons Mas | Client intake / RF | Formatting | Is RF ownership always checked? |
| Report date | 21.08.2025 | System | Automatic | Date of issue or date of valuation? |
| Visit date | 28.07.2025 | Calendar/agent | Manual | One or multiple visits? |
| Purpose | Sale | Client intake | Selection | Other purposes supported? |
| Validity | December 2025 | Sandra | Expert rule | Fixed duration or market-dependent? |
| Fee | Offered instead of CHF 890 | Agency policy | Template | When is it invoiced or waived? |

### 4.2 Legal and cadastral identity

| Field | Case value | Primary source | Secondary source | Automation potential |
|---|---|---|---|---|
| Address | Saut-du-Loup 18 | RF/PPE | Geocoder | High |
| Parcel | 4643 | RF/cadastre | SITG | High |
| Buildings | 2921 and 2922 | RF/cadastre | SITG | High |
| Legal form | PPE | RF/PPE deed | Owner document | Medium |
| PPE lot | 2.02 | PPE deed/cahier | RF | Medium |
| Quota | 132.5‰ | PPE deed/cahier | RF | Medium |
| Floor | Ground floor | PPE plan | Visit | Medium |
| Zone | Zone 5 villas | RDPPF/SITG | RF plan | High |
| Development name | Le Clos des Papillons | PPE/marketing docs | Owner | Low |
| Purchase date | 01.04.2019 | RF/deed/FAO | Owner | Medium |
| Purchase price | CHF 990,000 | Deed/FAO | Owner | Medium |
| Easements | Garden, parking 7, cellar c | RF/PPE documents | Plans | Low due legal interpretation |

**Potential official sources**

- Geneva Land Registry consultation and certified extracts: https://www.ge.ch/consulter-registre-foncier and https://www.ge.ch/consulter-registre-foncier/demander-prestations-certifiees-du-registre-foncier
- SITG parcel layer: https://sitg.ge.ch/donnees/cad-parcelle-mensu
- SITG catalogue and geospatial services: https://sitg.ge.ch/
- RDPPF extract: https://www.ge.ch/consulter-cadastre-rdppf/demander-extrait-du-cadastre-rdppf
- FAO official notices: https://fao.ge.ch/

### 4.3 Areas and physical configuration

| Field | Case value | Likely source | Risk |
|---|---:|---|---|
| PPE apartment surface | 73 m² | PPE deed/plan | Must distinguish PPE, net, usable and sale surface |
| Loggia | 11 m² | Plan/brochure | Closed but unheated: classification matters |
| Terrace | 42 m² | Plan/measurement | Verify title and exclusive use |
| Garden | approx. 250 m² | Plan/easement/measurement | Report calls it private, legal section suggests a use right |
| Rooms | 3 | PPE/agency convention | Geneva room-count convention must be consistent |
| Bedrooms | 1 | Visit/plan | Current use differs from intended use |
| Bathrooms | 2 | Visit/plan | Straightforward |
| Parking | No. 7 | PPE/easement/plan | Confirm whether separate lot or servitude |
| Cellar | Letter c | PPE/easement/plan | Confirm legal attachment |

The system should retain original area definitions and calculate a separate agency-weighted area. It should never overwrite the authoritative PPE area.

### 4.4 Building, energy and compliance

| Field | Case value | Potential source | Validation rule |
|---|---|---|---|
| Construction year | 2019 | RF/building register/PPE | Cross-check |
| Minergie | GE-1672 | Certificate / Minergie register | Lookup by certificate or address |
| Heating | Heat pump, underfloor | Technical specification/PPE | Document or owner confirmation |
| Solar panels | Roof | PPE/building spec/SITG | Confirm shared/private and function |
| Windows | Triple glazing, PVC | Visit/specifications | Mark observed vs documented |
| IDC | Not performed | OCEN/SITG/PPE | Verify whether exempt/facultative/undeclared |
| OIBT | To be planned | Certificate/owner | Store certificate date and expiry logic |
| Asbestos | No | Construction year/report | Must not state categorical absence without evidence |
| Polluted site | No | SITG polluted-sites cadastre | Spatial lookup with retrieval date |

**Potential sources**

- Minergie building register: https://www.minergie.ch/fr/batiments/liste-des-batiments/
- Geneva IDC explanation: https://www.ge.ch/connaitre-consommation-energie-batiment-idc
- SITG IDC declaration status: https://sitg.ge.ch/donnees/ocen-etat-idc
- SITG building IDC averages: https://sitg.ge.ch/donnees/scane-indice-moyennes-3-ans
- Polluted-sites FeatureServer: https://thematic.sitg.ge.ch/arcgis/rest/services/CADASTRE_RDPPF/FeatureServer/43
- Road-noise cadastre: https://sitg.ge.ch/applications/cadastre-du-bruit-routier-3d

### 4.5 PPE finances and future works

| Field | Case value | Source | Extraction opportunity |
|---|---:|---|---|
| Renovation fund | CHF 31,862.30 at 12.2024 | PPE accounts | OCR/table extraction |
| Charges | CHF 559/month | PPE statements/accounts | Normalise monthly/annual and inclusions |
| Future works | None indicated | AG agendas/minutes | Document search and risk summary |
| Shared dependencies | Bike/stroller room, visitor parking, green space | PPE documents/visit | Structured checklist |

The system should analyse at least the last three available years of accounts and minutes where possible, not only two selected years. It should extract voted works, quotations, litigation, arrears, fund balance, annual contributions and extraordinary calls.

### 4.6 Visit and qualitative scoring

The report uses narrative judgements without an explicit scoring model:

- condition: very good;
- location: good;
- environment: pleasant;
- nuisance: none;
- view: greenery;
- orientation: north-south-east;
- sunlight: all day;
- positive features: location, closed loggia, landscaped garden, corner position, terraces, parking.

Recommended structured visit dimensions:

| Dimension | Scale | Evidence |
|---|---|---|
| Interior condition | 1-5 plus notes | Photos |
| Building/common parts | 1-5 | Photos/PPE docs |
| Renovation quality | Date and grade | Invoices/observation |
| Light | Poor to exceptional | Orientation/time/photo |
| View/outlook | Obstructed to exceptional | Photos |
| Noise | None to severe | Observation plus SITG noise |
| Privacy | Low to high | Observation |
| Exterior usability | Low to high | Size, access, slope, exposure |
| Layout efficiency | Poor to excellent | Plan and agent assessment |
| Accessibility | Structured checklist | Lift, steps, doors |
| Micro-location | 1-5 | Distances and agent assessment |

Sandra should decide which scores affect price quantitatively and which remain explanatory only.

## 5. Comparable-market process

### 5.1 Current listings, page 8

Visible sources are dreamo.ch and properstar.ch. Five three-room apartments between 63 and 119 m² are selected, with asking prices from approximately CHF 9,118 to CHF 16,032 per m².

Required comparable fields:

- listing ID and canonical URL;
- portal and capture date;
- first-seen and last-seen dates;
- status: active, removed, reserved, sold if known;
- duplicate group across portals;
- asking-price history;
- address confidence;
- property type and legal form;
- rooms, interior area and area definition;
- construction/renovation year;
- floor, lift, condition and energy features;
- balcony, terrace and garden;
- parking inclusion or supplement;
- new-build versus resale;
- straight-line and travel distance;
- similarity score and exclusion reason.

**Critical controls**

1. De-duplicate the same property advertised by several agencies/portals.
2. Separate asking prices from transaction prices.
3. Separate new-build from resale or apply an explicit new-build premium.
4. Record whether parking is included.
5. Avoid dividing by incompatible surface definitions.
6. Preserve screenshots because listings change or disappear.
7. Check portal terms before automated collection; prefer licensed feeds or manual assisted capture where scraping is not authorised.

### 5.2 New-development benchmark, page 9

The table uses Belara and Clos des Charmes. It normalises garden apartments by assigning CHF 1,000/m² to the garden, subtracting this amount from the advertised price and dividing the residual price by weighted built area. The reported average is CHF 11,903/m² weighted.

Reverse-engineered row formula:

```text
weighted_surface = interior_surface
                 + balcony_weight × balcony_surface
                 + rooftop_weight × rooftop_surface

garden_value = garden_surface × garden_rate
price_ex_garden = displayed_price - garden_value
price_per_weighted_m2 = price_ex_garden / weighted_surface
```

Open questions:

- What are the balcony and rooftop coefficients?
- Does displayed price exclude parking in every row?
- Is garden value linear at all sizes?
- Are ground-floor privacy, orientation and direct access considered?
- Are unavailable prices excluded automatically?
- Is the average arithmetic, weighted, median or trimmed?
- Are the prices signed transactions, reservation prices or brochure asking prices?

The future tool should calculate median, mean, weighted mean and interquartile range. Sandra should select the decision statistic, with outliers shown rather than silently removed.

### 5.3 Transaction evidence

Potential sources, in descending order of evidential strength:

1. notarised/deed or confirmed agency transaction;
2. official FAO notice and RF information;
3. D&V historic closed transactions;
4. OCSTAT aggregated transaction statistics;
5. developer reservation/sale lists;
6. removed listings with inferred sale, clearly labelled as inference;
7. current asking-price listings.

FAO notices and the existing FAO PDF extraction pipeline can support a structured transaction database. Each record should preserve the source PDF, publication date, parties where lawful, parcel/building references, transaction price, property description and extraction confidence. Personal-data use must be purpose-limited and access-controlled.

## 6. Macro and geospatial context

### 6.1 Market context

The report uses:

- OCSTAT historical PPE price chart for the canton;
- RealAdvisor price evolution for Chêne-Bourg;
- RealAdvisor local average price per m².

Potential additions:

- OCSTAT transaction and price series by commune/property type;
- Swiss National Bank mortgage-rate series;
- vacancy and housing-stock statistics;
- building permits and local development pipeline;
- D&V internal time-on-market and negotiation discount;
- licensed AVM or professional market data where economically justified.

Official OCSTAT entry point: https://statistique.ge.ch/ . The site includes the domain “transactions et prix de l’immobilier”.

### 6.2 Micro-location

Potential sources:

- SITG parcel, zoning, RDPPF, noise, heritage, trees, hazards and building layers;
- TPG stop and timetable data;
- OpenStreetMap for amenities and pedestrian network;
- municipal/school data for schools and childcare;
- travel-time engine for station, city centre and services;
- orthophotos and permitted street imagery.

Calculated indicators could include walking distance to CEVA/TPG, schools, groceries, parks and health services, while keeping Sandra's qualitative neighbourhood judgement separate.

## 7. Valuation calculation reconstructed

### 7.1 Weighted area

```text
73.00 × 100% = 73.00
11.00 ×  50% =  5.50
42.00 ×  33% = 13.86
Exact weighted area = 92.36 m²
Reported weighted area = 92.5 m²
```

The rounding convention should be explicit. At CHF 11,000/m², using 92.5 rather than 92.36 adds CHF 1,540.

### 7.2 Base and adjustments

```text
92.5 × CHF 11,000                         CHF 1,017,500
Depreciation: 5% of base                 -CHF    50,875
Garden: 250 m² × CHF 1,000               +CHF   250,000
Parking                                  +CHF    50,000
Cellar                                               0
Calculated total                          CHF 1,266,625
Recommended asking range                  CHF 1,270,000-1,290,000
```

The recommended range is CHF 3,375 to CHF 23,375 above the calculated result, or approximately 0.3% to 1.8%.

### 7.3 Sensitivity

Each CHF 500/m² change in the base rate changes value by CHF 46,250 before depreciation. Each CHF 100/m² change in garden rate changes value by CHF 25,000. The garden-rate assumption is therefore almost as influential as a CHF 270/m² shift in the base rate.

The tool should show at least three scenarios:

- conservative;
- central;
- ambitious asking price.

Each scenario should show expected negotiation margin and likely sale range separately from the published asking price.

## 8. Issues and controls identified

| Issue | Risk | Proposed control |
|---|---|---|
| Asking prices treated alongside transaction evidence | Overvaluation | Label source type and use separate statistics |
| Parking may be included in some comparables and added again | Double counting | Mandatory parking inclusion field |
| Garden-use right described as private garden | Legal overstatement | Extract exact RF/PPE wording |
| Fixed CHF 1,000/m² garden rule | Large unsupported adjustment | Versioned rule plus sensitivity and rationale |
| 5% depreciation despite 2019 build and “very good” condition | Unclear adjustment | Depreciation matrix and manual reason |
| CHF 11,000 selected from higher market indicators | Opaque judgement | Selection rationale and comparable reconciliation |
| “Valeur intrinsèque” label | Methodological ambiguity | Rename “adjusted comparative indication” unless Sandra defines otherwise |
| “No asbestos” | Unsupported categorical statement | Evidence or “not identified / not expected due to age” wording |
| “No nuisance” | Visit-time bias | Agent observation plus noise/geospatial evidence |
| Fiscal date on page 12 | Incorrect advice | Rule engine sourced to official brackets |

## 9. Fiscal module correction

For an acquisition on 1 April 2019:

- 1 April 2025 to 31 March 2027: at least six years, 20%;
- 1 April 2027 to 31 March 2029: at least eight years, 15%;
- from 1 April 2029: at least ten years, 10%.

The report's “April 2028” transition and “10-25 years at 15%” do not match the official Geneva bands. The current official source is: https://www.ge.ch/impot-benefices-gains-immobiliers/calculer-montant-impot

The tool should present this as general information, record the retrieval date and direct the owner to a tax adviser/notary for personal advice. It should also capture deductible acquisition costs, qualifying value-adding works, brokerage commission and possible replacement-home reinvestment.

## 10. Proposed future workflow

### Ownership legend

- **AUTO:** the system executes the step once its source and rule are configured.
- **ASSISTED:** the system prepares a result, but Sandra or another qualified professional validates it.
- **PRO:** the step depends on professional observation, interpretation, negotiation or accountability.

### Stage A: Intake

1. **AUTO:** Create the case from an intake form, email or CRM record.
2. **PRO:** Confirm the owner, purpose, scope and client consent.
3. **ASSISTED:** Issue the document request and reminders; Sandra decides whether the evidence received is sufficient.
4. **AUTO:** Classify uploads, identify duplicates and generate the missing-document checklist.
5. **PRO:** Decide whether work may proceed when mandatory evidence is unavailable.

### Stage B: Extraction and official enrichment

1. **AUTO:** OCR, classify and index documents.
2. **AUTO:** Extract property, surface, financial and legal-reference candidates with page citations and confidence.
3. **AUTO:** Resolve address, parcel and building identifiers.
4. **AUTO:** Query approved SITG, RDPPF, OCSTAT, IDC and Minergie sources.
5. **AUTO:** Flag contradictions, missing values and stale evidence.
6. **ASSISTED:** Sandra validates material facts and exact legal/PPE wording.
7. **PRO:** Consult a notary, lawyer, electrician, energy or building specialist when needed.

### Stage C: Visit

1. **AUTO:** Prepare a property-specific mobile checklist from unresolved questions.
2. **PRO:** Sandra performs the visit and evaluates condition, layout, light, outlook, noise, privacy, usability and defects.
3. **ASSISTED:** Automatically group photographs by room and check required views; Sandra validates labels and selections.
4. **AUTO:** Transcribe dictated notes and propose structured observations.
5. **PRO:** Sandra validates qualitative scores and decides which observations affect value.
6. **PRO:** OIBT, asbestos, structural, moisture and energy inspections remain specialist inputs.

### Stage D: Market evidence

1. **AUTO, with authorised access:** Retrieve candidate listings from licensed feeds, approved integrations or assisted capture.
2. **AUTO:** Standardise fields, detect duplicates, identify price changes and distinguish listings from transactions.
3. **AUTO:** Retrieve D&V historical cases, structured FAO evidence and approved market indicators.
4. **AUTO:** Rank comparables by distance, type, area, age, condition, floor, exterior space, parking and evidence quality.
5. **ASSISTED:** Generate an explained proposed comparable set.
6. **PRO:** Sandra includes or excludes comparables and records why.
7. **PRO:** Sandra decides whether and how new-build comparables should be adjusted.

### Stage E: Valuation

1. **AUTO:** Calculate weighted areas using the approved rule version.
2. **AUTO:** Produce median, mean, range, dispersion and outlier analysis.
3. **AUTO:** Apply versioned rules for exterior areas, parking, cellar and dependencies.
4. **AUTO:** Generate conservative, central and ambitious scenarios and sensitivities.
5. **ASSISTED:** Recommend a base-rate interval with supporting and contradictory evidence.
6. **PRO:** Sandra selects or overrides the base rate, garden value, depreciation, parking and qualitative adjustments.
7. **PRO:** Sandra defines market value, asking price, expected sale range and negotiation strategy.
8. **AUTO:** Recalculate, verify and record approvals and override reasons.

### Stage F: Report and mandate

1. **AUTO:** Generate a source-linked draft.
2. **AUTO:** Run completeness, arithmetic, freshness, double-counting, unsupported-claim and contradiction checks.
3. **ASSISTED:** Draft the property description, market narrative, fiscal information and recommendations.
4. **PRO:** Sandra approves wording, evidence, valuation and price strategy.
5. **AUTO:** Generate the final PDF and client portal only after approval.
6. **PRO:** Sandra presents the estimate, answers objections and recommends the commercial strategy.
7. **AUTO:** Capture feedback, follow-up tasks and mandate outcome.

### Stage G: Learning loop

**AUTO:** Import and calculate measurable outcome fields.  
**PRO:** Sandra records the contextual reasons behind unexpected results.

After sale, record:

- first asking price;
- price changes;
- days on market;
- number and quality of enquiries;
- offers received;
- final sale price;
- adjustment from estimate;
- which comparables and assumptions proved accurate.

This turns Sandra's experience into an auditable local evidence base without reducing it to an opaque model.

### What can be fully automated

- Case creation, document requests and reminders.
- Document classification, OCR, extraction and page-level citation.
- Address, parcel and building resolution and approved public-data enrichment.
- Missing-data, contradiction and freshness checks.
- Deterministic surface and valuation calculations.
- Comparable normalisation, duplicate detection and preliminary ranking.
- Statistics, sensitivity analysis and scenario generation.
- Fiscal-bracket date calculation from an approved official rule table.
- Draft tables, charts, narratives and report population.
- Arithmetic, double-counting and unsupported-claim controls.
- Version history, decision log, approval workflow and audit trail.
- Final document generation after approval.
- Follow-up reminders and outcome calculations.

### What requires Sandra or another professional

- Confirming the purpose, scope and sufficiency of evidence.
- Interpreting RF, PPE, servitude and ownership documents where material.
- Inspecting condition, quality, layout, light, nuisance, privacy and defects.
- Deciding which comparables are genuinely relevant.
- Approving weighting and adjustment rules.
- Setting garden, parking, depreciation, condition and location adjustments.
- Selecting the base CHF/m² and explaining deviations.
- Distinguishing market value, expected sale value, asking price and negotiation strategy.
- Validating legal, fiscal, energy and compliance statements.
- Deciding when a notary, tax adviser, electrician or building specialist is required.
- Presenting the estimate, handling objections and approving the final report.

## 11. Minimum data model

Core entities:

- Client
- Property
- Ownership/legal record
- Building
- PPE
- Area component
- Dependency/easement
- Document
- Extracted fact
- Visit observation
- Photograph
- Comparable
- Market indicator
- Valuation rule
- Valuation scenario
- Adjustment
- Decision/override
- Report version
- Mandate
- Sale outcome

Every extracted fact should contain `value`, `unit`, `source_type`, `source_reference`, `source_date`, `extracted_at`, `confidence`, `verified_by`, `verified_at` and `superseded_by`.

## 12. Questions Sandra must confirm

1. Which documents are mandatory before an estimate can be issued?
2. Which fields come from RF, PPE documents, the owner and the visit?
3. What does FAO contribute to this specific report today?
4. Are surfaces copied, measured or reconciled when documents disagree?
5. Are the 100%/50%/33% weighting coefficients fixed?
6. How are balconies, loggias, terraces, roof terraces and gardens distinguished?
7. Is CHF 1,000/m² for gardens universal, communal or case-specific?
8. Is garden value linear, capped or discounted by size?
9. What rules select current listings?
10. How are duplicate listings recognised?
11. Are Belara/Clos des Charmes prices asking, reservation or completed-sale prices?
12. How is parking removed from comparable prices?
13. Which statistic determines the market benchmark?
14. Why was CHF 11,000/m² selected instead of CHF 11,903 or CHF 12,723?
15. How is the 5% depreciation determined?
16. Which qualitative characteristics create numerical adjustments?
17. How are value, asking price and expected sale price distinguished?
18. How wide should the final range be?
19. Who validates legal, energy and tax statements?
20. Which parts must always remain Sandra's manual decision?
21. How long does each current step take?
22. Which source licences or subscriptions does the agency already have?
23. Where are past estimates and final sale outcomes stored?
24. May those historical cases be used to calibrate internal rules?

## 13. Recommended implementation boundary

**Automate first:** document extraction, source linking, cadastral/geospatial enrichment, calculations, comparable tables, duplicate detection, report population, arithmetic and consistency checks.

**Human approval required:** legal interpretation, condition assessment, comparable inclusion, adjustment rates, final price strategy, tax wording and final report release.

**Do not automate without licensed access:** large-scale portal scraping, reuse of copyrighted listing images/text, or personal-data enrichment beyond the agreed and lawful purpose.

## 14. Proposed validation output from Sandra

For each process step, Sandra should mark:

- correct as described;
- correct with modification;
- not part of the process;
- missing step;
- automatable;
- assisted only;
- must remain manual.

The validated result becomes the functional specification for the estimation module and should be versioned separately from the seller-identification prospecting module.
