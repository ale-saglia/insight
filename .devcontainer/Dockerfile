# Docker requires ARG before FROM and cannot read external files.
# .python-version is the source of truth; scripts/sync_python_version.py keeps this in sync.
ARG PYTHON_VERSION=3.12
FROM ghcr.io/astral-sh/uv:latest AS uv
FROM python:${PYTHON_VERSION}-bookworm

COPY --from=uv /uv /uvx /usr/local/bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    sudo \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN ARCH=$(uname -m) && \
    curl -sSL "https://github.com/lycheeverse/lychee/releases/latest/download/lychee-${ARCH}-unknown-linux-gnu.tar.gz" \
    | tar -xz -C /usr/local/bin lychee

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME

# Crea la virtualenv e installa le dipendenze Python
WORKDIR /workspaces/insight
COPY requirements.txt requirements-dev.txt ./
RUN uv venv .venv \
 && uv pip install --require-hashes -r requirements-dev.txt
