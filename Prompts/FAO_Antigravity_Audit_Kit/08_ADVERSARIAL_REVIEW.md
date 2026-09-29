# Stage 7 — Adversarial / 10th-Man Review

Goal: deliberately attempt to prove that the system is misleading or unreliable.

Assume a skeptical senior engineer says:

> “The application looks convincing, but its data cannot be trusted.”

Attempt to substantiate that claim using evidence.

Search specifically for:

- silent data loss
- missed FAO pages
- incomplete periods
- stale data
- duplicate records
- duplicate documents
- incorrect joins
- broken lineage
- parser edge cases
- wrong field semantics
- false map precision
- bad cadastral matches
- aggregation mistakes
- inconsistent filters
- missing validation
- survivorship bias
- selection bias
- historical gaps
- retry/resume corruption
- undocumented assumptions

## For every hypothesis record

| Hypothesis | Evidence for | Evidence against | Status | Severity |
|---|---|---|---|---|

Status:
- CONFIRMED
- PLAUSIBLE
- WEAK
- DISPROVEN
- UNTESTABLE

Do not exaggerate.

If the evidence does not support the skeptical hypothesis, explicitly say so.

## Required output

Create:

`docs/audit/fao/07_ADVERSARIAL_REVIEW.md`

End with:

### Strongest reasons NOT to trust the system
### Strongest reasons TO trust the system
### Questions that remain unresolved

Update `00_AUDIT_INDEX.md`.

Do not implement fixes yet.
