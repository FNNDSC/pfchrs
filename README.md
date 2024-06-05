# `pfchrs`

[![Build](https://github.com/FNNDSC/pfchrs/actions/workflows/build.yml/badge.svg)](https://github.com/FNNDSC/pfchrs/actions/workflows/build.yml)

*a FAST API REST service about an embedded chrs application -- basically a web-based chrs*

## Abstract

`pfchrs` is a FastAPI application thought experiment that provides REST services about an "embedded" `chrs` client. This repo is part of an experiment into examining the feasibility of offering `chrs` via web to a bundled ChRIS ecosystem instantiation.


## Conceptualization

A fuller experience closer to the imagined goal is to use the `[chrs_web](https://github.com/FNNDSC/chrs_web)`.


## `pfchrs` Deployment

### local build

To build a local version, clone this repo and then

```bash
set UID=$(id -u) # for bash/zsh
set UID (id -u)  # for fish shell
docker build --build-arg UID=UID -t local/pfchrs .
```

### dockerhub

To use the version available on dockerhub (note, might not be available at time of reading):

```bash
docker pull fnndsc/pfchrs
```

### running

To start the services

```bash
SESSIONUSER=localuser
docker run                                  \
        --env SESSIONUSER=$SESSIONUSER      \
        --name pfchrs --rm -it -d           \
        -p 2025:2025                        \
        local/pfchrs /start-reload.sh
```

To start with source code debugging and live refreshing:

```bash
SESSIONUSER=localuser
docker run                                  \
        --env SESSIONUSER=$SESSIONUSER      \
        --name pfchrs --rm -it -d           \
        -p 2025:2025                        \
        -v $PWD/pfchrs:/app:ro
        local/pfchrs /start-reload.sh
```

(note if you pulled from dockerhub, use `fnndsc/pfchrs` instead of `local/pfchrs`)

## `pfchrs` Usage

### POST a chrs command

`pfchrs` provides a POST endpoint that accepts a command to execute internally. A "vault" is used to provide credentialling to a connected CUBE.

```html
POST :2025/api/v1/chrs/{cmd}
```


_-30-_
