FROM python:3.12-slim

# use this Dockerfile to install additional tools you might need, e.g.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh


    