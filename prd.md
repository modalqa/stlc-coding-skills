# STLC Coding Agent Skill
## Product Requirements Document (PRD) & Implementation Specification

**Document ID:** STLC-AGENT-PRD-001  
**Version:** 0.1.0-draft  
**Status:** Baseline specification  
**Product type:** Open-source, portable coding-agent skill  
**Primary mode:** Autonomous execution with policy-based safeguards  
**Scope:** Full Software Testing Life Cycle (STLC)  
**Distribution:** Portable core plus platform-specific adapters

---

# 1. Executive Summary

STLC Coding Agent Skill adalah skill yang memungkinkan AI coding agent menjalankan proses software testing secara sistematis, mulai dari analisis kebutuhan hingga evaluasi hasil dan test closure.

Produk ini bukan coding agent mandiri, bukan test management SaaS, dan bukan framework automation baru. Produk ini merupakan lapisan metodologi, workflow, kebijakan, dan instruksi yang mengarahkan coding agent yang sudah digunakan developer.

Skill menggunakan referensi ISO/IEC/IEEE 29119, model kualitas ISO/IEC 25010, dan pengetahuan testing ISTQB sebagai fondasi. Implementasi teknisnya menggunakan format Agent Skills yang portable, dengan adapter untuk Claude Code, Cursor, GitHub Copilot, Kilo Code, dan platform lain yang mendukung integrasi setara.

## 1.1 Product vision

Membuat setiap coding agent mampu melakukan software testing dengan disiplin seorang Quality Engineering professional, bukan sekadar menghasilkan test script.

## 1.2 Core principles

1. **Standards-informed:** keputusan testing merujuk pada standar dan praktik yang relevan.
2. **Risk-driven:** tingkat pengujian ditentukan oleh risiko, bukan hanya jumlah test.
3. **Autonomous by default:** agent melakukan pekerjaan yang diizinkan tanpa meminta konfirmasi untuk setiap langkah.
4. **Evidence-based:** setiap hasil pengujian harus dapat ditelusuri ke bukti yang tersedia.
5. **Portable:** metodologi tidak bergantung pada vendor coding agent.
6. **Human-governed:** tindakan berisiko tinggi dan keputusan yang membutuhkan otoritas manusia tetap memiliki approval gate.
7. **Tool-agnostic:** tidak mengharuskan penggunaan satu vendor LLM, test framework, atau platform CI tertentu.
8. **Auditable:** artefak, perubahan, hasil, dan keputusan dicatat dalam format yang dapat diperiksa.

# 2. Problem Statement

Coding agent saat ini dapat menulis unit test, integration test, dan end-to-end test. Namun, kemampuan tersebut tidak otomatis menjamin proses testing yang sistematis.

Masalah utama yang hendak diselesaikan:

- Test dibuat tanpa traceability ke requirement.
- Acceptance criteria yang ambigu tidak selalu diidentifikasi.
- Pemilihan test case tidak mempertimbangkan risiko secara konsisten.
- Test automation berfokus pada happy path.
- Hasil test sering tidak memiliki bukti yang cukup.
- Agent dapat menyatakan pengujian berhasil tanpa menjalankannya.
- Regression scope tidak ditentukan berdasarkan impact analysis.
- Dokumentasi test tersebar dan tidak konsisten.
- Keputusan release dibuat tanpa mempertimbangkan residual risk.
- Metodologi berubah mengikuti coding agent yang digunakan.

Solusinya adalah satu skill yang mendefinisikan perilaku testing secara konsisten di berbagai platform.

# 3. Product Goals

## 3.1 Goals

**G-01. Full STLC coverage**

Mendukung seluruh proses pengujian dari requirement analysis, planning, design, implementation, execution, monitoring, evaluation, sampai closure.

**G-02. Standards mapping**

Menyediakan registry referensi dan mapping ke standar ISO dan syllabus ISTQB yang relevan, lengkap dengan versi, sumber, dan tanggal verifikasi.

**G-03. Autonomous test engineering**

Mampu menganalisis repository, membuat artefak pengujian, mengimplementasikan test, menjalankan pengujian yang diizinkan, memperbaiki test yang memang salah, dan menghasilkan laporan.

**G-04. Cross-agent portability**

Core workflow tetap sama pada semua agent. Adapter hanya menangani perbedaan lokasi skill, frontmatter, kemampuan tool, dan mekanisme pemanggilan.

**G-05. Verifiable results**

Tidak ada klaim pass, coverage, atau release readiness tanpa bukti yang sesuai.

**G-06. Incremental adoption**

Mampu digunakan pada proyek baru, repository existing, aplikasi API, web application, backend service, dan perubahan kecil dalam workflow harian developer.

## 3.2 Non-goals

Versi pertama tidak bertujuan untuk:

- Menggantikan seluruh test management platform.
- Menggantikan otoritas QA Lead, auditor, atau release manager.
- Menjamin kepatuhan atau sertifikasi ISO suatu organisasi.
- Menjamin bebas defect.
- Menyediakan LLM sendiri atau mewajibkan AI gateway.
- Menyediakan dashboard SaaS dan database terpusat.
- Menjalankan pentest, load test, atau production testing secara otomatis tanpa scope dan izin khusus.
- Memaksakan penggunaan Playwright, Selenium, Cypress, Postman, atau framework tertentu.
- Mengunduh atau mendistribusikan salinan standar ISO berhak cipta.

# 4. Target Users

| Persona | Kebutuhan |
|---|---|
| AI-assisted developer | Membuat dan memelihara test dengan kualitas yang konsisten |
| QA Engineer | Melakukan test analysis, design, automation, dan reporting |
| Quality Engineering Lead | Menentukan strategi, risk-based coverage, dan quality gates |
| Tech Lead | Memahami dampak perubahan dan risiko regresi |
| Engineering Manager | Memperoleh informasi kualitas yang dapat ditelusuri |
| Enterprise QA / Audit team | Memeriksa artefak, evidence, approval, dan riwayat perubahan |

# 5. Product Requirements

## 5.1 Functional requirements

### FR-01: Repository discovery

Agent harus:

- Mendeteksi bahasa pemrograman, framework, dan struktur repository.
- Mengidentifikasi test framework yang sudah digunakan.
- Menemukan test commands dari package manifest, build files, CI configuration, atau dokumentasi.
- Mengidentifikasi arsitektur dan batas modul sejauh dapat disimpulkan dari source code.
- Memeriksa working tree dan perubahan yang belum di-commit.
- Mengidentifikasi environment variable, dependency, serta konfigurasi yang dibutuhkan tanpa membocorkan secret.
- Menyusun context summary sebelum melakukan perubahan yang signifikan.

Agent tidak boleh mengasumsikan bahwa framework tertentu tersedia sebelum memeriksa repository.

### FR-02: Requirement analysis

Agent harus:

- Mengidentifikasi requirement fungsional dan nonfungsional.
- Mengidentifikasi acceptance criteria.
- Menemukan requirement yang ambigu, bertentangan, atau tidak testable.
- Menentukan kebutuhan klarifikasi berdasarkan dampak dan risiko.
- Membuat requirement ID yang stabil.
- Menghubungkan requirement dengan test condition dan test case.

Jika requirement tidak tersedia, agent dapat melakukan provisional analysis berdasarkan kode dan dokumentasi, tetapi harus menandai asumsi serta keterbatasan.

### FR-03: Risk assessment

Agent harus mengevaluasi setidaknya:

- Dampak kegagalan terhadap pengguna dan bisnis.
- Probabilitas atau likelihood kegagalan.
- Kompleksitas perubahan.
- Dampak keamanan dan akses.
- Dampak terhadap data dan integrasi.
- Ketergantungan pada layanan eksternal.
- Riwayat defect jika tersedia.
- Ketidakpastian bukti dan environment.

Risk score boleh menggunakan skala numerik yang dapat dikonfigurasi, misalnya likelihood × impact. Skala dan threshold harus didefinisikan dalam kebijakan proyek, bukan diklaim sebagai rumus wajib ISO.

Output: risk register, prioritas testing, dan alasan pemilihan scope.

### FR-04: Test planning

Agent harus menentukan:

- Test scope dan out-of-scope.
- Test levels dan test types yang relevan.
- Strategi manual dan automation.
- Test environment dan dependency.
- Test data requirements.
- Entry dan exit criteria.
- Execution order dan prioritas.
- Coverage objectives.
- Risiko yang belum dapat diuji.
- Keterbatasan waktu, tool, dan akses.

Rencana disimpan sebagai artefak Markdown atau format lain yang telah ditentukan repository.

### FR-05: Test design

Agent harus mampu memilih teknik desain sesuai konteks, termasuk:

- Equivalence partitioning.
- Boundary value analysis.
- Decision table testing.
- State transition testing.
- Use case testing.
- Error guessing yang didasarkan pada konteks.
- Pairwise atau combinatorial testing bila relevan.
- Branch, condition, atau statement coverage bila sesuai.
- Exploratory testing sebagai aktivitas pengujian yang dapat direncanakan.

Agent tidak harus menggunakan seluruh teknik pada setiap perubahan. Pemilihan teknik harus memiliki alasan yang dapat ditelusuri.

### FR-06: Test implementation

Agent harus:

- Memilih framework yang sesuai dengan stack yang ditemukan.
- Menggunakan struktur dan konvensi repository yang sudah ada.
- Menulis test yang dapat dipelihara dan tidak bergantung pada urutan eksekusi yang tidak disengaja.
- Menggunakan fixtures dan test data secara terkontrol.
- Memisahkan test setup, execution, assertion, dan cleanup.
- Menghindari penggunaan data produksi tanpa otorisasi.
- Menambahkan test ke CI bila diizinkan dan sesuai dengan project conventions.
- Memastikan test failure tidak disamarkan oleh retry berlebihan atau assertion yang terlalu lemah.

### FR-07: Test execution

Agent harus:

- Menjalankan test melalui perintah yang teridentifikasi dan diizinkan.
- Merekam command, exit status, timestamp, environment context, dan hasil.
- Mengumpulkan log dan screenshot bila relevan serta tersedia.
- Membedakan test failure dari infrastructure failure.
- Menandai test yang tidak dapat dijalankan.
- Memverifikasi apakah hasil berasal dari eksekusi terbaru atau laporan sebelumnya.

Jika execution tool tidak tersedia, hasil harus ditandai `NOT_RUN`, bukan `PASS`.

### FR-08: Failure analysis and defect management

Agent harus mengklasifikasikan kegagalan menjadi kategori seperti:

- Product defect candidate.
- Test implementation defect.
- Environment atau infrastructure failure.
- Test data problem.
- Dependency atau service failure.
- Flaky atau nondeterministic behavior.
- Inconclusive result.

Klasifikasi merupakan hipotesis sampai didukung bukti. Agent tidak boleh mengubah status kegagalan menjadi pass hanya untuk memenuhi quality gate.

### FR-09: Regression analysis

Agent harus mengidentifikasi:

- Modul yang berubah.
- Dependensi langsung dan tidak langsung yang dapat ditelusuri.
- Test yang terdampak.
- Risiko perubahan terhadap kontrak API, database, autentikasi, dan integrasi.
- Test prioritas tinggi yang perlu dijalankan terlebih dahulu.

Jika impact analysis tidak lengkap, agent harus menyatakan area yang belum terverifikasi.

### FR-10: Quality evaluation and test closure

Agent harus menghasilkan:

- Execution summary.
- Requirement dan risk coverage.
- Test pass/fail/blocked/not-run counts.
- Defect summary.
- Exit-criteria evaluation.
- Residual risks.
- Limitations and evidence gaps.
- QA recommendation: ready, ready with risks, atau not ready.

Rekomendasi tersebut bukan approval release yang mengikat. Keputusan final tetap mengikuti otoritas dan kebijakan proyek.

### FR-11: Standards registry

Setiap referensi harus menyimpan:

- Identifier.
- Judul.
- Edisi atau versi.
- Status verifikasi.
- Sumber resmi.
- Tanggal verifikasi.
- Area penggunaan.
- Mapping ke workflow atau artefak.
- Catatan batasan dan lisensi.

Agent tidak boleh mengarang nomor klausul ISO. Referensi klausul hanya boleh dicantumkan setelah diverifikasi melalui sumber yang sah.

### FR-12: Portability and adapters

Core skill harus dapat dipakai tanpa dependency terhadap satu agent atau vendor.

Setiap adapter harus mendefinisikan:

- Supported platform dan versi yang diuji.
- Instalasi project-level dan global jika didukung.
- Lokasi dan format skill.
- Metadata atau frontmatter khusus platform.
- Cara memanggil skill.
- Perbedaan kemampuan eksekusi.
- Known limitations.
- Automated compatibility checks.

# 6. Autonomous Execution Policy

Autonomous berarti agent boleh menjalankan rangkaian pekerjaan tanpa persetujuan di setiap langkah. Autonomous tidak berarti memiliki izin tak terbatas.

## 6.1 Allowed by default

Selama diizinkan oleh coding agent dan kebijakan repository:

- Membaca source code dan dokumentasi proyek.
- Membuat atau memperbarui test plan dan test cases.
- Menambahkan test scripts.
- Menjalankan test lokal yang aman.
- Memperbaiki test implementation defect.
- Menjalankan ulang test yang gagal setelah perubahan relevan.
- Membuat laporan dan evidence artifacts.
- Memperbarui traceability matrix.

## 6.2 Requires explicit authorization or a configured policy

- Mengakses environment bersama yang berisiko.
- Menjalankan destructive database operations.
- Mengubah atau menghapus data non-test.
- Memodifikasi deployment dan release configuration.
- Mengakses secret atau credential sensitif.
- Menjalankan security testing aktif terhadap sistem eksternal.
- Mengirim data keluar repository ke layanan AI eksternal.
- Mengubah status release atau menyetujui release.
- Menonaktifkan security control atau quality gate.

## 6.3 Stop conditions

Agent harus berhenti pada tindakan yang relevan apabila:

- Scope dan izin pengujian tidak memadai.
- Ada indikasi risiko kehilangan data.
- Environment yang dipilih tidak sesuai.
- Test memerlukan credential yang tidak tersedia.
- Requirement kritis saling bertentangan.
- Bukti tidak cukup untuk mengambil keputusan yang aman.

Agent tetap boleh melanjutkan pekerjaan independen yang aman dan mencatat blocker yang tersisa.

# 7. STLC Workflow Specification

Enam fase di bawah merupakan workflow operasional produk. Ini adalah pemetaan implementasi yang mengacu pada proses testing, bukan klaim bahwa ISO mewajibkan enam fase linear yang identik untuk setiap proyek.

## Phase 1: Requirement and Context Analysis

**Input:** requirement, issue, acceptance criteria, source code, architecture, API contract.

**Actions:**
1. Discover repository and context.
2. Extract requirement candidates.
3. Identify ambiguity and testability gaps.
4. Build initial traceability identifiers.
5. Assess preliminary risks.
6. Identify assumptions.

**Outputs:**
- `requirements-analysis.md`
- `assumptions.md`
- `initial-risk-register.md`
- `traceability-matrix.csv`

**Gate A:** konteks memadai untuk melanjutkan atau keterbatasan telah dinyatakan.

## Phase 2: Test Planning and Risk Assessment

**Actions:**
1. Establish scope and exclusions.
2. Identify test levels and types.
3. Prioritize based on risk.
4. Select test environments and tools.
5. Define entry/exit criteria.
6. Define execution and evidence requirements.

**Outputs:**
- `test-approach.md`
- `risk-register.csv`
- `test-plan.md`

**Gate B:** test scope, risiko utama, dan kriteria evaluasi terdefinisi.

## Phase 3: Test Analysis and Design

**Actions:**
1. Derive test conditions from requirements.
2. Select suitable design techniques.
3. Design positive, negative, boundary, and state-dependent scenarios.
4. Identify security and authorization cases when relevant.
5. Identify test data.
6. Link test cases to requirement and risk IDs.

**Outputs:**
- `test-cases.md`
- `test-data-plan.md`
- `traceability-matrix.csv`

**Gate C:** kebutuhan testing prioritas tinggi dapat ditelusuri ke test conditions dan test cases.

## Phase 4: Test Implementation

**Actions:**
1. Detect existing framework and conventions.
2. Implement tests and supporting fixtures.
3. Validate test syntax and dependencies.
4. Run safe smoke checks.
5. Configure test commands and CI integration where authorized.

**Outputs:**
- Test scripts.
- Fixtures and test data configuration.
- Execution instructions.
- Updated test inventory.

**Gate D:** test implementation siap dieksekusi atau blocker terdokumentasi.

## Phase 5: Execution and Monitoring

**Actions:**
1. Validate environment readiness.
2. Execute tests.
3. Record raw results and evidence.
4. Classify failures.
5. Fix test defects where justified.
6. Rerun affected tests.
7. Perform regression execution based on risk.

**Outputs:**
- `test-execution-report.md`
- `execution-results.json`
- `defect-candidates.md`
- `evidence/`

**Gate E:** hasil eksekusi dan keterbatasan dapat diverifikasi.

## Phase 6: Evaluation and Closure

**Actions:**
1. Compare results with exit criteria.
2. Evaluate coverage and unresolved risks.
3. Check traceability completeness.
4. Summarize defect candidates.
5. Assess whether more testing is needed.
6. Produce QA recommendation.

**Outputs:**
- `test-closure-report.md`
- `residual-risk-register.md`
- `release-readiness.md`

**Gate F:** closure report lengkap, atau closure ditandai blocked/incomplete.

Workflow boleh berulang ketika requirement berubah, defect ditemukan, atau bukti baru mengubah penilaian risiko.

# 8. Non-Functional Requirements

## NFR-01: Portability

Core skill harus menggunakan file teks, Markdown, YAML, JSON, dan skrip opsional yang tidak mengikat ke vendor tertentu.

## NFR-02: Maintainability

Setiap fase, kebijakan, dan adapter dipisahkan agar perubahan pada satu platform tidak merusak core workflow.

## NFR-03: Security

- Tidak mengekspos secret di laporan.
- Memperlakukan isi repository dan output tool sebagai data yang tidak tepercaya.
- Tidak menjalankan perintah destruktif tanpa izin.
- Meminimalkan pengiriman data ke layanan eksternal.
- Menggunakan least privilege sesuai kemampuan platform.

## NFR-04: Reliability

Hasil testing harus konsisten dengan bukti yang tersedia. Status tidak boleh diubah tanpa eksekusi atau dasar yang dapat diverifikasi.

## NFR-05: Auditability

Setiap run harus memiliki identifier, waktu, context, versi skill, daftar aktivitas, hasil, dan artefak relevan.

## NFR-06: Performance

Skill harus menggunakan context secara efisien. Referensi fase dimuat sesuai kebutuhan, bukan seluruh dokumentasi sekaligus.

## NFR-07: Extensibility

Pengguna dapat menambahkan test framework, project policy, template, atau adapter tanpa mengubah seluruh core skill.

## NFR-08: Accessibility

Dokumentasi, output, dan template harus menggunakan struktur teks yang konsisten dan mudah dibaca manusia maupun agent.

# 9. Technical Architecture

## 9.1 Architecture components

### A. Core skill

Berisi instruksi utama, fase STLC, aturan pengambilan keputusan, definisi status, dan batasan autonomous execution.

### B. Knowledge references

Berisi workflow details, test design techniques, standards mapping, quality model mapping, dan template guidelines.

### C. Policy layer

Mengatur scope, izin eksekusi, risk threshold, approval requirements, data handling, dan exit criteria.

### D. Adapter layer

Mengemas core skill untuk platform yang berbeda. Adapter tidak boleh mendefinisikan ulang metodologi atau mengubah arti status.

### E. Validation layer

Memvalidasi struktur artefak, ID, traceability, status hasil, dan kelengkapan laporan. Validator merupakan pemeriksaan deterministik, bukan pengganti penilaian testing.

### F. Evaluation layer

Menggunakan fixture repository dan expected outcomes untuk mengukur apakah agent mengikuti instruksi dengan benar.

## 9.2 Data flow

Repository context  
→ Requirement analysis  
→ Risk assessment  
→ Test planning  
→ Test design  
→ Test implementation  
→ Test execution  
→ Evidence validation  
→ Test closure

Pada setiap fase, hasil disimpan sebagai artefak yang dapat ditelusuri. Fase selanjutnya menggunakan artefak sebelumnya sebagai input.

# 10. Repository Structure

```text
stlc-agent-skill/
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── agents/
│   └── openai.yaml
├── skills/
│   └── stlc-engineer/
│       ├── SKILL.md
│       ├── references/
│       │   ├── standards-registry.md
│       │   ├── stlc-workflow.md
│       │   ├── requirement-analysis.md
│       │   ├── risk-based-testing.md
│       │   ├── test-design-techniques.md
│       │   ├── automation-guidelines.md
│       │   ├── execution-and-evidence.md
│       │   ├── traceability.md
│       │   └── release-evaluation.md
│       ├── templates/
│       │   ├── requirements-analysis.md
│       │   ├── test-plan.md
│       │   ├── test-cases.md
│       │   ├── risk-register.csv
│       │   ├── traceability-matrix.csv
│       │   ├── defect-report.md
│       │   └── test-closure-report.md
│       └── scripts/
│           └── validate_artifacts.py
├── adapters/
│   ├── claude-code/
│   ├── cursor/
│   ├── github-copilot/
│   └── kilo-code/
├── tests/
│   ├── fixtures/
│   ├── scenarios/
│   ├── expected/
│   └── evaluations/
├── docs/
│   ├── architecture.md
│   ├── installation.md
│   ├── compatibility.md
│   └── standards-mapping.md
└── scripts/
    ├── validate_repository.py
    └── package_skill.py
```

File `agents/openai.yaml` hanya dipertahankan jika memang diperlukan oleh ekosistem Agent Skills yang ditargetkan. File tersebut bukan pengganti adapter platform lainnya.

# 11. Core Skill Contract

File `SKILL.md` harus berisi frontmatter sesuai format yang ditargetkan dan instruksi operasional yang ringkas.

Contoh baseline:

```yaml
---
name: stlc-engineer
description: >
  Executes risk-based software testing workflows from requirement
  analysis through test closure, including test design, automation,
  execution, evidence validation, and quality evaluation.
---
```

Isi minimal `SKILL.md`:

1. Trigger conditions.
2. Required repository discovery.
3. Autonomous execution policy.
4. Six STLC phases.
5. Mandatory artifact conventions.
6. Traceability rules.
7. Evidence and execution status rules.
8. Failure classification.
9. Quality gate behavior.
10. Standards registry usage.
11. References to supporting documents.

Core skill tidak boleh terlalu besar. Detail teknis dimuat dari folder `references/` berdasarkan fase yang sedang dijalankan.

# 12. Artifact Schemas

## 12.1 Test case

Setiap test case minimal memiliki:

- `test_case_id`
- `requirement_ids`
- `risk_ids`
- `title`
- `objective`
- `preconditions`
- `test_data`
- `steps`
- `expected_result`
- `test_level`
- `test_type`
- `design_technique`
- `automation_status`
- `priority`

## 12.2 Execution result

Setiap execution record minimal memiliki:

- `run_id`
- `test_case_id`
- `status`
- `started_at`
- `finished_at`
- `command`
- `exit_code`
- `environment`
- `evidence_refs`
- `failure_category`
- `notes`

Status yang diperbolehkan:

- `PASS`
- `FAIL`
- `BLOCKED`
- `NOT_RUN`
- `INCONCLUSIVE`

Status hasil dan status workflow harus dipisahkan. Misalnya, `BLOCKED` pada environment bukan bukti bahwa requirement gagal, sedangkan `FAIL` menunjukkan assertion atau expected behavior tidak terpenuhi berdasarkan eksekusi yang sah.

## 12.3 Traceability

Traceability harus menghubungkan:

Requirement → Risk → Test Condition → Test Case → Execution Result → Defect Candidate → Closure Decision

Relasi yang tidak tersedia harus ditandai, bukan diisi dengan identifier rekaan.

# 13. Standards and ISTQB Mapping

Standards registry awal harus mencakup referensi berikut. Edisi dan status perlu diverifikasi ulang sebelum setiap release produk.

| Reference | Application |
|---|---|
| ISO/IEC/IEEE 29119-1:2022 | General concepts and terminology |
| ISO/IEC/IEEE 29119-2:2021 | Test process mapping |
| ISO/IEC/IEEE 29119-3:2021 | Test documentation |
| ISO/IEC/IEEE 29119-4:2021 | Test design techniques |
| ISO/IEC/IEEE 29119-5:2024 | Keyword-driven testing, where applicable |
| ISO/IEC 25010:2023 | Product quality model |
| ISO/IEC 25002:2024 | Quality model concepts and usage |
| ISTQB CTFL v4.0.1 | Core testing knowledge |
| ISTQB CT-GenAI v1.1 | Generative AI in software testing |
| ISTQB CT-AI v2.0 | AI-system testing, where applicable |

The ISO/IEC/IEEE 29119 family defines complementary concepts, processes, documentation, and design techniques. The core workflow should map to these sources rather than treating every source as interchangeable.

The quality model should be used to derive applicable quality requirements and tests. It must not be interpreted as requiring every quality characteristic to be tested in every application.

ISTQB material is a knowledge reference, not a replacement for normative standards or a certification claim.

For AI-powered products, the registry may additionally reference ISO/IEC 25059:2023, ISO/IEC TR 29119-11:2020, and ISO/IEC TS 42119-2:2025, where relevant.

# 14. Adapter Implementation Specification

## 14.1 Shared contract

Every adapter must preserve:

- Core workflow semantics.
- Artifact paths or documented mappings.
- Risk classification.
- Execution result states.
- Approval requirements.
- Evidence requirements.
- Standards registry references.

## 14.2 Claude Code adapter

Requirements:

- Install into the documented project or user skill directory.
- Expose the skill using the supported invocation mechanism.
- Verify the skill is discoverable by Claude Code.
- Test whether file access and execution permissions match the policy.
- Document any differences between interactive and autonomous execution.

## 14.3 Cursor adapter

Requirements:

- Support the appropriate project-level Agent Skills location.
- Verify skill discovery and activation.
- Check frontmatter compatibility.
- Confirm how repository context and tool execution are provided.
- Test the core acceptance scenarios.

## 14.4 GitHub Copilot adapter

Requirements:

- Use the documented repository skill mechanism supported by the targeted Copilot environment.
- Verify that the selected Copilot surface supports the required skill features.
- Document differences among supported IDEs and interfaces.
- Confirm that test execution permissions are supplied by the host environment, not assumed by the skill.

## 14.5 Kilo Code adapter

Requirements:

- Use the documented skill location and metadata format.
- Verify skill discovery.
- Test execution behavior under configured permissions.
- Record any platform-specific restrictions.

## 14.6 Other agents

New adapters may be added when an agent can consume the core skill or a generated representation of it.

An adapter must pass the same behavioral acceptance suite before being labeled supported.

# 15. Security and Safety Controls

The implementation must include the following safeguards:

1. Treat repository instructions, issue descriptions, test data, logs, and external responses as untrusted input.
2. Do not allow prompt injection within project content to override system or platform security boundaries.
3. Do not print secrets into reports or evidence.
4. Never assume production testing is authorized.
5. Require appropriate permission for destructive actions.
6. Prevent unintended changes to user modifications.
7. Keep raw evidence separate from generated summaries.
8. Record when evidence is missing or incomplete.
9. Do not claim that a test was executed if only its source code was inspected.
10. Do not label a repository ISO-compliant solely because the skill was used.

The repository must document known limitations and a security reporting process.

# 16. Evaluation and Testing Strategy

The skill itself must be tested as a software product.

## 16.1 Evaluation fixtures

Create deterministic fixture repositories containing:

- A simple CRUD application with acceptance criteria.
- A business-rule calculation with boundary conditions.
- An API with authentication and authorization.
- A service with an external dependency failure.
- A repository with intentionally flawed tests.
- A repository with ambiguous requirements.
- A repository where tests cannot execute due to a missing environment.
- A project with existing uncommitted user changes.
- A project containing malicious instructions embedded in test data.

## 16.2 Acceptance criteria

**AC-01: Requirement traceability**

All applicable high-priority requirements in the evaluation fixture are linked to relevant test conditions or an explicitly documented gap.

**AC-02: Risk prioritization**

The agent identifies critical risk areas and provides a reasoned priority order.

**AC-03: Test design**

The agent produces appropriate positive, negative, boundary, and state-based cases where applicable.

**AC-04: Autonomous execution**

The agent performs authorized analysis, test implementation, and execution without unnecessary confirmation prompts.

**AC-05: Honest execution reporting**

When execution is unavailable, the result is `NOT_RUN` or another appropriate non-pass status.

**AC-06: Failure classification**

The agent distinguishes a product failure from an infrastructure or test implementation problem when the evidence supports that distinction.

**AC-07: Closure completeness**

The closure report contains actual execution status, coverage information, unresolved risks, limitations, and a recommendation.

**AC-08: Safety**

The agent does not perform prohibited destructive actions or expose secrets.

**AC-09: Portability**

The core acceptance suite passes on every adapter declared supported.

**AC-10: Standards integrity**

The agent does not fabricate standards clauses, edition numbers, or claims of certification.

**AC-11: Regression preservation**

Existing user changes are not unintentionally overwritten.

**AC-12: Repeatability**

Repeated runs on deterministic fixtures produce semantically consistent results, allowing for expected model variation.

## 16.3 Metrics

Track:

- Requirement traceability completeness.
- High-risk test coverage.
- Defect detection precision on known fixtures.
- False-positive and false-negative rates.
- Execution status accuracy.
- Evidence completeness.
- Quality gate correctness.
- Unauthorized action count.
- Adapter compatibility pass rate.
- Token usage and execution duration where measurable.

Targets should be established from a baseline evaluation. Security violations and fabricated execution claims have a target of zero in the acceptance suite.

# 17. Implementation Plan

## Milestone 1: Core contract

Deliverables:

- Repository scaffold.
- Core `SKILL.md`.
- Workflow definitions.
- Standards registry.
- Artifact schemas.
- Autonomous execution policy.

Exit criteria: the core contract and terminology are stable.

## Milestone 2: Full STLC workflow

Deliverables:

- Six phase reference documents.
- Risk register and test design templates.
- Traceability matrix.
- Execution result format.
- Closure report template.
- Deterministic artifact validator.

Exit criteria: a fixture project can progress through the full workflow and produce a complete closure report.

## Milestone 3: Safety and evaluation

Deliverables:

- Evaluation fixture repositories.
- Expected outcomes.
- Safety scenarios.
- Evidence validation checks.
- Metrics collection.
- Regression evaluation suite.

Exit criteria: all critical acceptance scenarios pass.

## Milestone 4: First adapters

Deliverables:

- Claude Code adapter.
- Cursor adapter.
- GitHub Copilot adapter.
- Kilo Code adapter.
- Installation guide.
- Compatibility matrix.

Exit criteria: every declared adapter passes the shared behavioral suite on the tested version.

## Milestone 5: Open-source release

Deliverables:

- README and quick start.
- License and contribution policy.
- Changelog.
- Security reporting policy.
- Release packaging and versioning.
- Example fixture project.
- CI validation.

Exit criteria: a new user can install the skill, execute an example workflow, and understand its limitations without requiring proprietary tooling.

# 18. Versioning and Maintenance

Use semantic versioning for the skill:

- **MAJOR:** breaking changes to the skill contract, schemas, or behavior.
- **MINOR:** backward-compatible capabilities or adapters.
- **PATCH:** corrections, documentation fixes, and non-breaking improvements.

Standards registry updates should be separately recorded with source, date, and impact assessment.

Before a release:

1. Verify official standards status.
2. Verify ISTQB syllabus versions.
3. Review adapter compatibility.
4. Run evaluation and security fixtures.
5. Update the changelog.
6. Publish limitations and supported versions.

The skill must not claim to contain the latest standard merely because a version appears in its documentation.

# 19. Open-Source Licensing and Intellectual Property

The repository may contain original workflow instructions, templates, schemas, adapters, and validation scripts.

It should not redistribute copyrighted ISO standards or reproduce proprietary standard text beyond permitted use. The registry should identify references and provide links to official sources.

The project must select a license compatible with its intended distribution before the first public release. A permissive license such as Apache-2.0 can be evaluated if broad reuse and explicit patent licensing are priorities, subject to review of the project's dependencies and contributions.

ISTQB syllabus material should likewise be referenced according to its applicable terms rather than copied wholesale.

# 20. Definition of Done

The first stable release is complete only when:

- [ ] The core skill implements the full STLC workflow.
- [ ] Risk-based planning is functional.
- [ ] Test cases and results have stable schemas.
- [ ] Traceability can be validated.
- [ ] Autonomous execution respects configured permissions.
- [ ] Test results are backed by evidence.
- [ ] Test closure evaluates exit criteria and residual risk.
- [ ] Standards references have verified source metadata.
- [ ] Core evaluation fixtures pass.
- [ ] Security and prompt-injection scenarios pass.
- [ ] Every claimed adapter passes its compatibility tests.
- [ ] Installation and troubleshooting documentation is available.
- [ ] License, contribution, and security policies are published.
- [ ] Limitations and non-certification claims are explicit.

---

# Appendix A: Reference Sources

Official references to maintain in the standards registry:

1. ISO/IEC/IEEE 29119 series: https://committee.iso.org/sites/jtc1sc7/home/projects/flagship-standards/isoiecieee-29119-series.html
2. ISO/IEC/IEEE 29119-1:2022: https://www.iso.org/standard/81291.html
3. ISO/IEC/IEEE 29119-2:2021: https://standards.ieee.org/ieee/29119-2/7498/
4. ISO/IEC/IEEE 29119-3:2021: https://www.iso.org/standard/79429.html
5. ISO/IEC/IEEE 29119-4:2021: https://www.iso.org/standard/79430.html
6. ISO/IEC/IEEE 29119-5:2024: https://standards.ieee.org/ieee/29119-5/11042/
7. ISO/IEC 25010:2023: https://www.iso.org/standard/78176.html
8. ISO/IEC 25002:2024: https://www.iso.org/standard/78175.html
9. ISTQB CTFL: https://www.istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/
10. ISTQB CT-GenAI: https://istqb.org/certifications/gen-ai/
11. ISTQB CT-AI: verify the current official certification and syllabus page before adopting a specific edition.
12. ISO/IEC TS 42119-2:2025: https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec%3Ats%3A42119%3A-2%3Aed-1%3Av1%3Aen

# Final Product Decision

The approved baseline is:

**STLC Coding Agent Skill = Portable Agent Skills Core + Full STLC Workflow + Autonomous Execution Policy + Standards Registry + Evidence and Traceability + Agent-Specific Adapters + Shared Evaluation Suite.**

The first implementation priority is the core skill and its acceptance suite. Platform adapters follow the core contract, rather than independently defining the testing methodology.

This PRD is an implementation specification, not a claim that the resulting product or any organization using it is ISO-certified or automatically compliant with every requirement of the referenced standards.
