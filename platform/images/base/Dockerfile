# cyberlab-base — shared foundation for every CyberLab tool image.
# Build context: platform/   (so lib/ is available to COPY)
#
#   docker build -f platform/images/base/Dockerfile -t cyberlab-base:dev platform
#
# Status: UNTESTED as a container build (the development workspace cannot pull
# base images). CI builds it natively for linux/amd64 and linux/arm64.

# Pin by digest at release time (ADR-0005), e.g. debian:trixie-slim@sha256:<digest>
ARG DEBIAN_IMAGE=debian:trixie-slim
FROM ${DEBIAN_IMAGE}

ARG CYBERLAB_VERSION=0.1.0-dev
LABEL org.opencontainers.image.title="cyberlab-base" \
      org.opencontainers.image.description="CyberLab shared base image: Debian 13, Python 3, non-root analyst user" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="CyberLab (John Jay College research project)"

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/cyberlab/lib \
    HOME=/home/analyst \
    CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION}

# Tools every lab uses. Keep this list short; role images add their own tools.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash-completion \
      bsdextrautils \
      ca-certificates \
      coreutils \
      file \
      gawk \
      grep \
      iproute2 \
      jq \
      less \
      procps \
      python3 \
      python3-yaml \
      sed \
      tree \
      unzip \
      vim-tiny \
      xxd \
      zip \
 && rm -rf /var/lib/apt/lists/*

# Non-root analyst user. UID/GID 1000 matches the first user on most Linux hosts,
# so files written to bind-mounted work/ folders stay editable by the student.
RUN groupadd --gid 1000 analyst \
 && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash analyst

COPY lib/cyberlab_common/ /opt/cyberlab/lib/cyberlab_common/
COPY images/base/bin/ /usr/local/bin/
COPY images/base/analyst.bashrc /home/analyst/.bashrc
RUN chmod 0755 /usr/local/bin/cyberlab-* \
 && chown analyst:analyst /home/analyst/.bashrc \
 && python3 -c "import cyberlab_common, yaml; print('cyberlab_common', cyberlab_common.__version__)"

WORKDIR /work
USER 1000:1000
CMD ["bash", "-l"]
