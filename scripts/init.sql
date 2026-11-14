SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'db_user') AS role_does_not_exist
\gset

\if :role_does_not_exist
    CREATE ROLE :"db_user" WITH LOGIN PASSWORD :'db_password';
\endif

SELECT NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'asset_database') AS database_does_not_exist
\gset

\if :database_does_not_exist
    CREATE DATABASE :"asset_database" OWNER :"db_user";
\endif

SELECT NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'work_order_database') AS database_does_not_exist
\gset

\if :database_does_not_exist
    CREATE DATABASE :"work_order_database" OWNER :"db_user";
\endif

SELECT NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'workforce_database') AS database_does_not_exist
\gset

\if :database_does_not_exist
    CREATE DATABASE :"workforce_database" OWNER :"db_user";
\endif
