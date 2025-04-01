from kafka import KafkaConsumer, KafkaProducer
import pandas as pd
import json
import os

RAW_TOPIC = "raw_data"
PIVOTED_TOPIC = "pivoted_data"
KAFKA_SERVER = "kafka:9092"

def preprocess_and_publish():
    consumer = KafkaConsumer(
        RAW_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id="smart-preprocessor-group"
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    records = []
    for message in consumer:
        records.append(message.value)
        if len(records) >= 5000:  # Flush every 5000 records
            break

    df = pd.DataFrame(records)

    if df.empty:
        print("No data received for preprocessing.")
        return

    df.dropna(subset=["Timestamp", "SYSTEM_DEMAND"], inplace=True)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d-%b-%Y %H:%M:%S")
    df.sort_values("Timestamp", inplace=True)

    for _, row in df.iterrows():
        msg = {k: (str(v) if isinstance(v, pd.Timestamp) else v) for k, v in row.to_dict().items()}
        producer.send(PIVOTED_TOPIC, msg)


    producer.flush()
    print(f"✅ Preprocessed and published {len(df)} records to topic '{PIVOTED_TOPIC}'.")

if __name__ == "__main__":
    preprocess_and_publish()
