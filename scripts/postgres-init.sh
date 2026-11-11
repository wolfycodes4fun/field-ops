#!/bin/bash
# Description: This script pulls the Docker image for postgres and runs it with
# the set environment variables to carry out connectivity to the asset service (initially)

POSTGRES_IMAGE_TAG="${1:-17-alpine}"
POSTGRES_DB_NAME="${2:-assets}"

docker pull "postgres:${POSTGRES_IMAGE_TAG}"

docker run -d \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    -e POSTGRES_USER=microapp \
    -e POSTGRES_DB="${POSTGRES_DB_NAME}" \
    "postgres:${POSTGRES_IMAGE_TAG}"
