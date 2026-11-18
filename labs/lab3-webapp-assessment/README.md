# Lab 3 — Web Application Security Assessment

> **Status: IN DEVELOPMENT (Milestone 4).** The donation site (`app/`, `db/schema.sql`), four container images, Compose file (Pattern B), verify checks and work templates are written. Demo evidence (generator 1.0.0) and the [student guide](docs/student-guide.md) (draft) are written; the integration test, CI job and instructor materials are not yet. Tested on macOS Apple Silicon 2026-11-18: all services healthy, `verify` 14/14, every weakness validated end to end.

| | |
|---|---|
| Level | Upper undergraduate (graduate extension: log analysis, remediation design) |
| Time | 120–150 minutes (target) |
| Pattern | B: gateway on 127.0.0.1:8080 only; app and database on an internal network with no route out |
| Version | 0.4.0-dev |

**Scenario.** Cedarwick Neighborhood Aid again (fictional). After the incident in Labs 1 and 2, the board wants its **donation website** assessed before it relaunches. You have a signed authorisation to test the lab copy only. Identify, validate and report the weaknesses, then fix one and prove the fix.

> **The site is intentionally vulnerable.** It runs only on your computer, bound to 127.0.0.1. Never change the port binding, never deploy it anywhere else, and never use these techniques on systems you are not authorised to test. You must sign `work/authorized-use.md` before you start.

**Containers.** `gateway` (nginx, JSON access log), `app` (Flask + gunicorn; source in `app/`, mounted read-only so you can patch it on your computer), `db` (PostgreSQL; logs every statement), and the `workstation` tools container (curl, HTTPie, Python requests) that can reach only the gateway.
