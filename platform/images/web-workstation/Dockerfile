# cyberlab-web-workstation — Lab 3 assessment workstation: curl, HTTPie, Python requests.
# Joins only the lab's internal "edge" network, from which it can reach the gateway and
# nothing else. Build context: platform/
#
# Status: UNTESTED as a container build (written 2026-11-17).

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.3.0
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.4.0-dev
LABEL org.opencontainers.image.title="cyberlab-web-workstation" \
      org.opencontainers.image.description="CyberLab Lab 3: curl, HTTPie and Python requests" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl httpie python3-requests \
 && rm -rf /var/lib/apt/lists/* \
 && command -v curl http \
 && python3 -c "import requests"

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION} \
    SITE=http://gateway:8080
WORKDIR /work
USER 1000:1000
CMD ["bash", "-l"]
