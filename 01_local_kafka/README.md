# Local Kafka (KRaft) with Docker Compose

This setup runs a single-node Kafka (KRaft mode, no ZooKeeper) and Kafka UI.

## Services
- kafka: bitnami/kafka exposed on http://localhost:9094
- kafka-ui: UI at http://localhost:8080

## Quick Start
```bash
cd 01_local_kafka
# start in background
docker compose up -d

# view logs
docker compose logs -f kafka

# stop
docker compose down
```

## Create and Inspect Topics
```bash
# create a topic (3 partitions)
docker compose exec kafka kafka-topics.sh \
  --create --topic demo-topic --partitions 3 --replication-factor 1 \
  --bootstrap-server localhost:9092

# list topics
docker compose exec kafka kafka-topics.sh \
  --list --bootstrap-server localhost:9092

# describe topic
docker compose exec kafka kafka-topics.sh \
  --describe --topic demo-topic --bootstrap-server localhost:9092
```

## Produce and Consume
```bash
# producer
docker compose exec -it kafka kafka-console-producer.sh \
  --topic demo-topic --bootstrap-server localhost:9092
# type some lines, Ctrl+C to exit

# consumer
docker compose exec -it kafka kafka-console-consumer.sh \
  --topic demo-topic --from-beginning --bootstrap-server localhost:9092
```

## Ports
- Kafka internal: 9092 (inside Docker network)
- Kafka external: 9094 (localhost)
- Kafka controller: 9093 (internal, for KRaft quorum)
- Kafka UI: 8080

## Notes
- Auto topic creation is enabled for convenience.
- For production-like setups, increase replication, disable auto-create, and consider multi-broker clusters.

