FROM python:3.11-slim

WORKDIR /app

# copy over python dependencies file
COPY . /app



# install additional tools you might need, e.g.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && cp /root/.local/bin/uv /usr/local/bin/uv \
    && uv python install
    
    
    
# add execute permissions to the entrypoint script
RUN chmod -R 755 ./src/scripts

ENTRYPOINT [ "/bin/sh", "-c"]
CMD ["./src/scripts/run.sh"]