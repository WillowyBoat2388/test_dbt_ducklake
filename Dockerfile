FROM python:3.11-slim

WORKDIR /src

# copy over python dependencies file
COPY ./src /src

COPY .venv pyproject.toml main.py .env uv.lock .python-version /src/

# install additional tools you might need, e.g.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && cp /root/.local/bin/uv /usr/local/bin/uv \
    && uv python install
    
    
# RUN uv python install
    
# add execute permissions to the entrypoint script
RUN chmod -R 755 ./scripts

ENTRYPOINT [ "/bin/sh", "-c"]
CMD ["scripts/run.sh"]