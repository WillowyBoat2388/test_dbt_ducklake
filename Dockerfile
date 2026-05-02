FROM python:3.11-slim

WORKDIR src

# copy over python dependencies file
COPY ./src /src

# install additional tools you might need, e.g.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && uv python install
    
# add execute permissions to the entrypoint script
RUN chmod -R 755 ./scripts

ENTRYPOINT [ "/bin/sh", "-c"]
CMD ["scripts/run.sh"]