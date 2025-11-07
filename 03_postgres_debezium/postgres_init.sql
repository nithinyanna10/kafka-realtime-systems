-- Bank Database Initialization
-- This script runs when PostgreSQL container starts

-- Enable logical replication (required for Debezium)
ALTER SYSTEM SET wal_level = logical;
SELECT pg_reload_conf();

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    account INT NOT NULL,
    amount FLOAT NOT NULL,
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index on account for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account);

-- Create an index on timestamp for time-based queries
CREATE INDEX IF NOT EXISTS idx_transactions_ts ON transactions(ts);

-- Insert some sample data (optional - for testing)
INSERT INTO transactions (account, amount) VALUES
    (1001, 150.50),
    (1002, -75.25),
    (1003, 200.00),
    (1001, -50.00),
    (1002, 300.75);

-- Grant necessary permissions for Debezium
-- Debezium needs replication privileges
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'debezium') THEN
        CREATE USER debezium WITH REPLICATION PASSWORD 'debezium';
    END IF;
END
$$;

-- Grant connect and select permissions
GRANT CONNECT ON DATABASE bankdb TO debezium;
GRANT USAGE ON SCHEMA public TO debezium;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO debezium;

