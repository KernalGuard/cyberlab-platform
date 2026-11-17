# Lab 2 — Linux File-System Forensics and Evidence Examination

> **Status: IN DEVELOPMENT (Milestone 3).** Skeleton only: Compose file, verify checks, work templates and the `fs-forensics` image definition. Evidence, student guide and tests are not written yet. **UNTESTED.**

| | |
|---|---|
| Level | Intermediate undergraduate (graduate extension: ext4 journal recovery) |
| Time | 90–120 minutes (target) |
| Pattern | A: offline workstation, no network, read-only evidence, nothing mounted |
| Version | 0.3.0-dev |

**Scenario.** Cedarwick Neighborhood Aid again (fictional). After the Lab 1 network investigation, the IT contractor imaged the compromised workstation's disk and a USB stick found plugged into it. Find out how the malware arrived, how it persisted, what it staged and deleted, and whether the disk agrees with the network evidence.

**Evidence (planned).** `workstation.E01` (ext4), `usb.E01` (FAT32), `CASE-BRIEF.txt`, `MANIFEST.sha256`. Your instructor gives you your own variant, which continues **your** Lab 1 incident.

**Design notes.** Deleted files behave like a modern Linux kernel's deletions: the name and block map are gone and the content must be carved from unallocated space (see [`docs/spikes/ext4-kernel-deletion/`](../../docs/spikes/ext4-kernel-deletion/README.md)).
