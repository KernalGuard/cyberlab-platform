# cyberlab-postgres — Lab 3 database (Debian PostgreSQL), running as UID 1000.
# Build context: platform/
#
# On first start with an empty data volume it creates the database (UTF-8; SQL_ASCII would
# make psycopg return bytes), loads /schema/schema.sql then the variant's seed
# ($SEED_SQL, from the read-only evidence mount), and starts the server. Every statement
# is logged to /logs/postgres.log (Lab 4 evidence).
#
# Status: UNTESTED as a container build (written 2026-11-17).

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.3.0
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.4.0-dev
LABEL org.opencontainers.image.title="cyberlab-postgres" \
      org.opencontainers.image.description="CyberLab Lab 3: PostgreSQL for the training donation site" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql \
 && rm -rf /var/lib/apt/lists/* \
 && ls -d /usr/lib/postgresql/*/bin \
 && install -d -o 1000 -g 1000 -m 0700 /var/lib/cyberlab/pgdata \
 && install -d -o 1000 -g 1000 -m 0775 /logs
COPY images/postgres/bin/cyberlab-pg-start /usr/local/bin/cyberlab-pg-start
RUN chmod 0755 /usr/local/bin/cyberlab-pg-start

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION} \
    PGDATA=/var/lib/cyberlab/pgdata \
    POSTGRES_DB=donations \
    SEED_SQL=/seed/seed.sql \
    SCHEMA_SQL=/schema/schema.sql
USER 1000:1000
EXPOSE 5432
HEALTHCHECK --interval=5s --timeout=3s --retries=20 CMD pg_isready -q -h 127.0.0.1 -p 5432
CMD ["cyberlab-pg-start"]
