#!/bin/bash

# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql


# Define the PostgreSQL superuser from the .env file
PG_SUPERUSER="${PG_SUPERUSER}"

#psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -c "CREATE ROLE $PG_SUPERUSER WITH LOGIN SUPERUSER PASSWORD '$SUPERUSER_PASSWORD';"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Superuser '$PG_SUPERUSER' created successfully."
else
    echo "Failed to create superuser '$PG_SUPERUSER'."
fi

# Create the SQL script dynamically with user input from .env
cat <<EOF > create_db_and_users.sql
-- create_db_and_users.sql

-- Create databases
CREATE DATABASE ${DB_NAME_DEV};
CREATE DATABASE ${DB_NAME_STAGING};
CREATE DATABASE ${DB_NAME_PROD};

-- Create users with passwords
CREATE USER dev_user WITH PASSWORD '${DEV_PASSWORD}';
CREATE USER staging_user WITH PASSWORD '${STAGING_PASSWORD}';
CREATE USER prod_user WITH PASSWORD '${PROD_PASSWORD}';

-- Grant privileges to users
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME_DEV} TO dev_user;
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME_STAGING} TO staging_user;
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME_PROD} TO prod_user;
EOF

# Execute the SQL script
sudo -u $PG_SUPERUSER  psql  -f create_db_and_users.sql 

# Clean up the SQL script
#rm create_db_and_users.sql
