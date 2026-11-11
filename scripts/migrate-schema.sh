#!/bin/bash
# Description: The following script is responsible for mitigating the drift between
# the current database schema and the schema we intend to publish in the future. (A sort
# of complicated way of saying upgrading the database schema to what we need with any
# future changes). This file needs to be run individually for each service and run from within
# the service folder.

COMMIT_MESSAGE="${1:-minor changes}"

source ../../venv/Scripts/activate

python -m pip install -r ../../requirements.txt

# Needs to be run once to initialize the migration repository (EXACTLY ONCE & NEVER AGAIN)
# python -m flask --app app db init

# Updates the /migrations folder with incoming changes
python -m flask --app app db migrate -m "${COMMIT_MESSAGE}"
python -m flask --app app db upgrade