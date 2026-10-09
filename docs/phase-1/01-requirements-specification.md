# Project Requirements Specification

| Field | Value |
|---|---|
| Project | Containerized Cybersecurity & Digital Forensics Laboratory Platform ("CyberLab") |
| Document ID | CL-P1-SRS |
| Version | 0.1.0 (Draft for review) |
| Phase | 1 — Requirements and Feasibility |
| Author | Sharif Vadon (M.S. Digital Forensics & Cybersecurity, John Jay College), with AI-assisted drafting |
| Status | **Proposed** — not yet reviewed by faculty |
| Date | 2026-10-09 |

Requirement keywords **MUST**, **SHOULD**, and **MAY** follow RFC 2119. Priorities use MoSCoW (M = Must, S = Should, C = Could, W = Won't this release).

---

## 1. Purpose

This document defines what the CyberLab platform must do, under what constraints, and how success will be judged. It is the reference against which every later phase (implementation, QA, cloud feasibility, research) is traced.

## 2. Scope

### 2.1 In scope (Release 1, target: Spring 2027 pilot)

- A reusable laboratory **platform**: shared base images, conventions, tests, CI, and documentation templates.
- **Lab 0** — Environment orientation (Docker, Linux shell, hashing, troubleshooting). *Mandatory.*
- **Lab 1** — Network Traffic Analysis and Threat Identification (intro undergraduate).
- **Lab 2** — Linux File-System Forensics and Evidence Examination (intermediate undergraduate).
- **Lab 3** — Web Application Security Assessment (upper undergraduate).
- **Lab 4** — Incident Response and Multi-Source Digital Forensics (early graduate).
- Seeded, per-student synthetic evidence with instructor-regenerable answer keys.
- Student guides, instructor guides, 100-point rubrics, partial automated grading.
- A cloud/Kubernetes **feasibility study** and parameterized cost model (no paid deployment).
- A research **methodology** suitable for faculty review and IRB submission.

### 2.2 Out of scope for Release 1

- Paid cloud deployment of any kind (requires explicit written authorization).
- Live malware execution. Memory acquisition. Windows-guest labs.
- Collection of any student research data before IRB approval or an exempt determination.
- A browser-based lab portal (designed for, not built).

### 2.3 Designed-for future labs (architecture must not preclude)

Windows artifact analysis · Memory forensics · Malware triage (static only, in containers) · SIEM / log analysis. Their container-vs-VM feasibility is assessed in [02-architecture.md §8](02-architecture.md#8-container-vs-virtual-machine-feasibility).

## 3. Stakeholders

| Stakeholder | Interest | Access |
|---|---|---|
| Students (UG intro, UG forensics, early grad) | Working labs on personal laptops; clear guidance; fair grading | Public repo, own evidence bundle |
| Instructors / TAs | Low setup effort; answer keys; reproducible grading | Public + private instructor repo |
| Faculty sponsor / program | Academic rigor, alignment with course outcomes, safety | Review rights on all docs |
| Developer / researcher (S. Vadon) | Maintainable codebase, publishable methodology | Owner of both repos |
| Department / college IT | Policy compliance; no exposed services | Informational |
| IRB (Institutional Review Board) | Protection of human subjects | Reviews research protocol only |

## 4. Assumptions

Each assumption carries a confirmation status. **Unconfirmed** items are tracked in [08-open-decisions.md](08-open-decisions.md).

| ID | Assumption | Source | Status |
|---|---|---|---|
| A-01 | Students use Windows 10/11, macOS (Apple Silicon and Intel), or Linux | User answer | Confirmed by developer |
| A-02 | Minimum student machine: 8 GB RAM, 4 CPU cores, 20 GB free disk | User answer | Confirmed by developer |
| A-03 | Most students can install Docker Desktop (or an equivalent) on a personal computer | User answer | **Needs faculty/IT confirmation** |
| A-04 | Some students cannot (locked-down, Chromebook, low-spec), so a fallback path is required | User answer | Confirmed by developer |
| A-05 | 25–40 students per section, 1–2 sections per semester (≤ 80 students/semester) | User answer | **Needs faculty confirmation** |
| A-06 | Students have little prior Linux / Docker / CLI experience | User answer | Confirmed by developer |
| A-07 | Submissions go through the institutional LMS (assumed Brightspace) | User answer | **Needs confirmation of LMS** |
| A-08 | Developer has GitHub; a public repo for student materials is acceptable | User answer | **Needs faculty confirmation** |
| A-09 | No cloud budget exists | User answer | Confirmed |
| A-10 | Pilot target is Spring 2027, subject to faculty approval and course availability | User answer | **Needs faculty confirmation** |
| A-11 | Labs map to specific John Jay courses (to be named) | Inferred | **Needs faculty confirmation** |
| A-12 | Faculty supervision will exist for the research component | User answer ("potentially") | **Needs confirmation** |
| A-13 | Docker Desktop's license permits this educational use | Docker license terms (verify) | **Needs IT/legal confirmation** |

## 5. Functional Requirements

### 5.1 Platform (FR-P)

| ID | Requirement | Priority |
|---|---|---|
| FR-P-01 | Each lab MUST start with a single documented command (`docker compose up -d` or `docker compose run`) from its lab directory. | M |
| FR-P-02 | Each lab MUST provide a `verify` service that checks tools, evidence integrity, and isolation, exiting `0` on success and non-zero with a human-readable reason on failure. | M |
| FR-P-03 | Each lab MUST provide a `reset` procedure that returns it to the initial state without re-downloading evidence. | M |
| FR-P-04 | Each lab MUST provide a `teardown` procedure that removes all containers, networks, and volumes it created. | M |
| FR-P-05 | All helper scripts MUST run inside containers; the host requires only Docker with Compose v2 (Git optional). | M |
| FR-P-06 | Prebuilt multi-architecture images (linux/amd64, linux/arm64) MUST be published to a container registry so students do not build locally. | M |
| FR-P-07 | Images MUST be referenced by immutable version tag and SHOULD be pinned by digest in released compose files. | S |
| FR-P-08 | A shared base image MUST supply common tooling (Python, hashing, shell utilities, non-root user) to all labs. | M |
| FR-P-09 | The platform SHOULD provide a development container definition for a browser-hosted fallback (e.g., GitHub Codespaces). | S |
| FR-P-10 | The platform COULD provide a browser-based terminal frontend for future hosted delivery. | C |

### 5.2 Evidence (FR-E)

| ID | Requirement | Priority |
|---|---|---|
| FR-E-01 | All evidence MUST be synthetic or legally authorized; no real personal data. | M |
| FR-E-02 | Evidence MUST be generated by versioned, deterministic generators: same generator version + same seed ⇒ byte-identical evidence. | M |
| FR-E-03 | Each evidence bundle MUST ship with a manifest listing every file and its SHA-256 hash. | M |
| FR-E-04 | Evidence MUST be mounted read-only into analysis containers. | M |
| FR-E-05 | Integrity MUST be verifiable by students before and after analysis. | M |
| FR-E-06 | Generators MUST emit a machine-readable ground-truth file (answer key) per seed. | M |
| FR-E-07 | Seeds MUST be derived from random pseudonymous identifiers, never from student IDs or names. | M |
| FR-E-08 | The seed-to-student mapping MUST exist only in instructor-controlled storage. | M |
| FR-E-09 | A public demonstration variant (seed `demo`) with a published key MUST exist for testing and self-study. | M |

### 5.3 Instruction and assessment (FR-I)

| ID | Requirement | Priority |
|---|---|---|
| FR-I-01 | Each lab MUST include a student guide with the 16 sections required by the project brief. | M |
| FR-I-02 | Each lab MUST include an instructor guide, answer key, and 100-point rubric. | M |
| FR-I-03 | Learning objectives MUST be written as measurable outcomes tagged with a Bloom's level. | M |
| FR-I-04 | Each lab MUST define undergraduate and graduate expectations (graduate: correlation, uncertainty, defensibility). | M |
| FR-I-05 | Students MUST submit a PDF report plus a structured `findings.json` for objectively checkable answers. | M |
| FR-I-06 | An auto-checker MUST score `findings.json` against the seed's answer key and produce a per-item report for the grader. | M |
| FR-I-07 | Qualitative criteria (methodology, reasoning, communication) MUST be scored by a human using the rubric. | M |
| FR-I-08 | Each lab SHOULD target 90–120 minutes for a prepared student; Lab 0 SHOULD take 30–45 minutes. | S |
| FR-I-09 | Each lab MUST include an optional advanced challenge. | M |

## 6. Non-Functional Requirements

| ID | Category | Requirement | Priority |
|---|---|---|---|
| NFR-01 | Portability | Labs MUST run on Windows (Docker Desktop + WSL 2), macOS Apple Silicon and Intel, and Linux (Docker Engine). | M |
| NFR-02 | Resources | Total lab memory limit MUST NOT exceed **3 GB** (Labs 0–2: ≤ 1 GB) so that an 8 GB host remains usable. | M |
| NFR-03 | Disk | Images + evidence per lab SHOULD be ≤ 2 GB on disk; whole course ≤ 8 GB. | S |
| NFR-04 | Setup time | First-time setup (install excluded, pull included) SHOULD complete in ≤ 15 minutes on a 50 Mbit/s connection. | S |
| NFR-05 | Reproducibility | Generators MUST be byte-reproducible (verified by a double-build CI test). | M |
| NFR-06 | Reliability | `verify` MUST pass on all three reference platforms before each release. | M |
| NFR-07 | Maintainability | Shared logic MUST live in one place (base image, shared library, templates); lab directories contain only lab-specific content. | M |
| NFR-08 | Documentation | Every command in student guides MUST be tested (scripted where possible) before release. | M |
| NFR-09 | Accessibility | Guides SHOULD be plain Markdown/HTML with alt text and no information conveyed by color alone. | S |
| NFR-10 | K8s-readiness | Containers MUST follow 12-factor conventions (config via env, stateless images, health checks, no host-path assumptions besides evidence) so they can later be expressed as Kubernetes manifests. | S |
| NFR-11 | Transparency | Every artifact MUST be labeled as *tested* (with platform and date) or *untested*. | M |

## 7. Security Requirements

| ID | Requirement | Priority |
|---|---|---|
| SEC-01 | No container MUST run with `privileged: true`, host networking, host PID, or the Docker socket mounted. | M |
| SEC-02 | Containers MUST run as a non-root user, drop all Linux capabilities (`cap_drop: [ALL]`), and set `no-new-privileges`. Exceptions require an ADR. | M |
| SEC-03 | Root filesystems SHOULD be read-only, with explicit `tmpfs` or volumes for writable paths. | S |
| SEC-04 | Analysis-only labs (0, 1, 2) MUST have **no network** (`network_mode: none`). | M |
| SEC-05 | Multi-service labs (3, 4) MUST place services on an `internal: true` network with no egress. Any port exposed to the host MUST bind to `127.0.0.1` only. | M |
| SEC-06 | Intentionally vulnerable services MUST NEVER be published on non-loopback interfaces or deployed to the internet. | M |
| SEC-07 | Every container MUST have memory, CPU, and PID limits. | M |
| SEC-08 | No real malware or live exploit payloads are distributed. Simulated "malicious" artifacts MUST be inert and labeled. | M |
| SEC-09 | Instructor materials (generators' secrets, answer keys, seed map) MUST NOT be present in the public repository or student images; CI MUST scan for leaks. | M |
| SEC-10 | Images MUST be scanned for known vulnerabilities in CI; findings above a threshold are reviewed before release. | S |
| SEC-11 | Students MUST acknowledge an authorized-use agreement before Lab 3. | M |

## 8. Educational Requirements

| ID | Requirement |
|---|---|
| EDU-01 | Every technical component MUST trace to at least one learning objective (traceability matrix per lab). |
| EDU-02 | Labs MUST progress in cognitive demand: Lab 0–1 emphasize *Remember/Understand/Apply*; Lab 2 *Apply/Analyze*; Lab 3 *Analyze/Evaluate*; Lab 4 *Evaluate/Create*. |
| EDU-03 | Labs MUST model professional workflow: integrity verification, notes, chain-of-custody record, report. |
| EDU-04 | Each lab MUST distinguish *identification*, *authorized validation*, and *remediation* where offensive techniques are involved (Lab 3). |
| EDU-05 | Lab 4 MUST include deliberate ambiguity requiring students to state confidence and alternative hypotheses. |

## 9. Research Requirements

| ID | Requirement |
|---|---|
| RES-01 | The platform MUST log *operational* metrics that require no personal data (image pull/build success in CI, verify pass rates in testing). |
| RES-02 | No student data (setup time, surveys, grades) MAY be collected for research until IRB approval or an exempt determination. |
| RES-03 | Any future telemetry MUST be opt-in, anonymous, and disabled by default. |
| RES-04 | The repository MUST be citable and archived at release (tagged release; e.g., Zenodo DOI — to confirm). |
| RES-05 | Architecture decisions MUST be recorded as ADRs to support the methodology section of the research report. |

## 10. Constraints

- **No budget.** All tooling must be free/open-source or free for education.
- **Timeline.** Eight-week initial development window: 2026-10-12 → 2026-12-04.
- **Single developer.** Scope must fit one part-time graduate student plus AI assistance.
- **Development environment.** Developer uses macOS; this AI workspace (Linux x86-64) can run Docker but **cannot pull images from Docker Hub or other public registries** (blocked by egress policy). Image builds will therefore be tested on the developer's Mac and in GitHub Actions; generators and scripts can be tested natively here.

## 11. Traceability

Each requirement ID is referenced by an acceptance criterion in [05-mvp-and-acceptance-criteria.md](05-mvp-and-acceptance-criteria.md) or explicitly deferred to a later milestone in [04-roadmap.md](04-roadmap.md).
