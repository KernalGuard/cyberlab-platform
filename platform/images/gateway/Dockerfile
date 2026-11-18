# cyberlab-gateway — Lab 3 reverse proxy (Debian nginx), the only container reachable
# from the student's computer (published on 127.0.0.1 only). Writes a JSON access log
# to /logs/gateway.jsonl (Lab 3 log tasks; Lab 4 evidence). Build context: platform/
#
# Status: UNTESTED as a container build (written 2026-11-17).

ARG BASE_IMAGE=ghcr.io/kernalguard/cyberlab-base:0.4.0
# The tag lives in the ARG default above; hadolint cannot see through ARGs.
# hadolint ignore=DL3006
FROM ${BASE_IMAGE}

ARG CYBERLAB_VERSION=0.4.0-dev
LABEL org.opencontainers.image.title="cyberlab-gateway" \
      org.opencontainers.image.description="CyberLab Lab 3: nginx gateway with JSON access logs" \
      org.opencontainers.image.version="${CYBERLAB_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0"

USER 0:0
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
 && apt-get install -y --no-install-recommends nginx \
 && rm -rf /var/lib/apt/lists/* \
 && install -d -o 1000 -g 1000 -m 0775 /logs
COPY images/gateway/nginx.conf /etc/cyberlab/nginx.conf
RUN chmod 0755 /etc/cyberlab && chmod 0644 /etc/cyberlab/nginx.conf \
 && nginx -t -c /etc/cyberlab/nginx.conf \
 && rm -f /logs/gateway.jsonl /tmp/nginx.pid

ENV CYBERLAB_IMAGE_VERSION=${CYBERLAB_VERSION}
USER 1000:1000
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=3s --retries=6 \
  CMD python3 -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/gateway-health', timeout=2).status == 200 else 1)"
CMD ["nginx", "-c", "/etc/cyberlab/nginx.conf", "-g", "daemon off;"]
