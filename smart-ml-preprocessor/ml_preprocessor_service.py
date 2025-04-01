
import json
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from io import StringIO
from sklearn.preprocessing import StandardScaler

KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
INPUT_TOPIC = 'pivoted_data'
OUTPUT_TOPIC = 'ml_ready_data'

consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    enable_auto_commit=True,
    group_id='ml-preprocessor-group'
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_and_publish():
    print("✅ ML Preprocessor started. Waiting for data...")
    buffer = []

    for message in consumer:
        buffer.append(message.value)
        if len(buffer) >= 5000:
            break

    df = pd.DataFrame(buffer)
    timestamp_col = df.pop("Timestamp")
    scaled = StandardScaler().fit_transform(df)
    df_scaled = pd.DataFrame(scaled, columns=df.columns)
    df_scaled.insert(0, "Timestamp", timestamp_col)

    for _, row in df_scaled.iterrows():
        producer.send(OUTPUT_TOPIC, row.to_dict())

    producer.flush()
    print(f"✅ Processed and published {len(df_scaled)} records to topic '{OUTPUT_TOPIC}'")

if __name__ == "__main__":
    process_and_publish()
