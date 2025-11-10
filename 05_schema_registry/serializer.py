#!/usr/bin/env python3
"""
Avro Producer: Publishes transactions using Avro serialization

What it does:
- Reads Avro schema from file
- Creates Avro-encoded messages
- Publishes to Kafka with schema registry
- Ensures data contract compliance
"""

from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json
import time
from datetime import datetime

# Configuration
SCHEMA_REGISTRY_URL = "http://localhost:8081"
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "transactions-avro"
SCHEMA_FILE = "avro_schemas/transaction.avsc"

def load_avro_schema(schema_file):
    """Load Avro schema from file."""
    with open(schema_file, 'r') as f:
        schema_str = f.read()
    return schema_str

def create_producer():
    """Create Kafka producer with Avro serializer."""
    # Schema Registry client
    schema_registry_client = SchemaRegistryClient({
        'url': SCHEMA_REGISTRY_URL
    })
    
    # Load schema
    schema_str = load_avro_schema(SCHEMA_FILE)
    
    # Create Avro serializer
    avro_serializer = AvroSerializer(
        schema_registry_client,
        schema_str
    )
    
    # Create Kafka producer with Avro serializer
    producer = Producer({
        'bootstrap.servers': BOOTSTRAP_SERVERS
    })
    
    return producer, avro_serializer

def create_transaction(account, amount, tx_type, description=None):
    """Create a transaction record matching Avro schema."""
    return {
        "id": f"TXN-{int(time.time() * 1000)}",
        "account": account,
        "amount": amount,
        "timestamp": int(time.time() * 1000),
        "type": tx_type,
        "description": description
    }

def main():
    """Main producer loop."""
    print("📝 Avro Transaction Producer")
    print("=" * 50)
    print(f"📡 Schema Registry: {SCHEMA_REGISTRY_URL}")
    print(f"📨 Kafka: {BOOTSTRAP_SERVERS}")
    print(f"📋 Topic: {TOPIC}")
    print("=" * 50)
    print("Press Ctrl+C to stop\n")
    
    try:
        producer, avro_serializer = create_producer()
        print("✅ Producer created with Avro serialization\n")
        
        # Example transactions
        transactions = [
            (1001, 150.50, "deposit", "Salary deposit"),
            (1002, -75.25, "withdrawal", "ATM withdrawal"),
            (1003, 200.00, "deposit", None),
            (1001, -50.00, "payment", "Online purchase"),
            (1002, 300.75, "transfer", "Received from friend")
        ]
        
        def delivery_callback(err, msg):
            if err:
                print(f"❌ Failed to deliver message: {err}")
            else:
                print(f"✅ Sent: Account {msg.key()} | Partition: {msg.partition()} | Offset: {msg.offset()}")
        
        for account, amount, tx_type, description in transactions:
            tx = create_transaction(account, amount, tx_type, description)
            
            # Serialize with Avro
            serialized_value = avro_serializer(
                tx,
                SerializationContext(TOPIC, MessageField.VALUE)
            )
            
            # Send to Kafka
            producer.produce(
                TOPIC,
                key=str(account),
                value=serialized_value,
                callback=delivery_callback
            )
            
            time.sleep(1)
        
        producer.flush()
        print("\n✅ All transactions sent!")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure Schema Registry is running:")
        print("   docker compose up -d (in 05_schema_registry/)")

if __name__ == "__main__":
    main()

