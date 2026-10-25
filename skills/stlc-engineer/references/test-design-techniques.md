# Test Design Techniques (Phase 3)

Pick techniques to fit the requirement and the risk. You do not need every
technique on every change. Record in `test-approach.md` → Techniques *why*
each chosen technique fits. Technique names follow common ISTQB and
ISO/IEC/IEEE 29119-4 terminology. Do not cite clause numbers.

| Technique | Use when | Produces |
|---|---|---|
| Equivalence partitioning | Inputs or outputs fall into classes that are handled the same way | One case per valid and invalid partition |
| Boundary value analysis | Ordered ranges, limits, sizes, dates, money | Cases at each boundary and either side of it (2- or 3-value) |
| Decision table | Several conditions combine into different outcomes (business rules, permissions) | One case per relevant rule column. Collapse impossible combinations and record the reason. |
| State transition | Behaviour depends on state or history (orders, sessions, workflows) | Valid transitions, invalid transitions, guard conditions |
| Use case / scenario | End-to-end user goals with alternate and exception flows | Main flow plus alternate and exception paths |
| Error guessing | Context suggests likely mistakes (null, empty, unicode, timezone, concurrency, retries) | Targeted negative cases. Name the context that suggested them. |
| Pairwise / combinatorial | Many parameters with interactions; exhaustive testing is infeasible | A covering array. Record the tool and the strength. |
| Statement / branch / condition coverage | White-box assessment of the changed code | Coverage gaps turned into cases. Report the coverage tool and its numbers only from an actual run. |
| Exploratory testing | Low specification, new UI, or a need to learn | A charter (mission, area, timebox), notes, and findings, recorded as MANUAL cases |

## Minimum design set per requirement

- **Positive**: the expected behaviour with valid input.
- **Negative**: invalid input, unauthorized actor, wrong state.
- **Boundary**: for every ordered input or limit.
- **State-dependent**: when the behaviour depends on prior state.

Leave a type out only with a one-line reason in the test case or approach.

## Security and authorization (when relevant)

When a change touches authn/authz, input parsing, file handling, or multi-tenancy, add cases for:
missing or invalid or expired credentials; a valid user acting on another user's or tenant's resource (IDOR); role escalation; input that is injection-shaped (SQL, command, template, path traversal) *against the local system under test only*; and error messages that leak internals or secrets.
Active security testing of external or shared systems needs authorization (see autonomy-policy.md).

## Oracles

Every expected result must be checkable: an exact value, a state, a status
code, a message pattern, or a property such as "balance never negative".
Avoid oracles such as "works correctly".

## Test case format

Use `templates/test-cases.md`. All 14 fields are required. `priority`
inherits the highest risk level linked to the case unless a reason is given.
