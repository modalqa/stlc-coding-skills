# Risk-Based Testing (Phase 2)

Risk decides how much testing each area gets, and in what order.

## Factors (FR-03)

Assess each risk against all of these, and write in `rationale` the ones that drove the score:

| Factor | Ask |
|---|---|
| User and business impact | Who is hurt, and how badly, if this fails? Money, data, legal exposure, reputation? |
| Likelihood | How complex or new is the code? Has it changed recently? Is coverage poor? |
| Change complexity | How many modules, branches, or states? Concurrency? |
| Security and access | Does it touch authn/authz, input handling, secrets, or tenancy? |
| Data and integration | Persistence, migrations, data contracts, external APIs? |
| External dependencies | Timeouts, retries, partial failures, rate limits? |
| Defect history | Past bugs, reverted commits, TODO/FIXME notes, flaky tests in the same area? |
| Uncertainty | Unclear requirements, unavailable environment, no oracle? Uncertainty *raises* risk. |

## Scoring

The default model, configurable in `stlc-policy.yaml`, is `score = likelihood × impact` on 1–5 scales:

| Score | Level | Testing depth |
|---|---|---|
| 20–25 | CRITICAL | Multiple techniques, negative and boundary cases, regression of dependants. Must execute before closure. |
| 12–19 | HIGH | Positive, negative, and boundary cases. Must execute before closure. |
| 6–11 | MEDIUM | Representative positive and negative cases. |
| 1–5 | LOW | Smoke-level coverage or a documented exclusion. |

This model is a project convention. It is **not** a formula required by any
ISO standard. Do not present it as one. If the project defines another
model, set `formula: none` and validate with `--risk-formula none`.

## risk-register.csv columns

`risk_id, requirement_ids, description, category, quality_characteristic,
likelihood, impact, score, level, rationale, mitigation, test_case_ids,
residual_status`

- `category`: functional | security | data | integration | performance | reliability | usability | compatibility | other
- `test_case_ids`: filled in during Phase 3. Use `GAP` before that.
- `residual_status`: OPEN | PARTIAL | MITIGATED | ACCEPTED (ACCEPTED only with a named human decision).

## Prioritisation output

In `test-plan.md` → Risk-Based Priorities, order the work CRITICAL first,
then HIGH, and within each level put fast feedback first. Give the reason
for each position. Excluded high risks go in **Untestable Risks**, never
silently dropped.
