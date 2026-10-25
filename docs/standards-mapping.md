# Standards Mapping

The machine-readable registry is `skills/stlc-engineer/references/standards-registry.json`. This page explains how the workflow relates to each reference. **It cites no clauses**: none have been verified. ISO text is copyrighted and is not reproduced here.

| Workflow element | Reference (edition per registry) | Relationship |
|---|---|---|
| Terminology (test basis, test condition, test case, test item, residual risk) | ISO/IEC/IEEE 29119-1; ISTQB CTFL v4.0.1 | Terms used with their common meaning |
| Phases 1–6 and gates A–F | ISO/IEC/IEEE 29119-2 (test processes) | The six phases are an *operational mapping* of the planning, monitoring and control, design and implementation, environment, execution, and completion processes. The standard does not mandate this exact sequence. |
| Templates (plan, cases, execution report, closure report) | ISO/IEC/IEEE 29119-3 (test documentation) | Templates are inspired by the documentation types. They are not certified conformant templates. |
| Design techniques | ISO/IEC/IEEE 29119-4; ISTQB CTFL v4.0.1 | Technique names and selection rationale |
| Keyword-driven automation (optional) | ISO/IEC/IEEE 29119-5 | Only where a project already uses keyword-driven frameworks |
| Non-functional requirement derivation | ISO/IEC 25010 (product quality model), ISO/IEC 25002 | Derive the *applicable* characteristics. Do not test all of them by default. |
| Risk-based testing | ISTQB CTFL v4.0.1 | Likelihood × impact is a project convention, not a standards formula |
| Agent's own use of generative AI | ISTQB CT-GenAI v1.1 | Hallucination and verification concerns, which motivate the evidence rules |
| AI-based systems under test (optional) | ISTQB CT-AI v2.0, ISO/IEC 25059, ISO/IEC TR 29119-11, ISO/IEC TS 42119-2 | Only when the product contains AI components |

## What this does and does not mean

- Using this skill does **not** make a project conformant with, or certified to, any of these standards. The validator rejects such claims in artifacts.
- Organisations that need formal conformance must obtain the standards, perform their own gap analysis, and involve qualified auditors.
