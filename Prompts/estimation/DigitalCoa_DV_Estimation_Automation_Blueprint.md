# DigitalCoa.ch blueprint: assisted property-estimation system

**Client process:** Désormière & Vanhalst  
**Reference case:** Saut-du-Loup 18, Chêne-Bourg  
**Product principle:** automate evidence and production; preserve professional judgement and accountability.

## 1. Product outcome

Build a secure workspace that transforms property documents, approved external data, visit observations and market evidence into a traceable draft valuation. Sandra remains the final decision-maker for comparables, adjustments, valuation, sales strategy and release.

The system succeeds when it reduces repetitive preparation without hiding assumptions or producing an unsupervised valuation.

## 2. Scope boundary

### In scope

- intake and document collection;
- document extraction and evidence mapping;
- Geneva official-data enrichment;
- visit preparation and structured capture;
- comparable collection from authorised sources;
- comparable normalisation and ranking;
- transparent calculations and scenarios;
- professional review and override;
- report generation and audit history;
- outcome capture and later calibration.

### Out of scope initially

- autonomous publication of a valuation;
- definitive legal, tax, OIBT, asbestos or structural conclusions;
- unlicensed mass scraping of portals;
- fully automatic comparable acceptance;
- black-box price prediction;
- automatic client negotiation or mandate signing.

## 3. End-to-end flow

~~~mermaid
flowchart TD
    A["Documents and intake"] --> B["Evidence extraction"]
    B --> C["Official enrichment"]
    C --> D["Visit workspace"]
    D --> E["Comparable engine"]
    E --> F["Calculation and scenarios"]
    F --> G["Sandra review gate"]
    G --> H["Report and client portal"]
    H --> I["Mandate and sale outcome"]
    I --> E
~~~

No client-facing estimate is released until every material fact and adjustment is approved.

## 4. Decision classes

| Class | System behaviour | Examples |
|---|---|---|
| Deterministic | Calculate automatically | Weighted area, totals, tax dates |
| Extracted | Propose with source and confidence | PPE quota, fund balance |
| Enriched | Retrieve from approved source | Parcel, RDPPF, Minergie |
| Recommended | Propose with explanation | Comparable set, base-rate interval |
| Professional | Require explicit decision | Final comparables, adjustments, price |
| Specialist | Block or qualify pending input | OIBT, asbestos, structural concern |

## 5. Roles and authority

| Role | Authority |
|---|---|
| Sandra / senior valuer | Validate evidence, select comparables, approve adjustments, release report |
| Adrien / authorised valuer | Equivalent authority where agreed |
| Assistant | Documents, listings and visit preparation; cannot release |
| DigitalCoa administrator | Templates, integrations and rule configuration; cannot silently change issued cases |
| Client | Upload requested documents and view approved outputs |
| External specialist | Supply a scoped certificate/report without unrelated case access |

## 6. Core screens

### Case dashboard

- workflow stage and next action;
- missing documents;
- unresolved contradictions;
- pending professional decisions;
- source-freshness warnings;
- report-readiness score.

### Evidence room

- classified documents;
- PDF viewer with highlighted extracted fields;
- source page for every fact;
- competing values side by side;
- confidence and verification status.

### Property record

- authoritative legal and physical facts;
- legal, physical and weighted surfaces kept separate;
- dependencies, easements and PPE finances;
- energy/compliance evidence;
- provenance on every field.

### Visit workspace

- pre-filled unresolved questions;
- mobile checklist;
- voice transcription;
- room-linked photos;
- qualitative scoring;
- specialist-referral flags.

### Comparable workspace

- map and sortable table;
- listings versus transactions;
- duplicate groups and price history;
- similarity explanation;
- parking/garden/new-build controls;
- Sandra's include/exclude reason;
- source snapshot.

### Valuation workbench

- exact weighted-area formula;
- comparable distribution and outliers;
- rule version;
- conservative, central and ambitious scenarios;
- editable professional adjustments;
- immediate sensitivity effect;
- separate market value, asking price and expected sale value;
- mandatory override rationale.

### Report review

- page preview;
- claim-to-source links;
- unresolved-warning panel;
- version comparison;
- approval checklist;
- authorised release.

### Outcome dashboard

- mandate and listing history;
- enquiries, visits and offers;
- final sale;
- estimate-versus-sale variance;
- rule and comparable performance.

## 7. Technical architecture

Use the existing DigitalCoa client-workspace stack:

- **Frontend:** Next.js, responsive and bilingual-ready.
- **Identity/database:** Supabase Auth and PostgreSQL with row-level security.
- **Files:** private object storage with short-lived signed access.
- **Processing:** queued OCR, classification and extraction workers.
- **Geospatial:** PostGIS or PostgreSQL geographic types.
- **Rules:** versioned database/JSON rules, not values hidden in interface code.
- **Reports:** HTML/CSS templates rendered to PDF with immutable source snapshots.
- **Audit:** append-only decisions and event history.
- **Sources:** approved SITG, RDPPF, OCSTAT, IDC, Minergie, internal FAO and licensed market feeds.
- **Agent support:** Hermes or approved models may extract and draft, but cannot approve fields or release reports.

## 8. Service modules

| Service | Responsibility |
|---|---|
| Intake | Case, consent and document requests |
| Documents | Upload, OCR, classification, extraction and citation |
| Property | Canonical record and contradiction resolution |
| Enrichment | Official and licensed source retrieval |
| Visit | Checklists, notes, photos and observations |
| Comparables | Capture, de-duplication, normalisation and ranking |
| Valuation | Rules, calculations, statistics and scenarios |
| Decisions | Approvals, overrides and role enforcement |
| Reports | Draft, controls, PDF/portal output and versioning |
| Outcomes | Mandate, marketing and sale-result capture |

## 9. Minimum data model

- cases, clients, properties and buildings;
- PPE entities, ownership records, areas, dependencies and servitudes;
- documents, pages, extracted facts and source snapshots;
- external observations, visits and photographs;
- comparables, adjustments and market indicators;
- rule sets, scenarios, valuation decisions and approvals;
- report versions, mandates, sale outcomes and audit events.

Every material fact stores its value, unit, source type, source reference, source date, extraction date, confidence, verification state, verifier and supersession history.

## 10. Workflow states and release gates

~~~mermaid
stateDiagram-v2
    [*] --> Intake
    Intake --> EvidenceReview
    EvidenceReview --> VisitReady
    VisitReady --> MarketAnalysis
    MarketAnalysis --> ValuationReview
    ValuationReview --> ReportReview
    ReportReview --> Released: Sandra approves
    ReportReview --> ValuationReview: Changes required
    Released --> MandateTracking
    MandateTracking --> Closed
~~~

Hard blockers before release:

- unresolved owner or property identity;
- missing authoritative surface;
- unexplained material contradiction;
- no approved comparable set;
- unapproved material adjustment;
- arithmetic/control failure;
- unsupported categorical legal or compliance claim;
- absent authorised-valuer approval.

## 11. Rule engine

Every rule needs:

- identifier and version;
- applicable property type and geography;
- effective dates;
- formula or decision table;
- default and permitted range;
- rationale/source;
- approving professional;
- change history.

Rules to validate with Sandra:

- apartment 100%, loggia 50%, terrace 33%;
- balcony and rooftop coefficients;
- garden-value function and any cap/decline;
- parking and cellar treatment;
- depreciation/condition matrix;
- new-build versus resale adjustment;
- comparable distance and age limits;
- outlier treatment;
- range width and rounding.

Changing a rule must never alter an already issued report.

## 12. Comparable engine

### Candidate generation

Filter by commune/distance, legal and property type, rooms, interior/weighted area, age, floor, lift, condition, exterior space, parking and evidence date.

### Ranking

Start with an explainable weighted similarity score. Display each component. Sandra may override it with a reason.

### Normalisation

- preserve original values;
- identify the surface definition;
- separate parking where possible;
- apply approved exterior-area rules;
- mark new-build versus resale;
- exclude instead of inventing a critical missing value.

### Output

- selected and rejected sets;
- median, mean and dispersion;
- original and weighted CHF/m²;
- map;
- adjustment bridge from each comparable to the subject.

## 13. Automated controls

- recompute every arithmetic result;
- detect parking/garden double counting;
- flag exact versus rounded area;
- flag asking prices described as transactions;
- detect incompatible surface definitions;
- flag stale sources and missing snapshots;
- block unsupported categorical asbestos/pollution claims;
- validate tax dates against the active rule table;
- compare narrative claims with structured fields;
- require reason and approver for every override;
- prevent internal notes from entering client output.

## 14. Security and data protection

- row-level case isolation and least privilege;
- encryption in transit and at rest;
- short-lived document links and multi-factor authentication;
- separate client/internal views;
- immutable audit trail;
- retention/deletion rules;
- export and subject-access capability;
- data minimisation and redaction;
- no model training on client files without an explicit basis;
- approved confidential-data routing.

## 15. Delivery roadmap

### Phase 0: Validate Sandra's process

Deliver:

- validated process and authority map;
- mandatory-document list;
- approved rule catalogue;
- source/licence inventory;
- editable template inventory;
- three anonymised historical cases with outcomes where possible.

Exit criterion: every report field has a named source or is explicitly professional judgement.

### Phase 1: Evidence-first MVP

Build case management, private upload, OCR/extraction with page citations, property record, verification, deterministic calculator, report template, approval and audit.

Exit criterion: reproduce the reference case's facts and arithmetic with Sandra approving all professional fields.

### Phase 2: Official enrichment and visit

Add SITG/RDPPF/Minergie enrichment, geospatial context, mobile checklist, photos, voice notes and specialist referrals.

Exit criterion: reduce preparation and transcription while retaining evidence.

### Phase 3: Comparable workbench

Add authorised listing capture/import, FAO/D&V transactions, duplicate detection, ranking, normalisation, approval and market charts.

Exit criterion: Sandra can explain the comparable set without a separate spreadsheet.

### Phase 4: Full valuation and report

Add rule engine, scenarios, release gate, client portal, bilingual PDF and mandate follow-up.

Exit criterion: prepare, review and issue the estimate in one workspace.

### Phase 5: Learning loop

Add outcome tracking, estimate-versus-sale analysis, rule performance and proposed recalibration.

Exit criterion: recommendations learn from verified D&V outcomes, with every rule change professionally approved.

## 16. MVP backlog

### Must have

- case and role management;
- secure uploads;
- OCR and structured extraction;
- page-level evidence;
- verification states;
- area calculator;
- versioned basic rules;
- manual comparable import;
- valuation scenarios and overrides;
- PDF report;
- release approval and audit log.

### Should have

- official-source enrichment;
- mobile visit workflow;
- comparable duplicate detection;
- source snapshots;
- tax-date calculator;
- bilingual output;
- client document-request page.

### Later

- licensed portal/feed integrations;
- advanced geographic scoring;
- outcome calibration;
- recommendation learning;
- CRM and e-signature integration.

## 17. Acceptance tests using Saut-du-Loup

The MVP must:

1. extract the address, acquisition, parcel/building/PPE references and source pages;
2. preserve 73 m² apartment, 11 m² loggia, 42 m² terrace and 250 m² garden separately;
3. calculate 92.36 m² exact and approved rounding to 92.5 m²;
4. calculate CHF 1,017,500 at CHF 11,000/m²;
5. calculate 5% as CHF 50,875;
6. add CHF 250,000 garden and CHF 50,000 parking;
7. reproduce CHF 1,266,625;
8. require approval of the four material assumptions;
9. flag possible parking double counting;
10. flag the fiscal-date inconsistency;
11. block release until mandatory decisions are approved;
12. generate a source-linked PDF matching the structured record.

## 18. Success measures

- preparation time per estimate;
- automatic extraction rate and verified accuracy;
- unresolved contradictions at release;
- comparable-table preparation time;
- evidence-linked content percentage;
- manual re-entry count;
- override frequency by rule;
- estimate-to-sale variance;
- asking-to-sale discount;
- time to mandate decision.

## 19. Immediate next actions

1. Validate the 24 process questions with Sandra.
2. Obtain the editable current estimation template.
3. Collect three different historical estimates and their outcomes.
4. Inventory spreadsheets, portal accounts and paid data.
5. Confirm use of historical cases for internal calibration.
6. Freeze v1 of weighting and adjustment rules.
7. Build the evidence-first MVP before broad market-data automation.
