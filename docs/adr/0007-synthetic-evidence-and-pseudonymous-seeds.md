# ADR-0007: Synthetic deterministic evidence with HMAC-derived pseudonymous seeds

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** FR-E-01…FR-E-09, NFR-05, SEC-09

## Context
Evidence must be legal (synthetic), reproducible (for grading and research), and varied per student (academic integrity) without exposing student identity.

## Decision
1. Evidence is produced only by versioned generators. Same generator version + seed ⇒ byte-identical output (enforced by a CI double-build test).
2. `seed = HMAC-SHA256(course_secret, lab_id ‖ generator_major ‖ pseudonym)`. Pseudonyms are random 8-character base-32 IDs; the mapping to students stays with the instructor.
3. All randomness flows from a single seeded RNG; wall-clock time, UUIDs, and OS entropy are forbidden inside generators (enforced by code review and the determinism test).
4. Network identifiers use reserved ranges and domains (RFC 5737, RFC 1918, RFC 2606 `.example/.test/.invalid`); personal data is fictional.
5. Variants change values and timing, never difficulty or the number and types of findings.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| One shared dataset | Simplest | Answer sharing | Integrity |
| Public datasets (e.g., published PCAPs) | Realistic | Write-ups online; licensing; real IPs/PII | Integrity and legal |
| Seed = student ID | Simple | Exposes identity; guessable | Privacy (FERPA) |
| Live-captured traffic from lab containers | Realistic stacks | Not deterministic | Reproducibility (still usable for decoy realism checks) |

## Consequences
+ Any key regenerates from (secret, pseudonym). + Research artifacts are reproducible.
− `course_secret` must be protected and rotated each term. − Equal-difficulty variants require validation (AC-L1-02).
