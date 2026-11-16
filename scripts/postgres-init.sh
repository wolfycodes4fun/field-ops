#!/bin/bash
# Description: This script pulls the Docker image for postgres and runs it with
# the set environment variables to carry out connectivity to the asset service (initially)

if [-f .env]; then
    source .env
fi

docker pull "postgres:${POSTGRES_IMAGE_TAG}"

docker run -d \
    -p 5432:5432 \
    --mount type=bind,source=./scripts/init.sql,target=/tmp/db_scripts/init.sql:ro \
    --mount  type=bind,source=./scripts/init-postgre-sql.sh,target=/docker-entrypoint-initdb.d/init-postgre-sql.sh \
    -e POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    -e POSTGRES_USER="${POSTGRES_USER}" \
    "postgres:${POSTGRES_IMAGE_TAG}"
