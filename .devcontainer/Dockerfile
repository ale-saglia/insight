# PYTHON_VERSION duplicated here: Docker requires ARG before FROM and cannot read external files.
# Keep in sync with /versions.env.
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    build-essential \
    sudo \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

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
COPY requirements.txt .
RUN python3 -m venv .venv \
 && .venv/bin/pip install --upgrade pip \
 && .venv/bin/pip install -r requirements.txt
