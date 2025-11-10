# 🎬 Stream Processing: Kafka Streams + Flink

**Real-time data processing** - like having super-smart helpers that watch your data and tell you important things as they happen!

## 🎯 What is Stream Processing? (Explained Like You're 5)

Imagine you have a **piggy bank** that gets coins dropped in it all day long. 

**Old Way (Batch Processing):**
- Wait until the end of the day
- Open the piggy bank
- Count all the coins
- "Oh! You have $50!"

**New Way (Stream Processing):**
- Every time a coin drops in, a **smart helper** immediately counts it
- The helper keeps a running total
- "You just added $1! Your total is now $51!"
- You know your balance **right now**, not at the end of the day!

**Stream Processing = Watching and counting things as they happen, not waiting until later!**

## 🏦 Our Bank Example

We have a bank with lots of transactions happening:
- Account 1234 deposits $100
- Account 5678 withdraws $50
- Account 1234 deposits $200
- Account 9999 withdraws $1000
- ... and so on, all day long!

**Question:** How much money does each account have **right now**?

**Answer:** Use **Stream Processing** to keep track in real-time!

## 📊 Two Super Helpers

### Helper #1: Kafka Streams (The Accountant)
**Job:** Keep a running total for each account

**What it does:**
- Watches every transaction
- Groups them by account number
- Adds up all the money for each account
- Updates the total every 10 seconds
- Writes the answer to a "report" (Kafka topic)

**Like:** A smart calculator that never stops counting!

### Helper #2: Flink (The Security Guard)
**Job:** Watch for suspicious activity (fraud detection)

**What it does:**
- Watches every transaction
- Groups by account
- Counts total activity in 1-minute windows
- If someone spends more than $5000 in 1 minute → **ALERT!** 🚨
- Writes alerts to a "security report" (Kafka topic)

**Like:** A security guard watching for suspicious behavior!

## 🎬 How It Works (Step by Step)

```
┌─────────────────┐
│  Transactions   │
│  (Kafka Topic)  │
│                 │
│ Account 1234:   │
│   +$100         │
│   +$200         │
│   -$50          │
└────────┬────────┘
         │
         │ Two helpers read the same stream!
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Kafka   │ │  Flink  │
│ Streams │ │  Job    │
│         │ │         │
│ Groups  │ │ Groups  │
│ by      │ │ by      │
│ account │ │ account │
│         │ │         │
│ Sums    │ │ Sums in │
│ every   │ │ 1-min   │
│ 10 sec  │ │ windows │
└────┬────┘ └────┬────┘
     │          │
     │          │ If > $5000
     │          │ → ALERT! 🚨
     │          │
     ▼          ▼
┌──────────┐ ┌──────────┐
│ Account  │ │  Fraud   │
│ Balances │ │  Alerts  │
│ Topic    │ │  Topic   │
└──────────┘ └──────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Kafka must be running** (from `01_local_kafka/` or `03_postgres_debezium/`):
   ```bash
   # Use one of these:
   cd ../01_local_kafka && docker compose up -d
   # OR
   cd ../03_postgres_debezium && docker compose up -d
   ```

2. **Transactions topic must exist** (or will be auto-created):
   ```bash
   # If using 01_local_kafka
   docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 \
     --create --topic transactions --partitions 3 --replication-factor 1
   ```

### Option 1: Kafka Streams (Java)

**What it does:** Real-time account balance aggregation

**Setup:**
```bash
# Compile (requires Java 11+ and Maven)
mvn clean package

# Run
java -cp target/kafka-streams-app-1.0.jar KafkaStreamsApp
```

**What you'll see:**
- Reads transactions from `transactions` topic
- Groups by account
- Calculates rolling sum every 10 seconds
- Writes to `account-balances` topic

**View results:**
```bash
# In another terminal
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic account-balances \
  --from-beginning
```

**Example output:**
```json
{"account":"1234","balance":250.00,"window_start":1704110400000,"window_end":1704110410000}
{"account":"5678","balance":-50.00,"window_start":1704110400000,"window_end":1704110410000}
```

### Option 2: Flink (Python)

**What it does:** Fraud detection - flags high activity

**Setup:**
```bash
# Install PyFlink
pip install apache-flink

# Run
python flink_job.py
```

**What you'll see:**
- Reads transactions from `transactions` topic
- Groups by account
- Calculates 1-minute activity windows
- Flags accounts with > $5000 activity
- Writes alerts to `fraud-alerts` topic

**View fraud alerts:**
```bash
# In another terminal
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic fraud-alerts \
  --from-beginning
```

**Example output:**
```json
{
  "account": 9999,
  "total_activity": 7500.00,
  "threshold": 5000.0,
  "alert_type": "HIGH_ACTIVITY",
  "message": "Account 9999 has $7500.00 activity in 1 minute (threshold: $5000.0)"
}
```

## 🎓 Understanding the Concepts

### Kafka Streams: Rolling Aggregation

**What is "rolling sum"?**
- Like a moving average, but for sums
- Every 10 seconds, add up all transactions for each account
- The "window" slides forward in time

**Example:**
```
Time 0-10s:  Account 1234: +$100, +$200  → Total: $300
Time 10-20s: Account 1234: -$50          → Total: $250 (new window)
Time 20-30s: Account 1234: +$100         → Total: $100 (new window)
```

**Why 10 seconds?**
- Fast enough to see changes quickly
- Not so fast that it's overwhelming
- Good balance for real-time monitoring

### Flink: Time Windows

**What is a "time window"?**
- A bucket of time (like 1 minute)
- All transactions in that minute get grouped together
- After 1 minute, the window closes and we check the total

**Example:**
```
12:00:00 - 12:01:00 (Window 1):
  Account 9999: $1000, $2000, $3000, $1000
  Total: $7000 → ALERT! (exceeds $5000 threshold)

12:01:00 - 12:02:00 (Window 2):
  Account 9999: $500
  Total: $500 → OK (under threshold)
```

**Why 1 minute?**
- Long enough to catch suspicious patterns
- Short enough to alert quickly
- Common fraud detection window

## 🧪 Test Scenarios

### Test 1: Generate Transactions

Use the stream simulator from `02_producer_consumer/`:
```bash
cd ../02_producer_consumer
source venv/bin/activate
python stream_simulator.py
```

### Test 2: Watch Account Balances (Kafka Streams)

In another terminal:
```bash
# Start Kafka Streams app
java -cp target/kafka-streams-app-1.0.jar KafkaStreamsApp

# Watch account balances
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic account-balances \
  --from-beginning
```

### Test 3: Trigger Fraud Alert (Flink)

Generate high-value transactions:
```bash
# Send a batch of large transactions to same account
for i in {1..10}; do
  echo '{"account":9999,"amount":600,"timestamp":"'$(date +%s)'","type":"deposit"}' | \
  docker compose exec -T kafka kafka-console-producer \
    --bootstrap-server localhost:9092 \
    --topic transactions
done
```

**Result:** Flink should detect > $5000 activity and send alert!

## 📊 Visualizing Results

### Kafka UI
1. Open http://localhost:8080 (or 8082 for debezium setup)
2. Navigate to **Topics**
3. View:
   - `transactions` - Input stream
   - `account-balances` - Kafka Streams output
   - `fraud-alerts` - Flink output

### Flink Dashboard
1. Start Flink cluster: `docker compose up -d` (in this directory)
2. Open http://localhost:8081
3. Submit job and monitor:
   - Job status
   - Throughput (records/second)
   - Latency
   - Task metrics

## 🔑 Key Differences: Kafka Streams vs Flink

| Feature | Kafka Streams | Flink |
|---------|--------------|-------|
| **Language** | Java/Scala | Java/Scala/Python |
| **Best For** | Simple aggregations | Complex processing |
| **State Management** | Built-in | Advanced options |
| **Window Types** | Time, Session, Sliding | Time, Count, Session, Custom |
| **Learning Curve** | Easier | Steeper |
| **Use Case Here** | Rolling sums | Fraud detection |

**Think of it like:**
- **Kafka Streams** = A simple calculator (does one thing well)
- **Flink** = A full computer (can do complex things)

## 🎯 Real-World Use Cases

### Kafka Streams Use Cases
- ✅ Real-time dashboards (live metrics)
- ✅ Rolling averages (stock prices, temperatures)
- ✅ Simple aggregations (counts, sums)
- ✅ Data enrichment (add missing fields)

### Flink Use Cases
- ✅ Fraud detection (complex rules)
- ✅ Anomaly detection (unusual patterns)
- ✅ Complex event processing (multiple conditions)
- ✅ Machine learning on streams
- ✅ Real-time recommendations

## 🐛 Troubleshooting

### Kafka Streams Not Processing
- Check Kafka is running
- Verify `transactions` topic exists
- Check application logs for errors

### Flink Job Not Starting
- Ensure PyFlink is installed: `pip install apache-flink`
- Check Kafka connection: `bootstrap.servers` correct?
- Verify topic exists

### No Fraud Alerts
- Generate high-value transactions (> $5000 total in 1 min)
- Check same account number for multiple transactions
- Verify Flink job is running

## 📚 Key Takeaways

✅ **Stream Processing** = Processing data as it arrives, not in batches
✅ **Kafka Streams** = Simple, built-in stream processing for Kafka
✅ **Flink** = Powerful stream processing framework
✅ **Windows** = Time buckets for aggregating data
✅ **Real-time** = See results immediately, not later

## 🎉 Summary

You've learned:
- ✅ What stream processing is (like a smart helper counting coins)
- ✅ How Kafka Streams does rolling aggregations
- ✅ How Flink detects fraud with time windows
- ✅ When to use each tool
- ✅ How to monitor and visualize results

**Congratulations!** You can now process data streams in real-time! 🚀

## 🎬 Next Steps

1. **Modify window sizes** - Try 5 seconds or 1 minute
2. **Add more rules** - Multiple fraud detection patterns
3. **Visualize** - Create dashboards from the output topics
4. **Scale** - Run multiple instances for high throughput
5. **Combine** - Use both tools together for complex pipelines

