#!/usr/bin/env python3
"""
Simple Kafka Producer Example

A clean, reusable producer that can send messages to any Kafka topic.
"""

from kafka import KafkaProducer
import json
import sys

class TransactionProducer:
    """Producer for sending bank transactions to Kafka."""
    
    def __init__(self, bootstrap_servers="localhost:9092", topic="transactions"):
        """
        Initialize the producer.
        
        Args:
            bootstrap_servers: Kafka broker address
            topic: Target topic name
        """
        self.topic = topic
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
            print(f"✅ Connected to Kafka at {bootstrap_servers}")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            sys.exit(1)
    
    def send(self, message, key=None):
        """
        Send a message to Kafka.
        
        Args:
            message: Dictionary or JSON-serializable object
            key: Optional partition key (for consistent partitioning)
        """
        future = self.producer.send(self.topic, key=key, value=message)
        
        # Wait for acknowledgment (optional, for reliability)
        try:
            record_metadata = future.get(timeout=10)
            return {
                "topic": record_metadata.topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset
            }
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return None
    
    def send_batch(self, messages):
        """Send multiple messages in a batch."""
        results = []
        for msg in messages:
            result = self.send(msg, key=msg.get("account"))
            results.append(result)
        self.producer.flush()  # Ensure all messages are sent
        return results
    
    def close(self):
        """Close the producer connection."""
        self.producer.close()
        print("👋 Producer closed")

# Example usage
if __name__ == "__main__":
    producer = TransactionProducer()
    
    # Send a single transaction
    transaction = {
        "account": 1234,
        "amount": 150.50,
        "timestamp": "2024-01-01T12:00:00",
        "type": "deposit"
    }
    
    print(f"\n📤 Sending transaction: {transaction}")
    result = producer.send(transaction, key=transaction["account"])
    
    if result:
        print(f"✅ Message sent successfully!")
        print(f"   Topic: {result['topic']}")
        print(f"   Partition: {result['partition']}")
        print(f"   Offset: {result['offset']}")
    
    producer.close()

