#!/usr/bin/env python3
"""
Real-time Kafka Consumer with Statistics

Consumes transactions from Kafka and displays real-time statistics.
"""

from kafka import KafkaConsumer
import json
import sys
from collections import defaultdict
from datetime import datetime

class TransactionConsumer:
    """Consumer for processing bank transactions in real-time."""
    
    def __init__(self, bootstrap_servers="localhost:9092", topic="transactions", 
                 group_id="transaction-monitor", auto_offset_reset="earliest"):
        """
        Initialize the consumer.
        
        Args:
            bootstrap_servers: Kafka broker address
            topic: Topic to consume from
            group_id: Consumer group identifier
            auto_offset_reset: Where to start reading ("earliest" or "latest")
        """
        self.topic = topic
        self.stats = {
            "total": 0,
            "by_type": defaultdict(int),
            "by_account": defaultdict(int),
            "total_amount": 0.0,
            "deposits": 0,
            "withdrawals": 0
        }
        
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000  # Timeout for polling
            )
            print(f"✅ Connected to Kafka at {bootstrap_servers}")
            print(f"📥 Consuming from topic: {topic}")
            print(f"👥 Consumer group: {group_id}")
            print("=" * 60)
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            print("💡 Make sure Kafka is running: docker compose up -d (in 01_local_kafka/)")
            sys.exit(1)
    
    def process_message(self, message):
        """Process a single transaction message."""
        tx = message.value
        self.stats["total"] += 1
        self.stats["by_type"][tx.get("type", "unknown")] += 1
        self.stats["by_account"][tx.get("account")] += 1
        self.stats["total_amount"] += tx.get("amount", 0)
        
        if tx.get("amount", 0) > 0:
            self.stats["deposits"] += 1
        else:
            self.stats["withdrawals"] += 1
        
        return tx
    
    def print_stats(self):
        """Print current statistics."""
        print("\n" + "=" * 60)
        print("📊 REAL-TIME STATISTICS")
        print("=" * 60)
        print(f"Total Transactions: {self.stats['total']}")
        print(f"Total Amount: ${self.stats['total_amount']:,.2f}")
        print(f"Deposits: {self.stats['deposits']} | Withdrawals: {self.stats['withdrawals']}")
        print("\n📈 Transactions by Type:")
        for tx_type, count in self.stats['by_type'].items():
            print(f"   {tx_type.capitalize()}: {count}")
        print(f"\n👥 Active Accounts: {len(self.stats['by_account'])}")
        print("=" * 60)
    
    def consume(self, print_interval=10):
        """
        Start consuming messages.
        
        Args:
            print_interval: Print stats every N messages
        """
        print("🎯 Starting to consume messages...\n")
        print("Press Ctrl+C to stop\n")
        
        try:
            count = 0
            for message in self.consumer:
                tx = self.process_message(message)
                count += 1
                
                # Print each transaction
                amount_str = f"${tx.get('amount', 0):+.2f}"
                print(f"[{count:4d}] Account {tx.get('account'):4d} | "
                      f"{amount_str:>10s} | {tx.get('type', 'unknown'):12s} | "
                      f"{tx.get('transaction_id', 'N/A')}")
                
                # Print stats periodically
                if count % print_interval == 0:
                    self.print_stats()
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopped by user")
            self.print_stats()
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            self.close()
    
    def consume_silent(self, max_messages=None):
        """
        Consume messages without printing each one (for testing).
        
        Args:
            max_messages: Maximum number of messages to consume (None = unlimited)
        """
        count = 0
        try:
            for message in self.consumer:
                self.process_message(message)
                count += 1
                if max_messages and count >= max_messages:
                    break
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.print_stats()
            self.close()
    
    def close(self):
        """Close the consumer connection."""
        self.consumer.close()
        print("\n👋 Consumer closed")

# Example usage
if __name__ == "__main__":
    consumer = TransactionConsumer()
    consumer.consume(print_interval=10)

