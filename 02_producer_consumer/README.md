# 🏦 Python Producer & Consumer - Bank Transaction Stream

A hands-on demonstration of Kafka producers and consumers using a **real-time bank transaction simulation**.

## 📋 Overview

This module demonstrates:
- **Producer**: Sending messages to Kafka topics
- **Consumer**: Reading and processing messages in real-time
- **Stream Simulation**: Continuous data generation for testing

### 🎯 What You'll Learn

- How to create Kafka producers in Python
- How to consume messages with consumer groups
- Real-time data streaming patterns
- Message serialization/deserialization
- Offset management and consumer groups

## 🚀 Quick Start

### Prerequisites

1. **Kafka must be running** (from `01_local_kafka/`):
   ```bash
   cd ../01_local_kafka
   docker compose up -d
   ```

2. **Activate virtual environment and install dependencies**:
   ```bash
   # From project root - ALWAYS activate venv first!
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
   
   **⚠️ Important**: Always activate the venv before running scripts:
   ```bash
   source venv/bin/activate  # Do this in every terminal window
   ```

### 🎬 Running the Demo

#### **Step 1: Start the Stream Simulator** (Terminal 1)
```bash
# Make sure venv is activated!
source venv/bin/activate
cd 02_producer_consumer
python stream_simulator.py
```

**What you'll see:**
```
🏦 Bank Transaction Stream Simulator
==================================================
📡 Connecting to Kafka at localhost:9092
📨 Publishing to topic: transactions
⏱️  Rate: 1 transaction every 0.5 seconds
==================================================
Press Ctrl+C to stop

✅ Sent 10 transactions | Latest: Account 2345 | $+456.78 | deposit
✅ Sent 20 transactions | Latest: Account 1890 | $-234.56 | withdrawal
...
```

#### **Step 2: Start the Consumer** (Terminal 2)
```bash
# Make sure venv is activated!
source venv/bin/activate
cd 02_producer_consumer
python consumer.py
```

**What you'll see:**
```
✅ Connected to Kafka at localhost:9092
📥 Consuming from topic: transactions
👥 Consumer group: transaction-monitor
============================================================
🎯 Starting to consume messages...

[   1] Account 1234 |    $+150.50 | deposit      | TXN-45678
[   2] Account 2345 |    $-234.56 | withdrawal   | TXN-78901
[   3] Account 3456 |    $+890.12 | deposit      | TXN-12345
...

============================================================
📊 REAL-TIME STATISTICS
============================================================
Total Transactions: 10
Total Amount: $1,234.56
Deposits: 6 | Withdrawals: 4

📈 Transactions by Type:
   Deposit: 6
   Withdrawal: 3
   Transfer: 1

👥 Active Accounts: 8
============================================================
```

## 📁 Files Explained

### `stream_simulator.py`
**Purpose**: Generates continuous bank transactions and streams them to Kafka.

**Key Features**:
- Generates random transactions (accounts, amounts, types)
- Sends messages at configurable rate (default: 0.5 seconds)
- Uses account number as partition key (ensures related transactions go to same partition)
- JSON serialization for message values

**Transaction Structure**:
```python
{
    "account": 1234,                    # Account number (1000-5000)
    "amount": 150.50,                   # Transaction amount (-1000 to +1000)
    "timestamp": "2024-01-01T12:00:00", # ISO timestamp
    "transaction_id": "TXN-45678",      # Unique transaction ID
    "type": "deposit"                   # deposit, withdrawal, transfer, payment
}
```

### `producer.py`
**Purpose**: Reusable producer class for sending messages to Kafka.

**Key Concepts**:
- **Bootstrap Servers**: Kafka broker addresses
- **Serialization**: Converting Python objects to bytes (JSON)
- **Partition Keys**: Optional keys for consistent partitioning
- **Acknowledgments**: Confirmation that message was received

**Usage Example**:
```python
from producer import TransactionProducer

producer = TransactionProducer()
tx = {"account": 1234, "amount": 100.0, "type": "deposit"}
result = producer.send(tx, key=tx["account"])
producer.close()
```

### `consumer.py`
**Purpose**: Real-time consumer that processes transactions and displays statistics.

**Key Concepts**:
- **Consumer Groups**: Multiple consumers sharing work
- **Offset Management**: Tracks where consumer left off
- **Auto Offset Reset**: `earliest` (from beginning) or `latest` (new messages only)
- **Polling**: Continuous checking for new messages

**Features**:
- Real-time statistics (counts, totals, by type)
- Per-transaction display
- Periodic summary reports
- Graceful shutdown handling

## 🔄 Data Flow Diagram

```
┌─────────────────┐
│ stream_simulator │
│    (Producer)    │
└────────┬─────────┘
         │
         │ JSON messages
         │ (every 0.5s)
         ▼
┌─────────────────┐
│  Kafka Topic    │
│  "transactions" │
│  (3 partitions)  │
└────────┬─────────┘
         │
         │ Consumer polls
         │ for messages
         ▼
┌─────────────────┐
│    consumer.py   │
│   (Consumer)     │
│                  │
│  • Process tx    │
│  • Update stats  │
│  • Print output  │
└─────────────────┘
```

## 🎓 Understanding the Concepts

### Producer Side
1. **Connection**: Producer connects to Kafka broker
2. **Serialization**: Python dict → JSON → bytes
3. **Partitioning**: Key-based routing (same account → same partition)
4. **Sending**: Async send with acknowledgment
5. **Batching**: Messages can be batched for efficiency

### Consumer Side
1. **Connection**: Consumer connects and joins consumer group
2. **Partition Assignment**: Kafka assigns partitions to consumers
3. **Polling**: Consumer continuously polls for new messages
4. **Deserialization**: Bytes → JSON → Python dict
5. **Processing**: Business logic (statistics, validation, etc.)
6. **Offset Commit**: Tracks progress through topic

### Message Flow
```
Producer → Kafka Topic → Consumer Group → Consumers
   ↓            ↓              ↓              ↓
Serialize    Store         Assign         Process
   ↓            ↓              ↓              ↓
  Send       Partition      Distribute     Commit Offset
```

## 🧪 Testing Scenarios

### Scenario 1: Single Producer, Single Consumer
```bash
# Terminal 1
python stream_simulator.py

# Terminal 2
python consumer.py
```
**Result**: Consumer processes all messages in order.

### Scenario 2: Multiple Consumers (Same Group)
```bash
# Terminal 1
python stream_simulator.py

# Terminal 2
python consumer.py

# Terminal 3 (new consumer, same group)
python consumer.py
```
**Result**: Kafka distributes partitions between consumers (load balancing).

### Scenario 3: Multiple Consumer Groups
```bash
# Terminal 1
python stream_simulator.py

# Terminal 2 (Group: transaction-monitor)
python consumer.py

# Terminal 3 (Group: fraud-detector)
python -c "from consumer import TransactionConsumer; \
          TransactionConsumer(group_id='fraud-detector').consume()"
```
**Result**: Both groups receive all messages (publish-subscribe pattern).

## 🔧 Configuration

### Adjust Stream Rate
Edit `stream_simulator.py`:
```python
DELAY_SECONDS = 0.5  # Change to 0.1 for faster, 1.0 for slower
```

### Change Consumer Group
Edit `consumer.py`:
```python
consumer = TransactionConsumer(group_id="my-custom-group")
```

### Use Different Topic
```python
# In stream_simulator.py
TOPIC = "my-topic"

# In consumer.py
consumer = TransactionConsumer(topic="my-topic")
```

## 📊 Visualizing in Kafka UI

1. Open http://localhost:8080
2. Navigate to **Topics** → **transactions**
3. Go to **Messages** tab
4. Set offset to **Latest**
5. Watch messages appear in real-time as simulator runs!

## 🐛 Troubleshooting

### "Failed to connect to Kafka"
- **Solution**: Ensure Kafka is running: `cd ../01_local_kafka && docker compose ps`

### "No messages received"
- **Solution**: Check consumer group offset. Use `auto_offset_reset="earliest"` to read from beginning

### "ModuleNotFoundError: kafka"
- **Solution**: Install dependencies: `pip install -r requirements.txt`

## 📚 Next Steps

- Modify `stream_simulator.py` to generate different data types
- Add filtering logic to `consumer.py` (e.g., flag large transactions)
- Implement message schemas with Avro or Protobuf
- Add error handling and retry logic
- Explore consumer lag and monitoring

## 🎉 Summary

You've learned:
- ✅ How to produce messages to Kafka
- ✅ How to consume messages in real-time
- ✅ Consumer groups and partitioning
- ✅ Real-time data streaming patterns

**Congratulations!** You're now ready to build real-time streaming applications with Kafka! 🚀

