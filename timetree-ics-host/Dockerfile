ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache \
  python3 py3-pip bash jq ca-certificates tzdata

RUN python3 -m venv /opt/venv \
  && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
  && /opt/venv/bin/pip install --no-cache-dir timetree-exporter

ENV PATH="/opt/venv/bin:${PATH}"

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]