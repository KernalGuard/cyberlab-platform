"""Known-answer and property tests for seed derivation.

The expected digests below were computed independently with OpenSSL on
2026-10-09, not with this library:

    printf '\\x00\\x00\\x00\\x10cyberlab-seed-v1\\x00\\x00\\x00\\x14lab1-network-traffic'\\
           '\\x00\\x00\\x00\\x011\\x00\\x00\\x00\\x09K7QX-2M4P' \\
      | openssl dgst -sha256 -mac HMAC -macopt key:cyberlab-test-secret-0123456789
"""

import random

import pytest

from cyberlab_common import seeds

SECRET = b"cyberlab-test-secret-0123456789"
KAT_HMAC = "b035af80d530b22123cc9b748548cc9d77d56379a32ef21e2261724ec91599b7"
KAT_DEMO = "c5854aba159f3bb4c3462169871814163d62f8f3afd588facedc2768a89bc8e5"


def test_known_answer_hmac():
    digest = seeds.derive_seed_bytes(SECRET, "lab1-network-traffic", 1, "K7QX-2M4P")
    assert digest.hex() == KAT_HMAC


def test_known_answer_demo_seed():
    assert seeds.public_demo_seed("lab1-network-traffic", 1) == int(KAT_DEMO, 16)


def test_seed_int_matches_bytes():
    raw = seeds.derive_seed_bytes(SECRET, "lab1-network-traffic", 1, "K7QX-2M4P")
    assert seeds.derive_seed(SECRET, "lab1-network-traffic", 1, "K7QX-2M4P") == int.from_bytes(raw, "big")


@pytest.mark.parametrize("variant", ["k7qx2m4p", " K7QX-2M4P ", "K7QX 2M4P"])
def test_pseudonym_normalisation_gives_same_seed(variant):
    assert seeds.derive_seed(SECRET, "lab1", 1, variant) == seeds.derive_seed(SECRET, "lab1", 1, "K7QX-2M4P")


def test_lookalike_letters_are_mapped():
    assert seeds.normalize_pseudonym("O1IL-0000") == "0111-0000"


@pytest.mark.parametrize("bad", ["", "K7QX-2M4", "K7QX-2M4PZ", "K7QX-2M4U", "K7QX-2M4!"])
def test_invalid_pseudonyms_rejected(bad):
    with pytest.raises(ValueError):
        seeds.normalize_pseudonym(bad)


def test_every_input_changes_the_seed():
    base = seeds.derive_seed(SECRET, "lab1", 1, "AAAA-AAAA")
    assert seeds.derive_seed(SECRET + b"x", "lab1", 1, "AAAA-AAAA") != base
    assert seeds.derive_seed(SECRET, "lab2", 1, "AAAA-AAAA") != base
    assert seeds.derive_seed(SECRET, "lab1", 2, "AAAA-AAAA") != base
    assert seeds.derive_seed(SECRET, "lab1", 1, "AAAA-AAAB") != base


def test_field_boundaries_cannot_collide():
    # Without length prefixes, ("lab1", 11) and ("lab11", 1) would concatenate identically.
    assert seeds.derive_seed(SECRET, "lab1", 11, "AAAA-AAAA") != seeds.derive_seed(SECRET, "lab11", 1, "AAAA-AAAA")


def test_short_secret_rejected():
    with pytest.raises(ValueError):
        seeds.derive_seed(b"short", "lab1", 1, "AAAA-AAAA")


def test_negative_generator_major_rejected():
    with pytest.raises(ValueError):
        seeds.derive_seed(SECRET, "lab1", -1, "AAAA-AAAA")


def test_generated_pseudonyms_are_valid_and_varied():
    made = {seeds.generate_pseudonym() for _ in range(200)}
    assert len(made) == 200
    for p in made:
        assert seeds.normalize_pseudonym(p) == p


def test_generate_pseudonym_with_seeded_rng_is_reproducible():
    assert seeds.generate_pseudonym(random.Random(7)) == seeds.generate_pseudonym(random.Random(7))


def test_seeded_rng_reproducible():
    a = seeds.seeded_rng(12345)
    b = seeds.seeded_rng(12345)
    assert [a.random() for _ in range(5)] == [b.random() for _ in range(5)]
