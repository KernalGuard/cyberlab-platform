-- Cedarwick donation site schema (CyberLab Lab 3). SYNTHETIC; all data is fictional.
-- Loaded once into an empty database, before the variant's seed.sql.

CREATE TABLE donors (
    id            SERIAL PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,
    full_name     TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE staff (
    id            SERIAL PRIMARY KEY,
    username      TEXT NOT NULL UNIQUE,
    full_name     TEXT NOT NULL,
    role          TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE donations (
    id           SERIAL PRIMARY KEY,
    receipt_no   INTEGER NOT NULL UNIQUE,
    donor_id     INTEGER NOT NULL REFERENCES donors(id),
    amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
    fund         TEXT NOT NULL,
    card_last4   TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL
);

CREATE INDEX donations_donor ON donations(donor_id);

CREATE TABLE site_settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
