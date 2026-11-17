# cyberlab-fs-forensics — Lab 2 file-system forensics workstation.
# Build context: platform/
#
#   docker build -f platform/images/fs-forensics/Dockerfile -t ghcr.io/kernalguard/cyberlab-fs-forensics:dev platform
#   (pulls the base image below; override with --build-arg BASE_IMAGE=...)
#
# Reads disk images only: The Sleuth Kit, debugfs (read-only use), mtools, libewf tools,
# binutils (strings), perl (needed by TSK's mactime). No mounting (ADR-0008): no FUSE, no loop devices, no capabilities.
#
# KNOWN ISSUE (found 2026-11-17, macOS Apple Silicon): with Debian 13's libewf 20140816,
# every TSK tool prints correct output from an E01 and then segfaults on exit (status 139).
# Raw images work. The Lab 2 workflow therefore exports raw working copies with ewfexport
# into /work and runs TSK on those (ewfinfo/ewfverify/ewfexport themselves are fine).
#
# Status: builds in CI (amd64 + arm64); runs on macOS Apple Silicon, 2026-11-17.

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.2.1
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.3.0-dev
LABEL org.opencontainers.image.title="cyberlab-fs-forensics" \
      org.opencontainers.image.description="CyberLab Lab 2: The Sleuth Kit, e2fsprogs, mtools and libewf tools on the CyberLab base" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      sleuthkit \
      e2fsprogs \
      mtools \
      ewf-tools \
      binutils \
      perl \
 && rm -rf /var/lib/apt/lists/* \
 && fls -V \
 && command -v debugfs ewfinfo ewfverify ewfexport mdir \
 && ldd "$(command -v fls)" | grep -q libewf \
 && command -v strings \
 && mactime -V

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION}
WORKDIR /work
USER 1000:1000
CMD ["bash", "-l"]
