#!/bin/bash
# Description: This script is meant to be executed as an init script in the postgres container. It will be mounted
# on to the path '/docker-entrypoint-initdb.d/init-postgre-sql.sh'. A separate bash script like this was written
# because env variables aren't directly parsed by an SQL script in a postgres container.

set -e

psql -v ON_ERROR_STOP=1 \
    --username "${POSTGRES_USER}" \
    -v db_user="${DB_USER}" -v db_password="${DB_PASSWORD}" \
    -v asset_database="${ASSET_DB_NAME}" \
    -v work_order_database="${WORK_ORDER_DB_NAME}" \
    -v workforce_database="${WORKFORCE_DB_NAME}" \
    -f /tmp/db_scripts/init.sql
