# Standards Registry

Machine-readable source of truth: [standards-registry.json](standards-registry.json).
`scripts/validate_repository.py` checks that this table and the JSON agree.

## Usage rules

1. Cite a reference by its **identifier and edition** only. Do not quote its text: ISO standards are copyrighted, and ISTQB material is used under its own terms.
2. **Never cite a clause or section number** unless it appears in that entry's `verified_clauses` (all are currently empty).
3. If an entry is not `verified`, write "(edition needs verification)" when you cite it.
4. Do not claim that a project is compliant, conformant, or certified to any of these references because this skill was used.
5. ISTQB syllabi are knowledge references, not normative standards.
6. The quality model (ISO/IEC 25010) is used to *derive the applicable* quality requirements. It does not require every characteristic to be tested.
7. The 29119 parts are complementary: concepts (1), processes (2), documentation (3), techniques (4), keyword-driven (5). Map each activity to the part that covers it. Do not treat them as interchangeable.

## Registry

| Identifier | Edition | Status | Verified on | Used for | Optional |
|---|---|---|---|---|---|
| ISO/IEC/IEEE 29119-1:2022 | 2022 | unverified | — | Terminology and general testing concepts | no |
| ISO/IEC/IEEE 29119-2:2021 | 2021 | unverified | — | Test process mapping (planning, monitoring and control, design and implementation, environment, execution, completion) | no |
| ISO/IEC/IEEE 29119-3:2021 | 2021 | unverified | — | Test documentation structure (plans, specifications, reports) | no |
| ISO/IEC/IEEE 29119-4:2021 | 2021 | unverified | — | Test design technique selection and terminology | no |
| ISO/IEC/IEEE 29119-5:2024 | 2024 | unverified | — | Keyword-driven automation, where applicable | no |
| ISO/IEC 25010:2023 | 2023 | unverified | — | Deriving applicable quality characteristics for non-functional requirements and test types | no |
| ISO/IEC 25002:2024 | 2024 | unverified | — | How to apply quality models when deriving quality requirements | no |
| ISTQB CTFL v4.0.1 | v4.0.1 | verified | 2026-10-25 | Core testing knowledge: test levels and types, techniques, risk-based testing, defect management | no |
| ISTQB CT-GenAI v1.1 | v1.1 | verified | 2026-10-25 | Responsible use of generative AI (this agent) in testing: hallucination risk, verification of AI output | no |
| ISTQB CT-AI v2.0 | v2.0 | partially_verified | — | Testing AI-based systems under test, where applicable | yes |
| ISO/IEC 25059:2023 | 2023 | unverified | — | Quality model for AI-based products | yes |
| ISO/IEC TR 29119-11:2020 | 2020 | unverified | — | Testing AI-based systems | yes |
| ISO/IEC TS 42119-2:2025 | 2025 | unverified | — | Testing AI systems | yes |

## Workflow mapping

- **ISO/IEC/IEEE 29119-1:2022** → SKILL.md; references/stlc-workflow.md; references/artifact-schemas.md
- **ISO/IEC/IEEE 29119-2:2021** → references/stlc-workflow.md; Phases 1-6; Gates A-F
- **ISO/IEC/IEEE 29119-3:2021** → templates/test-plan.md; templates/test-cases.md; templates/test-execution-report.md; templates/test-closure-report.md
- **ISO/IEC/IEEE 29119-4:2021** → references/test-design-techniques.md; Phase 3
- **ISO/IEC/IEEE 29119-5:2024** → references/automation-guidelines.md
- **ISO/IEC 25010:2023** → references/requirement-analysis.md; templates/test-approach.md; risk-register.csv:quality_characteristic
- **ISO/IEC 25002:2024** → references/requirement-analysis.md
- **ISTQB CTFL v4.0.1** → references/test-design-techniques.md; references/risk-based-testing.md; references/execution-and-evidence.md
- **ISTQB CT-GenAI v1.1** → SKILL.md §2 non-negotiable rules; references/execution-and-evidence.md
- **ISTQB CT-AI v2.0** → references/test-design-techniques.md (when the product under test is AI-based)
- **ISO/IEC 25059:2023** → Only when the product under test is AI-based
- **ISO/IEC TR 29119-11:2020** → Only when the product under test is AI-based
- **ISO/IEC TS 42119-2:2025** → Only when the product under test is AI-based

## Re-verification before each release

For each entry, open `official_source`, confirm the title, edition, and status (published, withdrawn, or under revision), then update `verification_status`, `verified_on`, and `verified_by`. Record the change and its impact in CHANGELOG.md under "Standards registry". The registry does not claim to list the latest editions just because an edition appears here.
