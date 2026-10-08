SELECT 'CREATE USER litellm WITH PASSWORD ''litellm-local''' WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname='litellm')\gexec
SELECT 'CREATE DATABASE litellm OWNER litellm' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='litellm')\gexec
