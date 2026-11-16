# Asset Service

Initally, run only ONCE:  
    cd services/asset-service/  
    bash scripts/migrate-schema.sh  

To run service, execute command:  
    python services/asset-service/app.py

# Workforce Service  

Initially, run only ONCE:  
    cd services/workforce-service/  
    bash scripts/migrate-schema.sh  

To run service, execute command:  
    python services/workforce-service/app.py  

# Postgres instance 🏛️

A postgres container instance can be spun up with:  
    docker compose --env-file .env up -d  
Databases can be connected to on port 5432!

# Omitting Docker Compose  

To run the setup without using Docker Compose, execute command (from project root):  
    bash scripts/postgres-init.sh