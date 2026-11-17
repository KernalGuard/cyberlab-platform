# Lab 2 — Linux File-System Forensics and Evidence Examination

> **Status: IN DEVELOPMENT (Milestone 3).** Demo evidence (generator 1.0.0, 2026-11-17), Compose file, verify checks, work templates and the `fs-forensics` image (builds in CI on amd64 + arm64). Student guide, integration test and instructor materials are not written yet. The Lab 2 container has **not** yet been run with this evidence.

| | |
|---|---|
| Level | Intermediate undergraduate (graduate extension: ext4 journal recovery) |
| Time | 90–120 minutes (target) |
| Pattern | A: offline workstation, no network, read-only evidence, nothing mounted |
| Version | 0.3.0-dev |

**Scenario.** Cedarwick Neighborhood Aid again (fictional). After the Lab 1 network investigation, the IT contractor imaged the compromised workstation's disk and a USB stick found plugged into it. Find out how the malware arrived, how it persisted, what it staged and deleted, and whether the disk agrees with the network evidence.

**Evidence.** `evidence/` holds the public **demo** variant, which continues the Lab 1 demo incident: `workstation.E01` (ext4, 128 MiB), `usb.E01` (FAT32, 64 MiB), `CASE-BRIEF.txt`, `MANIFEST.sha256` (≈ 390 KB in total). For graded work your instructor gives you your own variant, which continues **your** Lab 1 incident.

**Design notes.** Deleted files behave like a modern Linux kernel's deletions: the name and block map are gone and the content must be carved from unallocated space (see [`docs/spikes/ext4-kernel-deletion/`](../../docs/spikes/ext4-kernel-deletion/README.md)).
