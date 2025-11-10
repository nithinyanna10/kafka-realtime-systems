#!/usr/bin/env python3
"""
Apache Flink Job: Real-time Fraud Detection

What it does:
- Reads transactions from Kafka topic
- Groups by account
- Calculates total activity in 1-minute windows
- Flags accounts with > $5000 activity in 1 minute
- Writes fraud alerts to "fraud-alerts" topic
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction, KeyedProcessFunction
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.common import Time
import json
import re

class TransactionParser(MapFunction):
    """Parse JSON transaction and extract account + amount."""
    
    def map(self, value):
        try:
            # Parse JSON transaction
            tx = json.loads(value)
            account = tx.get('account')
            amount = abs(float(tx.get('amount', 0)))  # Use absolute value
            timestamp = tx.get('timestamp', 0)
            
            return {
                'account': account,
                'amount': amount,
                'timestamp': timestamp
            }
        except Exception as e:
            print(f"Error parsing transaction: {e}")
            return None

class FraudDetector(KeyedProcessFunction):
    """Detect fraud: flag accounts with > $5000 activity in 1 minute."""
    
    FRAUD_THRESHOLD = 5000.0
    
    def process_element(self, value, ctx, out):
        account = value['account']
        total_amount = value['total_amount']
        
        if total_amount > self.FRAUD_THRESHOLD:
            alert = {
                'account': account,
                'total_activity': total_amount,
                'threshold': self.FRAUD_THRESHOLD,
                'alert_type': 'HIGH_ACTIVITY',
                'message': f'Account {account} has ${total_amount:.2f} activity in 1 minute (threshold: ${self.FRAUD_THRESHOLD})'
            }
            out.collect(json.dumps(alert))
            print(f"🚨 FRAUD ALERT: {alert['message']}")

def main():
    """Main Flink job."""
    # Create execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    
    # Kafka consumer properties
    kafka_props = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'flink-fraud-detector'
    }
    
    # Read from transactions topic
    kafka_consumer = FlinkKafkaConsumer(
        topics='transactions',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    
    # Set watermark strategy (for event time processing)
    watermark_strategy = WatermarkStrategy.for_monotonous_timestamps()
    
    # Create stream from Kafka
    transactions = env.add_source(
        kafka_consumer,
        watermark_strategy=watermark_strategy
    )
    
    # Parse transactions
    parsed = transactions.map(TransactionParser(), output_type=Types.MAP(Types.STRING(), Types.ANY()))
    
    # Filter out None values
    valid_transactions = parsed.filter(lambda x: x is not None)
    
    # Key by account and window by 1 minute
    fraud_alerts = valid_transactions \
        .key_by(lambda x: x['account']) \
        .window(TumblingEventTimeWindows.of(Time.minutes(1))) \
        .sum('amount') \
        .map(lambda x: {
            'account': x['account'],
            'total_amount': x['amount']
        }) \
        .key_by(lambda x: x['account']) \
        .process(FraudDetector(), output_type=Types.STRING())
    
    # Write fraud alerts to Kafka
    kafka_producer = FlinkKafkaProducer(
        topic='fraud-alerts',
        serialization_schema=SimpleStringSchema(),
        producer_config=kafka_props
    )
    
    fraud_alerts.add_sink(kafka_producer)
    
    # Execute the job
    print("🚀 Starting Flink Fraud Detection Job...")
    print("📊 Monitoring: > $5000 activity in 1 minute per account")
    print("📤 Alerts written to 'fraud-alerts' topic")
    
    env.execute("Fraud Detection Job")

if __name__ == "__main__":
    main()

