CREATE DATABASE iggnpk;
CREATE USER iggnpk WITH PASSWORD 'mI@haUx9q|';
ALTER ROLE iggnpk SET client_encoding TO 'utf8';
ALTER ROLE iggnpk SET default_transaction_isolation TO 'read committed';
ALTER ROLE iggnpk SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE iggnpk TO iggnpk;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO iggnpk;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO iggnpk;