# cyberlab-webapp — Lab 3 application server (Flask + gunicorn + psycopg) for the
# intentionally vulnerable Cedarwick donation site. Build context: platform/
#
# The site's source is NOT baked in: the lab bind-mounts labs/lab3-webapp-assessment/app
# at /app (read-only), so students can patch it on their computer and restart.
#
# Status: UNTESTED as a container build (written 2026-11-17).

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.4.0
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.4.0-dev
LABEL org.opencontainers.image.title="cyberlab-webapp" \
      org.opencontainers.image.description="CyberLab Lab 3: Flask, gunicorn and psycopg for the training donation site" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-flask python3-psycopg gunicorn \
 && rm -rf /var/lib/apt/lists/* \
 && python3 -c "import flask, psycopg" \
 && command -v gunicorn \
 && install -d -o 1000 -g 1000 -m 0775 /logs /app

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION} \
    APP_LOG=/logs/app.jsonl
WORKDIR /app
USER 1000:1000
EXPOSE 5000
HEALTHCHECK --interval=10s --timeout=3s --retries=6 \
  CMD python3 -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/healthz', timeout=2).status == 200 else 1)"
CMD ["gunicorn", "--chdir", "/app", "--bind", "0.0.0.0:5000", "--workers", "2", "--worker-tmp-dir", "/tmp", "app:app"]
