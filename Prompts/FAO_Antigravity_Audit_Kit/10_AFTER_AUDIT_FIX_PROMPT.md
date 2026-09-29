# Optional Follow-Up — After the Audit Only

Use this ONLY after `08_FINAL_AUDIT.md` exists.

Antigravity:

Read the completed FAO audit under:

`docs/audit/fao/`

Do not implement broad refactors.

Create a proposed remediation plan focused only on verified P0 and P1 findings.

For each proposed change provide:

- finding ID
- affected file(s)
- affected table(s)
- exact failure mechanism
- minimal code/schema change
- regression risk
- validation test
- rollback plan
- whether historical data requires reprocessing

Then create:

`docs/audit/fao/09_REMEDIATION_PLAN.md`

Do not modify production code yet.

The next human decision will determine which fixes are authorized.
