# Development Roadmap, Backlog, and Definition of Done

**Window:** eight weeks, Monday 2026-10-12 → Friday 2026-12-04 (Week 7 contains Thanksgiving).
**Then:** Weeks 9–12 (Dec 7 → Jan 15) for completion, pilot preparation, and the IRB submission ahead of the Spring 2027 pilot.

## 1. Lab priority and rationale

| Order | Lab | Why this position |
|---|---|---|
| 1 | **Lab 0** Orientation | Every later lab depends on students being able to run containers. It is the cheapest way to surface R-01 early. |
| 2 | **Lab 1** Network Traffic Analysis | **MVP.** Exercises every platform mechanism (image, generator, seeds, verify, auto-checker, docs) with the simplest runtime (Pattern A). |
| 3 | **Lab 2** File-System Forensics | Reuses Pattern A; the hardest generator (realism gap, R-03) is tackled while the scope is still small. |
| 4 | **Lab 3** Web App Assessment | Introduces Pattern B (multi-service, internal network). |
| 5 | **Lab 4** Incident Response | Reuses Labs 1–3 generators to produce correlated evidence. Built last because it depends on all of them. |

## 2. Week-by-week plan

### Week 1 (Oct 12–16) — Platform foundation + Lab 0 · **Milestone 1**
- **Objectives:** a working skeleton that any later lab plugs into; students can complete Lab 0.
- **Development tasks:** repo scaffolding; `cyberlab/base` Dockerfile (non-root, Python 3.13); shared `cyberlab_common` Python package (manifest hashing, verify framework, seed derivation); Compose conventions and a security baseline fragment; Lab 0 image and Compose file; `.devcontainer/` draft; CI pipeline (lint, unit tests, multi-arch build, push to GHCR on tag).
- **Technical deliverables:** `platform/images/base/Dockerfile`, `platform/lib/cyberlab_common/`, `labs/lab0-orientation/compose.yaml`, `.github/workflows/ci.yml`.
- **Documentation:** Lab 0 student guide; CONTRIBUTING; SECURITY; lab template README; ADRs 0001–0011 accepted or revised.
- **Testing:** unit tests for hashing and seed derivation; the Lab 0 verify passes on Mac (developer) and in CI on amd64 and arm64.
- **Dependencies:** GitHub account/org decision (OD-03); Phase 1 approval.
- **Risks:** R-01, R-16.
- **Acceptance:** see [07-milestone-1-proposal.md](07-milestone-1-proposal.md).

### Week 2 (Oct 19–23) — Lab 1 evidence and tooling
- **Objectives:** a deterministic PCAP generator and analysis image.
- **Tasks:** write the Lab 1 scenario narrative; Scapy generator (benign baseline traffic + suspicious activity: DNS beaconing to a DGA-like domain, HTTP C2 check-ins, a small exfil over HTTP POST, plus an optional port scan); `answer_key.json` schema; `net-analysis` image; Lab 1 Compose (Pattern A).
- **Deliverables:** `instructor/generators/lab1/` (private repo), demo variant in the public repo, `findings.schema.json`.
- **Documentation:** Lab 1 architecture doc with Mermaid diagrams; generator design note.
- **Testing:** double-build reproducibility; the solution script recovers 100% of answer-key items on 10 random seeds; `tshark` parses the full capture with no malformed-packet warnings.
- **Dependencies:** Week 1 base image.
- **Risks:** R-04, R-08.
- **Acceptance:** 10/10 seeds reproducible and solvable by the reference solution.

### Week 3 (Oct 26–30) — Lab 1 instruction, grading, MVP acceptance
- **Objectives:** Lab 1 **complete**, meeting the MVP definition of done.
- **Tasks:** student guide (16 sections), instructor guide, answer-key generator, 100-point rubric, auto-checker container, reset/teardown, troubleshooting page; first internal walkthrough by one volunteer tester (a peer, not a research participant).
- **Deliverables:** `labs/lab1-network-traffic/` complete; `v0.1.0-lab1` release with images on GHCR.
- **Testing:** full automated suite; manual walkthrough on macOS (Apple Silicon) and Windows 11 (if a machine is available — **open question OD-09**).
- **Risks:** R-02 (the MVP slipping is the main schedule signal).
- **Acceptance:** all MVP criteria in [05](05-mvp-and-acceptance-criteria.md) pass. **Gate: Phase 2 → Phase 3.**

### Week 4 (Nov 2–6) — Hardening and Lab 2 spike
- **Objectives:** fix Lab 1 issues found in the walkthrough; de-risk the Lab 2 generator.
- **Tasks:** apply Lab 1 feedback; Codespaces fallback test; resolve R-03 by building a reference ext4 image in a Linux VM (a real kernel deletes a file) and comparing it with the generator's output; draft the Lab 2 scenario.
- **Deliverables:** realism comparison report; `fs-forensics` image.
- **Testing:** Codespaces run-through; comparison of reference vs. generated images using `istat` and `blkls`.
- **Risks:** R-03.
- **Acceptance:** generated deleted-file behavior matches the kernel reference on the documented attributes.

### Week 5 (Nov 9–13) — Lab 2 complete
- **Tasks:** ext4 "workstation" image + FAT32 "USB" image generator (user activity: bash history, a document edited, a file copied to USB and deleted, a renamed/hidden file, timestamp evidence); chain-of-custody template; student and instructor guides; rubric; auto-checker items.
- **Testing:** reproducibility; read-only enforcement test (write attempts fail; hashes are unchanged after a full solution run); solvable across 10 seeds.
- **Acceptance:** Lab 2 meets the lab definition of done.

### Week 6 (Nov 16–20) — Lab 3 core
- **Tasks:** purpose-built Flask app with 4–5 controlled weaknesses (SQL injection in search, IDOR on a record endpoint, broken session handling, verbose errors, weak password policy); PostgreSQL; gateway; structured JSON logging; Pattern B Compose; authorized-use agreement.
- **Testing:** isolation tests (egress blocked from every container except the gateway; the host port bound to 127.0.0.1 only); health checks; resource ceiling measured.
- **Acceptance:** stack runs within 2 GB; all isolation tests pass.

### Week 7 (Nov 23–27, Thanksgiving week — reduced capacity) — Lab 3 instruction
- **Tasks:** student guide structured around *identify → validate (authorized) → remediate*; remediation exercise (students patch one flaw and re-test); instructor guide; rubric.
- **Acceptance:** Lab 3 is at **beta** (works end-to-end; documentation complete; awaiting second-tester review).

### Week 8 (Nov 30 – Dec 4) — Lab 4 scenario + Phases 4–6 drafts
- **Tasks:** fictional organization and incident narrative; master timeline; the Lab 4 generator composes the Lab 1–3 generators into correlated evidence; the student brief; security review checklist (Phase 4); Kubernetes/cloud feasibility draft and cost model (Phase 5); research methodology draft (Phase 6).
- **Acceptance:** the Lab 4 narrative and master timeline are internally consistent (an automated cross-source timestamp check passes); the Phase 4–6 drafts are ready for faculty review.

### Weeks 9–12 (Dec 7 – Jan 15) — Completion and pilot readiness
Lab 4 complete; full QA pass across three platforms; pilot packet for instructors; IRB submission (target by 2026-12-15, R-11); `v1.0.0` release candidate by 2027-01-15.

### Pre-agreed scope cuts if behind schedule
1. Lab 4 log aggregation (optional centralized logging) → deferred.
2. Per-student variants → pooled variants (K = 8).
3. Codespaces fallback → documented but not officially supported.
4. Lab 3 vulnerability count 5 → 3.

## 3. Prioritized backlog

| Pri | ID | Item | Phase |
|---|---|---|---|
| P0 | BL-01 | Base image + common library + security baseline | 2 |
| P0 | BL-02 | CI: lint, unit, multi-arch build, GHCR push, double-build reproducibility | 2 |
| P0 | BL-03 | Lab 0 complete | 2 |
| P0 | BL-04 | Lab 1 generator + image + verify | 2 |
| P0 | BL-05 | Lab 1 documentation, rubric, auto-checker | 2 |
| P1 | BL-06 | Variant pipeline (pseudonyms, HMAC seeds, bundle packaging for the LMS) | 2–3 |
| P1 | BL-07 | Lab 2 (incl. kernel-realism validation) | 3 |
| P1 | BL-08 | Lab 3 | 3 |
| P1 | BL-09 | Lab 4 | 3 |
| P1 | BL-10 | Security review + isolation test suite across labs | 4 |
| P2 | BL-11 | Codespaces / dev container fallback | 2–4 |
| P2 | BL-12 | Offline image tarball distribution | 4 |
| P2 | BL-13 | Cloud/Kubernetes feasibility + cost model | 5 |
| P2 | BL-14 | Research methodology + IRB packet | 6 |
| P3 | BL-15 | Browser terminal frontend (ttyd or similar) prototype | 5 |
| P3 | BL-16 | Future-lab design notes (Windows artifacts, memory, malware static triage, SIEM) | 5 |

## 4. Definition of Done (applies to every lab)

A lab is **Done** only when all of the following are true:

**Technical**
- [ ] Images build for linux/amd64 and linux/arm64 in CI and are published to GHCR with an immutable tag.
- [ ] `docker compose run --rm verify` passes in CI and on at least two real host OSes (one macOS Apple Silicon).
- [ ] The generator is byte-reproducible (double-build test) and its reference solution solves ≥ 10 random seeds at 100%.
- [ ] Evidence is mounted read-only; a test proves write attempts fail and hashes are unchanged after a full solution run.
- [ ] Reset and teardown leave no containers, networks, or volumes (`docker ps -a`, `docker network ls`, `docker volume ls` checked by a test).
- [ ] Resource limits are declared and peak usage is measured and recorded.
- [ ] Security baseline met (non-root, `cap_drop: ALL`, `no-new-privileges`, no privileged, network rules per pattern); deviations recorded in an ADR.
- [ ] Vulnerability scan reviewed; no unreviewed critical findings.

**Educational**
- [ ] The student guide has all 16 required sections; every command in it was executed by a test or a recorded walkthrough.
- [ ] The instructor guide, answer key, and 100-point rubric are complete and stored in the private repo.
- [ ] Learning objectives are Bloom-tagged and traced to tasks and rubric rows.
- [ ] Undergraduate and graduate expectations are distinguished.
- [ ] At least one person other than the developer completed the lab within 1.5× the target time.

**Documentation & transparency**
- [ ] The architecture doc includes Mermaid diagrams, ports, storage, trust boundaries, and resources.
- [ ] Known limitations and synthetic-vs-real differences are documented for students.
- [ ] CHANGELOG entry; version tag; test status labels (*tested on X, date* / *untested*).
