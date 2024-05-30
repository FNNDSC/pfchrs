#
# Dockerfile for pfchrs.
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build --build-arg UID=$UID -t local/pfchrs .
#
# In the case of a proxy (located at say 10.41.13.4:3128), do:
#
#    export PROXY="http://10.41.13.4:3128"
#    docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pfchrs .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pfchrs
#
# To pass an env var HOST_IP to the container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pfchrs
#
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

LABEL DEVELOPMENT="                                                         \
    docker run --rm -it                                                     \
    -p 2025:2025                                                            \
    -v $PWD/pfchrs:/app:ro  local/pfchrs /start-reload.sh                   \
"

ENV DEBIAN_FRONTEND=noninteractive


COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -U email-validator
RUN pip install -r /tmp/requirements.txt && rm -v /tmp/requirements.txt
RUN pip install tzlocal
RUN pip install ipython
# RUN pip install pydantic
# RUN pip install tabulate
# RUN pip install rich
COPY ./pfchrs /app

RUN apt update                              && \
    apt -y upgrade                          && \
    apt-get install -y apt-transport-https  && \
    apt -y install ssh iputils-ping         && \
    apt -y install vim telnet netcat-traditional procps curl gcc

# Create the 'localuser' group with specified GID
RUN groupadd -g 1102 localuser

# Create the 'localuser' user with specified UID, add to the group, and create home directory
RUN useradd -u 7748 -g localuser -m -s /bin/bash localuser

# Grant sudo privileges to the 'localuser' user
RUN apt-get update && apt-get install -y sudo
RUN echo '%localuser ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER localuser

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
RUN /home/localuser/.cargo/bin/cargo install chrs

ENV PORT=2025
EXPOSE ${PORT}
