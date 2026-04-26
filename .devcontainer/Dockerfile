# RUBY_VERSION duplicated here: Docker requires ARG before FROM and cannot read external files.
# Keep in sync with /versions.env.
ARG RUBY_VERSION=3.3
FROM ruby:${RUBY_VERSION}-bookworm

# All other versions come from /versions.env (build context is repo root)
COPY versions.env /tmp/versions.env

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    perl \
    python3 \
    build-essential \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN . /tmp/versions.env \
    && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN . /tmp/versions.env && gem install bundler:${BUNDLER_VERSION}

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown -R $USERNAME:$USERNAME /usr/local/bundle

USER $USERNAME
