# cyberlab-ir-workstation — Lab 4 incident-response workstation (union of the Lab 1-3 analysis tools).
# Build context: platform/
#
#   docker build -f platform/images/ir-workstation/Dockerfile -t ghcr.io/kernalguard/cyberlab-ir-workstation:dev platform
#   (pulls the base image below; override with --build-arg BASE_IMAGE=...)
#
# Offline analysis only (Pattern A, ADR-0006): TShark for the capture, The Sleuth Kit and
# libewf tools for the laptop image (no mounting, ADR-0008), jq and sqlite3 for logs and
# browser databases, mactime for timelines. No capabilities, no network, no live capture.
# As in Lab 2, TSK runs on raw working copies exported with ewfexport (Debian libewf crash on exit).
#
# Status: built and tested 2026-11-18 on macOS Apple Silicon; CI amd64 + arm64. Released from v0.5.0.

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.5.0
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.5.0-dev
LABEL org.opencontainers.image.title="cyberlab-ir-workstation" \
      org.opencontainers.image.description="CyberLab Lab 4: TShark, The Sleuth Kit, libewf tools, jq and sqlite3 on the CyberLab base" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
# tshark asks whether non-root users may capture; preseed "no" (we never capture live).
RUN echo "wireshark-common wireshark-common/install-setuid boolean false" | debconf-set-selections \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      tshark \
      sleuthkit \
      ewf-tools \
      binutils \
      perl \
      sqlite3 \
 && rm -rf /var/lib/apt/lists/* \
 && tshark --version > /dev/null \
 && fls -V \
 && command -v capinfos ewfinfo ewfverify ewfexport strings sqlite3 jq \
 && mactime -V

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION}
WORKDIR /work
USER 1000:1000
CMD ["bash", "-l"]
