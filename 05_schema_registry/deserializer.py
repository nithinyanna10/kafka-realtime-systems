#!/usr/bin/env python3
"""
Avro Consumer: Reads transactions using Avro deserialization

What it does:
- Consumes Avro-encoded messages from Kafka
- Automatically deserializes using schema from registry
- Validates data against schema
- Handles schema evolution gracefully
"""

from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json

# Configuration
SCHEMA_REGISTRY_URL = "http://localhost:8081"
BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "transactions-avro"
GROUP_ID = "avro-consumer-group"

def create_consumer():
    """Create Kafka consumer with Avro deserializer."""
    # Schema Registry client
    schema_registry_client = SchemaRegistryClient({
        'url': SCHEMA_REGISTRY_URL
    })
    
    # Create Avro deserializer
    avro_deserializer = AvroDeserializer(
        schema_registry_client
    )
    
    # Create Kafka consumer
    consumer = Consumer({
        'bootstrap.servers': BOOTSTRAP_SERVERS,
        'group.id': GROUP_ID,
        'auto.offset.reset': 'earliest'
    })
    
    consumer.subscribe([TOPIC])
    
    return consumer, avro_deserializer

def format_transaction(tx):
    """Format transaction for display."""
    desc = tx.get('description', 'N/A')
    amount_str = f"${tx['amount']:+.2f}"
    
    return (
        f"Account: {tx['account']:4d} | "
        f"Amount: {amount_str:>10s} | "
        f"Type: {tx['type']:12s} | "
        f"Description: {desc}"
    )

def main():
    """Main consumer loop."""
    print("📥 Avro Transaction Consumer")
    print("=" * 50)
    print(f"📡 Schema Registry: {SCHEMA_REGISTRY_URL}")
    print(f"📨 Kafka: {BOOTSTRAP_SERVERS}")
    print(f"📋 Topic: {TOPIC}")
    print(f"👥 Group: {GROUP_ID}")
    print("=" * 50)
    print("🎯 Consuming messages...\n")
    print("Press Ctrl+C to stop\n")
    
    try:
        consumer, avro_deserializer = create_consumer()
        print("✅ Consumer created with Avro deserialization\n")
        
        count = 0
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"❌ Consumer error: {msg.error()}")
                continue
            
            # Deserialize with Avro
            tx = avro_deserializer(
                msg.value(),
                SerializationContext(TOPIC, MessageField.VALUE)
            )
            
            count += 1
            print(f"[{count:3d}] {format_transaction(tx)}")
            
            # Show schema evolution info if available
            if 'merchant' in tx or 'location' in tx:
                print(f"     ⚡ Schema v2 detected! Additional fields present")
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Stopped after consuming {count} messages")
        consumer.close()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("💡 Make sure Schema Registry is running:")
        print("   docker compose up -d (in 05_schema_registry/)")

if __name__ == "__main__":
    main()

