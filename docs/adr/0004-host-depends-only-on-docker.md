# ADR-0004: Host depends only on Docker; all scripts run in containers

- **Status:** Accepted (2026-10-09, by developer; faculty review pending)
- **Date:** 2026-10-09
- **Related requirements:** FR-P-05, NFR-01, NFR-04

## Context
The most common lab failures on mixed student hardware come from host differences: Windows lacking Bash, wrong Python versions, CRLF line endings, missing `make`, PATH problems.

## Decision
Students need **only Docker with Compose v2** (Git optional — a zip download works). Every helper (`verify`, `reset`, checkers) is a Compose service or runs inside the workstation container. An optional `labctl` convenience CLI may exist but is never required by any guide.

## Alternatives considered
| Option | Pros | Cons | Why not chosen |
|---|---|---|---|
| Bash scripts + Makefile on host | Familiar | Breaks on Windows PowerShell | Portability |
| Host Python CLI | Rich UX | Python install/version support burden | Extra dependency |
| PowerShell + Bash duplicates | Native on each OS | Double maintenance; divergence | Maintainability |

## Consequences
+ One set of commands for all OSes. + Scripts are tested in the same image students run.
− Commands are slightly longer (`docker compose run --rm verify`). Lab 0 teaches them explicitly.
