# 📊 Kafka Monitoring: Prometheus + Grafana

**Real-time monitoring and visualization** of your Kafka cluster - see everything that's happening!

## 🎯 What is Monitoring? (Explained Simply)

Imagine you're driving a car. You need to see:
- **Speed** (how fast are you going?)
- **Fuel** (do you have enough gas?)
- **Engine temperature** (is everything running smoothly?)

**Monitoring Kafka is the same!** You need to see:
- **Messages per second** (how busy is Kafka?)
- **Consumer lag** (are consumers keeping up?)
- **Broker health** (is everything running smoothly?)

**Monitoring = Dashboard showing all the important numbers!**

## 🛠️ Tools We Use

### Prometheus
**What it does:** Collects and stores metrics (numbers about your system)

**Like:** A smart notebook that writes down all the measurements

**Features:**
- Collects metrics every few seconds
- Stores them in a time-series database
- Can query metrics with PromQL

### Kafka Exporter
**What it does:** Reads Kafka metrics and makes them available to Prometheus

**Like:** A translator that speaks both "Kafka language" and "Prometheus language"

**Metrics it exports:**
- Messages per second
- Consumer lag
- Broker state
- Topic sizes
- Partition counts

### Grafana
**What it does:** Creates beautiful dashboards from Prometheus data

**Like:** A TV screen showing all your car's gauges in one place

**Features:**
- Real-time graphs
- Alerts when things go wrong
- Multiple dashboards
- Beautiful visualizations

## 🚀 Quick Start

### Step 1: Start Monitoring Stack

```bash
cd 06_monitoring
docker compose up -d
```

**What starts:**
- ✅ Prometheus (port 9090)
- ✅ Kafka Exporter (port 9308)
- ✅ Grafana (port 3000)

### Step 2: Access Dashboards

1. **Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin`
   - Dashboard: "Kafka Real-time Monitoring"

2. **Prometheus**: http://localhost:9090
   - Query metrics directly
   - View targets (what's being monitored)

### Step 3: Verify Kafka Exporter

```bash
# Check if Kafka Exporter is running
curl http://localhost:9308/metrics | head -20
```

You should see Kafka metrics in Prometheus format!

## 📊 Dashboard Widgets Explained

### 1. Messages per Second
**What it shows:** How many messages are flowing through Kafka topics

**Why it matters:**
- High = Kafka is busy (good!)
- Low = Not much activity
- Sudden spike = Something interesting happened

**Example:**
```
transactions topic: 150 messages/sec
account-balances topic: 10 messages/sec
```

### 2. Consumer Lag per Group
**What it shows:** How many unprocessed messages each consumer group has

**Why it matters:**
- **Lag = 0**: Consumers are keeping up perfectly! ✅
- **Lag = 100**: Consumers are 100 messages behind ⚠️
- **Lag = 1000+**: Consumers are falling behind! 🚨

**Example:**
```
transaction-monitor group: 0 lag (perfect!)
fraud-detector group: 5 lag (slight delay)
analytics group: 250 lag (needs attention!)
```

### 3. Broker CPU Usage
**What it shows:** How hard Kafka brokers are working

**Why it matters:**
- **Low CPU**: Kafka has plenty of resources
- **High CPU**: Kafka might be overloaded
- **Spikes**: Temporary load (usually OK)

**Example:**
```
Broker 1: 25% CPU (healthy)
Broker 2: 30% CPU (healthy)
```

### 4. Total Messages In (Stat Panel)
**What it shows:** Overall message throughput

**Quick glance:** See total activity at a glance

### 5. Total Consumer Lag (Stat Panel)
**What it shows:** Overall lag across all consumer groups

**Quick glance:** Is the system keeping up?

### 6. Bytes In/Out per Second
**What it shows:** Network traffic (data flowing in and out)

**Why it matters:**
- Shows data volume, not just message count
- Large messages = more bytes
- Helps identify bandwidth issues

### 7. Partition Count
**What it shows:** Number of partitions across all topics

**Why it matters:**
- More partitions = more parallelism
- Helps understand cluster size

### 8. Active Consumers
**What it shows:** Number of active consumer groups

**Why it matters:**
- Shows how many applications are consuming
- Helps track system usage

## 🔍 Understanding Metrics

### Key Metrics to Watch

#### Consumer Lag
```
kafka_consumer_lag_sum
```
**What it means:** Messages waiting to be processed

**Healthy:** < 100 messages
**Warning:** 100-1000 messages
**Critical:** > 1000 messages

#### Messages per Second
```
rate(kafka_server_brokertopicmetrics_messagesin_total[1m])
```
**What it means:** Throughput - how fast messages arrive

**Healthy:** Consistent rate
**Warning:** Sudden drops (consumers might be stuck)
**Critical:** Zero messages (producers stopped?)

#### Broker State
```
kafka_server_kafkaserver_brokerstate
```
**What it means:** Is the broker running?

**Healthy:** 3 (RunningAsBroker)
**Warning:** 2 (Starting)
**Critical:** 0 (NotRunning)

## 🎓 How It All Works Together

```
┌─────────────┐
│   Kafka     │
│   Cluster   │
└──────┬──────┘
       │
       │ Metrics
       │
       ▼
┌─────────────┐
│   Kafka     │
│  Exporter   │
│             │
│ Reads Kafka │
│ metrics     │
└──────┬──────┘
       │
       │ Prometheus format
       │
       ▼
┌─────────────┐
│ Prometheus  │
│             │
│ Collects &  │
│ stores      │
└──────┬──────┘
       │
       │ Query data
       │
       ▼
┌─────────────┐
│   Grafana   │
│             │
│ Visualizes  │
│ metrics     │
└─────────────┘
```

## 🧪 Testing the Setup

### Test 1: Generate Some Traffic

Use the stream simulator from `02_producer_consumer/`:
```bash
cd ../02_producer_consumer
source venv/bin/activate
python stream_simulator.py
```

**Watch in Grafana:**
- Messages/sec should increase
- Consumer lag might appear (if consumer is slow)

### Test 2: Check Consumer Lag

Start a consumer:
```bash
cd ../02_producer_consumer
python consumer.py
```

**Watch in Grafana:**
- Consumer lag should decrease as consumer processes messages
- Lag should stay near zero if consumer keeps up

### Test 3: Query Prometheus Directly

```bash
# Open Prometheus: http://localhost:9090
# Try these queries:

# Total messages per second
sum(rate(kafka_server_brokertopicmetrics_messagesin_total[1m]))

# Consumer lag by group
kafka_consumer_lag_sum

# Bytes in per topic
rate(kafka_server_brokertopicmetrics_bytesin_total[1m])
```

## 📈 Creating Custom Dashboards

### Step 1: Add New Panel
1. Open Grafana
2. Click "Add panel"
3. Select "Prometheus" as data source
4. Enter PromQL query

### Step 2: Useful Queries

**Messages per topic:**
```promql
sum(rate(kafka_server_brokertopicmetrics_messagesin_total[1m])) by (topic)
```

**Consumer lag by group:**
```promql
sum(kafka_consumer_lag_sum) by (consumer_group)
```

**Top 5 topics by messages:**
```promql
topk(5, sum(rate(kafka_server_brokertopicmetrics_messagesin_total[1m])) by (topic))
```

**Partition count per topic:**
```promql
count(kafka_server_brokertopicmetrics_messagesin_total) by (topic)
```

## 🚨 Setting Up Alerts

### Example Alert: High Consumer Lag

1. In Grafana, go to "Alerting" → "Alert rules"
2. Create new rule:
   - **Name:** High Consumer Lag
   - **Query:** `sum(kafka_consumer_lag_sum) > 1000`
   - **Condition:** When value is above 1000 for 5 minutes
   - **Notification:** Email/Slack

**Result:** You'll get notified when lag gets too high!

### Example Alert: Broker Down

1. Create alert rule:
   - **Name:** Kafka Broker Down
   - **Query:** `kafka_server_kafkaserver_brokerstate == 0`
   - **Condition:** When value equals 0
   - **Notification:** Immediate alert

## 🔧 Configuration Files

### `prometheus.yml`
**Purpose:** Tells Prometheus what to scrape

**Key settings:**
- `scrape_interval`: How often to collect metrics (15s)
- `scrape_configs`: What to monitor (Kafka Exporter)

### `docker-compose.yml`
**Purpose:** Orchestrates all monitoring services

**Services:**
- Prometheus: Metrics storage
- Kafka Exporter: Kafka → Prometheus bridge
- Grafana: Visualization

### `grafana_dashboards/kafka-monitoring.json`
**Purpose:** Pre-configured dashboard

**Contains:**
- All widget definitions
- Queries for each metric
- Layout and styling

## 🐛 Troubleshooting

### "No metrics showing"
- **Check:** Is Kafka Exporter running? `docker compose ps`
- **Check:** Can Kafka Exporter reach Kafka? `curl http://localhost:9308/metrics`
- **Check:** Is Prometheus scraping? View targets in Prometheus UI

### "Kafka Exporter can't connect"
- **Solution:** Update `KAFKA_BROKER_LIST` in docker-compose.yml
- **Solution:** Ensure Kafka is accessible from container
- **Solution:** Check network mode (host network might be needed)

### "Grafana shows no data"
- **Check:** Is Prometheus data source configured?
- **Check:** Are queries correct? Test in Prometheus first
- **Check:** Time range - data might be outside selected range

### "Dashboard not loading"
- **Check:** Dashboard JSON is valid
- **Check:** Dashboard is in correct directory
- **Check:** Grafana has read permissions

## 📚 Key Takeaways

✅ **Prometheus** = Collects and stores metrics
✅ **Kafka Exporter** = Exports Kafka metrics to Prometheus
✅ **Grafana** = Visualizes metrics in dashboards
✅ **Consumer Lag** = Most important metric to watch
✅ **Messages/sec** = Shows system throughput
✅ **Alerts** = Get notified when things go wrong

## 🎉 Summary

You've learned:
- ✅ What monitoring is (like car dashboard)
- ✅ How Prometheus collects metrics
- ✅ How Kafka Exporter bridges Kafka and Prometheus
- ✅ How Grafana visualizes data
- ✅ Key metrics to watch (lag, throughput, health)
- ✅ How to set up alerts

**Congratulations!** You can now monitor your Kafka cluster in real-time! 🚀

## 🎬 Next Steps

1. **Customize dashboards** - Add metrics specific to your use case
2. **Set up alerts** - Get notified of issues automatically
3. **Add more exporters** - Monitor other systems (databases, apps)
4. **Create custom queries** - Track specific business metrics
5. **Production setup** - Scale monitoring for production clusters

