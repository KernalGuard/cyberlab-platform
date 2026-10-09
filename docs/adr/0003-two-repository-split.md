# ADR-0003: Public platform repository + private instructor repository

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** SEC-09, FR-E-06, FR-E-08, RES-04

## Context
Students need the platform, images, and guides. Answer keys, variant logic, and the student mapping must stay confidential. The research goal favors openness and reproducibility. These pull in opposite directions.

## Decision
- `cyberlab-platform` (**public**): images, Compose, shared library, guides, tests, a public **demo** variant with its key.
- `cyberlab-instructor` (**private**): full generators, answer keys, rubrics with anchors, reference solutions, exemplars, bundle scripts. The pseudonym map is never committed in plaintext.
- For research reproducibility, a **scrubbed reference generator** (same algorithms, different indicator pools) is published at release time (OD-15).

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Single private repo | Simple | Students can't clone; no open science | Fails distribution |
| Single public repo, keys encrypted | One repo | Generator code reveals answers; encryption key management | Leakage risk |
| Git submodules | Linked versions | Confusing for students and maintainers | Complexity; private repo pins public version instead |

## Consequences
+ Clear confidentiality boundary; CI leak scan enforces it.
− Two CI pipelines; the private repo must pin a public library version. Revisit if the maintainer team grows.
