import json
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from sklearn.linear_model import LinearRegression
from io import StringIO

KAFKA_BROKER = 'kafka:9092'
INPUT_TOPIC = 'ml_ready_data'
OUTPUT_TOPIC = 'forecast_output'

def run_forecaster():
    consumer = KafkaConsumer(
        INPUT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='ml-forecast-group'
    )

    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("✅ ML Forecaster started. Waiting for data...")
    data = []
    for message in consumer:
        data.append(message.value)
        if len(data) >= 5000:
            break

    df = pd.DataFrame(data)
    if 'SYSTEM_DEMAND' not in df.columns:
        print("❌ Required field 'SYSTEM_DEMAND' not found. Skipping.")
        return

    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour + df['Timestamp'].dt.minute / 60.0

    X = df[['Hour']]
    y = df['SYSTEM_DEMAND']

    model = LinearRegression()
    model.fit(X, y)

    future_hours = pd.DataFrame({'Hour': [h + 0.25 for h in range(24)]})
    predictions = model.predict(future_hours)
    output = [{'Hour': float(h), 'Predicted_Demand': float(p)} for h, p in zip(future_hours['Hour'], predictions)]

    for record in output:
        producer.send(OUTPUT_TOPIC, value=record)
    producer.flush()

    print(f"✅ Published {len(output)} forecast records to topic '{OUTPUT_TOPIC}'")

if __name__ == "__main__":
    run_forecaster()