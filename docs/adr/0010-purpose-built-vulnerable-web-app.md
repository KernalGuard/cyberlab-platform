# ADR-0010: Purpose-built vulnerable web application

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** SEC-06, SEC-08, EDU-04, FR-E-02

## Context
Lab 3 needs a web application with known weaknesses; Lab 4 needs the same application's logs as incident evidence, consistent with a scripted narrative.

## Decision
Build a small purpose-built Flask + PostgreSQL application ("fictional organization portal") with 4–5 deliberately introduced, documented weaknesses, structured JSON logging, seedable data, and a "patched" configuration flag for the remediation exercise.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| DVWA | Classic, simple | Public walkthroughs everywhere; PHP; limited logging | Integrity, log realism |
| OWASP Juice Shop | Rich, modern, maintained | Large; many published solutions; challenge-centric rather than investigation-centric | Integrity; harder to correlate with Lab 4 |
| WebGoat | Strong pedagogy | Java, heavier RAM | Resource budget |

## Consequences
+ Control over weaknesses, logs, data, and seeds; reused directly in Lab 4. − We own its maintenance and must ensure the weaknesses are exactly the intended ones (code review + tests). Juice Shop remains a recommended optional extension for advanced students.
