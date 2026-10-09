# Minimum Viable Laboratory and Acceptance Criteria

## 1. MVP definition

The **Minimum Viable Laboratory** is **Lab 0 + Lab 1 on the shared platform core**, released as `v0.1.0-lab1` by **2026-10-30** (end of Week 3).

It must exercise every platform mechanism once, so Labs 2–4 only add content and never invent new infrastructure:

| Mechanism | Exercised in MVP by |
|---|---|
| Shared base image + role image | `cyberlab/base` → `cyberlab/net-analysis` |
| Multi-arch build + registry | CI publishes amd64 + arm64 to GHCR |
| Deterministic generator | Lab 1 Scapy PCAP generator |
| Seeded variants + answer key | HMAC-derived seed → evidence + `answer_key.json` |
| Evidence manifest + integrity verification | `MANIFEST.sha256` + `verify` service |
| Read-only evidence, isolated runtime | Pattern A, `network_mode: none` |
| Reset / teardown | Compose-based procedures, tested |
| Partial auto-grading | `findings.json` checker |
| Student + instructor docs + rubric | Lab 1 complete set |

### MVP scope — Lab 1 storyline (proposed)

*A small fictional nonprofit's IT contractor exports one hour of traffic from a workstation segment after an endpoint alert.* The capture contains normal traffic (DNS, HTTPS handshakes, HTTP to an internal intranet, NTP, DHCP) and a hidden pattern for students to find:

1. A host periodically resolves algorithmically generated-looking domains (DNS beaconing).
2. The same host makes regular HTTP check-ins with a distinctive User-Agent (C2-like).
3. One larger HTTP POST carries a base64 "staging" blob containing **fake** records (exfiltration).
4. *(Optional challenge)* a short TCP SYN scan from that host against an internal subnet.

All domains use reserved names (`.example`, `.test`, `.invalid`) and all IPs come from documentation or private ranges (RFC 5737 / RFC 1918), so no artifact points at a real system.

## 2. Acceptance criteria

**V** = verification method: **A** automated (CI), **M** manual inspection, **W** walkthrough with a human tester.

### 2.1 Platform

| ID | Criterion | Target | V | Traces to |
|---|---|---|---|---|
| AC-P-01 | Images build in CI for linux/amd64 and linux/arm64 | 100% of images, both arches | A | FR-P-06, NFR-01 |
| AC-P-02 | Compressed image size, `net-analysis` | ≤ 350 MB | A | NFR-03 |
| AC-P-03 | Containers run as non-root UID 1000 with all capabilities dropped | 100% of services | A | SEC-02 |
| AC-P-04 | No service has `privileged`, host network/PID, or the Docker socket | 0 occurrences (policy test on rendered `docker compose config`) | A | SEC-01 |
| AC-P-05 | Each service declares memory, CPU, and PID limits | 100% | A | SEC-07 |
| AC-P-06 | Leak scan finds no answer keys, secrets, or the seed map in the public repo or images | 0 findings | A | SEC-09 |
| AC-P-07 | Host requires only Docker + Compose v2 | Guide steps use no host Python/Bash/Make | M | FR-P-05 |

### 2.2 Lab 0

| ID | Criterion | Target | V |
|---|---|---|---|
| AC-L0-01 | `verify` reports Docker version, architecture, available memory, and disk, with PASS/WARN/FAIL against minimums | Correct on Mac and in CI | A + M |
| AC-L0-02 | Student completes Lab 0 | ≤ 45 min for a tester new to Docker | W |
| AC-L0-03 | Every Lab 0 guide command runs exactly as written | 100% (scripted transcript test) | A |

### 2.3 Lab 1 (MVP)

| ID | Criterion | Target | V | Traces to |
|---|---|---|---|---|
| AC-L1-01 | Generator byte-reproducible | Identical SHA-256 across 2 builds, 10 seeds | A | FR-E-02, NFR-05 |
| AC-L1-02 | Different seeds produce different indicators of equal difficulty | 10 seeds: all distinct indicator sets; identical finding count/types | A | ARCH §6 (variant design) |
| AC-L1-03 | Reference solution recovers every answer-key item | 100% on 10 random seeds | A | FR-E-06 |
| AC-L1-04 | TShark parses capture cleanly | 0 malformed-packet warnings | A | — |
| AC-L1-05 | Evidence integrity | `verify` PASS before and after the reference solution runs | A | FR-E-05 |
| AC-L1-06 | Evidence immutability | Write attempts to `/evidence` fail (read-only FS) | A | FR-E-04 |
| AC-L1-07 | No network | Container shows only `lo`; DNS lookup and outbound connect fail | A | SEC-04 |
| AC-L1-08 | Startup | `docker compose run --rm workstation true` < 10 s after pull | A | — |
| AC-L1-09 | Peak memory | < 512 MB while running the reference solution | A | NFR-02 |
| AC-L1-10 | Reset | After reset, `work/` restored to template and evidence hashes unchanged | A | FR-P-03 |
| AC-L1-11 | Teardown | Zero lab containers, networks, volumes remain | A | FR-P-04 |
| AC-L1-12 | Auto-checker | Scores the reference `findings.json` 100%, a blank one 0%, and a seeded wrong-variant submission flagged | A | FR-I-06 |
| AC-L1-13 | Student guide completeness | All 16 required sections present (doc lint) | A | FR-I-01 |
| AC-L1-14 | Learning objectives | ≥ 5 objectives, each Bloom-tagged and traced to ≥ 1 task and rubric row | M | FR-I-03, EDU-01 |
| AC-L1-15 | Rubric | Totals 100 points; separate UG and graduate weighting tables | M | FR-I-02 |
| AC-L1-16 | Completion time | 1 tester (new to Wireshark) finishes core tasks in 90–120 min | W | FR-I-08 |
| AC-L1-17 | Cross-platform walkthrough | Completed on macOS Apple Silicon; Windows 11 if a machine is available | W | NFR-01 |
| AC-L1-18 | Test-status labels | Every file header or README states its tested/untested status | M | NFR-11 |

### 2.4 Phase gate

Phase 2 (MVP) is **accepted** when all **A** criteria pass in CI on the release tag, all **M** criteria are signed off by the developer (and the faculty sponsor, if available), and at least AC-L0-02 and AC-L1-16 have one completed walkthrough. Any unmet criterion requires a written waiver with a reason and a follow-up date.
