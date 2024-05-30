
# Dockerfile for pfmdb to deploy to openshift.
# This can be deployed using source to image or image based deployment on openshift
# To do - We need to use RHEL UBI image and make necessary improvements if required.

# Refernce: https://github.com/grdryn/pfms/blob/openshift/Dockerfile

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

LABEL DEVELOPMENT="                                                         \
    docker run --rm -it                                                     \
    -p 2024:2024                                                            \
    -v $PWD/pfms:/app:ro  local/pfms /start-reload.sh                      \
"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update                              && \
    apt -y upgrade                          && \
    apt-get install -y apt-transport-https  && \
    apt -y install ssh iputils-ping         && \
    apt -y install vim telnet netcat-traditional procps && \
    apt -y install gcc python3-dev


COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -U email-validator
RUN pip install -r /tmp/requirements.txt && rm -v /tmp/requirements.txt
# RUN pip install tzlocal
# RUN pip install ipython
# RUN pip install pydantic
# RUN pip install tabulate
# RUN pip install rich
COPY ./pfms /app

# In OpenShift, an arbitrary UID will be assigned, with HOME set to /
# It will be part of the root group though, and that group will need
# to be able to write to these locations.
RUN for d in spleenseg/ spleenseg/analysis/ spleenseg/models/ .config/ ; do \
      mkdir /${d} /app/${d} ; \
      chgrp -R 0 /${d} /app/${d} ; \
      chmod -R g+rwX /${d} /app/${d} ; \
      chown -R 1001 /${d} /app/${d} ; \
    done

USER 1001
RUN mkdir -p /tmp/matplotlib /tmp/hf_home

ENV MPLCONFIGDIR=/tmp/matplotlib
ENV HF_HOME=/tmp/hf_home
ENV PORT=2024
EXPOSE ${PORT}