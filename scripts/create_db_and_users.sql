-- create_db_and_users.sql

-- Create databases
CREATE DATABASE hs_dev;
CREATE DATABASE hs_staging;
CREATE DATABASE hs_prod;

-- Create users with passwords
CREATE USER dev_user WITH PASSWORD 'DevP@ssw0rd!2023';
CREATE USER staging_user WITH PASSWORD 'St@g1ngP@ssw0rd!2023';
CREATE USER prod_user WITH PASSWORD 'Pr0dP@ssw0rd!2023';

-- Grant privileges to users
GRANT ALL PRIVILEGES ON DATABASE hs_dev TO dev_user;
GRANT ALL PRIVILEGES ON DATABASE hs_staging TO staging_user;
GRANT ALL PRIVILEGES ON DATABASE hs_prod TO prod_user;
