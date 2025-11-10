import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.state.KeyValueStore;
import org.apache.kafka.streams.state.StoreBuilder;
import org.apache.kafka.streams.state.Stores;

import java.util.Properties;
import java.util.concurrent.TimeUnit;

/**
 * Kafka Streams Application: Real-time Account Balance Aggregation
 * 
 * What it does:
 * - Reads transactions from "transactions" topic
 * - Groups by account number
 * - Calculates rolling sum (total balance) per account
 * - Updates every 10 seconds
 * - Writes results to "account-balances" topic
 */
public class KafkaStreamsApp {
    
    public static void main(String[] args) {
        // Configuration
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "account-balance-aggregator");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        
        // Build the stream processing topology
        StreamsBuilder builder = new StreamsBuilder();
        
        // Read from transactions topic
        KStream<String, String> transactions = builder.stream("transactions");
        
        // Parse transaction JSON and extract account + amount
        KStream<String, Double> accountAmounts = transactions
            .mapValues(value -> {
                // Simple JSON parsing (in production, use proper JSON library)
                // Expected format: {"account":1234,"amount":100.50,...}
                try {
                    String accountStr = value.substring(
                        value.indexOf("\"account\":") + 10,
                        value.indexOf(",", value.indexOf("\"account\":"))
                    );
                    String amountStr = value.substring(
                        value.indexOf("\"amount\":") + 9,
                        value.indexOf(",", value.indexOf("\"amount\":"))
                    );
                    int account = Integer.parseInt(accountStr.trim());
                    double amount = Double.parseDouble(amountStr.trim());
                    return new AccountAmount(account, amount);
                } catch (Exception e) {
                    return null;
                }
            })
            .filter((key, value) -> value != null)
            .map((key, value) -> KeyValue.pair(
                String.valueOf(value.account), 
                value.amount
            ));
        
        // Group by account and aggregate (rolling sum)
        KTable<Windowed<String>, Double> accountBalances = accountAmounts
            .groupByKey()
            .windowedBy(TimeWindows.ofSizeWithNoGrace(TimeUnit.SECONDS.toMillis(10)))
            .aggregate(
                () -> 0.0,
                (key, value, aggregate) -> aggregate + value,
                Materialized.as("account-balance-store")
            );
        
        // Convert windowed key back to string and write to output topic
        accountBalances
            .toStream()
            .map((windowedKey, balance) -> {
                String account = windowedKey.key();
                String windowStart = String.valueOf(windowedKey.window().start());
                String outputKey = account + "-" + windowStart;
                String outputValue = String.format(
                    "{\"account\":%s,\"balance\":%.2f,\"window_start\":%s,\"window_end\":%d}",
                    account, balance, windowStart, windowedKey.window().end()
                );
                return KeyValue.pair(outputKey, outputValue);
            })
            .to("account-balances");
        
        // Start the stream processing
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
        
        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
        
        System.out.println("🚀 Kafka Streams started! Processing transactions...");
        System.out.println("📊 Aggregating account balances every 10 seconds");
        System.out.println("📤 Results written to 'account-balances' topic");
    }
    
    // Helper class for account-amount pairs
    static class AccountAmount {
        int account;
        double amount;
        
        AccountAmount(int account, double amount) {
            this.account = account;
            this.amount = amount;
        }
    }
}

