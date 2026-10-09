# ADR-0001: Record architecture decisions

- **Status:** Proposed
- **Date:** 2026-10-09
- **Deciders:** S. Vadon (developer); faculty sponsor (TBD)
- **Related requirements:** RES-05, NFR-07

## Context
This is both a teaching platform and a candidate applied-research artifact. Reviewers (faculty, IRB, peer reviewers) will ask *why* technologies were chosen, not only *what* was built. Decisions made by one developer with AI assistance are easily lost or rationalized after the fact.

## Decision
Record every decision that affects security, portability, pedagogy, evidence integrity, or cost as an ADR in `docs/adr/`, numbered sequentially, written **at the time of the decision**, including alternatives considered and any evidence (spikes, measurements).

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Design rationale only in the final report | Less overhead | Hindsight bias; untraceable | Weak for research reproducibility |
| Wiki pages | Easy editing | Not versioned with code; drift | Decisions must be versioned with the code they govern |

## Consequences
+ Traceable design rationale for the methodology chapter. + Onboarding for future maintainers.
− About 15–30 minutes of writing per decision. Revisit if ADRs are being written after the fact (the process is not working).
