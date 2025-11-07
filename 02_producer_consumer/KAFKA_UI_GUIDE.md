# 🎯 How to View Messages in Kafka UI

## Problem: Messages appear in Python but not in Kafka UI

This usually happens because:
1. Messages are being consumed too quickly
2. Kafka UI needs to be refreshed
3. Wrong offset/view settings in Kafka UI

## ✅ Solution Steps

### Step 1: Access Kafka UI
1. Open browser: http://localhost:8080
2. Wait for cluster to connect (should show "local" cluster)

### Step 2: Navigate to Transactions Topic
1. Click **"Topics"** in left sidebar
2. Click on **"transactions"** topic
3. You should see 3 partitions (0, 1, 2)

### Step 3: View Messages (IMPORTANT!)

**Option A: View from Beginning (See All Messages)**
1. Go to **"Messages"** tab
2. Set **"Offset"** dropdown to **"Earliest"** (or "From beginning")
3. Click **"Consume messages"** button
4. Messages should appear!

**Option B: View Latest Messages (Live Stream)**
1. Go to **"Messages"** tab  
2. Set **"Offset"** dropdown to **"Latest"**
3. Click **"Consume messages"** button
4. **Important**: Keep the producer running - new messages will appear as they arrive

### Step 4: Troubleshooting

**If you still don't see messages:**

1. **Stop your consumer temporarily** (let messages accumulate):
   ```bash
   # Press Ctrl+C on consumer terminal
   # Keep producer running
   ```

2. **Refresh Kafka UI**:
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
   - Or reload the page

3. **Check topic has messages**:
   ```bash
   cd ../01_local_kafka
   docker compose exec kafka kafka-console-consumer \
     --bootstrap-server localhost:9092 \
     --topic transactions \
     --from-beginning \
     --max-messages 5
   ```

4. **Check Kafka UI logs**:
   ```bash
   docker compose logs kafka-ui
   ```

## 🎬 Live Demo Setup

For best viewing experience:

**Terminal 1: Producer only** (let it run)
```bash
source venv/bin/activate
cd 02_producer_consumer
python stream_simulator.py
```

**Terminal 2: Consumer** (stop it temporarily to see messages accumulate)
```bash
# Don't run consumer yet - let messages accumulate first
```

**Browser: Kafka UI**
1. Go to http://localhost:8080
2. Topics → transactions → Messages tab
3. Set offset to "Latest"
4. Click "Consume messages"
5. Watch messages appear in real-time!

**Then start consumer** to see it processing messages:
```bash
source venv/bin/activate
cd 02_producer_consumer
python consumer.py
```

## 📊 What You Should See

In Kafka UI Messages tab:
- **Key**: Account number (e.g., "4055")
- **Value**: JSON transaction object
- **Partition**: 0, 1, or 2 (randomly assigned)
- **Offset**: Message position in partition
- **Timestamp**: When message was produced

Example message:
```json
{
  "account": 4055,
  "amount": 13.54,
  "timestamp": "2025-11-03T21:26:57.863698",
  "transaction_id": "TXN-48046",
  "type": "withdrawal"
}
```

## 💡 Pro Tips

1. **Use "Latest" offset** to see new messages as they arrive
2. **Use "Earliest" offset** to see all historical messages
3. **Stop consumer** to see messages accumulate in topic
4. **Check partition distribution** - messages are distributed across 3 partitions
5. **View consumer groups** - see your consumer's progress in "Consumer groups" section

