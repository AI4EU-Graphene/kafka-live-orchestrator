import json
import pandas as pd
from kafka import KafkaConsumer
from io import StringIO

# Configuration
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "raw_data"

def consume_kafka_data(timeout_ms=10000, max_records=10000):
    """
    Consumes messages from Kafka topic and returns a pandas DataFrame.
    """
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=timeout_ms,
        max_poll_records=max_records,
        enable_auto_commit=False,
    )

    messages = []
    for msg in consumer:
        messages.append(msg.value)

    consumer.close()

    if not messages:
        return pd.DataFrame()

    df = pd.DataFrame(messages)

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d-%b-%Y %H:%M:%S")

    return df
