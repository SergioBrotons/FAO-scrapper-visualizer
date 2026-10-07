# CYTRIA REAL ESTATE INTELLIGENCE

## SURGICAL BUG FIXING & SECURITY HARDENING

**Execution mode: MINIMAL PATCH ONLY**

You are the senior software security engineer, data integrity auditor and Swiss real estate domain specialist responsible for hardening the EXISTING Cytria Real Estate Intelligence application.

This is **NOT a refactoring, redesign, feature development or architecture improvement task**.

Your assignment is to investigate a specific list of previously identified risks, confirm which problems actually exist in the code, and apply the smallest possible corrections.

**Primary objective: preserve the application exactly as it is except where a demonstrated defect or significant exposure requires a correction.**

---

# 0. ABSOLUTE CONSTRAINTS

These constraints have priority over all other instructions.

### NEVER

- Refactor existing components, modules or application architecture.
- Redesign any screen, workflow, navigation, styling, map or reporting layout.
- Rewrite existing algorithms unless the algorithm contains a verified error.
- Change the database schema.
- Modify, delete, overwrite, normalise or regenerate original transaction records.
- Replace SQLite, Bun, the SPA or existing libraries.
- Introduce frameworks, microservices, containers or major dependencies.
- Build new commercial features.
- Implement new scrapers, APIs or external data sources.
- Rebuild the frontend.
- Expand functionality beyond fixing the identified problems.
- Change established filenames, routes, endpoints or function signatures unless unavoidable for security.
- Silently change calculations, default filters or underlying business assumptions.
- Introduce speculative heuristics or fabricated data.
- Make unrequested changes to deployment or infrastructure.
- Print credentials or personal information in logs or reports.
- Push changes or deploy to production without explicit approval.

**Do not modify `data/state/state.sqlite`. Treat it as read-only, including avoiding migrations, index creation, VACUUM, data repair and test writes.**

### ALWAYS

- Inspect the actual implementation before changing anything.
- Distinguish confirmed defects from suspected risks.
- Preserve current functionality unless demonstrably unsafe or incorrect.
- Prefer a 5-line correction over a 100-line rewrite.
- Use existing utilities, patterns, dependencies and configuration.
- Make each patch independently understandable.
- Provide exact file and line references.
- Add narrowly targeted regression tests.
- Keep fixes reversible.
- Preserve current French/English labels unless factually incorrect or unsafe.
- Document every changed behaviour.
- Respect existing source-data provenance.
- Use synthetic data in tests containing personal information.

If a correction requires a major architectural change, STOP work on that issue, document the blocker and suggest a minimal containment measure. Continue with other independent fixes.

Do not disguise a refactoring as a security improvement.

---

# 1. APPLICATION CONTEXT

The reported architecture comprises:

- SQLite: `data/state/state.sqlite`
- Approximately 8,970 notarial transactions
- Approximately 6,535 transactions with recorded monetary values
- 83 agency profiles
- 93 broker profiles
- Approximately 2,183 attributed agency sales
- SPA: `index.html`
- Bun application engine
- Python FAO collectors
- SITG cadastral enrichment
- RegBL building attributes
- Agency sales reconciliation
- CMA valuation reports
- Client-facing privacy masking and administrative unlocking

Primary business modules:

1. Argus Notarié
2. Agency BI
3. Sourcing Off-Market
4. Foncier & Développeurs
5. Simulateur CMA / Avis de Valeur
6. nLPD privacy masking and controlled access

**This information comes from a development report, not a verified repository audit. Confirm the actual architecture, paths and implementation before acting.**

The records are commercially valuable and may contain personal information. Protect the originals throughout execution.

---

# 2. REQUIRED EXECUTION PROCEDURE

## Phase A: Establish the baseline

Before modifying code:

1. Inspect repository status, current branch and recent commits.
2. Identify the application entry points.
3. Identify authentication and data-access mechanisms.
4. Identify APIs, static assets and export/report routes.
5. Inspect existing tests, build commands and runtime requirements.
6. Locate all relevant calculations and configuration.
7. Check for hard-coded credentials and potentially exposed secrets without displaying or copying secret values.
8. Establish current build and test results.
9. Produce a concise baseline report.

Use existing project conventions.

Create a dedicated branch if the repository state safely permits it, such as:

`fix/surgical-security-data-hardening`

Do not automatically discard or overwrite uncommitted user changes.

Verify database integrity using read-only access. Do not change database content or configuration.

Perform all testing on a local or isolated environment. Do not run real data collection, scraping or production writes.

## Phase B: Classify findings

For every issue below, report:

- **CONFIRMED:** Verified in source code or runtime.
- **NOT PRESENT:** Inspected and not found.
- **UNVERIFIED:** Insufficient evidence to decide.
- **EXTERNAL REVIEW:** Requires legal, contractual, source-owner or operational confirmation.

Assign priority:

- P0: Security exposure, unauthorised disclosure, serious data integrity defect.
- P1: Incorrect financial calculation, misleading client-facing information, broken access protections.
- P2: Incorrect wording, provenance or minor reliability defect.

**Patch CONFIRMED issues only.**

Do not add controls based solely on an unverified allegation unless they are necessary to contain a demonstrable risk.

---

# 3. P0: MASTER VAULT & ACCESS SECURITY

The development report describes:

- A global unlock mechanism.
- A shared master credential.
- A potential `?vault=` URL parameter.
- Natural-person names masked by default.
- A client-facing application with detailed transaction records.

This requires immediate verification.

## 3.1 Inspect exposure paths

Search for:

- `vault`
- `master`
- `cytria`
- `password`
- `secret`
- `token`
- `seller`
- `buyer`
- Authentication and authorisation checks.
- Data serialisation and API response functions.
- Browser storage and URL parameters.

Inspect JavaScript bundles, backend responses, HTML payloads, JSON files, report endpoints, exports and embedded data.

Check whether names are genuinely protected or merely hidden visually.

**Critical:** If the browser already receives the unmasked data, client-side masking is insufficient.

## 3.2 Required corrections

If a shared master credential or URL-based unlocking mechanism exists:

1. Eliminate URL-controlled privileged access.
2. Remove reliance on any hard-coded shared credential.
3. Reuse existing server-side authentication and authorisation if available.
4. Prevent unauthorised clients from receiving restricted personal information.
5. Preserve the legitimate administrative workflow where safely possible.
6. Prevent sensitive records or credentials from appearing in URLs, logs, browser history or caches.

Check all equivalent access paths, not only the visible button.

Do not introduce a new authentication framework.

If the current architecture cannot enforce genuine server-side authorisation without substantial changes:

- Disable the unsafe privileged disclosure path using the smallest possible patch.
- Preserve non-sensitive, authorised functionality.
- Record the precise limitation.
- Explain the minimal architectural change required as a separate future proposal.
- Do not perform that architectural change.

An unsafe unlock mechanism must not remain accessible merely to preserve feature parity.

## 3.3 Object-level access

Inspect endpoints such as:

`/dossier?id=...`

Also inspect transaction details, geographic searches, PDF generation, exports and any other object-specific endpoints.

Verify that changing an object ID does not circumvent permissions.

Check that:

- Authentication is required where appropriate.
- Authorisation is checked for each restricted object.
- Sensitive fields cannot be requested through alternative response formats.
- Export permissions follow the same restrictions as ordinary views.
- Unauthenticated access does not leak detailed personal data.

Apply minimal localised corrections.

## 3.4 Required regression tests

Prove, using synthetic fixtures, that:

- Unauthenticated requests cannot retrieve restricted identities.
- Changing URL parameters cannot grant privileges.
- A restricted user cannot retrieve privileged data through an alternate endpoint.
- Printable reports and exports follow the same access rules.
- Authorised users retain appropriate access.
- Masking does not rely solely on CSS or presentation state.

Never log raw personal data as test evidence.

---

# 4. P1: CASATAX CALCULATION ERRORS

The report mentions thresholds near CHF 1,417,000 and uses a CASATAX classification or cliff-deal indicator.

Official Geneva sources establish CHF 1,394,928 from 1 March 2026.

References:

- <https://www.ge.ch/document/communique-hebdomadaire-du-conseil-etat-du-4-fevrier-2026>
- <https://www.ge.ch/document/cautionnement-etat-acquisition-logement>

## Tasks

1. Find every threshold, eligibility calculation, label and filter.
2. Identify whether the system hard-codes a single threshold.
3. Verify the historical thresholds and their effective dates using official sources.
4. Determine which transaction date is legally relevant.
5. Identify whether the available data contains that date or only a publication date.
6. Correct demonstrably inaccurate calculations with minimal changes.

Do not retrospectively apply the 2026 threshold to older transactions.

If the legally relevant date is unavailable, do not infer it from publication date without justification.

If full eligibility cannot be established, label the result as a preliminary price-based indicator rather than confirmed CASATAX eligibility.

Do not invent missing legal conditions or thresholds.

## Tests

- Values immediately below the threshold.
- Values exactly equal to the threshold.
- Values immediately above the threshold.
- Dates before and after applicable changes.
- Missing transaction dates.
- Missing or invalid prices.
- Historical transactions.

Retain the existing visual interface and filtering experience.

---

# 5. P1: DATE RANGES, METRICS & DATA CONSISTENCY

The documentation states approximately April 2025 to September 2026, while some agency metrics are described as 24-month measures.

These claims may be inconsistent.

## Inspect

- Date filtering.
- Transaction counting.
- Missing-price handling.
- Aggregate CHF calculations.
- Transaction deduplication.
- Agency transaction counts.
- Annualisation.
- Market-share denominators.
- Rolling quarterly comparisons.
- Last-sale dates.
- Publication delays.
- Agency leaderboard statistics.

The following reported metrics require verification against actual read-only SQL results:

- 8,970 transactions.
- 6,535 priced transactions.
- CHF 17,466,487,594 total recorded value.
- 83 agencies.
- 93 brokers.
- 2,183 agency-attributed sales.

## Required corrections

Fix only confirmed discrepancies.

Ensure the displayed observation period matches the data actually used.

For example, do not label 18 months of observations as an actual 24-month measurement.

If annualised estimates are used, identify them explicitly as annualised, rather than observed annual values.

If a denominator covers only agency-attributed records, do not label its percentage as the complete Geneva market share without adequate supporting coverage.

Exclude missing or invalid values from calculations requiring valid prices.

Do not modify source records to make aggregate totals match expected figures.

If the values in the report are simply obsolete, correct the documentation or dynamic labels, not the original transaction database.

## Tests

- Empty date windows.
- Boundary dates.
- Missing prices.
- Duplicate identifiers.
- Unattributed transactions.
- No sales for a broker.
- Negative or zero values where invalid.
- Quarter-to-quarter comparisons with unequal coverage.
- Correctness of annualisation.

---

# 6. P1: CMA VALUATION RELIABILITY

The CMA is described as providing P25, median and P75 valuations based on nearby recorded transactions.

The report uses the term "certified valuation".

This wording is potentially misleading unless a valid certification basis exists.

## Tasks

1. Inspect the current comparable selection logic.
2. Verify property-type filtering.
3. Inspect price-per-square-metre calculations.
4. Inspect surface-area source selection.
5. Check missing or zero surface handling.
6. Confirm sorting and percentile calculations.
7. Inspect treatment of extreme outliers.
8. Check whether transaction classes that should not be considered comparable are excluded or flagged.
9. Check for sample size and observation date.
10. Inspect the PDF/HTML report for unqualified claims.

## Corrections

- Fix mathematically incorrect calculations.
- Prevent division by zero and invalid price/m² outputs.
- Ensure the selected comparables match the criteria actually displayed.
- Display the real number of eligible comparables.
- Remove unsupported "certified" terminology.
- Avoid presenting statistical quartiles as professional guarantees.
- Correct unsupported confidence claims.
- Preserve professional judgment in the dossier.
- If insufficient comparable evidence exists, explicitly indicate that the estimate is not adequately supported.

Do not invent a new valuation model.

Do not introduce arbitrary statistical thresholds without documenting their assumptions and obtaining evidence.

Do not change existing radii or standard filters unless they are objectively defective.

### Regression tests

Use synthetic, independently calculable examples for:

- Median.
- P25.
- P75.
- Price/m².
- Empty sample.
- One comparable.
- Invalid surface.
- Outlier behaviour.
- Mixed property types.
- Missing values.

Ensure the generated dossier and interactive interface produce consistent results.

---

# 7. P1: AGENCY ATTRIBUTION & PERFORMANCE CLAIMS

The system reportedly attributes 2,183 transactions to agencies and supports performance rankings.

Inspect:

- Attribution algorithm and confidence fields.
- Matching criteria.
- Timing constraints.
- Duplicate agency listings.
- Uncertain matches.
- Broker-specific assignment logic.
- Sales volume calculations.
- Rankings and market-share calculations.

### Required corrections

If the system already has attribution confidence:

- Verify the confidence values are applied correctly.
- Ensure low-confidence matches are not silently described as verified sales.
- Ensure rankings use clearly defined criteria and denominators.
- Distinguish observed attributed sales from exhaustive market performance.
- Avoid converting estimated broker activity into confirmed individual achievements.
- Suppress unsupported client-facing certainty where necessary.

Preserve existing historical matches and source records.

Do not rebuild the attribution engine or introduce new matching algorithms.

If confidence thresholds require empirical validation, document the uncertainty rather than inventing a new threshold.

Test known ambiguous examples where fixtures are available.

---

# 8. P1: PRIVACY, OUTPUTS & SENSITIVE INFERENCES

Inspect all client-visible locations in which buyer, seller or broker identity or personal information might be exposed:

- Maps.
- Popups.
- Detail drawers.
- API payloads.
- Agency comparisons.
- Broker profiles.
- Search results.
- Downloads.
- CSV/JSON exports.
- PDF/HTML valuation dossiers.
- Error messages.
- Server and application logs.

The current application may mask names but reveal them indirectly through other fields or combinations of filters.

Check for inconsistent masking and accidental disclosures.

## Corrections

Apply the existing privacy policy consistently.

Restricted personal fields should not be disclosed before the required authorisation checks.

Use the smallest available access controls to limit detailed information to authorised use.

Prevent public-facing reports from incorrectly inferring personal financial distress, a motivation to sell or other unobserved private circumstances based solely on succession, inheritance or discount indicators.

Preserve legitimate aggregate market analytics.

Do not automatically remove publicly sourced records from the protected internal database.

Do not claim that software changes alone establish complete nLPD compliance.

Any unresolved privacy, retention, collection or disclosure questions must be documented for human legal review.

---

# 9. P1: SOURCE RIGHTS & PROVENANCE

Current reported sources include:

- FAO Geneva.
- SITG.
- RegBL.
- Zefix.
- Agency websites and property portals.

SITG rules updated in July 2026 distinguish:

- Class A: commercial use under applicable conditions.
- Class A*: commercial use requires authorisation.
- Class B: restricted use.

Reference:

<https://sitg.ge.ch/ressources/conditions-utilisation-donnees>

## Required audit

Inspect:

1. Existing source metadata and provenance records.
2. Source references in reports.
3. External exports.
4. Commercial or public-facing redistribution paths.
5. Existing attribution labels.
6. Source-rights configuration if present.

Correct missing or objectively incorrect source labels where provenance can be established.

Do not assume all publicly visible information is unrestricted for commercial redistribution.

Do not invent licence classifications for individual datasets.

If an external export exposes a dataset with verified restricted rights and no applicable authorisation, disable the specific unauthorised disclosure path while preserving lawful internal functionality.

If a licence or permission cannot be verified, flag it as requiring review rather than inventing approval.

### FAO collector boundary

The report mentions a direct API collection method and CAPTCHA-related browser automation.

Do not alter collectors as part of this assignment unless a confirmed security or correctness defect lies within the defined scope.

Do not introduce CAPTCHA bypasses, detection evasion, additional endpoints or new ingestion mechanisms.

Record unresolved collection-authorisation questions for legal or operational review.

---

# 10. P2: UNSUPPORTED BUSINESS CLAIMS

Inspect existing client-facing labels and calculations for the following potential claims:

- Guaranteed seller intent.
- Motivated sellers inferred from succession.
- Confirmed financial distress.
- Confirmed cash purchases.
- Actual buyer mortgage leverage.
- Legally established residual building rights.
- Guaranteed redevelopment potential.
- Certified financial or property valuations.
- Complete institutional ownership portfolios.

These cannot automatically be established from the fields described in the report.

If unsupported claims are actually implemented:

- Correct their wording.
- Distinguish calculations, simulations and assumptions from verified facts.
- Avoid misleading certainty.
- Retain useful evidence-based functionality.
- Add a brief existing-style qualifier where essential.

Do not create replacement analytical models.

Do not modify features merely because their names sound ambitious: verify what each feature actually calculates and exposes first.

---

# 11. CROSS-CUTTING HARDENING

Only within the existing architecture, inspect for directly related:

- Hard-coded secrets.
- Unsafe logging of sensitive data.
- Missing access restrictions.
- Unsafe error responses.
- Sensitive browser caching.
- Exposed database or backup files.
- Unsafe export routes.
- Unauthorised direct access to static files.
- Injection risks in inputs relevant to the affected features.
- Incorrect server error handling.

Apply minimal changes to confirmed material exposures.

If the static application serves the raw SQLite file or sensitive data files publicly, block that exposure using the smallest available server/static-hosting configuration change.

Avoid generic dependency upgrades, wholesale security rewrites and cosmetic cleanup.

Do not add tools or dependencies solely for an audit report.

---

# 12. TESTING & VALIDATION

After each fix:

1. Run the relevant focused tests.
2. Compare behaviour before and after.
3. Review the complete diff.
4. Verify no unrelated file was changed.
5. Confirm the original SQLite dataset remains unchanged.
6. Re-test the relevant security or calculation failure.

At completion:

- Run existing unit tests.
- Run relevant integration tests.
- Run the application build.
- Test existing primary navigation and workflows.
- Verify maps render normally.
- Verify transaction filters.
- Verify Agency BI.
- Verify CMA dossier output.
- Verify authorised data access.
- Verify denied/unauthorised data access.
- Check for new console or server errors.

If browser automation already exists, use it. Do not introduce a large end-to-end testing framework solely for this task.

Do not claim a test passed unless it was executed.

If dependencies or environmental limitations prevent execution, record that explicitly.

---

# 13. CHANGE CONTROL

Keep changes narrowly scoped.

For every correction report:

- Original behaviour.
- Verified problem.
- Root cause.
- File and lines modified.
- Minimum correction applied.
- Security or calculation effect.
- Regression test performed.
- Result.
- Remaining limitations.

Do not combine unrelated changes into a sweeping rewrite.

Avoid bulk formatting.

Avoid renaming files.

Avoid unrelated import sorting.

Avoid automatic lint fixes over untouched code.

Avoid changing public APIs unless essential.

If the patch scope grows unexpectedly, stop that specific issue and document the reason.

---

# 14. REQUIRED DELIVERABLES

Create only the following concise audit artifacts, under an existing appropriate documentation directory, or `docs/hardening/` if no suitable location exists.

## A. `SURGICAL_HARDENING_REPORT.md`

Include a table:

| ID | Severity | Finding | Evidence | Files | Fix | Tests | Status |
|---|---|---|---|---|---|---|---|

Status must distinguish:

- FIXED
- ALREADY SAFE
- NOT REPRODUCED
- BLOCKED
- REQUIRES HUMAN REVIEW
- DEFERRED: OUT OF SCOPE

## B. `SECURITY_AND_DATA_RISKS.md`

Only unresolved risks.

Include actual evidence, affected data, possible consequences, minimal mitigation and required owner decision.

## C. `REGRESSION_RESULTS.md`

Include:

- Exact tests executed.
- Commands.
- Results.
- Before/after observations.
- Any unexecuted tests and reasons.
- Read-only database integrity evidence.
- Confirmation that no unrequested migration or scraping was performed.

## D. Final diff summary

Provide:

- Files changed.
- Lines added and removed.
- Security issues fixed.
- Calculation issues corrected.
- Labels corrected.
- Features temporarily restricted for safety.
- Remaining blockers.
- Recommended manual checks.

Do not generate marketing content, a new roadmap, architecture proposals or speculative features.

---

# 15. DEFINITION OF DONE

The assignment is complete when:

1. All findings have been classified using actual code or runtime evidence.
2. Confirmed P0 exposures have been fixed or safely contained.
3. Confirmed in-scope P1 and P2 defects have received minimal corrections.
4. Tests provide evidence for the changes.
5. Original source records remain untouched.
6. Existing unaffected functionality is preserved.
7. No unrelated refactoring has occurred.
8. Any unfixable problem is clearly explained.
9. Changes remain reviewable and reversible.
10. The application has not been deployed or pushed without permission.

**A short, correct patch is preferable to a comprehensive redesign.**

---

# 16. EXECUTE NOW

Start by inspecting the actual repository.

First establish the baseline, identify relevant source files and confirm which reported vulnerabilities or defects exist.

Then apply narrowly scoped corrections in severity order:

1. P0: Security and unauthorised disclosure.
2. P1: CASATAX and factual/calculation integrity.
3. P1: CMA reliability and agency attribution.
4. P1: Privacy, exports and source rights.
5. P2: Unsupported client-facing claims.

Do not spend time improving already correct code.

If an issue is unverified, do not pretend it is fixed.

**Final governing instruction:**

FIX WHAT IS WRONG. PROTECT WHAT IS SENSITIVE. PRESERVE EVERYTHING ELSE.

No refactoring. No redesign. No feature development. Surgical patches only.
