# Message Flows in Kafka

## Overview

Understanding message flows is essential for designing efficient Kafka-based systems.

## Producer Flow

### Steps
1. **Message Creation**: Application creates a message with key and value
2. **Serialization**: Message is serialized (JSON, Avro, Protobuf, etc.)
3. **Topic Selection**: Producer selects target topic
4. **Partitioning**: 
   - If key exists: hash(key) % partitions → target partition
   - If no key: round-robin or custom partitioner
5. **Batch Collection**: Messages are batched for efficiency
6. **Send to Broker**: Batch sent to partition leader
7. **Acknowledgment**: Producer waits for acknowledgment based on `acks` setting

### Producer Configurations
- `acks`: 0 (fire-and-forget), 1 (leader only), all (all replicas)
- `retries`: Number of retry attempts
- `batch.size`: Size of batches before sending
- `linger.ms`: Wait time to fill batches

## Consumer Flow

### Steps
1. **Consumer Group Assignment**: Kafka assigns partitions to consumers
2. **Offset Management**: Consumer tracks last read offset
3. **Fetch Request**: Consumer requests messages from broker
4. **Message Delivery**: Broker sends batch of messages
5. **Processing**: Consumer processes messages
6. **Commit Offset**: Consumer commits offset after processing
7. **Poll Loop**: Consumer continues polling for new messages

### Consumer Configurations
- `group.id`: Consumer group identifier
- `auto.offset.reset`: earliest or latest
- `enable.auto.commit`: Automatic offset committing
- `max.poll.records`: Maximum records per poll

## Message Flow Patterns

### Point-to-Point
- Single producer → Single consumer
- Simple message passing
- One-to-one communication

### Publish-Subscribe
- Multiple producers → Multiple consumers
- Broadcast pattern
- Each consumer group processes all messages

### Request-Reply
- Producer sends request → Consumer processes → Consumer sends reply
- Two topics: request topic and reply topic
- Correlation ID to match requests with replies

### Fan-Out
- One topic → Multiple consumer groups
- Each group processes messages independently
- Allows different processing logic per consumer group

### Pipeline
- Producer → Topic 1 → Consumer/Processor → Topic 2 → Consumer
- Multi-stage processing
- Each stage transforms and forwards data

## Message Ordering

### Within Partition
- Messages in the same partition maintain order
- Key-based partitioning ensures related messages stay together

### Across Partitions
- No guaranteed order across partitions
- If ordering is critical, use single partition or ensure related messages use same key

## Error Handling in Flows

### Producer Errors
- **Retryable**: Network errors, broker unavailable → automatic retry
- **Non-retryable**: Message too large, serialization error → immediate failure

### Consumer Errors
- **Processing Errors**: Handle in application logic
- **Offset Management**: Decide whether to skip or reprocess failed messages
- **Dead Letter Topics**: Route problematic messages for investigation

## Performance Considerations

### Throughput Optimization
- Batch messages for producers
- Tune consumer fetch sizes
- Parallel processing with multiple partitions

### Latency Optimization
- Reduce batch sizes
- Decrease `linger.ms` for producers
- Increase `max.poll.records` for consumers (if appropriate)

### Reliability
- Use `acks=all` for critical data
- Implement idempotent processing
- Monitor consumer lag

## Visual Diagram

![Kafka Message Flow](./message_flow.gif)

If the GIF is not present, generate it from the Mermaid source:

```bash
cd docs
chmod +x generate_gif.sh
./generate_gif.sh
```

This will produce `message_flow.png` and `message_flow.gif` from `message_flow.mmd`.
