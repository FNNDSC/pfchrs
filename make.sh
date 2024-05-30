#!/usr/bin/env bash
# =========================================================
# STEP 0: BUILD a local docker image
# =========================================================
docker build -t local/pfchrs .
# =========================================================
# STEP 1: RUN the docker compose file to start container
# =========================================================
docker compose up -d --remove-orphans
# =========================================================
