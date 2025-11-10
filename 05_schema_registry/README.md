# 📋 Schema Registry + Avro: Data Contracts & Schema Evolution

**Guarantee your data structure** - like a contract that says "this is exactly what my data looks like!"

## 🎯 What is Schema Registry? (Explained Like You're 5)

Imagine you're sending **letters** to your friend, but you want to make sure they can **always read them**.

**Problem Without Schema:**
- You write a letter: "Hi! I have 3 apples and 2 bananas"
- Your friend reads: "Hi! I have apples and bananas" (numbers got lost!)
- Your friend doesn't know how many of each!

**Solution With Schema (Like a Template):**
- You both agree on a **template** (schema):
  ```
  Letter must have:
  - Greeting (text)
  - Number of apples (number)
  - Number of bananas (number)
  ```
- You write using the template
- Your friend reads using the same template
- **Everyone understands the same way!**

**Schema Registry = A library that stores all the templates (schemas) so everyone can use them!**

## 🏦 Our Bank Example

We send **transaction messages** between systems:
- Producer sends: `{"account": 1234, "amount": 100.50}`
- Consumer receives: `{"account": 1234, "amount": 100.50}`

**But what if:**
- Producer sends: `{"account": 1234, "amount": 100.50, "type": "deposit"}`
- Consumer expects: `{"account": 1234, "amount": 100.50}` (no "type" field!)
- **Problem!** Consumer doesn't know what "type" is!

**Solution:** Use **Avro schema** to define exactly what fields exist!

## 📊 What is Avro?

**Avro** is a data format that:
- Defines the **structure** of your data (like a blueprint)
- Makes data **smaller** (compressed)
- Works with **Schema Registry** (stores schemas centrally)
- Supports **schema evolution** (can add new fields safely)

**Think of it like:**
- **JSON** = Plain text (easy to read, but no structure guarantee)
- **Avro** = Structured format with a contract (guaranteed structure)

## 🔄 Schema Evolution (The Magic Part!)

**Schema Evolution** = Changing your schema over time without breaking things!

### Example: Adding a New Field

**Version 1 Schema:**
```json
{
  "account": 1234,
  "amount": 100.50,
  "type": "deposit"
}
```

**Version 2 Schema (Added "merchant" field):**
```json
{
  "account": 1234,
  "amount": 100.50,
  "type": "deposit",
  "merchant": "Amazon"  ← NEW FIELD!
}
```

**What happens:**
- ✅ Old consumers (expecting v1) still work! (they ignore "merchant")
- ✅ New consumers (expecting v2) get the new field!
- ✅ **No breaking changes!**

**Like:** Adding a new room to your house blueprint - old builders can still build, new builders get the extra room!

## 🚀 Quick Start

### Step 1: Start Services

```bash
cd 05_schema_registry
docker compose up -d
```

**What starts:**
- ✅ Zookeeper (port 2183)
- ✅ Kafka (port 9095)
- ✅ Schema Registry (port 8081)
- ✅ Kafka UI (port 8083)

### Step 2: Install Dependencies

```bash
# From project root
source venv/bin/activate
pip install confluent-kafka[avro]
```

### Step 3: Create Topic

```bash
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9095 \
  --create --topic transactions-avro \
  --partitions 3 --replication-factor 1
```

### Step 4: Run Producer

```bash
source venv/bin/activate
cd 05_schema_registry
python serializer.py
```

**What you'll see:**
```
📝 Avro Transaction Producer
==================================================
📡 Schema Registry: http://localhost:8081
📨 Kafka: localhost:9092
📋 Topic: transactions-avro
==================================================
✅ Producer created with Avro serialization

✅ Sent: Account 1001 | $+150.50 | deposit | Partition: 0 | Offset: 0
✅ Sent: Account 1002 | $-75.25 | withdrawal | Partition: 1 | Offset: 0
...
```

### Step 5: Run Consumer

```bash
# In another terminal
source venv/bin/activate
cd 05_schema_registry
python deserializer.py
```

**What you'll see:**
```
📥 Avro Transaction Consumer
==================================================
🎯 Consuming messages...

[  1] Account: 1001 | Amount:   $+150.50 | Type: deposit      | Description: Salary deposit
[  2] Account: 1002 | Amount:   $-75.25 | Type: withdrawal   | Description: ATM withdrawal
...
```

## 📁 Files Explained

### `avro_schemas/transaction.avsc`
**Purpose:** Defines the structure of transaction data

**What it contains:**
- Field names (id, account, amount, etc.)
- Field types (string, int, double, enum)
- Optional fields (description can be null)
- Documentation for each field

**Why `.avsc`?** Avro Schema file format

### `avro_schemas/transaction_v2.avsc`
**Purpose:** Evolved schema with new fields

**What's new:**
- Added `merchant` field (optional)
- Added `location` field (optional)
- Added `refund` to transaction type enum

**Backward compatible:** Old consumers can still read v2 messages!

### `serializer.py`
**Purpose:** Producer that uses Avro serialization

**What it does:**
1. Loads Avro schema from file
2. Connects to Schema Registry
3. Registers schema (if not exists)
4. Serializes data using Avro
5. Sends to Kafka

**Key benefit:** Data is validated against schema before sending!

### `deserializer.py`
**Purpose:** Consumer that uses Avro deserialization

**What it does:**
1. Connects to Schema Registry
2. Gets schema automatically
3. Deserializes Avro messages
4. Validates data structure
5. Handles schema evolution

**Key benefit:** Always gets correct data structure, even if schema evolved!

## 🔍 How Schema Registry Works

```
┌─────────────────┐
│   Producer      │
│                 │
│ 1. Load schema  │
│ 2. Register     │
│    with SR      │
└────────┬────────┘
         │
         │ Register schema
         │
         ▼
┌─────────────────┐
│ Schema Registry │
│                 │
│ Stores schemas: │
│ - v1: basic     │
│ - v2: +merchant │
│ - v3: +location │
└────────┬────────┘
         │
         │ Get schema
         │
         ▼
┌─────────────────┐
│   Consumer      │
│                 │
│ 1. Get schema   │
│    from SR      │
│ 2. Deserialize  │
│    message      │
└─────────────────┘
```

## 🧪 Schema Evolution Examples

### Example 1: Adding Optional Field

**Before (v1):**
```json
{
  "account": 1234,
  "amount": 100.50
}
```

**After (v2):**
```json
{
  "account": 1234,
  "amount": 100.50,
  "merchant": "Amazon"  ← NEW!
}
```

**Result:** ✅ Works! Old consumers ignore new field, new consumers use it.

### Example 2: Adding to Enum

**Before (v1):**
```json
"type": ["deposit", "withdrawal", "transfer", "payment"]
```

**After (v2):**
```json
"type": ["deposit", "withdrawal", "transfer", "payment", "refund"]  ← NEW!
```

**Result:** ✅ Works! Old consumers handle new enum value gracefully.

### Example 3: Making Field Optional

**Before (v1):**
```json
"description": "string"  // Required
```

**After (v2):**
```json
"description": ["null", "string"]  // Optional now
```

**Result:** ✅ Works! Old consumers still get description, new consumers can omit it.

## 🎓 Key Concepts

### Data Contract
**Definition:** An agreement about data structure between producer and consumer

**Why important:**
- Prevents errors (wrong field types)
- Enables evolution (add fields safely)
- Documents structure (self-documenting)

**Like:** A contract between two companies - both agree on what data looks like!

### Schema Compatibility
**Types:**
- **Backward compatible:** New schema works with old consumers
- **Forward compatible:** Old schema works with new consumers
- **Full compatible:** Both directions work

**Our examples:** All backward compatible (safe to add fields)

### Serialization vs Deserialization
- **Serialization:** Convert data → bytes (for sending)
- **Deserialization:** Convert bytes → data (for receiving)

**With Avro:**
- Schema ensures both sides understand the same structure
- Smaller size (compressed)
- Faster (binary format)

## 🔧 Viewing Schemas

### Schema Registry UI
1. Open: http://localhost:8081
2. View registered schemas
3. See schema versions
4. Check compatibility

### Kafka UI
1. Open: http://localhost:8083
2. Navigate to **Schema Registry** section
3. View schemas and versions
4. See topic-schema mappings

### Command Line
```bash
# List all subjects (topics with schemas)
curl http://localhost:8081/subjects

# Get latest schema for a subject
curl http://localhost:8081/subjects/transactions-avro-value/versions/latest

# Get all versions
curl http://localhost:8081/subjects/transactions-avro-value/versions
```

## 🐛 Troubleshooting

### "Schema Registry not found"
- **Solution:** Ensure Schema Registry is running: `docker compose ps`

### "Schema compatibility error"
- **Solution:** Check schema evolution rules. Adding fields is usually safe, removing is not.

### "Deserialization error"
- **Solution:** Verify producer and consumer use compatible schemas

### "Topic not found"
- **Solution:** Create topic first: `kafka-topics --create ...`

## 📚 Real-World Use Cases

### 1. **Microservices Communication**
- Service A sends data → Service B receives
- Schema ensures both understand structure
- Evolution allows adding fields without breaking

### 2. **Data Pipelines**
- Source system → Kafka → Target system
- Schema validates data at each step
- Evolution allows pipeline improvements

### 3. **API Versioning**
- API v1 → API v2
- Schema evolution = smooth migration
- No breaking changes for consumers

### 4. **Data Quality**
- Schema validates data before processing
- Catches errors early
- Ensures data consistency

## 🎯 Key Takeaways

✅ **Schema Registry** = Central storage for data structure definitions
✅ **Avro** = Binary format with schema support
✅ **Schema Evolution** = Changing schemas safely over time
✅ **Data Contracts** = Guaranteed data structure between systems
✅ **Backward Compatibility** = New schemas work with old consumers

## 🎉 Summary

You've learned:
- ✅ What Schema Registry is (like a template library)
- ✅ What Avro is (structured data format)
- ✅ How schema evolution works (adding fields safely)
- ✅ Why data contracts matter (guaranteed structure)
- ✅ How to use Avro with Kafka

**Congratulations!** You can now guarantee data structure and evolve schemas safely! 🚀

## 🎬 Next Steps

1. **Try schema evolution** - Update to v2 schema and see backward compatibility
2. **Add more fields** - Experiment with different field types
3. **Check compatibility** - Test forward/backward compatibility rules
4. **Monitor schemas** - Use Schema Registry UI to track versions
5. **Production patterns** - Learn about schema naming conventions

