# CYTRIA — From Data Intelligence to Commercial Value

Strategic productization audit · DigitalCOA / Cytria · 2 October 2026

My reading is that Cytria has the foundations of something commercially interesting, but its current presentation is too technology-centric. The next challenge isn't necessarily adding more intelligence. It's turning the intelligence already described into practical tools that estate agents immediately understand, use, appreciate and eventually become dependent on because those tools improve their everyday work.

There are two opportunities here:

1. Immediate value and the wow effect: Show agents something meaningful about their own territory, properties, clients or competitors that they couldn't easily establish themselves.
2. Long-term differentiation: Combine Cytria's market intelligence with the agency's proprietary information to create insights competitors cannot reproduce simply by obtaining the same public records.

And there is a third consideration: DigitalCOA should own the client relationship through continuous improvement, not just deliver a technically impressive application.

## 1. Domain classification

Business — product strategy, organizational adoption, data intelligence and client retention.

The business challenge operates across three distinct levels:

CYTRIA — Intelligence infrastructure

Public data · Notarial transactions · Market observations · Geospatial intelligence

AGENCY — Proprietary intelligence

Mandates · CRM · Offers · Visits · Sales history · Commercial expertise

DIGITALCOA — Applied decision tools

Better valuations · Better mandates · Faster matching · Client-facing reports · Actionable alerts

The opportunity is to make DigitalCOA the partner that translates those two data layers into business decisions while Cytria remains the reusable intelligence engine.

## 2. Surface interpretation — What has actually been achieved?

Based on the supplied strategic report, the technical groundwork is substantial. Importantly, I am distinguishing reported implementation from independently verified production readiness: I have the report, not the database, repository, live application, audit logs or executable tests.

### Reported existing assets

# 8,970

Notarial transactions

# 6,535

Transactions with values

# CHF 17.47B

Reported transaction value

# 2,183

Agency-attributed sales

# 83

Agencies profiled

# 93

Brokers profiled

Figures reported in the document, not independently audited. Coverage is identified as April 2025–September 2026.

The report also describes six implemented capabilities:

| Capability                        | Described status         | Practical significance                                    |
| --------------------------------- | ------------------------ | --------------------------------------------------------- |
| Notarial transaction explorer     | Implemented              | Understand actual transactions rather than asking prices. |
| Agency & competitor intelligence  | Implemented              | Understand geographic activity and market presence.       |
| Off-market opportunity detection  | Implemented              | Surface unusual transactions and potential leads.         |
| Land development analysis         | Implemented              | Screen parcels for possible development opportunities.    |
| Comparative Market Analysis (CMA) | Implemented              | Support property valuations with recorded transactions.   |
| Privacy masking & access controls | Implemented in some form | Separate public views from nominative information.        |

The report separately proposes five additional developments: multi-agency listing collision detection, building permit monitoring, corporate ownership graphs, mortgage stress analysis and an AI-generated investment memorandum.

Those five should not be treated as already delivered.

More importantly, the existing six capabilities differ significantly in their maturity requirements. A map can function while its source attributions are inaccurate. A valuation report can render successfully without being professionally defensible. We need to test the actual correctness of the underlying decisions.

## 3. Hidden interpretation — What is the real commercial asset?

The strongest part of Cytria is not its interface, a chatbot, or even its transaction count.

It's the potential to establish the chain:

Actual transaction → identified property → location → characteristics → market context → commercial action.

This is more meaningful than simply aggregating market statistics.

Consider what a typical estate agent works with:

- What the market is asking: advertised prices.
- What the agency knows: client relationships, visits, objections, offers and mandates.
- What actually happened: finalized transactions and recorded sale prices.

Cytria potentially closes the gap between those three worlds.

That unlocks questions such as:

- Are we pricing our mandates consistently with actual sales?
- Which properties in our portfolio deserve a pricing review?
- Which of our buyers may now be suited to an opportunity?
- Where are our competitors completing transactions?
- What can we demonstrate to a prospective seller to earn their confidence?

The major strategic shift I would make:

> Don't sell access to Geneva real estate data. Sell better commercial decisions, supported by evidence that the agent can explain to a client.

A technical terminal is useful to an analyst. A defensible valuation, an early alert or a meaningful client conversation is useful to an estate agent.

1. Key blind spots — Before presenting this to a paying client
I found several issues that deserve attention. Some are primarily about reliability; others are about commercial credibility or security.
Finding Assessment Implication
Hardcoded vault key Critical The report describes unlocking nominative records through a shared key or URL parameter. That is not adequate client-grade access control.
CASATAX threshold Incorrect The report uses CHF 1.417M. The 2026 official threshold is approximately CHF 1.394M.  ge.ch
Agency attribution Unverified The 2,183 matched sales require sampling, confidence scores and explicit treatment of multiple mandates.
Market coverage Inconsistent The stated April 2025–September 2026 coverage is roughly 18 months, while some metrics are described as covering 24 months.
Certified valuations Unsupported Transaction quartiles alone cannot establish a certified valuation or fully account for property condition, micro-location, rights and characteristics.
Residual building rights Preliminary Density calculations must account for applicable restrictions and parcel-specific conditions.
Seller motivation signals Sensitive Succession status or anomalous sale prices do not reliably prove financial distress or willingness to sell.
Mortgage intelligence Proposed Cash purchases, actual lending and leverage cannot be identified from a transaction price alone.
Three findings particularly concern me.
First: security. Masking names in an interface is not the same as anonymization or access control. If the reported vault mechanism is active, it should be disabled or secured immediately, with proper server-side authentication, individual permissions and audit logging. The Swiss data protection framework specifically emphasizes protection by design and by default.

FDPIC
+1

Second: permission to commercialize sources. SITG distinguishes unrestricted commercial datasets (A) from datasets requiring authorization (A*) and restricted datasets (B). Cytria must track licensing and attribution for each dataset, not assume that public accessibility permits commercial reuse.

Catalogue SITG

 The FAO also deliberately restricts public online consultation to the latest two years for data-protection reasons. That warrants a separate retention and reuse assessment before commercial deployment.

ge.ch

Third: professional confidence. The report mentions real sales, identified intermediaries and automated valuations. These are commercially powerful assertions, but errors in them are more damaging than errors in a conventional dashboard.
I would create a small validation set of actual deeds, properties, agency-attributed sales and valuations before any live demonstration. Display the source, date, sample size, uncertainty and whether a result is observed, calculated or inferred.
5. Hidden assumptions — Which tools should Cytria become?
This is where I would make the biggest change.
Don't build six independent applications with six databases and six authentication systems. Build one Cytria engine with small, independently accessible workflows.
Each micro-app should solve one recognizable problem.
Recommended product portfolio
SCORES BELOW ARE MY PRODUCT-PLANNING ASSESSMENTS, NOT MEASURED CUSTOMER RESULTS.

01. Cytria VALUE
First pilot

Property valuation & seller presentation
Input an address and produce an explainable appraisal with relevant recorded transactions, asking-price context, a map and an agency-branded seller report.
Wow moment: The agent can say “Here is what actually sold around your property, not just what is advertised.”
Users: Valuation agents, managers, sellers · Agency data: condition, previous sales, valuations, mandate feedback · Effort: Low–medium

01. Cytria TERRITORY
Hyperlocal market intelligence
Select a commune, neighborhood or drawn territory to understand actual transactions, geographic trends, price dispersion and agency activity.
Wow moment: Reveal insights about the specific streets where an agent already works.
Users: Agents, managers · Agency data: own sales, catchment areas, lost mandates · Effort: Low

02. Cytria MANDATE
Seller management & portfolio intelligence
Evaluate active listings against recent comparables and agency history. Produce seller updates, price-review evidence and follow-up recommendations.
Wow moment: Identify a mandate that merits review and generate a credible seller conversation in seconds.
Users: Listing agents, branch managers · Agency data: listings, visits, offers, reductions, seller feedback · Effort: Medium

03. Cytria MATCH
Buyer-to-property matching
Match active buyers to internal mandates, with comparative price evidence and explanations of fit.
Wow moment: An existing buyer is connected to a previously overlooked listing, with a clear explanation of why it meets their requirements.
Users: Sales agents · Agency data: buyer searches, qualifications, CRM, listing availability · Effort: Medium

04. Cytria PULSE
Market & competitor monitoring
A concise weekly digest of actual sales, relevant local changes and verified competitive activity in the agency's areas.
Wow moment: Show three concrete developments worth discussing at the next sales meeting.
Users: Managers, agents · Agency data: strategic territories, team portfolios, own results · Effort: Low–medium

05. Cytria LAND
Developer & investment screening
Assess a parcel, relevant zoning information, nearby transfers and possible development constraints. Eventually incorporate authorizations.
Wow moment: Reveal a non-obvious parcel opportunity, accompanied by official evidence and explicit limitations.
Users: Developers, investment specialists · Agency data: feasibility assessments, construction costs, yield targets · Effort: High

The images above illustrate product directions, not screenshots of implemented Cytria tools.
My deployment order
Indicative business value versus implementation effort
Qualitative prioritization: estimated from the described capabilities and expected agency data integration. Requires validation with the actual client.
I'd introduce VALUE and TERRITORY first, then move toward MANDATE and MATCH once the agency contributes its own information. PULSE makes sense as a lightweight recurring service. LAND deserves a specialist audience and a separate quality-assurance process.
This sequence avoids the trap of building ever more functionality before anyone becomes a regular user.
6. Organizational dynamics — Where the agency's proprietary information changes everything
This is probably the most commercially important section of the analysis.
Cytria's public-data foundation can provide similar information to every agency. It is the agency's own history, relationships and operational knowledge that make the product unique.
Consider the difference:
Agency-owned information What combining it with Cytria makes possible Added business value
Historical mandates, including closed and lost cases Compare initial listing prices, revisions and actual transaction outcomes where reliably matched. Improve valuation discipline.
Offers and negotiations Understand which pricing ranges and property characteristics attracted real offers. Improve negotiating evidence.
Viewing history and buyer feedback Explain why a mandate is attracting attention without progressing. Support meaningful seller updates.
Buyer requirements and qualified prospects Match current buyers against the agency's property portfolio. Unlock opportunities in the existing CRM.
Historical contacts and consent records Re-engage known clients when a genuinely relevant property or market update appears. Improve retention and repeat business.
Agent territories and areas of expertise Compare internal coverage with transaction patterns. Improve geographic focus.
Marketing activity and advertising spend Compare promotion, qualified inquiries, offers and sales outcomes. Improve campaign spending decisions.
Actual property conditions and renovations Improve comparable-property selection and adjustments. Produce more defensible valuations.
Reasons for lost mandates Identify pricing or service factors associated with unsuccessful acquisition attempts. Improve future mandate acquisition.
Manager-validated local knowledge Flag misleading comparable records and document local exceptions. Accumulate agency-specific expertise.
The proprietary-data multiplier
Take a single property.
PUBLIC CYTRIA INTELLIGENCE
Comparable sales around a villa
Recorded prices, dates, parcel characteristics, approximate proximity and building information.

PRIVATE AGENCY INTELLIGENCE
What happened during commercialization
Asking-price changes, number of qualified visits, buyer objections, condition observations, offers and actual result.

AGENCY-SPECIFIC INTELLIGENCE
Explainable pricing recommendation
Market evidence + observed buyer response + property-specific adjustments + uncertainty + recommended agent review.

This is the difference between knowing a house sold for CHF 2.4 million and understanding how its characteristics, pricing history and buyer response contributed to the commercial outcome.
The second is much harder to reproduce.
What data would I request from the client initially?
Not their entire CRM. That creates friction, privacy exposure and integration work before value is proven.
I'd request just three controlled exports:
First data import Minimum useful fields
Mandates Agency property ID, address, type, surface, rooms, listing dates, prices, status, agent, renovations/condition if known.
Sales history Property ID, initial/final asking price, accepted and closing price where known, important dates, number of visits/offers.
Buyers (optional, later) Pseudonymous buyer ID, preferred municipalities, budget, type, size, essential criteria, contact eligibility.
The first two are enough to attempt something unusually valuable: a Pricing Intelligence Audit, comparing an agency's past mandate decisions with independently recorded transactions.
Technically, I would reconcile data using property and parcel identifiers where possible (EGRID, EGID, PPE/unit references), not addresses alone. Every match should retain its source, confidence and review status.
One distinction matters: customer knowledge belongs to the agency. Each agency should retain control over its private data and any sharing or cross-client model reuse must require a separate, explicit agreement. Cytria can provide shared market facts without sharing one agency's private commercial intelligence with another.

## 7. Power, roles and identity — How the agency will perceive Cytria

There's an important organizational dimension here.

An agency director, a senior broker and a junior commercial agent do not necessarily interpret the same information in the same way.

| Stakeholder             | What they want                                                       | What could create resistance                                   |
| ----------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------- |
| Agency owner / director | More mandates, better sales performance, visibility.                 | Paying for a tool nobody uses.                                 |
| Senior broker           | Better information, quicker valuations, stronger client credibility. | Feeling that algorithms challenge professional judgment.       |
| Junior agent            | Faster preparation, local knowledge, better follow-up.               | Complex interfaces and unreliable recommendations.             |
| Marketing / operations  | Reliable reporting, market content, performance intelligence.        | Duplicate data entry and additional systems.                   |
| Sellers / buyers        | Transparent, convincing evidence, confidence in the advice.          | Automated valuations presented without sufficient explanation. |

This matters particularly for Agency BI.

Cytria currently describes broker profiles, agency rankings, activity velocity and territorial competition. This could be useful to management but also be perceived by agents as surveillance or as criticism of their commercial performance.

I would avoid making league tables the centerpiece of the client experience.

Instead, let agents challenge, correct and enrich the information. Make them the experts who interpret the data, rather than subjects being judged by it.

The same principle applies to DigitalCOA. A good first impression might secure a demonstration, but preserving the agency's professional autonomy is more likely to sustain adoption.

## 8. Systemic loops — How to create recurring value

Cytria's long-term advantage depends on the operational feedback loops it creates.

The positive intelligence loop

1

Cytria detects market changes

2

The agent receives relevant evidence

3

The agent takes a commercial action

4

The agency records feedback and outcomes

5

Future recommendations improve

Feedback returns to the agency's intelligence layer.

Three potential negative loops should also be anticipated.

- Noise loop: Too many weak signals lead to ignored alerts, then disengagement.
- Trust loop: One highly visible incorrect transaction attribution or valuation undermines confidence in everything else.
- Administrative loop: Agents must enter more information than they get back in value, so data quality deteriorates.

The solution isn't another AI agent or another dashboard. It's tightly scoped workflows, fewer notifications, transparent evidence and feedback capture that happens naturally during normal work.

For example, a weekly Cytria Pulse should not be a generic market newsletter. It should report something like:

> Three relevant transactions occurred in your operating area this week. Two may affect active mandates. One warrants a pricing review.

Each item should link to the relevant evidence, the agency property and a possible action.

That's a service worth opening every Monday.

## 9. Contradictions and tensions in the current concept

The report exposes some tensions that I would resolve before deciding on further development.

Sophistication versus trust. There are several sophisticated calculations, such as agency attribution, seller-motivation identification and residual building rights. However, the report does not document precision, recall, valuation error or operational testing. Impressive complexity without measurable reliability can weaken the product.

Data sovereignty versus access design. A local SQLite database may keep storage under control, but sovereignty also requires access security, clear ownership, recovery and responsible handling of personal information. The described master-key approach is inconsistent with this objective.

Exhaustive intelligence versus incomplete coverage. The report characterizes the database as exhaustive while also distinguishing total transactions, valued records and agency-attributed sales. Those are different populations. Their coverage and limitations must be explicit.

General market intelligence versus proprietary value. The report emphasizes sources that others can potentially collect. That provides an initial product but doesn't by itself establish enduring competitive differentiation.

Advanced AI versus commercial simplicity. An automated 10-page investment memorandum sounds impressive, yet a one-page seller argument supported by five carefully selected comparables may deliver more immediate value.

There is also a practical concern with parcel-development calculations. Geneva's public RDPPF system documents restrictions involving zoning, alignments, heritage, groundwater and other conditions. These must be considered before treating density calculations as buildable capacity.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://sitg.ge.ch\&sz=32)

Catalogue SITG

+1

The recurring pattern: Cytria appears to have prioritized analytical possibilities over validating specific, repeated agency decisions.

That's a hypothesis about product development priorities, not evidence that the implementation has failed.

## 10. Three alternative interpretations of the business opportunity

I see three commercially distinct ways to package the technology.

A. Cytria as a market-intelligence subscription

A recurring product providing transaction data, charts, agency analytics and market reports.

Revenue comes primarily from access to the data and tools.

Trade-off: Relatively standardized and scalable, but value depends on continually maintaining a data advantage and product adoption.

B. Cytria as a white-label agency toolkit

Small branded applications and PDFs for valuations, sellers, buyers and managers.

Revenue comes from agency subscriptions, implementation and specific modules.

Trade-off: Clearer day-to-day use cases but requires excellent user experience, reliable reporting and agency-specific configuration.

C. DigitalCOA as the agency's intelligence partner

Cytria supplies the market layer. DigitalCOA integrates proprietary workflows, CRM exports, analytics, automations and human decision processes.

Revenue comes from initial implementation and recurring, outcome-driven improvement work.

Trade-off: Strong potential for relationship depth and customization, but greater consulting and maintenance responsibility.

I would pursue B as the customer-facing experience and C as the service model, both powered by the same standardized Cytria data infrastructure.

That avoids turning DigitalCOA into a generic data reseller while keeping delivery manageable.

## 11. Most constructive meaning — Design the wow effect around the client's work

The strongest demonstration would not start with an 8,970-point map or a long explanation of the ingestion architecture.

I would start with a property the client knows extremely well.

### The five-minute demonstration

ILLUSTRATIVE PROTOTYPE

## Cytria VALUE

Confidential agency workspace

Property address

Agency property / Geneva

[Fin du gel en zone villa: de nouvelles exigences pour préserver la qualité de la zone villa | ge.ch](https://images.openai.com/static-rsc-4/zvWh4aN6PyPfWfYXDzX8853cRGjnEfbWsx_Ze97pPYsgKIyEDhx2q49svw-AcqK-T8JTWWHTPR0Nkd7bf5CBztFyHhe6nAGroLTUQOZnQrEPuu--Qgy3L-19fh5GxzwKJyvzn1grrU6KdXPoM9UrXkg1HVdTvcMqnA6RVAVwsAU?purpose=inline)

[ge.ch](https://www.ge.ch/document/fin-du-gel-zone-villa-nouvelles-exigences-preserver-qualite-zone-villa)

01

Actual sales

Recorded comparables

02

Differences

Property adjustments

03

Conclusion

Explainable estimate

Seller-ready report

Comparable sales • Evidence • Expert notes • Agency branding

Conceptual experience, not a live screenshot or a computed valuation.

The demonstration narrative:

Minute 1 — Recognition. Ask the director or broker for a property they personally know.

Minute 2 — Discovery. Display recent transactions nearby, explain which are genuinely comparable and which have been excluded.

Minute 3 — Surprise. Introduce an agency-specific observation: for example, how its original asking price compares with final transactions or actual buyer feedback. This requires its supplied data.

Minute 4 — Utility. Show the valuation reasoning, uncertainty, sources and what might justify adjusting the estimate.

Minute 5 — Tangible outcome. Produce an agency-branded report for a seller appointment.

This creates a different reaction from showing software functionality.

Instead of saying, “Interesting platform,” the broker can start thinking, “I can use this at my next valuation appointment.”

That distinction matters.

### Three useful forms of wow

1. Discovery: Something previously unknown about a familiar property or territory.
2. Credibility: Evidence that can strengthen an argument in front of a seller.
3. Acceleration: A task that used to require manual research is prepared in seconds, with the agent retaining final judgment.

I'd aim for all three, without overstating data accuracy.

## 12. Actionable shifts — Execution, satisfaction and future relationship

I'd organize the next stage as a short pilot with clear acceptance criteria, rather than opening another major software-development cycle.

### Phase 1 — Establish that the intelligence is trustworthy

WEEK 1 · TECHNICAL AND DATA VALIDATION

Audit the actual app and data rather than relying on its strategic report.

- Validate sampled transaction records and original FAO sources.
- Test agency attribution against known closed sales.
- Assess coverage, dates, missing fields and questionable comparables.
- Validate zoning and price-per-square-meter assumptions.
- Replace insecure vault access and assess data licenses, privacy and retention.
- Confirm whether the existing CMA can produce a defensible report.

Deliverable: A small evidence-backed quality report and a list of functions safe to demonstrate.

### Phase 2 — Build one complete customer experience

WEEK 2 · FIRST USABLE PRODUCT

Choose Cytria VALUE.

The user journey should be no more complicated than:

1

Select property

2

Inspect comparables

3

Adjust property-specific facts

4

Review valuation reasoning

5

Generate seller report

The interface should follow a restrained Swiss-grid design: minimal navigation, strong typography, highly readable maps and tables, no decorative AI jargon, and meaningful source labels.

No new general-purpose chat assistant is required. Use deterministic queries for figures and AI selectively to explain evidence or draft reviewed reports.

### Phase 3 — Add the client's private intelligence

WEEK 3 · AGENCY DIFFERENTIATION

Import a small historical mandate sample. Test how well it reconciles with Cytria. Add original asking prices, subsequent revisions and selected outcomes.

The objective is to demonstrate at least one agency-specific insight that would not exist without that private data.

This is when the platform becomes their version of Cytria, not simply Cytria with a different logo.

### Phase 4 — Create recurring usage

WEEK 4 · ADOPTION AND RETENTION

Introduce a limited Cytria Pulse for one territory and link it to existing work: active mandates, valuation appointments or management reviews.

Collect explicit agent feedback, including corrections and rejected recommendations. Measure whether agents use the resulting intelligence in client conversations.

### Pilot success measures

Transaction reliability

Source records reconciled, uncertainties documented

Time saved

Time to prepare a valuation before vs. after

Useful output

Share of tested reports agents approve for client use

Commercial actions

Documented pricing reviews or client meetings informed

Repeat adoption

Weekly use without prompting or compulsory reporting

Satisfaction

Qualitative confidence and perceived usefulness

I would set numerical acceptance thresholds with the pilot agency, based on its existing workflow. Inventing efficiency or conversion claims before measuring them would undermine the very credibility Cytria is intended to establish.

### Commercial packaging for DigitalCOA

| Offering                      | Client receives                                                                | DigitalCOA relationship                                  |
| ----------------------------- | ------------------------------------------------------------------------------ | -------------------------------------------------------- |
| Discovery / proof             | Personalized territory and property demonstration using validated public data. | Earn attention and identify a concrete business problem. |
| Agency pilot                  | Branded VALUE tool, limited private-data integration and training.             | Demonstrate measurable usefulness.                       |
| Ongoing intelligence          | Maintained data, PULSE alerts, reports, support and quality monitoring.        | Recurring engagement and reliability.                    |
| Agency intelligence expansion | MANDATE, MATCH, deeper integrations and specialist analytics.                  | Long-term development linked to operational needs.       |

These are commercial packaging suggestions, not existing Cytria products or validated prices.

### What I would deliberately postpone

I would not prioritize the ownership graph, automated mortgage classifications, autonomous deal sourcing, or AI investment memoranda yet.

Nor would I build a new agent framework, a complicated RAG infrastructure, or a standalone application for every feature.

Maintain the existing transactional backbone where it is adequate. Add structured joins and agency-specific permissions, then expose only the workflows people actually need. Before a multi-agency launch, tenant separation, auditability and backup/recovery must be production-ready.

## Final synthesis

I think the commercial opportunity is larger than the scope currently emphasized in the report, but it requires simplifying rather than expanding the technology.

Here is the distinction I would use to guide development:

|                        | Current report emphasis           | Proposed commercial emphasis                     |
| ---------------------- | --------------------------------- | ------------------------------------------------ |
| Core identity          | Real estate intelligence terminal | Agency decision-support toolkit                  |
| Primary differentiator | Public transaction coverage       | Public evidence + agency knowledge               |
| Demonstration          | Data volume and analytical power  | Insight about the client's own property          |
| Daily relevance        | Market exploration                | Valuations, mandates and buyer matching          |
| Client value           | Access to information             | Better-informed actions and faster preparation   |
| Recurring relationship | Data and feature updates          | Continuous intelligence and workflow improvement |
| DigitalCOA role        | Technology builder                | Integration, adoption and intelligence partner   |

The commercial architecture I would preserve

Illustrative simplified architecture. Other modules such as MATCH, TERRITORY and LAND use the same core rather than separate infrastructure.

My central recommendation: Use Cytria to win attention with validated, hyperlocal evidence. Use the agency's proprietary information to create genuinely unique intelligence. Use DigitalCOA to make that intelligence operational and continuously valuable.

The long-term differentiation isn't simply the number of records. It's the combination of reliable evidence, proprietary context, practical workflows and user trust.

### The next concrete step

I recommend conducting a Cytria Product Readiness & Value Extraction Audit against the actual repository and database. The supplied report is a good inventory, but it does not prove that the interfaces work correctly, that agency attribution is dependable, or that the valuation outputs are suitable for clients.

That audit should produce three specific deliverables: a reuse-versus-fix inventory, an implementation specification for Cytria VALUE, and the minimum agency-data import schema needed to demonstrate proprietary intelligence. These would give you a practical path from what is already built to a client-ready pilot without unnecessary re-architecture.

# CYTRIA — Complete Evidence, Sources & Decision Rationale

DigitalCOA / Cytria · Analysis provenance and strategic decision audit · 2 October 2026

I'll reconstruct the previous assessment as an evidence and decision dossier, including the source material, factual verification, analytical frameworks, expert perspectives, assumptions, product choices, alternatives, risks, proposed artifacts and validation methods.

One important distinction: I can provide the evidence, explicit calculations, assumptions, decision criteria and a detailed explanation of how the conclusions were reached, rather than an internal, verbatim thought-by-thought transcript. That makes the assessment reproducible and, more importantly, open to challenge.

## 1. What actually went into the previous analysis

There were three layers of input.

A. Primary evidence — Your Cytria strategic report

The 142-line document Cytria — Rapport Stratégique, which describes the database, data collectors, six application capabilities, source systems and five future modules.

Evidence level: Directly documented claims about Cytria, not independently tested implementation.

B. External verification — Official Swiss sources

Geneva government pages, SITG data-access rules, the Swiss Federal Data Protection and Information Commissioner, the official property-restrictions cadastre, and related regulatory material.

Evidence level: Independent support for particular legal, regulatory or data-source facts. These sources do not establish whether Cytria implements the requirements correctly.

C. Business and technical interpretation

Product design, agency workflows, market positioning, proprietary-data integration, adoption, information architecture, risk analysis and prioritization.

Evidence level: My synthesis and proposed hypotheses. These are not externally validated findings about what Geneva estate agents will purchase.

### What I did not use

The previous assessment did not include access to the live SQLite database, application source code, functional tests, performance logs, Cytria user analytics, a client CRM, financial accounts or interviews with estate agents.

Nor did I launch independent specialist AI agents. The different expert perspectives were analytical lenses within one assessment.

The diagrams, product illustrations, priority matrix and simulated UI presented previously were explanatory or conceptual artifacts. They were not production screenshots, functioning prototypes or outputs generated by the Cytria codebase.

This distinction is important because a documented capability, a working capability, a validated capability and a commercially valuable capability are four different things.

## 2. The main evidence-to-conclusion map

This is the central traceability table behind the prior recommendation.

| Original observation                                              | Interpretation / rationale                                                    | Conclusion                                                    |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 8,970 recorded transactions with cadastral enrichment.            | Potentially substantial reusable market-data infrastructure.                  | Preserve Cytria as a shared intelligence engine.              |
| 6,535 valued acts, rather than all 8,970.                         | Financial coverage is incomplete.                                             | Show data availability and missing-value rates explicitly.    |
| 2,183 agency-linked sales.                                        | Competitive analysis depends on matching accuracy.                            | Validate before making agent- or agency-level claims.         |
| A CMA simulator and printable report already exist.               | This is closest to a recognizable, client-facing agency task.                 | Start by productizing VALUE, rather than inventing a new app. |
| Geographic maps and neighborhood filters exist.                   | Much of TERRITORY can reuse the existing interface and queries.               | Low additional build complexity is plausible.                 |
| No agency-owned CRM or mandate-history integration is documented. | Public data cannot explain much of the agency's commercial process.           | Add a private agency intelligence layer.                      |
| Competitor rankings and sales velocity are prominent.             | Management metrics may not translate directly into daily adoption by brokers. | Organize applications around jobs rather than dashboards.     |
| Master-key access and nominative data are described.              | Personal-data access needs more than display masking.                         | Audit and redesign authorization before client deployment.    |
| Five advanced modules remain proposed.                            | Their dependencies, accuracy and value remain unverified.                     | Avoid expanding scope until the existing product is tested.   |

Every observation in this table comes from the supplied report. The implications and priorities are my interpretations, not claims that the report itself establishes.&#x20;

Pasted text.txt

Pasted text.txt

1. The external sources, what each establishes, and why I used it
Here are the principal independent references. I've rechecked them against the official sources.
Source What it establishes Why it matters for Cytria
Geneva — CASATAX 2026 The 2026 price limit is CHF 1,394,928, with other eligibility requirements.  ge.ch +1 The document's CHF 1,417,000 threshold must be corrected and calculations made year-aware.
SITG — Data-use conditions Level A allows commercial use with conditions and attribution; A* requires authorization; B is restricted.  Catalogue SITG +1 Cytria needs a source-by-source commercial licensing inventory.
Geneva — FAO Public online consultation is limited to publications from the preceding two years for data-protection reasons.  République et canton de Genève Collection, long-term retention and reuse require a separate legal assessment.
PFPDT — Revised Swiss Data Protection Act Privacy by design and by default, alongside appropriate data-protection measures.  FDPIC Interface masking alone does not establish compliant processing or secure authorization.
Geneva — RDPPF Property use is subject to multiple applicable restrictions, not simply zoning coefficients.  ge.ch +1 The LAND module needs more than its reported density formula.
Swiss RegBL lookup Official building characteristics are available, but this public lookup explicitly prohibits robots.  delimo.bfs.admin.ch Cytria must confirm its actual acquisition channel is permitted; other authorized distribution options need checking.
FINMA — Mortgage financing Creditworthiness assessment is principles-based, with banks exercising their own lending policies within regulatory requirements.  FINMA A generic affordability scenario cannot reveal an actual buyer's mortgage or cash-financing status.
The downloadable dossier includes the full source bibliography, additional official references and direct links.
A central distinction is that these sources verify rules, official data definitions and relevant constraints. They do not verify that Cytria has correctly implemented its own data collection, analysis, security or compliance.
2. The expert perspectives and analytical methods
Here is how the different interpretations contributed to the assessment. These were analytical perspectives, not independently launched agents.
Expert perspective Question applied Contribution to the conclusion
Data engineering Is the data trustworthy, complete and correctly joined? Identified unverified counts, coverage and attribution.
Real estate practitioner What can an agent actually use in a meeting? Informed VALUE, TERRITORY, MANDATE and MATCH.
Product and UX Can each capability solve one complete task? Led to small, focused applications rather than more dashboards.
Security and privacy What happens if personal information or property claims are wrong or exposed? Established pre-launch validation requirements.
Organizational psychology How might directors, brokers and operations perceive the tools? Identified possible resistance to rankings and additional reporting work.
Systems thinking What improves or undermines long-term adoption? Produced the trust, feedback and administrative-burden loops.
Business strategy Why would the agency continue paying DigitalCOA? Led to the proprietary-data layer and ongoing intelligence-service model.
Hermeneutics What does the report emphasize, assume, omit or characterize too confidently? Exposed the difference between technical accomplishment and demonstrated business value.
The hermeneutic interpretation
The report presents Cytria largely through what the system can collect, process and infer.
Its prominent concepts include sovereignty, exhaustiveness, certified valuations, competitive scoring and increasingly advanced analytical intelligence.
Those concepts express a coherent technological ambition. But they also reveal an important omission: the document rarely demonstrates what a specific agent can do better tomorrow morning, or whether the agent has actually done it.
That is why I reframed the problem around the user and their workflow.
This was not evidence that the developer had chosen the wrong priorities. It was an interpretation of the report's framing, requiring verification against the actual product and the intended customer.
3. The detailed rationale behind the most important conclusion
My proposal was:
A shared Cytria intelligence engine + small task-oriented tools + proprietary agency data + recurring DigitalCOA services.
The rationale has four parts.
A. Why keep the intelligence engine shared?
The report describes one transaction database, one enrichment mechanism and several applications that rely on overlapping information.
For example, a single validated sale could contribute to a neighborhood map, a valuation, an agency activity summary and an alert about a nearby mandate.
Creating independent databases for each function risks unnecessary duplication, inconsistent results, multiple source updates and more security boundaries to maintain.
This is an architectural inference, though. It would need revision if the actual deployment requires physical database isolation or the current architecture cannot enforce client permissions reliably.
B. Why start with VALUE?
The report says Cytria already has a comparative valuation workflow, configurable search radii and printable dossier generation.
Pasted text.txt

So VALUE was not selected because valuation is necessarily the most profitable real estate application.
It was selected because:

- The core functionality is reportedly already present.
- The output can be examined against real properties and completed transactions.
- The agent has an obvious use for it: preparing a seller discussion.
- A finished report provides a tangible product demonstration.
- The first version need not integrate an entire private CRM.
The main counterargument is that the reported valuation model may not be reliable enough. Simple geographic quartiles may ignore property quality, transaction context and insufficient sample sizes.
If an independent test showed poor comparable quality, I would change the deployment order. TERRITORY or a more carefully curated transaction report could become the first product.
C. Why proprietary agency data?
A public notarial record can establish a reported transaction price.
It generally cannot establish the full commercial process that preceded that sale: the original asking price, the visits, objections, offers, negotiations, marketing choices or seller expectations.
The agency may have that information.
Consider a hypothetical property:
Field Information
Initial asking price CHF 2.75M
Subsequent asking price CHF 2.59M
Final transaction CHF 2.45M
Qualified visits 18
Offers 3
Buyer objections Condition and expected renovation cost
Entirely illustrative example — not an actual Cytria or agency record.
Cytria's public layer supplies the market outcome and comparable transactions. The agency's internal records explain aspects of the marketing and negotiation process.
The combination could improve future valuation discussions. However, one case would not establish that the initial price caused slower sales or that the same pattern generalizes to other properties.
The agency data creates additional explanatory context, not automatic proof of causality.
This is also why I suggested three small CSV imports instead of implementing a full CRM synchronization immediately.
D. Why an ongoing DigitalCOA relationship?
A database can be sold as software access.
But reliable client-specific intelligence requires additional activities: correcting data, managing permissions, understanding local business practices, training agents and verifying whether recommendations are useful.
DigitalCOA could provide those services.
The economic hypothesis is that clients will value and retain a service that consistently improves meaningful workflows.
That still needs testing through actual usage, support costs, willingness to pay and retention. None of those have yet been established.

6. How I arrived at the six product slices
Each proposed tool was created by identifying a distinct user task and mapping it back to existing or missing functionality.
Product Primary user question Reuses reported Cytria capabilities What still needs development
VALUE What evidence supports this valuation? Transactions, comparables, reports Validated comp selection, adjustments, professional review
TERRITORY What is happening in my area? Maps, communes, filters, agency observations Saved territories, clear reporting, focused UI
MANDATE Which listings require attention? Market comparisons Private listings, price history, offers, follow-up
MATCH Which current buyer fits which property? Property information and market context Buyer preferences, CRM linkage, matching rules
PULSE What changed that requires action? Dates, locations, market events Relevance filters, alerts, feedback
LAND Which parcels warrant investigation? Cadastre, zoning, density estimates Regulatory checks, professional validation
The proposed implementation-effort positions were qualitative estimates based on apparent reuse and dependencies.
They were not measured engineering estimates, and no actual client provided value scores. The positioning needs confirmation against the source code and a representative customer workflow.
2. What could overturn the recommendations?
This is particularly important because it separates a defensible working hypothesis from a predetermined conclusion.
If we discover… Then the interpretation changes
The current CMA is unreliable. Do not make VALUE the first client-facing product.
The client has an excellent CRM and clean historical mandates. MANDATE or MATCH may offer a faster demonstration of differentiated value.
The client is a specialist developer. LAND may deserve priority after expert validation.
The real agents rarely use dashboards. Focus on reports or tools embedded in their existing systems.
Private-data integration is expensive. Prefer standardized tools until commercial justification exists.
Market data has licensing restrictions. Adjust the product scope, permissions or commercial model.
Agents do not return after the demonstration. Revisit the use case and adoption approach before building new modules.
DigitalCOA support costs exceed recurring revenue. Simplify implementation and reconsider service pricing or target clients.
This is the logic behind the recommendation to run a small, measurable pilot before building the proposed advanced modules.
3. Which artifacts exist, and which were proposed?
The previous answer contained conceptual diagrams, an illustrative interface, a qualitative effort/value matrix and a proposed four-week plan.
It did not create a working application, execute the Cytria data pipeline or produce a tested valuation.
The complete dossier now adds a concrete definition of the evidence artifacts needed to continue.
Artifact Purpose Status
Source and licensing register Establish rights and provenance for each data source Proposed
Transaction-quality report Verify coverage, completeness and accuracy Proposed
Agency-attribution validation Test whether attributed sales are correct Proposed
Security and authorization review Confirm access controls and data protection Proposed
VALUE functional specification Define the complete appraisal workflow Outlined in dossier
Agency import schemas Define minimum private data requirements Outlined in dossier
Pilot acceptance criteria Determine whether the tool is ready to deploy Outlined in dossier
Adoption and satisfaction scorecard Test actual usefulness and repeat engagement Outlined in dossier
Evidence and decision dossier Explain previous conclusions and assumptions Created now
Claim traceability matrix Map conclusions to sources and missing validation Created now
4. Complete working documents
I've assembled two downloadable files so this can become part of your Cytria project documentation rather than remain scattered throughout a conversation.
CYTRIA — Evidence & Decision Dossier
A detailed 451-line Markdown document with source bibliography, report inventory, numerical checks, assumptions, explanatory rationale, product specifications, six specialist-review prompts, proposed architecture, validation methods, organizational analysis and conditions that would reverse the recommendations.
Download the complete Markdown dossier

CYTRIA — Claims Traceability Matrix
A machine-readable CSV with 26 claims and recommendations, their source origins, original report lines, official reference URLs, evidence status, uncertainties and proposed verification.
Download the evidence matrix (CSV)

Both generated artifacts were checked for file presence; the CSV structure was validated with 26 entries and eight fields per entry.

 1. How to use the specialist perspectives without overengineering Cytria
The dossier includes detailed instructions for six specialist reviews. They are intended to run sequentially or independently against actual evidence, not as a permanently operating multi-agent framework.
I would begin with a data engineer and a security/privacy reviewer, because they can establish whether the product's underlying claims are defensible and whether a customer demonstration can safely proceed.
Then a real estate valuation reviewer should test the comparative analysis using a blind historical sample. Only after that should a product/UX reviewer assemble the first seller-facing experience.
CRM integration and commercial testing should follow once the core demonstration passes its basic validation checks.
This keeps the approach aligned with your preference for controlled, relatively simple, low-overhead systems.

 2. Updated conclusion
Having reconstructed the evidence, my main commercial proposal remains the same, but its limitations are now more explicit.
The documented asset: Cytria appears to have substantial data collection, normalization and analysis capabilities.
The unproven elements: Data completeness, accuracy, source permissions, actual security controls, defensible property valuations, agent satisfaction and willingness to pay.
The central opportunity: Translate the reportedly existing capabilities into small, useful agency workflows, then enrich those workflows with proprietary agency knowledge where permissions and data quality permit.
The unresolved decision: Which particular workflow creates the greatest value for the first real paying client? The report alone cannot settle that question.
 3. Recommended next step
I recommend treating the two attached documents as the starting point for a read-only technical and commercial due-diligence exercise.
Use the claim matrix as the audit checklist, then inspect the real repository and a sanitized database snapshot. The first objective should be to convert every significant reported capability into one of four outcomes: verified, verified with limitations, contradicted, or still untested.
That would give you something considerably stronger than another strategic opinion: a documented, evidence-backed foundation for deciding exactly what Cytria and DigitalCOA should commercialize first.
