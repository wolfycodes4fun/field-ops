# Asset Service

To run service, execute command:  
    python services/asset-service/app.py

# Workforce Service  

To run service, execute command:  
    python services/workforce-service/app.py  

# Postgres instance 🏛️

A postgres container instance can be spun up with:  
    docker compose --env-file .env up -d  
Databases can be connected to on port 5432!

# Omitting Docker Compose  

To run the setup without using Docker Compose, execute command (from project root):  
    bash scripts/migrate_schemas.sh  
    bash scripts/postgres-init.sh