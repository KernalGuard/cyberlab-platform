# Repository Structure

Two repositories ([ADR-0003](../adr/0003-two-repository-split.md)):

- **`cyberlab-platform`** (public): everything a student or outside reviewer may see.
- **`cyberlab-instructor`** (private): generators' variant logic, answer keys, rubrics with anchors, the seed map, and exemplar reports.

## 1. Public repository: `cyberlab-platform/`

```text
cyberlab-platform/
├── README.md                       # What this is, quick start, support matrix, test status
├── LICENSE                         # Code license (proposed: Apache-2.0 — OD-07)
├── LICENSE-docs                    # Docs license (proposed: CC BY 4.0 — OD-07)
├── CITATION.cff                    # How to cite (research)
├── CHANGELOG.md
├── SECURITY.md                     # Reporting issues; lab safety model
├── CONTRIBUTING.md
├── VERSION                         # Platform version (SemVer)
├── .gitattributes                  # eol=lf for all text; *.img/*.pcap binary (LFS optional)
├── .editorconfig
├── .devcontainer/
│   └── devcontainer.json           # Tier-2 browser-hosted fallback (Codespaces)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # lint → unit → build (amd64+arm64) → integration → scan
│   │   ├── release.yml             # tag → push images to GHCR, attach SBOM, demo bundles
│   │   └── docs.yml                # doc lint (required sections, links, Mermaid)
│   └── ISSUE_TEMPLATE/
├── platform/                       # ── SHARED: used by every lab ──
│   ├── images/
│   │   ├── base/Dockerfile         # debian:trixie-slim + python3 + analyst user
│   │   ├── net-analysis/Dockerfile
│   │   ├── fs-forensics/Dockerfile
│   │   ├── web-workstation/Dockerfile
│   │   └── ir-workstation/Dockerfile
│   ├── lib/cyberlab_common/        # Python package installed in base image
│   │   ├── manifest.py             # create/verify MANIFEST.sha256
│   │   ├── seeds.py                # HMAC seed derivation, deterministic RNG
│   │   ├── verify.py               # check framework: tools, integrity, isolation, resources
│   │   ├── findings.py             # findings.json schema validation
│   │   └── checker.py              # generic auto-checker engine
│   ├── compose/
│   │   └── security-baseline.yaml  # x-cyberlab-hardening anchor (cap_drop, user, ro, limits)
│   ├── schemas/
│   │   ├── findings.schema.json
│   │   └── manifest.schema.json
│   └── templates/                  # doc templates copied when creating a lab
│       ├── student-guide.md
│       ├── lab-architecture.md
│       └── report-template.md      # student report skeleton (Markdown → PDF)
├── labs/                           # ── LAB-SPECIFIC ──
│   ├── lab0-orientation/
│   ├── lab1-network-traffic/
│   │   ├── README.md               # Lab card: level, time, status, tested-on
│   │   ├── compose.yaml
│   │   ├── .env.example
│   │   ├── lab.yaml                # metadata: id, version, image digests, resources, objectives
│   │   ├── docs/
│   │   │   ├── student-guide.md
│   │   │   ├── architecture.md
│   │   │   └── troubleshooting.md
│   │   ├── evidence/               # demo variant only (seed "demo"); student bundles replace this
│   │   │   ├── MANIFEST.sha256
│   │   │   └── capture.pcapng
│   │   ├── work/                   # student-writable; reset restores from work.template/
│   │   ├── work.template/
│   │   │   ├── findings.json
│   │   │   ├── case-notes.md
│   │   │   └── chain-of-custody.md
│   │   ├── scripts/                # run INSIDE containers (verify hooks, reset)
│   │   └── tests/
│   │       ├── test_isolation.py
│   │       ├── test_integrity.py
│   │       └── test_demo_solution.py
│   ├── lab2-filesystem-forensics/
│   ├── lab3-webapp-assessment/
│   │   └── app/                    # purpose-built vulnerable app source (weaknesses documented in private repo)
│   └── lab4-incident-response/
├── tests/                          # cross-lab tests
│   ├── policy/test_compose_policy.py   # SEC-01/02/05/07 checks on `docker compose config`
│   └── docs/test_guide_sections.py
├── tools/
│   └── labctl/                     # optional convenience CLI (containerized), never required
└── docs/
    ├── phase-1/                    # this package
    ├── adr/                        # Architecture Decision Records
    ├── spikes/                     # feasibility experiments (not production code)
    ├── student/                    # install guides per OS, Lab 0 pre-flight checklist
    └── research/                   # public methodology (no participant data, ever)
```

## 2. Private repository: `cyberlab-instructor/`

```text
cyberlab-instructor/
├── README.md
├── generators/
│   ├── common/                     # imports cyberlab_common from the public repo (pinned version)
│   ├── lab1/generate.py            # full variant logic (indicator pools, narrative timing)
│   ├── lab2/generate.py
│   ├── lab3/seed_data.py
│   └── lab4/compose_incident.py    # orchestrates lab1–3 generators into one coherent incident
├── keys/                           # generated answer keys (gitignored; reproducible from seeds)
├── labs/
│   └── lab1/
│       ├── instructor-guide.md
│       ├── answer-key.md           # narrative key for the demo seed + how to read JSON keys
│       ├── rubric.md               # 100 pts, UG and grad tables, anchored descriptors
│       ├── reference-solution/     # scripted solution used by CI
│       └── exemplars/              # graded example reports (synthetic)
├── roster/                         # NEVER committed in plaintext: pseudonym map encrypted (OD-05)
├── scripts/
│   ├── make-bundles.sh             # pseudonyms → per-student evidence zips + keys
│   └── grade-batch.sh              # runs checker over exported LMS submissions
└── .github/workflows/ci.yml        # generator reproducibility + solution tests (private)
```

## 3. Shared vs. lab-specific

| Concern | Shared (platform/) | Lab-specific (labs/labN/) |
|---|---|---|
| OS, Python, non-root user | `images/base` | — |
| Tool sets | role images (`net-analysis`, …) | only if a lab needs a unique tool |
| Security hardening | `compose/security-baseline.yaml` (YAML anchors via `include`) | network topology, ports |
| Integrity / verify engine | `cyberlab_common.verify` | lab check list (`lab.yaml`) |
| Seeds, manifest, schemas | `cyberlab_common`, `schemas/` | lab's finding item definitions |
| Auto-checker engine | `cyberlab_common.checker` | item weights + match rules |
| Docs | templates | content |
| Tests | policy + doc lint | isolation/integrity/solution tests for that lab |
| Evidence | — | always lab-specific |

## 4. Conventions

- **Versioning:** platform SemVer in `VERSION`; each lab has its own `lab.yaml: version`; release tags `vX.Y.Z` (platform) and `labN-vX.Y.Z`. Images are tagged with both and never overwritten.
- **Image names:** `ghcr.io/<owner>/cyberlab-<role>:<version>`.
- **Branching:** `main` is always releasable; feature branches + pull requests; CI required to merge.
- **Binary evidence:** demo evidence only, kept small (< 20 MB per lab) in Git; student bundles are never committed.
- **Test-status header:** every README has `Tested on: <platform>, <date>` or `Status: UNTESTED`.
