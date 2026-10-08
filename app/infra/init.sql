CREATE USER market WITH PASSWORD 'market-local';
CREATE USER agent_reader WITH PASSWORD 'reader-local';
CREATE DATABASE market OWNER market;
CREATE USER langfuse WITH PASSWORD 'langfuse-local';
CREATE DATABASE langfuse OWNER langfuse;
CREATE USER litellm WITH PASSWORD 'litellm-local';
CREATE DATABASE litellm OWNER litellm;
\connect market
CREATE EXTENSION vector;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
ALTER ROLE agent_reader SET default_transaction_read_only = on;
ALTER ROLE agent_reader SET statement_timeout = '3000ms';
ALTER ROLE agent_reader SET search_path = analytics;
