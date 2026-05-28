DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'sewa') THEN
      CREATE ROLE sewa LOGIN PASSWORD 'sewa';
   END IF;
END
$do$;
SELECT 'CREATE DATABASE offline_sewa OWNER sewa'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'offline_sewa')\gexec
GRANT ALL PRIVILEGES ON DATABASE offline_sewa TO sewa;
