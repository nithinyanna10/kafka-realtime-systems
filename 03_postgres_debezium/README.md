# 🔄 Debezium + PostgreSQL CDC (Change Data Capture)

Real-time database change streaming from PostgreSQL to Kafka using **Debezium**.

## 🎯 What is Debezium?

**Debezium** is a **Change Data Capture (CDC)** platform that captures database changes in real-time and streams them to Kafka topics.

### 🤔 What is Change Data Capture (CDC)?

**CDC** is a technique to detect and capture changes in a database (INSERTs, UPDATEs, DELETEs) and stream them to other systems in real-time.

**Traditional Approach:**
```
Application writes to DB → Other systems poll DB → Slow, inefficient
```

**CDC Approach:**
```
Application writes to DB → Debezium captures changes → Streams to Kafka → Real-time!
```

### 🏗️ How Debezium Works

```
┌─────────────┐
│ PostgreSQL  │
│  Database   │
│             │
│ transactions│
│   table     │
└──────┬──────┘
       │
       │ WAL (Write-Ahead Log)
       │ PostgreSQL logs all changes here
       │
       ▼
┌─────────────┐
│  Debezium   │
│  Connector  │
│             │
│ • Reads WAL │
│ • Captures  │
│   changes   │
└──────┬──────┘
       │
       │ JSON messages
       │ (insert/update/delete events)
       │
       ▼
┌─────────────┐
│   Kafka     │
│   Topic     │
│             │
│ bankdb.public│
│ .transactions│
└─────────────┘
```

### 🔑 Key Concepts

1. **WAL (Write-Ahead Log)**: PostgreSQL's transaction log - every change is recorded here
2. **Logical Replication**: PostgreSQL feature that allows external systems to read WAL
3. **Kafka Connect**: Framework for connecting Kafka to external systems
4. **Debezium Connector**: Specialized connector that reads WAL and converts to Kafka messages

### 📊 What You'll See

When you insert a row in PostgreSQL:
```sql
INSERT INTO transactions (account, amount) VALUES (1234, 100.50);
```

**Debezium captures this and creates a Kafka message:**
```json
{
  "before": null,
  "after": {
    "id": 6,
    "account": 1234,
    "amount": 100.50,
    "ts": "2024-01-01T12:00:00Z"
  },
  "source": {
    "version": "2.5.0",
    "connector": "postgresql",
    "name": "bankdb",
    "ts_ms": 1704110400000,
    "snapshot": "false",
    "db": "bankdb",
    "sequence": "[\"1234567890:6\"]",
    "schema": "public",
    "table": "transactions",
    "txId": 789,
    "lsid": null,
    "xmin": null
  },
  "op": "c",  // 'c' = create/insert
  "ts_ms": 1704110400123
}
```

**Kafka Topic Name**: `bankdb.public.transactions`

## 🚀 Quick Start

### Step 1: Start All Services

```bash
cd 03_postgres_debezium
docker compose up -d
```

**What starts:**
- ✅ PostgreSQL (port 5433 - external, 5432 internal)
- ✅ Zookeeper (port 2182 - external, 2181 internal)
- ✅ Kafka (port 9094 - external, 9093 internal)
- ✅ Kafka Connect with Debezium (port 8083)
- ✅ Kafka UI (port 8082)

### Step 2: Wait for Services to be Ready

```bash
# Check all containers are running
docker compose ps

# Wait ~30 seconds for everything to initialize
```

### Step 3: Register Debezium Connector

```bash
# Register the PostgreSQL connector
curl -i -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connect_config.json
```

**Expected response:**
```json
{
  "name": "postgres-transactions-connector",
  "config": {...},
  "tasks": [...],
  "type": "source"
}
```

### Step 4: Verify Connector Status

```bash
curl http://localhost:8083/connectors/postgres-transactions-connector/status
```

Should show: `"state": "RUNNING"`

### Step 5: Insert Data and Watch It Stream!

**Connect to PostgreSQL:**
```bash
# From host machine (if needed)
docker compose exec postgres psql -U postgres -d bankdb

# Or from outside container (host: 5433)
# psql -h localhost -p 5433 -U postgres -d bankdb
```

**Insert a transaction:**
```sql
INSERT INTO transactions (account, amount) VALUES (5555, 999.99);
```

### Step 6: View in Kafka UI

1. Open: http://localhost:8082
2. Navigate to **Topics** → `bankdb.public.transactions`
3. Go to **Messages** tab
4. Set offset to **Latest**
5. Click **Consume messages**
6. **You'll see your INSERT appear as a Kafka message!**

## 📁 Files Explained

### `docker-compose.yml`
**Purpose**: Orchestrates all services needed for CDC

**Services:**
- **postgres**: Database with logical replication enabled
- **zookeeper & kafka**: Message broker (separate from 01_local_kafka)
- **kafka-connect**: Kafka Connect framework with Debezium connector
- **kafka-ui**: Web UI to view CDC messages

### `postgres_init.sql`
**Purpose**: Initializes PostgreSQL database

**What it does:**
- Creates `transactions` table
- Enables logical replication (WAL level)
- Creates `debezium` user with replication permissions
- Inserts sample data

### `connect_config.json`
**Purpose**: Configuration for Debezium PostgreSQL connector

**Key Settings:**
- `database.server.name`: Prefix for Kafka topics (`bankdb`)
- `table.include.list`: Which tables to monitor (`public.transactions`)
- `plugin.name`: `pgoutput` (PostgreSQL's logical replication plugin)
- `transforms.unwrap`: Extracts just the new record (simplifies message format)

**Topic Naming:**
- Topic name: `{database.server.name}.{schema}.{table}`
- Example: `bankdb.public.transactions`

## 🔍 Understanding CDC Messages

### Insert Event (`op: "c"`)
```json
{
  "before": null,
  "after": {
    "id": 1,
    "account": 1234,
    "amount": 100.50,
    "ts": "2024-01-01T12:00:00Z"
  },
  "op": "c"
}
```

### Update Event (`op: "u"`)
```json
{
  "before": {
    "id": 1,
    "account": 1234,
    "amount": 100.50
  },
  "after": {
    "id": 1,
    "account": 1234,
    "amount": 200.00  // Changed!
  },
  "op": "u"
}
```

### Delete Event (`op: "d"`)
```json
{
  "before": {
    "id": 1,
    "account": 1234,
    "amount": 100.50
  },
  "after": null,
  "op": "d"
}
```

## 🎓 Real-World Use Cases

### 1. **Data Synchronization**
- Keep multiple databases in sync
- Example: Main DB → Cache DB, Search Index

### 2. **Event Sourcing**
- Capture all changes as events
- Rebuild state from event log

### 3. **Analytics & Reporting**
- Stream changes to data warehouse
- Real-time business intelligence

### 4. **Microservices Integration**
- Database changes trigger microservice events
- Decoupled architecture

### 5. **Audit Logging**
- Track all database changes
- Compliance and security

## 🧪 Test Scenarios

### Test 1: Insert Multiple Rows
```sql
INSERT INTO transactions (account, amount) VALUES
  (1001, 50.00),
  (1002, -25.50),
  (1003, 100.00);
```
**Result**: 3 messages appear in Kafka UI immediately!

### Test 2: Update Existing Row
```sql
UPDATE transactions SET amount = 999.99 WHERE id = 1;
```
**Result**: Update event with `before` and `after` states

### Test 3: Delete Row
```sql
DELETE FROM transactions WHERE id = 1;
```
**Result**: Delete event with `before` state

### Test 4: Batch Insert
```sql
INSERT INTO transactions (account, amount)
SELECT 1000 + (random() * 1000)::int, 
       (random() * 1000 - 500)::float
FROM generate_series(1, 100);
```
**Result**: 100 messages stream to Kafka in real-time!

## 🔧 Troubleshooting

### Connector Not Starting
```bash
# Check connector status
curl http://localhost:8083/connectors/postgres-transactions-connector/status

# Check logs
docker compose logs kafka-connect
```

### No Messages Appearing
1. **Check PostgreSQL is running**: `docker compose ps postgres`
2. **Verify connector is running**: Check status endpoint
3. **Check WAL level**: Should be `logical`
   ```bash
   docker compose exec postgres psql -U postgres -c "SHOW wal_level;"
   ```

### Connection Issues
```bash
# Test PostgreSQL connection
docker compose exec postgres psql -U postgres -d bankdb -c "SELECT 1;"

# Test Kafka Connect
curl http://localhost:8083/connectors
```

## 📚 Key Takeaways

✅ **CDC captures database changes automatically**
✅ **No application code changes needed**
✅ **Real-time streaming to Kafka**
✅ **Debezium handles all complexity**
✅ **Works with any application writing to DB**

## 🎉 Summary

You've learned:
- ✅ What Change Data Capture (CDC) is
- ✅ How Debezium works with PostgreSQL
- ✅ How to set up CDC pipeline
- ✅ How database changes become Kafka messages
- ✅ Real-world use cases for CDC

**Congratulations!** You can now stream database changes to Kafka in real-time! 🚀

