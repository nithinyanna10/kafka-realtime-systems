#!/usr/bin/env python3
"""
Bank Transaction Stream Simulator

Simulates continuous bank transactions and streams them to Kafka.
Perfect for demonstrating real-time data streaming!
"""

from kafka import KafkaProducer
import json
import time
import random
import sys
from datetime import datetime

# Configuration
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "transactions"
DELAY_SECONDS = 0.5  # Time between transactions

def create_transaction():
    """Generate a random bank transaction."""
    return {
        "account": random.randint(1000, 5000),
        "amount": round(random.uniform(-1000, 1000), 2),
        "timestamp": datetime.now().isoformat(),
        "transaction_id": f"TXN-{random.randint(10000, 99999)}",
        "type": random.choice(["deposit", "withdrawal", "transfer", "payment"])
    }

def main():
    """Main simulation loop."""
    print("🏦 Bank Transaction Stream Simulator")
    print("=" * 50)
    print(f"📡 Connecting to Kafka at {BOOTSTRAP_SERVERS}")
    print(f"📨 Publishing to topic: {TOPIC}")
    print(f"⏱️  Rate: 1 transaction every {DELAY_SECONDS} seconds")
    print("=" * 50)
    print("Press Ctrl+C to stop\n")

    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8') if k else None
        )
        
        count = 0
        while True:
            tx = create_transaction()
            # Use account as key for consistent partitioning
            producer.send(TOPIC, key=tx["account"], value=tx)
            count += 1
            
            # Print every 10th transaction for visibility
            if count % 10 == 0:
                print(f"✅ Sent {count} transactions | Latest: Account {tx['account']} | ${tx['amount']:+.2f} | {tx['type']}")
            
            time.sleep(DELAY_SECONDS)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped after sending {count} transactions")
        producer.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure Kafka is running: docker compose up -d (in 01_local_kafka/)")
        sys.exit(1)

if __name__ == "__main__":
    main()

