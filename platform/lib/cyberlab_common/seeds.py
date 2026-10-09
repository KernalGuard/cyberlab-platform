"""Pseudonyms and deterministic seed derivation for per-student evidence variants.

Design (ADR-0007)
-----------------
* Each student receives a random **pseudonym** such as ``K7QX-2M4P``. It is never
  derived from a name, email, or student ID. The pseudonym → student mapping is
  kept only by the instructor.
* The seed for a lab variant is::

      HMAC-SHA256(course_secret, "cyberlab-seed-v1" | lab_id | generator_major | pseudonym)

  where each field is length-prefixed so different field splits can never
  collide. Without ``course_secret`` a pseudonym cannot be turned into a seed,
  so students cannot regenerate an answer key from public generator code.
* All randomness inside a generator must come from :func:`seeded_rng`; wall-clock
  time, ``uuid4`` and ``os.urandom`` are forbidden in generators.

Note: ``random.Random`` produces identical sequences for the same seed on every
platform for a given CPython minor version. Generators therefore pin Python 3.13
(the Debian 13 system Python) and CI checks reproducibility on amd64 and arm64.
"""

from __future__ import annotations

import hashlib
import hmac
import random
import secrets

# Crockford base-32 alphabet: no I, L, O, U, so pseudonyms are easy to read aloud.
PSEUDONYM_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
PSEUDONYM_LENGTH = 8
_DOMAIN_TAG = b"cyberlab-seed-v1"


def generate_pseudonym(rng: secrets.SystemRandom | random.Random | None = None) -> str:
    """Return a random pseudonym formatted ``XXXX-XXXX``.

    Uses the OS CSPRNG by default. Passing a seeded ``random.Random`` is allowed
    only in tests.
    """
    source = rng or secrets.SystemRandom()
    chars = "".join(source.choice(PSEUDONYM_ALPHABET) for _ in range(PSEUDONYM_LENGTH))
    return f"{chars[:4]}-{chars[4:]}"


def normalize_pseudonym(pseudonym: str) -> str:
    """Upper-case, strip separators, map look-alike letters, and validate."""
    cleaned = pseudonym.strip().upper().replace("-", "").replace(" ", "")
    cleaned = cleaned.replace("O", "0").replace("I", "1").replace("L", "1")
    if len(cleaned) != PSEUDONYM_LENGTH or any(c not in PSEUDONYM_ALPHABET for c in cleaned):
        raise ValueError(f"invalid pseudonym: {pseudonym!r}")
    return f"{cleaned[:4]}-{cleaned[4:]}"


def _field(value: bytes) -> bytes:
    return len(value).to_bytes(4, "big") + value


def derive_seed_bytes(course_secret: bytes, lab_id: str, generator_major: int, pseudonym: str) -> bytes:
    """Return the 32-byte HMAC-SHA256 seed for one student's lab variant."""
    if len(course_secret) < 16:
        raise ValueError("course_secret must be at least 16 bytes")
    if generator_major < 0:
        raise ValueError("generator_major must be non-negative")
    message = b"".join(
        _field(part)
        for part in (
            _DOMAIN_TAG,
            lab_id.encode("utf-8"),
            str(generator_major).encode("ascii"),
            normalize_pseudonym(pseudonym).encode("ascii"),
        )
    )
    return hmac.new(course_secret, message, hashlib.sha256).digest()


def derive_seed(course_secret: bytes, lab_id: str, generator_major: int, pseudonym: str) -> int:
    """Return the seed as a 256-bit integer (suitable for ``random.Random``)."""
    return int.from_bytes(derive_seed_bytes(course_secret, lab_id, generator_major, pseudonym), "big")


def public_demo_seed(lab_id: str, generator_major: int) -> int:
    """Seed for the public ``demo`` variant, whose evidence and key are published.

    Derived from a fixed, public secret so anyone can reproduce it.
    """
    return int.from_bytes(
        hashlib.sha256(_field(_DOMAIN_TAG) + _field(b"demo") + _field(lab_id.encode()) +
                       _field(str(generator_major).encode())).digest(),
        "big",
    )


def seeded_rng(seed: int) -> random.Random:
    """The only RNG generators are allowed to use."""
    return random.Random(seed)
