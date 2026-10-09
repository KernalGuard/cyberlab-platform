# Milestone 1 Proposal — Platform Foundation + Lab 0

**For approval.** Week 1, 2026-10-12 → 2026-10-16. Nothing in this milestone is built until you approve it.

## 1. Goal

Deliver the shared platform skeleton and a complete Lab 0, so that (a) any student machine can be checked for readiness and (b) Lab 1 can be built in Weeks 2–3 purely as content.

## 2. Deliverables

| # | Deliverable | Path |
|---|---|---|
| 1 | Base image (Debian 13 slim, Python 3.13, user `analyst` UID 1000, `cyberlab_common` installed) | `platform/images/base/Dockerfile` |
| 2 | Shared library: manifest create/verify, HMAC seed derivation, verify framework, findings schema | `platform/lib/cyberlab_common/` |
| 3 | Security baseline Compose fragment | `platform/compose/security-baseline.yaml` |
| 4 | Lab 0 image, Compose file, `verify` service, sample evidence + manifest | `labs/lab0-orientation/` |
| 5 | Lab 0 student guide (all 16 sections; 30–45 min) | `labs/lab0-orientation/docs/student-guide.md` |
| 6 | Per-OS install guides + one-page pre-flight checklist | `docs/student/` |
| 7 | CI: hadolint, ruff, pytest, multi-arch build (native arm64 runner), Compose policy tests, Trivy scan | `.github/workflows/ci.yml` |
| 8 | Dev container draft for the browser fallback | `.devcontainer/devcontainer.json` |
| 9 | Repo hygiene: README, LICENSE(s), SECURITY, CONTRIBUTING, `.gitattributes`, CHANGELOG | repo root |
| 10 | ADRs 0001–0011 moved from *Proposed* to *Accepted* (or revised per your feedback) | `docs/adr/` |

### Lab 0 content outline

1. Verify Docker works; read `docker version` and `docker info`; check VM memory.
2. Pull an image; run, list, stop, and remove containers; understand images vs. containers.
3. Shell basics inside the workstation: `pwd`, `ls -la`, `cd`, `cat`, `less`, `file`, `grep`, pipes.
4. Hashing: compute SHA-256, compare against a manifest, detect a deliberately altered decoy file.
5. Read-only evidence: attempt to modify `/evidence` and interpret the error.
6. Troubleshooting drill: diagnose three staged problems (wrong directory, port/name conflict, stopped container).
7. Clean up: `docker compose down`, verify nothing remains.

**Bloom levels:** Remember / Understand / Apply. **Deliverable:** a short `lab0-check.json` produced by `verify`, uploaded to the LMS as proof of a working environment.

## 3. Out of scope for Milestone 1

Lab 1 content; seeded variant bundles for the LMS; Codespaces testing (Week 4); any cloud resources.

## 4. Acceptance criteria

- [ ] CI passes on `main`: lint, unit tests (≥ 90% line coverage on `manifest.py` and `seeds.py`), and a multi-arch build.
- [ ] Policy tests pass: non-root, `cap_drop: ALL`, `no-new-privileges`, limits present, `network_mode: none`, no privileged.
- [ ] `seeds.py` passes known-answer tests (fixed secret + pseudonym → fixed seed).
- [ ] Lab 0 `verify` passes on your Mac (Apple Silicon) — **you run this; I'll provide the exact commands and expected output.**
- [ ] Lab 0 guide commands pass a scripted transcript test in CI.
- [ ] One person new to Docker completes Lab 0 in ≤ 45 minutes (can slip to Week 2).

## 5. Testing transparency

| What | Where it can be tested |
|---|---|
| Python library, generators, Sleuth Kit / TShark logic | **This AI workspace** (packages install natively) |
| Docker image builds and Compose runs | **Not here**: this workspace's egress policy blocks container registries (Docker Hub, GCR mirror, ECR Public all returned 403). Tested in **GitHub Actions** and on **your Mac**. |
| Windows | Only if you or a peer has a Windows machine (OD-09) |

Every file will be marked *tested (where, when)* or *UNTESTED* accordingly.

## 6. What I need from you to start

1. **Approve** this milestone (or request changes).
2. **GitHub owner** for the repos: personal account or a new organization (OD-03).
3. Confirm the **licenses** (OD-07), or tell me to hold them as placeholders.
4. Optionally **connect a folder** on your Mac in the Claude desktop app so I can write the repo straight into it; otherwise I'll keep delivering it as a zip.
