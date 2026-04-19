ARG BUILD_FROM=ghcr.io/home-assistant/base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    python3 \
    py3-pip \
    bash \
    jq \
    ca-certificates \
    tzdata \
    ffmpeg

RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir \
        fastapi \
        uvicorn[standard] \
        httpx \
        pydantic

ENV PATH="/opt/venv/bin:${PATH}"

COPY pa_system_app /opt/pa_system_app
COPY run.sh /run.sh
RUN chmod +x /run.sh

WORKDIR /opt/pa_system_app
CMD ["/run.sh"]
