"""Shared utilities for CyberLab laboratories.

Modules
-------
manifest  Create and verify SHA-256 evidence manifests.
seeds     Pseudonym generation and HMAC-based seed derivation for per-student variants.
verify    Environment self-check framework used by every lab's ``verify`` service.
findings  Validation of student ``findings.json`` submissions.
reset     Restore a lab's ``work/`` directory from its template.

The package depends only on the Python standard library plus PyYAML
(Debian package ``python3-yaml``), so it runs in the base image without pip.
"""

__version__ = "0.1.0"
