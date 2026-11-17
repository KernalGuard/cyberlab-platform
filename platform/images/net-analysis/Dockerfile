# cyberlab-net-analysis — Lab 1 analysis workstation (TShark + capture utilities).
# Build context: platform/
#
#   docker build -f platform/images/net-analysis/Dockerfile -t ghcr.io/kernalguard/cyberlab-net-analysis:dev platform
#   (pulls the base image below; override with --build-arg BASE_IMAGE=...)
#
# Reads capture files only: no capabilities, no network, no live capture (ADR-0011).
# Wireshark GUI is used on the host against the shared work/ and evidence/ folders.
#
# Status: built and tested 2026-11-17 on macOS Apple Silicon and in CI (amd64 + arm64);
# ~100 MB compressed (AC-P-02 target <= 350 MB).

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.2.0
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.1.0-dev
LABEL org.opencontainers.image.title="cyberlab-net-analysis" \
      org.opencontainers.image.description="CyberLab Lab 1: TShark, capinfos, editcap, mergecap on the CyberLab base" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# tshark asks whether non-root users may capture; preseed "no" (we never capture live).
RUN echo "wireshark-common wireshark-common/install-setuid boolean false" | debconf-set-selections \
 && apt-get update \
 && apt-get install -y --no-install-recommends tshark \
 && rm -rf /var/lib/apt/lists/* \
 && tshark --version > /dev/null \
 && command -v capinfos editcap mergecap

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION}
WORKDIR /work
USER 1000:1000
CMD ["bash", "-l"]
