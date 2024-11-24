-- On primary database
ALTER SYSTEM SET wal_level = logical;
ALTER SYSTEM SET max_replication_slots = 10;
ALTER SYSTEM SET max_wal_senders = 10;

-- Create publication
CREATE PUBLICATION main_pub FOR ALL TABLES;

-- On replica database
-- Create subscription
CREATE SUBSCRIPTION main_sub 
CONNECTION 'host=postgres-cluster-postgresql port=5432 dbname=testdb user=repl_user password=repl123' 
PUBLICATION main_pub;